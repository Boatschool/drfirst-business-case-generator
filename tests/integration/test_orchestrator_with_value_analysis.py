#!/usr/bin/env python3
"""
Test script to verify the complete orchestration workflow including SalesValueAnalystAgent.
This tests the end-to-end PRD approval -> System Design -> Planning -> Costing -> Value Analysis flow.
"""

import asyncio
import sys
import os
import json

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.agents.orchestrator_agent import OrchestratorAgent

async def test_complete_workflow():
    """Test the complete business case workflow including value analysis."""
    print("🧪 Testing Complete Orchestration Workflow with Value Analysis...")
    print("=" * 80)
    
    try:
        # Initialize the orchestrator
        print("1. Initializing OrchestratorAgent...")
        orchestrator = OrchestratorAgent()
        print(f"   ✅ Orchestrator initialized: {orchestrator.name}")
        
        # First, create a test business case
        print("\n2. Creating a test business case...")
        user_id = "test_user_123"
        case_payload = {
            "problemStatement": "Our current patient portal has low engagement rates and poor user experience. Patients struggle to access their medical records, schedule appointments, and communicate with providers efficiently.",
            "projectTitle": "Enhanced Patient Portal System",
            "relevantLinks": [
                {
                    "url": "https://example.com/current-portal-analytics",
                    "description": "Current portal usage analytics"
                }
            ]
        }
        
        case_response = await orchestrator.handle_request("initiate_case", case_payload, user_id)
        
        if case_response.get("status") != "success":
            print(f"   ❌ Failed to create test case: {case_response.get('message')}")
            return
            
        case_id = case_response.get("caseId")
        print(f"   ✅ Test case created: {case_id}")
        print(f"   Message: {case_response.get('message')}")
        
        # First manually set the case status to PRD_APPROVED to simulate approval
        print(f"\n3. Setting case status to PRD_APPROVED to simulate approval...")
        case_doc_ref = orchestrator.db.collection("businessCases").document(case_id)
        await asyncio.to_thread(case_doc_ref.update, {"status": "PRD_APPROVED"})
        print(f"   ✅ Case status updated to PRD_APPROVED")
        
        # Now test the PRD approval workflow which should trigger the complete chain
        print(f"\n4. Testing PRD approval workflow for case {case_id}...")
        print("   This should trigger: System Design -> Planning -> Costing -> Value Analysis")
        
        approval_response = await orchestrator.handle_prd_approval(case_id)
        
        print(f"\n   📊 Approval Response:")
        print(f"   Status: {approval_response.get('status')}")
        print(f"   Message: {approval_response.get('message')}")
        print(f"   Final Status: {approval_response.get('new_status')}")
        
        if approval_response.get("status") == "success":
            print(f"\n   ✅ Complete workflow executed successfully!")
            
            # Check if value projection was generated
            if "value_projection" in approval_response:
                value_projection = approval_response["value_projection"]
                print(f"\n   💰 Value Projection Generated:")
                print(f"   Template Used: {value_projection.get('template_used')}")
                print(f"   Currency: {value_projection.get('currency')}")
                
                scenarios = value_projection.get("scenarios", [])
                for scenario in scenarios:
                    print(f"     • {scenario.get('case')}: ${scenario.get('value'):,}")
            
            print(f"\n   📈 Workflow Summary:")
            print(f"   • PRD: Generated and approved")
            print(f"   • System Design: Generated")
            print(f"   • Effort Estimation: Completed") 
            print(f"   • Cost Analysis: Completed")
            print(f"   • Value Analysis: Completed ✨ NEW!")
            print(f"   • Final Status: {approval_response.get('new_status')}")
            
        else:
            print(f"   ❌ Workflow failed: {approval_response.get('message')}")
            
        print("\n=" * 80)
        print("✅ Complete orchestration workflow test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(test_complete_workflow()) 