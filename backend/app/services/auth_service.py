"""
Authentication service for Google Cloud Identity Platform integration
"""

import logging
import time
import traceback
import platform
import sys
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import auth, credentials
from app.core.config import settings
from app.core.logging_config import log_error_with_context
import os
import json
import asyncio
import asyncio

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication with Google Cloud Identity Platform"""

    def __init__(self):
        self._initialized = False
        # Remove automatic initialization - will be done by lifecycle manager
        # self._initialize_firebase()

    def _initialize_firebase(self):
        """
        Initialize Firebase Admin SDK with robust handling of existing/stale apps.
        
        This method implements proper cleanup of stale Firebase apps and health checking
        to prevent re-initialization conflicts during Uvicorn reloads.
        """
        if self._initialized:
            logger.info("✅ Firebase already initialized, skipping")
            return
            
        try:
            logger.info("🚀 Starting Firebase Admin SDK initialization...")
            
            # Check if already initialized and working
            if firebase_admin._apps and firebase_admin._DEFAULT_APP_NAME in firebase_admin._apps:
                app = firebase_admin._apps[firebase_admin._DEFAULT_APP_NAME]
                try:
                    # Test if app is still healthy by accessing project_id
                    if app and app.project_id:
                        logger.info(f"✅ Firebase already initialized and healthy (project: {app.project_id})")
                        self._initialized = True
                        return
                except Exception as e:
                    logger.warning(f"⚠️ Existing Firebase app unhealthy: {e}")
            
            # Clean up any stale apps before reinitializing
            if firebase_admin._apps:
                logger.info(f"🧹 Found {len(firebase_admin._apps)} existing Firebase app(s), cleaning up...")
                for app_name in list(firebase_admin._apps.keys()):
                    try:
                        firebase_admin.delete_app(firebase_admin._apps[app_name])
                        logger.info(f"✅ Cleaned up stale Firebase app: {app_name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to cleanup stale Firebase app '{app_name}': {e}")
            
            logger.info("🚀 Initializing Firebase Admin SDK...")
            
            # Debug: Log environment information
            logger.info(f"📋 Environment debug info:")
            logger.info(f"  - Firebase Project ID: {settings.firebase_project_id}")
            logger.info(f"  - Google Cloud Project ID: {settings.google_cloud_project_id}")
            logger.info(f"  - GOOGLE_APPLICATION_CREDENTIALS env var: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
            logger.info(f"  - Settings credentials path: {settings.google_application_credentials}")

            # Try to initialize with service account credentials
            cred = None

            # Method 1: Try to use service account file if it exists
            if settings.google_application_credentials and os.path.exists(
                settings.google_application_credentials
            ):
                logger.info(
                    f"📁 Using service account file: {settings.google_application_credentials}"
                )
                try:
                    cred = credentials.Certificate(
                        settings.google_application_credentials
                    )
                    logger.info("✅ Service account credentials loaded successfully")
                except Exception as e:
                    logger.error(f"❌ Failed to load service account file: {e}")

            # Method 2: Try to use GOOGLE_APPLICATION_CREDENTIALS environment variable
            elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                if os.path.exists(cred_path):
                    logger.info(f"📁 Using service account from env: {cred_path}")
                    try:
                        cred = credentials.Certificate(cred_path)
                        logger.info("✅ Environment service account credentials loaded successfully")
                    except Exception as e:
                        logger.error(f"❌ Failed to load environment service account: {e}")
                else:
                    logger.error(f"❌ Service account file not found at: {cred_path}")

            # Method 3: Try to use default credentials (for Cloud Run)
            else:
                logger.info("🔧 Using default credentials (suitable for Cloud Run)")
                try:
                    cred = credentials.ApplicationDefault()
                    logger.info("✅ Default application credentials loaded successfully")
                except Exception as default_cred_error:
                    logger.error(
                        f"❌ Failed to use default credentials: {default_cred_error}"
                    )
                    logger.error(f"❌ Default credentials error type: {type(default_cred_error)}")

                    # Method 4: Use certificate data directly if available
                    if settings.firebase_project_id:
                        logger.info(
                            "🔧 Attempting to initialize without explicit credentials..."
                        )
                        cred = None  # Will use default application credentials

            # Initialize Firebase app
            project_id = settings.firebase_project_id or settings.google_cloud_project_id
            logger.info(f"🔧 Initializing Firebase with project ID: {project_id}")
            
            if cred:
                logger.info("🔑 Initializing with explicit credentials")
                firebase_admin.initialize_app(
                    cred,
                    {
                        "projectId": project_id,
                    },
                )
            else:
                # Initialize with default credentials
                logger.info("🔑 Initializing with default credentials")
                firebase_admin.initialize_app(
                    options={
                        "projectId": project_id,
                    }
                )

            # Verify the app was initialized correctly
            app = firebase_admin._apps.get(firebase_admin._DEFAULT_APP_NAME)
            if app and app.project_id:
                self._initialized = True
                logger.info(
                    f"✅ Firebase Admin SDK initialized successfully for project: {project_id}"
                )
            else:
                logger.error("❌ Firebase app initialization appeared to succeed but app is not accessible")
                self._initialized = False

        except Exception as e:
            logger.error(f"❌ Firebase initialization error: {e}")
            logger.error(f"❌ Error type: {type(e)}")
            logger.error(f"❌ Error details: {str(e)}")
            logger.info("🔍 Debug info:")
            logger.info(f"  - firebase_project_id: {settings.firebase_project_id}")
            logger.info(f"  - google_cloud_project_id: {settings.google_cloud_project_id}")
            logger.info(
                f"  - google_application_credentials: {settings.google_application_credentials}"
            )
            logger.info(
                f"  - GOOGLE_APPLICATION_CREDENTIALS env: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}"
            )
            
            # Try to provide more specific error guidance
            if "Permission denied" in str(e) or "403" in str(e):
                logger.error("🚨 LIKELY CAUSE: Service account lacks Firebase Admin permissions")
                logger.error("🛠️  SOLUTION: Add 'Firebase Admin SDK Administrator Service Agent' role to the service account")
            elif "not found" in str(e) or "404" in str(e):
                logger.error("🚨 LIKELY CAUSE: Project ID not found or incorrect")
                logger.error("🛠️  SOLUTION: Verify the Firebase project ID is correct")
            elif "credential" in str(e).lower():
                logger.error("🚨 LIKELY CAUSE: Service account credentials issue")
                logger.error("🛠️  SOLUTION: Check service account key file or Cloud Run service account configuration")
            elif "already exists" in str(e).lower():
                logger.error("🚨 LIKELY CAUSE: Firebase app already exists (cleanup failed)")
                logger.error("🛠️  SOLUTION: This should be handled by cleanup logic, consider restarting server")
            
            # Set initialized to False so we can provide helpful error messages
            self._initialized = False

    async def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a Firebase ID token and return decoded claims

        Args:
            id_token: The Firebase ID token to verify

        Returns:
            Decoded token claims if valid, None otherwise
        """
        if not self._initialized:
            logger.error("Firebase not initialized, cannot verify token")
            return None

        try:
            logger.debug(
                "Verifying Firebase ID token",
                extra={'token_length': len(id_token)}
            )
            decoded_token = await asyncio.to_thread(auth.verify_id_token, id_token)
            logger.info(
                "Token verification successful",
                extra={
                    'user_email': decoded_token.get('email', 'unknown'),
                    'user_uid': decoded_token.get('uid', 'unknown'),
                    'email_verified': decoded_token.get('email_verified', False)
                }
            )
            return decoded_token

        except auth.ExpiredIdTokenError as e:
            logger.warning("Token verification failed: token expired")
            return None
        except auth.InvalidIdTokenError as e:
            logger.warning(
                "Token verification failed: invalid token",
                extra={'error_details': str(e)}
            )
            return None
        except auth.RevokedIdTokenError as e:
            logger.warning("Token verification failed: token revoked")
            return None
        except Exception as e:
            log_error_with_context(
                logger,
                "Unexpected error during token verification",
                e,
                {'token_length': len(id_token)}
            )
            return None

    def get_user_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by UID

        Args:
            uid: Firebase user UID

        Returns:
            User record if found, None otherwise
        """
        if not self._initialized:
            logger.info("❌ Firebase not initialized, cannot get user")
            return None

        try:
            user_record = auth.get_user(uid)
            return {
                "uid": user_record.uid,
                "email": user_record.email,
                "email_verified": user_record.email_verified,
                "display_name": user_record.display_name,
                "photo_url": user_record.photo_url,
                "disabled": user_record.disabled,
            }
        except auth.UserNotFoundError:
            logger.info(f"❌ User not found: {uid}")
            return None
        except Exception as e:
            logger.info(f"❌ Error getting user: {e}")
            return None

    async def revoke_refresh_tokens(self, uid: str) -> bool:
        """
        Revoke all refresh tokens for a user, effectively signing them out of all sessions.

        Args:
            uid: Firebase user UID

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            logger.error("Firebase not initialized, cannot revoke tokens")
            return False

        try:
            logger.info(f"Revoking refresh tokens for user: {uid}")
            await asyncio.to_thread(auth.revoke_refresh_tokens, uid)
            logger.info(f"Successfully revoked refresh tokens for user: {uid}")
            return True
        except Exception as e:
            log_error_with_context(
                logger,
                f"Failed to revoke refresh tokens for user {uid}",
                e,
                {'user_uid': uid}
            )
            return False

    def reset(self):
        """
        Reset service state for clean reloads.
        
        This method is called by the lifecycle manager during server reloads
        to reset the AuthService initialization state.
        """
        self._initialized = False
        logger.info("🔄 AuthService reset for reload")
    
    def cleanup(self):
        """
        Cleanup resources during shutdown.
        
        This method properly cleans up Firebase Admin SDK apps and resources
        to prevent resource leaks and ensure clean shutdown.
        """
        logger.info("🧹 Starting AuthService cleanup...")
        
        try:
            if firebase_admin._apps:
                logger.info(f"🧹 Cleaning up {len(firebase_admin._apps)} Firebase app(s)...")
                for app_name in list(firebase_admin._apps.keys()):
                    try:
                        firebase_admin.delete_app(firebase_admin._apps[app_name])
                        logger.info(f"✅ Cleaned up Firebase app: {app_name}")
                    except Exception as e:
                        logger.error(f"❌ Error cleaning up Firebase app '{app_name}': {e}")
            else:
                logger.info("ℹ️ No Firebase apps to clean up")
                
        except Exception as e:
            logger.error(f"❌ Error during Firebase cleanup: {e}")
        finally:
            self._initialized = False
            logger.info("✅ AuthService cleanup completed")

    @property
    def is_initialized(self) -> bool:
        """Check if Firebase is properly initialized"""
        return self._initialized
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status information about the Auth service.
        
        Returns:
            dict: Detailed status information including Firebase app health
        """
        status = {
            # Basic status
            "initialized": self._initialized,
            "service_name": "Firebase Auth Service",
            "version": "1.0.0",
            
            # Configuration
            "configuration": {
                "firebase_project_id": settings.firebase_project_id,
                "google_cloud_project_id": settings.google_cloud_project_id,
                "credentials_path": settings.google_application_credentials,
                "environment_credentials": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")),
            },
            
            # Firebase app information
            "firebase_apps": {
                "total_apps": len(firebase_admin._apps) if firebase_admin._apps else 0,
                "app_names": list(firebase_admin._apps.keys()) if firebase_admin._apps else [],
                "default_app_exists": firebase_admin._DEFAULT_APP_NAME in firebase_admin._apps if firebase_admin._apps else False
            },
            
            # System information
            "system": {
                "platform": platform.platform(),
                "python_version": sys.version.split()[0],
                "working_directory": os.getcwd(),
                "credentials_file_exists": os.path.exists(settings.google_application_credentials) if settings.google_application_credentials else False,
                "env_credentials_file_exists": os.path.exists(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")) if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") else False
            },
            
            # Health check
            "health": {
                "status": "healthy" if self._initialized else "unhealthy",
                "can_access_auth": False,
                "firebase_app_healthy": False,
                "last_check_time": time.time()
            }
        }
        
        # Test Firebase app health if initialized
        if self._initialized and firebase_admin._apps:
            try:
                default_app = firebase_admin._apps.get(firebase_admin._DEFAULT_APP_NAME)
                if default_app:
                    # Test project ID access
                    project_id = default_app.project_id
                    status["health"]["firebase_app_healthy"] = True
                    status["health"]["project_id"] = project_id
                    
                    # Test auth functionality
                    try:
                        # This will fail gracefully if auth is not accessible
                        from firebase_admin import auth
                        status["health"]["can_access_auth"] = True
                        status["health"]["auth_test_result"] = "accessible"
                    except Exception as auth_error:
                        status["health"]["can_access_auth"] = False
                        status["health"]["auth_test_result"] = f"failed: {str(auth_error)}"
                        status["health"]["status"] = "degraded"
                        
            except Exception as e:
                status["health"]["firebase_app_healthy"] = False
                status["health"]["app_test_result"] = f"failed: {str(e)}"
                status["health"]["status"] = "unhealthy"
        
        return status
    
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """
        Get comprehensive diagnostic information for troubleshooting.
        
        Returns:
            dict: Detailed diagnostic information
        """
        try:
            import firebase_admin
            firebase_version = getattr(firebase_admin, '__version__', 'Unknown')
        except:
            firebase_version = 'Not available'
        
        return {
            "service_diagnostics": {
                "class_name": self.__class__.__name__,
                "instance_id": id(self),
                "initialization_state": {
                    "initialized": self._initialized,
                    "firebase_apps_count": len(firebase_admin._apps) if firebase_admin._apps else 0,
                    "default_app_name": firebase_admin._DEFAULT_APP_NAME,
                    "available_apps": list(firebase_admin._apps.keys()) if firebase_admin._apps else []
                }
            },
            "environment_diagnostics": {
                "python_executable": sys.executable,
                "python_path": sys.path[:5],  # First 5 entries
                "environment_variables": {
                    "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'Not set'),
                    "GOOGLE_CLOUD_PROJECT": os.environ.get('GOOGLE_CLOUD_PROJECT', 'Not set'),
                    "FIREBASE_PROJECT_ID": os.environ.get('FIREBASE_PROJECT_ID', 'Not set'),
                    "PYTHONPATH": os.environ.get('PYTHONPATH', 'Not set')
                }
            },
            "dependency_diagnostics": {
                "firebase_admin_version": firebase_version,
                "platform_info": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "machine": platform.machine(),
                    "processor": platform.processor()
                }
            },
            "configuration_diagnostics": {
                "settings_module": str(settings.__class__),
                "firebase_settings": {
                    "firebase_project_id": settings.firebase_project_id,
                    "google_cloud_project_id": settings.google_cloud_project_id,
                    "credentials_path": settings.google_application_credentials,
                    "credentials_file_readable": self._check_credentials_file_readable(),
                }
            },
            "file_diagnostics": {
                "credentials_file_analysis": self._analyze_credentials_file()
            }
        }
    
    def _check_credentials_file_readable(self) -> Dict[str, Any]:
        """Check if credentials file is readable and valid JSON"""
        result = {"readable": False, "valid_json": False, "has_required_fields": False}
        
        # Check settings file
        if settings.google_application_credentials:
            try:
                if os.path.exists(settings.google_application_credentials):
                    result["readable"] = True
                    with open(settings.google_application_credentials, 'r') as f:
                        cred_data = json.load(f)
                        result["valid_json"] = True
                        required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
                        result["has_required_fields"] = all(field in cred_data for field in required_fields)
                        result["credential_type"] = cred_data.get("type", "unknown")
                        result["project_id"] = cred_data.get("project_id", "unknown")
                        result["client_email"] = cred_data.get("client_email", "unknown")
            except Exception as e:
                result["error"] = str(e)
        
        return result
    
    def _analyze_credentials_file(self) -> Dict[str, Any]:
        """Analyze credentials file and environment setup"""
        analysis = {
            "settings_file": None,
            "environment_file": None,
            "recommendation": "unknown"
        }
        
        # Analyze settings file
        if settings.google_application_credentials:
            analysis["settings_file"] = {
                "path": settings.google_application_credentials,
                "exists": os.path.exists(settings.google_application_credentials),
                "readable": self._check_credentials_file_readable()
            }
        
        # Analyze environment file
        env_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if env_creds:
            analysis["environment_file"] = {
                "path": env_creds,
                "exists": os.path.exists(env_creds),
                "readable": env_creds == settings.google_application_credentials
            }
        
        # Provide recommendation
        if analysis["settings_file"] and analysis["settings_file"]["exists"]:
            analysis["recommendation"] = "using_settings_file"
        elif analysis["environment_file"] and analysis["environment_file"]["exists"]:
            analysis["recommendation"] = "using_environment_file"
        elif os.getenv("GOOGLE_CLOUD_PROJECT"):
            analysis["recommendation"] = "using_default_credentials"
        else:
            analysis["recommendation"] = "no_credentials_found"
        
        return analysis


# Global auth service instance - lazy initialization
_auth_service_instance: Optional[AuthService] = None

def get_auth_service() -> AuthService:
    """Get the global auth service instance with lazy initialization"""
    global _auth_service_instance
    if _auth_service_instance is None:
        _auth_service_instance = AuthService()
    return _auth_service_instance