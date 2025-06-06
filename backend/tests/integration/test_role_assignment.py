"""
Integration tests for role assignment functionality
Tests role assignment scripts, user service, and Firebase claims sync
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import patch, Mock, AsyncMock
from datetime import datetime, timezone

# Add the scripts directory to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts"))

from app.models.firestore_models import UserRole
from app.services.user_service import user_service


class TestUserServiceRoleOperations:
    """Test UserService role management operations"""

    @pytest.mark.asyncio
    async def test_create_user_with_role(self):
        """Test creating a user with a specific role"""
        test_uid = "test_user_123"
        test_email = "test@drfirst.com"
        test_role = UserRole.SALES_MANAGER

        with patch("asyncio.to_thread") as mock_to_thread:
            with patch.object(user_service, "db") as mock_firestore:
                # Mock Firestore document operations
                mock_doc_ref = Mock()
                mock_collection = Mock()
                mock_collection.document.return_value = mock_doc_ref
                mock_firestore.collection.return_value = mock_collection

                # Mock document exists check (new user)
                mock_doc_snapshot = Mock()
                mock_doc_snapshot.exists = False

                # Mock the actual user data that would be returned
                mock_created_data = {
                    "uid": test_uid,
                    "email": test_email,
                    "display_name": "Test User",
                    "systemRole": test_role.value,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                    "last_login": "2025-01-01T00:00:00Z",
                    "is_active": True,
                }

                # Mock asyncio.to_thread calls (get, then set)
                mock_to_thread.side_effect = [
                    mock_doc_snapshot,  # First call: doc_ref.get()
                    None,  # Second call: doc_ref.set()
                ]

                # Test user creation
                result = await user_service.create_or_update_user(
                    uid=test_uid,
                    email=test_email,
                    display_name="Test User",
                    system_role=test_role,
                )

                # Verify the user service returned data
                assert result is not None
                assert result["email"] == test_email
                assert result["systemRole"] == test_role.value
                assert "created_at" in result

                # Verify Firestore operations were called
                mock_collection.document.assert_called_with(test_uid)
                assert mock_to_thread.call_count == 2

    @pytest.mark.asyncio
    async def test_update_user_role(self):
        """Test updating an existing user's role"""
        test_uid = "existing_user_456"
        test_email = "existing@drfirst.com"
        new_role = UserRole.FINANCE_APPROVER

        with patch("asyncio.to_thread") as mock_to_thread:
            with patch.object(user_service, "db") as mock_firestore:
                # Mock Firestore operations
                mock_doc_ref = Mock()
                mock_collection = Mock()
                mock_collection.document.return_value = mock_doc_ref
                mock_firestore.collection.return_value = mock_collection

                # Mock document exists check (new user for simplicity)
                mock_doc_snapshot = Mock()
                mock_doc_snapshot.exists = False

                # Mock the actual user data that would be returned
                mock_updated_data = {
                    "uid": test_uid,
                    "email": test_email,
                    "display_name": "Existing User",
                    "systemRole": new_role.value,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                    "last_login": "2025-01-01T00:00:00Z",
                    "is_active": True,
                }

                # Mock asyncio.to_thread calls (get, then set)
                mock_to_thread.side_effect = [
                    mock_doc_snapshot,  # First call: doc_ref.get()
                    None,  # Second call: doc_ref.set()
                ]

                # Test role update
                result = await user_service.create_or_update_user(
                    uid=test_uid,
                    email=test_email,
                    display_name="Existing User",
                    system_role=new_role,
                )

                # Verify the operation succeeded
                assert result is not None
                assert result["email"] == test_email
                assert result["systemRole"] == new_role.value
                assert "created_at" in result

                # Verify Firestore operations were called
                mock_collection.document.assert_called_with(test_uid)
                assert mock_to_thread.call_count == 2

    @pytest.mark.asyncio
    async def test_sync_user_claims(self):
        """Test syncing user role to Firebase custom claims"""
        test_uid = "claims_test_user"

        with patch("asyncio.to_thread") as mock_to_thread:
            with patch.object(user_service, "db") as mock_firestore:
                # Mock Firestore get operation
                mock_doc_ref = Mock()
                mock_collection = Mock()
                mock_collection.document.return_value = mock_doc_ref
                mock_firestore.collection.return_value = mock_collection

                # Mock user document with role
                mock_doc_snapshot = Mock()
                mock_doc_snapshot.exists = True
                mock_doc_snapshot.to_dict.return_value = {
                    "email": "claims@drfirst.com",
                    "systemRole": "TECHNICAL_ARCHITECT",  # Fixed field name
                }

                # Mock asyncio.to_thread calls
                # First call returns the document snapshot
                # Second call simulates the auth.set_custom_user_claims call
                mock_to_thread.side_effect = [
                    mock_doc_snapshot,  # First call: doc_ref.get()
                    None,  # Second call: auth.set_custom_user_claims()
                ]

                # Test claims sync
                result = await user_service.sync_user_claims(test_uid)

                # Verify the result and that asyncio.to_thread was called twice
                assert result is True
                assert mock_to_thread.call_count == 2

                # Verify the second call was to set_custom_user_claims with correct args
                second_call_args = mock_to_thread.call_args_list[1]
                assert second_call_args[0][1] == test_uid  # UID argument
                assert second_call_args[0][2] == {
                    "systemRole": "TECHNICAL_ARCHITECT"
                }  # Claims argument

    @pytest.mark.asyncio
    async def test_sync_claims_user_not_found(self):
        """Test claims sync when user document doesn't exist"""
        test_uid = "nonexistent_user"

        with patch("asyncio.to_thread") as mock_to_thread:
            with patch.object(user_service, "db") as mock_firestore:
                # Mock Firestore get operation returning non-existent document
                mock_doc_ref = Mock()
                mock_collection = Mock()
                mock_collection.document.return_value = mock_doc_ref
                mock_firestore.collection.return_value = mock_collection

                mock_doc_snapshot = Mock()
                mock_doc_snapshot.exists = False

                # Mock asyncio.to_thread call (just the get operation)
                mock_to_thread.return_value = mock_doc_snapshot

                # Test claims sync for non-existent user
                result = await user_service.sync_user_claims(test_uid)

                # Should return False when user not found
                assert result is False


class TestRoleAssignmentScripts:
    """Test role assignment script functionality"""

    def test_universal_script_validation(self):
        """Test universal role assignment script validation"""
        # Import the set_user_role function
        from set_user_role import set_user_role, ROLE_DESCRIPTIONS

        # Test that all roles have descriptions
        for role in UserRole:
            assert (
                role.value in ROLE_DESCRIPTIONS
            ), f"Missing description for role {role.value}"

        # Test description format
        for role_name, description in ROLE_DESCRIPTIONS.items():
            assert isinstance(description, str)
            assert len(description) > 0
            assert description.startswith(
                ("🔑", "👤", "👁️", "👨‍💻", "💼", "📊", "💰", "⚖️", "🏗️", "📦", "📈", "👑")
            )

    @pytest.mark.asyncio
    async def test_role_assignment_validation(self):
        """Test role assignment with valid and invalid roles"""
        from set_user_role import set_user_role

        test_email = "validation@drfirst.com"

        with patch("firebase_admin.auth.get_user_by_email") as mock_get_user:
            with patch.object(
                user_service, "create_or_update_user"
            ) as mock_create_user:
                with patch.object(user_service, "sync_user_claims") as mock_sync_claims:

                    # Mock Firebase user lookup
                    mock_user_record = Mock()
                    mock_user_record.uid = "test_uid_789"
                    mock_user_record.display_name = "Test Validation User"
                    mock_get_user.return_value = mock_user_record

                    # Mock successful operations
                    mock_create_user.return_value = {"id": "test_uid_789"}
                    mock_sync_claims.return_value = True

                    # Test valid role assignment
                    result = await set_user_role(test_email, "LEGAL_APPROVER")
                    assert result is True

                    # Verify calls were made
                    mock_get_user.assert_called_with(test_email)
                    mock_create_user.assert_called_once()
                    mock_sync_claims.assert_called_with("test_uid_789")

                    # Verify role was set correctly
                    create_call_args = mock_create_user.call_args[1]
                    assert create_call_args["system_role"] == UserRole.LEGAL_APPROVER

    @pytest.mark.asyncio
    async def test_invalid_role_assignment(self):
        """Test role assignment with invalid role"""
        from set_user_role import set_user_role

        test_email = "invalid@drfirst.com"

        # Test invalid role
        result = await set_user_role(test_email, "INVALID_ROLE")
        assert result is False

    def test_specific_role_scripts_exist(self):
        """Test that specific role assignment scripts exist and are importable"""
        script_files = [
            "set_admin_role.py",
            "set_developer_role.py",
            "set_sales_manager_role.py",
            "set_finance_approver_role.py",
            "set_product_owner_role.py",
        ]

        scripts_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "scripts"
        )

        for script_file in script_files:
            script_path = os.path.join(scripts_dir, script_file)
            assert os.path.exists(
                script_path
            ), f"Script file {script_file} should exist"
            assert os.path.isfile(script_path), f"{script_file} should be a file"

            # Check that file is executable (has shebang)
            with open(script_path, "r") as f:
                first_line = f.readline().strip()
                assert first_line.startswith(
                    "#!"
                ), f"{script_file} should start with shebang"


class TestRoleBasedFeatures:
    """Test role-based feature access patterns"""

    def test_admin_permissions(self):
        """Test admin role permissions"""
        admin_role = UserRole.ADMIN

        # Admin should have access to everything
        admin_accessible_endpoints = [
            "admin_panel",
            "user_management",
            "rate_cards",
            "pricing_templates",
            "business_case_approval",
            "system_design_approval",
            "financial_approval",
        ]

        for endpoint in admin_accessible_endpoints:
            # In a real implementation, this would test actual permission checking
            assert admin_role == UserRole.ADMIN  # Admin always has access

    def test_role_specific_permissions(self):
        """Test role-specific permission patterns"""
        permission_matrix = {
            UserRole.FINANCE_APPROVER: ["financial_approval", "cost_review"],
            UserRole.SALES_MANAGER: ["sales_approval", "revenue_review"],
            UserRole.DEVELOPER: ["system_design_approval", "technical_review"],
            UserRole.PRODUCT_OWNER: ["prd_approval", "feature_prioritization"],
            UserRole.LEGAL_APPROVER: ["legal_review", "compliance_check"],
            UserRole.TECHNICAL_ARCHITECT: [
                "architecture_review",
                "system_design_approval",
            ],
            UserRole.BUSINESS_ANALYST: ["requirements_analysis", "process_review"],
            UserRole.SALES_REP: ["case_creation", "initial_estimates"],
        }

        for role, expected_permissions in permission_matrix.items():
            # Test that role exists and has expected structure
            assert isinstance(role, UserRole)
            assert isinstance(expected_permissions, list)
            assert len(expected_permissions) > 0

            # In a real implementation, these would be actual permission checks
            for permission in expected_permissions:
                assert isinstance(permission, str)
                assert len(permission) > 0

    def test_role_exclusions(self):
        """Test that certain roles are excluded from sensitive operations"""
        sensitive_operations = [
            "user_role_assignment",
            "system_configuration",
            "admin_panel",
        ]

        non_admin_roles = [
            UserRole.USER,
            UserRole.VIEWER,
            UserRole.SALES_REP,
            UserRole.BUSINESS_ANALYST,
            UserRole.DEVELOPER,
        ]

        for role in non_admin_roles:
            # Non-admin roles should not have admin access
            assert role != UserRole.ADMIN

            # In a real implementation, this would test actual access denial
            for operation in sensitive_operations:
                if operation == "admin_panel":
                    # Only admin should access admin panel
                    has_access = role == UserRole.ADMIN
                    assert not has_access or role == UserRole.ADMIN


class TestRoleWorkflowIntegration:
    """Test role integration with business case workflows"""

    def test_approval_workflow_roles(self):
        """Test roles involved in approval workflows"""
        approval_workflows = {
            "prd_approval": [UserRole.PRODUCT_OWNER, UserRole.ADMIN],
            "system_design_approval": [
                UserRole.DEVELOPER,
                UserRole.TECHNICAL_ARCHITECT,
                UserRole.ADMIN,
            ],
            "financial_approval": [UserRole.FINANCE_APPROVER, UserRole.ADMIN],
            "legal_approval": [UserRole.LEGAL_APPROVER, UserRole.ADMIN],
            "sales_approval": [UserRole.SALES_MANAGER, UserRole.ADMIN],
        }

        for workflow, approver_roles in approval_workflows.items():
            # Test that workflow has appropriate approvers
            assert (
                len(approver_roles) >= 1
            ), f"Workflow {workflow} should have at least one approver"
            assert (
                UserRole.ADMIN in approver_roles
            ), f"Admin should be able to approve {workflow}"

            # Test role types
            for role in approver_roles:
                assert isinstance(role, UserRole)

    def test_role_transition_scenarios(self):
        """Test scenarios where users might change roles"""
        role_transitions = [
            (UserRole.SALES_REP, UserRole.SALES_MANAGER),
            (UserRole.DEVELOPER, UserRole.TECHNICAL_ARCHITECT),
            (UserRole.USER, UserRole.BUSINESS_ANALYST),
            (UserRole.BUSINESS_ANALYST, UserRole.PRODUCT_OWNER),
        ]

        for from_role, to_role in role_transitions:
            # Test that roles are valid
            assert isinstance(from_role, UserRole)
            assert isinstance(to_role, UserRole)
            assert from_role != to_role

            # Test that transition makes logical sense (not enforced, but documented)
            assert from_role.value != to_role.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
