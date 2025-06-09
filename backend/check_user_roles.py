#!/usr/bin/env python3
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials/service-account-key.json'
from app.services.firebase_admin_service import FirebaseAdminService

def main():
    admin_service = FirebaseAdminService()
    
    test_users = [
        'test.initiator@drfirst.com',
        'test.prd.approver@drfirst.com', 
        'test.developer@drfirst.com',
        'test.effort.approver@drfirst.com',
        'test.finance@drfirst.com',
        'test.sales@drfirst.com',
        'test.final.approver@drfirst.com'
    ]
    
    print("=== Test User Roles ===")
    for email in test_users:
        try:
            user = admin_service.get_user_by_email(email)
            role = user.custom_claims.get('systemRole', 'No role') if user.custom_claims else 'No role'
            print(f'{email:<35}: {role}')
        except Exception as e:
            print(f'{email:<35}: ERROR - {e}')

if __name__ == "__main__":
    main() 