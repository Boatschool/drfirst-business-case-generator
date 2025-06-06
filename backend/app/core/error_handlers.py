"""
Global exception handlers for the DrFirst Business Case Generator API.

This module provides centralized exception handling to ensure consistent
error responses and proper logging across all API endpoints.
"""

import logging
import traceback
from typing import Dict, Any, Union

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import BaseAPIException, extract_error_context, should_log_error


# Configure logger for error handlers
logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = None,
    details: Dict[str, Any] = None,
    request_id: str = None
) -> Dict[str, Any]:
    """
    Create a standardized error response structure.
    
    Args:
        status_code: HTTP status code
        message: User-friendly error message
        error_code: Optional application-specific error code
        details: Optional additional error details
        request_id: Optional request ID for tracking
        
    Returns:
        Standardized error response dictionary
    """
    error_response = {
        "error": {
            "message": message,
            "status_code": status_code,
        }
    }
    
    if error_code:
        error_response["error"]["error_code"] = error_code
        
    if details:
        error_response["error"]["details"] = details
        
    if request_id:
        error_response["error"]["request_id"] = request_id
    
    return error_response


async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """
    Handle custom API exceptions with enhanced logging and structured responses.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    # Log the error if it should be logged based on severity
    if should_log_error(exc):
        error_context = extract_error_context(exc)
        logger.error(
            f"API Exception: {exc.error_code or 'UNKNOWN'} - {exc.detail}",
            extra={
                "request_id": request_id,
                "url": str(request.url),
                "method": request.method,
                "status_code": exc.status_code,
                "error_context": error_context,
                "user_agent": request.headers.get("user-agent"),
                "client_ip": request.client.host if request.client else None,
            }
        )
    
    # Create structured error response
    error_response = create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_code=exc.error_code,
        details=exc.context if exc.context else None,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers=exc.headers
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle standard FastAPI HTTPExceptions with consistent formatting.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    # Log server errors and authentication issues
    if exc.status_code >= 500 or exc.status_code in [401, 403]:
        logger.error(
            f"HTTP Exception: {exc.status_code} - {exc.detail}",
            extra={
                "request_id": request_id,
                "url": str(request.url),
                "method": request.method,
                "status_code": exc.status_code,
                "user_agent": request.headers.get("user-agent"),
                "client_ip": request.client.host if request.client else None,
            }
        )
    
    # Determine error code based on status
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED", 
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
        500: "INTERNAL_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE"
    }
    
    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
    
    error_response = create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_code=error_code,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers=getattr(exc, 'headers', None)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors with detailed field information.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    # Extract field-level validation errors
    field_errors = {}
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        field_errors[field_path] = error["msg"]
    
    logger.warning(
        f"Validation Error: {len(field_errors)} field(s) failed validation",
        extra={
            "request_id": request_id,
            "url": str(request.url),
            "method": request.method,
            "field_errors": field_errors,
            "user_agent": request.headers.get("user-agent"),
            "client_ip": request.client.host if request.client else None,
        }
    )
    
    error_response = create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Input validation failed",
        error_code="VALIDATION_ERROR",
        details={"field_errors": field_errors},
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions with secure error responses.
    
    This is the catch-all handler for any exceptions not handled by more specific handlers.
    It ensures that internal details are not leaked to clients while providing proper logging.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    # Log the full exception details for debugging
    logger.error(
        f"Unhandled Exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "request_id": request_id,
            "url": str(request.url),
            "method": request.method,
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc(),
            "user_agent": request.headers.get("user-agent"),
            "client_ip": request.client.host if request.client else None,
        }
    )
    
    # Return a generic error response to avoid leaking internal details
    error_response = create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An internal server error occurred. Please try again later.",
        error_code="INTERNAL_ERROR",
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )


async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle Starlette HTTP exceptions (like 404 for non-existent routes).
    """
    request_id = getattr(request.state, 'request_id', None)
    
    # Log client errors only at debug level, server errors at error level
    if exc.status_code >= 500:
        log_level = logger.error
    else:
        log_level = logger.debug
        
    log_level(
        f"Starlette HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "request_id": request_id,
            "url": str(request.url),
            "method": request.method,
            "status_code": exc.status_code,
        }
    )
    
    error_code_map = {
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED", 
        500: "INTERNAL_ERROR"
    }
    
    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
    
    error_response = create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_code=error_code,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


# Exception handler registry for easy configuration
EXCEPTION_HANDLERS = {
    BaseAPIException: base_api_exception_handler,
    HTTPException: http_exception_handler,
    RequestValidationError: validation_exception_handler,
    StarletteHTTPException: starlette_http_exception_handler,
    Exception: generic_exception_handler,  # Catch-all handler
} 