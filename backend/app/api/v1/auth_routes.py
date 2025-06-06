"""
Authentication API routes for the DrFirst Business Case Generator
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from app.services.auth_service import auth_service
from app.middleware.rate_limiter import limiter

router = APIRouter()
security = HTTPBearer()


class TokenRequest(BaseModel):
    id_token: str


class UserResponse(BaseModel):
    uid: str
    email: Optional[str]
    name: Optional[str]
    picture: Optional[str]
    email_verified: bool


@router.post(
    "/verify-token", summary="Verify Firebase ID token", response_model=UserResponse
)
@limiter.limit("10/minute")  # Strict limit for token verification
async def verify_token(request: Request, token_request: TokenRequest):
    """Verify Firebase ID token and return user information"""
    try:
        user_info = await auth_service.verify_token(token_request.id_token)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        # Check if user email is from DrFirst domain
        if not user_info.get("email", "").endswith("@drfirst.com"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access restricted to DrFirst employees",
            )

        return UserResponse(
            uid=user_info["uid"],
            email=user_info.get("email"),
            name=user_info.get("name"),
            picture=user_info.get("picture"),
            email_verified=user_info.get("email_verified", False),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}",
        )


@router.get("/me", summary="Get current user profile")
@limiter.limit("30/minute")
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get current user profile information using Bearer token"""
    try:
        # Extract token from Authorization header
        id_token = credentials.credentials

        user_info = await auth_service.verify_token(id_token)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        return UserResponse(
            uid=user_info["uid"],
            email=user_info.get("email"),
            name=user_info.get("name"),
            picture=user_info.get("picture"),
            email_verified=user_info.get("email_verified", False),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}",
        )


@router.post("/revoke", summary="Revoke user sessions")
@limiter.limit("5/minute")  # Very strict limit for session revocation
async def revoke_user_sessions(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Revoke all refresh tokens for current user (signs them out of all sessions)"""
    try:
        # Extract token from Authorization header
        id_token = credentials.credentials

        user_info = await auth_service.verify_token(id_token)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        success = await auth_service.revoke_refresh_tokens(user_info["uid"])
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke user sessions",
            )

        return {"message": "All user sessions revoked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session revocation error: {str(e)}",
        )
