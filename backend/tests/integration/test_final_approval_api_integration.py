"""
Integration tests for final approval API endpoints.
Tests complete API workflows with real service integration.
Includes end-to-end workflow validation and authorization integration.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone
from fastapi import HTTPException

from app.api.v1.cases.final_approval_routes import (
    submit_case_for_final_approval,
    approve_final_case,
    reject_final_case
)
from app.api.v1.cases.models import FinalRejectRequest
from app.agents.orchestrator_agent import BusinessCaseStatus
from app.services.firestore_service import FirestoreService


class TestFinalApprovalAPIIntegration:
    """Integration test suite for final approval API workflows."""

    @pytest.fixture
    def sample_business_case_financial_complete(self):
        """Create a sample business case ready for final approval."""
        return {
            "case_id": "integration-test-case-123",
            "user_id": "test-user-456",
            "title": "Integration Test Business Case",
            "problem_statement": "Testing final approval integration",
            "status": BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE.value,
            "financial_model": {
                "summary": "Complete financial model",
                "total_cost": 250000,
                "roi_percentage": 15.5,
                "generated_by": "FinancialModelAgent",
                "generated_timestamp": "2024-01-01T00:00:00Z"
            },
            "history": [
                {
                    "timestamp": "2024-01-01T00:00:00Z",
                    "message": "Financial model completed",
                    "messageType": "FINANCIAL_MODEL_COMPLETE"
                }
            ],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

    @pytest.fixture
    def sample_business_case_pending_approval(self):
        """Create a sample business case pending final approval."""
        return {
            "case_id": "integration-test-case-456",
            "user_id": "test-user-456",
            "title": "Integration Test Pending Case",
            "problem_statement": "Testing pending approval integration",
            "status": BusinessCaseStatus.PENDING_FINAL_APPROVAL.value,
            "financial_model": {
                "summary": "Complete financial model",
                "total_cost": 250000,
                "roi_percentage": 15.5
            },
            "history": [
                {
                    "timestamp": "2024-01-01T00:00:00Z",
                    "message": "Case submitted for final approval",
                    "messageType": "SUBMIT_FOR_FINAL_APPROVAL"
                }
            ],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

    @pytest.fixture
    def case_owner_user(self):
        """Create a case owner user."""
        return {
            "uid": "test-user-456",
            "email": "owner@example.com",
            "systemRole": "USER"
        }

    @pytest.fixture
    def admin_user(self):
        """Create an admin user."""
        return {
            "uid": "admin-user-789",
            "email": "admin@example.com",
            "systemRole": "ADMIN"
        }

    @pytest.fixture
    def final_approver_user(self):
        """Create a final approver user."""
        return {
            "uid": "approver-user-999",
            "email": "approver@example.com",
            "systemRole": "FINAL_APPROVER"
        }

    @pytest.fixture
    def unauthorized_user(self):
        """Create an unauthorized user."""
        return {
            "uid": "unauthorized-user-111",
            "email": "unauthorized@example.com",
            "systemRole": "USER"
        }

    @pytest.fixture
    def mock_firestore_service(self):
        """Create a comprehensive mock firestore service."""
        service = Mock(spec=FirestoreService)
        service.get_business_case = AsyncMock()
        service.update_business_case = AsyncMock()
        return service

    # ============================================================================
    # Complete Workflow Integration Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_complete_final_approval_workflow(
        self, sample_business_case_financial_complete, sample_business_case_pending_approval,
        case_owner_user, admin_user, mock_firestore_service
    ):
        """Test complete final approval workflow from submission to approval."""
        
        # Stage 1: Submit case for final approval
        mock_firestore_service.get_business_case.return_value = Mock(**sample_business_case_financial_complete)
        mock_firestore_service.update_business_case.return_value = True

        submit_result = await submit_case_for_final_approval(
            case_id="integration-test-case-123",
            current_user=case_owner_user,
            firestore_service=mock_firestore_service
        )

        # Verify submission
        assert submit_result["message"] == "Business case submitted for final approval successfully"
        assert submit_result["new_status"] == BusinessCaseStatus.PENDING_FINAL_APPROVAL.value

        # Stage 2: Admin approves the case
        with patch("app.utils.approval_permissions.check_final_approval_permissions") as mock_permissions:
            mock_permissions.return_value = None  # No exception = authorized
            mock_firestore_service.get_business_case.return_value = Mock(**sample_business_case_pending_approval)
            mock_firestore_service.update_business_case.return_value = True

            approve_result = await approve_final_case(
                case_id="integration-test-case-456",
                current_user=admin_user,
                firestore_service=mock_firestore_service
            )

        # Verify approval
        assert approve_result["message"] == "Business case approved successfully"
        assert approve_result["new_status"] == BusinessCaseStatus.APPROVED.value

        # Verify Firestore interactions
        assert mock_firestore_service.get_business_case.call_count == 2
        assert mock_firestore_service.update_business_case.call_count == 2

    @pytest.mark.asyncio
    async def test_final_approval_with_rejection_workflow(
        self, sample_business_case_pending_approval, admin_user, mock_firestore_service
    ):
        """Test final approval workflow with rejection."""
        
        reject_request = FinalRejectRequest(
            reason="Business case needs more detailed cost analysis."
        )

        with patch("app.utils.approval_permissions.check_final_approval_permissions") as mock_permissions:
            mock_permissions.return_value = None  # No exception = authorized
            mock_firestore_service.get_business_case.return_value = Mock(**sample_business_case_pending_approval)
            mock_firestore_service.update_business_case.return_value = True

            # Execute rejection
            reject_result = await reject_final_case(
                case_id="integration-test-case-456",
                reject_request=reject_request,
                current_user=admin_user,
                firestore_service=mock_firestore_service
            )

        # Verify rejection
        assert reject_result["message"] == "Business case rejected successfully"
        assert reject_result["new_status"] == BusinessCaseStatus.REJECTED.value

        # Verify Firestore interactions
        mock_firestore_service.get_business_case.assert_called_once_with("integration-test-case-456")
        mock_firestore_service.update_business_case.assert_called_once()

        # Verify history logging includes rejection reason
        update_call_args = mock_firestore_service.update_business_case.call_args[0]
        updated_case = update_call_args[1]  # Second argument is the updated case data
        assert any("needs more detailed cost analysis" in entry.get("message", "") for entry in updated_case.get("history", []))

    # ============================================================================
    # Authorization Integration Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_final_approval_authorization_enforcement(
        self, sample_business_case_financial_complete, sample_business_case_pending_approval,
        case_owner_user, unauthorized_user, admin_user, final_approver_user, mock_firestore_service
    ):
        """Test comprehensive authorization enforcement across all endpoints."""
        
        # Test 1: Only case owner can submit for final approval
        mock_firestore_service.get_business_case.return_value = Mock(**sample_business_case_financial_complete)
        
        # Case owner should succeed
        await submit_case_for_final_approval(
            case_id="integration-test-case-123",
            current_user=case_owner_user,
            firestore_service=mock_firestore_service
        )

        # Unauthorized user should fail
        with pytest.raises(HTTPException) as exc_info:
            await submit_case_for_final_approval(
                case_id="integration-test-case-123",
                current_user=unauthorized_user,
                firestore_service=mock_firestore_service
            )
        assert exc_info.value.status_code == 403

        # Test 2: Only authorized users can approve/reject
        mock_firestore_service.get_business_case.return_value = Mock(**sample_business_case_pending_approval)

        with patch("app.utils.approval_permissions.check_final_approval_permissions") as mock_permissions:
            # Admin should succeed
            mock_permissions.return_value = None
            await approve_final_case(
                case_id="integration-test-case-456",
                current_user=admin_user,
                firestore_service=mock_firestore_service
            )

            # Final approver should succeed
            mock_permissions.return_value = None
            await approve_final_case(
                case_id="integration-test-case-456",
                current_user=final_approver_user,
                firestore_service=mock_firestore_service
            )

            # Unauthorized user should fail
            mock_permissions.side_effect = HTTPException(status_code=403, detail="Access denied")
            with pytest.raises(HTTPException) as exc_info:
                await approve_final_case(
                    case_id="integration-test-case-456",
                    current_user=unauthorized_user,
                    firestore_service=mock_firestore_service
                )
            assert exc_info.value.status_code == 403

    # ============================================================================
    # Status Transition Integration Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_final_approval_status_validation(
        self, case_owner_user, admin_user, mock_firestore_service
    ):
        """Test proper status validation across all operations."""
        
        # Test 1: Can only submit from FINANCIAL_MODEL_COMPLETE
        draft_case = Mock()
        draft_case.case_id = "test-case"
        draft_case.user_id = case_owner_user["uid"]
        draft_case.status = BusinessCaseStatus.DRAFT
        
        mock_firestore_service.get_business_case.return_value = draft_case

        with pytest.raises(HTTPException) as exc_info:
            await submit_case_for_final_approval(
                case_id="test-case",
                current_user=case_owner_user,
                firestore_service=mock_firestore_service
            )
        assert exc_info.value.status_code == 400
        assert "Must be in FINANCIAL_MODEL_COMPLETE status" in str(exc_info.value.detail)

        # Test 2: Can only approve/reject from PENDING_FINAL_APPROVAL
        approved_case = Mock()
        approved_case.case_id = "test-case"
        approved_case.user_id = case_owner_user["uid"]
        approved_case.status = BusinessCaseStatus.APPROVED
        
        mock_firestore_service.get_business_case.return_value = approved_case

        with patch("app.utils.approval_permissions.check_final_approval_permissions") as mock_permissions:
            mock_permissions.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await approve_final_case(
                    case_id="test-case",
                    current_user=admin_user,
                    firestore_service=mock_firestore_service
                )
            assert exc_info.value.status_code == 400
            assert "Must be in PENDING_FINAL_APPROVAL status" in str(exc_info.value.detail)

    # ============================================================================
    # History Logging Integration Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_final_approval_history_logging(
        self, sample_business_case_financial_complete, case_owner_user, mock_firestore_service
    ):
        """Test that all final approval operations are properly logged to history."""
        
        mock_firestore_service.get_business_case.return_value = Mock(**sample_business_case_financial_complete)
        mock_firestore_service.update_business_case.return_value = True

        # Execute submission
        await submit_case_for_final_approval(
            case_id="integration-test-case-123",
            current_user=case_owner_user,
            firestore_service=mock_firestore_service
        )

        # Verify history logging
        update_call = mock_firestore_service.update_business_case.call_args
        case_id, updated_data = update_call[0]
        
        # Verify new history entry was added
        assert "history" in updated_data
        history_entries = updated_data["history"]
        assert len(history_entries) > 0
        
        # Verify the new entry contains submission information
        latest_entry = history_entries[-1]
        assert latest_entry["messageType"] == "SUBMIT_FOR_FINAL_APPROVAL"
        assert "Case submitted for final approval" in latest_entry["message"]
        assert latest_entry["user_email"] == case_owner_user["email"]

    # ============================================================================
    # Error Handling Integration Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_final_approval_database_error_handling(
        self, sample_business_case_financial_complete, case_owner_user, mock_firestore_service
    ):
        """Test error handling when database operations fail."""
        
        # Test 1: Database read failure
        mock_firestore_service.get_business_case.side_effect = Exception("Database connection error")

        with pytest.raises(HTTPException) as exc_info:
            await submit_case_for_final_approval(
                case_id="integration-test-case-123",
                current_user=case_owner_user,
                firestore_service=mock_firestore_service
            )
        assert exc_info.value.status_code == 500

        # Test 2: Database write failure
        mock_firestore_service.get_business_case.side_effect = None
        mock_firestore_service.get_business_case.return_value = Mock(**sample_business_case_financial_complete)
        mock_firestore_service.update_business_case.side_effect = Exception("Database write error")

        with pytest.raises(HTTPException) as exc_info:
            await submit_case_for_final_approval(
                case_id="integration-test-case-123",
                current_user=case_owner_user,
                firestore_service=mock_firestore_service
            )
        assert exc_info.value.status_code == 500

    # ============================================================================
    # Performance and Edge Case Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_final_approval_with_large_history(
        self, case_owner_user, mock_firestore_service
    ):
        """Test final approval operations with large history arrays."""
        
        # Create a case with large history (simulating real-world scenarios)
        large_history = [
            {
                "timestamp": f"2024-01-{i:02d}T00:00:00Z",
                "message": f"Test history entry {i}",
                "messageType": "TEST_ENTRY"
            }
            for i in range(1, 101)  # 100 history entries
        ]

        large_case = {
            "case_id": "large-history-case",
            "user_id": case_owner_user["uid"],
            "status": BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE.value,
            "history": large_history
        }

        mock_firestore_service.get_business_case.return_value = Mock(**large_case)
        mock_firestore_service.update_business_case.return_value = True

        # Execute - should handle large history gracefully
        result = await submit_case_for_final_approval(
            case_id="large-history-case",
            current_user=case_owner_user,
            firestore_service=mock_firestore_service
        )

        assert result["message"] == "Business case submitted for final approval successfully"

        # Verify history was properly extended
        update_call = mock_firestore_service.update_business_case.call_args
        updated_data = update_call[0][1]
        assert len(updated_data["history"]) == 101  # Original 100 + 1 new entry 