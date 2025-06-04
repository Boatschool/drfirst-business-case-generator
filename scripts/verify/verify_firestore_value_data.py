#!/usr/bin/env python3
"""
Script to verify that value projection data was properly stored in Firestore.
"""

import asyncio
import sys
import os
import json

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from google.cloud import firestore
from backend.app.core.config import settings

async def verify_value_data():
    """Verify value projection data in Firestore."""
    print("🔍 Verifying Value Projection Data in Firestore...")
    print("=" * 60)
    
    try:
        # Initialize Firestore client
        db = firestore.Client(project=settings.firebase_project_id)
        print("✅ Firestore client initialized")
        
        # Query for the most recent business cases
        print("\n📊 Searching for recent business cases...")
        
        cases_ref = db.collection("businessCases")
        query = cases_ref.order_by("updated_at", direction=firestore.Query.DESCENDING).limit(5)
        
        docs = await asyncio.to_thread(query.get)
        
        if not docs:
            print("❌ No business cases found")
            return
        
        # Filter for cases with value projection data
        cases_with_value = [doc for doc in docs if doc.to_dict().get("value_projection_v1")]
        
        print(f"✅ Found {len(docs)} business case(s), {len(cases_with_value)} with value projection data")
        
        for i, doc in enumerate(cases_with_value, 1):
            case_data = doc.to_dict()
            case_id = doc.id
            
            print(f"\n📋 Business Case #{i}: {case_id}")
            print(f"   Title: {case_data.get('title', 'Unknown')}")
            print(f"   Status: {case_data.get('status', 'Unknown')}")
            print(f"   Updated: {case_data.get('updated_at', 'Unknown')}")
            
            # Check value projection data
            value_projection = case_data.get("value_projection_v1")
            if value_projection:
                print(f"\n   💰 Value Projection:")
                print(f"   Template Used: {value_projection.get('template_used')}")
                print(f"   Currency: {value_projection.get('currency')}")
                print(f"   Methodology: {value_projection.get('methodology')}")
                
                scenarios = value_projection.get("scenarios", [])
                print(f"   Scenarios:")
                for scenario in scenarios:
                    print(f"     • {scenario.get('case')}: ${scenario.get('value'):,} - {scenario.get('description')}")
                
                assumptions = value_projection.get("assumptions", [])
                if assumptions:
                    print(f"   Assumptions:")
                    for assumption in assumptions[:2]:  # Show first 2 assumptions
                        print(f"     • {assumption}")
                    if len(assumptions) > 2:
                        print(f"     ... and {len(assumptions) - 2} more")
                
                print(f"   Notes: {value_projection.get('notes', 'None')[:100]}...")
            
            # Check other financial data for comparison
            effort_estimate = case_data.get("effort_estimate_v1")
            cost_estimate = case_data.get("cost_estimate_v1")
            
            if effort_estimate:
                total_hours = effort_estimate.get("total_hours", "Unknown")
                print(f"\n   ⏱️  Effort Estimate: {total_hours} hours")
            
            if cost_estimate:
                estimated_cost = cost_estimate.get("estimated_cost", "Unknown")
                currency = cost_estimate.get("currency", "")
                print(f"   💵 Cost Estimate: ${estimated_cost:,} {currency}" if isinstance(estimated_cost, (int, float)) else f"   💵 Cost Estimate: {estimated_cost}")
            
            # Calculate simple ROI based on base scenario if available
            if value_projection and cost_estimate:
                try:
                    scenarios = value_projection.get("scenarios", [])
                    base_scenario = next((s for s in scenarios if s.get("case") == "Base"), None)
                    if base_scenario and isinstance(estimated_cost, (int, float)):
                        base_value = base_scenario.get("value", 0)
                        roi_percentage = ((base_value - estimated_cost) / estimated_cost) * 100
                        print(f"   📈 Simple ROI (Base scenario): {roi_percentage:.1f}%")
                except:
                    pass
            
            print("-" * 60)
        
        print("\n✅ Firestore verification completed successfully!")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_value_data()) 