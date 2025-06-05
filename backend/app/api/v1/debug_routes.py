"""
Debug routes for testing authentication and basic functionality
"""

from fastapi import APIRouter, Depends
from app.auth.firebase_auth import get_current_user

router = APIRouter()


@router.get("/debug/auth-test")
async def test_auth(current_user: dict = Depends(get_current_user)):
    """
    Simple endpoint to test authentication
    """
    return {
        "message": "Authentication successful!",
        "user_info": {
            "uid": current_user.get("uid"),
            "email": current_user.get("email"),
            "email_verified": current_user.get("email_verified"),
            "name": current_user.get("name"),
        },
    }


@router.get("/debug/no-auth")
async def test_no_auth():
    """
    Endpoint that doesn't require authentication
    """
    return {
        "message": "This endpoint doesn't require authentication",
        "status": "accessible",
    }
