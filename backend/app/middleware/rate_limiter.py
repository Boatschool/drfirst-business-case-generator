"""
Rate limiting middleware for FastAPI using slowapi.

This module provides basic rate limiting functionality to protect the API
from abuse and ensure fair usage across all clients.
"""

import logging
from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from app.core.config import settings

# Optional Redis import
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


def get_user_id_or_ip(request: Request) -> str:
    """
    Key function for rate limiting that tries to use authenticated user ID,
    falling back to IP address for unauthenticated requests.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        str: User ID if authenticated, otherwise IP address
    """
    try:
        # Try to get user from auth context if available
        if hasattr(request.state, 'user') and request.state.user:
            user_id = getattr(request.state.user, 'uid', None)
            if user_id:
                logger.debug(f"Rate limiting by user ID: {user_id}")
                return f"user:{user_id}"
    except (AttributeError, Exception) as e:
        logger.debug(f"Could not get user ID for rate limiting: {e}")
    
    # Fall back to IP address
    ip = get_remote_address(request)
    logger.debug(f"Rate limiting by IP: {ip}")
    return f"ip:{ip}"


def create_limiter() -> Limiter:
    """
    Create and configure the rate limiter instance.
    
    Returns:
        Limiter: Configured slowapi Limiter instance
    """
    # Check if Redis URL is configured for distributed rate limiting
    storage_uri = None
    if settings.redis_url and REDIS_AVAILABLE:
        try:
            # Test Redis connection
            storage_uri = settings.redis_url
            logger.info("Configuring rate limiter with Redis storage")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis for rate limiting: {e}")
            logger.info("Falling back to in-memory rate limiting")
    else:
        if settings.redis_url and not REDIS_AVAILABLE:
            logger.warning("Redis URL configured but redis package not available. Install 'redis' for distributed rate limiting.")
        logger.info("Using in-memory rate limiting (not suitable for multi-instance deployments)")
    
    # Create limiter with user ID or IP as key
    limiter = Limiter(
        key_func=get_user_id_or_ip,
        default_limits=[settings.default_rate_limit],
        storage_uri=storage_uri
    )
    
    logger.info(f"Rate limiter initialized with default limit: {settings.default_rate_limit}")
    return limiter


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded exceptions.
    
    Args:
        request: The FastAPI request object
        exc: The RateLimitExceeded exception
        
    Returns:
        JSONResponse: JSON response with rate limit error details
    """
    logger.warning(
        f"Rate limit exceeded for {get_user_id_or_ip(request)} "
        f"on {request.method} {request.url.path}"
    )
    
    response_data = {
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later.",
        "detail": str(exc.detail) if hasattr(exc, 'detail') else None,
        "type": "rate_limit_exceeded"
    }
    
    # Create response with appropriate headers
    response = JSONResponse(
        status_code=429,
        content=response_data
    )
    
    # Add rate limit headers if available
    if hasattr(exc, 'retry_after'):
        response.headers["Retry-After"] = str(exc.retry_after)
    
    response.headers["X-RateLimit-Limit"] = settings.default_rate_limit
    
    return response


# Global limiter instance
limiter = create_limiter() 