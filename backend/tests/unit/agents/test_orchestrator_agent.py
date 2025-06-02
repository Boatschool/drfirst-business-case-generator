import pytest
import asyncio
from backend.app.agents.orchestrator_agent import OrchestratorAgent, EchoTool

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