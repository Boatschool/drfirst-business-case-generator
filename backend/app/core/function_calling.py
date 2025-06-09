"""
OpenAPI Function Calling Schema Generation for Agent Tools
Enables LLMs to directly invoke agent tools using structured function calling
"""

import json
from typing import Dict, Any, List, Type, get_type_hints, get_origin, get_args
from pydantic import BaseModel
from enum import Enum
import inspect

# Pydantic v2 compatibility
def model_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """Get model schema compatible with both Pydantic v1 and v2"""
    # For Pydantic v2 (which we have installed)
    if hasattr(model, 'model_json_schema'):
        return model.model_json_schema()
    # Fallback for Pydantic v1
    elif hasattr(model, 'schema'):
        return model.schema()
    else:
        raise ValueError(f"Unable to generate schema for model {model}")

from ..models.agent_models import (
    DraftPrdInput, DraftPrdOutput,
    GenerateSystemDesignInput, GenerateSystemDesignOutput,
    EstimateEffortInput, EstimateEffortOutput,
    EstimateCostInput, EstimateCostOutput,
    EstimateValueInput, EstimateValueOutput,
    GenerateFinancialModelInput, GenerateFinancialModelOutput
)


class AgentToolRegistry:
    """Registry for agent tools with OpenAPI schema generation"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default agent tools"""
        # Product Manager Agent Tools
        self.register_tool(
            name="draft_prd",
            description="Generate a comprehensive Product Requirements Document based on problem statement and business case details",
            input_schema=DraftPrdInput,
            output_schema=DraftPrdOutput,
            agent_class="ProductManagerAgent",
            method_name="draft_prd"
        )
        
        # Architect Agent Tools
        self.register_tool(
            name="generate_system_design",
            description="Create a detailed system architecture design based on an approved PRD",
            input_schema=GenerateSystemDesignInput,
            output_schema=GenerateSystemDesignOutput,
            agent_class="ArchitectAgent",
            method_name="generate_system_design"
        )
        
        # Planner Agent Tools
        self.register_tool(
            name="estimate_effort",
            description="Estimate development effort and timeline based on system design specifications",
            input_schema=EstimateEffortInput,
            output_schema=EstimateEffortOutput,
            agent_class="PlannerAgent",
            method_name="estimate_effort"
        )
        
        # Cost Analyst Agent Tools
        self.register_tool(
            name="estimate_costs",
            description="Calculate development and operational costs based on effort estimates",
            input_schema=EstimateCostInput,
            output_schema=EstimateCostOutput,
            agent_class="CostAnalystAgent",
            method_name="estimate_costs"
        )
        
        # Sales Value Analyst Agent Tools
        self.register_tool(
            name="estimate_value",
            description="Project business value, ROI, and revenue potential based on PRD analysis",
            input_schema=EstimateValueInput,
            output_schema=EstimateValueOutput,
            agent_class="SalesValueAnalystAgent", 
            method_name="analyze_value"
        )
        
        # Financial Model Agent Tools
        self.register_tool(
            name="generate_financial_model",
            description="Create comprehensive financial model combining costs and value projections",
            input_schema=GenerateFinancialModelInput,
            output_schema=GenerateFinancialModelOutput,
            agent_class="FinancialModelAgent",
            method_name="generate_financial_model"
        )
    
    def register_tool(
        self, 
        name: str, 
        description: str, 
        input_schema: Type[BaseModel],
        output_schema: Type[BaseModel],
        agent_class: str,
        method_name: str,
        tags: List[str] = None
    ):
        """Register a new agent tool"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "input_schema": input_schema,
            "output_schema": output_schema,
            "agent_class": agent_class,
            "method_name": method_name,
            "tags": tags or [],
            "openapi_function": self._generate_openapi_function(name, description, input_schema),
            "gemini_function": self._generate_gemini_function(name, description, input_schema),
            "anthropic_function": self._generate_anthropic_function(name, description, input_schema)
        }
    
    def _generate_openapi_function(self, name: str, description: str, input_schema: Type[BaseModel]) -> Dict[str, Any]:
        """Generate OpenAPI-compatible function definition"""
        schema = model_schema(input_schema)
        
        # Convert Pydantic schema to OpenAPI function calling format
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        if "properties" in schema:
            parameters["properties"] = schema["properties"]
            
        if "required" in schema:
            parameters["required"] = schema["required"]
            
        return {
            "name": name,
            "description": description,
            "parameters": parameters
        }
    
    def _generate_gemini_function(self, name: str, description: str, input_schema: Type[BaseModel]) -> Dict[str, Any]:
        """Generate Google Gemini function calling format"""
        schema = model_schema(input_schema)
        
        return {
            "name": name,
            "description": description,
            "parameters": {
                "type_": "OBJECT",
                "properties": self._convert_to_gemini_properties(schema.get("properties", {})),
                "required": schema.get("required", [])
            }
        }
    
    def _generate_anthropic_function(self, name: str, description: str, input_schema: Type[BaseModel]) -> Dict[str, Any]:
        """Generate Anthropic Claude function calling format"""
        schema = model_schema(input_schema)
        
        return {
            "name": name,
            "description": description,
            "input_schema": {
                "type": "object",
                "properties": schema.get("properties", {}),
                "required": schema.get("required", [])
            }
        }
    
    def _convert_to_gemini_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Convert OpenAPI properties to Gemini format"""
        gemini_props = {}
        
        for prop_name, prop_def in properties.items():
            prop_type = prop_def.get("type", "string")
            
            # Map types to Gemini format
            type_mapping = {
                "string": "STRING",
                "integer": "INTEGER", 
                "number": "NUMBER",
                "boolean": "BOOLEAN",
                "array": "ARRAY",
                "object": "OBJECT"
            }
            
            gemini_props[prop_name] = {
                "type_": type_mapping.get(prop_type, "STRING"),
                "description": prop_def.get("description", "")
            }
            
            # Handle arrays
            if prop_type == "array" and "items" in prop_def:
                items_type = prop_def["items"].get("type", "string")
                gemini_props[prop_name]["items"] = {
                    "type_": type_mapping.get(items_type, "STRING")
                }
        
        return gemini_props
    
    def get_tool(self, name: str) -> Dict[str, Any]:
        """Get tool definition by name"""
        return self.tools.get(name)
    
    def get_all_tools(self) -> Dict[str, Any]:
        """Get all registered tools"""
        return self.tools
    
    def get_openapi_functions(self) -> List[Dict[str, Any]]:
        """Get all tools in OpenAPI function calling format"""
        return [tool["openapi_function"] for tool in self.tools.values()]
    
    def get_gemini_functions(self) -> List[Dict[str, Any]]:
        """Get all tools in Gemini function calling format"""
        return [tool["gemini_function"] for tool in self.tools.values()]
    
    def get_anthropic_functions(self) -> List[Dict[str, Any]]:
        """Get all tools in Anthropic function calling format"""
        return [tool["anthropic_function"] for tool in self.tools.values()]
    
    def get_tools_by_agent(self, agent_class: str) -> List[Dict[str, Any]]:
        """Get tools for a specific agent class"""
        return [tool for tool in self.tools.values() if tool["agent_class"] == agent_class]
    
    def export_openapi_spec(self) -> Dict[str, Any]:
        """Export complete OpenAPI specification for all agent tools"""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "DrFirst Agent Tools API",
                "version": "1.0.0",
                "description": "Agent tool functions for LLM function calling"
            },
            "paths": {},
            "components": {
                "schemas": {},
                "functions": {}
            }
        }
        
        # Add function definitions
        for tool_name, tool in self.tools.items():
            spec["components"]["functions"][tool_name] = tool["openapi_function"]
            
            # Add schema definitions
            input_schema = model_schema(tool["input_schema"])
            output_schema = model_schema(tool["output_schema"])
            
            spec["components"]["schemas"][f"{tool_name}_input"] = input_schema
            spec["components"]["schemas"][f"{tool_name}_output"] = output_schema
        
        return spec
    
    def validate_function_call(self, function_name: str, arguments: Dict[str, Any]) -> tuple[bool, str]:
        """Validate a function call against the registered schema"""
        tool = self.get_tool(function_name)
        if not tool:
            return False, f"Unknown function: {function_name}"
        
        try:
            # Validate using Pydantic model
            tool["input_schema"](**arguments)
            return True, "Valid"
        except Exception as e:
            return False, f"Validation error: {str(e)}"


class LLMFunctionCaller:
    """Handles execution of LLM function calls on agent tools"""
    
    def __init__(self, agent_registry: 'AgentRegistry' = None):
        self.tool_registry = AgentToolRegistry()
        self.agent_registry = agent_registry
    
    async def execute_function_call(
        self, 
        function_name: str, 
        arguments: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a function call from an LLM"""
        
        # Validate function call
        is_valid, validation_message = self.tool_registry.validate_function_call(function_name, arguments)
        if not is_valid:
            return {
                "success": False,
                "error": validation_message,
                "function_name": function_name
            }
        
        # Get tool definition
        tool = self.tool_registry.get_tool(function_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool not found: {function_name}",
                "function_name": function_name
            }
        
        try:
            # Get agent instance
            if not self.agent_registry:
                return {
                    "success": False,
                    "error": "Agent registry not configured",
                    "function_name": function_name
                }
            
            agent = self.agent_registry.get_agent(tool["agent_class"])
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent not found: {tool['agent_class']}",
                    "function_name": function_name
                }
            
            # Create input object
            input_obj = tool["input_schema"](**arguments)
            
            # Execute agent method
            method = getattr(agent, tool["method_name"])
            result = await method(input_obj)
            
            return {
                "success": True,
                "result": result.dict() if hasattr(result, 'dict') else result,
                "function_name": function_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "function_name": function_name
            }


# Global registry instance
tool_registry = AgentToolRegistry() 