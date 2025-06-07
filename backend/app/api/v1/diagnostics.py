"""
Diagnostic API endpoints for system monitoring and troubleshooting.

This module provides comprehensive health checks, status information, and diagnostic
data for all services and components in the application.
"""

import logging
import time
import platform
import sys
import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.services.vertex_ai_service import vertex_ai_service
from app.services.auth_service import auth_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        dict: Basic health status of all services
    """
    start_time = time.time()
    
    try:
        # Check core services
        vertex_ai_healthy = vertex_ai_service.is_initialized
        auth_healthy = auth_service.is_initialized
        
        # Overall health status
        overall_healthy = vertex_ai_healthy and auth_healthy
        
        response_time = time.time() - start_time
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": time.time(),
            "response_time_seconds": response_time,
            "services": {
                "vertex_ai": "healthy" if vertex_ai_healthy else "unhealthy",
                "firebase_auth": "healthy" if auth_healthy else "unhealthy"
            },
            "version": "1.0.0",
            "environment": "development" if settings.debug else "production"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": time.time()
            }
        )


@router.get("/status")
async def detailed_status() -> Dict[str, Any]:
    """
    Detailed status information for all services.
    
    Returns:
        dict: Comprehensive status information
    """
    start_time = time.time()
    
    try:
        status = {
            "timestamp": time.time(),
            "application": {
                "name": "DrFirst Business Case Generator API",
                "version": "1.0.0",
                "environment": "development" if settings.debug else "production",
                "debug_mode": settings.debug
            },
            "system": {
                "platform": platform.platform(),
                "python_version": sys.version.split()[0],
                "working_directory": os.getcwd(),
                "process_id": os.getpid(),
                "uptime_seconds": time.time() - start_time  # Approximate
            },
            "services": {
                "vertex_ai": vertex_ai_service.get_status(),
                "firebase_auth": auth_service.get_status()
            },
            "performance": {
                "response_time_seconds": time.time() - start_time,
                "memory_usage": _get_memory_usage(),
                "cpu_usage": _get_cpu_usage()
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get("/diagnostics")
async def full_diagnostics() -> Dict[str, Any]:
    """
    Comprehensive diagnostic information for troubleshooting.
    
    Returns:
        dict: Detailed diagnostic data
    """
    start_time = time.time()
    
    try:
        diagnostics = {
            "timestamp": time.time(),
            "diagnostic_version": "1.0.0",
            "collection_time_seconds": 0,  # Will be updated at the end
            
            "application_diagnostics": {
                "name": "DrFirst Business Case Generator API",
                "version": "1.0.0",
                "startup_info": _get_startup_diagnostics(),
                "configuration": _get_configuration_diagnostics()
            },
            
            "system_diagnostics": {
                "platform": _get_platform_diagnostics(),
                "python": _get_python_diagnostics(),
                "environment": _get_environment_diagnostics(),
                "performance": _get_performance_diagnostics()
            },
            
            "service_diagnostics": {
                "vertex_ai": vertex_ai_service.get_diagnostic_info(),
                "firebase_auth": auth_service.get_diagnostic_info()
            },
            
            "dependency_diagnostics": _get_dependency_diagnostics(),
            "troubleshooting": _get_troubleshooting_hints()
        }
        
        # Update collection time
        diagnostics["collection_time_seconds"] = time.time() - start_time
        
        return diagnostics
        
    except Exception as e:
        logger.error(f"Diagnostics collection failed: {e}")
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc(),
            "timestamp": time.time()
        }


@router.get("/services/{service_name}")
async def service_status(service_name: str) -> Dict[str, Any]:
    """
    Get detailed status for a specific service.
    
    Args:
        service_name: Name of the service ('vertex_ai' or 'firebase_auth')
    
    Returns:
        dict: Detailed service status
    """
    if service_name == "vertex_ai":
        return vertex_ai_service.get_status()
    elif service_name == "firebase_auth":
        return auth_service.get_status()
    else:
        raise HTTPException(
            status_code=404, 
            detail=f"Service '{service_name}' not found. Available services: vertex_ai, firebase_auth"
        )


@router.get("/config")
async def configuration_info() -> Dict[str, Any]:
    """
    Get sanitized configuration information (sensitive data removed).
    
    Returns:
        dict: Configuration information
    """
    try:
        config = {
            "application": {
                "debug": settings.debug,
                "environment": "development" if settings.debug else "production"
            },
            "vertex_ai": {
                "project_id": settings.google_cloud_project_id,
                "location": settings.vertex_ai_location,
                "model_name": settings.vertex_ai_model_name,
                "temperature": settings.vertex_ai_temperature,
                "max_tokens": settings.vertex_ai_max_tokens,
                "top_p": settings.vertex_ai_top_p,
                "top_k": settings.vertex_ai_top_k
            },
            "firebase": {
                "project_id": settings.firebase_project_id,
                "credentials_configured": bool(settings.google_application_credentials),
                "environment_credentials": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
            },
            "system": {
                "working_directory": os.getcwd(),
                "python_version": sys.version.split()[0],
                "platform": platform.platform()
            }
        }
        
        return config
        
    except Exception as e:
        logger.error(f"Configuration info failed: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration info failed: {str(e)}")


def _get_memory_usage() -> Optional[Dict[str, Any]]:
    """Get memory usage information"""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            "percent": process.memory_percent()
        }
    except:
        return None


def _get_cpu_usage() -> Optional[float]:
    """Get CPU usage percentage"""
    try:
        import psutil
        return psutil.Process().cpu_percent()
    except:
        return None


def _get_startup_diagnostics() -> Dict[str, Any]:
    """Get application startup diagnostics"""
    return {
        "process_id": os.getpid(),
        "parent_process_id": os.getppid(),
        "command_line": " ".join(sys.argv),
        "startup_time": time.time(),  # Approximate
        "python_executable": sys.executable
    }


def _get_configuration_diagnostics() -> Dict[str, Any]:
    """Get configuration diagnostics (sanitized)"""
    return {
        "settings_class": str(settings.__class__),
        "debug_mode": settings.debug,
        "has_firebase_project": bool(settings.firebase_project_id),
        "has_gcp_project": bool(settings.google_cloud_project_id),
        "has_credentials_file": bool(settings.google_application_credentials),
        "vertex_ai_configured": all([
            settings.google_cloud_project_id,
            settings.vertex_ai_location,
            settings.vertex_ai_model_name
        ])
    }


def _get_platform_diagnostics() -> Dict[str, Any]:
    """Get platform diagnostics"""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture(),
        "platform": platform.platform()
    }


def _get_python_diagnostics() -> Dict[str, Any]:
    """Get Python environment diagnostics"""
    return {
        "version": sys.version,
        "version_info": {
            "major": sys.version_info.major,
            "minor": sys.version_info.minor,
            "micro": sys.version_info.micro
        },
        "executable": sys.executable,
        "path": sys.path[:10],  # First 10 entries
        "modules_count": len(sys.modules)
    }


def _get_environment_diagnostics() -> Dict[str, Any]:
    """Get environment variable diagnostics"""
    relevant_env_vars = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_CLOUD_PROJECT", 
        "FIREBASE_PROJECT_ID",
        "PYTHONPATH",
        "PATH",
        "HOME",
        "USER"
    ]
    
    env_info = {}
    for var in relevant_env_vars:
        value = os.getenv(var)
        if var in ["PATH", "PYTHONPATH"]:
            # Truncate long path variables
            env_info[var] = value[:100] + "..." if value and len(value) > 100 else value
        else:
            env_info[var] = value
    
    return env_info


def _get_performance_diagnostics() -> Dict[str, Any]:
    """Get performance diagnostics"""
    try:
        performance = {
            "memory": _get_memory_usage(),
            "cpu": _get_cpu_usage(),
            "disk_usage": None,
            "load_average": None
        }
        
        # Disk usage
        try:
            import psutil
            disk = psutil.disk_usage('/')
            performance["disk_usage"] = {
                "total_gb": disk.total / 1024 / 1024 / 1024,
                "used_gb": disk.used / 1024 / 1024 / 1024,
                "free_gb": disk.free / 1024 / 1024 / 1024,
                "percent": (disk.used / disk.total) * 100
            }
        except:
            pass
        
        # Load average (Unix-like systems)
        try:
            if hasattr(os, 'getloadavg'):
                performance["load_average"] = os.getloadavg()
        except:
            pass
        
        return performance
        
    except Exception:
        return {"error": "Could not collect performance data"}


def _get_dependency_diagnostics() -> Dict[str, Any]:
    """Get dependency version diagnostics"""
    dependencies = {}
    
    # Core dependencies
    dependency_modules = [
        'fastapi', 'uvicorn', 'pydantic', 'firebase_admin', 
        'vertexai', 'google.cloud', 'psutil'
    ]
    
    for module_name in dependency_modules:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'Unknown')
            dependencies[module_name] = version
        except ImportError:
            dependencies[module_name] = 'Not installed'
        except Exception as e:
            dependencies[module_name] = f'Error: {str(e)}'
    
    return dependencies


def _get_troubleshooting_hints() -> Dict[str, Any]:
    """Get troubleshooting hints based on current system state"""
    hints = {
        "common_issues": [],
        "recommendations": [],
        "next_steps": []
    }
    
    # Check for common issues
    if not vertex_ai_service.is_initialized:
        hints["common_issues"].append("VertexAI service not initialized")
        hints["recommendations"].append("Check Google Cloud credentials and project configuration")
    
    if not auth_service.is_initialized:
        hints["common_issues"].append("Firebase Auth service not initialized")
        hints["recommendations"].append("Check Firebase credentials and project configuration")
    
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        hints["common_issues"].append("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        hints["recommendations"].append("Set GOOGLE_APPLICATION_CREDENTIALS or configure default credentials")
    
    # Server startup hints
    if os.getcwd().endswith("drfirst-business-case-generator"):
        hints["recommendations"].append("Run server from backend directory: cd backend && PYTHONPATH=. uvicorn app.main:app --reload")
    
    # Performance hints
    memory = _get_memory_usage()
    if memory and memory["rss_mb"] > 1000:
        hints["recommendations"].append("High memory usage detected - consider optimization")
    
    if not hints["common_issues"]:
        hints["next_steps"].append("All services appear healthy - check application logs for specific errors")
    else:
        hints["next_steps"].append("Address the identified issues above")
        hints["next_steps"].append("Use /diagnostics endpoint for detailed troubleshooting information")
    
    return hints 