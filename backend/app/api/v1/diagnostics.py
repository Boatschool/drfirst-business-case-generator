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
import asyncio
import traceback
import psutil  # Add this import for resource monitoring
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.services.vertex_ai_service import vertex_ai_service
from app.services.auth_service import get_auth_service
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
        auth_service = get_auth_service()
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
                "firebase_auth": get_auth_service().get_status()
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
                "firebase_auth": get_auth_service().get_diagnostic_info()
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
        return get_auth_service().get_status()
    else:
        raise HTTPException(
            status_code=404, 
            detail=f"Service '{service_name}' not found. Available services: vertex_ai, firebase_auth"
        )


@router.get("/resources")
async def get_resource_usage():
    """
    Get comprehensive system resource usage information for Issue #5 monitoring.
    
    This endpoint monitors resource usage to detect and prevent resource leaks
    during application lifecycle events.
    """
    try:
        # Memory usage information
        memory_info = _get_memory_usage()
        
        # Disk usage information  
        disk_info = _get_disk_usage()
        
        # Network connection information
        network_info = _get_network_info()
        
        # Database connection health
        database_health = _check_database_health()
        
        # Service health checks
        auth_health = _check_auth_service_health()
        vertex_health = _check_vertex_ai_health()
        
        # Resource warnings detection
        warnings = _detect_resource_warnings(memory_info, network_info)
        
        return {
            "timestamp": time.time(),
            "resource_usage": {
                "memory": memory_info,
                "disk": disk_info,
                "network": network_info
            },
            "service_health": {
                "database": database_health,
                "auth_service": auth_health,
                "vertex_ai": vertex_health
            },
            "warnings": warnings,
            "status": "healthy" if not warnings else "warning"
        }
        
    except Exception as e:
        logger.error(f"Error getting resource usage: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get resource usage: {str(e)}")


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


def _get_memory_usage() -> Dict[str, Any]:
    """Get detailed memory usage information"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": round(memory_info.rss / 1024 / 1024, 2),  # Resident Set Size
            "vms_mb": round(memory_info.vms / 1024 / 1024, 2),  # Virtual Memory Size
            "percent": round(process.memory_percent(), 2),
            "available_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2),
            "total_mb": round(psutil.virtual_memory().total / 1024 / 1024, 2)
        }
    except Exception as e:
        return {"error": str(e), "available": False}


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
    
    if not get_auth_service().is_initialized:
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


def _get_disk_usage() -> Dict[str, Any]:
    """Get disk usage information for the working directory"""
    try:
        usage = psutil.disk_usage(os.getcwd())
        
        return {
            "total_gb": round(usage.total / 1024 / 1024 / 1024, 2),
            "used_gb": round(usage.used / 1024 / 1024 / 1024, 2),
            "free_gb": round(usage.free / 1024 / 1024 / 1024, 2),
            "percent_used": round((usage.used / usage.total) * 100, 2)
        }
    except Exception as e:
        return {"error": str(e), "available": False}


def _get_network_info() -> Dict[str, Any]:
    """Get network connection information to detect connection leaks"""
    try:
        connections = psutil.net_connections()
        
        # Count connections by status
        status_counts = {}
        for conn in connections:
            status = conn.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count connections by local port (to detect port accumulation)
        port_counts = {}
        for conn in connections:
            if conn.laddr:
                port = conn.laddr.port
                port_counts[port] = port_counts.get(port, 0) + 1
        
        return {
            "total_connections": len(connections),
            "status_breakdown": status_counts,
            "close_wait_count": status_counts.get("CLOSE_WAIT", 0),
            "established_count": status_counts.get("ESTABLISHED", 0),
            "listening_count": status_counts.get("LISTEN", 0),
            "port_usage": dict(list(sorted(port_counts.items(), key=lambda x: x[1], reverse=True))[:10])
        }
    except Exception as e:
        return {"error": str(e), "available": False}


def _check_database_health() -> Dict[str, Any]:
    """Check database connection health"""
    try:
        from app.core.dependencies import get_db
        db = get_db()
        
        if hasattr(db, 'get_status'):
            return db.get_status()
        else:
            return {
                "status": "unknown",
                "message": "Database client does not support status check"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def _check_auth_service_health() -> Dict[str, Any]:
    """Check auth service health"""
    try:
        auth_service = get_auth_service()
        return {
            "initialized": auth_service.is_initialized,
            "status": "healthy" if auth_service.is_initialized else "not_initialized"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def _check_vertex_ai_health() -> Dict[str, Any]:
    """Check Vertex AI service health"""
    try:
        status = vertex_ai_service.get_status()
        return {
            "initialized": status["initialized"],
            "status": status["health"]["status"],
            "metrics": status["metrics"]
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e)
        }


def _detect_resource_warnings(memory_info: Dict[str, Any], network_info: Dict[str, Any]) -> List[str]:
    """Detect potential resource leak warnings"""
    warnings = []
    
    # Memory warnings
    if "rss_mb" in memory_info:
        if memory_info["rss_mb"] > 1000:  # More than 1GB
            warnings.append(f"High memory usage: {memory_info['rss_mb']}MB RSS")
        elif memory_info["rss_mb"] > 500:  # More than 500MB
            warnings.append(f"Medium memory usage: {memory_info['rss_mb']}MB RSS")
    
    # Network connection warnings  
    if "close_wait_count" in network_info:
        if network_info["close_wait_count"] > 10:
            warnings.append(f"High CLOSE_WAIT connections: {network_info['close_wait_count']} (potential connection leak)")
        elif network_info["close_wait_count"] > 5:
            warnings.append(f"Moderate CLOSE_WAIT connections: {network_info['close_wait_count']}")
    
    if "total_connections" in network_info:
        if network_info["total_connections"] > 100:
            warnings.append(f"High total connections: {network_info['total_connections']}")
    
    return warnings 