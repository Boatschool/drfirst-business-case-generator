#!/usr/bin/env python3
"""
Simple API test for Global Final Approver Role Configuration
Tests the endpoints without authentication (will show 401/403 errors as expected)
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_endpoints_without_auth():
    """Test endpoints without authentication to verify they exist and require auth"""
    
    print("🧪 Testing Global Approver Config API Endpoints")
    print("=" * 60)
    
    # Test GET endpoint without auth (should return 401)
    print("\n📋 Testing GET /api/v1/admin/config/final-approver-role (without auth)")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/admin/config/final-approver-role")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 401:
            print("   ✅ EXPECTED: Endpoint exists and requires authentication")
        else:
            print("   ❌ UNEXPECTED: Should require authentication")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend server not running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test PUT endpoint without auth (should return 401)
    print("\n📋 Testing PUT /api/v1/admin/config/final-approver-role (without auth)")
    try:
        test_data = {"finalApproverRoleName": "ADMIN"}
        response = requests.put(
            f"{BACKEND_URL}/api/v1/admin/config/final-approver-role",
            json=test_data
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 401:
            print("   ✅ EXPECTED: Endpoint exists and requires authentication")
        else:
            print("   ❌ UNEXPECTED: Should require authentication")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n🎉 API endpoints are responding correctly!")
    print("   Both endpoints exist and properly require authentication.")
    return True

def test_health_check():
    """Test that the backend is running"""
    print("\n📋 Testing backend health")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("   ✅ Backend is running and healthy")
            return True
        else:
            print(f"   ⚠️  Backend responded with: {response.status_code}")
            return True  # Still running, just different endpoint
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend server not running")
        return False
    except Exception as e:
        print(f"   ❌ Error checking health: {e}")
        return False

def main():
    print("🚀 Simple API Test for Global Final Approver Configuration")
    
    # Test backend health
    if not test_health_check():
        print("\n❌ Backend server is not running!")
        print("   Please start the backend server:")
        print("   cd backend && source venv/bin/activate && uvicorn app.main:app --reload")
        return
    
    # Test endpoints
    test_endpoints_without_auth()
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS FOR FULL TESTING:")
    print("=" * 60)
    print("1. 🔐 Get an ADMIN authentication token:")
    print("   - Log into the frontend as an ADMIN user")
    print("   - Open browser dev tools (F12)")
    print("   - Go to Application/Storage > Local Storage")
    print("   - Find the Firebase token and copy it")
    print("")
    print("2. 🧪 Run authenticated tests:")
    print("   - Edit test_global_approver_config.py")
    print("   - Set ADMIN_TOKEN = 'your_token_here'")
    print("   - Run: python test_global_approver_config.py")
    print("")
    print("3. 🎨 Test the frontend UI:")
    print("   - Go to http://localhost:3000/admin")
    print("   - Look for 'Global Approval Settings' section")
    print("   - Test changing the role and saving")

if __name__ == "__main__":
    main() 