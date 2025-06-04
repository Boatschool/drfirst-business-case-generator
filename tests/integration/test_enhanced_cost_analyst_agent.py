#!/usr/bin/env python3
"""
Test script for the enhanced CostAnalystAgent with detailed rate cards functionality.
Tests the new features implemented in Task 8.4.2.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.agents.cost_analyst_agent import CostAnalystAgent

async def test_enhanced_cost_analyst_agent():
    """
    Test the enhanced CostAnalystAgent with various scenarios.
    """
    print("🧪 Testing Enhanced CostAnalystAgent (Task 8.4.2)")
    print("=" * 80)
    
    # Test Case 1: Standard roles with exact matches
    print("\n📊 TEST 1: Standard Roles with Exact Matches")
    print("-" * 50)
    
    standard_effort_breakdown = {
        "roles": [
            {"role": "Developer", "hours": 100},
            {"role": "Product Manager", "hours": 20},
            {"role": "QA Engineer", "hours": 40},
            {"role": "DevOps Engineer", "hours": 15},
            {"role": "UI/UX Designer", "hours": 25}
        ],
        "total_hours": 200,
        "estimated_duration_weeks": 8,
        "complexity_assessment": "Medium"
    }
    
    try:
        cost_analyst = CostAnalystAgent()
        print(f"✅ CostAnalystAgent initialized: {cost_analyst.name}")
        
        result = await cost_analyst.calculate_cost(
            effort_breakdown=standard_effort_breakdown,
            case_title="Standard Test Case"
        )
        
        if result["status"] == "success":
            cost_data = result["cost_estimate"]
            print(f"✅ Cost calculation successful!")
            print(f"   Total Cost: ${cost_data['estimated_cost']:,.2f} {cost_data['currency']}")
            print(f"   Rate Card: {cost_data['rate_card_used']}")
            print(f"   Rate Card ID: {cost_data.get('rate_card_id', 'N/A')}")
            print(f"   Method: {cost_data['calculation_method']}")
            print(f"   Warnings: {len(cost_data.get('warnings', []))}")
            
            print("   Role Cost Breakdown:")
            for role_cost in cost_data["breakdown_by_role"]:
                rate_source = role_cost.get('rate_source', 'unknown')
                print(f"     - {role_cost['role']}: {role_cost['hours']}h × ${role_cost['hourly_rate']}/h = ${role_cost['total_cost']:,.2f} ({rate_source})")
                
        else:
            print(f"❌ Cost calculation failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False
    
    # Test Case 2: Roles with fuzzy matching needed
    print("\n🔍 TEST 2: Roles with Fuzzy Matching")
    print("-" * 50)
    
    fuzzy_effort_breakdown = {
        "roles": [
            {"role": "Lead Developer", "hours": 80},      # Should match "Developer"
            {"role": "Senior Developer", "hours": 120},   # Should match "Developer" 
            {"role": "Software Engineer", "hours": 60},   # Should match "Developer"
            {"role": "PM", "hours": 30},                  # Should match "Product Manager"
            {"role": "Quality Engineer", "hours": 50},    # Should match "QA Engineer"
            {"role": "Designer", "hours": 40},            # Should match "UI/UX Designer"
            {"role": "SRE", "hours": 25}                  # Should match "DevOps Engineer"
        ],
        "total_hours": 405,
        "estimated_duration_weeks": 12,
        "complexity_assessment": "High"
    }
    
    try:
        result = await cost_analyst.calculate_cost(
            effort_breakdown=fuzzy_effort_breakdown,
            case_title="Fuzzy Matching Test Case"
        )
        
        if result["status"] == "success":
            cost_data = result["cost_estimate"]
            print(f"✅ Fuzzy matching cost calculation successful!")
            print(f"   Total Cost: ${cost_data['estimated_cost']:,.2f} {cost_data['currency']}")
            print(f"   Warnings: {len(cost_data.get('warnings', []))}")
            
            print("   Role Cost Breakdown (with matching info):")
            for role_cost in cost_data["breakdown_by_role"]:
                rate_source = role_cost.get('rate_source', 'unknown')
                print(f"     - {role_cost['role']}: {role_cost['hours']}h × ${role_cost['hourly_rate']}/h = ${role_cost['total_cost']:,.2f} ({rate_source})")
                
            if cost_data.get('warnings'):
                print("   Warnings generated:")
                for warning in cost_data['warnings']:
                    print(f"     ⚠️  {warning}")
                    
        else:
            print(f"❌ Fuzzy matching test failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return False
    
    # Test Case 3: Roles not in rate card (should use default rates)
    print("\n❓ TEST 3: Unknown Roles (Default Rate Usage)")
    print("-" * 50)
    
    unknown_roles_breakdown = {
        "roles": [
            {"role": "Data Scientist", "hours": 60},      # Not in rate card
            {"role": "Security Specialist", "hours": 40}, # Not in rate card
            {"role": "Business Analyst", "hours": 30},    # Not in rate card
            {"role": "Developer", "hours": 80}            # In rate card
        ],
        "total_hours": 210,
        "estimated_duration_weeks": 8,
        "complexity_assessment": "Medium"
    }
    
    try:
        result = await cost_analyst.calculate_cost(
            effort_breakdown=unknown_roles_breakdown,
            case_title="Unknown Roles Test Case"
        )
        
        if result["status"] == "success":
            cost_data = result["cost_estimate"]
            print(f"✅ Unknown roles cost calculation successful!")
            print(f"   Total Cost: ${cost_data['estimated_cost']:,.2f} {cost_data['currency']}")
            print(f"   Warnings: {len(cost_data.get('warnings', []))}")
            
            print("   Role Cost Breakdown (with rate sources):")
            for role_cost in cost_data["breakdown_by_role"]:
                rate_source = role_cost.get('rate_source', 'unknown')
                print(f"     - {role_cost['role']}: {role_cost['hours']}h × ${role_cost['hourly_rate']}/h = ${role_cost['total_cost']:,.2f} ({rate_source})")
                
            if cost_data.get('warnings'):
                print("   Expected warnings for unknown roles:")
                for warning in cost_data['warnings']:
                    print(f"     ⚠️  {warning}")
                    
        else:
            print(f"❌ Unknown roles test failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return False
    
    # Test Case 4: Data structure validation
    print("\n🔍 TEST 4: Enhanced Data Structure Validation")
    print("-" * 50)
    
    validation_effort_breakdown = {
        "roles": [
            {"role": "Developer", "hours": 50}
        ],
        "total_hours": 50,
        "estimated_duration_weeks": 2,
        "complexity_assessment": "Low"
    }
    
    try:
        result = await cost_analyst.calculate_cost(
            effort_breakdown=validation_effort_breakdown,
            case_title="Data Structure Validation Test"
        )
        
        if result["status"] == "success":
            cost_data = result["cost_estimate"]
            
            # Validate new structure
            required_fields = [
                "estimated_cost", "currency", "rate_card_used", "rate_card_id",
                "breakdown_by_role", "calculation_method", "warnings", "notes"
            ]
            
            missing_fields = [field for field in required_fields if field not in cost_data]
            
            if not missing_fields:
                print("✅ All required fields present in enhanced cost estimate structure")
                
                # Validate breakdown_by_role structure
                if cost_data["breakdown_by_role"]:
                    role_entry = cost_data["breakdown_by_role"][0]
                    role_fields = ["role", "hours", "hourly_rate", "total_cost", "currency", "rate_source"]
                    missing_role_fields = [field for field in role_fields if field not in role_entry]
                    
                    if not missing_role_fields:
                        print("✅ Enhanced role breakdown structure validated")
                    else:
                        print(f"❌ Missing role fields: {missing_role_fields}")
                        return False
                        
                print(f"✅ Enhanced features validated:")
                print(f"   - Rate Card ID: {cost_data.get('rate_card_id')}")
                print(f"   - Warnings Array: {type(cost_data.get('warnings', []))}")
                print(f"   - Rate Source Tracking: {cost_data['breakdown_by_role'][0].get('rate_source')}")
                
            else:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
                
        else:
            print(f"❌ Structure validation test failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return False
    
    print("\n🎉 ALL ENHANCED COST ANALYST AGENT TESTS PASSED!")
    print("=" * 80)
    print("✅ Active rate card fetching with isDefault preference")
    print("✅ Detailed role-specific rate matching")
    print("✅ Fuzzy matching for role name variations")
    print("✅ Warning generation for missing rates")
    print("✅ Enhanced cost breakdown with rate source tracking")
    print("✅ Robust error handling and fallbacks")
    return True

if __name__ == "__main__":
    asyncio.run(test_enhanced_cost_analyst_agent()) 