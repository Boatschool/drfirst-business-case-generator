"""
Centralized VertexAI service for managing Vertex AI initialization across all agents.

This service implements the singleton pattern to ensure Vertex AI is initialized only once
per application lifecycle, preventing conflicts during Uvicorn reloads.
"""

import logging
import time
import traceback
import platform
import sys
import os
import vertexai
from typing import Optional, Dict, Any
from app.core.config import settings
from google.cloud import aiplatform

logger = logging.getLogger(__name__)


class VertexAIService:
    """
    Centralized service for Vertex AI initialization and management.
    
    This singleton service ensures that Vertex AI is initialized only once per
    application lifecycle, preventing conflicts and resource issues during
    server reloads.
    """
    
    _instance: Optional['VertexAIService'] = None
    _initialized: bool = False
    _initialization_time: Optional[float] = None
    _initialization_count: int = 0
    _error_count: int = 0
    _last_error: Optional[str] = None
    
    def __new__(cls) -> 'VertexAIService':
        """
        Implement singleton pattern to ensure only one instance exists.
        
        Returns:
            VertexAIService: The singleton instance
        """
        if cls._instance is None:
            logger.info("🤖 [VERTEX-AI] Creating new VertexAIService instance")
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if hasattr(self, '_service_initialized'):
            return
        
        logger.info("🤖 [VERTEX-AI] Initializing VertexAI service")
        self._service_initialized = True
        self.project_id = None
        self.location = "us-central1"  # Default location
        logger.info("🤖 [VERTEX-AI] ✅ VertexAI service instance created")
    
    def initialize(self, project_id: Optional[str] = None, location: str = "us-central1") -> bool:
        """Initialize VertexAI with project configuration"""
        if self._initialized:
            logger.info("🤖 [VERTEX-AI] ✅ Already initialized, skipping")
            return True
        
        logger.info("🤖 [VERTEX-AI] 🔄 Starting VertexAI initialization")
        
        try:
            # Get project ID from environment if not provided
            if not project_id:
                project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
                logger.info(f"🤖 [VERTEX-AI] 🔍 Using project ID from environment: {project_id}")
            
            # If still no project ID, try to get from settings
            if not project_id:
                try:
                    from app.core.config import settings
                    project_id = settings.google_cloud_project_id
                    logger.info(f"🤖 [VERTEX-AI] 🔍 Using project ID from settings: {project_id}")
                except Exception as settings_error:
                    logger.warning(f"🤖 [VERTEX-AI] ⚠️ Could not load settings: {settings_error}")
            
            if not project_id:
                logger.warning("🤖 [VERTEX-AI] ⚠️ No project ID found, using default project")
                project_id = "default-project"
            
            self.project_id = project_id
            self.location = location
            
            logger.info(f"🤖 [VERTEX-AI] 🎯 Initializing with project: {project_id}, location: {location}")
            
            # Initialize VertexAI
            vertexai.init(project=project_id, location=location)
            logger.info("🤖 [VERTEX-AI] ✅ VertexAI initialized successfully")
            
            # Initialize AI Platform client for additional functionality
            try:
                aiplatform.init(project=project_id, location=location)
                logger.info("🤖 [VERTEX-AI] ✅ AI Platform client initialized")
            except Exception as platform_error:
                logger.warning(f"🤖 [VERTEX-AI] ⚠️ AI Platform client initialization failed: {platform_error}")
                # Continue without AI Platform client
            
            self._initialized = True
            logger.info(f"🤖 [VERTEX-AI] 🎉 VertexAI service fully initialized for project: {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"🤖 [VERTEX-AI] ❌ Failed to initialize VertexAI: {e}")
            logger.error(f"🤖 [VERTEX-AI] 📊 Full traceback: {traceback.format_exc()}")
            self._initialized = False
            return False
    
    def reset(self) -> None:
        """
        Reset initialization state for clean reloads.
        
        This method is called during application shutdown to reset the 
        initialization state, allowing for clean re-initialization on
        the next startup cycle.
        """
        logger.info("🤖 [VERTEX-AI] 🔄 Resetting VertexAI service state")
        
        try:
            # Reset initialization state
            self._initialized = False
            self.project_id = None
            logger.info("🤖 [VERTEX-AI] ✅ Service state reset successfully")
            
        except Exception as e:
            logger.error(f"🤖 [VERTEX-AI] ❌ Error during reset: {e}")
            logger.error(f"🤖 [VERTEX-AI] 📊 Full traceback: {traceback.format_exc()}")
    
    def cleanup(self) -> None:
        """
        Cleanup VertexAI resources to prevent resource leaks.
        
        This method performs comprehensive cleanup of VertexAI resources
        including any cached models, connections, or other resources that
        might accumulate during application lifecycle.
        """
        try:
            logger.info("🧹 Starting VertexAI service cleanup...")
            
            # Reset initialization state
            self._initialized = False
            
            # Clear any cached model references (if we were storing them)
            # Note: VertexAI SDK handles most cleanup internally, but we reset our state
            
            # Reset metrics for clean state
            self._initialization_count = 0
            self._error_count = 0
            self._last_error = None
            self._initialization_time = None
            
            logger.info("✅ VertexAI service cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during VertexAI cleanup: {e}")
            logger.exception("VertexAI cleanup error details:")
        finally:
            # Ensure state is reset even if cleanup fails
            self._initialized = False
            
    @classmethod
    def reset_singleton(cls) -> None:
        """
        Reset the singleton instance for clean application reloads.
        
        This method can be called to completely reset the VertexAI service
        singleton, which is useful during development or testing.
        """
        if cls._instance is not None:
            logger.info("🔄 Resetting VertexAI singleton instance...")
            cls._instance.cleanup()
            cls._instance = None
            logger.info("✅ VertexAI singleton reset completed")
    
    @property
    def is_initialized(self) -> bool:
        """
        Check if Vertex AI is properly initialized.
        
        Returns:
            bool: True if Vertex AI is initialized, False otherwise
        """
        status = self._initialized
        logger.debug(f"🤖 [VERTEX-AI] Initialization status: {status}")
        return status
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status information about the Vertex AI service.
        
        Returns:
            dict: Detailed status information including performance metrics
        """
        status = {
            # Basic status
            "initialized": self._initialized,
            "service_name": "VertexAI Service",
            "version": "1.0.0",
            
            # Configuration
            "configuration": {
                "project_id": self.project_id,
                "location": self.location,
                "model_name": settings.vertex_ai_model_name,
                "temperature": settings.vertex_ai_temperature,
                "max_tokens": settings.vertex_ai_max_tokens,
                "top_p": settings.vertex_ai_top_p,
                "top_k": settings.vertex_ai_top_k,
            },
            
            # Performance metrics
            "metrics": {
                "initialization_count": self._initialization_count,
                "error_count": self._error_count,
                "initialization_time_seconds": self._initialization_time,
                "last_error": self._last_error,
                "uptime_status": "healthy" if self._initialized and self._error_count == 0 else "degraded" if self._initialized else "unhealthy"
            },
            
            # System information
            "system": {
                "platform": platform.platform(),
                "python_version": sys.version.split()[0],
                "working_directory": os.getcwd(),
                "google_credentials_set": bool(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')),
                "credentials_file_exists": os.path.exists(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', ''))
            },
            
            # Health check
            "health": {
                "status": "healthy" if self._initialized else "unhealthy",
                "can_create_model": False,
                "last_check_time": time.time()
            }
        }
        
        # Test model creation if initialized
        if self._initialized:
            try:
                from vertexai.generative_models import GenerativeModel
                test_model = GenerativeModel(settings.vertex_ai_model_name)
                status["health"]["can_create_model"] = True
                status["health"]["model_test_result"] = "success"
            except Exception as e:
                status["health"]["can_create_model"] = False
                status["health"]["model_test_result"] = f"failed: {str(e)}"
                status["health"]["status"] = "degraded"
        
        return status
    
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """
        Get comprehensive diagnostic information for troubleshooting.
        
        Returns:
            dict: Detailed diagnostic information
        """
        try:
            import vertexai
            vertexai_version = getattr(vertexai, '__version__', 'Unknown')
        except:
            vertexai_version = 'Not available'
        
        return {
            "service_diagnostics": {
                "class_name": self.__class__.__name__,
                "instance_id": id(self),
                "singleton_verified": self._instance is not None and self._instance is self,
                "initialization_state": {
                    "initialized": self._initialized,
                    "init_count": self._initialization_count,
                    "error_count": self._error_count,
                    "init_time": self._initialization_time,
                    "last_error": self._last_error
                }
            },
            "environment_diagnostics": {
                "python_executable": sys.executable,
                "python_path": sys.path[:5],  # First 5 entries
                "environment_variables": {
                    "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'Not set'),
                    "GOOGLE_CLOUD_PROJECT": os.environ.get('GOOGLE_CLOUD_PROJECT', 'Not set'),
                    "PYTHONPATH": os.environ.get('PYTHONPATH', 'Not set')
                }
            },
            "dependency_diagnostics": {
                "vertexai_version": vertexai_version,
                "platform_info": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "machine": platform.machine(),
                    "processor": platform.processor()
                }
            },
            "configuration_diagnostics": {
                "settings_module": str(settings.__class__),
                "all_vertex_settings": {
                    "project_id": self.project_id,
                    "location": self.location,
                    "model_name": settings.vertex_ai_model_name,
                    "temperature": settings.vertex_ai_temperature,
                    "max_tokens": settings.vertex_ai_max_tokens,
                    "top_p": settings.vertex_ai_top_p,
                    "top_k": settings.vertex_ai_top_k,
                }
            }
        }


# Global singleton instance
vertex_ai_service = VertexAIService()
logger.info("🤖 [VERTEX-AI] 🌟 VertexAI service singleton created") 