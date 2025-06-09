"""
Unit tests for approval permissions utility functions.
Tests authorization logic for final approval workflow.
Includes comprehensive permission validation scenarios.
"""

import pytest
import pytest_asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from app.utils.approval_permissions import check_final_approval_permissions
from app.core.constants import HTTPStatus


class TestApprovalPermissions:
    """Unit test suite for approval permission checking."""

    @pytest.fixture
    def mock_admin_user(self):
        """Create a mock ADMIN user."""
        return {
            "uid": "admin-user-123",
            "email": "admin@example.com",
            "systemRole": "ADMIN"
        }

    @pytest.fixture
    def mock_final_approver_user(self):
        """Create a mock FINAL_APPROVER user."""
        return {
            "uid": "approver-user-456",
            "email": "approver@example.com",
            "systemRole": "FINAL_APPROVER"
        }

    @pytest.fixture
    def mock_case_owner_user(self):
        """Create a mock case owner user."""
        return {
            "uid": "owner-user-789",
            "email": "owner@example.com",
            "systemRole": "USER"
        }

    @pytest.fixture
    def mock_regular_user(self):
        """Create a mock regular user with no special permissions."""
        return {
            "uid": "regular-user-999",
            "email": "regular@example.com",
            "systemRole": "USER"
        }

    # ============================================================================
    # Admin User Authorization Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_check_final_approval_permissions_admin_user(self, mock_admin_user, caplog):
        """Test that ADMIN users are always authorized for final approval."""
        with caplog.at_level(logging.INFO):
            # Execute - should not raise exception
            await check_final_approval_permissions(mock_admin_user, "any-case-owner-id")

        # Verify logging
        assert "🔑 [FINAL_APPROVAL] ADMIN override" in caplog.text
        assert "admin@example.com approved for final approval" in caplog.text

    @pytest.mark.asyncio
    async def test_check_final_approval_permissions_admin_user_different_case_owner(self, mock_admin_user):
        """Test that ADMIN users can approve cases they don't own."""
        # Execute - should not raise exception for different case owner
        await check_final_approval_permissions(mock_admin_user, "different-owner-id")

    # ============================================================================
    # Case Owner Authorization Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_check_final_approval_permissions_case_owner(self, mock_case_owner_user, caplog):
        """Test that case owners are authorized for their own cases."""
        with caplog.at_level(logging.INFO):
            # Execute - should not raise exception when user owns the case
            await check_final_approval_permissions(mock_case_owner_user, "owner-user-789")

        # Verify logging
        assert "👤 [FINAL_APPROVAL] Case owner approval" in caplog.text
        assert "owner@example.com approved for final approval" in caplog.text

    @pytest.mark.asyncio
    async def test_check_final_approval_permissions_case_owner_different_case(self, mock_case_owner_user):
        """Test that case owners cannot approve cases they don't own."""
        # Execute & Verify - should raise exception for different case
        with pytest.raises(HTTPException) as exc_info:
            await check_final_approval_permissions(mock_case_owner_user, "different-owner-id")
        
        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN
        assert "Access denied for regular@example.com" in str(exc_info.value.detail)

    # ============================================================================
    # Role-Based Authorization Tests
    # ============================================================================

    @pytest.mark.asyncio
    @patch("app.services.firestore_service.FirestoreService")
    async def test_check_final_approval_permissions_final_approver_role(
        self, mock_firestore_service_class, mock_final_approver_user, caplog
    ):
        """Test that users with FINAL_APPROVER role are authorized."""
        # Setup mock Firestore service
        mock_service = Mock()
        mock_service.get_document = AsyncMock(return_value={
            "finalApproverRoleName": "FINAL_APPROVER"
        })
        mock_firestore_service_class.return_value = mock_service

        with caplog.at_level(logging.INFO):
            # Execute - should not raise exception
            await check_final_approval_permissions(mock_final_approver_user, "any-case-owner-id")

        # Verify logging
        assert "✅ [FINAL_APPROVAL] Role-based final approval" in caplog.text
        assert "approver@example.com (FINAL_APPROVER) approved for final approval" in caplog.text

    @pytest.mark.asyncio
    @patch("app.services.firestore_service.FirestoreService")
    async def test_check_final_approval_permissions_custom_approver_role(
        self, mock_firestore_service_class, caplog
    ):
        """Test authorization with custom final approver role configuration."""
        # Setup mock user with custom role
        custom_approver_user = {
            "uid": "custom-user-123",
            "email": "custom@example.com",
            "systemRole": "CUSTOM_APPROVER"
        }

        # Setup mock Firestore service with custom role
        mock_service = Mock()
        mock_service.get_document = AsyncMock(return_value={
            "finalApproverRoleName": "CUSTOM_APPROVER"
        })
        mock_firestore_service_class.return_value = mock_service

        with caplog.at_level(logging.INFO):
            # Execute - should not raise exception
            await check_final_approval_permissions(custom_approver_user, "any-case-owner-id")

        # Verify logging
        assert "✅ [FINAL_APPROVAL] Role-based final approval" in caplog.text
        assert "custom@example.com (CUSTOM_APPROVER) approved for final approval" in caplog.text

    @pytest.mark.asyncio
    @patch("app.services.firestore_service.FirestoreService")
    async def test_check_final_approval_permissions_wrong_role(
        self, mock_firestore_service_class, mock_regular_user
    ):
        """Test that users with wrong role are denied."""
        # Setup mock Firestore service
        mock_service = Mock()
        mock_service.get_document = AsyncMock(return_value={
            "finalApproverRoleName": "FINAL_APPROVER"
        })
        mock_firestore_service_class.return_value = mock_service

        # Execute & Verify - should raise exception
        with pytest.raises(HTTPException) as exc_info:
            await check_final_approval_permissions(mock_regular_user, "different-owner-id")
        
        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN
        assert "Access denied for regular@example.com" in str(exc_info.value.detail)

    # ============================================================================
    # Configuration Handling Tests
    # ============================================================================

    @pytest.mark.asyncio
    @patch("app.services.firestore_service.FirestoreService")
    async def test_check_final_approval_permissions_no_config_defaults_to_final_approver(
        self, mock_firestore_service_class, mock_final_approver_user, caplog
    ):
        """Test that missing configuration defaults to FINAL_APPROVER role."""
        # Setup mock Firestore service returning None (no config)
        mock_service = Mock()
        mock_service.get_document = AsyncMock(return_value=None)
        mock_firestore_service_class.return_value = mock_service

        with caplog.at_level(logging.INFO):
            # Execute - should not raise exception for FINAL_APPROVER
            await check_final_approval_permissions(mock_final_approver_user, "any-case-owner-id")

        # Verify logging shows default behavior
        assert "⚠️ [FINAL_APPROVAL] No final approver configuration found, using default: FINAL_APPROVER" in caplog.text

    @pytest.mark.asyncio
    @patch("app.services.firestore_service.FirestoreService")
    async def test_check_final_approval_permissions_config_error_defaults(
        self, mock_firestore_service_class, mock_final_approver_user, caplog
    ):
        """Test that configuration errors default to FINAL_APPROVER role."""
        # Setup mock Firestore service that raises an exception
        mock_service = Mock()
        mock_service.get_document = AsyncMock(side_effect=Exception("Firestore error"))
        mock_firestore_service_class.return_value = mock_service

        with caplog.at_level(logging.ERROR):
            # Execute - should not raise exception for FINAL_APPROVER
            await check_final_approval_permissions(mock_final_approver_user, "any-case-owner-id")

        # Verify error logging and fallback behavior
        assert "❌ [FINAL_APPROVAL] Error fetching final approver configuration" in caplog.text

    @pytest.mark.asyncio
    @patch("app.services.firestore_service.FirestoreService")
    async def test_check_final_approval_permissions_config_error_denies_wrong_role(
        self, mock_firestore_service_class, mock_regular_user
    ):
        """Test that configuration errors still deny unauthorized users."""
        # Setup mock Firestore service that raises an exception
        mock_service = Mock()
        mock_service.get_document = AsyncMock(side_effect=Exception("Firestore error"))
        mock_firestore_service_class.return_value = mock_service

        # Execute & Verify - should still raise exception for wrong role
        with pytest.raises(HTTPException) as exc_info:
            await check_final_approval_permissions(mock_regular_user, "different-owner-id")
        
        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN

    # ============================================================================
    # Edge Case Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_check_final_approval_permissions_user_without_uid(self):
        """Test error handling when user lacks uid."""
        user_without_uid = {
            "email": "test@example.com",
            "systemRole": "USER"
        }

        # Execute & Verify - should raise exception
        with pytest.raises(HTTPException) as exc_info:
            await check_final_approval_permissions(user_without_uid, "any-case-owner-id")
        
        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST

    @pytest.mark.asyncio
    async def test_check_final_approval_permissions_user_without_email(self):
        """Test error handling when user lacks email."""
        user_without_email = {
            "uid": "test-uid-123",
            "systemRole": "USER"
        }

        # Execute & Verify - should raise exception
        with pytest.raises(HTTPException) as exc_info:
            await check_final_approval_permissions(user_without_email, "any-case-owner-id")
        
        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST

    @pytest.mark.asyncio
    async def test_check_final_approval_permissions_user_without_role(self, caplog):
        """Test handling when user lacks systemRole."""
        user_without_role = {
            "uid": "test-uid-123",
            "email": "test@example.com"
        }

        # Execute & Verify - should raise exception
        with pytest.raises(HTTPException) as exc_info:
            await check_final_approval_permissions(user_without_role, "different-owner-id")
        
        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN

    @pytest.mark.asyncio
    async def test_check_final_approval_permissions_none_case_owner_id(self, mock_admin_user):
        """Test handling when case_owner_id is None."""
        # Execute - ADMIN should still be authorized
        await check_final_approval_permissions(mock_admin_user, None)

    @pytest.mark.asyncio
    async def test_check_final_approval_permissions_empty_case_owner_id(self, mock_admin_user):
        """Test handling when case_owner_id is empty string."""
        # Execute - ADMIN should still be authorized
        await check_final_approval_permissions(mock_admin_user, "")

    # ============================================================================
    # Integration-Style Tests
    # ============================================================================

    @pytest.mark.asyncio
    @patch("app.services.firestore_service.FirestoreService")
    async def test_authorization_flow_comprehensive(self, mock_firestore_service_class, caplog):
        """Test comprehensive authorization flow with various user types."""
        # Setup mock Firestore service
        mock_service = Mock()
        mock_service.get_document = AsyncMock(return_value={
            "finalApproverRoleName": "FINAL_APPROVER"
        })
        mock_firestore_service_class.return_value = mock_service

        case_owner_id = "case-owner-123"

        # Test 1: ADMIN should always be authorized
        admin_user = {"uid": "admin", "email": "admin@test.com", "systemRole": "ADMIN"}
        await check_final_approval_permissions(admin_user, case_owner_id)

        # Test 2: Case owner should be authorized for their own case
        owner_user = {"uid": case_owner_id, "email": "owner@test.com", "systemRole": "USER"}
        await check_final_approval_permissions(owner_user, case_owner_id)

        # Test 3: FINAL_APPROVER should be authorized
        approver_user = {"uid": "approver", "email": "approver@test.com", "systemRole": "FINAL_APPROVER"}
        await check_final_approval_permissions(approver_user, case_owner_id)

        # Test 4: Regular user should be denied
        regular_user = {"uid": "regular", "email": "regular@test.com", "systemRole": "USER"}
        with pytest.raises(HTTPException) as exc_info:
            await check_final_approval_permissions(regular_user, case_owner_id)
        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN 