#!/usr/bin/env python3
"""
Setup script to assign FINAL_APPROVER role to a user in Firestore and Firebase Auth custom claims.
This script demonstrates how to set up the role for testing the Final Business Case Approval Workflow.
"""

import sys
import json
from datetime import datetime, timezone

# Add the backend path to Python path for imports
sys.path.append('./backend')

def setup_final_approver_role_instructions():
    """
    Provide instructions for setting up FINAL_APPROVER role manually.
    Since we don't have Firebase Admin SDK access in this environment,
    this script provides the exact steps needed.
    """
    
    print("🔧 FINAL_APPROVER Role Setup Instructions")
    print("=" * 60)
    
    print("\n📋 Step 1: Update Firestore User Document")
    print("-" * 40)
    
    user_doc_example = {
        "email": "approver@drfirst.com",
        "displayName": "Final Approver",
        "systemRole": "FINAL_APPROVER",  # This is the key field
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "lastLoginAt": datetime.now(timezone.utc).isoformat(),
        "isActive": True
    }
    
    print("Update the user document in Firestore collection 'users':")
    print(f"Collection: users")
    print(f"Document ID: [USER_UID]")
    print(f"Document Data:")
    print(json.dumps(user_doc_example, indent=2, default=str))
    
    print("\n📋 Step 2: Set Custom Claims in Firebase Auth")
    print("-" * 40)
    
    custom_claims_example = {
        "systemRole": "FINAL_APPROVER",
        "permissions": ["APPROVE_FINAL_BUSINESS_CASE", "REJECT_FINAL_BUSINESS_CASE"]
    }
    
    print("Set custom claims for the user in Firebase Auth:")
    print("Using Firebase Admin SDK or Firebase Console:")
    print(json.dumps(custom_claims_example, indent=2))
    
    print("\n🔧 Firebase Admin SDK Code Example:")
    print("-" * 40)
    
    admin_sdk_code = '''
import firebase_admin
from firebase_admin import auth, firestore
from datetime import datetime, timezone

# Initialize Firebase Admin SDK (if not already done)
# firebase_admin.initialize_app()

def setup_final_approver(user_email, display_name="Final Approver"):
    """Set up FINAL_APPROVER role for a user"""
    
    try:
        # Get user by email
        user = auth.get_user_by_email(user_email)
        user_uid = user.uid
        
        # Set custom claims
        custom_claims = {
            "systemRole": "FINAL_APPROVER",
            "permissions": ["APPROVE_FINAL_BUSINESS_CASE", "REJECT_FINAL_BUSINESS_CASE"]
        }
        auth.set_custom_user_claims(user_uid, custom_claims)
        print(f"✅ Custom claims set for {user_email}")
        
        # Update Firestore user document
        db = firestore.client()
        user_doc_data = {
            "email": user_email,
            "displayName": display_name,
            "systemRole": "FINAL_APPROVER",
            "createdAt": datetime.now(timezone.utc),
            "lastLoginAt": datetime.now(timezone.utc),
            "isActive": True
        }
        
        db.collection("users").document(user_uid).set(user_doc_data, merge=True)
        print(f"✅ Firestore user document updated for {user_email}")
        
        return user_uid
        
    except Exception as e:
        print(f"❌ Error setting up final approver: {e}")
        return None

# Usage
user_uid = setup_final_approver("approver@drfirst.com")
if user_uid:
    print(f"🎉 Final approver setup complete for user: {user_uid}")
'''
    
    print(admin_sdk_code)
    
    print("\n📋 Step 3: Test Role Assignment")
    print("-" * 40)
    
    test_steps = [
        "1. Log in with the final approver user",
        "2. Check that isFinalApprover is true in the frontend AuthContext",
        "3. Navigate to a business case with PENDING_FINAL_APPROVAL status",
        "4. Verify that approve/reject buttons are visible",
        "5. Test approval and rejection functionality"
    ]
    
    for step in test_steps:
        print(f"   {step}")
    
    print("\n📋 Step 4: Verification Queries")
    print("-" * 40)
    
    verification_queries = {
        "Firestore Query": "SELECT * FROM users WHERE systemRole = 'FINAL_APPROVER'",
        "Firebase Auth": "Check custom claims for the user",
        "Frontend Check": "console.log(authContext.isFinalApprover) should be true"
    }
    
    for check_type, query in verification_queries.items():
        print(f"   {check_type}: {query}")
    
    print("\n🔐 Security Notes")
    print("-" * 40)
    
    security_notes = [
        "🔒 FINAL_APPROVER role should be assigned sparingly",
        "🔒 Users with this role can approve/reject any business case",
        "🔒 Consider implementing approval delegation for temporary access",
        "🔒 Monitor usage through Firestore history logs",
        "🔒 Regularly audit users with FINAL_APPROVER role"
    ]
    
    for note in security_notes:
        print(f"   {note}")

def create_test_business_case():
    """Provide example of creating a test business case for final approval testing"""
    
    print("\n" + "=" * 60)
    print("📋 Creating Test Business Case for Final Approval")
    print("=" * 60)
    
    test_case_data = {
        "case_id": "test-final-approval-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
        "user_id": "[INITIATOR_USER_UID]",
        "title": "Test Final Approval Workflow",
        "problem_statement": "This is a test case to validate the final approval workflow implementation.",
        "status": "FINANCIAL_MODEL_COMPLETE",
        "relevant_links": [],
        "history": [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "SYSTEM",
                "messageType": "CASE_CREATED",
                "content": "Test case created for final approval workflow validation"
            }
        ],
        "prd_draft": {
            "title": "Test PRD",
            "content_markdown": "# Test PRD\n\nThis is a test PRD for final approval workflow.",
            "version": "1.0.0"
        },
        "system_design_v1_draft": {
            "content_markdown": "# Test System Design\n\nThis is a test system design.",
            "generated_by": "ArchitectAgent",
            "version": "1.0.0"
        },
        "effort_estimate_v1": {
            "roles": [{"role": "Developer", "hours": 100}],
            "total_hours": 100,
            "estimated_duration_weeks": 4,
            "complexity_assessment": "Medium"
        },
        "cost_estimate_v1": {
            "estimated_cost": 10000,
            "currency": "USD",
            "breakdown_by_role": [{"role": "Developer", "hours": 100, "hourly_rate": 100, "total_cost": 10000}]
        },
        "value_projection_v1": {
            "scenarios": [
                {"case": "Low", "value": 5000},
                {"case": "Base", "value": 15000},
                {"case": "High", "value": 30000}
            ],
            "currency": "USD"
        },
        "financial_summary_v1": {
            "total_estimated_cost": 10000,
            "currency": "USD",
            "value_scenarios": {"Low": 5000, "Base": 15000, "High": 30000},
            "financial_metrics": {
                "primary_net_value": 5000,
                "primary_roi_percentage": 50.0,
                "simple_payback_period_years": 2.0
            }
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    print("Create this document in Firestore collection 'businessCases':")
    print(json.dumps(test_case_data, indent=2, default=str))
    
    print(f"\n📋 Test Case Ready for Final Approval")
    print(f"   Case ID: {test_case_data['case_id']}")
    print(f"   Status: {test_case_data['status']}")
    print(f"   Ready for: Submit for final approval")

def main():
    """Main function to run the setup"""
    
    print("🚀 Final Business Case Approval Workflow - Role Setup")
    print("=" * 60)
    
    setup_final_approver_role_instructions()
    create_test_business_case()
    
    print("\n" + "=" * 60)
    print("✅ Setup Instructions Complete")
    print("=" * 60)
    
    print("\n🎯 Summary:")
    print("   1. ✅ FINAL_APPROVER role setup instructions provided")
    print("   2. ✅ Firebase Admin SDK code example included")
    print("   3. ✅ Test business case template provided")
    print("   4. ✅ Verification steps outlined")
    print("   5. ✅ Security considerations documented")
    
    print("\n🔧 Next Actions:")
    print("   1. Run the Firebase Admin SDK code to set up the role")
    print("   2. Create the test business case in Firestore")
    print("   3. Test the complete workflow end-to-end")
    print("   4. Verify role-based UI behavior")

if __name__ == "__main__":
    main() 