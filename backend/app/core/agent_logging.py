"""
Enhanced Agent Interaction Logging Module

This module provides specialized logging capabilities for AI agents, designed to support
evaluation systems with structured logging of:
- Agent inputs and outputs
- LLM prompts and responses 
- Performance metrics
- Error handling

All logs are structured for Google Cloud Logging and queryable for evaluation purposes.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager

from .logging_config import get_contextual_logger, log_error_with_context, log_performance_metric


class AgentInteractionLogger:
    """
    Enhanced logger for AI agent interactions that provides structured logging
    for evaluation and monitoring purposes.
    """
    
    def __init__(self, agent_name: str, case_id: Optional[str] = None):
        """
        Initialize the agent interaction logger.
        
        Args:
            agent_name: Name of the agent (e.g., "ProductManagerAgent")
            case_id: Business case ID being processed
        """
        self.agent_name = agent_name
        self.case_id = case_id
        self.base_logger = logging.getLogger(f"app.agents.{agent_name.lower()}")
        
        # Create contextual logger with agent information
        context = {
            'agent_name': agent_name,
            'component': 'agent_interaction'
        }
        if case_id:
            context['case_id'] = case_id
            
        self.logger = get_contextual_logger(self.base_logger.name, context)
    
    def log_method_start(
        self, 
        method_name: str, 
        input_payload: Dict[str, Any],
        trace_id: Optional[str] = None,
        **additional_context
    ) -> str:
        """
        Log the start of an agent method execution.
        
        Args:
            method_name: Name of the agent method being called
            input_payload: JSON-serializable input data
            trace_id: Optional trace ID (will generate if not provided)
            **additional_context: Additional context fields
            
        Returns:
            str: Generated or provided trace_id
        """
        if not trace_id:
            trace_id = str(uuid.uuid4())
        
        log_data = {
            'trace_id': trace_id,
            'method_name': method_name,
            'timestamp_start': datetime.utcnow().isoformat(),
            'input_payload': self._sanitize_payload(input_payload),
            'log_type': 'agent_method_start',
            **additional_context
        }
        
        self.logger.info(
            f"Agent method {method_name} started",
            extra=log_data
        )
        
        return trace_id
    
    def log_method_end(
        self,
        trace_id: str,
        method_name: str,
        output_payload: Dict[str, Any],
        execution_time_ms: float,
        status: str = "SUCCESS",
        error_message: Optional[str] = None,
        **additional_context
    ) -> None:
        """
        Log the completion of an agent method execution.
        
        Args:
            trace_id: Trace ID from method start
            method_name: Name of the agent method
            output_payload: JSON-serializable output data
            execution_time_ms: Method execution time in milliseconds
            status: "SUCCESS" or "ERROR"
            error_message: Error message if status is "ERROR"
            **additional_context: Additional context fields
        """
        log_data = {
            'trace_id': trace_id,
            'method_name': method_name,
            'timestamp_end': datetime.utcnow().isoformat(),
            'agent_output_payload': self._sanitize_payload(output_payload),
            'execution_time_ms': execution_time_ms,
            'status': status,
            'log_type': 'agent_method_end',
            **additional_context
        }
        
        if error_message:
            log_data['error_message'] = error_message
        
        log_level = logging.INFO if status == "SUCCESS" else logging.ERROR
        self.logger.log(
            log_level,
            f"Agent method {method_name} completed with status {status}",
            extra=log_data
        )
    
    def log_llm_call(
        self,
        trace_id: str,
        model_name: str,
        prompt: str,
        parameters: Dict[str, Any],
        response: Optional[str] = None,
        response_time_ms: Optional[float] = None,
        error: Optional[str] = None,
        **additional_context
    ) -> None:
        """
        Log an LLM interaction within an agent method.
        
        Args:
            trace_id: Trace ID from parent method
            model_name: Name of the LLM model used
            prompt: Full prompt sent to the LLM
            parameters: LLM parameters (temperature, max_tokens, etc.)
            response: Raw response from the LLM
            response_time_ms: LLM response time in milliseconds
            error: Error message if LLM call failed
            **additional_context: Additional context fields
        """
        log_data = {
            'trace_id': trace_id,
            'llm_model_name': model_name,
            'llm_prompt': self._sanitize_prompt(prompt),
            'llm_parameters': parameters,
            'log_type': 'llm_interaction',
            **additional_context
        }
        
        if response is not None:
            log_data['llm_raw_response'] = self._sanitize_response(response)
        
        if response_time_ms is not None:
            log_data['llm_response_time_ms'] = response_time_ms
        
        if error:
            log_data['llm_error'] = error
            log_level = logging.ERROR
            message = f"LLM call to {model_name} failed"
        else:
            log_level = logging.INFO
            message = f"LLM call to {model_name} completed"
        
        self.logger.log(log_level, message, extra=log_data)
    
    @contextmanager
    def log_method_execution(
        self,
        method_name: str,
        input_payload: Dict[str, Any],
        trace_id: Optional[str] = None,
        **additional_context
    ):
        """
        Context manager for logging method execution with automatic timing.
        
        Args:
            method_name: Name of the agent method
            input_payload: Method input data
            trace_id: Optional trace ID
            **additional_context: Additional context fields
            
        Yields:
            dict: Contains 'trace_id' and 'log_llm' function for LLM logging
            
        Example:
            with logger.log_method_execution('draft_prd', input_data) as ctx:
                # ... method logic ...
                ctx['log_llm'](model_name, prompt, params, response)
                # ... more logic ...
                return output_data
        """
        start_time = time.time()
        trace_id = self.log_method_start(method_name, input_payload, trace_id, **additional_context)
        
        # Create LLM logging function bound to this trace
        def log_llm(model_name: str, prompt: str, parameters: Dict[str, Any], 
                   response: Optional[str] = None, response_time_ms: Optional[float] = None,
                   error: Optional[str] = None, **llm_context):
            self.log_llm_call(trace_id, model_name, prompt, parameters, response, 
                            response_time_ms, error, **llm_context)
        
        context = {
            'trace_id': trace_id,
            'log_llm': log_llm
        }
        
        try:
            yield context
            # Success case will be logged by the caller using log_method_end
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            self.log_method_end(
                trace_id, method_name, {}, execution_time_ms,
                status="ERROR", error_message=str(e), **additional_context
            )
            raise
    
    def _sanitize_payload(self, payload: Any) -> Any:
        """
        Sanitize payload data for logging, handling large objects and sensitive data.
        
        Args:
            payload: The payload to sanitize
            
        Returns:
            Sanitized payload safe for logging
        """
        if isinstance(payload, dict):
            sanitized = {}
            for key, value in payload.items():
                if key.lower() in ['password', 'token', 'secret', 'key', 'credential']:
                    sanitized[key] = "[REDACTED]"
                elif isinstance(value, str) and len(value) > 10000:
                    sanitized[key] = f"[TRUNCATED: {len(value)} chars]"
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self._sanitize_payload(value)
                else:
                    sanitized[key] = value
            return sanitized
        elif isinstance(payload, list):
            return [self._sanitize_payload(item) for item in payload[:100]]  # Limit list size
        elif isinstance(payload, str) and len(payload) > 10000:
            return f"[TRUNCATED: {len(payload)} chars] {payload[:1000]}..."
        else:
            return payload
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """
        Sanitize LLM prompt for logging.
        
        Args:
            prompt: The prompt to sanitize
            
        Returns:
            Sanitized prompt safe for logging
        """
        if len(prompt) > 15000:
            return f"[PROMPT TRUNCATED: {len(prompt)} chars] {prompt[:5000]}..."
        return prompt
    
    def _sanitize_response(self, response: str) -> str:
        """
        Sanitize LLM response for logging.
        
        Args:
            response: The response to sanitize
            
        Returns:
            Sanitized response safe for logging
        """
        if len(response) > 20000:
            return f"[RESPONSE TRUNCATED: {len(response)} chars] {response[:10000]}..."
        return response


def create_agent_logger(agent_name: str, case_id: Optional[str] = None) -> AgentInteractionLogger:
    """
    Factory function to create an agent interaction logger.
    
    Args:
        agent_name: Name of the agent
        case_id: Optional case ID
        
    Returns:
        AgentInteractionLogger instance
    """
    return AgentInteractionLogger(agent_name, case_id)


def log_agent_error(
    logger: logging.Logger,
    agent_name: str,
    method_name: str,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None
) -> None:
    """
    Log an agent error with full context.
    
    Args:
        logger: Logger instance
        agent_name: Name of the agent
        method_name: Method where error occurred
        error: Exception that occurred
        context: Additional context
        trace_id: Optional trace ID
    """
    error_context = context or {}
    error_context.update({
        'agent_name': agent_name,
        'method_name': method_name,
        'log_type': 'agent_error'
    })
    
    if trace_id:
        error_context['trace_id'] = trace_id
    
    log_error_with_context(
        logger,
        f"Agent {agent_name}.{method_name} encountered an error",
        error,
        error_context
    )


def log_agent_performance(
    logger: logging.Logger,
    agent_name: str,
    method_name: str,
    duration_ms: float,
    success: bool,
    context: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None
) -> None:
    """
    Log agent performance metrics.
    
    Args:
        logger: Logger instance
        agent_name: Name of the agent
        method_name: Method being measured
        duration_ms: Duration in milliseconds
        success: Whether operation succeeded
        context: Additional context
        trace_id: Optional trace ID
    """
    perf_context = context or {}
    perf_context.update({
        'agent_name': agent_name,
        'method_name': method_name
    })
    
    if trace_id:
        perf_context['trace_id'] = trace_id
    
    operation_name = f"{agent_name}.{method_name}"
    log_performance_metric(logger, operation_name, duration_ms, success, perf_context) 