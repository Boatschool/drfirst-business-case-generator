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
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self) -> None:
        """
        Initialize Vertex AI with comprehensive logging and diagnostics.
        
        This method is safe to call multiple times - it will only initialize
        Vertex AI once per application lifecycle.
        
        Raises:
            Exception: If Vertex AI initialization fails
        """
        start_time = time.time()
        self._initialization_count += 1
        
        logger.info(f"🤖 VertexAI Initialization Request #{self._initialization_count}")
        logger.info(f"📊 Current Status: Initialized={self._initialized}")
        
        if self._initialized:
            total_duration = time.time() - start_time
            logger.info(f"✅ VertexAI already initialized (checked in {total_duration:.3f}s)")
            logger.info(f"📊 Service Stats: Init Count={self._initialization_count}, Errors={self._error_count}")
            return
        
        if not self._initialized:
            try:
                # Log system environment
                logger.info(f"🖥️  System Environment:")
                logger.info(f"  - Platform: {platform.platform()}")
                logger.info(f"  - Python Version: {sys.version}")
                logger.info(f"  - Working Directory: {os.getcwd()}")
                logger.info(f"  - Python Path: {sys.path[:3]}...")  # First 3 entries
                
                # Log dependency versions
                try:
                    import vertexai
                    logger.info(f"  - VertexAI Version: {vertexai.__version__ if hasattr(vertexai, '__version__') else 'Unknown'}")
                except:
                    logger.warning("  - VertexAI Version: Could not determine")
                
                project_id = settings.google_cloud_project_id or "drfirst-business-case-gen"
                location = settings.vertex_ai_location
                
                logger.info(f"🔧 VertexAI Configuration:")
                logger.info(f"  - Project ID: {project_id}")
                logger.info(f"  - Location: {location}")
                logger.info(f"  - Model: {settings.vertex_ai_model_name}")
                logger.info(f"  - Temperature: {settings.vertex_ai_temperature}")
                logger.info(f"  - Max Tokens: {settings.vertex_ai_max_tokens}")
                logger.info(f"  - Top P: {settings.vertex_ai_top_p}")
                logger.info(f"  - Top K: {settings.vertex_ai_top_k}")
                
                # Check environment variables
                logger.info(f"🔍 Environment Check:")
                google_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                if google_creds:
                    logger.info(f"  - GOOGLE_APPLICATION_CREDENTIALS: {google_creds}")
                    logger.info(f"  - Credentials file exists: {os.path.exists(google_creds) if google_creds else False}")
                else:
                    logger.info("  - GOOGLE_APPLICATION_CREDENTIALS: Not set (using default credentials)")
                
                logger.info(f"⏳ Starting VertexAI initialization...")
                init_start = time.time()
                
                vertexai.init(project=project_id, location=location)
                
                init_duration = time.time() - init_start
                self._initialization_time = init_duration
                self._initialized = True
                
                total_duration = time.time() - start_time
                
                logger.info(f"✅ VertexAI initialized successfully!")
                logger.info(f"⏱️  Timing Information:")
                logger.info(f"  - VertexAI Init Time: {init_duration:.3f} seconds")
                logger.info(f"  - Total Setup Time: {total_duration:.3f} seconds")
                logger.info(f"  - Initialization Count: {self._initialization_count}")
                
                # Verify initialization by testing basic functionality
                try:
                    from vertexai.generative_models import GenerativeModel
                    test_model = GenerativeModel(settings.vertex_ai_model_name)
                    logger.info(f"✅ Model creation test successful: {settings.vertex_ai_model_name}")
                except Exception as model_error:
                    logger.warning(f"⚠️ Model creation test failed: {model_error}")
                
            except Exception as e:
                error_duration = time.time() - start_time
                self._error_count += 1
                self._last_error = str(e)
                
                logger.error(f"❌ VertexAI initialization failed!")
                logger.error(f"❌ Error #{self._error_count}: {type(e).__name__}: {str(e)}")
                logger.error(f"⏱️  Failed after {error_duration:.3f} seconds")
                
                # Enhanced error diagnostics
                logger.error(f"🔍 Detailed Error Information:")
                logger.error(f"  - Error Type: {type(e)}")
                logger.error(f"  - Error Message: {str(e)}")
                logger.error(f"  - Project ID Used: {project_id}")
                logger.error(f"  - Location Used: {location}")
                
                # Log full traceback for debugging
                logger.error(f"📋 Full Traceback:")
                for line in traceback.format_exc().splitlines():
                    logger.error(f"  {line}")
                
                # Provide troubleshooting hints
                logger.error(f"💡 Troubleshooting Hints:")
                logger.error(f"  - Ensure GOOGLE_APPLICATION_CREDENTIALS is set correctly")
                logger.error(f"  - Verify project '{project_id}' has Vertex AI API enabled")
                logger.error(f"  - Check if location '{location}' is valid for your project")
                logger.error(f"  - Ensure billing is enabled for the project")
                
                self._initialized = False
                raise
        else:
            total_duration = time.time() - start_time
            logger.info(f"✅ VertexAI already initialized (checked in {total_duration:.3f}s)")
            logger.info(f"📊 Service Stats: Init Count={self._initialization_count}, Errors={self._error_count}")
    
    def reset(self) -> None:
        """
        Reset initialization state for clean reloads.
        
        This method is called during application shutdown to reset the 
        initialization state, allowing for clean re-initialization on
        the next startup cycle.
        """
        self._initialized = False
        logger.info("🔄 Vertex AI service reset for reload")
    
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
        return self._initialized
    
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
                "project_id": settings.google_cloud_project_id,
                "location": settings.vertex_ai_location,
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
                    "project_id": settings.google_cloud_project_id,
                    "location": settings.vertex_ai_location,
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