#!/usr/bin/env python3
"""
Standalone Admin Access Grant Script

This script grants admin access to a user without requiring the full backend setup.
It only requires firebase-admin to be installed.
"""

import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 grant_admin_access.py <email>")
        print("Example: python3 grant_admin_access.py user@drfirst.com")
        sys.exit(1)
    
    email = sys.argv[1]
    
    try:
        import firebase_admin
        from firebase_admin import auth, credentials, firestore
        print("✅ Firebase Admin SDK is available")
    except ImportError:
        print("❌ Firebase Admin SDK not found. Please install it:")
        print("pip install firebase-admin")
        sys.exit(1)
    
    try:
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            # Look for service account key
            key_paths = [
                'credentials/drfirst-business-case-gen-firebase-adminsdk.json',
                'backend/credentials/drfirst-business-case-gen-firebase-adminsdk.json',
                'config/firebase/service-account-key.json'
            ]
            
            service_account_path = None
            for path in key_paths:
                if Path(path).exists():
                    service_account_path = path
                    break
            
            if service_account_path:
                print(f"📋 Using service account: {service_account_path}")
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
            else:
                print("🔄 Attempting to use default credentials (Application Default Credentials)")
                firebase_admin.initialize_app()
        
        print(f"🔍 Looking up user: {email}")
        
        # Get user by email
        try:
            user_record = auth.get_user_by_email(email)
            print(f"✅ Found user: {user_record.uid}")
        except auth.UserNotFoundError:
            print(f"❌ User not found: {email}")
            print("Make sure the user has signed in to the application at least once.")
            sys.exit(1)
        
        # Set custom claims
        print(f"🔧 Setting ADMIN role for user {email}")
        auth.set_custom_user_claims(user_record.uid, {
            'systemRole': 'ADMIN'
        })
        
        print(f"✅ Successfully granted ADMIN role to {email}")
        print(f"🔄 User will need to refresh their browser or sign out/in to get the new permissions")
        
        # Optional: Also update Firestore if accessible
        try:
            db = firestore.client()
            user_doc_ref = db.collection('users').document(user_record.uid)
            user_doc_ref.set({
                'uid': user_record.uid,
                'email': email,
                'display_name': user_record.display_name,
                'system_role': 'ADMIN',
                'is_active': True,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }, merge=True)
            print(f"✅ Also updated Firestore user document")
        except Exception as e:
            print(f"⚠️ Could not update Firestore (this is optional): {e}")
        
        print("\n🎉 Admin access granted successfully!")
        print("\nNext steps:")
        print("1. Go to https://drfirst-business-case-gen.web.app")
        print("2. Refresh the page or sign out and sign back in")
        print("3. Navigate to the Admin page - you should now have access")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 