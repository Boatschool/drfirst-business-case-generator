"""
Unit tests for OrchestratorAgent's handle_cost_approval method.
Tests the cost approval workflow and value analysis triggering.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone
import asyncio

from app.agents.orchestrator_agent import OrchestratorAgent, BusinessCaseStatus


class TestOrchestratorCostApproval:
    """Unit tests for OrchestratorAgent cost approval functionality"""

    @pytest.fixture
    def mock_db(self):
        """Mock Firestore database client"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_document = Mock()
        mock_doc_ref = Mock()
        
        # Setup collection/document chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        return mock_db, mock_doc_ref

    @pytest.fixture
    def mock_case_data(self):
        """Mock business case data with approved cost estimate"""
        return {
            "case_id": "test-case-123",
            "title": "Test Business Case",
            "status": BusinessCaseStatus.COSTING_APPROVED.value,
            "prd_draft": {
                "content_markdown": "# Test PRD\n\nThis is a test PRD for value analysis.",
                "title": "Test Product",
                "version": "v1"
            },
            "cost_estimate_v1": {
                "estimated_cost": 35000.00,
                "currency": "USD",
                "breakdown_by_role": [
                    {"role": "Developer", "hours": 100, "total_cost": 15000}
                ]
            },
            "history": []
        }

    @pytest.fixture
    def orchestrator_with_mocks(self, mock_db):
        """Create OrchestratorAgent with mocked dependencies"""
        db_client, doc_ref = mock_db
        
        with patch('app.agents.orchestrator_agent.get_db', return_value=db_client):
            orchestrator = OrchestratorAgent(db=db_client)
            
            # Mock the sales value analyst agent
            mock_sales_agent = Mock()
            orchestrator._sales_value_analyst_agent = mock_sales_agent
            
            return orchestrator, doc_ref, mock_sales_agent

    # ============================================================================
    # Successful Cost Approval Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_handle_cost_approval_success_with_value_analysis(
        self, orchestrator_with_mocks, mock_case_data
    ):
        """Test successful cost approval with value analysis generation."""
        orchestrator, mock_doc_ref, mock_sales_agent = orchestrator_with_mocks
        
        # Setup document snapshot
        mock_snapshot = Mock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = mock_case_data
        
        # Mock asyncio.to_thread for document operations
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        # Mock SalesValueAnalystAgent success
        mock_sales_agent.project_value = AsyncMock(return_value={
            "status": "success",
            "value_projection": {
                "scenarios": [
                    {"case": "Low", "value": 50000},
                    {"case": "Base", "value": 100000},
                    {"case": "High", "value": 200000}
                ],
                "currency": "USD",
                "methodology": "AI-assisted projection"
            }
        })
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            with patch('app.core.dependencies.get_array_union') as mock_array_union:
                mock_array_union.side_effect = lambda x: x  # Return input as-is
                
                # Execute
                result = await orchestrator.handle_cost_approval("test-case-123")
                
                # Assertions
                assert result["status"] == "success"
                assert result["message"] == "Value projection generated and ready for review."
                assert result["new_status"] == BusinessCaseStatus.VALUE_PENDING_REVIEW.value
                assert result["case_id"] == "test-case-123"
                
                # Verify SalesValueAnalystAgent was called
                mock_sales_agent.project_value.assert_called_once()
                call_args = mock_sales_agent.project_value.call_args
                assert call_args[1]["prd_content"] == mock_case_data["prd_draft"]["content_markdown"]
                assert call_args[1]["case_title"] == mock_case_data["title"]
                
                # Verify document updates (2 updates: VALUE_ANALYSIS_COMPLETE, then VALUE_PENDING_REVIEW)
                assert mock_doc_ref.update.call_count == 3  # Initial status, complete, pending review

    @pytest.mark.asyncio
    async def test_handle_cost_approval_sales_agent_failure(
        self, orchestrator_with_mocks, mock_case_data
    ):
        """Test cost approval with SalesValueAnalystAgent failure."""
        orchestrator, mock_doc_ref, mock_sales_agent = orchestrator_with_mocks
        
        # Setup document snapshot
        mock_snapshot = Mock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = mock_case_data
        
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        # Mock SalesValueAnalystAgent failure
        mock_sales_agent.project_value = AsyncMock(return_value={
            "status": "error",
            "message": "Failed to generate value projection due to insufficient data",
            "value_projection": None
        })
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            with patch('app.core.dependencies.get_array_union') as mock_array_union:
                mock_array_union.side_effect = lambda x: x
                
                # Execute
                result = await orchestrator.handle_cost_approval("test-case-123")
                
                # Assertions
                assert result["status"] == "error"
                assert "Failed to generate value projection" in result["message"]
                
                # Verify status was reverted
                # Should have 2 updates: initial status change, then revert on failure
                assert mock_doc_ref.update.call_count == 2

    # ============================================================================
    # Validation and Error Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_handle_cost_approval_case_not_found(self, orchestrator_with_mocks):
        """Test cost approval for non-existent case."""
        orchestrator, mock_doc_ref, _ = orchestrator_with_mocks
        
        # Setup non-existent document
        mock_snapshot = Mock()
        mock_snapshot.exists = False
        
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            # Execute
            result = await orchestrator.handle_cost_approval("non-existent-case")
            
            # Assertions
            assert result["status"] == "error"
            assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_cost_approval_invalid_status(
        self, orchestrator_with_mocks, mock_case_data
    ):
        """Test cost approval from invalid status."""
        orchestrator, mock_doc_ref, _ = orchestrator_with_mocks
        
        # Setup case with wrong status
        invalid_case_data = mock_case_data.copy()
        invalid_case_data["status"] = BusinessCaseStatus.COSTING_PENDING_REVIEW.value
        
        mock_snapshot = Mock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = invalid_case_data
        
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            # Execute
            result = await orchestrator.handle_cost_approval("test-case-123")
            
            # Assertions
            assert result["status"] == "error"
            assert "expected COSTING_APPROVED" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_cost_approval_missing_prd(
        self, orchestrator_with_mocks, mock_case_data
    ):
        """Test cost approval with missing PRD content."""
        orchestrator, mock_doc_ref, _ = orchestrator_with_mocks
        
        # Setup case without PRD
        case_without_prd = mock_case_data.copy()
        del case_without_prd["prd_draft"]
        
        mock_snapshot = Mock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = case_without_prd
        
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            # Execute
            result = await orchestrator.handle_cost_approval("test-case-123")
            
            # Assertions
            assert result["status"] == "error"
            assert "PRD draft content not found" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_cost_approval_exception_handling(
        self, orchestrator_with_mocks, mock_case_data
    ):
        """Test cost approval with unexpected exception."""
        orchestrator, mock_doc_ref, mock_sales_agent = orchestrator_with_mocks
        
        # Mock to_thread to raise exception
        async def mock_to_thread_exception(func, *args):
            raise Exception("Database connection timeout")
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread_exception):
            # Execute
            result = await orchestrator.handle_cost_approval("test-case-123")
            
            # Assertions
            assert result["status"] == "error"
            assert "Error handling cost approval" in result["message"]
            assert "Database connection timeout" in result["message"]

    # ============================================================================
    # Integration and Edge Case Tests
    # ============================================================================

    @pytest.mark.asyncio
    async def test_handle_cost_approval_with_empty_prd_content(
        self, orchestrator_with_mocks, mock_case_data
    ):
        """Test cost approval with empty PRD content."""
        orchestrator, mock_doc_ref, _ = orchestrator_with_mocks
        
        # Setup case with empty PRD content
        case_with_empty_prd = mock_case_data.copy()
        case_with_empty_prd["prd_draft"]["content_markdown"] = ""
        
        mock_snapshot = Mock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = case_with_empty_prd
        
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            # Execute
            result = await orchestrator.handle_cost_approval("test-case-123")
            
            # Assertions
            assert result["status"] == "error"
            assert "PRD draft content not found" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_cost_approval_status_transitions(
        self, orchestrator_with_mocks, mock_case_data
    ):
        """Test proper status transitions during cost approval."""
        orchestrator, mock_doc_ref, mock_sales_agent = orchestrator_with_mocks
        
        # Setup successful scenario
        mock_snapshot = Mock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = mock_case_data
        
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        mock_sales_agent.project_value = AsyncMock(return_value={
            "status": "success",
            "value_projection": {"scenarios": [{"case": "Base", "value": 100000}]}
        })
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            with patch('app.core.dependencies.get_array_union') as mock_array_union:
                mock_array_union.side_effect = lambda x: x
                
                # Execute
                await orchestrator.handle_cost_approval("test-case-123")
                
                # Verify the sequence of status updates
                update_calls = mock_doc_ref.update.call_args_list
                
                # Should have 3 updates: 
                # 1. VALUE_ANALYSIS_IN_PROGRESS
                # 2. VALUE_ANALYSIS_COMPLETE with value_projection_v1
                # 3. VALUE_PENDING_REVIEW
                assert len(update_calls) == 3
                
                # Check first update (VALUE_ANALYSIS_IN_PROGRESS)
                first_update = update_calls[0][0][0]
                assert first_update["status"] == BusinessCaseStatus.VALUE_ANALYSIS_IN_PROGRESS.value
                
                # Check second update (VALUE_ANALYSIS_COMPLETE with data)
                second_update = update_calls[1][0][0]
                assert second_update["status"] == BusinessCaseStatus.VALUE_ANALYSIS_COMPLETE.value
                assert "value_projection_v1" in second_update
                
                # Check third update (VALUE_PENDING_REVIEW)
                third_update = update_calls[2][0][0]
                assert third_update["status"] == BusinessCaseStatus.VALUE_PENDING_REVIEW.value

    @pytest.mark.asyncio
    async def test_handle_cost_approval_logging_and_metadata(
        self, orchestrator_with_mocks, mock_case_data
    ):
        """Test that cost approval includes proper logging and metadata."""
        orchestrator, mock_doc_ref, mock_sales_agent = orchestrator_with_mocks
        
        mock_snapshot = Mock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = mock_case_data
        
        async def mock_to_thread(func, *args):
            return mock_snapshot
        
        mock_sales_agent.project_value = AsyncMock(return_value={
            "status": "success",
            "value_projection": {"scenarios": [{"case": "Base", "value": 100000}]}
        })
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            with patch('app.core.dependencies.get_array_union') as mock_array_union:
                mock_array_union.side_effect = lambda x: x
                
                # Execute
                await orchestrator.handle_cost_approval("test-case-123")
                
                # Check that value projection includes metadata
                update_calls = mock_doc_ref.update.call_args_list
                value_complete_update = update_calls[1][0][0]
                
                value_projection = value_complete_update["value_projection_v1"]
                assert value_projection["generated_by"] == "SalesValueAnalystAgent"
                assert value_projection["version"] == "v1"
                assert "generated_timestamp" in value_projection 