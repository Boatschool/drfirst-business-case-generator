"""
End-to-end integration tests for effort estimation workflow.
These tests verify the complete orchestration flow from system design approval
through effort estimation to HITL review and cost estimation.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone

from app.agents.orchestrator_agent import OrchestratorAgent, BusinessCaseStatus
from app.agents.planner_agent import PlannerAgent
from app.agents.cost_analyst_agent import CostAnalystAgent


class TestEffortEstimationWorkflowIntegration:
    """Integration tests for the complete effort estimation workflow"""

    @pytest.fixture
    def sample_workflow_case(self):
        """Sample business case data for workflow testing"""
        return {
            "id": "integration-test-case",
            "title": "Integration Test Business Case",
            "user_id": "test-user-workflow",
            "status": BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "history": [],
            "prd_draft": {
                "content_markdown": "# Integration Test PRD\n\nThis is a comprehensive PRD for integration testing with detailed requirements and specifications.",
                "generated_by": "ProductManagerAgent",
                "version": "v1"
            },
            "system_design_v1_draft": {
                "content_markdown": "# Integration Test System Design\n\nComprehensive system architecture for testing.",
                "generated_by": "ArchitectAgent",
                "version": "v1"
            }
        }

    @pytest.fixture
    def mock_database_workflow(self):
        """Mock database for workflow testing"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_document = Mock()
        mock_doc_ref = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        mock_document.get.return_value = mock_doc_ref
        mock_document.update = AsyncMock()
        
        return {
            'db': mock_db,
            'collection': mock_collection,
            'document': mock_document,
            'doc_ref': mock_doc_ref
        }

    @pytest.mark.asyncio
    async def test_complete_system_design_to_effort_review_workflow(self, sample_workflow_case):
        """Test complete workflow: System Design Approved -> Effort Estimate -> Pending Review"""
        
        # Mock database
        mock_db = Mock()
        mock_collection = Mock()
        mock_document = Mock()
        mock_doc_ref = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        mock_document.get.return_value = mock_doc_ref
        mock_doc_ref.exists = True
        mock_doc_ref.to_dict.return_value = sample_workflow_case
        
        # Create orchestrator
        orchestrator = OrchestratorAgent(db=mock_db)
        
        # Mock PlannerAgent
        expected_effort_estimate = {
            "status": "success",
            "message": "Effort estimation completed successfully",
            "effort_breakdown": {
                "roles": [{"role": "Developer", "hours": 100}],
                "total_hours": 100,
                "estimated_duration_weeks": 2,
                "complexity_assessment": "Medium",
                "notes": "Test effort estimate"
            }
        }

        mock_planner = AsyncMock()
        mock_planner.estimate_effort.return_value = expected_effort_estimate
        orchestrator._planner_agent = mock_planner

        # Mock database operations
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [
                mock_doc_ref,  # get() call
                None,  # first update
                None,  # second update
                None   # third update
            ]

            # Execute the workflow
            result = await orchestrator.handle_system_design_approval("integration-test-case")

            # Verify successful progression
            assert result["status"] == "success"
            assert result["case_id"] == "integration-test-case"
            assert result["new_status"] == BusinessCaseStatus.EFFORT_PENDING_REVIEW.value

            # Verify database interactions
            assert mock_to_thread.call_count == 4

    @pytest.mark.asyncio
    async def test_complete_effort_approval_to_cost_review_workflow(self, sample_workflow_case):
        """Test complete workflow: Effort Approved -> Cost Analysis -> Cost Pending Review"""
        
        # Setup case with effort estimate
        effort_approved_case = sample_workflow_case.copy()
        effort_approved_case["status"] = BusinessCaseStatus.EFFORT_APPROVED.value
        effort_approved_case["effort_estimate_v1"] = {
            "roles": [{"role": "Developer", "hours": 100}],
            "total_hours": 100
        }

        # Mock database
        mock_db = Mock()
        mock_collection = Mock()
        mock_document = Mock()
        mock_doc_ref = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        mock_document.get.return_value = mock_doc_ref
        mock_doc_ref.exists = True
        mock_doc_ref.to_dict.return_value = effort_approved_case
        
        # Create orchestrator
        orchestrator = OrchestratorAgent(db=mock_db)
        
        # Mock CostAnalystAgent
        expected_cost_estimate = {
            "status": "success",
            "message": "Cost calculation completed successfully",
            "cost_estimate": {
                "estimated_cost": 10000.0,
                "currency": "USD"
            }
        }

        mock_cost_analyst = AsyncMock()
        mock_cost_analyst.calculate_cost.return_value = expected_cost_estimate
        orchestrator._cost_analyst_agent = mock_cost_analyst

        # Mock database operations
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [
                mock_doc_ref,  # get() call
                None,  # first update
                None,  # second update
                None   # third update
            ]

            # Execute the workflow
            result = await orchestrator.handle_effort_approval("integration-test-case")

            # Verify successful progression
            assert result["status"] == "success"
            assert result["case_id"] == "integration-test-case"
            assert result["new_status"] == BusinessCaseStatus.COSTING_PENDING_REVIEW.value

            # Verify database interactions
            assert mock_to_thread.call_count == 4

    @pytest.mark.asyncio
    async def test_workflow_failure_and_rollback(self, sample_workflow_case):
        """Test workflow resilience when agents fail"""
        
        # Mock database
        mock_db = Mock()
        mock_collection = Mock()
        mock_document = Mock()
        mock_doc_ref = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        mock_document.get.return_value = mock_doc_ref
        mock_doc_ref.exists = True
        mock_doc_ref.to_dict.return_value = sample_workflow_case
        
        # Create orchestrator
        orchestrator = OrchestratorAgent(db=mock_db)
        
        # Mock PlannerAgent to fail
        mock_planner = AsyncMock()
        mock_planner.estimate_effort.return_value = {
            "status": "error",
            "message": "AI model unavailable"
        }
        orchestrator._planner_agent = mock_planner

        # Mock database operations
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [
                mock_doc_ref,  # get() call
                None,  # first update
                None   # rollback update
            ]

            # Execute the workflow
            result = await orchestrator.handle_system_design_approval("integration-test-case")

            # Verify error handling
            assert result["status"] == "error"
            assert "AI model unavailable" in result["message"]

            # Verify rollback occurred (3 calls instead of 4)
            assert mock_to_thread.call_count == 3

    # Note: Additional complex integration tests for concurrent processing 
    # and detailed status transitions could be added here for comprehensive coverage 