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
import asyncio
import json
import re
from typing import Optional, Dict, Any, Callable
from app.core.config import settings
from google.cloud import aiplatform
import vertexai.preview.generative_models as generative_models

logger = logging.getLogger(__name__)


class LLMParsingError(Exception):
    """Custom exception for LLM response parsing errors"""
    pass


class LLMTimeoutError(Exception):
    """Custom exception for LLM timeout errors"""
    pass


class VertexAIService:
    """
    Centralized service for Vertex AI initialization and management.
    
    This singleton service ensures that Vertex AI is initialized only once per
    application lifecycle, preventing conflicts and resource issues during
    server reloads. Also provides common LLM utility functions.
    """
    
    _instance: Optional['VertexAIService'] = None
    _initialized: bool = False
    _initialization_time: Optional[float] = None
    _initialization_count: int = 0
    _error_count: int = 0
    _last_error: Optional[str] = None

    # Default safety settings for all LLM calls
    DEFAULT_SAFETY_SETTINGS = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }
    
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

    @staticmethod
    def extract_json_from_text(text: str, log_raw_text: bool = True) -> Optional[Dict[str, Any]]:
        """
        Extract JSON object from text using regex pattern matching.
        Handles cases where LLM returns JSON surrounded by additional text.
        
        Args:
            text (str): The text containing JSON
            log_raw_text (bool): Whether to log the raw text on parsing errors
            
        Returns:
            Optional[Dict[str, Any]]: Parsed JSON object or None if parsing fails
        """
        if not text or not text.strip():
            logger.warning("🔍 [JSON-EXTRACT] Empty or None text provided")
            return None
            
        try:
            # First try to parse the entire text as JSON
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        try:
            # Extract JSON using regex - find the first complete JSON object
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
                return json.loads(json_text)
            else:
                logger.warning("🔍 [JSON-EXTRACT] No JSON object pattern found in text")
                if log_raw_text:
                    logger.debug(f"🔍 [JSON-EXTRACT] Raw text: {text[:500]}...")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"🔍 [JSON-EXTRACT] JSON parsing error: {str(e)}")
            if log_raw_text:
                logger.debug(f"🔍 [JSON-EXTRACT] Raw text: {text[:500]}...")
            return None

    @staticmethod
    def extract_json_array_from_text(text: str, log_raw_text: bool = True) -> Optional[list]:
        """
        Extract JSON array from text using regex pattern matching.
        
        Args:
            text (str): The text containing JSON array
            log_raw_text (bool): Whether to log the raw text on parsing errors
            
        Returns:
            Optional[list]: Parsed JSON array or None if parsing fails
        """
        if not text or not text.strip():
            logger.warning("🔍 [JSON-EXTRACT] Empty or None text provided")
            return None
            
        try:
            # First try to parse the entire text as JSON
            result = json.loads(text.strip())
            return result if isinstance(result, list) else None
        except json.JSONDecodeError:
            pass
        
        try:
            # Extract JSON array using regex
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
                result = json.loads(json_text)
                return result if isinstance(result, list) else None
            else:
                logger.warning("🔍 [JSON-EXTRACT] No JSON array pattern found in text")
                if log_raw_text:
                    logger.debug(f"🔍 [JSON-EXTRACT] Raw text: {text[:500]}...")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"🔍 [JSON-EXTRACT] JSON array parsing error: {str(e)}")
            if log_raw_text:
                logger.debug(f"🔍 [JSON-EXTRACT] Raw text: {text[:500]}...")
            return None

    @staticmethod
    async def generate_with_retry(
        model,
        prompt: str,
        generation_config: Dict[str, Any],
        model_name: str = "unknown",
        max_retries: int = 2,
        timeout_seconds: int = 120,
        safety_settings: Optional[Dict] = None,
        log_llm_call: Optional[Callable] = None,
        agent_name: str = "Unknown"
    ) -> Optional[str]:
        """
        Generate content with retry logic, exponential backoff, and timeout protection.
        
        Args:
            model: The Vertex AI GenerativeModel instance
            prompt (str): The prompt to send to the model
            generation_config (Dict[str, Any]): Generation configuration parameters
            model_name (str): Name of the model for logging
            max_retries (int): Maximum number of retry attempts (default: 2)
            timeout_seconds (int): Timeout for each generation attempt (default: 120)
            safety_settings (Optional[Dict]): Safety settings, uses defaults if None
            log_llm_call (Optional[Callable]): Function to log LLM interactions
            agent_name (str): Name of the calling agent for logging
            
        Returns:
            Optional[str]: Generated content or None if all attempts fail
            
        Raises:
            LLMTimeoutError: If all attempts timeout
            Exception: If non-recoverable error occurs
        """
        if safety_settings is None:
            safety_settings = VertexAIService.DEFAULT_SAFETY_SETTINGS
        
        last_error = None
        
        for attempt in range(1, max_retries + 2):  # +2 because range is exclusive and we want max_retries + 1 total attempts
            try:
                logger.info(f"🔄 [{agent_name}] LLM generation attempt {attempt}/{max_retries + 1}")
                
                llm_start_time = time.time()
                
                # Apply timeout to the actual Vertex AI call
                response = await asyncio.wait_for(
                    model.generate_content_async(
                        [prompt],
                        generation_config=generation_config,
                        safety_settings=safety_settings,
                        stream=False,
                    ),
                    timeout=timeout_seconds
                )
                
                llm_response_time_ms = (time.time() - llm_start_time) * 1000

                # Check if we got a valid response
                if response.candidates and response.candidates[0].content.parts:
                    content = response.candidates[0].content.parts[0].text.strip()
                    logger.info(f"✅ [{agent_name}] Successfully generated content ({len(content)} characters)")
                    
                    # Log successful LLM interaction
                    if log_llm_call:
                        log_llm_call(
                            model_name=model_name,
                            prompt=prompt,
                            parameters=generation_config,
                            response=content,
                            response_time_ms=llm_response_time_ms
                        )
                    
                    return content
                else:
                    error_msg = f"No content generated on attempt {attempt}"
                    logger.warning(f"⚠️ [{agent_name}] {error_msg}")
                    
                    # Log LLM interaction with no content
                    if log_llm_call:
                        log_llm_call(
                            model_name=model_name,
                            prompt=prompt,
                            parameters=generation_config,
                            response_time_ms=llm_response_time_ms,
                            error=error_msg
                        )
                    
                    last_error = Exception(error_msg)

            except asyncio.TimeoutError as e:
                error_msg = f"LLM call timed out after {timeout_seconds}s on attempt {attempt}"
                logger.error(f"⏰ [{agent_name}] {error_msg}")
                
                # Log timeout error
                if log_llm_call:
                    log_llm_call(
                        model_name=model_name,
                        prompt=prompt,
                        parameters=generation_config,
                        error=error_msg
                    )
                
                last_error = LLMTimeoutError(error_msg)
                
            except Exception as e:
                error_msg = f"Error on attempt {attempt}: {str(e)}"
                logger.error(f"❌ [{agent_name}] {error_msg}")
                
                # Log general error
                if log_llm_call:
                    log_llm_call(
                        model_name=model_name,
                        prompt=prompt,
                        parameters=generation_config,
                        error=str(e)
                    )
                
                last_error = e
                
                # Don't retry on certain non-recoverable errors
                if "permission" in str(e).lower() or "authentication" in str(e).lower():
                    logger.error(f"❌ [{agent_name}] Non-recoverable error, not retrying: {str(e)}")
                    raise e
            
            # Apply exponential backoff before retry (except on last attempt)
            if attempt <= max_retries:
                backoff_seconds = 2 ** attempt
                logger.info(f"⏳ [{agent_name}] Waiting {backoff_seconds}s before retry...")
                await asyncio.sleep(backoff_seconds)
        
        # All attempts failed
        if isinstance(last_error, LLMTimeoutError):
            raise LLMTimeoutError(f"LLM generation timed out after {max_retries + 1} attempts")
        elif last_error:
            raise last_error
        else:
            raise Exception(f"LLM generation failed after {max_retries + 1} attempts with unknown error")

    @staticmethod
    def truncate_content(content: str, max_length: int, truncation_message: str = "\n\n[Content truncated for processing...]") -> tuple[str, bool]:
        """
        Truncate content to fit within token/character limits.
        
        Args:
            content (str): Content to potentially truncate
            max_length (int): Maximum allowed length
            truncation_message (str): Message to append when content is truncated
            
        Returns:
            tuple[str, bool]: (truncated_content, was_truncated)
        """
        if not content:
            return "", False
            
        if len(content) <= max_length:
            return content, False
        
        # Truncate and add message
        truncated = content[:max_length - len(truncation_message)] + truncation_message
        return truncated, True


# Global singleton instance
vertex_ai_service = VertexAIService()
logger.info("🤖 [VERTEX-AI] 🌟 VertexAI service singleton created") 