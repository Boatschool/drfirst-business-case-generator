#!/usr/bin/env python3
"""
Setup script for initializing global final approver role configuration in Firestore
"""

import firebase_admin
from firebase_admin import firestore
from datetime import datetime, timezone
import sys
import os

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if already initialized
        firebase_admin.get_app()
        print("✅ Firebase Admin SDK already initialized")
    except ValueError:
        # Initialize Firebase Admin SDK
        firebase_admin.initialize_app()
        print("✅ Firebase Admin SDK initialized")

def setup_global_approver_config():
    """Set up the global final approver role configuration in Firestore"""
    
    initialize_firebase()
    
    # Get Firestore client
    db = firestore.client()
    
    # Configuration document
    config_data = {
        "finalApproverRoleName": "FINAL_APPROVER",  # Default to existing role
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
        "description": "Global configuration for which systemRole acts as the final approver for business cases"
    }
    
    try:
        # Check if configuration already exists
        doc_ref = db.collection("systemConfiguration").document("approvalSettings")
        doc = doc_ref.get()
        
        if doc.exists:
            existing_data = doc.to_dict()
            current_role = existing_data.get("finalApproverRoleName", "NONE")
            print(f"⚠️  Configuration already exists!")
            print(f"   Current final approver role: {current_role}")
            
            # Ask if user wants to update
            response = input("   Do you want to update it? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("   ❌ Skipping configuration update")
                return False
        
        # Create or update the configuration
        doc_ref.set(config_data)
        print(f"✅ Global approver configuration created/updated successfully!")
        print(f"   Final approver role set to: {config_data['finalApproverRoleName']}")
        print(f"   Document path: systemConfiguration/approvalSettings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up configuration: {e}")
        return False

def verify_configuration():
    """Verify the configuration was set up correctly"""
    
    try:
        db = firestore.client()
        doc_ref = db.collection("systemConfiguration").document("approvalSettings")
        doc = doc_ref.get()
        
        if doc.exists:
            config_data = doc.to_dict()
            print("\n📋 Configuration Verification:")
            print(f"   ✅ Document exists: systemConfiguration/approvalSettings")
            print(f"   ✅ Final Approver Role: {config_data.get('finalApproverRoleName')}")
            print(f"   ✅ Created At: {config_data.get('createdAt')}")
            print(f"   ✅ Updated At: {config_data.get('updatedAt')}")
            return True
        else:
            print("\n❌ Configuration document not found!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error verifying configuration: {e}")
        return False

def print_usage_instructions():
    """Print instructions for using the new configuration system"""
    
    print("\n" + "="*60)
    print("📚 GLOBAL FINAL APPROVER CONFIGURATION SETUP COMPLETE")
    print("="*60)
    
    print("\n🎯 What was configured:")
    print("   • Created systemConfiguration/approvalSettings document in Firestore")
    print("   • Set default finalApproverRoleName to 'FINAL_APPROVER'")
    print("   • This setting can now be changed via the Admin UI")
    
    print("\n🔧 Next Steps:")
    print("   1. Deploy the updated backend with new admin endpoints")
    print("   2. Deploy the updated frontend with admin UI")
    print("   3. Log in as an Admin user and navigate to /admin")
    print("   4. Use the 'Global Approval Settings' section to change the role")
    
    print("\n🔐 Available System Roles:")
    roles = [
        "ADMIN - Can approve and has all permissions",
        "DEVELOPER - Can approve system designs", 
        "SALES_MANAGER_APPROVER - Can approve value projections",
        "FINAL_APPROVER - Traditional final approver role",
        "CASE_INITIATOR - Basic user role"
    ]
    for role in roles:
        print(f"   • {role}")
    
    print("\n⚠️  Security Notes:")
    print("   • Only users with ADMIN systemRole can change this setting")
    print("   • The change affects ALL business case final approvals")
    print("   • Test thoroughly before using in production")
    
    print("\n🧪 Testing:")
    print("   1. Set final approver role to 'ADMIN' in admin UI")
    print("   2. Create a test business case and complete all stages")
    print("   3. Verify only ADMIN users can approve/reject the final case")
    print("   4. Change setting back to 'FINAL_APPROVER' if needed")

def main():
    """Main execution function"""
    
    print("🚀 Setting up Global Final Approver Role Configuration")
    print("="*60)
    
    # Setup configuration
    success = setup_global_approver_config()
    
    if success:
        # Verify configuration
        verify_configuration()
        
        # Print usage instructions
        print_usage_instructions()
        
        print(f"\n✅ Setup completed successfully!")
        
    else:
        print(f"\n❌ Setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 