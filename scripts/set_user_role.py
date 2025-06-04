#!/usr/bin/env python3
"""
Universal script to assign any role to a user
Usage: python scripts/set_user_role.py <user_email> <role>

Available roles:
- ADMIN
- USER  
- VIEWER
- DEVELOPER
- SALES_REP
- SALES_MANAGER
- FINANCE_APPROVER
- LEGAL_APPROVER
- TECHNICAL_ARCHITECT
- PRODUCT_OWNER
- BUSINESS_ANALYST
"""

import sys
import os
import asyncio
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.user_service import user_service
from app.models.firestore_models import UserRole
from firebase_admin import auth
from app.core.config import settings

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        if not firebase_admin._apps:
            print("🚀 Initializing Firebase Admin SDK...")
            
            # Try to initialize with service account credentials
            cred = None
            
            # Method 1: Try to use service account file if it exists
            if (settings.google_application_credentials and 
                os.path.exists(settings.google_application_credentials)):
                print(f"📁 Using service account file: {settings.google_application_credentials}")
                cred = credentials.Certificate(settings.google_application_credentials)
            
            # Method 2: Try to use GOOGLE_APPLICATION_CREDENTIALS environment variable
            elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                if os.path.exists(cred_path):
                    print(f"📁 Using service account from env: {cred_path}")
                    cred = credentials.Certificate(cred_path)
                else:
                    print(f"❌ Service account file not found at: {cred_path}")
            
            # Method 3: Try to use default credentials (for Cloud Run)
            else:
                print("🔧 Using default credentials")
                try:
                    cred = credentials.ApplicationDefault()
                except Exception as default_cred_error:
                    print(f"❌ Failed to use default credentials: {default_cred_error}")
                    if settings.firebase_project_id:
                        print("🔧 Attempting to initialize without explicit credentials...")
                        cred = None
            
            # Initialize Firebase app
            if cred:
                firebase_admin.initialize_app(cred, {
                    'projectId': settings.firebase_project_id or settings.google_cloud_project_id,
                })
            else:
                firebase_admin.initialize_app(options={
                    'projectId': settings.firebase_project_id or settings.google_cloud_project_id,
                })
            
            print(f"✅ Firebase Admin SDK initialized successfully")
            
        else:
            print("📱 Firebase Admin SDK already initialized")
            
    except Exception as e:
        print(f"❌ Firebase initialization error: {e}")
        raise

# Role descriptions for display
ROLE_DESCRIPTIONS = {
    "ADMIN": "🔑 System Administrator",
    "USER": "👤 Regular User", 
    "VIEWER": "👁️ View-Only User",
    "DEVELOPER": "👨‍💻 Developer/Technical Reviewer",
    "SALES_REP": "💼 Sales Representative",
    "SALES_MANAGER": "📊 Sales Manager", 
    "FINANCE_APPROVER": "💰 Finance Approver",
    "LEGAL_APPROVER": "⚖️ Legal Approver",
    "TECHNICAL_ARCHITECT": "🏗️ Technical Architect", 
    "PRODUCT_OWNER": "📦 Product Owner",
    "BUSINESS_ANALYST": "📈 Business Analyst",
    "FINAL_APPROVER": "👑 Final Business Case Approver"
}

async def set_user_role(user_email: str, role_name: str):
    """
    Set a user's role in Firestore and sync to Firebase custom claims
    
    Args:
        user_email: Email address of the user
        role_name: Role to assign (must be valid UserRole)
    """
    try:
        # Validate role
        try:
            role = UserRole(role_name)
        except ValueError:
            valid_roles = [r.value for r in UserRole]
            print(f"❌ Invalid role: {role_name}")
            print(f"Valid roles: {', '.join(valid_roles)}")
            return False
        
        print(f"🔍 Looking up user with email: {user_email}")
        
        # Get user by email from Firebase Auth
        try:
            user_record = auth.get_user_by_email(user_email)
            uid = user_record.uid
            print(f"✅ Found user: {user_email} (UID: {uid})")
        except auth.UserNotFoundError:
            print(f"❌ User not found in Firebase Auth: {user_email}")
            return False
        
        # Create or update user in Firestore with new role
        print(f"🔄 Setting user role to {role_name} in Firestore...")
        user_data = await user_service.create_or_update_user(
            uid=uid,
            email=user_email,
            display_name=user_record.display_name,
            system_role=role
        )
        
        if not user_data:
            print(f"❌ Failed to update user in Firestore")
            return False
        
        print(f"✅ User updated in Firestore with {role_name} role")
        
        # Sync to Firebase custom claims
        print(f"🔄 Syncing custom claims...")
        success = await user_service.sync_user_claims(uid)
        
        if success:
            role_desc = ROLE_DESCRIPTIONS.get(role_name, f"🎯 {role_name}")
            print(f"🎉 SUCCESS: {user_email} is now assigned the role: {role_desc}")
            print(f"📝 Note: User will need to sign out and sign back in for changes to take effect.")
            return True
        else:
            print(f"❌ Failed to sync custom claims")
            return False
            
    except Exception as e:
        print(f"❌ Error setting user role: {e}")
        return False

def show_usage():
    """Display usage information and available roles"""
    print("Usage: python scripts/set_user_role.py <user_email> <role>")
    print("\nExample: python scripts/set_user_role.py john@carelogic.co SALES_MANAGER")
    print("\nAvailable roles:")
    for role_value, description in ROLE_DESCRIPTIONS.items():
        print(f"  {role_value:<20} - {description}")

async def main():
    """Main function"""
    # Initialize Firebase
    try:
        initialize_firebase()
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        sys.exit(1)
    
    if len(sys.argv) != 3:
        show_usage()
        sys.exit(1)
    
    user_email = sys.argv[1].strip()
    role_name = sys.argv[2].strip().upper()
    
    if not user_email or '@' not in user_email:
        print("❌ Invalid email address")
        sys.exit(1)
    
    if not role_name:
        print("❌ Role name is required")
        show_usage()
        sys.exit(1)
    
    # Validate role exists
    try:
        UserRole(role_name)
    except ValueError:
        print(f"❌ Invalid role: {role_name}")
        show_usage()
        sys.exit(1)
    
    role_desc = ROLE_DESCRIPTIONS.get(role_name, f"🎯 {role_name}")
    
    print("🚀 DrFirst Business Case Generator - User Role Assignment")
    print("=" * 60)
    print(f"📧 Target user: {user_email}")
    print(f"🎯 New role: {role_desc}")
    print("=" * 60)
    
    # Confirm action
    confirm = input(f"Are you sure you want to assign {role_name} role to {user_email}? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Operation cancelled")
        sys.exit(0)
    
    # Set user role
    success = await set_user_role(user_email, role_name)
    
    if success:
        print(f"\n🎊 ROLE ASSIGNMENT COMPLETE!")
        print(f"{role_desc} role assigned to {user_email}")
        print("\n📋 Next steps:")
        print("1. User should sign out of the application")
        print("2. User should sign back in to get new token with updated role claims")
        print("3. User can now access role-specific features and workflows")
    else:
        print("\n❌ ROLE ASSIGNMENT FAILED")
        print("Please check the logs above for error details")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 