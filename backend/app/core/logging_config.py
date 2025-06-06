"""
Logging configuration for the DrFirst Business Case Generator Backend.

This module provides structured logging configuration with:
- JSON logging for production/staging environments (Cloud Run friendly)
- Human-readable logging for development
- Contextual logging utilities for case_id, user_id, etc.
- Proper log level configuration based on environment variables
"""

import logging
import logging.config
import sys
from typing import Any, Dict, Optional

try:
    from pythonjsonlogger import jsonlogger
    HAS_JSON_LOGGER = True
except ImportError:
    HAS_JSON_LOGGER = False

from .config import settings


class ContextualLoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds contextual information to log records.
    Useful for adding case_id, user_id, request_id, etc. to log messages.
    """
    
    def __init__(self, logger: logging.Logger, context: Optional[Dict[str, Any]] = None):
        super().__init__(logger, context or {})
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process the logging record to add contextual information.
        
        Args:
            msg: The log message
            kwargs: Additional keyword arguments
            
        Returns:
            Tuple of (msg, kwargs) with context added to extra
        """
        # Merge context into the 'extra' field for structured logging
        extra = kwargs.setdefault('extra', {})
        
        # Add our adapter's context to extra
        for key, value in self.extra.items():
            if key not in extra:  # Don't override existing extra values
                extra[key] = value
        
        return msg, kwargs


def setup_logging() -> None:
    """
    Configure logging for the application based on environment.
    
    - Production/Staging: JSON structured logging to stdout
    - Development: Human-readable logging to stdout
    - Configurable log level via LOG_LEVEL environment variable
    """
    
    # Determine if we should use JSON logging
    use_json_logging = (
        HAS_JSON_LOGGER and 
        settings.environment.lower() in ['production', 'staging']
    )
    
    # Get log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Create formatter based on environment
    if use_json_logging:
        # JSON formatter for production/staging
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Human-readable formatter for development
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Configure handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers to avoid duplication
    for existing_handler in root_logger.handlers[:]:
        root_logger.removeHandler(existing_handler)
    
    root_logger.addHandler(handler)
    
    # Set specific log levels for third-party libraries to reduce noise
    logging.getLogger('google.cloud').setLevel(logging.WARNING)
    logging.getLogger('firebase_admin').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    # Log the logging configuration
    app_logger = logging.getLogger('app.core.logging_config')
    app_logger.info(
        "Logging configuration complete",
        extra={
            'environment': settings.environment,
            'log_level': settings.log_level,
            'json_logging': use_json_logging,
            'has_json_logger': HAS_JSON_LOGGER
        }
    )


def get_contextual_logger(name: str, context: Optional[Dict[str, Any]] = None) -> ContextualLoggerAdapter:
    """
    Get a logger with contextual information pre-configured.
    
    Args:
        name: Logger name (typically __name__)
        context: Initial context to add to all log messages
        
    Returns:
        ContextualLoggerAdapter instance
        
    Example:
        logger = get_contextual_logger(__name__, {'case_id': 'case-123'})
        logger.info("Processing case", extra={'step': 'validation'})
        # Results in log with case_id='case-123' and step='validation'
    """
    base_logger = logging.getLogger(name)
    return ContextualLoggerAdapter(base_logger, context)


def log_function_entry_exit(logger: logging.Logger):
    """
    Decorator to log function entry and exit at DEBUG level.
    Useful for tracing execution flow during development.
    
    Args:
        logger: Logger instance to use
        
    Returns:
        Decorator function
        
    Example:
        logger = logging.getLogger(__name__)
        
        @log_function_entry_exit(logger)
        async def my_function(param1, param2):
            # function body
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Entering {func.__name__}", extra={
                'function': func.__name__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            })
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Exiting {func.__name__}", extra={
                    'function': func.__name__,
                    'success': True
                })
                return result
            except Exception as e:
                logger.debug(f"Exiting {func.__name__} with exception", extra={
                    'function': func.__name__,
                    'success': False,
                    'exception_type': type(e).__name__
                })
                raise
        return wrapper
    return decorator


def log_api_request(logger: logging.Logger, request_id: str, user_id: str, endpoint: str, method: str) -> ContextualLoggerAdapter:
    """
    Create a contextual logger for API request handling.
    
    Args:
        logger: Base logger
        request_id: Unique request identifier
        user_id: User ID from authentication
        endpoint: API endpoint being called
        method: HTTP method
        
    Returns:
        ContextualLoggerAdapter with request context
    """
    context = {
        'request_id': request_id,
        'user_id': user_id,
        'endpoint': endpoint,
        'method': method
    }
    return ContextualLoggerAdapter(logger, context)


def log_business_case_operation(logger: logging.Logger, case_id: str, user_id: str, operation: str) -> ContextualLoggerAdapter:
    """
    Create a contextual logger for business case operations.
    
    Args:
        logger: Base logger
        case_id: Business case ID
        user_id: User ID performing the operation
        operation: Type of operation being performed
        
    Returns:
        ContextualLoggerAdapter with business case context
    """
    context = {
        'case_id': case_id,
        'user_id': user_id,
        'operation': operation
    }
    return ContextualLoggerAdapter(logger, context)


def log_agent_operation(logger: logging.Logger, agent_name: str, case_id: str, operation: str) -> ContextualLoggerAdapter:
    """
    Create a contextual logger for agent operations.
    
    Args:
        logger: Base logger
        agent_name: Name of the agent performing the operation
        case_id: Business case ID being processed
        operation: Type of operation being performed
        
    Returns:
        ContextualLoggerAdapter with agent context
    """
    context = {
        'agent_name': agent_name,
        'case_id': case_id,
        'operation': operation
    }
    return ContextualLoggerAdapter(logger, context)


# Convenience functions for common logging patterns
def log_error_with_context(logger: logging.Logger, message: str, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an error with full context and exception information.
    
    Args:
        logger: Logger instance
        message: Error description
        error: Exception that occurred
        context: Additional context information
    """
    extra = context or {}
    extra.update({
        'exception_type': type(error).__name__,
        'exception_message': str(error)
    })
    
    logger.error(message, extra=extra, exc_info=True)


def log_performance_metric(logger: logging.Logger, operation: str, duration_ms: float, success: bool, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log performance metrics for operations.
    
    Args:
        logger: Logger instance
        operation: Operation name
        duration_ms: Duration in milliseconds
        success: Whether the operation succeeded
        context: Additional context information
    """
    extra = context or {}
    extra.update({
        'operation': operation,
        'duration_ms': duration_ms,
        'success': success,
        'metric_type': 'performance'
    })
    
    logger.info(f"Operation {operation} completed", extra=extra) 