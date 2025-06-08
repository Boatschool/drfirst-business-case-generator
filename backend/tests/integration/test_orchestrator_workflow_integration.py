"""
Integration tests for orchestrator workflow
Tests the complete workflow from PRD approval through system design to effort estimation
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone

from app.agents.orchestrator_agent import OrchestratorAgent, BusinessCaseStatus


class TestOrchestratorWorkflowIntegration:
    """Integration tests for orchestrator workflow"""

    @pytest.fixture
    def sample_business_case(self):
        """Sample business case for workflow testing"""
        return {
            "case_id": "integration-test-case",
            "user_id": "test-user-123", 
            "title": "Integration Test Business Case",
            "problem_statement": "Testing the complete orchestrator workflow",
            "status": BusinessCaseStatus.PRD_APPROVED.value,
            "prd_draft": {
                "content_markdown": "# Integration Test PRD\n\nThis is a comprehensive PRD for testing.",
                "generated_by": "ProductManagerAgent",
                "version": "v1"
            },
            "history": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

    @pytest.fixture
    def mock_orchestrator_with_agents(self):
        """Create orchestrator with mocked agents"""
        orchestrator = OrchestratorAgent()
        
        # Mock the database
        mock_db = Mock()
        orchestrator._db = mock_db
        orchestrator._db_initialized = True
        
        # Mock ArchitectAgent
        mock_architect = AsyncMock()
        mock_architect.generate_system_design.return_value = {
            "status": "success",
            "system_design": {
                "content_markdown": "# Generated System Design\n\nTest system architecture design",
                "components": ["Web API", "Database", "Frontend"],
                "technologies": ["Python", "FastAPI", "React"]
            }
        }
        orchestrator._architect_agent = mock_architect
        
        # Mock PlannerAgent 
        mock_planner = AsyncMock()
        mock_planner.estimate_effort.return_value = {
            "status": "success",
            "message": "Effort estimation completed successfully",
            "effort_breakdown": {
                "roles": [
                    {"role": "Product Manager", "hours": 40},
                    {"role": "Lead Developer", "hours": 120},
                    {"role": "Senior Developer", "hours": 200},
                    {"role": "Junior Developer", "hours": 80},
                    {"role": "QA Engineer", "hours": 60},
                    {"role": "DevOps Engineer", "hours": 40},
                    {"role": "UI/UX Designer", "hours": 80}
                ],
                "total_hours": 620,
                "estimated_duration_weeks": 8,
                "complexity_assessment": "Medium",
                "notes": "Integration test effort estimate"
            }
        }
        orchestrator._planner_agent = mock_planner
        
        return {
            'orchestrator': orchestrator,
            'mock_db': mock_db,
            'mock_architect': mock_architect,
            'mock_planner': mock_planner
        }

    @pytest.mark.asyncio
    async def test_complete_workflow_prd_to_effort_estimation(
        self, mock_orchestrator_with_agents, sample_business_case
    ):
        """Test complete workflow: PRD approved → System Design → Effort Estimation"""
        
        mocks = mock_orchestrator_with_agents
        orchestrator = mocks['orchestrator']
        mock_db = mocks['mock_db']
        mock_architect = mocks['mock_architect']
        mock_planner = mocks['mock_planner']
        
        # Setup Firestore mocks
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc_snapshot = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        # Test Step 1: PRD Approval (should stop at SYSTEM_DESIGN_DRAFTED)
        mock_doc_snapshot.exists = True
        mock_doc_snapshot.to_dict.return_value = sample_business_case
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [
                mock_doc_snapshot,  # get() call
                None,  # status update to SYSTEM_DESIGN_DRAFTING
                None   # status update to SYSTEM_DESIGN_DRAFTED
            ]
            
            prd_result = await orchestrator.handle_prd_approval("integration-test-case")
            
            # Verify PRD approval completed correctly
            assert prd_result["status"] == "success"
            assert prd_result["new_status"] == BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value
            assert "System design generated successfully" in prd_result["message"]
            
            # Verify ArchitectAgent was called but PlannerAgent was NOT
            mock_architect.generate_system_design.assert_called_once()
            mock_planner.estimate_effort.assert_not_called()
            
            # Reset mock call counts for next step
            mock_architect.reset_mock()
            mock_planner.reset_mock()
        
        # Test Step 2: System Design Approval (should trigger effort estimation)
        # Update sample case to reflect system design approval state
        approved_case = sample_business_case.copy()
        approved_case["status"] = BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value
        approved_case["system_design_v1_draft"] = {
            "content_markdown": "# Generated System Design\n\nTest system architecture design",
            "generated_by": "ArchitectAgent",
            "version": "v1"
        }
        
        mock_doc_snapshot.to_dict.return_value = approved_case
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [
                mock_doc_snapshot,  # get() call
                None,  # status update to PLANNING_IN_PROGRESS
                None   # status update to PLANNING_COMPLETE
            ]
            
            design_result = await orchestrator.handle_system_design_approval("integration-test-case")
            
            # Verify system design approval completed correctly
            assert design_result["status"] == "success"
            assert design_result["new_status"] == BusinessCaseStatus.PLANNING_COMPLETE.value
            assert "Effort estimation generated successfully" in design_result["message"]
            
            # Verify PlannerAgent was called correctly
            mock_planner.estimate_effort.assert_called_once_with(
                prd_content="# Integration Test PRD\n\nThis is a comprehensive PRD for testing.",
                system_design_content="# Generated System Design\n\nTest system architecture design",
                case_title="Integration Test Business Case"
            )
            
            # Verify ArchitectAgent was NOT called in this step
            mock_architect.generate_system_design.assert_not_called()

    @pytest.mark.asyncio
    async def test_workflow_separation_of_concerns(
        self, mock_orchestrator_with_agents, sample_business_case
    ):
        """Test that workflow steps are properly separated and don't interfere"""
        
        mocks = mock_orchestrator_with_agents
        orchestrator = mocks['orchestrator']
        mock_db = mocks['mock_db']
        mock_architect = mocks['mock_architect']
        mock_planner = mocks['mock_planner']
        
        # Setup Firestore mocks
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc_snapshot = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_snapshot.exists = True
        mock_doc_snapshot.to_dict.return_value = sample_business_case
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = mock_doc_snapshot
            
            # Test that PRD approval doesn't directly call effort estimation
            await orchestrator.handle_prd_approval("integration-test-case")
            
            # Verify separation: only ArchitectAgent should be called
            mock_architect.generate_system_design.assert_called_once()
            mock_planner.estimate_effort.assert_not_called()

    @pytest.mark.asyncio
    async def test_workflow_error_handling_rollback(
        self, mock_orchestrator_with_agents, sample_business_case
    ):
        """Test that workflow errors properly rollback state"""
        
        mocks = mock_orchestrator_with_agents
        orchestrator = mocks['orchestrator']
        mock_db = mocks['mock_db']
        mock_planner = mocks['mock_planner']
        
        # Setup for system design approval test
        approved_case = sample_business_case.copy()
        approved_case["status"] = BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value
        approved_case["system_design_v1_draft"] = {
            "content_markdown": "# Test System Design",
            "generated_by": "ArchitectAgent",
            "version": "v1"
        }
        
        # Setup Firestore mocks
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc_snapshot = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_snapshot.exists = True
        mock_doc_snapshot.to_dict.return_value = approved_case
        
        # Make PlannerAgent fail
        mock_planner.estimate_effort.return_value = {
            "status": "error",
            "message": "AI service temporarily unavailable"
        }
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [
                mock_doc_snapshot,  # get() call
                None,  # status update to PLANNING_IN_PROGRESS
                None   # rollback status update to SYSTEM_DESIGN_APPROVED
            ]
            
            result = await orchestrator.handle_system_design_approval("integration-test-case")
            
            # Verify error handling
            assert result["status"] == "error"
            assert "Effort estimation failed" in result["message"]
            assert "AI service temporarily unavailable" in result["message"]
            
            # Verify rollback occurred (3 Firestore operations: get, update, rollback)
            assert mock_to_thread.call_count == 3

    @pytest.mark.asyncio
    async def test_workflow_status_validation(
        self, mock_orchestrator_with_agents, sample_business_case
    ):
        """Test that workflow methods validate status correctly"""
        
        mocks = mock_orchestrator_with_agents
        orchestrator = mocks['orchestrator']
        mock_db = mocks['mock_db']
        
        # Setup Firestore mocks
        mock_collection = Mock()
        mock_doc_ref = Mock() 
        mock_doc_snapshot = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_snapshot.exists = True
        
        # Test PRD approval with wrong status
        wrong_status_case = sample_business_case.copy()
        wrong_status_case["status"] = BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value
        mock_doc_snapshot.to_dict.return_value = wrong_status_case
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = mock_doc_snapshot
            
            prd_result = await orchestrator.handle_prd_approval("integration-test-case")
            
            assert prd_result["status"] == "error"
            assert "expected PRD_APPROVED" in prd_result["message"]
        
        # Test system design approval with wrong status
        wrong_status_case["status"] = BusinessCaseStatus.PRD_APPROVED.value
        mock_doc_snapshot.to_dict.return_value = wrong_status_case
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = mock_doc_snapshot
            
            design_result = await orchestrator.handle_system_design_approval("integration-test-case")
            
            assert design_result["status"] == "error"
            assert "expected SYSTEM_DESIGN_APPROVED" in design_result["message"] 