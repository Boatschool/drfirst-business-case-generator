"""
User service for managing user documents in Firestore and role synchronization
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from google.cloud import firestore
from firebase_admin import auth
from app.core.config import settings
from app.models.firestore_models import User, UserRole


class UserService:
    """Service for managing users in Firestore and synchronizing roles with Firebase custom claims"""

    def __init__(self):
        self.db = None
        self._initialize_firestore()

    def _initialize_firestore(self):
        """Initialize Firestore client"""
        try:
            from app.core.dependencies import get_db
            self.db = get_db()
            print("✅ UserService: Firestore client initialized successfully")
        except Exception as e:
            print(f"❌ UserService: Failed to initialize Firestore client: {e}")

    async def get_user_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user document from Firestore by UID

        Args:
            uid: Firebase user UID

        Returns:
            User document if found, None otherwise
        """
        if not self.db:
            print("❌ UserService: Firestore not initialized")
            return None

        try:
            doc_ref = self.db.collection("users").document(uid)
            doc = await asyncio.to_thread(doc_ref.get)

            if doc.exists:
                user_data = doc.to_dict()
                user_data["uid"] = doc.id  # Ensure UID is included
                return user_data
            else:
                return None

        except Exception as e:
            print(f"❌ UserService: Error getting user {uid}: {e}")
            return None

    async def create_or_update_user(
        self,
        uid: str,
        email: str,
        display_name: Optional[str] = None,
        system_role: Optional[UserRole] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Create or update user document in Firestore

        Args:
            uid: Firebase user UID
            email: User email address
            display_name: User display name
            system_role: User system role (defaults to USER for new users)

        Returns:
            User document if successful, None otherwise
        """
        if not self.db:
            print("❌ UserService: Firestore not initialized")
            return None

        try:
            doc_ref = self.db.collection("users").document(uid)
            doc = await asyncio.to_thread(doc_ref.get)

            current_time = datetime.now(timezone.utc)

            if doc.exists:
                # Update existing user
                update_data = {
                    "email": email,
                    "updated_at": current_time,
                    "last_login": current_time,
                }

                if display_name is not None:
                    update_data["display_name"] = display_name

                if system_role is not None:
                    update_data["systemRole"] = system_role.value

                await asyncio.to_thread(doc_ref.update, update_data)

                # Get updated document
                updated_doc = await asyncio.to_thread(doc_ref.get)
                user_data = updated_doc.to_dict()
                user_data["uid"] = uid

                print(f"✅ UserService: Updated user {email}")
                return user_data
            else:
                # Create new user
                user_data = {
                    "uid": uid,
                    "email": email,
                    "display_name": display_name,
                    "systemRole": (system_role or UserRole.USER).value,
                    "created_at": current_time,
                    "updated_at": current_time,
                    "last_login": current_time,
                    "is_active": True,
                }

                await asyncio.to_thread(doc_ref.set, user_data)

                print(
                    f"✅ UserService: Created new user {email} with role {user_data['systemRole']}"
                )
                return user_data

        except Exception as e:
            print(f"❌ UserService: Error creating/updating user {uid}: {e}")
            return None

    async def update_user_role(self, uid: str, new_role: UserRole) -> bool:
        """
        Update user's system role in Firestore and sync to Firebase custom claims

        Args:
            uid: Firebase user UID
            new_role: New system role

        Returns:
            True if successful, False otherwise
        """
        if not self.db:
            print("❌ UserService: Firestore not initialized")
            return False

        try:
            # Update Firestore document
            doc_ref = self.db.collection("users").document(uid)
            update_data = {
                "systemRole": new_role.value,
                "updated_at": datetime.now(timezone.utc),
            }

            await asyncio.to_thread(doc_ref.update, update_data)

            # Sync to Firebase custom claims
            success = await self.sync_user_claims(uid)

            if success:
                print(f"✅ UserService: Updated user {uid} role to {new_role.value}")
                return True
            else:
                print(f"❌ UserService: Failed to sync claims for user {uid}")
                return False

        except Exception as e:
            print(f"❌ UserService: Error updating user role {uid}: {e}")
            return False

    async def sync_user_claims(self, uid: str) -> bool:
        """
        Synchronize user's Firestore role to Firebase custom claims

        Args:
            uid: Firebase user UID

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get user document from Firestore
            user_data = await self.get_user_by_uid(uid)
            if not user_data:
                print(f"❌ UserService: User {uid} not found in Firestore")
                return False

            system_role = user_data.get("systemRole")
            if not system_role:
                print(f"❌ UserService: No systemRole found for user {uid}")
                return False

            # Set custom claims in Firebase
            custom_claims = {"systemRole": system_role}
            await asyncio.to_thread(auth.set_custom_user_claims, uid, custom_claims)

            print(
                f"✅ UserService: Synced claims for user {uid} with role {system_role}"
            )
            return True

        except Exception as e:
            print(f"❌ UserService: Error syncing claims for user {uid}: {e}")
            return False

    async def check_and_sync_user_claims(
        self, decoded_token: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Check if user's Firestore role matches their token claims and sync if needed

        Args:
            decoded_token: Decoded Firebase ID token

        Returns:
            Updated user data if successful, None otherwise
        """
        uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        display_name = decoded_token.get("name")

        if not uid or not email:
            print("❌ UserService: Invalid token - missing uid or email")
            return None

        try:
            # Get or create user document
            user_data = await self.create_or_update_user(uid, email, display_name)
            if not user_data:
                return None

            # Check if claims need syncing
            firestore_role = user_data.get("systemRole")
            token_role = decoded_token.get("systemRole")

            if firestore_role != token_role:
                print(
                    f"🔄 UserService: Role mismatch for {email} - Firestore: {firestore_role}, Token: {token_role}"
                )

                # Sync Firestore role to Firebase claims
                await self.sync_user_claims(uid)

                # Note: Custom claims only take effect on next token refresh
                print(
                    f"ℹ️ UserService: Claims updated for {email}. User needs to refresh token for changes to take effect."
                )

            return user_data

        except Exception as e:
            print(f"❌ UserService: Error checking/syncing claims for {uid}: {e}")
            return None


# Global user service instance
user_service = UserService()
