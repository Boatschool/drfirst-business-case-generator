#!/usr/bin/env python3
"""
Test script to verify the PlannerAgent and CostAnalystAgent integration
and end-to-end workflow after PRD approval.
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.agents.planner_agent import PlannerAgent
from backend.app.agents.cost_analyst_agent import CostAnalystAgent

async def test_planning_costing_workflow():
    """
    Test the complete planning and costing workflow with sample data.
    """
    print("🧪 DRFIRST BUSINESS CASE GENERATOR - PLANNING & COSTING WORKFLOW TEST")
    print("=" * 80)
    
    # Sample test data
    sample_prd = """
    # Patient Portal Mobile App Enhancement PRD
    
    ## Problem Statement
    Patients need better mobile access to their health information and medication management.
    
    ## Key Features
    - Mobile app with secure login
    - Medication reminders
    - Appointment scheduling
    - Health record access
    """
    
    sample_system_design = """
    # System Design - Patient Portal Mobile App
    
    ## Architecture
    - React Native mobile app
    - Node.js backend API
    - PostgreSQL database
    - AWS cloud infrastructure
    
    ## Security
    - OAuth 2.0 authentication
    - HIPAA compliance
    - Data encryption
    """
    
    case_title = "Patient Portal Mobile Enhancement"
    
    print(f"📋 Testing case: {case_title}")
    print()
    
    # Test 1: PlannerAgent effort estimation
    print("📊 TEST 1: PlannerAgent Effort Estimation")
    print("-" * 50)
    
    try:
        planner = PlannerAgent()
        print(f"✅ PlannerAgent initialized: {planner.name}")
        
        effort_result = await planner.estimate_effort(
            prd_content=sample_prd,
            system_design_content=sample_system_design,
            case_title=case_title
        )
        
        if effort_result["status"] == "success":
            effort_breakdown = effort_result["effort_breakdown"]
            print(f"✅ Effort estimation successful!")
            print(f"   Total Hours: {effort_breakdown['total_hours']}")
            print(f"   Duration: {effort_breakdown['estimated_duration_weeks']} weeks")
            print(f"   Complexity: {effort_breakdown['complexity_assessment']}")
            print("   Role Breakdown:")
            for role in effort_breakdown["roles"]:
                print(f"     - {role['role']}: {role['hours']} hours")
        else:
            print(f"❌ Effort estimation failed: {effort_result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ PlannerAgent test failed: {e}")
        return False
    
    print()
    
    # Test 2: CostAnalystAgent cost calculation
    print("💰 TEST 2: CostAnalystAgent Cost Calculation")
    print("-" * 50)
    
    try:
        cost_analyst = CostAnalystAgent()
        print(f"✅ CostAnalystAgent initialized: {cost_analyst.name}")
        
        cost_result = await cost_analyst.calculate_cost(
            effort_breakdown=effort_breakdown,
            case_title=case_title
        )
        
        if cost_result["status"] == "success":
            cost_estimate = cost_result["cost_estimate"]
            print(f"✅ Cost calculation successful!")
            print(f"   Total Cost: ${cost_estimate['estimated_cost']:,.2f} {cost_estimate['currency']}")
            print(f"   Rate Card: {cost_estimate['rate_card_used']}")
            print(f"   Method: {cost_estimate['calculation_method']}")
            print("   Role Cost Breakdown:")
            for role_cost in cost_estimate["role_breakdown"]:
                print(f"     - {role_cost['role']}: {role_cost['hours']}h × ${role_cost['hourly_rate']}/h = ${role_cost['total_cost']:,.2f}")
        else:
            print(f"❌ Cost calculation failed: {cost_result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ CostAnalystAgent test failed: {e}")
        return False
    
    print()
    
    # Test 3: Integration validation
    print("🔗 TEST 3: Integration Validation")
    print("-" * 50)
    
    # Verify data compatibility
    if effort_breakdown and cost_estimate:
        total_hours_check = sum(role['hours'] for role in effort_breakdown['roles'])
        calculated_cost_check = sum(role['total_cost'] for role in cost_estimate['role_breakdown'])
        
        print(f"✅ Data consistency checks:")
        print(f"   Effort total hours: {total_hours_check} (expected: {effort_breakdown['total_hours']})")
        print(f"   Cost breakdown total: ${calculated_cost_check:,.2f} (expected: ${cost_estimate['estimated_cost']:,.2f})")
        
        if total_hours_check == effort_breakdown['total_hours'] and abs(calculated_cost_check - cost_estimate['estimated_cost']) < 0.01:
            print("✅ All data consistency checks passed!")
        else:
            print("⚠️  Data consistency issues detected")
            return False
    
    print()
    print("🎉 ALL TESTS PASSED! Planning and costing workflow is ready.")
    return True

async def test_agent_status():
    """
    Test that all agents return proper status information.
    """
    print("\n📡 AGENT STATUS CHECK")
    print("-" * 30)
    
    try:
        planner = PlannerAgent()
        cost_analyst = CostAnalystAgent()
        
        planner_status = planner.get_status()
        cost_analyst_status = cost_analyst.get_status()
        
        print(f"PlannerAgent: {planner_status['name']} - {planner_status['status']}")
        print(f"CostAnalystAgent: {cost_analyst_status['name']} - {cost_analyst_status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent status check failed: {e}")
        return False

async def main():
    """
    Run all tests for the planning and costing workflow.
    """
    try:
        # Run workflow test
        workflow_success = await test_planning_costing_workflow()
        
        # Run status test
        status_success = await test_agent_status()
        
        if workflow_success and status_success:
            print("\n" + "=" * 80)
            print("🎊 COMPLETE SUCCESS: All planning and costing tests passed!")
            print("The system is ready for PRD approval → Planning → Costing workflow.")
            print("=" * 80)
            return True
        else:
            print("\n" + "=" * 80)
            print("❌ Some tests failed. Check the output above for details.")
            print("=" * 80)
            return False
            
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1) 