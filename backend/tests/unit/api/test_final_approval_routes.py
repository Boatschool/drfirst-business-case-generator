"""
Unit tests for final approval API endpoints.
Tests all final approval operations and authorization logic.
Includes comprehensive error handling and permission validation.
"""

import pytest
import pytest_asyncio
import logging
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from app.api.v1.cases.final_approval_routes import (
    submit_case_for_final_approval,
    approve_final_case,
    reject_final_case
)
from app.api.v1.cases.models import FinalRejectRequest
from app.agents.orchestrator_agent import BusinessCaseStatus
from app.core.constants import HTTPStatus, ErrorMessages, MessageTypes, MessageSources
# Note: Simplified test without logging helpers that may not be available
# from tests.utils.logging_test_helpers import (
#     assert_log_contains,
#     assert_workflow_logging_sequence,
#     LogLevelContext
# )


class TestFinalApprovalRoutesUnit:
    """Unit test suite for final approval API routes."""

    @pytest.fixture
    def mock_business_case_ready_for_final(self):
        """Create a mock business case ready for final approval submission."""
        case = Mock()
        case.case_id = "test-case-123"
        case.user_id = "test-user-456"
        case.title = "Test Business Case"
        case.status = BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE
        case.history = []
        case.financial_model = {
            "summary": "Financial model complete",
            "generated_by": "FinancialModelAgent",
            "generated_timestamp": "2024-01-01T00:00:00Z"
        }
        return case

    @pytest.fixture
    def mock_business_case_pending_final_approval(self):
        """Create a mock business case pending final approval."""
        case = Mock()
        case.case_id = "test-case-456"
        case.user_id = "test-user-456"
        case.title = "Test Business Case Pending Approval"
        case.status = BusinessCaseStatus.PENDING_FINAL_APPROVAL
        case.history = []
        case.financial_model = {
            "summary": "Financial model complete",
            "generated_by": "FinancialModelAgent",
            "generated_timestamp": "2024-01-01T00:00:00Z"
        }
        return case

    @pytest.fixture
    def mock_current_user_case_owner(self):
        """Create a mock current user who is the case owner."""
        return {
            "uid": "test-user-456",
            "email": "owner@example.com",
            "systemRole": "USER",
            "custom_claims": {"role": "USER"}
        }

    @pytest.fixture
    def mock_current_user_admin(self):
        """Create a mock current user with ADMIN role."""
        return {
            "uid": "admin-user-789",
            "email": "admin@example.com",
            "systemRole": "ADMIN",
            "custom_claims": {"role": "ADMIN"}
        }

    @pytest.fixture
    def mock_current_user_final_approver(self):
        """Create a mock current user with FINAL_APPROVER role."""
        return {
            "uid": "approver-user-999",
            "email": "approver@example.com",
            "systemRole": "FINAL_APPROVER",
            "custom_claims": {"role": "FINAL_APPROVER"}
        }

    @pytest.fixture
    def mock_current_user_unauthorized(self):
        """Create a mock current user with no permissions."""
        return {
            "uid": "unauthorized-user-111",
            "email": "unauthorized@example.com",
            "systemRole": "USER",
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
    def final_reject_request(self):
        """Create a final rejection request."""
        return FinalRejectRequest(
            reason="The business case does not meet our current strategic priorities."
        )

    @pytest.fixture
    def final_reject_request_no_reason(self):
        """Create a final rejection request without reason."""
        return FinalRejectRequest()

    # ============================================================================
    # Submit Case for Final Approval Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_submit_final_approval_success(
        self, mock_business_case_ready_for_final, mock_current_user_case_owner, mock_firestore_service
    ):
        """Test successful submission of case for final approval."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case_ready_for_final
        mock_firestore_service.update_business_case.return_value = True

        # Execute
        result = await submit_case_for_final_approval(
            case_id="test-case-123",
            current_user=mock_current_user_case_owner,
            firestore_service=mock_firestore_service
        )

        # Verify response
        assert result["message"] == "Business case submitted for final approval successfully"
        assert result["case_id"] == "test-case-123"
        assert result["new_status"] == BusinessCaseStatus.PENDING_FINAL_APPROVAL.value

        # Verify Firestore calls
        mock_firestore_service.get_business_case.assert_called_once_with("test-case-123")
        mock_firestore_service.update_business_case.assert_called_once()

    @pytest.mark.asyncio
    async def test_submit_final_approval_unauthorized_not_owner(
        self, mock_business_case_ready_for_final, mock_current_user_unauthorized, mock_firestore_service
    ):
        """Test submission rejection when user is not case owner."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case_ready_for_final

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await submit_case_for_final_approval(
                case_id="test-case-123",
                current_user=mock_current_user_unauthorized,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN
        assert "permission" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_submit_final_approval_wrong_status(
        self, mock_current_user_case_owner, mock_firestore_service
    ):
        """Test submission rejection when case is not in FINANCIAL_MODEL_COMPLETE status."""
        # Setup
        wrong_status_case = Mock()
        wrong_status_case.case_id = "test-case-123"
        wrong_status_case.user_id = "test-user-456"
        wrong_status_case.status = BusinessCaseStatus.PLANNING_COMPLETE
        mock_firestore_service.get_business_case.return_value = wrong_status_case

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await submit_case_for_final_approval(
                case_id="test-case-123",
                current_user=mock_current_user_case_owner,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
        assert "Must be in FINANCIAL_MODEL_COMPLETE status" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_submit_final_approval_case_not_found(
        self, mock_current_user_case_owner, mock_firestore_service
    ):
        """Test submission when case doesn't exist."""
        # Setup
        mock_firestore_service.get_business_case.return_value = None

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await submit_case_for_final_approval(
                case_id="non-existent-case",
                current_user=mock_current_user_case_owner,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_submit_final_approval_firestore_failure(
        self, mock_business_case_ready_for_final, mock_current_user_case_owner, mock_firestore_service, caplog
    ):
        """Test submission when Firestore update fails."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case_ready_for_final
        mock_firestore_service.update_business_case.side_effect = Exception("Firestore error")

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await submit_case_for_final_approval(
                case_id="test-case-123",
                current_user=mock_current_user_case_owner,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    # ============================================================================
    # Approve Final Case Tests
    # ============================================================================

    @pytest.mark.asyncio
    @patch("app.utils.approval_permissions.check_final_approval_permissions")
    async def test_approve_final_case_success_admin(
        self, mock_check_permissions, mock_business_case_pending_final_approval, 
        mock_current_user_admin, mock_firestore_service
    ):
        """Test successful final approval by ADMIN user."""
        # Setup
        mock_check_permissions.return_value = None  # No exception means authorized
        mock_firestore_service.get_business_case.return_value = mock_business_case_pending_final_approval
        mock_firestore_service.update_business_case.return_value = True

        # Execute
        result = await approve_final_case(
            case_id="test-case-456",
            current_user=mock_current_user_admin,
            firestore_service=mock_firestore_service
        )

        # Verify response
        assert result["message"] == "Business Case approved successfully"
        assert result["case_id"] == "test-case-456"
        assert result["new_status"] == BusinessCaseStatus.APPROVED.value

        # Verify authorization check
        mock_check_permissions.assert_called_once_with(
            mock_current_user_admin, 
            mock_business_case_pending_final_approval.user_id
        )

        # Verify Firestore calls
        mock_firestore_service.get_business_case.assert_called_once_with("test-case-456")
        mock_firestore_service.update_business_case.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.utils.approval_permissions.check_final_approval_permissions")
    async def test_approve_final_case_success_final_approver(
        self, mock_check_permissions, mock_business_case_pending_final_approval, 
        mock_current_user_final_approver, mock_firestore_service
    ):
        """Test successful final approval by FINAL_APPROVER user."""
        # Setup
        mock_check_permissions.return_value = None  # No exception means authorized
        mock_firestore_service.get_business_case.return_value = mock_business_case_pending_final_approval
        mock_firestore_service.update_business_case.return_value = True

        # Execute
        result = await approve_final_case(
            case_id="test-case-456",
            current_user=mock_current_user_final_approver,
            firestore_service=mock_firestore_service
        )

        # Verify
        assert result["message"] == "Business Case approved successfully"
        assert result["new_status"] == BusinessCaseStatus.APPROVED.value

    @pytest.mark.asyncio
    @patch("app.utils.approval_permissions.check_final_approval_permissions")
    async def test_approve_final_case_unauthorized(
        self, mock_check_permissions, mock_business_case_pending_final_approval, 
        mock_current_user_unauthorized, mock_firestore_service
    ):
        """Test approval rejection when user lacks permissions."""
        # Setup
        mock_check_permissions.side_effect = HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Access denied for final approval"
        )
        mock_firestore_service.get_business_case.return_value = mock_business_case_pending_final_approval

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await approve_final_case(
                case_id="test-case-456",
                current_user=mock_current_user_unauthorized,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN

    @pytest.mark.asyncio
    @patch("app.utils.approval_permissions.check_final_approval_permissions")
    async def test_approve_final_case_wrong_status(
        self, mock_check_permissions, mock_current_user_admin, mock_firestore_service
    ):
        """Test approval rejection when case is not in PENDING_FINAL_APPROVAL status."""
        # Setup
        mock_check_permissions.return_value = None
        wrong_status_case = Mock()
        wrong_status_case.case_id = "test-case-456"
        wrong_status_case.user_id = "test-user-456"
        wrong_status_case.status = BusinessCaseStatus.PLANNING_COMPLETE
        mock_firestore_service.get_business_case.return_value = wrong_status_case

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await approve_final_case(
                case_id="test-case-456",
                current_user=mock_current_user_admin,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
        assert "Must be in PENDING_FINAL_APPROVAL status" in str(exc_info.value.detail)

    # ============================================================================
    # Reject Final Case Tests
    # ============================================================================

    @pytest.mark.asyncio
    @patch("app.utils.approval_permissions.check_final_approval_permissions")
    async def test_reject_final_case_success_with_reason(
        self, mock_check_permissions, mock_business_case_pending_final_approval, 
        mock_current_user_admin, mock_firestore_service, final_reject_request
    ):
        """Test successful final rejection with reason."""
        # Setup
        mock_check_permissions.return_value = None
        mock_firestore_service.get_business_case.return_value = mock_business_case_pending_final_approval
        mock_firestore_service.update_business_case.return_value = True

        # Execute
        result = await reject_final_case(
            case_id="test-case-456",
            reject_request=final_reject_request,
            current_user=mock_current_user_admin,
            firestore_service=mock_firestore_service
        )

        # Verify response
        assert result["message"] == "Business Case rejected successfully"
        assert result["case_id"] == "test-case-456"
        assert result["new_status"] == BusinessCaseStatus.REJECTED.value

    @pytest.mark.asyncio
    @patch("app.utils.approval_permissions.check_final_approval_permissions")
    async def test_reject_final_case_success_no_reason(
        self, mock_check_permissions, mock_business_case_pending_final_approval, 
        mock_current_user_admin, mock_firestore_service, final_reject_request_no_reason
    ):
        """Test successful final rejection without reason."""
        # Setup
        mock_check_permissions.return_value = None
        mock_firestore_service.get_business_case.return_value = mock_business_case_pending_final_approval
        mock_firestore_service.update_business_case.return_value = True

        # Execute
        result = await reject_final_case(
            case_id="test-case-456",
            reject_request=final_reject_request_no_reason,
            current_user=mock_current_user_admin,
            firestore_service=mock_firestore_service
        )

        # Verify
        assert result["message"] == "Business Case rejected successfully"
        assert result["new_status"] == BusinessCaseStatus.REJECTED.value

    @pytest.mark.asyncio
    @patch("app.utils.approval_permissions.check_final_approval_permissions")
    async def test_reject_final_case_unauthorized(
        self, mock_check_permissions, mock_business_case_pending_final_approval, 
        mock_current_user_unauthorized, mock_firestore_service, final_reject_request
    ):
        """Test rejection when user lacks permissions."""
        # Setup
        mock_check_permissions.side_effect = HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Access denied for final approval"
        )
        mock_firestore_service.get_business_case.return_value = mock_business_case_pending_final_approval

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await reject_final_case(
                case_id="test-case-456",
                reject_request=final_reject_request,
                current_user=mock_current_user_unauthorized,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN

    # ============================================================================
    # General Error Handling Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_submit_final_approval_user_without_uid(
        self, mock_firestore_service, mock_business_case_ready_for_final
    ):
        """Test submission with user missing uid."""
        # Setup
        user_without_uid = {"email": "test@example.com"}
        mock_firestore_service.get_business_case.return_value = mock_business_case_ready_for_final

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await submit_case_for_final_approval(
                case_id="test-case-123",
                current_user=user_without_uid,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == 401  # UNAUTHORIZED

    @pytest.mark.asyncio
    @patch("app.utils.approval_permissions.check_final_approval_permissions")
    async def test_approve_final_case_general_exception(
        self, mock_check_permissions, mock_current_user_admin, mock_firestore_service
    ):
        """Test approval with unexpected exception."""
        # Setup
        mock_check_permissions.return_value = None
        mock_firestore_service.get_business_case.side_effect = Exception("Unexpected error")

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await approve_final_case(
                case_id="test-case-456",
                current_user=mock_current_user_admin,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    @patch("app.utils.approval_permissions.check_final_approval_permissions")
    async def test_reject_final_case_firestore_failure(
        self, mock_check_permissions, mock_business_case_pending_final_approval, 
        mock_current_user_admin, mock_firestore_service, final_reject_request
    ):
        """Test rejection when Firestore update fails."""
        # Setup
        mock_check_permissions.return_value = None
        mock_firestore_service.get_business_case.return_value = mock_business_case_pending_final_approval
        mock_firestore_service.update_business_case.side_effect = Exception("Firestore error")

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await reject_final_case(
                case_id="test-case-456",
                reject_request=final_reject_request,
                current_user=mock_current_user_admin,
                firestore_service=mock_firestore_service
            )
        
        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR 