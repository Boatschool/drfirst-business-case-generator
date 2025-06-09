"""
Unit tests for business case listing API endpoints.
These tests help prevent data conversion and validation issues.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock
from starlette.requests import Request
from starlette.datastructures import URL
from app.api.v1.cases.list_retrieve_routes import list_user_cases
from app.api.v1.cases.models import BusinessCaseSummary
from app.agents.orchestrator_agent import BusinessCaseData, BusinessCaseStatus


class TestBusinessCaseListAPI:
    """Test suite for business case listing API to prevent conversion issues."""

    @pytest.fixture
    def mock_business_case(self):
        """Create a mock business case for testing."""
        return BusinessCaseData(
            case_id="test-case-123",
            user_id="test-user-456",
            title="Test Business Case",
            problem_statement="Test problem",
            status=BusinessCaseStatus.PRD_APPROVED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @pytest.fixture
    def mock_current_user(self):
        """Create a mock current user for testing."""
        return {"uid": "test-user-456", "email": "test@example.com"}

    @pytest.fixture
    def mock_request(self):
        """Create a mock request object."""
        # Create a proper Starlette Request object
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/v1/cases",
            "query_string": b"",
            "headers": [],
        }
        return Request(scope)

    @pytest.fixture
    def mock_firestore_service(self):
        """Create a mock firestore service."""
        service = Mock()
        service.list_business_cases_for_user = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_business_case_summary_creation(self, mock_business_case):
        """Test that BusinessCaseSummary can be created from BusinessCaseData."""
        # This test ensures all required fields are properly mapped
        summary = BusinessCaseSummary(
            case_id=mock_business_case.case_id,
            user_id=mock_business_case.user_id,  # This field was missing before!
            title=mock_business_case.title,
            status=mock_business_case.status.value,
            created_at=mock_business_case.created_at,
            updated_at=mock_business_case.updated_at
        )
        
        assert summary.case_id == "test-case-123"
        assert summary.user_id == "test-user-456"
        assert summary.title == "Test Business Case"
        assert summary.status == "PRD_APPROVED"

    @pytest.mark.asyncio
    async def test_list_user_cases_with_data(self, mock_request, mock_current_user, 
                                           mock_firestore_service, mock_business_case):
        """Test that list_user_cases properly converts business cases to summaries."""
        # Setup
        mock_firestore_service.list_business_cases_for_user.return_value = [mock_business_case]
        
        # Execute
        result = await list_user_cases(
            request=mock_request,
            current_user=mock_current_user,
            firestore_service=mock_firestore_service,
            limit=10,
            offset=0,
            status_filter=None,
            created_after=None,
            sort_by="updated_at",
            sort_order="desc"
        )
        
        # Verify
        assert len(result) == 1
        assert isinstance(result[0], BusinessCaseSummary)
        assert result[0].case_id == "test-case-123"
        assert result[0].user_id == "test-user-456"  # Critical field that was missing
        assert result[0].title == "Test Business Case"

    @pytest.mark.asyncio
    async def test_list_user_cases_empty_result(self, mock_request, mock_current_user, 
                                              mock_firestore_service):
        """Test that empty results are handled properly."""
        # Setup
        mock_firestore_service.list_business_cases_for_user.return_value = []
        
        # Execute
        result = await list_user_cases(
            request=mock_request,
            current_user=mock_current_user,
            firestore_service=mock_firestore_service,
            limit=10,
            offset=0,
            status_filter=None,
            created_after=None,
            sort_by="updated_at",
            sort_order="desc"
        )
        
        # Verify
        assert result == []

    @pytest.mark.asyncio
    async def test_business_case_summary_validation_error(self):
        """Test that missing required fields cause validation errors."""
        with pytest.raises(Exception):  # Should be a ValidationError from Pydantic
            BusinessCaseSummary(
                case_id="test-case-123",
                # user_id missing - this should fail!
                title="Test Business Case",
                status="PRD_APPROVED",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )

    def test_business_case_summary_required_fields(self):
        """Test that all required fields are present in BusinessCaseSummary."""
        from app.api.v1.cases.models import BusinessCaseSummary
        import inspect
        
        # Get the BusinessCaseSummary model
        signature = inspect.signature(BusinessCaseSummary.__init__)
        required_fields = []
        
        for param_name, param in signature.parameters.items():
            if param_name != 'self' and param.default == inspect.Parameter.empty:
                required_fields.append(param_name)
        
        # These are the critical fields that must be present
        expected_fields = ['case_id', 'user_id', 'title', 'status', 'created_at', 'updated_at']
        
        for field in expected_fields:
            assert field in str(BusinessCaseSummary.__annotations__), f"Required field '{field}' missing from BusinessCaseSummary" 