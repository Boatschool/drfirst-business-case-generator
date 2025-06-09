"""
Unit tests for effort estimation API routes.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone
from fastapi import HTTPException

from app.api.v1.cases.effort_routes import (
    approve_effort_estimate,
    reject_effort_estimate,
    update_effort_estimate,
    generate_effort_estimate
)
from app.agents.orchestrator_agent import BusinessCaseStatus
from app.api.v1.cases.models import EffortEstimateUpdateRequest, EffortEstimateRejectRequest


class TestEffortEstimationRoutesUnit:
    """Unit tests for effort estimation API routes"""

    @pytest.fixture
    def mock_business_case(self):
        """Mock business case object"""
        mock_case = Mock()
        mock_case.user_id = "test-user-456"
        mock_case.title = "Test Business Case"
        mock_case.status = BusinessCaseStatus.EFFORT_PENDING_REVIEW
        mock_case.history = []
        mock_case.effort_estimate_v1 = {
            "roles": [
                {"role": "Product Manager", "hours": 40},
                {"role": "Lead Developer", "hours": 120}
            ],
            "total_hours": 160,
            "estimated_duration_weeks": 4,
            "complexity_assessment": "Medium",
            "notes": "Test effort estimate"
        }
        return mock_case

    @pytest.fixture
    def mock_current_user_owner(self):
        """Mock current user who owns the business case"""
        return {
            "uid": "test-user-456",
            "email": "owner@example.com",
            "custom_claims": {"role": "USER"},
            "systemRole": "USER"
        }

    @pytest.fixture
    def mock_current_user_approver(self):
        """Mock current user with approver role"""
        return {
            "uid": "approver-user-789",
            "email": "approver@example.com",
            "custom_claims": {"role": "DEVELOPER"},
            "systemRole": "DEVELOPER"
        }

    @pytest.fixture
    def mock_firestore_service(self):
        """Mock Firestore service"""
        mock_service = Mock()
        mock_service.get_business_case = AsyncMock()
        mock_service.update_business_case = AsyncMock()
        return mock_service

    @pytest.fixture
    def effort_update_request(self):
        """Sample effort estimate update request"""
        return EffortEstimateUpdateRequest(
            roles=[
                {"role_name": "Product Manager", "hours": 50},
                {"role_name": "Lead Developer", "hours": 140}
            ],
            total_hours=190,
            estimated_duration_weeks=5,
            complexity_assessment="Updated complexity assessment with detailed analysis",
            notes="Updated effort estimate"
        )

    @pytest.fixture
    def effort_reject_request(self):
        """Sample effort estimate rejection request"""
        return EffortEstimateRejectRequest(reason="Effort estimate is too high")

    # ============================================================================
    # Approve Effort Estimate Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_approve_effort_estimate_success(
        self, mock_business_case, mock_current_user_approver, mock_firestore_service
    ):
        """Test successful effort estimate approval with orchestrator integration."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.EFFORT_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Mock the orchestrator
        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_effort_approval = AsyncMock(return_value={
                "status": "success",
                "new_status": BusinessCaseStatus.COSTING_PENDING_REVIEW.value
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            # Mock approval permissions
            with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
                mock_check_perms.return_value = None  # No exception means approved
                
                # Execute
                result = await approve_effort_estimate(
                    case_id="test-case-123",
                    current_user=mock_current_user_approver,
                    firestore_service=mock_firestore_service
                )

                # Assertions
                assert "approved successfully and cost analysis initiated" in result["message"]
                assert result["new_status"] == BusinessCaseStatus.COSTING_PENDING_REVIEW.value
                assert result["case_id"] == "test-case-123"
                assert result["cost_analysis_initiated"] is True

                # Verify orchestrator was called
                mock_orchestrator.handle_effort_approval.assert_called_once_with("test-case-123")

    @pytest.mark.asyncio
    async def test_approve_effort_estimate_orchestrator_failure(
        self, mock_business_case, mock_current_user_approver, mock_firestore_service
    ):
        """Test effort estimate approval with orchestrator failure."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.EFFORT_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Mock the orchestrator with failure
        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_effort_approval = AsyncMock(return_value={
                "status": "error",
                "message": "CostAnalystAgent failed"
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            # Mock approval permissions
            with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
                mock_check_perms.return_value = None
                
                # Execute
                result = await approve_effort_estimate(
                    case_id="test-case-123",
                    current_user=mock_current_user_approver,
                    firestore_service=mock_firestore_service
                )

                # Assertions
                assert "approved successfully but cost analysis encountered an issue" in result["message"]
                assert result["new_status"] == BusinessCaseStatus.EFFORT_APPROVED.value
                assert result["cost_analysis_initiated"] is False
                assert "cost_analysis_error" in result

    @pytest.mark.asyncio
    async def test_approve_effort_estimate_unauthorized(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service
    ):
        """Test effort estimate approval by unauthorized user."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.EFFORT_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case

        # Mock approval permissions to raise exception
        with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
            mock_check_perms.side_effect = HTTPException(status_code=403, detail="Access denied")
            
            # Execute & Verify
            with pytest.raises(HTTPException) as exc_info:
                await approve_effort_estimate(
                    case_id="test-case-123",
                    current_user=mock_current_user_owner,
                    firestore_service=mock_firestore_service
                )

            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_approve_effort_estimate_invalid_status(
        self, mock_business_case, mock_current_user_approver, mock_firestore_service
    ):
        """Test effort estimate approval from invalid status."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.PLANNING_COMPLETE  # Invalid status
        mock_firestore_service.get_business_case.return_value = mock_business_case

        # Mock approval permissions
        with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
            mock_check_perms.return_value = None
            
            # Execute & Verify
            with pytest.raises(HTTPException) as exc_info:
                await approve_effort_estimate(
                    case_id="test-case-123",
                    current_user=mock_current_user_approver,
                    firestore_service=mock_firestore_service
                )

            assert exc_info.value.status_code == 400
            assert "Cannot approve effort estimate from current status" in str(exc_info.value.detail)

    # ============================================================================
    # Reject Effort Estimate Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_reject_effort_estimate_success_with_reason(
        self, mock_business_case, mock_current_user_approver, mock_firestore_service, effort_reject_request
    ):
        """Test successful effort estimate rejection with reason."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.EFFORT_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Mock approval permissions
        with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
            mock_check_perms.return_value = None
            
            # Execute
            result = await reject_effort_estimate(
                case_id="test-case-123",
                reject_request=effort_reject_request,
                current_user=mock_current_user_approver,
                firestore_service=mock_firestore_service
            )

            # Assertions
            assert result["message"] == "Effort estimate rejected successfully"
            assert result["new_status"] == BusinessCaseStatus.EFFORT_REJECTED.value
            assert result["case_id"] == "test-case-123"
            assert result["rejection_reason"] == "Effort estimate is too high"

    @pytest.mark.asyncio
    async def test_reject_effort_estimate_without_reason(
        self, mock_business_case, mock_current_user_approver, mock_firestore_service
    ):
        """Test effort estimate rejection without reason."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.EFFORT_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Create empty reject request
        empty_reject_request = EffortEstimateRejectRequest()

        # Mock approval permissions
        with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
            mock_check_perms.return_value = None
            
            # Execute
            result = await reject_effort_estimate(
                case_id="test-case-123",
                reject_request=empty_reject_request,
                current_user=mock_current_user_approver,
                firestore_service=mock_firestore_service
            )

            # Assertions
            assert result["message"] == "Effort estimate rejected successfully"
            assert result["rejection_reason"] is None

    # ============================================================================
    # Update Effort Estimate Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_update_effort_estimate_success(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service, effort_update_request
    ):
        """Test successful effort estimate update by owner."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.EFFORT_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Execute
        result = await update_effort_estimate(
            case_id="test-case-123",
            effort_update_request=effort_update_request,
            current_user=mock_current_user_owner,
            firestore_service=mock_firestore_service
        )

        # Assertions
        assert result["message"] == "Effort estimate updated successfully"
        assert result["case_id"] == "test-case-123"
        assert "updated_effort_estimate" in result

    @pytest.mark.asyncio
    async def test_update_effort_estimate_unauthorized(
        self, mock_business_case, mock_current_user_approver, mock_firestore_service, effort_update_request
    ):
        """Test effort estimate update by non-owner."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.EFFORT_PENDING_REVIEW
        mock_business_case.user_id = "different-user"  # Different from current user
        mock_firestore_service.get_business_case.return_value = mock_business_case

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await update_effort_estimate(
                case_id="test-case-123",
                effort_update_request=effort_update_request,
                current_user=mock_current_user_approver,
                firestore_service=mock_firestore_service
            )

        assert exc_info.value.status_code == 403
        assert "do not have permission to update" in str(exc_info.value.detail)

    # ============================================================================
    # Generate Effort Estimate Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_generate_effort_estimate_success(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service
    ):
        """Test successful effort estimate generation."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.SYSTEM_DESIGN_APPROVED
        mock_business_case.effort_estimate_v1 = None  # No existing estimate
        mock_firestore_service.get_business_case.return_value = mock_business_case

        # Mock the orchestrator
        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_system_design_approval = AsyncMock(return_value={
                "status": "success",
                "new_status": BusinessCaseStatus.EFFORT_PENDING_REVIEW.value
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            # Execute
            result = await generate_effort_estimate(
                case_id="test-case-123",
                current_user=mock_current_user_owner,
                firestore_service=mock_firestore_service
            )

            # Assertions
            assert "Effort estimate generation triggered successfully" in result["message"]
            assert result["new_status"] == BusinessCaseStatus.EFFORT_PENDING_REVIEW.value
            assert result["case_id"] == "test-case-123"

    @pytest.mark.asyncio
    async def test_generate_effort_estimate_already_exists(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service
    ):
        """Test effort estimate generation when estimate already exists."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.SYSTEM_DESIGN_APPROVED
        # effort_estimate_v1 already exists (from fixture)
        mock_firestore_service.get_business_case.return_value = mock_business_case

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await generate_effort_estimate(
                case_id="test-case-123",
                current_user=mock_current_user_owner,
                firestore_service=mock_firestore_service
            )

        assert exc_info.value.status_code == 409
        assert "already exists" in str(exc_info.value.detail)

    # ============================================================================
    # General Error Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_user_without_uid(self, mock_firestore_service):
        """Test API calls with user missing UID."""
        invalid_user = {"email": "test@example.com"}  # Missing uid

        with pytest.raises(HTTPException) as exc_info:
            await approve_effort_estimate(
                case_id="test-case-123",
                current_user=invalid_user,
                firestore_service=mock_firestore_service
            )

        assert exc_info.value.status_code == 401
        assert "User ID not found in token" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_case_not_found(
        self, mock_current_user_approver, mock_firestore_service
    ):
        """Test API calls when case doesn't exist."""
        # Setup
        mock_firestore_service.get_business_case.return_value = None

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await approve_effort_estimate(
                case_id="nonexistent-case",
                current_user=mock_current_user_approver,
                firestore_service=mock_firestore_service
            )

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_firestore_update_failure(
        self, mock_business_case, mock_current_user_approver, mock_firestore_service
    ):
        """Test API calls when Firestore update fails."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.EFFORT_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = False  # Simulate failure

        # Mock approval permissions
        with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
            mock_check_perms.return_value = None
            
            # Execute & Verify
            with pytest.raises(HTTPException) as exc_info:
                await approve_effort_estimate(
                    case_id="test-case-123",
                    current_user=mock_current_user_approver,
                    firestore_service=mock_firestore_service
                )

            assert exc_info.value.status_code == 500
            assert "Failed to approve effort estimate" in str(exc_info.value.detail) 