import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone
from app.agents.orchestrator_agent import OrchestratorAgent, EchoTool, BusinessCaseStatus


@pytest.fixture
def orchestrator_agent():
    """Fixture to create an OrchestratorAgent instance."""
    return OrchestratorAgent()


@pytest.fixture
def echo_tool():
    """Fixture to create an EchoTool instance."""
    return EchoTool()


@pytest.fixture
def mock_firestore_db():
    """Mock Firestore database client"""
    mock_db = Mock()
    mock_collection = Mock()
    mock_doc_ref = Mock()
    mock_doc_snapshot = Mock()
    
    mock_db.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_doc_ref
    
    return {
        'db': mock_db,
        'collection': mock_collection, 
        'doc_ref': mock_doc_ref,
        'doc_snapshot': mock_doc_snapshot
    }


@pytest.fixture
def sample_business_case_data():
    """Sample business case data for testing"""
    return {
        "case_id": "test-case-123",
        "user_id": "test-user-456",
        "title": "Test Business Case",
        "problem_statement": "This is a test problem statement",
        "status": BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value,
        "prd_draft": {
            "content_markdown": "# Test PRD Content\n\nThis is a test PRD.",
            "generated_by": "ProductManagerAgent",
            "version": "v1"
        },
        "system_design_v1_draft": {
            "content_markdown": "# Test System Design\n\nThis is a test system design.",
            "generated_by": "ArchitectAgent", 
            "version": "v1"
        },
        "history": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def sample_effort_estimate():
    """Sample effort estimate response from PlannerAgent"""
    return {
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
            "notes": "Standard web application development effort"
        }
    }


# Original tests
@pytest.mark.asyncio
async def test_echo_tool_run(echo_tool: EchoTool):
    """Test the EchoTool's run method."""
    input_string = "Hello, Echo!"
    output_string = await echo_tool.run(input_string)
    assert output_string == input_string


@pytest.mark.asyncio
async def test_orchestrator_run_echo_tool(orchestrator_agent: OrchestratorAgent):
    """Test the OrchestratorAgent's run_echo_tool method."""
    input_text = "Test message for orchestrator's echo tool"
    result = await orchestrator_agent.run_echo_tool(input_text)
    assert result == input_text


@pytest.mark.asyncio
async def test_orchestrator_handle_request_echo_success(
    orchestrator_agent: OrchestratorAgent,
):
    """Test the OrchestratorAgent's handle_request method for a successful echo."""
    request_type = "echo"
    payload = {"input_text": "Hello via handle_request"}
    response = await orchestrator_agent.handle_request(request_type, payload, "test-user-123")
    assert response["status"] == "success"
    assert response["message"] == "Echo request processed successfully."
    assert response["result"] == "Hello via handle_request"


@pytest.mark.asyncio
async def test_orchestrator_handle_request_echo_missing_payload(
    orchestrator_agent: OrchestratorAgent,
):
    """Test handle_request with echo type but missing input_text in payload."""
    request_type = "echo"
    payload = {}
    response = await orchestrator_agent.handle_request(request_type, payload, "test-user-123")
    assert response["status"] == "error"
    assert response["message"] == "Missing 'input_text' in payload for echo request."
    assert response["result"] is None


@pytest.mark.asyncio
async def test_orchestrator_handle_request_unknown_type(
    orchestrator_agent: OrchestratorAgent,
):
    """Test handle_request with an unknown request_type."""
    request_type = "unknown_action"
    payload = {"data": "some_data"}
    response = await orchestrator_agent.handle_request(request_type, payload, "test-user-123")
    assert response["status"] == "error"
    assert response["message"] == "Unknown request_type: unknown_action"
    assert response["result"] is None


# New tests for handle_system_design_approval
class TestHandleSystemDesignApproval:
    """Test suite for handle_system_design_approval method"""

    @pytest.mark.asyncio
    async def test_handle_system_design_approval_success(
        self, mock_firestore_db, sample_business_case_data, sample_effort_estimate
    ):
        """Test successful system design approval with effort estimation"""
        # Setup mocks
        db_mocks = mock_firestore_db
        db_mocks['doc_snapshot'].exists = True
        db_mocks['doc_snapshot'].to_dict.return_value = sample_business_case_data
        
        # Create orchestrator with mocked database
        orchestrator = OrchestratorAgent(db=db_mocks['db'])
        
        # Mock PlannerAgent
        mock_planner = AsyncMock()
        mock_planner.estimate_effort.return_value = sample_effort_estimate
        orchestrator._planner_agent = mock_planner
        
        with patch('asyncio.to_thread') as mock_to_thread:
            # Mock the Firestore operations
            mock_to_thread.side_effect = [
                db_mocks['doc_snapshot'],  # get() call
                None,  # first update() call (status change)
                None   # second update() call (effort estimate save)
            ]
            
            # Execute the method
            result = await orchestrator.handle_system_design_approval("test-case-123")
            
            # Assertions
            assert result["status"] == "success"
            assert result["message"] == "Effort estimation generated successfully"
            assert result["case_id"] == "test-case-123"
            assert result["new_status"] == BusinessCaseStatus.PLANNING_COMPLETE.value
            
            # Verify PlannerAgent was called correctly
            mock_planner.estimate_effort.assert_called_once_with(
                prd_content="# Test PRD Content\n\nThis is a test PRD.",
                system_design_content="# Test System Design\n\nThis is a test system design.",
                case_title="Test Business Case"
            )
            
            # Verify Firestore operations
            assert mock_to_thread.call_count == 3
            db_mocks['db'].collection.assert_called_with("businessCases")
            db_mocks['collection'].document.assert_called_with("test-case-123")

    @pytest.mark.asyncio
    async def test_handle_system_design_approval_case_not_found(
        self, mock_firestore_db
    ):
        """Test system design approval when case doesn't exist"""
        # Setup mocks
        db_mocks = mock_firestore_db
        db_mocks['doc_snapshot'].exists = False
        
        orchestrator = OrchestratorAgent(db=db_mocks['db'])
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = db_mocks['doc_snapshot']
            
            result = await orchestrator.handle_system_design_approval("nonexistent-case")
            
            assert result["status"] == "error"
            assert result["message"] == "Business case nonexistent-case not found"

    @pytest.mark.asyncio
    async def test_handle_system_design_approval_wrong_status(
        self, mock_firestore_db, sample_business_case_data
    ):
        """Test system design approval with wrong case status"""
        # Setup mocks with wrong status
        db_mocks = mock_firestore_db
        db_mocks['doc_snapshot'].exists = True
        wrong_status_data = sample_business_case_data.copy()
        wrong_status_data["status"] = BusinessCaseStatus.PRD_APPROVED.value
        db_mocks['doc_snapshot'].to_dict.return_value = wrong_status_data
        
        orchestrator = OrchestratorAgent(db=db_mocks['db'])
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = db_mocks['doc_snapshot']
            
            result = await orchestrator.handle_system_design_approval("test-case-123")
            
            assert result["status"] == "error"
            assert "expected SYSTEM_DESIGN_APPROVED" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_system_design_approval_missing_system_design(
        self, mock_firestore_db, sample_business_case_data
    ):
        """Test system design approval when system design is missing"""
        # Setup mocks without system design
        db_mocks = mock_firestore_db
        db_mocks['doc_snapshot'].exists = True
        no_design_data = sample_business_case_data.copy()
        del no_design_data["system_design_v1_draft"]
        db_mocks['doc_snapshot'].to_dict.return_value = no_design_data
        
        orchestrator = OrchestratorAgent(db=db_mocks['db'])
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = db_mocks['doc_snapshot']
            
            result = await orchestrator.handle_system_design_approval("test-case-123")
            
            assert result["status"] == "error"
            assert result["message"] == "System design draft not found"

    @pytest.mark.asyncio
    async def test_handle_system_design_approval_planner_failure(
        self, mock_firestore_db, sample_business_case_data
    ):
        """Test system design approval when PlannerAgent fails"""
        # Setup mocks
        db_mocks = mock_firestore_db
        db_mocks['doc_snapshot'].exists = True
        db_mocks['doc_snapshot'].to_dict.return_value = sample_business_case_data
        
        orchestrator = OrchestratorAgent(db=db_mocks['db'])
        
        # Mock PlannerAgent to fail
        mock_planner = AsyncMock()
        mock_planner.estimate_effort.return_value = {
            "status": "error",
            "message": "AI model unavailable"
        }
        orchestrator._planner_agent = mock_planner
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [
                db_mocks['doc_snapshot'],  # get() call
                None,  # first update() call (status change)
                None   # rollback update() call
            ]
            
            result = await orchestrator.handle_system_design_approval("test-case-123")
            
            assert result["status"] == "error"
            assert "Effort estimation failed: AI model unavailable" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_system_design_approval_exception_handling(
        self, mock_firestore_db
    ):
        """Test system design approval with unexpected exception"""
        # Setup mocks to raise exception
        db_mocks = mock_firestore_db
        
        orchestrator = OrchestratorAgent(db=db_mocks['db'])
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = Exception("Database connection error")
            
            result = await orchestrator.handle_system_design_approval("test-case-123")
            
            assert result["status"] == "error"
            assert "Error handling system design approval:" in result["message"]


# New tests for modified handle_prd_approval
class TestHandlePrdApproval:
    """Test suite for modified handle_prd_approval method"""

    @pytest.mark.asyncio
    async def test_handle_prd_approval_stops_at_system_design(
        self, mock_firestore_db, sample_business_case_data
    ):
        """Test that PRD approval now stops at SYSTEM_DESIGN_DRAFTED and doesn't call PlannerAgent"""
        # Setup mocks
        db_mocks = mock_firestore_db
        db_mocks['doc_snapshot'].exists = True
        prd_approved_data = sample_business_case_data.copy()
        prd_approved_data["status"] = BusinessCaseStatus.PRD_APPROVED.value
        db_mocks['doc_snapshot'].to_dict.return_value = prd_approved_data
        
        orchestrator = OrchestratorAgent(db=db_mocks['db'])
        
        # Mock ArchitectAgent to succeed
        mock_architect = AsyncMock()
        mock_architect.generate_system_design.return_value = {
            "status": "success",
            "system_design": {
                "content_markdown": "# Generated System Design\n\nTest design content"
            }
        }
        orchestrator._architect_agent = mock_architect
        
        # Mock PlannerAgent - this should NOT be called
        mock_planner = AsyncMock()
        orchestrator._planner_agent = mock_planner
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [
                db_mocks['doc_snapshot'],  # get() call
                None,  # status update to SYSTEM_DESIGN_DRAFTING
                None   # status update to SYSTEM_DESIGN_DRAFTED
            ]
            
            result = await orchestrator.handle_prd_approval("test-case-123")
            
            # Assertions
            assert result["status"] == "success"
            assert result["message"] == "System design generated successfully"
            assert result["case_id"] == "test-case-123" 
            assert result["new_status"] == BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value
            
            # Verify ArchitectAgent was called
            mock_architect.generate_system_design.assert_called_once()
            
            # Verify PlannerAgent was NOT called
            mock_planner.estimate_effort.assert_not_called()
            
            # Verify we don't have any PLANNING_* status updates
            assert mock_to_thread.call_count == 3  # Only 3 calls, not more

    @pytest.mark.asyncio 
    async def test_handle_prd_approval_architect_failure(
        self, mock_firestore_db, sample_business_case_data
    ):
        """Test PRD approval when ArchitectAgent fails"""
        # Setup mocks
        db_mocks = mock_firestore_db
        db_mocks['doc_snapshot'].exists = True
        prd_approved_data = sample_business_case_data.copy()
        prd_approved_data["status"] = BusinessCaseStatus.PRD_APPROVED.value
        db_mocks['doc_snapshot'].to_dict.return_value = prd_approved_data
        
        orchestrator = OrchestratorAgent(db=db_mocks['db'])
        
        # Mock ArchitectAgent to fail
        mock_architect = AsyncMock()
        mock_architect.generate_system_design.return_value = {
            "status": "error",
            "message": "Architecture analysis failed"
        }
        orchestrator._architect_agent = mock_architect
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [
                db_mocks['doc_snapshot'],  # get() call
                None,  # status update to SYSTEM_DESIGN_DRAFTING
                None   # revert status update
            ]
            
            result = await orchestrator.handle_prd_approval("test-case-123")
            
            assert result["status"] == "error"
            assert "System design generation failed: Architecture analysis failed" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_prd_approval_wrong_status(
        self, mock_firestore_db, sample_business_case_data
    ):
        """Test PRD approval with wrong case status"""
        # Setup mocks with wrong status
        db_mocks = mock_firestore_db
        db_mocks['doc_snapshot'].exists = True
        wrong_status_data = sample_business_case_data.copy()
        wrong_status_data["status"] = BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value
        db_mocks['doc_snapshot'].to_dict.return_value = wrong_status_data
        
        orchestrator = OrchestratorAgent(db=db_mocks['db'])
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = db_mocks['doc_snapshot']
            
            result = await orchestrator.handle_prd_approval("test-case-123")
            
            assert result["status"] == "error"
            assert "expected PRD_APPROVED" in result["message"]


# Example of how to run this test locally (optional, for demonstration)
# if __name__ == "__main__":
#     async def main():
#         # Test EchoTool directly
#         tool = EchoTool()
#         echo_result = await tool.run("Direct Echo Test")
#         print(f"Direct EchoTool Result: {echo_result}")

#         # Test OrchestratorAgent's echo tool
#         agent = OrchestratorAgent()
#         agent_echo_result = await agent.run_echo_tool("Agent Echo Test")
#         print(f"Agent EchoTool Result: {agent_echo_result}")

#     asyncio.run(main())
