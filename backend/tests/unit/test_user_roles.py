"""
Unit tests for user role system
Tests UserRole enum, role validation, and role-based functionality
"""

import pytest
from app.models.firestore_models import UserRole


class TestUserRoleEnum:
    """Test UserRole enum functionality"""

    def test_all_roles_exist(self):
        """Test that all expected roles are defined"""
        expected_roles = {
            "ADMIN",
            "USER",
            "VIEWER",
            "DEVELOPER",
            "SALES_REP",
            "SALES_MANAGER",
            "FINANCE_APPROVER",
            "LEGAL_APPROVER",
            "TECHNICAL_ARCHITECT",
            "PRODUCT_OWNER",
            "BUSINESS_ANALYST",
        }

        actual_roles = {role.value for role in UserRole}
        assert (
            actual_roles == expected_roles
        ), f"Missing or extra roles. Expected: {expected_roles}, Got: {actual_roles}"

    def test_role_count(self):
        """Test that we have the expected number of roles"""
        assert len(UserRole) == 11, f"Expected 11 roles, got {len(UserRole)}"

    def test_role_string_values(self):
        """Test that each role has the correct string value"""
        role_mapping = {
            UserRole.ADMIN: "ADMIN",
            UserRole.USER: "USER",
            UserRole.VIEWER: "VIEWER",
            UserRole.DEVELOPER: "DEVELOPER",
            UserRole.SALES_REP: "SALES_REP",
            UserRole.SALES_MANAGER: "SALES_MANAGER",
            UserRole.FINANCE_APPROVER: "FINANCE_APPROVER",
            UserRole.LEGAL_APPROVER: "LEGAL_APPROVER",
            UserRole.TECHNICAL_ARCHITECT: "TECHNICAL_ARCHITECT",
            UserRole.PRODUCT_OWNER: "PRODUCT_OWNER",
            UserRole.BUSINESS_ANALYST: "BUSINESS_ANALYST",
        }

        for role_enum, expected_string in role_mapping.items():
            assert role_enum.value == expected_string

    def test_role_creation_from_string(self):
        """Test creating UserRole from string values"""
        valid_strings = [
            "ADMIN",
            "USER",
            "VIEWER",
            "DEVELOPER",
            "SALES_REP",
            "SALES_MANAGER",
            "FINANCE_APPROVER",
            "LEGAL_APPROVER",
            "TECHNICAL_ARCHITECT",
            "PRODUCT_OWNER",
            "BUSINESS_ANALYST",
        ]

        for role_string in valid_strings:
            role = UserRole(role_string)
            assert role.value == role_string

    def test_invalid_role_creation(self):
        """Test that invalid role strings raise ValueError"""
        invalid_strings = ["INVALID_ROLE", "admin", "USER_ADMIN", "", None]  # lowercase

        for invalid_string in invalid_strings:
            with pytest.raises(ValueError):
                UserRole(invalid_string)

    def test_role_equality(self):
        """Test role equality comparisons"""
        admin1 = UserRole.ADMIN
        admin2 = UserRole("ADMIN")
        user_role = UserRole.USER

        assert admin1 == admin2
        assert admin1 != user_role
        assert admin1 == "ADMIN"
        assert admin1 != "USER"


class TestRolePermissions:
    """Test role-based permission logic"""

    def test_admin_identification(self):
        """Test identifying admin users"""
        admin_role = UserRole.ADMIN
        other_roles = [UserRole.USER, UserRole.DEVELOPER, UserRole.SALES_MANAGER]

        # Admin should be identified correctly
        assert admin_role == UserRole.ADMIN
        assert admin_role.value == "ADMIN"

        # Other roles should not be admin
        for role in other_roles:
            assert role != UserRole.ADMIN
            assert role.value != "ADMIN"

    def test_role_categorization(self):
        """Test logical grouping of roles"""
        # Administrative roles
        admin_roles = {UserRole.ADMIN}

        # Technical roles
        technical_roles = {UserRole.DEVELOPER, UserRole.TECHNICAL_ARCHITECT}

        # Business roles
        business_roles = {UserRole.PRODUCT_OWNER, UserRole.BUSINESS_ANALYST}

        # Sales roles
        sales_roles = {UserRole.SALES_REP, UserRole.SALES_MANAGER}

        # Approval roles
        approval_roles = {
            UserRole.FINANCE_APPROVER,
            UserRole.LEGAL_APPROVER,
            UserRole.ADMIN,  # Admin can approve everything
        }

        # Basic user roles
        basic_roles = {UserRole.USER, UserRole.VIEWER}

        # Test that roles are in expected categories
        assert UserRole.ADMIN in admin_roles
        assert UserRole.DEVELOPER in technical_roles
        assert UserRole.SALES_MANAGER in sales_roles
        assert UserRole.FINANCE_APPROVER in approval_roles
        assert UserRole.USER in basic_roles

    def test_role_hierarchy_concepts(self):
        """Test concepts that could be used for role hierarchy"""
        # This tests the logical foundation for future role hierarchy

        # Define privilege levels (higher number = more privileges)
        privilege_levels = {
            UserRole.VIEWER: 1,
            UserRole.USER: 2,
            UserRole.BUSINESS_ANALYST: 3,
            UserRole.SALES_REP: 3,
            UserRole.DEVELOPER: 4,
            UserRole.PRODUCT_OWNER: 4,
            UserRole.SALES_MANAGER: 5,
            UserRole.FINANCE_APPROVER: 5,
            UserRole.LEGAL_APPROVER: 5,
            UserRole.TECHNICAL_ARCHITECT: 6,
            UserRole.ADMIN: 10,
        }

        # Test that admin has highest privilege
        admin_level = privilege_levels[UserRole.ADMIN]
        for role, level in privilege_levels.items():
            if role != UserRole.ADMIN:
                assert (
                    admin_level > level
                ), f"Admin should have higher privilege than {role}"

        # Test that approvers have appropriate levels
        approver_roles = [UserRole.FINANCE_APPROVER, UserRole.LEGAL_APPROVER]
        for approver in approver_roles:
            assert (
                privilege_levels[approver] >= 5
            ), f"{approver} should have high privilege level"

        # Test that viewer has lowest level
        viewer_level = privilege_levels[UserRole.VIEWER]
        for role, level in privilege_levels.items():
            if role != UserRole.VIEWER:
                assert (
                    viewer_level <= level
                ), f"Viewer should have lowest or equal privilege to {role}"


class TestRoleValidation:
    """Test role validation functions"""

    def test_valid_role_validation(self):
        """Test validation of valid roles"""
        valid_role_strings = [
            "ADMIN",
            "USER",
            "VIEWER",
            "DEVELOPER",
            "SALES_REP",
            "SALES_MANAGER",
            "FINANCE_APPROVER",
            "LEGAL_APPROVER",
            "TECHNICAL_ARCHITECT",
            "PRODUCT_OWNER",
            "BUSINESS_ANALYST",
        ]

        for role_string in valid_role_strings:
            # Should not raise exception
            role = UserRole(role_string)
            assert isinstance(role, UserRole)
            assert role.value == role_string

    def test_role_case_sensitivity(self):
        """Test that roles are case sensitive"""
        # Valid uppercase
        admin_role = UserRole("ADMIN")
        assert admin_role == UserRole.ADMIN

        # Invalid lowercase should raise ValueError
        with pytest.raises(ValueError):
            UserRole("admin")

        with pytest.raises(ValueError):
            UserRole("User")

        with pytest.raises(ValueError):
            UserRole("sales_manager")  # should be SALES_MANAGER

    def test_role_in_checks(self):
        """Test using roles in membership checks"""
        admin_and_manager_roles = [UserRole.ADMIN, UserRole.SALES_MANAGER]

        assert UserRole.ADMIN in admin_and_manager_roles
        assert UserRole.SALES_MANAGER in admin_and_manager_roles
        assert UserRole.USER not in admin_and_manager_roles

        # Test with string values
        role_strings = ["ADMIN", "SALES_MANAGER"]
        assert UserRole.ADMIN.value in role_strings
        assert UserRole.SALES_MANAGER.value in role_strings
        assert UserRole.USER.value not in role_strings


class TestRoleCompatibility:
    """Test role compatibility with existing systems"""

    def test_role_serialization(self):
        """Test that roles can be serialized to strings"""
        for role in UserRole:
            # Should be able to convert to string
            role_string = role.value
            assert isinstance(role_string, str)
            assert len(role_string) > 0

            # Should be able to recreate from string
            recreated_role = UserRole(role_string)
            assert recreated_role == role

    def test_role_json_compatibility(self):
        """Test that roles work with JSON serialization patterns"""
        import json

        # Test serializing role values
        role_data = {
            "user_id": "test_user",
            "system_role": UserRole.SALES_MANAGER.value,
            "assigned_at": "2025-01-01T00:00:00Z",
        }

        # Should serialize to JSON
        json_string = json.dumps(role_data)
        assert "SALES_MANAGER" in json_string

        # Should deserialize from JSON
        parsed_data = json.loads(json_string)
        assert parsed_data["system_role"] == "SALES_MANAGER"

        # Should be able to recreate role
        role = UserRole(parsed_data["system_role"])
        assert role == UserRole.SALES_MANAGER

    def test_role_firestore_compatibility(self):
        """Test patterns used with Firestore documents"""
        # Test creating user document with role
        user_doc = {
            "email": "test@drfirst.com",
            "system_role": UserRole.FINANCE_APPROVER.value,
            "created_at": "2025-01-01T00:00:00Z",
        }

        # Test that role can be extracted and validated
        role_string = user_doc["system_role"]
        role = UserRole(role_string)
        assert role == UserRole.FINANCE_APPROVER

        # Test role updates
        user_doc["system_role"] = UserRole.SALES_MANAGER.value
        updated_role = UserRole(user_doc["system_role"])
        assert updated_role == UserRole.SALES_MANAGER


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
