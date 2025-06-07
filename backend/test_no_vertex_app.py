"""
Test app without VertexAI to isolate hang issue
"""

import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
import os

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.services.auth_service import auth_service

# Configure enhanced logging
setup_logging()

# Get logger for main module
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Test lifespan manager without VertexAI"""
    startup_start_time = time.time()
    
    # Startup
    logger.info("🚀 NO-VERTEX APP: Starting up...")
    
    try:
        # Test AuthService only (no VertexAI)
        auth_start = time.time()
        if not auth_service.is_initialized:
            logger.info("🔧 Initializing AuthService...")
            auth_service._initialize_firebase()
        else:
            logger.info("✅ AuthService already initialized")
        auth_duration = time.time() - auth_start
        
        # Skip VertexAI entirely
        logger.info("⏭️ SKIPPING VertexAI initialization for testing")
        
        total_startup_time = time.time() - startup_start_time
        
        logger.info("✅ NO-VERTEX APP: Services initialized successfully")
        logger.info(f"⏱️  AuthService: {auth_duration:.3f} seconds")
        logger.info(f"⏱️  Total: {total_startup_time:.3f} seconds")
        logger.info("📡 NO-VERTEX APP ready at: http://0.0.0.0:8002")
        
    except Exception as e:
        logger.error(f"❌ NO-VERTEX APP startup failed: {e}")
        logger.exception("Error details:")
        raise
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("🛑 NO-VERTEX APP: Shutting down...")


app = FastAPI(
    title="No VertexAI Test API",
    description="Test API without VertexAI to isolate startup issues",
    version="1.0.0",
    lifespan=lifespan
)

# Add basic CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "No VertexAI test API is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/test")
async def test():
    """Test endpoint"""
    return {
        "auth_initialized": auth_service.is_initialized,
        "firebase_apps": len(firebase_admin._apps) if hasattr(firebase_admin, '_apps') else 0,
        "vertex_ai_skipped": True
    } 