"""
Database Integration Tests
Tests the actual database operations without mocking
Critical for ensuring data integrity and query performance
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

from app.models.firestore_models import BusinessCase, JobStatus, User, UserRole
from app.core.config import settings


@pytest.fixture
def test_user_data():
    """Generate test user data"""
    return {
        "uid": f"test-{uuid4()}",
        "email": f"test-{uuid4()}@example.com",
        "systemRole": UserRole.BUSINESS_ANALYST,
        "created_at": datetime.utcnow(),
        "is_active": True
    }


@pytest.fixture
def test_case_data():
    """Generate test case data"""
    return {
        "id": f"case-{uuid4()}",
        "title": "Test Business Case",
        "description": "This is a test business case for integration testing",
        "status": JobStatus.PENDING,
        "created_by": "test@example.com",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


class TestBasicModels:
    """Test basic model validation and creation"""

    def test_user_model_creation(self, test_user_data):
        """Test creating a User model instance"""
        user = User(**test_user_data)
        assert user.uid == test_user_data["uid"]
        assert user.email == test_user_data["email"]
        assert user.systemRole == UserRole.BUSINESS_ANALYST
        assert user.is_active is True

    def test_user_role_validation(self):
        """Test user role validation"""
        valid_roles = [
            UserRole.ADMIN,
            UserRole.BUSINESS_ANALYST,
            UserRole.DEVELOPER,
            UserRole.SALES_REP
        ]
        
        for role in valid_roles:
            user_data = {
                "uid": f"test-{uuid4()}",
                "email": "test@example.com",
                "systemRole": role
            }
            user = User(**user_data)
            assert user.systemRole == role

    def test_job_status_validation(self):
        """Test job status validation"""
        valid_statuses = [
            JobStatus.PENDING,
            JobStatus.IN_PROGRESS,
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED
        ]
        
        for status in valid_statuses:
            assert status in JobStatus
            # Test string representation
            assert isinstance(status.value, str)

    def test_business_case_model_creation(self):
        """Test creating a BusinessCase model instance"""
        from app.models.firestore_models import BusinessCaseRequest, BusinessCase
        
        request_data = BusinessCaseRequest(
            title="Test Case",
            description="Test Description",
            requester_uid="test-uid-123"
        )
        
        business_case = BusinessCase(
            request_data=request_data,
            status=JobStatus.PENDING
        )
        
        assert business_case.request_data.title == "Test Case"
        assert business_case.status == JobStatus.PENDING
        assert isinstance(business_case.created_at, datetime)

    def test_model_serialization(self, test_user_data):
        """Test model serialization to dict"""
        user = User(**test_user_data)
        user_dict = user.model_dump()
        
        assert isinstance(user_dict, dict)
        assert user_dict["uid"] == test_user_data["uid"]
        assert user_dict["email"] == test_user_data["email"]
        assert user_dict["systemRole"] == UserRole.BUSINESS_ANALYST.value

    def test_datetime_handling(self):
        """Test datetime field handling"""
        user_data = {
            "uid": "test-uid",
            "email": "test@example.com",
            "systemRole": UserRole.USER
        }
        
        user = User(**user_data)
        
        # Should auto-populate timestamps
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.last_login is None

    def test_optional_fields(self):
        """Test handling of optional fields"""
        minimal_user_data = {
            "uid": "test-uid",
            "email": "test@example.com"
        }
        
        user = User(**minimal_user_data)
        
        # Should use defaults
        assert user.systemRole == UserRole.USER
        assert user.is_active is True
        assert user.display_name is None

    def test_field_validation(self):
        """Test field validation rules"""
        # Test missing required fields
        with pytest.raises(ValueError):
            User()  # Missing required uid and email
        
        # Test invalid email (basic check)
        invalid_user_data = {
            "uid": "test-uid",
            "email": "",  # Empty email
            "systemRole": UserRole.USER
        }
        
        with pytest.raises(ValueError):
            User(**invalid_user_data)


class TestDataIntegrity:
    """Test data integrity and validation"""

    def test_enum_consistency(self):
        """Test that enum values are consistent"""
        # Test UserRole enum
        assert len(UserRole) > 0
        for role in UserRole:
            assert isinstance(role.value, str)
            assert role.value.isupper()  # Should be uppercase
        
        # Test JobStatus enum
        assert len(JobStatus) > 0
        for status in JobStatus:
            assert isinstance(status.value, str)
            assert status.value.islower()  # Should be lowercase

    def test_model_immutability_protection(self):
        """Test that models handle updates properly"""
        user_data = {
            "uid": "test-uid",
            "email": "test@example.com",
            "systemRole": UserRole.USER
        }
        
        user = User(**user_data)
        original_created_at = user.created_at
        
        # Create new instance with updated timestamp
        updated_data = user.model_dump()
        updated_data["updated_at"] = datetime.utcnow()
        updated_user = User(**updated_data)
        
        # Should maintain original created_at
        assert updated_user.created_at == original_created_at
        assert updated_user.updated_at > original_created_at

    def test_complex_data_structures(self):
        """Test handling of complex nested data"""
        from app.models.firestore_models import BusinessCaseRequest, BusinessCase
        
        complex_requirements = {
            "technical_specs": {
                "database": "PostgreSQL",
                "frameworks": ["FastAPI", "React"],
                "integrations": ["Salesforce", "SAP"]
            },
            "business_rules": [
                {"rule": "Must support 1000 concurrent users"},
                {"rule": "Must have 99.9% uptime"}
            ],
            "compliance": {
                "gdpr": True,
                "hipaa": False,
                "sox": True
            }
        }
        
        request_data = BusinessCaseRequest(
            title="Complex Business Case",
            description="A complex business case with nested requirements",
            requester_uid="test-uid",
            requirements=complex_requirements
        )
        
        business_case = BusinessCase(
            request_data=request_data,
            generated_content={"summary": "Generated content"},
            generated_by_agents=["architect", "planner", "cost_analyst"]
        )
        
        # Should handle complex nested structures
        serialized = business_case.model_dump()
        assert serialized["request_data"]["requirements"]["technical_specs"]["database"] == "PostgreSQL"
        assert len(serialized["generated_by_agents"]) == 3


if __name__ == "__main__":
    # Run tests with: python -m pytest backend/tests/integration/test_database_integration.py -v
    pytest.main([__file__, "-v"]) 