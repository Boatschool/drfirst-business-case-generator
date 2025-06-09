#!/usr/bin/env python3
"""
Script to manually trigger effort estimation for a case in SYSTEM_DESIGN_APPROVED status.
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.agents.orchestrator_agent import OrchestratorAgent, BusinessCaseStatus
from app.services.firestore_service import FirestoreService

async def trigger_effort_estimation(case_id: str):
    """
    Trigger effort estimation for a case in SYSTEM_DESIGN_APPROVED status.
    
    Args:
        case_id: The business case ID
    """
    # First check the case status
    firestore_service = FirestoreService()
    business_case = await firestore_service.get_business_case(case_id)
    
    if not business_case:
        print(f"❌ Case {case_id} not found!")
        return
    
    current_status = business_case.status.value if hasattr(business_case.status, 'value') else str(business_case.status)
    print(f"Current status: {current_status}")
    
    if current_status != BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value:
        print(f"❌ Case is not in SYSTEM_DESIGN_APPROVED status. Current: {current_status}")
        return
    
    if business_case.effort_estimate_v1:
        print(f"⚠️  Case already has effort estimate. Total hours: {business_case.effort_estimate_v1.get('total_hours', 'N/A')}")
        return
    
    print("✅ Case is ready for effort estimation")
    print("🚀 Triggering effort estimation...")
    
    # Trigger effort estimation
    orchestrator = OrchestratorAgent()
    result = await orchestrator.handle_system_design_approval(case_id)
    
    if result.get("status") == "success":
        print(f"✅ Effort estimation completed successfully!")
        print(f"New status: {result.get('new_status')}")
        
        # Check the result
        updated_case = await firestore_service.get_business_case(case_id)
        if updated_case.effort_estimate_v1:
            print(f"📊 Total estimated hours: {updated_case.effort_estimate_v1.get('total_hours', 'N/A')}")
            print(f"📅 Estimated duration: {updated_case.effort_estimate_v1.get('estimated_duration_weeks', 'N/A')} weeks")
            print(f"🔍 Complexity: {updated_case.effort_estimate_v1.get('complexity_assessment', 'N/A')}")
        
    else:
        print(f"❌ Effort estimation failed: {result.get('message')}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python trigger_effort_estimation.py <case_id>")
        print("Example: python trigger_effort_estimation.py da8ad3b6-5aea-4a9e-be67-7251eebf2b98")
        sys.exit(1)
    
    case_id = sys.argv[1]
    asyncio.run(trigger_effort_estimation(case_id)) 