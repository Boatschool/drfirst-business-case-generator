"""
API routes for LLM function calling capabilities
Provides endpoints for schema discovery and function execution
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import logging

from ...core.function_calling import tool_registry, LLMFunctionCaller
from ...core.agent_registry import get_agent_registry
from ...auth.firebase_auth import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/function-calling", tags=["function-calling"])


# ===== REQUEST/RESPONSE MODELS =====

class FunctionCallRequest(BaseModel):
    """Request model for executing a function call"""
    function_name: str = Field(..., description="Name of the function to call")
    arguments: Dict[str, Any] = Field(..., description="Function arguments")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class FunctionCallResponse(BaseModel):
    """Response model for function call execution"""
    success: bool = Field(..., description="Whether the function call succeeded")
    result: Any = Field(None, description="Function call result")
    error: str = Field(None, description="Error message if failed")
    function_name: str = Field(..., description="Name of the called function")
    execution_time_ms: int = Field(None, description="Execution time in milliseconds")


class ToolDiscoveryResponse(BaseModel):
    """Response model for tool discovery"""
    tools: List[Dict[str, Any]] = Field(..., description="Available tools")
    total_count: int = Field(..., description="Total number of tools")
    format: str = Field(..., description="Schema format (openapi, gemini, anthropic)")


class OpenAPISpecResponse(BaseModel):
    """Response model for OpenAPI specification"""
    spec: Dict[str, Any] = Field(..., description="Complete OpenAPI specification")
    version: str = Field(..., description="OpenAPI version")
    tool_count: int = Field(..., description="Number of tools defined")


# ===== DISCOVERY ENDPOINTS =====

@router.get(
    "/tools/openapi",
    response_model=ToolDiscoveryResponse,
    summary="Get tools in OpenAPI function calling format"
)
async def get_openapi_tools():
    """Get all agent tools in OpenAPI function calling format"""
    try:
        tools = tool_registry.get_openapi_functions()
        return ToolDiscoveryResponse(
            tools=tools,
            total_count=len(tools),
            format="openapi"
        )
    except Exception as e:
        logger.error(f"Error getting OpenAPI tools: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving tools: {str(e)}")


@router.get(
    "/tools/gemini",
    response_model=ToolDiscoveryResponse,
    summary="Get tools in Google Gemini function calling format"
)
async def get_gemini_tools():
    """Get all agent tools in Google Gemini function calling format"""
    try:
        tools = tool_registry.get_gemini_functions()
        return ToolDiscoveryResponse(
            tools=tools,
            total_count=len(tools),
            format="gemini"
        )
    except Exception as e:
        logger.error(f"Error getting Gemini tools: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving tools: {str(e)}")


@router.get(
    "/tools/anthropic", 
    response_model=ToolDiscoveryResponse,
    summary="Get tools in Anthropic Claude function calling format"
)
async def get_anthropic_tools():
    """Get all agent tools in Anthropic Claude function calling format"""
    try:
        tools = tool_registry.get_anthropic_functions()
        return ToolDiscoveryResponse(
            tools=tools,
            total_count=len(tools),
            format="anthropic"
        )
    except Exception as e:
        logger.error(f"Error getting Anthropic tools: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving tools: {str(e)}")


@router.get(
    "/openapi-spec",
    response_model=OpenAPISpecResponse,
    summary="Get complete OpenAPI specification for all agent tools"
)
async def get_openapi_specification():
    """Get complete OpenAPI specification for all agent tools"""
    try:
        spec = tool_registry.export_openapi_spec()
        tool_count = len(spec.get("components", {}).get("functions", {}))
        
        return OpenAPISpecResponse(
            spec=spec,
            version=spec.get("openapi", "3.0.0"),
            tool_count=tool_count
        )
    except Exception as e:
        logger.error(f"Error generating OpenAPI spec: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating specification: {str(e)}")


# ===== FUNCTION EXECUTION ENDPOINTS =====

@router.post(
    "/execute",
    response_model=FunctionCallResponse,
    summary="Execute a function call from an LLM"
)
async def execute_function_call(
    request: FunctionCallRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Execute a function call from an LLM with authentication"""
    import time
    
    start_time = time.time()
    
    try:
        # Get agent registry
        agent_registry = get_agent_registry()
        
        # Create function caller with agent registry
        function_caller = LLMFunctionCaller(agent_registry=agent_registry)
        
        # Add user context
        context = request.context.copy()
        context["user_id"] = current_user.get("uid")
        context["user_email"] = current_user.get("email")
        
        # Execute function call
        result = await function_caller.execute_function_call(
            function_name=request.function_name,
            arguments=request.arguments,
            context=context
        )
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        return FunctionCallResponse(
            success=result["success"],
            result=result.get("result"),
            error=result.get("error"),
            function_name=request.function_name,
            execution_time_ms=execution_time_ms
        )
        
    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Error executing function call {request.function_name}: {str(e)}")
        
        return FunctionCallResponse(
            success=False,
            result=None,
            error=f"Execution error: {str(e)}",
            function_name=request.function_name,
            execution_time_ms=execution_time_ms
        )


@router.post(
    "/validate",
    summary="Validate a function call without executing it"
)
async def validate_function_call(request: FunctionCallRequest):
    """Validate a function call without executing it"""
    try:
        is_valid, message = tool_registry.validate_function_call(
            request.function_name,
            request.arguments
        )
        
        return {
            "valid": is_valid,
            "message": message,
            "function_name": request.function_name
        }
        
    except Exception as e:
        logger.error(f"Error validating function call {request.function_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


# ===== TOOL INFORMATION ENDPOINTS =====

@router.get(
    "/tools/{tool_name}",
    summary="Get detailed information about a specific tool"
)
async def get_tool_info(tool_name: str):
    """Get detailed information about a specific tool"""
    try:
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
        
        # Remove the actual schema classes from response (not JSON serializable)
        response_tool = tool.copy()
        response_tool.pop("input_schema", None)
        response_tool.pop("output_schema", None)
        
        return response_tool
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool info for {tool_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving tool info: {str(e)}")


@router.get(
    "/agents/{agent_class}/tools",
    summary="Get all tools for a specific agent"
)
async def get_agent_tools(agent_class: str):
    """Get all tools available for a specific agent"""
    try:
        tools = tool_registry.get_tools_by_agent(agent_class)
        if not tools:
            raise HTTPException(status_code=404, detail=f"No tools found for agent: {agent_class}")
        
        # Remove schema classes from response
        response_tools = []
        for tool in tools:
            response_tool = tool.copy()
            response_tool.pop("input_schema", None)
            response_tool.pop("output_schema", None)
            response_tools.append(response_tool)
        
        return {
            "agent_class": agent_class,
            "tools": response_tools,
            "tool_count": len(response_tools)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tools for agent {agent_class}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving agent tools: {str(e)}")


# ===== AGENT STATUS ENDPOINTS =====

@router.get(
    "/agents/status",
    summary="Get status of all agents"
)
async def get_agent_statuses():
    """Get status information for all agents"""
    try:
        agent_registry = get_agent_registry()
        statuses = agent_registry.get_all_agent_statuses()
        
        return {
            "agents": statuses,
            "total_agents": len(statuses),
            "available_agents": len([s for s in statuses.values() if s.get("available", False)])
        }
        
    except Exception as e:
        logger.error(f"Error getting agent statuses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving agent statuses: {str(e)}")


@router.get(
    "/agents/{agent_class}/status",
    summary="Get status of a specific agent"
)
async def get_agent_status(agent_class: str):
    """Get status information for a specific agent"""
    try:
        agent_registry = get_agent_registry()
        status = agent_registry.get_agent_status(agent_class)
        
        if status.get("status") == "not_found":
            raise HTTPException(status_code=404, detail=f"Agent not found: {agent_class}")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status for agent {agent_class}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving agent status: {str(e)}") 