"""
Authentication service for Google Cloud Identity Platform integration
"""

from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import auth, credentials
from app.core.config import settings
import os
import json


class AuthService:
    """Service for handling authentication with Google Cloud Identity Platform"""

    def __init__(self):
        self._initialized = False
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not self._initialized and not firebase_admin._apps:
                print("🚀 Initializing Firebase Admin SDK...")

                # Try to initialize with service account credentials
                cred = None

                # Method 1: Try to use service account file if it exists
                if settings.google_application_credentials and os.path.exists(
                    settings.google_application_credentials
                ):
                    print(
                        f"📁 Using service account file: {settings.google_application_credentials}"
                    )
                    cred = credentials.Certificate(
                        settings.google_application_credentials
                    )

                # Method 2: Try to use GOOGLE_APPLICATION_CREDENTIALS environment variable
                elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                    if os.path.exists(cred_path):
                        print(f"📁 Using service account from env: {cred_path}")
                        cred = credentials.Certificate(cred_path)
                    else:
                        print(f"❌ Service account file not found at: {cred_path}")

                # Method 3: Try to use default credentials (for Cloud Run)
                else:
                    print("🔧 Using default credentials (suitable for Cloud Run)")
                    try:
                        cred = credentials.ApplicationDefault()
                    except Exception as default_cred_error:
                        print(
                            f"❌ Failed to use default credentials: {default_cred_error}"
                        )

                        # Method 4: Use certificate data directly if available
                        if settings.firebase_project_id:
                            print(
                                "🔧 Attempting to initialize without explicit credentials..."
                            )
                            cred = None  # Will use default application credentials

                # Initialize Firebase app
                if cred:
                    firebase_admin.initialize_app(
                        cred,
                        {
                            "projectId": settings.firebase_project_id
                            or settings.google_cloud_project_id,
                        },
                    )
                else:
                    # Initialize with default credentials
                    firebase_admin.initialize_app(
                        options={
                            "projectId": settings.firebase_project_id
                            or settings.google_cloud_project_id,
                        }
                    )

                self._initialized = True
                print(
                    f"✅ Firebase Admin SDK initialized successfully for project: {settings.firebase_project_id}"
                )

            elif firebase_admin._apps:
                print("📱 Firebase Admin SDK already initialized")
                self._initialized = True

        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            print("🔍 Debug info:")
            print(f"  - firebase_project_id: {settings.firebase_project_id}")
            print(f"  - google_cloud_project_id: {settings.google_cloud_project_id}")
            print(
                f"  - google_application_credentials: {settings.google_application_credentials}"
            )
            print(
                f"  - GOOGLE_APPLICATION_CREDENTIALS env: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}"
            )
            # Don't raise the error - allow the service to continue but log the issue

    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a Firebase ID token and return decoded claims

        Args:
            id_token: The Firebase ID token to verify

        Returns:
            Decoded token claims if valid, None otherwise
        """
        if not self._initialized:
            print("❌ Firebase not initialized, cannot verify token")
            return None

        try:
            print(f"🔍 Verifying ID token (length: {len(id_token)})")
            decoded_token = auth.verify_id_token(id_token)
            print(
                f"✅ Token verified for user: {decoded_token.get('email', 'unknown')}"
            )
            return decoded_token

        except auth.ExpiredIdTokenError:
            print("❌ Token has expired")
            return None
        except auth.InvalidIdTokenError as e:
            print(f"❌ Invalid token: {e}")
            return None
        except auth.RevokedIdTokenError:
            print("❌ Token has been revoked")
            return None
        except Exception as e:
            print(f"❌ Unexpected error verifying token: {e}")
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
            print("❌ Firebase not initialized, cannot get user")
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
            print(f"❌ User not found: {uid}")
            return None
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None

    @property
    def is_initialized(self) -> bool:
        """Check if Firebase is properly initialized"""
        return self._initialized


# Global auth service instance
auth_service = AuthService()
