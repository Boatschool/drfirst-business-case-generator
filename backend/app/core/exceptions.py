"""
Custom exceptions for the DrFirst Business Case Generator API.

This module defines application-specific exceptions that provide consistent
error handling throughout the backend services and API routes.
"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class BaseAPIException(HTTPException):
    """
    Base exception class for all API-related errors.
    Provides consistent structure and logging capabilities.
    """
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.context = context or {}


# Authentication and Authorization Exceptions
class AuthenticationError(BaseAPIException):
    """Raised when user authentication fails"""
    
    def __init__(
        self,
        detail: str = "Authentication failed",
        error_code: str = "AUTH_FAILED",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            error_code=error_code,
            context=context
        )


class AuthorizationError(BaseAPIException):
    """Raised when user lacks permission for an action"""
    
    def __init__(
        self,
        detail: str = "Not authorized to perform this action",
        error_code: str = "AUTH_FORBIDDEN",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code,
            context=context
        )


class TokenExpiredError(AuthenticationError):
    """Raised when authentication token has expired"""
    
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            detail="Your session has expired. Please sign in again.",
            error_code="TOKEN_EXPIRED",
            context=context
        )


# Resource and Data Exceptions
class ResourceNotFoundError(BaseAPIException):
    """Raised when a requested resource cannot be found"""
    
    def __init__(
        self,
        resource_type: str = "Resource",
        resource_id: Optional[str] = None,
        detail: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        if detail is None:
            detail = f"{resource_type} not found"
            if resource_id:
                detail += f" (ID: {resource_id})"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="RESOURCE_NOT_FOUND",
            context=context or {"resource_type": resource_type, "resource_id": resource_id}
        )


class BusinessCaseNotFoundError(ResourceNotFoundError):
    """Raised when a business case cannot be found"""
    
    def __init__(self, case_id: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            resource_type="Business case",
            resource_id=case_id,
            context=context
        )


class UserNotFoundError(ResourceNotFoundError):
    """Raised when a user cannot be found"""
    
    def __init__(self, user_id: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            resource_type="User",
            resource_id=user_id,
            context=context
        )


class JobNotFoundError(ResourceNotFoundError):
    """Raised when a job cannot be found"""
    
    def __init__(self, job_id: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            resource_type="Job",
            resource_id=job_id,
            context=context
        )


# Validation and Input Exceptions
class ValidationError(BaseAPIException):
    """Raised when input validation fails"""
    
    def __init__(
        self,
        detail: str = "Input validation failed",
        field_errors: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            context=context or {"field_errors": field_errors}
        )


class InvalidOperationError(BaseAPIException):
    """Raised when an operation is not valid in the current state"""
    
    def __init__(
        self,
        detail: str,
        current_state: Optional[str] = None,
        required_state: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="INVALID_OPERATION",
            context=context or {
                "current_state": current_state,
                "required_state": required_state
            }
        )


class ConflictError(BaseAPIException):
    """Raised when a request conflicts with current resource state"""
    
    def __init__(
        self,
        detail: str,
        conflicting_resource: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="RESOURCE_CONFLICT",
            context=context or {"conflicting_resource": conflicting_resource}
        )


# Service and External System Exceptions
class ServiceError(BaseAPIException):
    """Raised when an internal service fails"""
    
    def __init__(
        self,
        service_name: str,
        detail: str,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{service_name} service error: {detail}",
            error_code="SERVICE_ERROR",
            context=context or {"service": service_name}
        )


class DatabaseError(ServiceError):
    """Raised when database operations fail"""
    
    def __init__(
        self,
        operation: str,
        detail: str,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            service_name="Database",
            detail=f"Failed to {operation}: {detail}",
            context=context or {"operation": operation}
        )


class ExternalServiceError(BaseAPIException):
    """Raised when external service calls fail"""
    
    def __init__(
        self,
        service_name: str,
        detail: str,
        status_code: int = status.HTTP_502_BAD_GATEWAY,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail=f"External service error ({service_name}): {detail}",
            error_code="EXTERNAL_SERVICE_ERROR",
            context=context or {"external_service": service_name}
        )


# Agent and Processing Exceptions  
class AgentProcessingError(ServiceError):
    """Raised when agent processing fails"""
    
    def __init__(
        self,
        agent_name: str,
        detail: str,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            service_name=f"Agent ({agent_name})",
            detail=detail,
            context=context or {"agent": agent_name}
        )


class BusinessLogicError(BaseAPIException):
    """Raised when business logic validation fails"""
    
    def __init__(
        self,
        detail: str,
        rule: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BUSINESS_LOGIC_ERROR",
            context=context or {"violated_rule": rule}
        )


# Rate Limiting and Quota Exceptions
class RateLimitExceededError(BaseAPIException):
    """Raised when rate limits are exceeded"""
    
    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        headers = {"Retry-After": str(retry_after)} if retry_after else None
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers=headers,
            error_code="RATE_LIMIT_EXCEEDED",
            context=context
        )


# Utility functions for exception handling
def extract_error_context(exception: Exception) -> Dict[str, Any]:
    """Extract relevant context information from an exception"""
    context = {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception)
    }
    
    if isinstance(exception, BaseAPIException):
        context.update({
            "error_code": exception.error_code,
            "status_code": exception.status_code,
            "context": exception.context
        })
    
    return context


def is_client_error(status_code: int) -> bool:
    """Check if status code represents a client error (4xx)"""
    return 400 <= status_code < 500


def is_server_error(status_code: int) -> bool:
    """Check if status code represents a server error (5xx)"""
    return 500 <= status_code < 600


def should_log_error(exception: Exception) -> bool:
    """Determine if an exception should be logged based on its type and severity"""
    if isinstance(exception, BaseAPIException):
        # Log server errors and authentication issues, but not client validation errors
        return (
            is_server_error(exception.status_code) or
            isinstance(exception, (AuthenticationError, AuthorizationError))
        )
    
    # Log all other exceptions as they're unexpected
    return True 