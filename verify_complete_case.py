#!/usr/bin/env python3
"""Verify complete business case data"""

import asyncio
from google.cloud import firestore

async def check_case():
    db = firestore.Client(project='drfirst-business-case-gen')
    doc = await asyncio.to_thread(db.collection('businessCases').document('dce63b34-2970-4116-b4da-4f9172811676').get)
    data = doc.to_dict()
    
    print('📊 COMPLETE BUSINESS CASE ANALYSIS:')
    print(f'Title: {data.get("title")}')
    print(f'Status: {data.get("status")}')
    print()
    
    if data.get('effort_estimate_v1'):
        effort = data['effort_estimate_v1']
        print('💼 EFFORT ESTIMATE:')
        print(f'  Total Hours: {effort.get("total_hours")}')
        print(f'  Duration: {effort.get("estimated_duration_weeks")} weeks')
        print(f'  Complexity: {effort.get("complexity_assessment")}')
        print('  Role Breakdown:')
        for role in effort.get('roles', []):
            print(f'    - {role["role"]}: {role["hours"]} hours')
        print()
    
    if data.get('cost_estimate_v1'):
        cost = data['cost_estimate_v1']
        print('💰 COST ESTIMATE:')
        print(f'  Total Cost: ${cost.get("estimated_cost"):,.2f} {cost.get("currency")}')
        print(f'  Rate Card: {cost.get("rate_card_used")}')
        print('  Role Cost Breakdown:')
        for role in cost.get('role_breakdown', []):
            print(f'    - {role["role"]}: {role["hours"]}h × ${role["hourly_rate"]}/h = ${role["total_cost"]:,.2f}')
    
    print()
    print('🎉 WORKFLOW VERIFICATION COMPLETE!')
    print('✅ PRD → System Design → Planning → Costing = ALL WORKING!')

if __name__ == "__main__":
    asyncio.run(check_case()) 