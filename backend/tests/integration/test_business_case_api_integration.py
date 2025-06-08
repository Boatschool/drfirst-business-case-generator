"""
Integration tests for business case API endpoints.
These tests use real Firestore connections to catch production-like issues.
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timezone
from app.core.dependencies import get_firestore_service
from app.api.v1.cases.list_retrieve_routes import list_user_cases
from app.api.v1.cases.models import BusinessCaseSummary
from app.agents.orchestrator_agent import OrchestratorAgent, BusinessCaseData, BusinessCaseStatus


class TestBusinessCaseAPIIntegration:
    """Integration tests to prevent data conversion issues in production."""

    @pytest.fixture
    def firestore_service(self):
        """Get the real Firestore service."""
        return get_firestore_service()

    @pytest.fixture
    def test_user_id(self):
        """Test user ID for integration testing."""
        return "integration-test-user-123"

    @pytest.fixture
    def mock_current_user(self, test_user_id):
        """Mock current user for integration testing."""
        return {
            "uid": test_user_id,
            "email": "integration-test@example.com",
            "name": "Integration Test User"
        }

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_end_to_end_business_case_workflow(self, firestore_service, mock_current_user, test_user_id):
        """Test the complete workflow from creation to listing."""
        # Step 1: Create a test business case
        orchestrator = OrchestratorAgent()
        
        test_request = {
            "problem_statement": "Integration test problem statement",
            "title": "Integration Test Case",
            "relevant_links": ["https://example.com"]
        }
        
        # Create business case
        case_response = await orchestrator.handle_request(
            request_type="initiate_case",
            request_data=test_request,
            user_id=test_user_id
        )
        
        assert case_response["status"] == "success"
        case_id = case_response["case_id"]
        
        try:
            # Step 2: List business cases for the user
            class MockRequest:
                pass
            
            result = await list_user_cases(
                request=MockRequest(),
                current_user=mock_current_user,
                firestore_service=firestore_service,
                limit=10,
                offset=0,
                status_filter=None,
                created_after=None,
                sort_by="updated_at",
                sort_order="desc"
            )
            
            # Step 3: Verify the created case appears in the list
            assert len(result) > 0, "No business cases returned"
            
            # Find our test case
            test_case = None
            for case in result:
                if case.case_id == case_id:
                    test_case = case
                    break
            
            assert test_case is not None, f"Test case {case_id} not found in results"
            assert isinstance(test_case, BusinessCaseSummary), "Result is not a BusinessCaseSummary"
            assert test_case.user_id == test_user_id, "User ID mismatch"
            assert test_case.title == "Integration Test Case", "Title mismatch"
            
            # Step 4: Verify all returned cases have required fields
            for case in result:
                assert hasattr(case, 'case_id'), "Missing case_id field"
                assert hasattr(case, 'user_id'), "Missing user_id field - THIS WAS THE BUG!"
                assert hasattr(case, 'title'), "Missing title field"
                assert hasattr(case, 'status'), "Missing status field"
                assert hasattr(case, 'created_at'), "Missing created_at field"
                assert hasattr(case, 'updated_at'), "Missing updated_at field"
                
                # Verify field values are not None/empty
                assert case.case_id, "case_id is empty"
                assert case.user_id, "user_id is empty"
                assert case.title, "title is empty"
                assert case.status, "status is empty"
                assert case.created_at, "created_at is empty"
                assert case.updated_at, "updated_at is empty"
        
        finally:
            # Cleanup: Delete the test case
            try:
                await firestore_service.delete_business_case(case_id)
            except Exception as e:
                print(f"Warning: Could not cleanup test case {case_id}: {e}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_list_cases_with_existing_user(self, firestore_service):
        """Test listing cases for a user known to have existing cases."""
        # Use the actual user ID from the production system
        real_user_id = "iYvf6yO3NiUzKiGUySoTV0U66nn1"
        mock_current_user = {
            "uid": real_user_id,
            "email": "rwince435@gmail.com"
        }
        
        class MockRequest:
            pass
        
        # This should return the user's actual business cases
        result = await list_user_cases(
            request=MockRequest(),
            current_user=mock_current_user,
            firestore_service=firestore_service,
            limit=20,  # Get more cases to test
            offset=0,
            status_filter=None,
            created_after=None,
            sort_by="updated_at",
            sort_order="desc"
        )
        
        # Should have business cases (as we confirmed in debugging)
        assert len(result) > 0, "Expected existing business cases but got none"
        
        # Verify all cases have correct structure
        for i, case in enumerate(result):
            assert isinstance(case, BusinessCaseSummary), f"Case {i} is not a BusinessCaseSummary"
            assert case.user_id == real_user_id, f"Case {i} has wrong user_id: {case.user_id}"
            assert case.case_id, f"Case {i} has empty case_id"
            assert case.title, f"Case {i} has empty title"
            assert case.status, f"Case {i} has empty status"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty_results_handling(self, firestore_service):
        """Test that empty results are handled properly."""
        # Use a user ID that definitely has no cases
        fake_user_id = "definitely-no-cases-user-999"
        mock_current_user = {
            "uid": fake_user_id,
            "email": "nocases@example.com"
        }
        
        class MockRequest:
            pass
        
        result = await list_user_cases(
            request=MockRequest(),
            current_user=mock_current_user,
            firestore_service=firestore_service,
            limit=10,
            offset=0,
            status_filter=None,
            created_after=None,
            sort_by="updated_at",
            sort_order="desc"
        )
        
        # Should return empty list, not None or raise an error
        assert result == [], f"Expected empty list but got: {result}"
        assert isinstance(result, list), "Result should be a list even when empty" 