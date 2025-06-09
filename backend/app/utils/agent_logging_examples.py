"""
Agent Logging Examples

This module demonstrates how to use the enhanced agent logging system
for AI agents in the DrFirst Business Case Generator.
"""

import asyncio
import logging
import time
from typing import Dict, Any

from ..core.agent_logging import create_agent_logger


async def example_agent_method_with_llm():
    """
    Example showing how to use the enhanced agent logging in an agent method
    that makes LLM calls.
    """
    # Create agent logger
    agent_logger = create_agent_logger("ExampleAgent", "case-123")
    
    # Example input data
    input_payload = {
        "user_query": "Generate a business case for AI chatbot",
        "complexity": "medium",
        "target_audience": "healthcare professionals"
    }
    
    # Use context manager for comprehensive logging
    with agent_logger.log_method_execution('generate_business_case', input_payload) as ctx:
        trace_id = ctx['trace_id']
        log_llm_call = ctx['log_llm']
        
        # Simulate some processing
        await asyncio.sleep(0.1)
        
        # Simulate LLM call
        llm_start_time = time.time()
        
        # Mock LLM parameters
        llm_params = {
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9
        }
        
        # Mock prompt
        prompt = "Generate a comprehensive business case for implementing an AI chatbot..."
        
        # Simulate LLM processing time
        await asyncio.sleep(0.5)
        
        # Mock response
        mock_response = "# Business Case for AI Chatbot\n\n## Executive Summary\n..."
        
        llm_response_time_ms = (time.time() - llm_start_time) * 1000
        
        # Log the LLM interaction
        log_llm_call(
            model_name="gemini-1.0-pro",
            prompt=prompt,
            parameters=llm_params,
            response=mock_response,
            response_time_ms=llm_response_time_ms
        )
        
        # Prepare output payload
        output_payload = {
            "status": "SUCCESS",
            "response_length": len(mock_response),
            "model_used": "gemini-1.0-pro",
            "processing_time_ms": llm_response_time_ms
        }
        
        # Calculate total execution time
        total_execution_time_ms = (time.time() - llm_start_time + 0.1) * 1000
        
        # Log method completion
        agent_logger.log_method_end(
            trace_id=trace_id,
            method_name='generate_business_case',
            output_payload=output_payload,
            execution_time_ms=total_execution_time_ms,
            status="SUCCESS"
        )
        
        return {
            "status": "success",
            "content": mock_response,
            "trace_id": trace_id
        }


async def example_agent_method_with_error():
    """
    Example showing how error handling works with the enhanced logging.
    """
    agent_logger = create_agent_logger("ExampleAgent", "case-456")
    
    input_payload = {
        "invalid_input": "This will cause an error"
    }
    
    # The context manager will automatically handle error logging
    with agent_logger.log_method_execution('process_invalid_data', input_payload) as ctx:
        trace_id = ctx['trace_id']
        log_llm_call = ctx['log_llm']
        
        # Simulate an error
        raise ValueError("Invalid input data provided")


async def example_multiple_llm_calls():
    """
    Example showing how to log multiple LLM calls within a single method.
    """
    agent_logger = create_agent_logger("MultiStepAgent", "case-789")
    
    input_payload = {
        "step_count": 3,
        "process_type": "multi_step_analysis"
    }
    
    with agent_logger.log_method_execution('multi_step_analysis', input_payload) as ctx:
        trace_id = ctx['trace_id']
        log_llm_call = ctx['log_llm']
        
        results = []
        
        # Step 1: Analysis
        llm_start_time = time.time()
        await asyncio.sleep(0.2)
        
        log_llm_call(
            model_name="gemini-1.0-pro",
            prompt="Analyze the business requirements...",
            parameters={"temperature": 0.3, "max_tokens": 1000},
            response="Analysis complete: Requirements are well-defined...",
            response_time_ms=(time.time() - llm_start_time) * 1000
        )
        
        results.append("analysis_complete")
        
        # Step 2: Design
        llm_start_time = time.time()
        await asyncio.sleep(0.3)
        
        log_llm_call(
            model_name="gemini-1.0-pro",
            prompt="Design the system architecture...",
            parameters={"temperature": 0.2, "max_tokens": 1500},
            response="System design: Microservices architecture recommended...",
            response_time_ms=(time.time() - llm_start_time) * 1000
        )
        
        results.append("design_complete")
        
        # Step 3: Cost estimation
        llm_start_time = time.time()
        await asyncio.sleep(0.1)
        
        log_llm_call(
            model_name="gemini-1.0-pro",
            prompt="Estimate implementation costs...",
            parameters={"temperature": 0.1, "max_tokens": 800},
            response="Cost estimate: $150,000 - $200,000 for full implementation...",
            response_time_ms=(time.time() - llm_start_time) * 1000
        )
        
        results.append("cost_estimation_complete")
        
        # Final output
        output_payload = {
            "status": "SUCCESS",
            "steps_completed": len(results),
            "results": results
        }
        
        total_execution_time_ms = 600  # Approximate total time
        
        agent_logger.log_method_end(
            trace_id=trace_id,
            method_name='multi_step_analysis',
            output_payload=output_payload,
            execution_time_ms=total_execution_time_ms,
            status="SUCCESS"
        )
        
        return {
            "status": "success",
            "results": results,
            "trace_id": trace_id
        }


async def run_examples():
    """
    Run all the logging examples.
    """
    print("Running Agent Logging Examples...")
    
    # Example 1: Successful method with LLM call
    print("\n1. Example: Successful method with LLM call")
    try:
        result1 = await example_agent_method_with_llm()
        print(f"✓ Success: {result1['status']}, Trace ID: {result1['trace_id']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 2: Method with error (demonstrates error logging)
    print("\n2. Example: Method with error handling")
    try:
        result2 = await example_agent_method_with_error()
        print(f"✓ Success: {result2}")
    except Exception as e:
        print(f"✓ Expected error caught: {e}")
    
    # Example 3: Multiple LLM calls
    print("\n3. Example: Multiple LLM calls in one method")
    try:
        result3 = await example_multiple_llm_calls()
        print(f"✓ Success: {result3['status']}, Steps: {len(result3['results'])}, Trace ID: {result3['trace_id']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\nAll examples completed!")


if __name__ == "__main__":
    # Set up basic logging to see the output
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the examples
    asyncio.run(run_examples()) 