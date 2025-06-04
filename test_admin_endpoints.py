#!/usr/bin/env python3
"""
Test script for admin endpoints
Tests the new rate cards and pricing templates admin endpoints
"""

import asyncio
import requests
import sys
import json

# Configure the base URL for testing
BASE_URL = "http://localhost:8000"

async def test_admin_endpoints():
    """Test the admin endpoints"""
    print("🧪 Testing Admin Endpoints for DrFirst Business Case Generator")
    print("=" * 70)
    
    try:
        # Test 1: Health check
        print("\n1. Testing health endpoint...")
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
        
        # Test 2: Rate cards endpoint (without auth - should fail)
        print("\n2. Testing rate cards endpoint without authentication...")
        response = requests.get(f"{BASE_URL}/api/v1/admin/rate-cards")
        if response.status_code == 401:
            print("   ✅ Rate cards endpoint properly requires authentication")
        else:
            print(f"   ❌ Rate cards endpoint should require auth but returned: {response.status_code}")
        
        # Test 3: Pricing templates endpoint (without auth - should fail)
        print("\n3. Testing pricing templates endpoint without authentication...")
        response = requests.get(f"{BASE_URL}/api/v1/admin/pricing-templates")
        if response.status_code == 401:
            print("   ✅ Pricing templates endpoint properly requires authentication")
        else:
            print(f"   ❌ Pricing templates endpoint should require auth but returned: {response.status_code}")
        
        # Test 4: Check if Firestore has data
        print("\n4. Checking for existing Firestore data...")
        try:
            from google.cloud import firestore
            db = firestore.Client()
            
            # Check rate cards
            rate_cards_count = len(list(db.collection("rateCards").stream()))
            print(f"   📊 Found {rate_cards_count} rate card(s) in Firestore")
            
            # Check pricing templates
            templates_count = len(list(db.collection("pricingTemplates").stream()))
            print(f"   📊 Found {templates_count} pricing template(s) in Firestore")
            
            if rate_cards_count == 0:
                print("   💡 Hint: Run 'python scripts/setup_firestore_rate_card.py' to create sample rate card")
                
            if templates_count == 0:
                print("   💡 Hint: Run 'python setup_firestore_pricing_template.py' to create sample pricing template")
                
        except Exception as e:
            print(f"   ⚠️  Could not check Firestore data: {e}")
        
        print("\n🎉 Admin endpoints test completed!")
        print("\n📝 To test with authentication:")
        print("   1. Start the backend server: cd backend && python -m uvicorn app.main:app --reload")
        print("   2. Start the frontend: cd frontend && npm run dev")
        print("   3. Sign in to the frontend and navigate to /admin")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_admin_endpoints()) 