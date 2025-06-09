#!/usr/bin/env python3
import firebase_admin
from firebase_admin import auth, credentials

def main():
    cred = credentials.Certificate('credentials/service-account-key.json')
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    test_users = [
        'test.initiator@drfirst.com',
        'test.prd.approver@drfirst.com', 
        'test.developer@drfirst.com',
        'test.effort.approver@drfirst.com',
        'test.finance@drfirst.com',
        'test.sales@drfirst.com',
        'test.final.approver@drfirst.com'
    ]

    print('=== Test User Roles ===')
    for email in test_users:
        try:
            user = auth.get_user_by_email(email)
            role = user.custom_claims.get('systemRole', 'No role') if user.custom_claims else 'No role'
            print(f'{email:<35}: {role}')
        except Exception as e:
            print(f'{email:<35}: ERROR - {e}')

if __name__ == "__main__":
    main() 