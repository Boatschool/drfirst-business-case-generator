#!/usr/bin/env python3
"""
Test script to verify RBAC implementation for DrFirst Business Case Generator
"""

import asyncio
import requests
import json
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.user_service import user_service
from app.models.firestore_models import UserRole

API_BASE_URL = "http://localhost:8000"

def test_admin_api_without_auth():
    """Test admin API endpoints without authentication"""
    print("\n🧪 Testing admin API endpoints without authentication...")
    
    endpoints = [
        "/api/v1/admin/rate-cards",
        "/api/v1/admin/pricing-templates",
        "/api/v1/admin/users",
        "/api/v1/admin/analytics"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            if response.status_code == 401:
                print(f"✅ {endpoint} - Correctly returns 401 (unauthorized)")
            else:
                print(f"❌ {endpoint} - Expected 401, got {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Request failed: {e}")

def test_admin_api_with_user_token(token: str):
    """Test admin API endpoints with regular user token"""
    print("\n🧪 Testing admin API endpoints with regular user token...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        "/api/v1/admin/rate-cards",
        "/api/v1/admin/pricing-templates",
        "/api/v1/admin/users",
        "/api/v1/admin/analytics"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 403:
                print(f"✅ {endpoint} - Correctly returns 403 (forbidden)")
            else:
                print(f"❌ {endpoint} - Expected 403, got {response.status_code}")
                if response.status_code == 200:
                    print(f"   Response: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Request failed: {e}")

def test_admin_api_with_admin_token(token: str):
    """Test admin API endpoints with admin token"""
    print("\n🧪 Testing admin API endpoints with admin token...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        "/api/v1/admin/rate-cards",
        "/api/v1/admin/pricing-templates",
        "/api/v1/admin/users",
        "/api/v1/admin/analytics"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 200:
                print(f"✅ {endpoint} - Correctly returns 200 (success)")
                data = response.json()
                if isinstance(data, list):
                    print(f"   Found {len(data)} items")
                elif isinstance(data, dict):
                    print(f"   Response keys: {list(data.keys())}")
            else:
                print(f"❌ {endpoint} - Expected 200, got {response.status_code}")
                if response.status_code != 200:
                    print(f"   Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Request failed: {e}")

async def check_user_in_firestore(email: str):
    """Check if user exists in Firestore and their role"""
    print(f"\n🔍 Checking user in Firestore: {email}")
    
    try:
        from firebase_admin import auth
        user_record = auth.get_user_by_email(email)
        uid = user_record.uid
        
        user_data = await user_service.get_user_by_uid(uid)
        
        if user_data:
            print(f"✅ User found in Firestore")
            print(f"   UID: {uid}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   System Role: {user_data.get('systemRole', 'Not set')}")
            print(f"   Created: {user_data.get('created_at', 'Unknown')}")
            print(f"   Last Login: {user_data.get('last_login', 'Unknown')}")
            return user_data
        else:
            print(f"❌ User not found in Firestore")
            return None
            
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 DrFirst Business Case Generator - RBAC Testing")
    print("=" * 60)
    print(f"🕒 Test started at: {datetime.now()}")
    print("=" * 60)
    
    # Test 1: Unauthenticated access
    test_admin_api_without_auth()
    
    # Instructions for manual testing
    print("\n📋 MANUAL TESTING INSTRUCTIONS:")
    print("=" * 40)
    print("1. Start the backend server: cd backend && python -m uvicorn app.main:app --reload")
    print("2. Start the frontend server: cd frontend && npm run dev")
    print("3. Sign in with a regular user (non-admin)")
    print("4. Try to access http://localhost:4000/admin")
    print("5. Check browser console for authentication logs")
    print("6. Use set_admin_role.py script to make a user admin")
    print("7. Sign out and sign back in as admin user")
    print("8. Try to access http://localhost:4000/admin again")
    print("9. Verify admin can access all admin features")
    
    print("\n🔧 ADMIN ROLE ASSIGNMENT:")
    print("To make a user admin, run:")
    print("python scripts/set_admin_role.py <user_email>")
    print("Example: python scripts/set_admin_role.py ron@carelogic.co")
    
    print("\n📊 VERIFICATION CHECKLIST:")
    print("□ Regular users cannot access /admin route")
    print("□ Regular users get 403 on admin API endpoints")
    print("□ Admin users can access /admin route")
    print("□ Admin users get 200 on admin API endpoints")
    print("□ User documents created in Firestore on first login")
    print("□ Custom claims sync from Firestore to Firebase")
    print("□ Role changes require sign out/sign in")
    
    # Test Firestore user checking if requested
    if len(sys.argv) > 1:
        email = sys.argv[1]
        print(f"\n🔍 Checking specific user: {email}")
        asyncio.run(check_user_in_firestore(email))
    
    print("\n✅ RBAC Test Setup Complete!")
    print("Follow the manual testing instructions above to verify implementation.")

if __name__ == "__main__":
    main() 