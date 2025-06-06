"""
Configuration helper functions for the DrFirst Business Case Generator
"""

import asyncio
import logging
from typing import Optional
from google.cloud import firestore
from app.core.config import settings
from app.auth.firebase_auth import get_current_active_user
from app.models.firestore_models import UserRole
from fastapi import Depends, HTTPException, status

logger = logging.getLogger(__name__)

# Cache for final approver role to avoid repeated Firestore reads
_final_approver_role_cache = {
    "role": None,
    "last_updated": None,
    "cache_duration": 300,  # 5 minutes in seconds
}


async def get_final_approver_role_name() -> str:
    """
    Get the currently configured final approver role name from Firestore.

    Returns:
        str: The system role name that should be used for final approvals

    Raises:
        Exception: If unable to fetch configuration from Firestore
    """
    import time
    from datetime import datetime, timezone

    # Check cache first
    current_time = time.time()
    if (
        _final_approver_role_cache["role"] is not None
        and _final_approver_role_cache["last_updated"] is not None
        and current_time - _final_approver_role_cache["last_updated"]
        < _final_approver_role_cache["cache_duration"]
    ):
        return _final_approver_role_cache["role"]

    try:
        # Initialize Firestore client
        db = firestore.Client(project=settings.firebase_project_id)

        # Fetch configuration from Firestore
        config_ref = db.collection("systemConfiguration").document("approvalSettings")
        doc = await asyncio.to_thread(config_ref.get)

        if not doc.exists:
            # Return default if configuration doesn't exist yet
            logger.info(
                "[CONFIG] No final approver configuration found, using default 'FINAL_APPROVER'"
            )
            final_approver_role = UserRole.FINAL_APPROVER.value
        else:
            config_data = doc.to_dict()
            final_approver_role = config_data.get(
                "finalApproverRoleName", UserRole.FINAL_APPROVER.value
            )
            logger.info(
                f"[CONFIG] Retrieved final approver role from Firestore: {final_approver_role}"
            )

        # Update cache
        _final_approver_role_cache["role"] = final_approver_role
        _final_approver_role_cache["last_updated"] = current_time

        return final_approver_role

    except Exception as e:
        logger.info(f"[CONFIG] Error fetching final approver role configuration: {e}")
        # Fallback to default role if there's an error
        logger.info("[CONFIG] Falling back to default 'FINAL_APPROVER' role")
        return UserRole.FINAL_APPROVER.value


def clear_final_approver_role_cache():
    """
    Clear the cached final approver role to force a fresh fetch on next request.
    Useful when the configuration is updated.
    """
    _final_approver_role_cache["role"] = None
    _final_approver_role_cache["last_updated"] = None
    logger.info("[CONFIG] Final approver role cache cleared")


def require_dynamic_final_approver_role():
    """
    Dependency factory for dynamic final approver role checking.

    Returns:
        A dependency function that checks for the currently configured final approver role
    """

    async def dynamic_role_checker(
        current_user: dict = Depends(get_current_active_user),
    ) -> dict:
        try:
            # Get the currently configured final approver role
            required_role = await get_final_approver_role_name()

            # Check user's role
            user_role = current_user.get("systemRole", "")
            user_email = current_user.get("email", "unknown")

            # Allow ADMIN role as a fallback (admins can always approve)
            if user_role != required_role and user_role != UserRole.ADMIN.value:
                logger.info(
                    f"[CONFIG] Access denied for {user_email} - requires '{required_role}' role, has: '{user_role}'"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: {required_role} (or ADMIN)",
                )

            logger.info(
                f"[CONFIG] Dynamic final approval access granted for {user_email} with role '{user_role}' (required: '{required_role}')"
            )
            return current_user

        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.info(f"[CONFIG] Error in dynamic role checking: {e}")
            # Fallback to default behavior
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error checking authorization. Please try again.",
            )

    return dynamic_role_checker
