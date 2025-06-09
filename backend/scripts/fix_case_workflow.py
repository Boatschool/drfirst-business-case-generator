#!/usr/bin/env python3
"""
Quick script to advance a business case through the system design approval workflow.
This will submit the system design for review and then approve it to trigger effort estimation.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Add the parent directory to the Python path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.firestore_service import FirestoreService
from app.agents.orchestrator_agent import BusinessCaseStatus

async def advance_case_workflow(case_id: str):
    """
    Advance a case from SYSTEM_DESIGN_DRAFTED to effort estimation ready.
    
    Args:
        case_id: The business case ID to advance
    """
    firestore_service = FirestoreService()
    
    print(f"Checking case {case_id}...")
    
    # Get current case
    business_case = await firestore_service.get_business_case(case_id)
    if not business_case:
        print(f"❌ Case {case_id} not found!")
        return
    
    current_status = business_case.status.value if hasattr(business_case.status, 'value') else str(business_case.status)
    print(f"Current status: {current_status}")
    
    # Check if case is in SYSTEM_DESIGN_DRAFTED
    if current_status != BusinessCaseStatus.SYSTEM_DESIGN_DRAFTED.value:
        print(f"❌ Case is not in SYSTEM_DESIGN_DRAFTED status. Current: {current_status}")
        return
    
    # Step 1: Submit for review
    print("Step 1: Submitting system design for review...")
    
    history_entry_1 = {
        "timestamp": datetime.now(timezone.utc),
        "source": "SCRIPT",
        "messageType": "STATUS_UPDATE", 
        "content": "System design submitted for review by workflow script",
    }
    
    current_history = business_case.history or []
    current_history.append(history_entry_1)
    
    update_data_1 = {
        "status": BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW.value,
        "updated_at": datetime.now(timezone.utc),
        "history": current_history,
    }
    
    success_1 = await firestore_service.update_business_case(case_id, update_data_1)
    if not success_1:
        print("❌ Failed to submit for review")
        return
    
    print("✅ Step 1 complete: System design submitted for review")
    
    # Step 2: Approve system design  
    print("Step 2: Approving system design...")
    
    history_entry_2 = {
        "timestamp": datetime.now(timezone.utc),
        "source": "SCRIPT",
        "messageType": "SYSTEM_DESIGN_APPROVAL",
        "content": "System design approved by workflow script",
    }
    
    current_history.append(history_entry_2)
    
    update_data_2 = {
        "status": BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value,
        "updated_at": datetime.now(timezone.utc),
        "history": current_history,
    }
    
    success_2 = await firestore_service.update_business_case(case_id, update_data_2)
    if not success_2:
        print("❌ Failed to approve system design")
        return
    
    print("✅ Step 2 complete: System design approved")
    
    # Step 3: Trigger effort estimation
    print("Step 3: Triggering effort estimation...")
    
    from app.agents.orchestrator_agent import OrchestratorAgent
    orchestrator = OrchestratorAgent()
    
    result = await orchestrator.handle_system_design_approval(case_id)
    
    if result.get("status") == "success":
        print(f"✅ Step 3 complete: Effort estimation triggered successfully!")
        print(f"New status: {result.get('new_status')}")
        print(f"🎉 Case {case_id} is now ready for effort estimation!")
    else:
        print(f"❌ Step 3 failed: {result.get('message')}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix_case_workflow.py <case_id>")
        print("Example: python fix_case_workflow.py da8ad3b6-5aea-4a9e-be67-7251eebf2b98")
        sys.exit(1)
    
    case_id = sys.argv[1]
    asyncio.run(advance_case_workflow(case_id)) 