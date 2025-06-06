"""
Example file demonstrating the enhanced logging capabilities for the DrFirst Business Case Generator.

This file shows best practices for using the structured logging system in different scenarios:
- API request logging
- Business case operations
- Agent operations
- Error handling with context
- Performance metrics

This file can be used for testing and as a reference for other developers.
"""

import logging
from datetime import datetime
import time
from typing import Dict, Any

from app.core.logging_config import (
    get_contextual_logger,
    log_api_request,
    log_business_case_operation,
    log_agent_operation,
    log_error_with_context,
    log_performance_metric,
    log_function_entry_exit
)

# Get base logger for this module
logger = logging.getLogger(__name__)


def demonstrate_basic_logging():
    """Demonstrate basic structured logging with context"""
    logger.info("Starting logging demonstration")
    
    # Basic contextual logging
    contextual_logger = get_contextual_logger(__name__, {
        'demo_session': 'basic_logging',
        'timestamp': datetime.now().isoformat()
    })
    
    contextual_logger.info(
        "This is a contextual log message",
        extra={
            'level': 'info',
            'message_type': 'demonstration'
        }
    )
    
    contextual_logger.warning(
        "This is a warning with additional context",
        extra={
            'warning_type': 'demonstration',
            'severity': 'low'
        }
    )


def demonstrate_api_request_logging():
    """Demonstrate API request logging patterns"""
    logger.info("Demonstrating API request logging")
    
    # Simulate an API request
    request_id = "req_12345"
    user_id = "user_67890"
    endpoint = "/api/v1/cases"
    method = "GET"
    
    # Create request logger
    request_logger = log_api_request(logger, request_id, user_id, endpoint, method)
    
    request_logger.info("Processing API request")
    
    # Simulate request processing
    request_logger.debug(
        "Validating request parameters",
        extra={'param_count': 3}
    )
    
    request_logger.info(
        "Request processed successfully",
        extra={
            'response_size': 1024,
            'processing_time_ms': 150
        }
    )


def demonstrate_business_case_logging():
    """Demonstrate business case operation logging"""
    logger.info("Demonstrating business case logging")
    
    case_id = "case_abc123"
    user_id = "user_67890"
    operation = "create_case"
    
    # Create business case logger
    case_logger = log_business_case_operation(logger, case_id, user_id, operation)
    
    case_logger.info("Starting business case creation")
    
    case_logger.info(
        "Business case data validated",
        extra={
            'title_length': 45,
            'problem_statement_length': 250,
            'links_count': 2
        }
    )
    
    case_logger.info(
        "Business case created successfully",
        extra={
            'status': 'INTAKE',
            'created_at': datetime.now().isoformat()
        }
    )


def demonstrate_agent_logging():
    """Demonstrate agent operation logging"""
    logger.info("Demonstrating agent logging")
    
    agent_name = "ProductManagerAgent"
    case_id = "case_abc123"
    operation = "draft_prd"
    
    # Create agent logger
    agent_logger = log_agent_operation(logger, agent_name, case_id, operation)
    
    agent_logger.info("Agent processing started")
    
    agent_logger.debug(
        "Analyzing requirements",
        extra={
            'requirement_count': 5,
            'complexity_score': 7.5
        }
    )
    
    agent_logger.info(
        "PRD draft completed",
        extra={
            'draft_length': 2500,
            'sections_count': 8,
            'processing_time_seconds': 45
        }
    )


def demonstrate_error_logging():
    """Demonstrate error logging with context"""
    logger.info("Demonstrating error logging")
    
    case_id = "case_error123"
    user_id = "user_67890"
    
    case_logger = log_business_case_operation(logger, case_id, user_id, "error_demo")
    
    try:
        # Simulate an error
        raise ValueError("Simulated validation error")
    except ValueError as e:
        log_error_with_context(
            case_logger,
            "Business case validation failed",
            e,
            {
                'validation_step': 'requirements_check',
                'input_data_size': 1024,
                'user_role': 'developer'
            }
        )
    
    try:
        # Simulate another error
        raise ConnectionError("Database connection failed")
    except ConnectionError as e:
        log_error_with_context(
            case_logger,
            "Database operation failed",
            e,
            {
                'operation': 'save_case',
                'retry_count': 3,
                'last_success': '2024-01-15T10:30:00Z'
            }
        )


def demonstrate_performance_logging():
    """Demonstrate performance metric logging"""
    logger.info("Demonstrating performance logging")
    
    # Simulate some operations with timing
    operations = [
        {"name": "database_query", "duration": 125.5, "success": True},
        {"name": "ai_processing", "duration": 2500.0, "success": True},
        {"name": "file_upload", "duration": 890.0, "success": False},
    ]
    
    for op in operations:
        log_performance_metric(
            logger,
            op["name"],
            op["duration"],
            op["success"],
            {
                'environment': 'development',
                'service': 'business_case_generator'
            }
        )


@log_function_entry_exit(logger)
def demonstrate_function_tracing():
    """Demonstrate function entry/exit logging (useful for DEBUG level)"""
    logger.debug("Inside function - this should show entry/exit logs at DEBUG level")
    
    # Simulate some work
    time.sleep(0.1)
    
    return "function_result"


def demonstrate_complex_scenario():
    """Demonstrate a complex scenario combining multiple logging patterns"""
    logger.info("Demonstrating complex logging scenario")
    
    # Simulate a complete business case workflow
    request_id = "req_complex_001"
    user_id = "user_12345"
    case_id = "case_complex_001"
    
    # 1. API Request starts
    request_logger = log_api_request(
        logger, request_id, user_id, "/api/v1/cases", "POST"
    )
    request_logger.info("Business case creation request received")
    
    # 2. Business case operation starts
    case_logger = log_business_case_operation(
        logger, case_id, user_id, "create_and_process"
    )
    
    start_time = time.time()
    
    try:
        case_logger.info("Creating business case")
        
        # 3. Agent processing
        agent_logger = log_agent_operation(
            logger, "OrchestratorAgent", case_id, "coordinate_creation"
        )
        agent_logger.info("Orchestrating business case creation")
        
        # Simulate processing steps
        steps = [
            {"name": "validate_input", "duration": 50},
            {"name": "store_case", "duration": 125},
            {"name": "trigger_prd", "duration": 2000},
        ]
        
        for step in steps:
            step_start = time.time()
            time.sleep(step["duration"] / 1000)  # Convert to seconds
            step_duration = (time.time() - step_start) * 1000
            
            log_performance_metric(
                agent_logger,
                step["name"],
                step_duration,
                True,
                {"case_id": case_id, "step_order": steps.index(step) + 1}
            )
        
        total_duration = (time.time() - start_time) * 1000
        
        case_logger.info(
            "Business case creation completed successfully",
            extra={
                'total_processing_time_ms': total_duration,
                'steps_completed': len(steps)
            }
        )
        
        request_logger.info(
            "API request completed successfully",
            extra={
                'case_id': case_id,
                'response_code': 201
            }
        )
        
    except Exception as e:
        log_error_with_context(
            case_logger,
            "Business case creation failed",
            e,
            {
                'request_id': request_id,
                'processing_step': 'unknown',
                'total_time_before_failure_ms': (time.time() - start_time) * 1000
            }
        )


def run_all_demonstrations():
    """Run all logging demonstrations"""
    logger.info("=" * 60)
    logger.info("STARTING LOGGING DEMONSTRATIONS")
    logger.info("=" * 60)
    
    demonstrations = [
        demonstrate_basic_logging,
        demonstrate_api_request_logging,
        demonstrate_business_case_logging,
        demonstrate_agent_logging,
        demonstrate_error_logging,
        demonstrate_performance_logging,
        demonstrate_function_tracing,
        demonstrate_complex_scenario,
    ]
    
    for demo in demonstrations:
        logger.info(f"Running demonstration: {demo.__name__}")
        try:
            demo()
        except Exception as e:
            logger.error(f"Demonstration {demo.__name__} failed: {e}")
        logger.info("-" * 40)
    
    logger.info("=" * 60)
    logger.info("LOGGING DEMONSTRATIONS COMPLETED")
    logger.info("=" * 60)


if __name__ == "__main__":
    # This can be run directly for testing
    run_all_demonstrations() 