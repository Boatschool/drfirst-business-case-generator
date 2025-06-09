#!/usr/bin/env python3
"""
Universal Role Assignment Script

This script provides a universal function for assigning roles to users,
along with role descriptions for validation.
"""

import asyncio
import sys
import os
from typing import Optional

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models.firestore_models import UserRole
from app.services.user_service import UserService
import firebase_admin
from firebase_admin import auth

# Role descriptions with emojis
ROLE_DESCRIPTIONS = {
    "ADMIN": "👑 Full system administrator with all permissions",
    "USER": "👤 Standard user with basic access",
    "VIEWER": "👁️ View-only access to system resources",
    "DEVELOPER": "👨‍💻 Development team member with technical access",
    "SALES_REP": "💼 Sales representative with customer interaction permissions",
    "SALES_MANAGER": "💼 Sales team manager with sales-related permissions",
    "FINANCE_APPROVER": "💰 Finance team member with approval authority",
    "LEGAL_APPROVER": "⚖️ Legal team member with legal approval authority",
    "TECHNICAL_ARCHITECT": "🏗️ Technical architect with system design authority",
    "PRODUCT_OWNER": "📦 Product owner with product management authority",
    "BUSINESS_ANALYST": "📈 Business analyst with requirements analysis authority",
    "FINAL_APPROVER": "👑 Final approver with ultimate decision authority"
}

async def set_user_role(email: str, role_name: str) -> bool:
    """
    Set a user's role by email address.
    
    Args:
        email: User's email address
        role_name: Role name as string (e.g., "ADMIN", "DEVELOPER")
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Validate role
        if role_name not in [role.value for role in UserRole]:
            print(f"❌ Invalid role: {role_name}")
            return False
            
        role = UserRole(role_name)
        
        # Get user by email from Firebase Auth
        user_record = auth.get_user_by_email(email)
        
        # Create/update user in Firestore
        user_service = UserService()
        result = await user_service.create_or_update_user(
            uid=user_record.uid,
            email=email,
            display_name=user_record.display_name,
            system_role=role
        )
        
        if not result:
            print(f"❌ Failed to create/update user {email}")
            return False
            
        # Sync role to Firebase custom claims
        success = await user_service.sync_user_claims(user_record.uid)
        
        if success:
            print(f"✅ Successfully assigned role {role_name} to {email}")
            return True
        else:
            print(f"❌ Failed to sync claims for {email}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting role for {email}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python set_user_role.py <email> <role>")
        print("Available roles:")
        for role_name, description in ROLE_DESCRIPTIONS.items():
            print(f"  {role_name}: {description}")
        sys.exit(1)
        
    email = sys.argv[1]
    role_name = sys.argv[2]
    
    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    
    # Run the role assignment
    success = asyncio.run(set_user_role(email, role_name))
    sys.exit(0 if success else 1) 