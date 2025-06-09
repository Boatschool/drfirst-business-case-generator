#!/usr/bin/env python3
"""
E2E Test Users Setup Script

This script creates all the test users required for the E2E workflow tests
and assigns them the appropriate roles.
"""

import asyncio
import sys
import os
import firebase_admin
from firebase_admin import auth, credentials
from app.models.firestore_models import UserRole
from app.services.user_service import UserService

# Test users configuration
TEST_USERS = [
    {
        "email": "test.initiator@drfirst.com",
        "password": "TestPassword123!",
        "display_name": "Test Initiator",
        "role": None  # No special role - regular user
    },
    {
        "email": "test.prd.approver@drfirst.com", 
        "password": "TestPassword123!",
        "display_name": "Test PRD Approver",
        "role": UserRole.PRODUCT_OWNER  # PRD approval requires PRODUCT_OWNER role
    },
    {
        "email": "test.developer@drfirst.com",
        "password": "TestPassword123!",
        "display_name": "Test Developer",
        "role": UserRole.DEVELOPER
    },
    {
        "email": "test.effort.approver@drfirst.com",
        "password": "TestPassword123!",
        "display_name": "Test Effort Approver", 
        "role": UserRole.TECHNICAL_ARCHITECT  # Effort approval requires TECHNICAL_ARCHITECT or DEVELOPER role
    },
    {
        "email": "test.finance@drfirst.com",
        "password": "TestPassword123!",
        "display_name": "Test Finance Approver",
        "role": UserRole.FINANCE_APPROVER
    },
    {
        "email": "test.sales@drfirst.com",
        "password": "TestPassword123!",
        "display_name": "Test Sales Manager",
        "role": UserRole.SALES_MANAGER
    },
    {
        "email": "test.final.approver@drfirst.com",
        "password": "TestPassword123!",
        "display_name": "Test Final Approver",
        "role": UserRole.FINAL_APPROVER
    },
    {
        "email": "test.admin@drfirst.com",
        "password": "TestPassword123!",
        "display_name": "Test Admin",
        "role": UserRole.ADMIN
    }
]

async def create_test_user(user_config):
    """Create a single test user in Firebase Auth and Firestore."""
    try:
        email = user_config["email"]
        password = user_config["password"]
        display_name = user_config["display_name"]
        role = user_config["role"]
        
        print(f"🔄 Creating user: {email}")
        
        # Check if user already exists
        try:
            existing_user = auth.get_user_by_email(email)
            print(f"✅ User {email} already exists (UID: {existing_user.uid})")
            user_record = existing_user
        except auth.UserNotFoundError:
            # Create user in Firebase Auth
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=display_name,
                email_verified=True
            )
            print(f"✅ Created user {email} (UID: {user_record.uid})")
        
        # Create/update user in Firestore with role
        user_service = UserService()
        result = await user_service.create_or_update_user(
            uid=user_record.uid,
            email=email,
            display_name=display_name,
            system_role=role
        )
        
        if not result:
            print(f"❌ Failed to create/update user {email} in Firestore")
            return False
            
        # Sync role to Firebase custom claims
        if role:
            success = await user_service.sync_user_claims(user_record.uid)
            if success:
                print(f"✅ Assigned role {role.value} to {email}")
            else:
                print(f"❌ Failed to sync claims for {email}")
                return False
        else:
            print(f"✅ User {email} created without special role")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating user {user_config['email']}: {e}")
        return False

async def setup_all_test_users():
    """Set up all test users for E2E testing."""
    print("🎯 Setting up E2E test users...")
    print("=" * 60)
    
    success_count = 0
    total_count = len(TEST_USERS)
    
    for user_config in TEST_USERS:
        success = await create_test_user(user_config)
        if success:
            success_count += 1
        print()  # Empty line for readability
    
    print("=" * 60)
    print(f"📊 Setup Summary: {success_count}/{total_count} users created successfully")
    
    if success_count == total_count:
        print("🎉 All test users set up successfully!")
        return True
    else:
        print("❌ Some users failed to set up")
        return False

def main():
    """Main function to initialize Firebase and set up users."""
    try:
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            # Use service account key
            cred = credentials.Certificate("credentials/service-account-key.json")
            firebase_admin.initialize_app(cred)
            print("🔧 Firebase Admin SDK initialized")
        
        # Run the setup
        success = asyncio.run(setup_all_test_users())
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 