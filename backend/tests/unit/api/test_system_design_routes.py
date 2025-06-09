"""
Unit tests for system design API endpoints.
Tests all CRUD operations and authorization logic for system design workflow.
Includes enhanced logging verification tests.
"""

import pytest
import pytest_asyncio
import logging
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from app.api.v1.cases.system_design_routes import (
    update_system_design,
    submit_system_design_for_review,
    approve_system_design,
    reject_system_design
)
from app.api.v1.cases.models import SystemDesignUpdateRequest, SystemDesignRejectRequest
from app.agents.orchestrator_agent import BusinessCaseStatus
from app.core.constants import HTTPStatus, ErrorMessages, MessageTypes, MessageSources
from tests.utils.logging_test_helpers import (
    assert_log_contains,
    assert_workflow_logging_sequence,
    LogLevelContext
)


class TestSystemDesignRoutesUnit:
    """Unit test suite for system design API routes."""

    @pytest.fixture
    def mock_business_case(self):
        """Create a mock business case for testing."""
        case = Mock()
        case.case_id = "test-case-123"
        case.user_id = "test-user-456"
        case.title = "Test Business Case"
        case.status = BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED
        case.system_design_v1_draft = {
            "content_markdown": "# Original System Design",
            "generated_by": "ArchitectAgent",
            "generated_timestamp": "2024-01-01T00:00:00Z"
        }
        case.history = []
        return case

    @pytest.fixture
    def mock_current_user_owner(self):
        """Create a mock current user who is the owner."""
        return {
            "uid": "test-user-456",
            "email": "owner@example.com",
            "custom_claims": {"role": "USER"}
        }

    @pytest.fixture
    def mock_current_user_developer(self):
        """Create a mock current user with DEVELOPER role."""
        return {
            "uid": "different-user-789",
            "email": "developer@example.com",
            "custom_claims": {"role": "DEVELOPER"}
        }

    @pytest.fixture
    def mock_current_user_unauthorized(self):
        """Create a mock current user with no permissions."""
        return {
            "uid": "unauthorized-user-999",
            "email": "unauthorized@example.com",
            "custom_claims": {"role": "USER"}
        }

    @pytest.fixture
    def mock_firestore_service(self):
        """Create a mock firestore service."""
        service = Mock()
        service.get_business_case = AsyncMock()
        service.update_business_case = AsyncMock()
        return service

    @pytest.fixture
    def system_design_update_request(self):
        """Create a system design update request."""
        return SystemDesignUpdateRequest(
            content_markdown="# Updated System Design\n\nThis is updated content with technical details."
        )

    @pytest.fixture
    def system_design_reject_request(self):
        """Create a system design reject request."""
        return SystemDesignRejectRequest(
            reason="The design doesn't meet performance requirements."
        )

    # ============================================================================
    # Update System Design Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_update_system_design_success_owner(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service, system_design_update_request
    ):
        """Test successful system design update by owner."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Execute
        result = await update_system_design(
            case_id="test-case-123",
            system_design_request=system_design_update_request,
            current_user=mock_current_user_owner,
            firestore_service=mock_firestore_service
        )

        # Verify
        assert result["message"] == "System design updated successfully"
        assert result["case_id"] == "test-case-123"
        mock_firestore_service.update_business_case.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_system_design_unauthorized(
        self, mock_business_case, mock_current_user_unauthorized, mock_firestore_service, system_design_update_request
    ):
        """Test system design update with unauthorized user."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await update_system_design(
                case_id="test-case-123",
                system_design_request=system_design_update_request,
                current_user=mock_current_user_unauthorized,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN

    @pytest.mark.asyncio
    async def test_update_system_design_case_not_found(
        self, mock_current_user_owner, mock_firestore_service, system_design_update_request
    ):
        """Test system design update with non-existent case."""
        # Setup
        mock_firestore_service.get_business_case.return_value = None

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await update_system_design(
                case_id="non-existent-case",
                system_design_request=system_design_update_request,
                current_user=mock_current_user_owner,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND

    # ============================================================================
    # Submit System Design Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_submit_system_design_success(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service
    ):
        """Test successful system design submission."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Execute
        result = await submit_system_design_for_review(
            case_id="test-case-123",
            current_user=mock_current_user_owner,
            firestore_service=mock_firestore_service
        )

        # Verify
        assert result["message"] == "System design submitted for review successfully"
        assert result["new_status"] == BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value
        mock_firestore_service.update_business_case.assert_called_once()

    @pytest.mark.asyncio
    async def test_submit_system_design_unauthorized(
        self, mock_business_case, mock_current_user_unauthorized, mock_firestore_service
    ):
        """Test system design submission by unauthorized user."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await submit_system_design_for_review(
                case_id="test-case-123",
                current_user=mock_current_user_unauthorized,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN

    # ============================================================================
    # Approve System Design Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_approve_system_design_success(
        self, mock_business_case, mock_current_user_developer, mock_firestore_service, caplog
    ):
        """Test successful system design approval with logging verification."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Mock the orchestrator
        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_system_design_approval = AsyncMock(return_value={
                "status": "success",
                "new_status": BusinessCaseStatus.PLANNING_COMPLETE.value
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            # Ensure INFO level logging is captured
            with LogLevelContext('app.api.v1.cases.system_design_routes', 'INFO'):
                # Execute
                result = await approve_system_design(
                    case_id="test-case-123",
                    current_user=mock_current_user_developer,
                    firestore_service=mock_firestore_service
                )

            # Verify functional behavior
            assert result["message"] == "System design approved successfully and effort estimation initiated"
            assert result["new_status"] == BusinessCaseStatus.PLANNING_COMPLETE.value
            assert result["effort_estimation_initiated"] is True
            mock_orchestrator.handle_system_design_approval.assert_called_once_with("test-case-123")

            # Verify enhanced logging
            assert_log_contains(
                caplog, 
                "INFO", 
                "System design approval initiated for case test-case-123 by user developer@example.com",
                "app.api.v1.cases.system_design_routes"
            )
            assert_log_contains(
                caplog,
                "INFO", 
                "Status check for case test-case-123: current is SYSTEM_DESIGN_PENDING_REVIEW, expecting SYSTEM_DESIGN_PENDING_REVIEW",
                "app.api.v1.cases.system_design_routes"
            )
            assert_log_contains(
                caplog,
                "INFO",
                "Status transition: SYSTEM_DESIGN_PENDING_REVIEW -> SYSTEM_DESIGN_APPROVED for case test-case-123",
                "app.api.v1.cases.system_design_routes"
            )
            assert_log_contains(
                caplog,
                "INFO",
                "Calling orchestrator\\.handle_system_design_approval\\(\\) for case test-case-123",
                "app.api.v1.cases.system_design_routes"
            )

    @pytest.mark.asyncio
    async def test_approve_system_design_orchestrator_failure(
        self, mock_business_case, mock_current_user_developer, mock_firestore_service
    ):
        """Test system design approval with orchestrator failure."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Mock the orchestrator with failure
        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_system_design_approval = AsyncMock(return_value={
                "status": "error",
                "message": "PlannerAgent failed"
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            # Execute
            result = await approve_system_design(
                case_id="test-case-123",
                current_user=mock_current_user_developer,
                firestore_service=mock_firestore_service
            )

            # Verify
            assert "approved successfully but effort estimation encountered an issue" in result["message"]
            assert result["new_status"] == BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value
            assert result["effort_estimation_initiated"] is False
            assert "effort_estimation_error" in result

    @pytest.mark.asyncio
    async def test_approve_system_design_non_developer(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service
    ):
        """Test system design approval by non-developer."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await approve_system_design(
                case_id="test-case-123",
                current_user=mock_current_user_owner,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == 403

    # ============================================================================
    # Reject System Design Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_reject_system_design_success_with_reason(
        self, mock_business_case, mock_current_user_developer, mock_firestore_service, system_design_reject_request, caplog
    ):
        """Test successful system design rejection with reason and logging verification."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Ensure INFO level logging is captured
        with LogLevelContext('app.api.v1.cases.system_design_routes', 'INFO'):
            # Execute
            result = await reject_system_design(
                case_id="test-case-123",
                reject_request=system_design_reject_request,
                current_user=mock_current_user_developer,
                firestore_service=mock_firestore_service
            )

        # Verify functional behavior
        assert result["message"] == "System design rejected successfully"
        assert result["new_status"] == BusinessCaseStatus.SYSTEM_DESIGN_REJECTED.value
        mock_firestore_service.update_business_case.assert_called_once()

        # Verify enhanced logging
        assert_log_contains(
            caplog,
            "INFO",
            "System design rejection initiated for case test-case-123 by user developer@example.com",
            "app.api.v1.cases.system_design_routes"
        )
        assert_log_contains(
            caplog,
            "INFO",
            "Status check for case test-case-123: current is SYSTEM_DESIGN_PENDING_REVIEW, expecting SYSTEM_DESIGN_PENDING_REVIEW",
            "app.api.v1.cases.system_design_routes"
        )
        assert_log_contains(
            caplog,
            "INFO",
            "Status transition: SYSTEM_DESIGN_PENDING_REVIEW -> SYSTEM_DESIGN_REJECTED for case test-case-123",
            "app.api.v1.cases.system_design_routes"
        )

    @pytest.mark.asyncio
    async def test_reject_system_design_non_developer(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service, system_design_reject_request
    ):
        """Test system design rejection by non-developer."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await reject_system_design(
                case_id="test-case-123",
                reject_request=system_design_reject_request,
                current_user=mock_current_user_owner,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == 403

    # ============================================================================
    # Error Handling Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_user_without_uid(self, mock_firestore_service, system_design_update_request):
        """Test with user missing UID."""
        # Setup
        mock_current_user = {"email": "test@example.com"}  # Missing uid

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await update_system_design(
                case_id="test-case-123",
                system_design_request=system_design_update_request,
                current_user=mock_current_user,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_update_system_design_firestore_failure(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service, system_design_update_request, caplog
    ):
        """Test system design update when Firestore update fails."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = False  # Firestore failure

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await update_system_design(
                case_id="test-case-123",
                system_design_request=system_design_update_request,
                current_user=mock_current_user_owner,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert "Failed to update system design" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_system_design_invalid_status(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service, system_design_update_request
    ):
        """Test system design update from invalid status."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.SYSTEM_DESIGN_APPROVED  # Invalid status for editing
        mock_firestore_service.get_business_case.return_value = mock_business_case

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await update_system_design(
                case_id="test-case-123",
                system_design_request=system_design_update_request,
                current_user=mock_current_user_owner,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
        assert "Cannot edit system design from current status" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_submit_system_design_firestore_failure(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service
    ):
        """Test system design submission when Firestore update fails."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = False

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await submit_system_design_for_review(
                case_id="test-case-123",
                current_user=mock_current_user_owner,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert "Failed to submit system design for review" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_submit_system_design_invalid_status(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service
    ):
        """Test system design submission from invalid status."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.SYSTEM_DESIGN_APPROVED  # Invalid status
        mock_firestore_service.get_business_case.return_value = mock_business_case

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await submit_system_design_for_review(
                case_id="test-case-123",
                current_user=mock_current_user_owner,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
        assert "Cannot submit system design from current status" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_approve_system_design_firestore_failure(
        self, mock_business_case, mock_current_user_developer, mock_firestore_service
    ):
        """Test system design approval when Firestore update fails."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = False

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await approve_system_design(
                case_id="test-case-123",
                current_user=mock_current_user_developer,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == 500
        assert "Failed to approve system design" in str(exc_info.value.detail)

    @pytest.mark.asyncio 
    async def test_approve_system_design_invalid_status(
        self, mock_business_case, mock_current_user_developer, mock_firestore_service
    ):
        """Test system design approval from invalid status."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED  # Invalid status
        mock_firestore_service.get_business_case.return_value = mock_business_case

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await approve_system_design(
                case_id="test-case-123",
                current_user=mock_current_user_developer,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == 400
        assert "System design must be in PENDING_REVIEW status" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_reject_system_design_firestore_failure(
        self, mock_business_case, mock_current_user_developer, mock_firestore_service, system_design_reject_request
    ):
        """Test system design rejection when Firestore update fails."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = False

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await reject_system_design(
                case_id="test-case-123",
                reject_request=system_design_reject_request,
                current_user=mock_current_user_developer,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == 500
        assert "Failed to reject system design" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_system_design_general_exception(
        self, mock_current_user_owner, mock_firestore_service, system_design_update_request, caplog
    ):
        """Test system design update with unexpected exception."""
        # Setup
        mock_firestore_service.get_business_case.side_effect = Exception("Database connection lost")

        # Ensure ERROR level logging is captured  
        with LogLevelContext('app.api.v1.cases.system_design_routes', 'ERROR'):
            # Execute & Verify
            with pytest.raises(HTTPException) as exc_info:
                await update_system_design(
                    case_id="test-case-123",
                    system_design_request=system_design_update_request,
                    current_user=mock_current_user_owner,
                    firestore_service=mock_firestore_service
                )
        
        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert "Failed to update system design" in str(exc_info.value.detail)
        
        # Verify error logging
        assert_log_contains(
            caplog,
            "ERROR",
            "Error updating system design for case test-case-123, user test-user-456",
            "app.api.v1.cases.system_design_routes"
        )
