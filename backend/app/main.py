"""
Main application entry point for DrFirst Business Case Generator Backend
"""

import logging
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
from app.core.config import settings
from app.core.error_handlers import EXCEPTION_HANDLERS
from app.core.logging_config import setup_logging
from app.services.auth_service import auth_service
from app.middleware.rate_limiter import limiter, rate_limit_exceeded_handler

# Configure enhanced logging
setup_logging()

# Get logger for main module
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK using our auth service
# The auth_service handles the initialization with proper fallbacks
logger.info(f"Firebase Admin SDK initialization status: {auth_service.is_initialized}")

app = FastAPI(
    title="DrFirst Business Case Generator API",
    description="Backend API for the DrFirst Agentic Business Case Generator",
    version="1.0.0",
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
