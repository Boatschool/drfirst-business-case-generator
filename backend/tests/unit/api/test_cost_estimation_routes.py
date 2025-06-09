"""
Unit tests for cost estimation API routes.
Tests the cost estimate approval and rejection functionality.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone
from fastapi import HTTPException

from app.api.v1.cases.financial_estimates_routes import (
    approve_cost_estimate,
    reject_cost_estimate
)
from app.agents.orchestrator_agent import BusinessCaseStatus
from app.api.v1.cases.models import CostEstimateRejectRequest


class TestCostEstimationRoutesUnit:
    """Unit tests for cost estimation API routes"""

    @pytest.fixture
    def mock_business_case(self):
        """Mock business case object with cost estimate"""
        mock_case = Mock()
        mock_case.user_id = "test-user-456"
        mock_case.title = "Test Business Case"
        mock_case.status = BusinessCaseStatus.COSTING_PENDING_REVIEW
        mock_case.history = []
        mock_case.cost_estimate_v1 = {
            "estimated_cost": 35000.00,
            "currency": "USD",
            "rate_card_used": "Standard 2024 Rates",
            "breakdown_by_role": [
                {
                    "role": "Product Manager",
                    "hours": 40,
                    "hourly_rate": 150.0,
                    "total_cost": 6000.0,
                    "currency": "USD"
                },
                {
                    "role": "Lead Developer", 
                    "hours": 120,
                    "hourly_rate": 175.0,
                    "total_cost": 21000.0,
                    "currency": "USD"
                }
            ],
            "calculation_method": "Based on effort estimate and standard rates",
            "notes": "Test cost estimate"
        }
        return mock_case

    @pytest.fixture
    def mock_current_user_finance_approver(self):
        """Mock current user with finance approver role"""
        return {
            "uid": "finance-user-789",
            "email": "finance@example.com",
            "custom_claims": {"role": "FINANCE_APPROVER"},
            "systemRole": "FINANCE_APPROVER"
        }

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
    def mock_current_user_admin(self):
        """Mock current user with admin role"""
        return {
            "uid": "admin-user-123",
            "email": "admin@example.com",
            "custom_claims": {"role": "ADMIN"},
            "systemRole": "ADMIN"
        }

    @pytest.fixture
    def mock_firestore_service(self):
        """Mock Firestore service"""
        mock_service = Mock()
        mock_service.get_business_case = AsyncMock()
        mock_service.update_business_case = AsyncMock()
        return mock_service

    # ============================================================================
    # Approve Cost Estimate Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_approve_cost_estimate_success_with_value_analysis(
        self, mock_business_case, mock_current_user_finance_approver, mock_firestore_service
    ):
        """Test successful cost estimate approval with value analysis generation."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.COSTING_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Mock the orchestrator with successful value analysis
        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_cost_approval = AsyncMock(return_value={
                "status": "success",
                "message": "Value projection generated and ready for review.",
                "new_status": BusinessCaseStatus.VALUE_PENDING_REVIEW.value
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            # Mock approval permissions
            with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
                mock_check_perms.return_value = None  # No exception means approved
                
                # Execute
                result = await approve_cost_estimate(
                    case_id="test-case-123",
                    current_user=mock_current_user_finance_approver,
                    firestore_service=mock_firestore_service
                )

                # Assertions
                assert "approved successfully and value analysis generation initiated" in result["message"]
                assert result["new_status"] == BusinessCaseStatus.VALUE_PENDING_REVIEW.value
                assert result["case_id"] == "test-case-123"
                assert result["value_analysis_initiated"] is True

                # Verify orchestrator was called with correct method
                mock_orchestrator.handle_cost_approval.assert_called_once_with("test-case-123")

    @pytest.mark.asyncio
    async def test_approve_cost_estimate_invalid_status(
        self, mock_business_case, mock_current_user_finance_approver, mock_firestore_service
    ):
        """Test cost estimate approval from invalid status."""
        # Setup - wrong status
        mock_business_case.status = BusinessCaseStatus.COSTING_COMPLETE  # Should be COSTING_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case

        # Mock approval permissions
        with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
            mock_check_perms.return_value = None
            
            # Execute & Verify
            with pytest.raises(HTTPException) as exc_info:
                await approve_cost_estimate(
                    case_id="test-case-123",
                    current_user=mock_current_user_finance_approver,
                    firestore_service=mock_firestore_service
                )

            assert exc_info.value.status_code == 400
            assert "COSTING_PENDING_REVIEW" in str(exc_info.value.detail)

    # ============================================================================
    # Reject Cost Estimate Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_reject_cost_estimate_success_with_reason(
        self, mock_business_case, mock_current_user_finance_approver, mock_firestore_service
    ):
        """Test successful cost estimate rejection with reason."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.COSTING_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        reject_request = CostEstimateRejectRequest(reason="Cost estimate is too high for current budget")

        # Mock approval permissions
        with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
            mock_check_perms.return_value = None
            
            # Execute
            result = await reject_cost_estimate(
                case_id="test-case-123",
                reject_request=reject_request,
                current_user=mock_current_user_finance_approver,
                firestore_service=mock_firestore_service
            )

            # Assertions
            assert "rejected successfully" in result["message"]
            assert result["new_status"] == BusinessCaseStatus.COSTING_REJECTED.value
            assert result["case_id"] == "test-case-123"

            # Verify update was called with history including reason
            mock_firestore_service.update_business_case.assert_called_once()
            update_call_args = mock_firestore_service.update_business_case.call_args[0]
            update_data = update_call_args[1]
            
            assert update_data["status"] == BusinessCaseStatus.COSTING_REJECTED.value
            # Check that reason is included in history
            history_entry = update_data["history"][0]
            assert reject_request.reason in history_entry["content"]

    @pytest.mark.asyncio
    async def test_reject_cost_estimate_without_reason(
        self, mock_business_case, mock_current_user_admin, mock_firestore_service
    ):
        """Test cost estimate rejection without reason (admin override)."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.COSTING_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Mock approval permissions (admin)
        with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
            mock_check_perms.return_value = None
            
            # Execute with empty request
            empty_request = CostEstimateRejectRequest()
            result = await reject_cost_estimate(
                case_id="test-case-123",
                reject_request=empty_request,
                current_user=mock_current_user_admin,
                firestore_service=mock_firestore_service
            )

            # Assertions
            assert "rejected successfully" in result["message"]
            assert result["new_status"] == BusinessCaseStatus.COSTING_REJECTED.value

            # Verify history doesn't include reason
            update_call_args = mock_firestore_service.update_business_case.call_args[0]
            update_data = update_call_args[1]
            history_entry = update_data["history"][0]
            assert "Reason:" not in history_entry["content"]

    @pytest.mark.asyncio
    async def test_reject_cost_estimate_unauthorized(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service
    ):
        """Test cost estimate rejection by unauthorized user."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.COSTING_PENDING_REVIEW
        mock_business_case.user_id = "different-user-789"  # Different from current user
        mock_firestore_service.get_business_case.return_value = mock_business_case

        reject_request = CostEstimateRejectRequest(reason="Unauthorized rejection")

        # Mock approval permissions to raise exception
        with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
            mock_check_perms.side_effect = HTTPException(status_code=403, detail="Access denied")
            
            # Execute & Verify
            with pytest.raises(HTTPException) as exc_info:
                await reject_cost_estimate(
                    case_id="test-case-123",
                    reject_request=reject_request,
                    current_user=mock_current_user_owner,
                    firestore_service=mock_firestore_service
                )

            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_reject_cost_estimate_invalid_status(
        self, mock_business_case, mock_current_user_finance_approver, mock_firestore_service
    ):
        """Test cost estimate rejection from invalid status."""
        # Setup - wrong status
        mock_business_case.status = BusinessCaseStatus.COSTING_APPROVED  # Should be COSTING_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case

        reject_request = CostEstimateRejectRequest(reason="Invalid status test")

        # Mock approval permissions
        with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
            mock_check_perms.return_value = None
            
            # Execute & Verify
            with pytest.raises(HTTPException) as exc_info:
                await reject_cost_estimate(
                    case_id="test-case-123",
                    reject_request=reject_request,
                    current_user=mock_current_user_finance_approver,
                    firestore_service=mock_firestore_service
                )

            assert exc_info.value.status_code == 400
            assert "COSTING_PENDING_REVIEW" in str(exc_info.value.detail)

    # ============================================================================
    # Error Handling Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_approve_cost_estimate_no_user_id(self, mock_firestore_service):
        """Test cost estimate approval with missing user ID."""
        # Setup user without uid
        invalid_user = {
            "email": "test@example.com",
            "systemRole": "FINANCE_APPROVER"
        }
        
        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await approve_cost_estimate(
                case_id="test-case-123",
                current_user=invalid_user,
                firestore_service=mock_firestore_service
            )

        assert exc_info.value.status_code == 401
        assert "User ID not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_reject_cost_estimate_firestore_failure(
        self, mock_business_case, mock_current_user_finance_approver, mock_firestore_service
    ):
        """Test cost estimate rejection with Firestore update failure."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.COSTING_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = False  # Simulate failure

        reject_request = CostEstimateRejectRequest(reason="Firestore failure test")

        # Mock approval permissions
        with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
            mock_check_perms.return_value = None
            
            # Execute & Verify
            with pytest.raises(HTTPException) as exc_info:
                await reject_cost_estimate(
                    case_id="test-case-123",
                    reject_request=reject_request,
                    current_user=mock_current_user_finance_approver,
                    firestore_service=mock_firestore_service
                )

            assert exc_info.value.status_code == 500
            assert "Failed to reject cost estimate" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_approve_cost_estimate_orchestrator_exception(
        self, mock_business_case, mock_current_user_finance_approver, mock_firestore_service
    ):
        """Test cost estimate approval with orchestrator exception."""
        # Setup
        mock_business_case.status = BusinessCaseStatus.COSTING_PENDING_REVIEW
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Mock the orchestrator to raise exception
        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_cost_approval = AsyncMock(side_effect=Exception("Network timeout"))
            mock_orchestrator_class.return_value = mock_orchestrator

            # Mock approval permissions
            with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
                mock_check_perms.return_value = None
                
                # Execute
                result = await approve_cost_estimate(
                    case_id="test-case-123",
                    current_user=mock_current_user_finance_approver,
                    firestore_service=mock_firestore_service
                )

                # Should handle exception gracefully
                assert "approved successfully but value analysis generation could not be initiated" in result["message"]
                assert result["new_status"] == BusinessCaseStatus.COSTING_APPROVED.value
                assert result["value_analysis_initiated"] is False
                assert "Network timeout" in result["value_analysis_error"]

    # ============================================================================
    # Edge Cases and Integration Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_approve_cost_estimate_owner_self_approval(
        self, mock_business_case, mock_current_user_owner, mock_firestore_service
    ):
        """Test cost estimate approval by case owner (self-approval)."""
        # Setup - user is the case owner
        mock_business_case.status = BusinessCaseStatus.COSTING_PENDING_REVIEW
        mock_business_case.user_id = mock_current_user_owner["uid"]  # Same user
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Mock orchestrator success
        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_cost_approval = AsyncMock(return_value={
                "status": "success",
                "new_status": BusinessCaseStatus.VALUE_PENDING_REVIEW.value
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            # Mock approval permissions (should allow self-approval)
            with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
                mock_check_perms.return_value = None
                
                # Execute
                result = await approve_cost_estimate(
                    case_id="test-case-123",
                    current_user=mock_current_user_owner,
                    firestore_service=mock_firestore_service
                )

                # Should succeed with self-approval
                assert "approved successfully" in result["message"]
                assert result["case_id"] == "test-case-123"

    @pytest.mark.asyncio 
    async def test_cost_estimate_operations_status_validation(
        self, mock_business_case, mock_current_user_finance_approver, mock_firestore_service
    ):
        """Test that cost estimate operations validate status correctly."""
        # Test various invalid statuses
        invalid_statuses = [
            BusinessCaseStatus.EFFORT_PENDING_REVIEW,
            BusinessCaseStatus.COSTING_IN_PROGRESS,
            BusinessCaseStatus.COSTING_COMPLETE,
            BusinessCaseStatus.COSTING_APPROVED,
            BusinessCaseStatus.VALUE_PENDING_REVIEW
        ]

        for invalid_status in invalid_statuses:
            mock_business_case.status = invalid_status
            mock_firestore_service.get_business_case.return_value = mock_business_case

            # Mock approval permissions
            with patch('app.utils.approval_permissions.check_approval_permissions') as mock_check_perms:
                mock_check_perms.return_value = None
                
                            # Both approve and reject should fail with invalid status
            with pytest.raises(HTTPException) as exc_info:
                await approve_cost_estimate(
                    case_id="test-case-123",
                    current_user=mock_current_user_finance_approver,
                    firestore_service=mock_firestore_service
                )
            assert exc_info.value.status_code == 400
            assert "COSTING_PENDING_REVIEW" in str(exc_info.value.detail)

            with pytest.raises(HTTPException) as exc_info:
                await reject_cost_estimate(
                    case_id="test-case-123", 
                    reject_request=CostEstimateRejectRequest(reason="Status validation test"),
                    current_user=mock_current_user_finance_approver,
                    firestore_service=mock_firestore_service
                )
            assert exc_info.value.status_code == 400
            assert "COSTING_PENDING_REVIEW" in str(exc_info.value.detail) 