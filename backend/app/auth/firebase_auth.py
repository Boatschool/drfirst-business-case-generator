import firebase_admin
from firebase_admin import auth
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token") # Placeholder tokenUrl

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency to verify Firebase ID token and get user data.
    
    Args:
        token: The ID token extracted by OAuth2PasswordBearer.
               Note: Despite the name 'OAuth2PasswordBearer', we're using it
               to extract a Firebase ID token (JWT Bearer token).
               The tokenUrl is a placeholder and not actually used by Firebase ID token flow.
    
    Returns:
        Decoded Firebase user claims (dictionary).
        
    Raises:
        HTTPException: If the token is invalid, expired, or authentication fails.
    """
    if not firebase_admin._DEFAULT_APP_NAME in firebase_admin._apps:
        # This check is important if the app might not initialize Firebase Admin correctly.
        # However, main.py should handle initialization.
        # Consider how to handle this error robustly, perhaps by ensuring init during startup.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase Admin SDK not initialized. Cannot authenticate user.",
        )
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except firebase_admin.auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID token has expired. Please re-authenticate.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except firebase_admin.auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ID token. Please re-authenticate.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except firebase_admin.auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID token has been revoked. Please re-authenticate.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except firebase_admin.auth.UserDisabledError:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, # Or 401, depending on desired UX
            detail="User account has been disabled.",
        )
    except Exception as e: # Catch any other Firebase auth errors or general exceptions
        # Log the exception e for server-side review
        print(f"An unexpected error occurred during token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials. An unexpected error occurred.",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(decoded_token: dict = Depends(get_current_user)) -> dict:
    """
    Placeholder for a user that is active. 
    Currently, just returns the decoded token.
    In the future, you could check if decoded_token['disabled'] is False,
    or check against a user status in your database.
    Firebase's verify_id_token() already checks for disabled users if the user
    was disabled via the Firebase console, raising UserDisabledError.
    """
    # Example: if decoded_token.get("disabled"):
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return decoded_token

# You can also create a dependency that optionally gets the user
async def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[dict]:
    if not token:
        return None
    try:
        # Re-use get_current_user logic but handle its specific HTTPExceptions differently if needed,
        # or let them propagate if a 401 is acceptable for an invalid optional token.
        # For simplicity, we'll just call it and handle errors generally.
        return await get_current_user(token)
    except HTTPException:
        # If token is provided but invalid, treat as no user
        return None
    except Exception:
        # Catch-all for other unexpected errors
        return None 