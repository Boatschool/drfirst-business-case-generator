"""
Configuration management for the DrFirst Business Case Generator Backend
"""

import os
from typing import Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    # Application settings
    app_name: str = "DrFirst Business Case Generator"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    # Authentication settings
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # Google Cloud settings
    google_cloud_project_id: Optional[str] = "drfirst-business-case-gen"  # Correct project ID
    google_application_credentials: Optional[str] = None
    
    # Firebase settings
    firebase_project_id: Optional[str] = "drfirst-business-case-gen"  # Same as Google Cloud project
    firebase_api_key: Optional[str] = None
    
    # Firestore settings
    firestore_collection_users: str = "users"
    firestore_collection_business_cases: str = "business_cases"
    firestore_collection_jobs: str = "jobs"
    
    # VertexAI settings
    vertex_ai_location: str = "us-central1"
    vertex_ai_model_name: str = "gemini-2.0-flash-lite"  # Current available model, replacement for text-bison
    vertex_ai_temperature: float = 0.6
    vertex_ai_max_tokens: int = 4096
    vertex_ai_top_p: float = 0.9
    vertex_ai_top_k: int = 40
    
    # CORS settings
    backend_cors_origins: list = [
        "http://localhost:4000",  # Frontend development
        "https://localhost:4000",
    ]

# Global settings instance
settings = Settings() 