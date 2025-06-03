#!/usr/bin/env python3
"""
End-to-end test for the complete business case workflow including 
PRD approval → System Design → Planning → Costing workflow.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.agents.orchestrator_agent import OrchestratorAgent
from google.cloud import firestore

async def test_complete_business_case_workflow():
    """
    Test the complete workflow from case creation through costing.
    """
    print("🧪 DRFIRST BUSINESS CASE GENERATOR - COMPLETE WORKFLOW TEST")
    print("=" * 80)
    
    try:
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        print(f"✅ OrchestratorAgent initialized")
        
        # Test data
        user_id = "test-user-planning-costing"
        payload = {
            "problemStatement": "DrFirst needs a new patient portal mobile app to improve patient engagement and medication adherence.",
            "projectTitle": "Patient Portal Mobile App v2.0",
            "relevantLinks": [
                {"name": "Current Portal", "url": "https://portal.drfirst.com"},
                {"name": "Mobile Requirements", "url": "https://docs.drfirst.com/mobile-reqs"}
            ]
        }
        
        print(f"📋 TEST 1: Initiating Business Case")
        print("-" * 50)
        
        # Step 1: Initiate business case (this will create PRD)
        initiate_result = await orchestrator.handle_request(
            request_type="initiate_case",
            payload=payload,
            user_id=user_id
        )
        
        if initiate_result["status"] != "success":
            print(f"❌ Case initiation failed: {initiate_result['message']}")
            return False
        
        case_id = initiate_result["caseId"]
        print(f"✅ Business case created: {case_id}")
        print(f"   Initial message: {initiate_result['initialMessage']}")
        
        # Give a moment for the async operations to complete
        await asyncio.sleep(2)
        
        print(f"\n📋 TEST 2: Verify Case Data in Firestore")
        print("-" * 50)
        
        # Verify case was created in Firestore
        db = firestore.Client()
        case_doc = await asyncio.to_thread(db.collection("businessCases").document(case_id).get)
        
        if not case_doc.exists:
            print(f"❌ Case document not found in Firestore")
            return False
        
        case_data = case_doc.to_dict()
        print(f"✅ Case found in Firestore")
        print(f"   Status: {case_data.get('status')}")
        print(f"   Title: {case_data.get('title')}")
        print(f"   Has PRD: {'Yes' if case_data.get('prd_draft') else 'No'}")
        
        # Step 2: Mock PRD approval to trigger system design → planning → costing
        print(f"\n📋 TEST 3: Simulate PRD Approval (Triggers System Design → Planning → Costing)")
        print("-" * 50)
        
        # First update status to PRD_APPROVED manually for testing
        await asyncio.to_thread(
            db.collection("businessCases").document(case_id).update,
            {
                "status": "PRD_APPROVED",
                "updated_at": datetime.now(timezone.utc)
            }
        )
        print(f"✅ Case status updated to PRD_APPROVED")
        
        # Now trigger the PRD approval workflow
        approval_result = await orchestrator.handle_prd_approval(case_id)
        
        if approval_result["status"] != "success":
            print(f"❌ PRD approval workflow failed: {approval_result['message']}")
            return False
        
        print(f"✅ PRD approval workflow completed")
        print(f"   Final status: {approval_result.get('new_status')}")
        print(f"   Message: {approval_result.get('message')}")
        
        # Give time for all async operations to complete
        await asyncio.sleep(3)
        
        print(f"\n📋 TEST 4: Verify Complete Data in Firestore")
        print("-" * 50)
        
        # Verify final case state
        final_case_doc = await asyncio.to_thread(db.collection("businessCases").document(case_id).get)
        final_case_data = final_case_doc.to_dict()
        
        print(f"✅ Final case verification:")
        print(f"   Status: {final_case_data.get('status')}")
        print(f"   Has PRD: {'Yes' if final_case_data.get('prd_draft') else 'No'}")
        print(f"   Has System Design: {'Yes' if final_case_data.get('system_design_v1_draft') else 'No'}")
        print(f"   Has Effort Estimate: {'Yes' if final_case_data.get('effort_estimate_v1') else 'No'}")
        print(f"   Has Cost Estimate: {'Yes' if final_case_data.get('cost_estimate_v1') else 'No'}")
        
        # Verify all components are present
        expected_status = "COSTING_COMPLETE"
        has_all_components = (
            final_case_data.get('status') == expected_status and
            final_case_data.get('prd_draft') and
            final_case_data.get('system_design_v1_draft') and
            final_case_data.get('effort_estimate_v1') and
            final_case_data.get('cost_estimate_v1')
        )
        
        if has_all_components:
            print(f"✅ All workflow components completed successfully!")
            
            # Display financial summary
            effort_data = final_case_data.get('effort_estimate_v1', {})
            cost_data = final_case_data.get('cost_estimate_v1', {})
            
            if effort_data and cost_data:
                print(f"\n💰 FINANCIAL SUMMARY:")
                print(f"   Total Effort: {effort_data.get('total_hours', 'N/A')} hours")
                print(f"   Duration: {effort_data.get('estimated_duration_weeks', 'N/A')} weeks")
                print(f"   Total Cost: ${cost_data.get('estimated_cost', 0):,.2f} {cost_data.get('currency', 'USD')}")
                print(f"   Rate Card: {cost_data.get('rate_card_used', 'N/A')}")
                
                # Show role breakdown
                if cost_data.get('role_breakdown'):
                    print(f"   Role Breakdown:")
                    for role_cost in cost_data['role_breakdown']:
                        print(f"     - {role_cost['role']}: {role_cost['hours']}h @ ${role_cost['hourly_rate']}/h = ${role_cost['total_cost']:,.2f}")
                        
        else:
            print(f"❌ Workflow incomplete!")
            print(f"   Expected status: {expected_status}, Got: {final_case_data.get('status')}")
            return False
        
        print(f"\n📋 TEST 5: Verify History Logs")
        print("-" * 50)
        
        history = final_case_data.get('history', [])
        print(f"✅ History entries: {len(history)}")
        
        # Check for key history entries
        status_updates = [h for h in history if h.get('type') == 'STATUS_UPDATE']
        effort_estimates = [h for h in history if h.get('type') == 'EFFORT_ESTIMATE']
        cost_estimates = [h for h in history if h.get('type') == 'COST_ESTIMATE']
        
        print(f"   Status updates: {len(status_updates)}")
        print(f"   Effort estimates: {len(effort_estimates)}")
        print(f"   Cost estimates: {len(cost_estimates)}")
        
        if len(effort_estimates) >= 1 and len(cost_estimates) >= 1:
            print(f"✅ All expected history entries found")
        else:
            print(f"⚠️  Some history entries missing")
        
        # Cleanup: Delete test case
        await asyncio.to_thread(db.collection("businessCases").document(case_id).delete)
        print(f"\n🧹 Test case {case_id} cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """
    Run the complete end-to-end test.
    """
    try:
        success = await test_complete_business_case_workflow()
        
        if success:
            print("\n" + "=" * 80)
            print("🎊 COMPLETE SUCCESS: End-to-end planning and costing workflow working!")
            print("✅ PRD Approval → System Design → Planning → Costing = COMPLETE")
            print("=" * 80)
            return True
        else:
            print("\n" + "=" * 80)
            print("❌ End-to-end test failed. Check the output above for details.")
            print("=" * 80)
            return False
            
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1) 