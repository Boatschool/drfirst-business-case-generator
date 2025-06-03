import pytest
import asyncio
from app.agents.orchestrator_agent import OrchestratorAgent, EchoTool

@pytest.fixture
def orchestrator_agent():
    """Fixture to create an OrchestratorAgent instance."""
    return OrchestratorAgent()

@pytest.fixture
def echo_tool():
    """Fixture to create an EchoTool instance."""
    return EchoTool()

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
async def test_orchestrator_handle_request_echo_success(orchestrator_agent: OrchestratorAgent):
    """Test the OrchestratorAgent's handle_request method for a successful echo."""
    request_type = "echo"
    payload = {"input_text": "Hello via handle_request"}
    response = await orchestrator_agent.handle_request(request_type, payload)
    assert response["status"] == "success"
    assert response["message"] == "Echo request processed successfully."
    assert response["result"] == "Hello via handle_request"

@pytest.mark.asyncio
async def test_orchestrator_handle_request_echo_missing_payload(orchestrator_agent: OrchestratorAgent):
    """Test handle_request with echo type but missing input_text in payload."""
    request_type = "echo"
    payload = {}
    response = await orchestrator_agent.handle_request(request_type, payload)
    assert response["status"] == "error"
    assert response["message"] == "Missing 'input_text' in payload for echo request."
    assert response["result"] is None

@pytest.mark.asyncio
async def test_orchestrator_handle_request_unknown_type(orchestrator_agent: OrchestratorAgent):
    """Test handle_request with an unknown request_type."""
    request_type = "unknown_action"
    payload = {"data": "some_data"}
    response = await orchestrator_agent.handle_request(request_type, payload)
    assert response["status"] == "error"
    assert response["message"] == "Unknown request_type: unknown_action"
    assert response["result"] is None

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