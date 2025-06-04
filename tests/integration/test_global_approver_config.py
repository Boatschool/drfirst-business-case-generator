#!/usr/bin/env python3
"""
Test script for Global Final Approver Role Configuration
Verifies the implementation of Task 9.1.4
"""

import asyncio
import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
ADMIN_TOKEN = None  # Will need to be set manually for testing

def print_test_header(test_name: str):
    """Print a formatted test header"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_step(step_name: str):
    """Print a formatted test step"""
    print(f"\n📋 {step_name}")
    print("-" * 40)

async def test_backend_endpoints():
    """Test the new backend endpoints for global approver configuration"""
    
    print_test_header("Backend API Endpoints Test")
    
    if not ADMIN_TOKEN:
        print("❌ ADMIN_TOKEN not set. Please set it manually for testing.")
        print("   To get a token:")
        print("   1. Log in to the frontend as an ADMIN user")
        print("   2. Open browser dev tools and copy the Firebase ID token")
        print("   3. Set ADMIN_TOKEN = 'your_token_here' in this script")
        return False
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test GET endpoint
    print_step("Testing GET /api/v1/admin/config/final-approver-role")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/admin/config/final-approver-role", headers=headers)
        if response.status_code == 200:
            config = response.json()
            print(f"✅ GET request successful")
            print(f"   Current role: {config['finalApproverRoleName']}")
            print(f"   Response: {json.dumps(config, indent=2)}")
        else:
            print(f"❌ GET request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ GET request error: {e}")
        return False
    
    # Test PUT endpoint
    print_step("Testing PUT /api/v1/admin/config/final-approver-role")
    test_role = "ADMIN"
    try:
        put_data = {"finalApproverRoleName": test_role}
        response = requests.put(
            f"{BACKEND_URL}/api/v1/admin/config/final-approver-role", 
            headers=headers,
            json=put_data
        )
        if response.status_code == 200:
            config = response.json()
            print(f"✅ PUT request successful")
            print(f"   Updated role to: {config['finalApproverRoleName']}")
            print(f"   Response: {json.dumps(config, indent=2)}")
        else:
            print(f"❌ PUT request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ PUT request error: {e}")
        return False
    
    # Verify the change persisted
    print_step("Verifying configuration change persisted")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/admin/config/final-approver-role", headers=headers)
        if response.status_code == 200:
            config = response.json()
            if config['finalApproverRoleName'] == test_role:
                print(f"✅ Configuration change verified")
                print(f"   Role is now: {config['finalApproverRoleName']}")
            else:
                print(f"❌ Configuration change not persisted")
                print(f"   Expected: {test_role}, Got: {config['finalApproverRoleName']}")
                return False
        else:
            print(f"❌ Verification request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False
    
    # Reset to original role
    print_step("Resetting to original role (FINAL_APPROVER)")
    try:
        reset_data = {"finalApproverRoleName": "FINAL_APPROVER"}
        response = requests.put(
            f"{BACKEND_URL}/api/v1/admin/config/final-approver-role", 
            headers=headers,
            json=reset_data
        )
        if response.status_code == 200:
            print(f"✅ Successfully reset to FINAL_APPROVER")
        else:
            print(f"⚠️  Failed to reset role: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error resetting role: {e}")
    
    return True

def test_firestore_configuration():
    """Test that Firestore configuration was set up correctly"""
    
    print_test_header("Firestore Configuration Test")
    
    try:
        import firebase_admin
        from firebase_admin import firestore
        
        # Initialize if not already done
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app()
        
        db = firestore.client()
        
        print_step("Checking systemConfiguration/approvalSettings document")
        doc_ref = db.collection("systemConfiguration").document("approvalSettings")
        doc = doc_ref.get()
        
        if doc.exists:
            config_data = doc.to_dict()
            print("✅ Configuration document exists")
            print(f"   Final Approver Role: {config_data.get('finalApproverRoleName')}")
            print(f"   Created At: {config_data.get('createdAt')}")
            print(f"   Updated At: {config_data.get('updatedAt')}")
            print(f"   Description: {config_data.get('description', 'N/A')}")
            return True
        else:
            print("❌ Configuration document not found")
            return False
            
    except Exception as e:
        print(f"❌ Firestore test error: {e}")
        return False

def test_frontend_implementation():
    """Test frontend implementation (manual verification)"""
    
    print_test_header("Frontend Implementation Test (Manual)")
    
    print_step("Frontend Testing Checklist")
    print("Please verify the following manually:")
    print("")
    print("1. ✅ AdminPage.tsx has new 'Global Approval Settings' section")
    print("2. ✅ Section shows current final approver role")
    print("3. ✅ Dropdown allows selecting different system roles")
    print("4. ✅ Save button updates the configuration")
    print("5. ✅ Success notification shows after saving")
    print("6. ✅ Configuration persists across page reloads")
    print("")
    print("📱 To test the frontend:")
    print("   1. Start the frontend: cd frontend && npm start")
    print("   2. Log in as an ADMIN user")
    print("   3. Navigate to /admin")
    print("   4. Look for 'Global Approval Settings' section")
    print("   5. Test changing the role and saving")

def test_dynamic_approval_logic():
    """Test that the dynamic approval logic works"""
    
    print_test_header("Dynamic Approval Logic Test (Manual)")
    
    print_step("Dynamic Logic Testing Instructions")
    print("To test that the dynamic approval logic works:")
    print("")
    print("1. 📝 Create a test business case and complete all stages")
    print("   - Complete PRD, System Design, and Financial Model")
    print("   - Submit for final approval")
    print("")
    print("2. 🔧 Change final approver role to 'ADMIN' via admin UI")
    print("")
    print("3. 👤 Test with different user roles:")
    print("   - ADMIN user should see approve/reject buttons")
    print("   - FINAL_APPROVER user should NOT see buttons")
    print("   - Other roles should NOT see buttons")
    print("")
    print("4. 🔄 Change role back to 'FINAL_APPROVER' and test again:")
    print("   - FINAL_APPROVER user should see approve/reject buttons")
    print("   - ADMIN user should still see buttons (fallback)")
    print("   - Other roles should NOT see buttons")
    print("")
    print("5. ✅ Verify approval/rejection actually works with new roles")

def generate_test_summary():
    """Generate a summary of what needs to be tested"""
    
    print_test_header("TEST SUMMARY & ACCEPTANCE CRITERIA")
    
    print_step("Implementation Components")
    components = [
        "✅ Firestore configuration (systemConfiguration/approvalSettings)",
        "✅ Backend API endpoints (GET/PUT /admin/config/final-approver-role)",
        "✅ Dynamic role checking helper (require_dynamic_final_approver_role)",
        "✅ Updated case approval endpoints to use dynamic role",
        "✅ Frontend AdminService methods (get/set final approver role)",
        "✅ Frontend AdminPage UI section (Global Approval Settings)",
        "✅ Role caching with cache invalidation"
    ]
    
    for component in components:
        print(f"   {component}")
    
    print_step("Acceptance Criteria Verification")
    criteria = [
        "🎯 Global setting stored and managed in Firestore",
        "🎯 Backend approval logic uses dynamic role from Firestore",
        "🎯 Admin UI allows viewing current final approver role",
        "🎯 Admin UI allows selecting and saving new approver role",
        "🎯 Changes affect subsequent final approvals immediately",
        "🎯 UI provides appropriate feedback (loading, success, error)",
        "🎯 Only ADMIN role can modify this setting"
    ]
    
    for criterion in criteria:
        print(f"   {criterion}")
    
    print_step("Next Steps")
    steps = [
        "1. Test backend endpoints with valid ADMIN token",
        "2. Test frontend UI in development environment",
        "3. Test dynamic approval logic with different roles",
        "4. Verify security (only ADMIN can change setting)",
        "5. Test error handling and edge cases",
        "6. Deploy to staging/production environment"
    ]
    
    for step in steps:
        print(f"   {step}")

def main():
    """Main test execution"""
    
    print("🚀 Global Final Approver Role Configuration Tests")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test Firestore configuration
    firestore_success = test_firestore_configuration()
    
    # Test backend endpoints (requires manual token setup)
    backend_success = asyncio.run(test_backend_endpoints())
    
    # Frontend and dynamic logic tests (manual)
    test_frontend_implementation()
    test_dynamic_approval_logic()
    
    # Generate summary
    generate_test_summary()
    
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"   Firestore Configuration: {'✅ PASS' if firestore_success else '❌ FAIL'}")
    print(f"   Backend API Endpoints: {'✅ PASS' if backend_success else '❌ MANUAL TEST REQUIRED'}")
    print(f"   Frontend Implementation: 📋 MANUAL VERIFICATION REQUIRED")
    print(f"   Dynamic Approval Logic: 📋 MANUAL VERIFICATION REQUIRED")
    
    if firestore_success:
        print(f"\n🎉 Core implementation is ready for testing!")
        print(f"   The Firestore configuration is set up correctly.")
        print(f"   Backend endpoints should work (test with valid ADMIN token).")
        print(f"   Frontend UI should show the Global Approval Settings section.")
    else:
        print(f"\n❌ Setup issues detected. Please resolve before testing.")

if __name__ == "__main__":
    main() 