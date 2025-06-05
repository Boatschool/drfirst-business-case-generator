"""
Main application entry point for DrFirst Business Case Generator Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials

from app.api.v1 import agent_routes as agent_routes_v1
from app.api.v1 import auth_routes, admin_routes, debug_routes
from app.api.v1 import case_routes as case_routes_v1
from app.api.v1 import prompts
from app.core.config import settings
from app.services.auth_service import auth_service

# Initialize Firebase Admin SDK using our auth service
# The auth_service handles the initialization with proper fallbacks
print(f"🔥 Firebase Admin SDK initialization status: {auth_service.is_initialized}")

app = FastAPI(
    title="DrFirst Business Case Generator API",
    description="Backend API for the DrFirst Agentic Business Case Generator",
    version="1.0.0"
)

# Configure CORS to allow frontend development servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(agent_routes_v1.router, prefix="/api/v1/agents", tags=["Agent API v1"])
app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin_routes.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(case_routes_v1.router, prefix="/api/v1", tags=["Case API v1"])
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 