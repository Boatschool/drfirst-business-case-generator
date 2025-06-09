"""
Unit tests for OrchestratorAgent.handle_value_approval method.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

from app.agents.orchestrator_agent import OrchestratorAgent, BusinessCaseStatus


class TestOrchestratorValueApproval:
    """Test cases for OrchestratorAgent.handle_value_approval method."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database with document references."""
        mock_db = Mock()
        mock_doc_ref = Mock()
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection
        return mock_db, mock_doc_ref

    @pytest.fixture
    def mock_case_data(self):
        """Create mock case data for testing."""
        return {
            "case_id": "test-case-123",
            "user_id": "test-user-456",
            "title": "Test Business Case",
            "status": BusinessCaseStatus.VALUE_APPROVED.value,
            "cost_estimate_v1": {"total_cost": 100000, "currency": "USD"},
            "value_projection_v1": {"scenarios": [{"case": "Base", "value": 200000}], "currency": "USD"},
            "history": [],
        }

    @pytest.fixture
    def orchestrator_with_mocks(self, mock_db):
        """Create OrchestratorAgent with mocked dependencies."""
        db_client, doc_ref = mock_db
        
        with patch('app.agents.orchestrator_agent.get_db', return_value=db_client):
            orchestrator = OrchestratorAgent(db=db_client)
            
            # Mock the _generate_financial_model method
            orchestrator._generate_financial_model = AsyncMock()
            
            return orchestrator, doc_ref

    # ============================================================================
    # Successful Value Approval Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_handle_value_approval_success_with_cost_approved(
        self, orchestrator_with_mocks, mock_case_data
    ):
        """Test successful value approval when cost is already approved."""
        orchestrator, mock_doc_ref = orchestrator_with_mocks
        
        # Setup document snapshot
        mock_snapshot = Mock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = mock_case_data
        
        # Mock asyncio.to_thread for document operations
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        # Mock successful financial model generation
        orchestrator._generate_financial_model.return_value = {
            "status": "success",
            "message": "Financial model generated successfully",
            "new_status": BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE.value,
        }
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            # Execute
            result = await orchestrator.handle_value_approval("test-case-123")
            
            # Assertions
            assert result["status"] == "success"
            assert result["message"] == "Financial model generated and ready for final review."
            assert result["new_status"] == BusinessCaseStatus.FINANCIAL_MODEL_COMPLETE.value
            
            # Verify _generate_financial_model was called
            orchestrator._generate_financial_model.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_value_approval_waiting_for_cost_data(
        self, orchestrator_with_mocks, mock_case_data
    ):
        """Test value approval when cost estimate data is not available."""
        orchestrator, mock_doc_ref = orchestrator_with_mocks
        
        # Remove cost estimate data
        mock_case_data["cost_estimate_v1"] = None
        
        mock_snapshot = Mock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = mock_case_data
        
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            # Execute
            result = await orchestrator.handle_value_approval("test-case-123")
            
            # Assertions
            assert result["status"] == "success"
            assert result["message"] == "Value projection approved. Awaiting cost estimate data."
            
            # Verify _generate_financial_model was NOT called
            orchestrator._generate_financial_model.assert_not_called()

    # ============================================================================
    # Error Handling Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_handle_value_approval_case_not_found(
        self, orchestrator_with_mocks
    ):
        """Test value approval with non-existent case."""
        orchestrator, mock_doc_ref = orchestrator_with_mocks
        
        mock_snapshot = Mock()
        mock_snapshot.exists = False
        
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            # Execute
            result = await orchestrator.handle_value_approval("non-existent-case")
            
            # Assertions
            assert result["status"] == "error"
            assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_value_approval_invalid_status(
        self, orchestrator_with_mocks, mock_case_data
    ):
        """Test value approval with invalid case status."""
        orchestrator, mock_doc_ref = orchestrator_with_mocks
        
        # Set invalid status
        mock_case_data["status"] = BusinessCaseStatus.COSTING_PENDING_REVIEW.value
        
        mock_snapshot = Mock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = mock_case_data
        
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            # Execute
            result = await orchestrator.handle_value_approval("test-case-123")
            
            # Assertions
            assert result["status"] == "error"
            assert "expected VALUE_APPROVED" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_value_approval_missing_value_data(
        self, orchestrator_with_mocks, mock_case_data
    ):
        """Test value approval with missing value projection data."""
        orchestrator, mock_doc_ref = orchestrator_with_mocks
        
        # Remove value projection data
        mock_case_data["value_projection_v1"] = None
        
        mock_snapshot = Mock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = mock_case_data
        
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            # Execute
            result = await orchestrator.handle_value_approval("test-case-123")
            
            # Assertions
            assert result["status"] == "error"
            assert "Value projection data missing despite VALUE_APPROVED status" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_value_approval_financial_model_failure(
        self, orchestrator_with_mocks, mock_case_data
    ):
        """Test value approval when financial model generation fails."""
        orchestrator, mock_doc_ref = orchestrator_with_mocks
        
        mock_snapshot = Mock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = mock_case_data
        
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        # Mock failed financial model generation
        orchestrator._generate_financial_model.return_value = {
            "status": "error",
            "message": "Failed to generate financial model",
        }
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            # Execute
            result = await orchestrator.handle_value_approval("test-case-123")
            
            # Assertions
            assert result["status"] == "error"
            assert "Failed to generate financial model" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_value_approval_exception_handling(
        self, orchestrator_with_mocks
    ):
        """Test value approval with exception during processing."""
        orchestrator, mock_doc_ref = orchestrator_with_mocks
        
        # Mock exception during document retrieval
        async def mock_to_thread_exception(func, *args):
            raise Exception("Database connection failed")
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread_exception):
            # Execute
            result = await orchestrator.handle_value_approval("test-case-123")
            
            # Assertions
            assert result["status"] == "error"
            assert "Error handling value approval" in result["message"] 