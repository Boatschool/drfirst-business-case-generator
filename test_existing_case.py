#!/usr/bin/env python3
"""Test planning and costing with existing case"""

import asyncio
import sys
import os
sys.path.append('.')

from backend.app.agents.orchestrator_agent import OrchestratorAgent
from google.cloud import firestore

async def test_existing_case():
    case_id = 'dce63b34-2970-4116-b4da-4f9172811676'
    
    print(f"🧪 Testing planning and costing workflow with existing case: {case_id}")
    
    # First update to PRD_APPROVED
    db = firestore.Client(project='drfirst-business-case-gen')
    await asyncio.to_thread(
        db.collection('businessCases').document(case_id).update,
        {'status': 'PRD_APPROVED'}
    )
    print('✅ Updated case to PRD_APPROVED')
    
    # Now test the workflow
    orchestrator = OrchestratorAgent()
    result = await orchestrator.handle_prd_approval(case_id)
    print(f'✅ Workflow result: {result["status"]}')
    print(f'   Message: {result.get("message", "N/A")}')
    print(f'   Final status: {result.get("new_status", "N/A")}')
    
    # Check final state
    final_doc = await asyncio.to_thread(db.collection('businessCases').document(case_id).get)
    final_data = final_doc.to_dict()
    
    print(f'\n📊 Final case state:')
    print(f'   Status: {final_data.get("status")}')
    print(f'   Has effort estimate: {"Yes" if final_data.get("effort_estimate_v1") else "No"}')
    print(f'   Has cost estimate: {"Yes" if final_data.get("cost_estimate_v1") else "No"}')
    
    if final_data.get('cost_estimate_v1'):
        cost_data = final_data['cost_estimate_v1']
        print(f'   Total cost: ${cost_data.get("estimated_cost", 0):,.2f} {cost_data.get("currency", "USD")}')

if __name__ == "__main__":
    asyncio.run(test_existing_case()) 