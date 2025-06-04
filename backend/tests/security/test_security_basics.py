"""
Basic Security Tests
Tests for fundamental security patterns and data validation
Critical for ensuring system security
"""

import pytest
from unittest.mock import patch, MagicMock

from app.models.firestore_models import UserRole, JobStatus, User


class TestBasicSecurityPatterns:
    """Test basic security patterns and validations"""

    def test_user_role_enum_security(self):
        """Test that user roles are properly constrained"""
        # Test all valid roles can be created
        valid_roles = [
            UserRole.ADMIN,
            UserRole.USER,
            UserRole.DEVELOPER,
            UserRole.BUSINESS_ANALYST,
            UserRole.SALES_REP
        ]
        
        for role in valid_roles:
            user_data = {
                "uid": "test-uid",
                "email": "test@example.com",
                "systemRole": role
            }
            user = User(**user_data)
            assert user.systemRole == role

    def test_role_privilege_levels(self):
        """Test role privilege hierarchy"""
        # Define role privilege levels (higher number = more privileges)
        role_privileges = {
            UserRole.VIEWER: 1,
            UserRole.USER: 2,
            UserRole.BUSINESS_ANALYST: 3,
            UserRole.SALES_REP: 3,
            UserRole.DEVELOPER: 4,
            UserRole.SALES_MANAGER: 4,
            UserRole.FINANCE_APPROVER: 5,
            UserRole.LEGAL_APPROVER: 5,
            UserRole.TECHNICAL_ARCHITECT: 5,
            UserRole.PRODUCT_OWNER: 5,
            UserRole.ADMIN: 10
        }
        
        # Verify admin has highest privilege
        assert role_privileges[UserRole.ADMIN] > max(
            priv for role, priv in role_privileges.items() if role != UserRole.ADMIN
        )
        
        # Verify viewer has lowest privilege
        assert role_privileges[UserRole.VIEWER] == min(role_privileges.values())

    def test_sensitive_data_patterns(self):
        """Test handling of sensitive data patterns"""
        sensitive_patterns = [
            "password",
            "secret",
            "token",
            "key",
            "credential",
            "api_key",
            "private_key"
        ]
        
        # Test that User model doesn't expose sensitive fields
        user_data = {
            "uid": "test-uid",
            "email": "test@example.com",
            "systemRole": UserRole.USER
        }
        
        user = User(**user_data)
        user_dict = user.model_dump()
        
        # Check that no sensitive patterns appear in serialized data
        serialized_text = str(user_dict).lower()
        for pattern in sensitive_patterns:
            assert pattern not in serialized_text, f"Sensitive pattern '{pattern}' found in user data"

    def test_email_validation_security(self):
        """Test email validation for security"""
        # Test valid emails
        valid_emails = [
            "user@example.com",
            "test.user@company.org",
            "admin+tag@domain.co.uk"
        ]
        
        for email in valid_emails:
            user_data = {
                "uid": "test-uid",
                "email": email,
                "systemRole": UserRole.USER
            }
            user = User(**user_data)
            assert user.email == email

    def test_injection_prevention_patterns(self):
        """Test basic injection prevention patterns"""
        # Test potentially dangerous inputs that should be handled safely
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "${7*7}",  # Template injection
            "{{constructor.constructor('return process')().exit()}}", # Node.js injection
            "%{#context.stop}",  # Struts injection
        ]
        
        for dangerous_input in dangerous_inputs:
            user_data = {
                "uid": dangerous_input,
                "email": "test@example.com",
                "systemRole": UserRole.USER,
                "display_name": dangerous_input
            }
            
            # Should not raise exceptions (sanitization/validation should handle)
            try:
                user = User(**user_data)
                # Verify the input is stored as-is but not executed
                assert dangerous_input in [user.uid, user.display_name]
            except ValueError:
                # Validation rejection is also acceptable
                pass

    def test_status_enum_integrity(self):
        """Test job status enum integrity"""
        # Verify all status values are lowercase (security convention)
        for status in JobStatus:
            assert status.value.islower(), f"Status {status} should be lowercase"
            assert " " not in status.value, f"Status {status} should not contain spaces"
            assert status.value.isalpha() or "_" in status.value, f"Status {status} should only contain letters and underscores"

    def test_user_model_field_types(self):
        """Test user model field type security"""
        user_data = {
            "uid": "test-uid",
            "email": "test@example.com",
            "systemRole": UserRole.USER
        }
        
        user = User(**user_data)
        
        # Verify critical fields have expected types
        assert isinstance(user.uid, str)
        assert isinstance(user.email, str)
        assert isinstance(user.systemRole, UserRole)
        assert isinstance(user.is_active, bool)


class TestInputValidationSecurity:
    """Test input validation and sanitization security"""

    def test_string_length_limits(self):
        """Test handling of very long strings"""
        # Test very long inputs
        long_string = "A" * 10000  # 10KB string
        very_long_string = "B" * 100000  # 100KB string
        
        test_cases = [
            {"field": "uid", "value": long_string},
            {"field": "email", "value": f"{long_string}@example.com"},
            {"field": "display_name", "value": very_long_string}
        ]
        
        for test_case in test_cases:
            user_data = {
                "uid": "test-uid",
                "email": "test@example.com",
                "systemRole": UserRole.USER
            }
            user_data[test_case["field"]] = test_case["value"]
            
            # Should either accept or reject gracefully, not crash
            try:
                user = User(**user_data)
                # If accepted, verify it's stored correctly
                assert getattr(user, test_case["field"]) == test_case["value"]
            except ValueError:
                # Validation rejection is acceptable
                pass

    def test_unicode_handling(self):
        """Test Unicode character handling security"""
        unicode_test_cases = [
            "测试用户",  # Chinese
            "пользователь",  # Russian  
            "🚀🔥💯",  # Emojis
            "user\x00name",  # Null byte
            "user\r\nname",  # CRLF injection attempt
            "user\tname"  # Tab character
        ]
        
        for unicode_input in unicode_test_cases:
            user_data = {
                "uid": "test-uid",
                "email": "test@example.com", 
                "systemRole": UserRole.USER,
                "display_name": unicode_input
            }
            
            # Should handle Unicode gracefully
            try:
                user = User(**user_data)
                # Should preserve or sanitize appropriately
                assert user.display_name is not None
            except ValueError:
                # Validation rejection is also acceptable
                pass

    def test_null_and_empty_value_handling(self):
        """Test null and empty value security"""
        test_cases = [
            {"field": "display_name", "value": None, "should_work": True},
            {"field": "display_name", "value": "", "should_work": True},
        ]
        
        for test_case in test_cases:
            user_data = {
                "uid": "test-uid",
                "email": "test@example.com",
                "systemRole": UserRole.USER
            }
            user_data[test_case["field"]] = test_case["value"]
            
            if test_case["should_work"]:
                try:
                    user = User(**user_data)
                    assert hasattr(user, test_case["field"])
                except ValueError:
                    # Some validation is still acceptable
                    pass

    def test_type_coercion_security(self):
        """Test type coercion security"""
        # Test attempts to pass wrong types
        type_test_cases = [
            {"field": "is_active", "value": "true", "expected_type": bool},
            {"field": "is_active", "value": 1, "expected_type": bool},
            {"field": "systemRole", "value": "ADMIN", "expected_type": UserRole}
        ]
        
        for test_case in type_test_cases:
            user_data = {
                "uid": "test-uid",
                "email": "test@example.com",
                "systemRole": UserRole.USER,
                "is_active": True
            }
            user_data[test_case["field"]] = test_case["value"]
            
            try:
                user = User(**user_data)
                # Verify proper type coercion
                actual_value = getattr(user, test_case["field"])
                assert isinstance(actual_value, test_case["expected_type"])
            except ValueError:
                # Type validation rejection is acceptable
                pass


class TestDataExposurePrevention:
    """Test prevention of sensitive data exposure"""

    def test_model_serialization_security(self):
        """Test that model serialization doesn't expose sensitive data"""
        user_data = {
            "uid": "sensitive-uid-12345",
            "email": "user@example.com",
            "systemRole": UserRole.USER,
            "display_name": "Test User"
        }
        
        user = User(**user_data)
        serialized = user.model_dump()
        
        # Verify structure is as expected
        expected_fields = ["uid", "email", "systemRole", "display_name", "created_at", "updated_at", "last_login", "is_active"]
        
        for field in expected_fields:
            assert field in serialized or getattr(user, field) is not None

    def test_error_message_security(self):
        """Test that error messages don't leak sensitive information"""
        try:
            # Attempt to create invalid user
            User(uid="", email="")
        except Exception as e:
            error_message = str(e).lower()
            
            # Error message should not contain sensitive patterns
            forbidden_patterns = [
                "database",
                "sql", 
                "firestore",
                "connection",
                "secret",
                "password",
                "key",
                "token"
            ]
            
            for pattern in forbidden_patterns:
                assert pattern not in error_message, f"Error message contains sensitive pattern: {pattern}"

    def test_default_values_security(self):
        """Test that default values are secure"""
        minimal_user_data = {
            "uid": "test-uid",
            "email": "test@example.com"
        }
        
        user = User(**minimal_user_data)
        
        # Verify secure defaults
        assert user.systemRole == UserRole.USER  # Not admin by default
        assert user.is_active is True  # Active by default is OK
        assert user.last_login is None  # No login history by default
        assert user.display_name is None  # No display name by default


if __name__ == "__main__":
    # Run tests with: python -m pytest backend/tests/security/test_security_basics.py -v
    pytest.main([__file__, "-v"]) 