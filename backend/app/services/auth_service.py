"""
Authentication service for Google Cloud Identity Platform integration
"""

import logging
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import auth, credentials
from app.core.config import settings
from app.core.logging_config import log_error_with_context
import os
import json

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication with Google Cloud Identity Platform"""

    def __init__(self):
        self._initialized = False
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not self._initialized and not firebase_admin._apps:
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

                self._initialized = True
                logger.info(
                    f"✅ Firebase Admin SDK initialized successfully for project: {project_id}"
                )

            elif firebase_admin._apps:
                logger.info("📱 Firebase Admin SDK already initialized")
                self._initialized = True
                # Log details about existing app
                if firebase_admin._apps:
                    app = firebase_admin._apps.get(firebase_admin._DEFAULT_APP_NAME)
                    if app:
                        logger.info(f"📱 Existing app project ID: {app.project_id}")

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
            
            # Set initialized to False so we can provide helpful error messages
            self._initialized = False

    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
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
            decoded_token = auth.verify_id_token(id_token)
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

    @property
    def is_initialized(self) -> bool:
        """Check if Firebase is properly initialized"""
        return self._initialized


# Global auth service instance
auth_service = AuthService()
