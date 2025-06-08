"""
Monitoring middleware to detect API response anomalies.
Prevents issues like empty responses when data should exist.
"""

import time
import logging
from typing import Dict, Any, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import json

logger = logging.getLogger(__name__)


class APIMonitoringMiddleware(BaseHTTPMiddleware):
    """Monitor API responses for anomalies."""
    
    def __init__(self, app):
        super().__init__(app)
        self.response_stats = {}
        
    async def dispatch(self, request: Request, call_next):
        """Monitor API requests and responses."""
        start_time = time.time()
        path = request.url.path
        method = request.method
        
        # Track request
        logger.info(f"📊 [MONITOR] {method} {path} - Request started")
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            duration_ms = int(duration * 1000)
            
            # Monitor response
            await self._monitor_response(request, response, duration_ms)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            duration_ms = int(duration * 1000)
            
            logger.error(f"📊 [MONITOR] {method} {path} - ERROR after {duration_ms}ms: {e}")
            raise
    
    async def _monitor_response(self, request: Request, response: Response, duration_ms: int):
        """Monitor specific response patterns."""
        path = request.url.path
        method = request.method
        status_code = response.status_code
        
        # Log basic metrics
        logger.info(f"📊 [MONITOR] {method} {path} - {status_code} in {duration_ms}ms")
        
        # Monitor business case listing endpoint specifically
        if path.startswith("/api/v1/cases") and method == "GET" and status_code == 200:
            await self._monitor_business_case_response(request, response, duration_ms)
        
        # Monitor other critical endpoints
        if status_code >= 500:
            logger.critical(f"🚨 [MONITOR] Server error: {method} {path} - {status_code}")
        
        # Track response time anomalies
        if duration_ms > 5000:  # 5 seconds
            logger.warning(f"⏱️ [MONITOR] Slow response: {method} {path} - {duration_ms}ms")
    
    async def _monitor_business_case_response(self, request: Request, response: Response, duration_ms: int):
        """Monitor business case API responses for anomalies."""
        path = request.url.path
        
        # Get response size
        content_length = response.headers.get("content-length", "0")
        content_size = int(content_length)
        
        # Check for suspiciously small responses (likely empty arrays)
        if content_size <= 2:  # "[]" is 2 bytes
            # This is what we experienced - getting empty array when data should exist
            user_info = ""
            if hasattr(request.state, 'current_user'):
                user_info = f" for user {request.state.current_user.get('uid', 'unknown')}"
            
            logger.warning(f"📊 [MONITOR] ⚠️ Suspiciously small response from {path}{user_info}: {content_size} bytes")
            logger.warning(f"📊 [MONITOR] 🔍 This might indicate an empty result when data should exist")
            
            # Log query parameters for debugging
            query_params = dict(request.query_params)
            if query_params:
                logger.warning(f"📊 [MONITOR] 🔍 Query parameters: {query_params}")
        
        # Check for typical response sizes
        elif content_size > 0:
            # Estimate number of items (rough calculation)
            estimated_items = max(1, content_size // 200)  # Rough estimate: 200 bytes per item
            logger.info(f"📊 [MONITOR] ✅ Normal response size: {content_size} bytes (~{estimated_items} items)")
        
        # Track performance
        if path == "/api/v1/cases":
            # This is the main business case listing endpoint
            if duration_ms > 1000:
                logger.warning(f"📊 [MONITOR] ⏱️ Slow business case listing: {duration_ms}ms")
            else:
                logger.info(f"📊 [MONITOR] ⚡ Fast business case listing: {duration_ms}ms")


class ResponseValidationMonitor:
    """Monitor for response validation issues."""
    
    @staticmethod
    def log_conversion_anomaly(operation: str, source_count: int, result_count: int, user_id: str = None):
        """Log when data conversion has anomalies."""
        user_info = f" for user {user_id}" if user_id else ""
        
        if source_count > 0 and result_count == 0:
            logger.critical(f"🚨 [VALIDATION] CRITICAL ANOMALY in {operation}{user_info}: "
                          f"Found {source_count} items but converted 0 - possible validation failure!")
        elif source_count > result_count:
            ratio = result_count / source_count
            logger.warning(f"⚠️ [VALIDATION] Partial conversion in {operation}{user_info}: "
                         f"{result_count}/{source_count} items ({ratio:.2%})")
        else:
            logger.info(f"✅ [VALIDATION] Perfect conversion in {operation}{user_info}: "
                       f"{result_count}/{source_count} items")
    
    @staticmethod
    def log_validation_error(operation: str, error: Exception, data_preview: str = None):
        """Log validation errors with context."""
        logger.error(f"❌ [VALIDATION] Validation failed in {operation}: {error}")
        if data_preview:
            logger.error(f"🔍 [VALIDATION] Data preview: {data_preview[:200]}...")
    
    @staticmethod
    def log_empty_response(operation: str, expected_data: bool = True, user_id: str = None):
        """Log when responses are unexpectedly empty."""
        user_info = f" for user {user_id}" if user_id else ""
        
        if expected_data:
            logger.warning(f"📊 [VALIDATION] Unexpected empty response in {operation}{user_info}")
        else:
            logger.info(f"📊 [VALIDATION] Expected empty response in {operation}{user_info}")


# Singleton instance for easy access
response_monitor = ResponseValidationMonitor() 