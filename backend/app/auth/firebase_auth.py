import firebase_admin
from firebase_admin import auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.auth_service import auth_service

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """
    Dependency to verify Firebase ID token and get user data.
    
    Args:
        credentials: The Bearer token credentials extracted by HTTPBearer
    
    Returns:
        Decoded Firebase user claims (dictionary).
        
    Raises:
        HTTPException: If the token is invalid, expired, or authentication fails.
    """
    if not credentials:
        print("❌ [AUTH] No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    print(f"🔐 [AUTH] Verifying Firebase ID token...")
    print(f"🎫 [AUTH] Token preview: {token[:50] if token else 'NULL'}...")
    
    if not auth_service.is_initialized:
        print("❌ [AUTH] Firebase Admin SDK not initialized!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not available. Please try again later.",
        )

    try:
        print("🔍 [AUTH] Calling auth_service.verify_id_token()...")
        decoded_token = auth_service.verify_id_token(token)
        
        if not decoded_token:
            print("❌ [AUTH] Token verification failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token. Please re-authenticate.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print(f"✅ [AUTH] Token verified successfully for user: {decoded_token.get('email', 'unknown')}")
        return decoded_token
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        # Log unexpected errors and return a generic auth error
        print(f"❌ [AUTH] Unexpected error during token verification: {e}")
        print(f"❌ [AUTH] Exception type: {type(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please re-authenticate.",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(decoded_token: dict = Depends(get_current_user)) -> dict:
    """
    Get current active user. Additional checks can be added here.
    
    Args:
        decoded_token: Decoded Firebase token from get_current_user
        
    Returns:
        Decoded token with additional validation
        
    Raises:
        HTTPException: If user is disabled or inactive
    """
    # Check if user is disabled (this is already checked by Firebase verify_id_token)
    # but we can add additional business logic here
    
    if decoded_token.get('disabled', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been disabled.",
        )
    
    # Additional business logic checks can be added here
    # For example, checking user roles, subscription status, etc.
    
    return decoded_token

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Optional authentication dependency that doesn't raise errors if no token is provided.
    
    Args:
        credentials: Optional Bearer token credentials
        
    Returns:
        Decoded user claims if valid token provided, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        # If token is provided but invalid, treat as no user for optional auth
        return None
    except Exception:
        # Catch-all for other unexpected errors
        return None

# Convenience function for checking if user has specific roles/permissions
def require_role(required_role: str):
    """
    Dependency factory for role-based access control.
    
    Args:
        required_role: The role required to access the endpoint
        
    Returns:
        A dependency function that checks for the required role
    """
    async def role_checker(current_user: dict = Depends(get_current_active_user)) -> dict:
        user_role = current_user.get('role', '')
        if user_role != required_role and 'admin' not in user_role.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}",
            )
        return current_user
    
    return role_checker 