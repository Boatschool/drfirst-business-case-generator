#!/usr/bin/env python3
"""
Test script to verify that financial estimates are included in the API response
"""

import asyncio
import requests
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_financial_api_response():
    """Test that the API includes financial estimates in case details."""
    
    # We'll need to use a real case ID that has financial data
    # Based on the dev logs, this case should have complete financial data:
    test_case_id = "dce63b34-2970-4116-b4da-4f9172811676"
    
    # Test the API endpoint (assuming backend is running on localhost:8000)
    api_url = f"http://localhost:8000/api/v1/cases/{test_case_id}"
    
    print("🧪 Testing Financial API Response")
    print("=" * 50)
    print(f"📋 Testing case: {test_case_id}")
    print(f"🌐 API URL: {api_url}")
    
    try:
        # Make request to API (this would normally need authentication)
        print("\n📡 Making API request...")
        response = requests.get(api_url)
        
        if response.status_code == 401:
            print("⚠️  Authentication required - this is expected")
            print("   In the frontend, this request would include a Firebase ID token")
            print("   The API structure test can still be performed with direct database access")
            return
        
        if response.status_code != 200:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return
        
        # Parse response
        case_data = response.json()
        
        print("✅ API request successful!")
        print("\n📊 Checking for financial estimate fields...")
        
        # Check for effort estimate
        if case_data.get("effort_estimate_v1"):
            effort = case_data["effort_estimate_v1"]
            print(f"✅ Effort Estimate found:")
            print(f"   Total Hours: {effort.get('total_hours')}")
            print(f"   Duration: {effort.get('estimated_duration_weeks')} weeks")
            print(f"   Roles: {len(effort.get('roles', []))} roles defined")
        else:
            print("❌ Effort Estimate not found in API response")
        
        # Check for cost estimate
        if case_data.get("cost_estimate_v1"):
            cost = case_data["cost_estimate_v1"]
            print(f"✅ Cost Estimate found:")
            print(f"   Total Cost: ${cost.get('estimated_cost'):,.2f} {cost.get('currency')}")
            print(f"   Rate Card: {cost.get('rate_card_used')}")
            print(f"   Role Breakdown: {len(cost.get('role_breakdown', []))} roles")
        else:
            print("❌ Cost Estimate not found in API response")
        
        # Check for value projection
        if case_data.get("value_projection_v1"):
            value = case_data["value_projection_v1"]
            print(f"✅ Value Projection found:")
            print(f"   Template: {value.get('template_used')}")
            print(f"   Scenarios: {len(value.get('scenarios', []))} scenarios")
            for scenario in value.get('scenarios', []):
                print(f"     - {scenario.get('case')}: ${scenario.get('value'):,}")
        else:
            print("❌ Value Projection not found in API response")
        
        # Summary
        has_all_financial = all([
            case_data.get("effort_estimate_v1"),
            case_data.get("cost_estimate_v1"),
            case_data.get("value_projection_v1")
        ])
        
        print(f"\n📋 Summary:")
        print(f"   Complete Financial Data: {'✅ Yes' if has_all_financial else '❌ No'}")
        print(f"   API Response Ready for Frontend: {'✅ Yes' if has_all_financial else '❌ No'}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend API")
        print("   Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_financial_api_response()) 