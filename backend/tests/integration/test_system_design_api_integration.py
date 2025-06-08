"""
Integration tests for system design API endpoints.
Tests the complete workflow integration with real service dependencies.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch

from app.api.v1.cases.system_design_routes import (
    update_system_design,
    submit_system_design_for_review,
    approve_system_design,
    reject_system_design
)
from app.api.v1.cases.models import SystemDesignUpdateRequest, SystemDesignRejectRequest
from app.agents.orchestrator_agent import OrchestratorAgent, BusinessCaseStatus, BusinessCaseData
from app.core.dependencies import get_firestore_service


class TestSystemDesignAPIIntegration:
    """Integration tests for system design API workflow."""

    @pytest.fixture
    def firestore_service(self):
        """Get the real Firestore service."""
        return get_firestore_service()

    @pytest.fixture
    def test_user_id(self):
        """Test user ID for integration testing."""
        return "integration-test-system-design-user"

    @pytest.fixture
    def test_developer_user_id(self):
        """Test developer user ID for integration testing."""
        return "integration-test-developer-user"

    @pytest.fixture
    def mock_current_user_owner(self, test_user_id):
        """Mock current user who is the owner."""
        return {
            "uid": test_user_id,
            "email": "owner@example.com",
            "custom_claims": {"role": "USER"}
        }

    @pytest.fixture
    def mock_current_user_developer(self, test_developer_user_id):
        """Mock current user with DEVELOPER role."""
        return {
            "uid": test_developer_user_id,
            "email": "developer@example.com",
            "custom_claims": {"role": "DEVELOPER"}
        }

    @pytest.fixture
    def system_design_update_request(self):
        """Create a system design update request."""
        return SystemDesignUpdateRequest(
            content_markdown="""# Integration Test System Design

## Architecture Overview
This is a comprehensive system design created for integration testing.

## Components
- Frontend: React application
- Backend: FastAPI service
- Database: Firestore
- Authentication: Firebase Auth

## Data Flow
1. User submits request
2. System processes request
3. Response is returned

## Performance Requirements
- Response time: < 200ms
- Availability: 99.9%
- Scalability: 1000 concurrent users
"""
        )

    @pytest.fixture
    def system_design_reject_request(self):
        """Create a system design reject request."""
        return SystemDesignRejectRequest(
            reason="Integration test rejection - design needs performance improvements."
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_system_design_workflow_end_to_end(
        self, firestore_service, mock_current_user_owner, mock_current_user_developer, 
        system_design_update_request, test_user_id
    ):
        """Test the complete system design workflow from creation to approval."""
        # Step 1: Create a test business case with system design
        orchestrator = OrchestratorAgent()
        
        test_request = {
            "problemStatement": "Integration test for system design workflow",
            "projectTitle": "System Design Integration Test Case",
            "relevantLinks": ["https://example.com"]
        }
        
        # Create business case and advance to SYSTEM_DESIGN_DRAFTED
        case_response = await orchestrator.handle_request(
            request_type="initiate_case",
            payload=test_request,
            user_id=test_user_id
        )
        
        assert case_response["status"] == "success"
        case_id = case_response["caseId"]
        
        try:
            # Advance to PRD_APPROVED then to SYSTEM_DESIGN_DRAFTED
            # (This would normally be done through the PRD workflow)
            await firestore_service.update_business_case(case_id, {
                "status": BusinessCaseStatus.PRD_APPROVED.value,
                "updated_at": datetime.now(timezone.utc)
            })
            
            # Generate system design using orchestrator
            prd_response = await orchestrator.handle_prd_approval(case_id)
            assert prd_response["status"] == "success"
            
            # Verify case is now in SYSTEM_DESIGN_DRAFTED status
            business_case = await firestore_service.get_business_case(case_id)
            assert business_case.status.value == BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value
            assert business_case.system_design_v1_draft is not None
            
            # Step 2: Update system design content
            result = await update_system_design(
                case_id=case_id,
                system_design_request=system_design_update_request,
                current_user=mock_current_user_owner,
                firestore_service=firestore_service
            )
            
            assert result["message"] == "System design updated successfully"
            assert result["case_id"] == case_id
            
            # Verify the update was applied
            updated_case = await firestore_service.get_business_case(case_id)
            assert updated_case.system_design_v1_draft["content_markdown"] == system_design_update_request.content_markdown
            assert "last_edited_by" in updated_case.system_design_v1_draft
            assert "last_edited_at" in updated_case.system_design_v1_draft
            
            # Step 3: Submit system design for review
            submit_result = await submit_system_design_for_review(
                case_id=case_id,
                current_user=mock_current_user_owner,
                firestore_service=firestore_service
            )
            
            assert submit_result["message"] == "System design submitted for review successfully"
            assert submit_result["new_status"] == BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value
            
            # Verify status update
            pending_case = await firestore_service.get_business_case(case_id)
            assert pending_case.status.value == BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value
            
            # Step 4: Approve system design and trigger effort estimation
            with patch.object(orchestrator, 'handle_system_design_approval') as mock_handle:
                mock_handle.return_value = {
                    "status": "success",
                    "new_status": BusinessCaseStatus.PLANNING_COMPLETE.value,
                    "case_id": case_id
                }
                
                approve_result = await approve_system_design(
                    case_id=case_id,
                    current_user=mock_current_user_developer,
                    firestore_service=firestore_service
                )
                
                assert approve_result["message"] == "System design approved successfully and effort estimation initiated"
                assert approve_result["new_status"] == BusinessCaseStatus.PLANNING_COMPLETE.value
                assert approve_result["effort_estimation_initiated"] is True
                
                # Verify orchestrator was called
                mock_handle.assert_called_once_with(case_id)
            
            # Verify approval was recorded
            approved_case = await firestore_service.get_business_case(case_id)
            assert approved_case.status.value == BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value
            
            # Verify history contains approval
            history_entries = [entry.get("content", "") for entry in approved_case.history]
            approval_entries = [entry for entry in history_entries if "approved" in entry.lower()]
            assert len(approval_entries) > 0
            
        finally:
            # Cleanup: Delete the test case
            try:
                await firestore_service.delete_business_case(case_id)
            except Exception as e:
                print(f"Warning: Could not cleanup test case {case_id}: {e}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_system_design_rejection_workflow(
        self, firestore_service, mock_current_user_owner, mock_current_user_developer,
        system_design_reject_request, test_user_id
    ):
        """Test the system design rejection workflow."""
        # Step 1: Create a test business case in SYSTEM_DESIGN_PENDING_REVIEW status
        orchestrator = OrchestratorAgent()
        
        test_request = {
            "problemStatement": "Integration test for system design rejection",
            "projectTitle": "System Design Rejection Test Case",
            "relevantLinks": []
        }
        
        case_response = await orchestrator.handle_request(
            request_type="initiate_case",
            payload=test_request,
            user_id=test_user_id
        )
        
        assert case_response["status"] == "success"
        case_id = case_response["caseId"]
        
        try:
            # Manually set case to SYSTEM_DESIGN_PENDING_REVIEW status
            await firestore_service.update_business_case(case_id, {
                "status": BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value,
                "system_design_v1_draft": {
                    "content_markdown": "# Test System Design",
                    "generated_by": "ArchitectAgent",
                    "generated_timestamp": datetime.now(timezone.utc).isoformat()
                },
                "updated_at": datetime.now(timezone.utc)
            })
            
            # Step 2: Reject system design
            reject_result = await reject_system_design(
                case_id=case_id,
                reject_request=system_design_reject_request,
                current_user=mock_current_user_developer,
                firestore_service=firestore_service
            )
            
            assert reject_result["message"] == "System design rejected successfully"
            assert reject_result["new_status"] == BusinessCaseStatus.SYSTEM_DESIGN_REJECTED.value
            
            # Step 3: Verify rejection was recorded
            rejected_case = await firestore_service.get_business_case(case_id)
            assert rejected_case.status.value == BusinessCaseStatus.SYSTEM_DESIGN_REJECTED.value
            
            # Verify history contains rejection with reason
            history_entries = [entry.get("content", "") for entry in rejected_case.history]
            rejection_entries = [entry for entry in history_entries if "rejected" in entry.lower()]
            assert len(rejection_entries) > 0
            
            # Check that rejection reason is included
            rejection_with_reason = [entry for entry in rejection_entries if system_design_reject_request.reason in entry]
            assert len(rejection_with_reason) > 0
            
            # Step 4: Verify owner can edit after rejection
            update_request = SystemDesignUpdateRequest(
                content_markdown="# Revised System Design\n\nFixed based on feedback."
            )
            
            update_result = await update_system_design(
                case_id=case_id,
                system_design_request=update_request,
                current_user=mock_current_user_owner,
                firestore_service=firestore_service
            )
            
            assert update_result["message"] == "System design updated successfully"
            
            # Verify the update was applied
            updated_case = await firestore_service.get_business_case(case_id)
            assert updated_case.system_design_v1_draft["content_markdown"] == update_request.content_markdown
            
        finally:
            # Cleanup
            try:
                await firestore_service.delete_business_case(case_id)
            except Exception as e:
                print(f"Warning: Could not cleanup test case {case_id}: {e}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_authorization_enforcement(
        self, firestore_service, mock_current_user_owner, test_user_id
    ):
        """Test that authorization is properly enforced across the workflow."""
        # Create a test case
        orchestrator = OrchestratorAgent()
        
        test_request = {
            "problemStatement": "Authorization test case",
            "projectTitle": "Authorization Test Case",
            "relevantLinks": []
        }
        
        case_response = await orchestrator.handle_request(
            request_type="initiate_case",
            payload=test_request,
            user_id=test_user_id
        )
        
        case_id = case_response["caseId"]
        
        try:
            # Set up case in SYSTEM_DESIGN_PENDING_REVIEW status
            await firestore_service.update_business_case(case_id, {
                "status": BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value,
                "system_design_v1_draft": {"content_markdown": "# Test Design"},
                "updated_at": datetime.now(timezone.utc)
            })
            
            # Test that non-developer cannot approve
            non_developer_user = {
                "uid": "non-developer-user",
                "email": "user@example.com",
                "custom_claims": {"role": "USER"}
            }
            
            with pytest.raises(Exception) as exc_info:
                await approve_system_design(
                    case_id=case_id,
                    current_user=non_developer_user,
                    firestore_service=firestore_service
                )
            
            # Should get 403 Forbidden
            assert "403" in str(exc_info.value) or "permission" in str(exc_info.value).lower()
            
            # Test that non-developer cannot reject
            reject_request = SystemDesignRejectRequest(reason="Test rejection")
            with pytest.raises(Exception) as exc_info:
                await reject_system_design(
                    case_id=case_id,
                    reject_request=reject_request,
                    current_user=non_developer_user,
                    firestore_service=firestore_service
                )
            
            # Should get 403 Forbidden
            assert "403" in str(exc_info.value) or "permission" in str(exc_info.value).lower()
            
            # Test that non-owner cannot submit for review
            await firestore_service.update_business_case(case_id, {
                "status": BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value
            })
            
            with pytest.raises(Exception) as exc_info:
                await submit_system_design_for_review(
                    case_id=case_id,
                    current_user=non_developer_user,
                    firestore_service=firestore_service
                )
            
            # Should get 403 Forbidden
            assert "403" in str(exc_info.value) or "permission" in str(exc_info.value).lower()
            
        finally:
            # Cleanup
            try:
                await firestore_service.delete_business_case(case_id)
            except Exception as e:
                print(f"Warning: Could not cleanup test case {case_id}: {e}")

    @pytest.mark.asyncio
    @pytest.mark.integration 
    async def test_status_transition_validation(
        self, firestore_service, mock_current_user_owner, mock_current_user_developer, test_user_id
    ):
        """Test that status transitions are properly validated."""
        # Create a test case
        orchestrator = OrchestratorAgent()
        
        test_request = {
            "problemStatement": "Status transition test case",
            "projectTitle": "Status Transition Test Case",
            "relevantLinks": []
        }
        
        case_response = await orchestrator.handle_request(
            request_type="initiate_case",
            payload=test_request,
            user_id=test_user_id
        )
        
        case_id = case_response["caseId"]
        
        try:
            # Test: Cannot approve when not in PENDING_REVIEW status
            await firestore_service.update_business_case(case_id, {
                "status": BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value,
                "system_design_v1_draft": {"content_markdown": "# Test Design"},
                "updated_at": datetime.now(timezone.utc)
            })
            
            with pytest.raises(Exception) as exc_info:
                await approve_system_design(
                    case_id=case_id,
                    current_user=mock_current_user_developer,
                    firestore_service=firestore_service
                )
            
            assert "400" in str(exc_info.value) or "Cannot approve" in str(exc_info.value)
            
            # Test: Cannot submit when already in PENDING_REVIEW
            await firestore_service.update_business_case(case_id, {
                "status": BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value
            })
            
            with pytest.raises(Exception) as exc_info:
                await submit_system_design_for_review(
                    case_id=case_id,
                    current_user=mock_current_user_owner,
                    firestore_service=firestore_service
                )
            
            assert "400" in str(exc_info.value) or "Cannot submit" in str(exc_info.value)
            
        finally:
            # Cleanup
            try:
                await firestore_service.delete_business_case(case_id)
            except Exception as e:
                print(f"Warning: Could not cleanup test case {case_id}: {e}") 