#!/usr/bin/env python3
"""
Script to manually assign FINANCE_APPROVER role to a user for financial approval workflows
Usage: python scripts/set_finance_approver_role.py <user_email>
"""

import sys
import os
import asyncio
from datetime import datetime, timezone

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.user_service import user_service
from app.models.firestore_models import UserRole
from firebase_admin import auth

async def set_user_finance_approver_role(user_email: str):
    """
    Set a user's role to FINANCE_APPROVER in Firestore and sync to Firebase custom claims
    
    Args:
        user_email: Email address of the user to make finance approver
    """
    try:
        print(f"🔍 Looking up user with email: {user_email}")
        
        # Get user by email from Firebase Auth
        try:
            user_record = auth.get_user_by_email(user_email)
            uid = user_record.uid
            print(f"✅ Found user: {user_email} (UID: {uid})")
        except auth.UserNotFoundError:
            print(f"❌ User not found in Firebase Auth: {user_email}")
            return False
        
        # Create or update user in Firestore with FINANCE_APPROVER role
        print(f"🔄 Setting user role to FINANCE_APPROVER in Firestore...")
        user_data = await user_service.create_or_update_user(
            uid=uid,
            email=user_email,
            display_name=user_record.display_name,
            system_role=UserRole.FINANCE_APPROVER
        )
        
        if not user_data:
            print(f"❌ Failed to update user in Firestore")
            return False
        
        print(f"✅ User updated in Firestore with FINANCE_APPROVER role")
        
        # Sync to Firebase custom claims
        print(f"🔄 Syncing custom claims...")
        success = await user_service.sync_user_claims(uid)
        
        if success:
            print(f"🎉 SUCCESS: {user_email} is now a FINANCE_APPROVER!")
            print(f"📝 Note: User will need to sign out and sign back in for changes to take effect.")
            return True
        else:
            print(f"❌ Failed to sync custom claims")
            return False
            
    except Exception as e:
        print(f"❌ Error setting finance approver role: {e}")
        return False

async def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python scripts/set_finance_approver_role.py <user_email>")
        print("Example: python scripts/set_finance_approver_role.py finance@carelogic.co")
        sys.exit(1)
    
    user_email = sys.argv[1].strip()
    
    if not user_email or '@' not in user_email:
        print("❌ Invalid email address")
        sys.exit(1)
    
    print("🚀 DrFirst Business Case Generator - Finance Approver Role Assignment")
    print("=" * 68)
    print(f"📧 Target user: {user_email}")
    print(f"🎯 Action: Set systemRole to FINANCE_APPROVER")
    print("=" * 68)
    
    # Confirm action
    confirm = input(f"Are you sure you want to make {user_email} a FINANCE_APPROVER? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Operation cancelled")
        sys.exit(0)
    
    # Set finance approver role
    success = await set_user_finance_approver_role(user_email)
    
    if success:
        print("\n🎊 FINANCE_APPROVER ROLE ASSIGNMENT COMPLETE!")
        print(f"💰 {user_email} is now a finance approver")
        print("\n📋 Next steps:")
        print("1. User should sign out of the application")
        print("2. User should sign back in to get new token with FINANCE_APPROVER claims")
        print("3. User can now approve cost estimates and financial projections")
    else:
        print("\n❌ FINANCE_APPROVER ROLE ASSIGNMENT FAILED")
        print("Please check the logs above for error details")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 