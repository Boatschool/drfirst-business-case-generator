"""
Main application entry point for DrFirst Business Case Generator Backend
"""

import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials
from slowapi.errors import RateLimitExceeded
import os

from app.api.v1 import agent_routes as agent_routes_v1
from app.api.v1 import auth_routes, admin_routes, debug_routes
from app.api.v1.cases import cases_router
from app.api.v1 import prompts
from app.api.v1 import function_calling_routes
from app.api.v1.diagnostics import router as diagnostics_router
from app.core.config import settings
from app.core.error_handlers import EXCEPTION_HANDLERS
from app.core.logging_config import setup_logging
from app.services.auth_service import auth_service
from app.middleware.rate_limiter import limiter, rate_limit_exceeded_handler

# Configure enhanced logging
setup_logging()

# Get logger for main module
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for proper resource initialization and cleanup.
    
    This ensures services are properly initialized during startup and cleaned up
    during shutdown, providing stability during Uvicorn reloads.
    """
    startup_start_time = time.time()
    
    # Startup
    logger.info("🚀 Application startup: Initializing services...")
    logger.info("=" * 60)
    
    # Log startup environment information
    import platform
    import sys
    logger.info("🖥️  Startup Environment Information:")
    logger.info(f"  - Platform: {platform.platform()}")
    logger.info(f"  - Python Version: {sys.version.split()[0]}")
    logger.info(f"  - Working Directory: {os.getcwd()}")
    logger.info(f"  - Process ID: {os.getpid()}")
    logger.info(f"  - Debug Mode: {settings.debug}")
    logger.info(f"  - Environment: {'development' if settings.debug else 'production'}")
    
    # Log key environment variables (non-sensitive)
    logger.info("🔍 Environment Variables Check:")
    env_vars = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_CLOUD_PROJECT", 
        "FIREBASE_PROJECT_ID",
        "PYTHONPATH"
    ]
    for var in env_vars:
        value = os.getenv(var)
        if var == "GOOGLE_APPLICATION_CREDENTIALS" and value:
            logger.info(f"  - {var}: {value} (exists: {os.path.exists(value)})")
        else:
            logger.info(f"  - {var}: {'Set' if value else 'Not set'}")
    
    # Quick directory check for common startup issues
    if not os.getcwd().endswith("backend"):
        logger.warning("⚠️ Working directory is not 'backend' - this may cause import issues")
        logger.warning("💡 Consider running: cd backend && PYTHONPATH=. uvicorn app.main:app --reload")
    
    try:
        # Initialize AuthService (Firebase Admin SDK)
        auth_start = time.time()
        if not auth_service.is_initialized:
            logger.info("🔧 Initializing AuthService...")
            auth_service._initialize_firebase()
        else:
            logger.info("✅ AuthService already initialized")
        auth_duration = time.time() - auth_start
        
        # Initialize VertexAIService
        vertex_start = time.time()
        logger.info("🤖 Initializing VertexAI service...")
        from app.services.vertex_ai_service import vertex_ai_service
        vertex_ai_service.initialize()
        vertex_duration = time.time() - vertex_start
        
        total_startup_time = time.time() - startup_start_time
        
        logger.info("✅ All services initialized successfully")
        logger.info("⏱️  Startup Timing Summary:")
        logger.info(f"  - AuthService: {auth_duration:.3f} seconds")
        logger.info(f"  - VertexAI Service: {vertex_duration:.3f} seconds")
        logger.info(f"  - Total Startup: {total_startup_time:.3f} seconds")
        
        # Log final service status
        logger.info("📊 Service Status Summary:")
        logger.info(f"  - Firebase Auth: {'✅ Healthy' if auth_service.is_initialized else '❌ Failed'}")
        logger.info(f"  - VertexAI: {'✅ Healthy' if vertex_ai_service.is_initialized else '❌ Failed'}")
        
        logger.info("=" * 60)
        logger.info("🎉 Application startup completed successfully!")
        logger.info("📡 API available at: http://0.0.0.0:8000")
        logger.info("📋 Health check: http://0.0.0.0:8000/health")
        logger.info("🔧 Diagnostics: http://0.0.0.0:8000/api/v1/diagnostics/health")
        logger.info("📊 Full status: http://0.0.0.0:8000/api/v1/diagnostics/status")
        logger.info("=" * 60)
        
    except Exception as e:
        error_time = time.time() - startup_start_time
        logger.error("=" * 60)
        logger.error(f"❌ STARTUP FAILED after {error_time:.3f} seconds")
        logger.error(f"❌ Error: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        logger.exception("❌ Startup error details:")
        logger.error("=" * 60)
        logger.error("💡 Troubleshooting Tips:")
        logger.error("  1. Check Google Cloud credentials configuration")
        logger.error("  2. Verify working directory (should be in 'backend' folder)")
        logger.error("  3. Ensure PYTHONPATH is set correctly")
        logger.error("  4. Check service account permissions")
        logger.error("  5. Visit /api/v1/diagnostics/diagnostics for detailed info")
        logger.error("=" * 60)
        raise
    
    yield  # Application runs here
    
    # Shutdown
    shutdown_start_time = time.time()
    logger.info("🛑 Application shutdown: Cleaning up resources...")
    
    try:
        # Cleanup AuthService (Firebase Admin SDK)
        logger.info("🧹 Cleaning up AuthService...")
        auth_service.cleanup()
        
        # Reset VertexAIService
        logger.info("🤖 Resetting VertexAI service...")
        vertex_ai_service.reset()
        
        # Placeholder for other singletons - to be implemented in P1.3/P2
        # from app.core.dependencies import reset_all_singletons
        # reset_all_singletons()
        
        shutdown_duration = time.time() - shutdown_start_time
        logger.info(f"✅ Cleanup completed successfully in {shutdown_duration:.3f} seconds")
        
    except Exception as e:
        shutdown_duration = time.time() - shutdown_start_time
        logger.error(f"❌ Error during cleanup after {shutdown_duration:.3f} seconds: {e}")
        logger.exception("Shutdown error details:")


# Initialize Firebase Admin SDK using our auth service at import time
# The lifespan manager will ensure proper initialization during startup
logger.info(f"🔍 Firebase Admin SDK initialization status at import: {auth_service.is_initialized}")

app = FastAPI(
    title="DrFirst Business Case Generator API",
    description="Backend API for the DrFirst Agentic Business Case Generator",
    version="1.0.0",
    lifespan=lifespan  # Add lifecycle management
)

# Configure CORS to allow frontend development servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure global exception handlers for consistent error responses
for exception_type, handler in EXCEPTION_HANDLERS.items():
    app.add_exception_handler(exception_type, handler)

# Configure rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Include API routers
app.include_router(
    agent_routes_v1.router, prefix="/api/v1/agents", tags=["Agent API v1"]
)
app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin_routes.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(cases_router, prefix="/api/v1", tags=["Business Cases"])
app.include_router(debug_routes.router, prefix="/api/v1", tags=["debug"])
app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["prompts"])
app.include_router(function_calling_routes.router, prefix="/api/v1", tags=["Function Calling"])
app.include_router(diagnostics_router, prefix="/api/v1", tags=["diagnostics"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "DrFirst Business Case Generator API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/debug/firebase-status")
async def firebase_status():
    """Debug endpoint to check Firebase initialization status and configuration"""
    firebase_debug_info = {
        "firebase_initialized": auth_service.is_initialized,
        "firebase_apps_count": len(firebase_admin._apps) if hasattr(firebase_admin, '_apps') else 0,
        "project_config": {
            "firebase_project_id": settings.firebase_project_id,
            "google_cloud_project_id": settings.google_cloud_project_id,
        },
        "environment_vars": {
            "GOOGLE_APPLICATION_CREDENTIALS": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")),
            "GOOGLE_APPLICATION_CREDENTIALS_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "not_set"),
            "settings_google_application_credentials": bool(settings.google_application_credentials),
        },
        "settings_debug": {
            "cors_origins": settings.cors_origins_list,
            "debug_mode": settings.debug,
            "environment": settings.environment,
        }
    }
    
    return {
        "status": "initialized" if auth_service.is_initialized else "failed",
        "debug_info": firebase_debug_info
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
