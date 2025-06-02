"""
Main application entry point for DrFirst Business Case Generator Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials

from app.api.v1 import agent_routes, auth_routes, admin_routes
from app.core.config import settings

# Initialize Firebase Admin SDK
try:
    # Attempt to initialize with default credentials (e.g., GOOGLE_APPLICATION_CREDENTIALS env var or Cloud Run service account)
    firebase_admin.initialize_app()
    print("Firebase Admin SDK initialized with default credentials.")
except Exception as e:
    print(f"Failed to initialize Firebase Admin SDK with default credentials: {e}")
    # As a fallback for local development if GOOGLE_APPLICATION_CREDENTIALS is not set,
    # you might explicitly load a service account key, but this is less secure for production.
    # For example (ensure 'path/to/your/serviceAccountKey.json' is correct and secure):
    # cred_path = "path/to/your/serviceAccountKey.json"
    # try:
    #     cred = credentials.Certificate(cred_path)
    #     firebase_admin.initialize_app(cred)
    #     print(f"Firebase Admin SDK initialized with credentials from: {cred_path}")
    # except Exception as e_cred:
    #     print(f"Failed to initialize Firebase Admin SDK with specified credentials ({cred_path}): {e_cred}")
    #     print("Firebase Admin SDK NOT initialized. Authentication will fail.")

app = FastAPI(
    title="DrFirst Business Case Generator API",
    description="Backend API for the DrFirst Agentic Business Case Generator",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4000"],  # Add frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(agent_routes.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin_routes.router, prefix="/api/v1/admin", tags=["admin"])

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