#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.firestore_service import FirestoreService

async def check_case(case_id):
    fs = FirestoreService()
    case = await fs.get_business_case(case_id)
    
    if not case:
        print(f"❌ Case {case_id} not found")
        return
        
    print(f"Case ID: {case.case_id}")
    print(f"Status: {case.status}")
    print(f"Has effort estimate: {bool(case.effort_estimate_v1)}")
    
    if case.effort_estimate_v1:
        print(f"Effort estimate keys: {list(case.effort_estimate_v1.keys())}")
        print(f"Total hours: {case.effort_estimate_v1.get('total_hours', 'N/A')}")
    else:
        print("No effort estimate found")
    
    print(f"Has system design: {bool(case.system_design_v1_draft)}")
    
    if case.history:
        print(f"\nRecent history (last 3 entries):")
        for entry in case.history[-3:]:
            print(f"  - {entry.get('timestamp', 'N/A')}: {entry.get('content', 'N/A')}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_case_status.py <case_id>")
        sys.exit(1)
    
    case_id = sys.argv[1]
    asyncio.run(check_case(case_id)) 