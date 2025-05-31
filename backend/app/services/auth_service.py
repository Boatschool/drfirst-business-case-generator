"""
Authentication service for Google Cloud Identity Platform integration
"""

from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import auth, credentials
from app.core.config import settings
import os

class AuthService:
    """Service for handling authentication with Google Cloud Identity Platform"""
    
    def __init__(self):
        self._initialized = False
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not self._initialized and not firebase_admin._apps:
                # Initialize with service account credentials
                if os.path.exists(settings.google_application_credentials):
                    cred = credentials.Certificate(settings.google_application_credentials)
                    firebase_admin.initialize_app(cred, {
                        'projectId': settings.firebase_project_id,
                    })
                    self._initialized = True
                    print("✅ Firebase Admin SDK initialized successfully")
                else:
                    print(f"❌ Service account file not found: {settings.google_application_credentials}")
        except Exception as e:
            print(f"Firebase initialization error: {e}")
    
    async def verify_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Firebase ID token and return user information
        """
        try:
            if not self._initialized:
                return None
                
            decoded_token = auth.verify_id_token(id_token)
            return {
                'uid': decoded_token.get('uid'),
                'email': decoded_token.get('email'),
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture'),
                'email_verified': decoded_token.get('email_verified', False),
                'firebase': decoded_token
            }
        except auth.InvalidIdTokenError:
            print("Invalid ID token")
            return None
        except auth.ExpiredIdTokenError:
            print("ID token expired")
            return None
        except Exception as e:
            print(f"Token verification error: {e}")
            return None
    
    async def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by UID
        """
        try:
            if not self._initialized:
                return None
                
            user = auth.get_user(uid)
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'photo_url': user.photo_url,
                'email_verified': user.email_verified,
                'disabled': user.disabled,
                'metadata': {
                    'creation_timestamp': user.user_metadata.creation_timestamp,
                    'last_sign_in_timestamp': user.user_metadata.last_sign_in_timestamp
                }
            }
        except auth.UserNotFoundError:
            print(f"User not found: {uid}")
            return None
        except Exception as e:
            print(f"User retrieval error: {e}")
            return None
    
    async def create_custom_token(self, uid: str, additional_claims: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Create a custom token for a user
        """
        try:
            if not self._initialized:
                return None
                
            token = auth.create_custom_token(uid, additional_claims)
            return token.decode('utf-8')
        except Exception as e:
            print(f"Custom token creation error: {e}")
            return None
    
    async def revoke_refresh_tokens(self, uid: str) -> bool:
        """
        Revoke all refresh tokens for a user (signs them out of all sessions)
        """
        try:
            if not self._initialized:
                return False
                
            auth.revoke_refresh_tokens(uid)
            return True
        except Exception as e:
            print(f"Token revocation error: {e}")
            return False

# Global auth service instance
auth_service = AuthService() 