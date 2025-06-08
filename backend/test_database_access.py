#!/usr/bin/env python3
"""
Test script to check database access and business case data.
"""

import asyncio
import sys
import traceback
from datetime import datetime

async def test_database_access():
    """Test database access and check for business cases"""
    print("🔍 Testing Database Access")
    print("=" * 50)
    
    try:
        # Import required services
        from app.services.firestore_service import FirestoreService
        from app.services.auth_service import get_auth_service
        
        # Initialize services
        print("🔧 Initializing services...")
        auth_service = get_auth_service()
        if not auth_service.is_initialized:
            auth_service._initialize_firebase()
        
        firestore_service = FirestoreService()
        print("✅ Services initialized")
        
        # Test user ID (you may need to replace this with a real user ID)
        test_user_id = "rwince435@gmail.com"  # Use your actual user ID
        
        print(f"📋 Checking business cases for user: {test_user_id}")
        
        # Get all business cases for the user
        business_cases = await firestore_service.list_business_cases_for_user(test_user_id)
        
        print(f"📊 Found {len(business_cases)} business cases")
        
        if business_cases:
            print("\n📋 Business Cases Found:")
            for i, case in enumerate(business_cases, 1):
                print(f"\n{i}. Case ID: {case.case_id}")
                print(f"   Title: {case.title}")
                print(f"   Status: {case.status}")
                print(f"   Created: {case.created_at}")
                print(f"   Updated: {case.updated_at}")
                print(f"   Problem Statement: {case.problem_statement[:100]}...")
                
                # Check for PRD content
                if case.prd_draft:
                    print(f"   📄 PRD Draft: Available")
                else:
                    print(f"   📄 PRD Draft: Not generated")
                
                # Check for other generated content
                content_status = []
                if case.system_design_v1_draft:
                    content_status.append("System Design")
                if case.effort_estimate_v1:
                    content_status.append("Effort Estimate")
                if case.cost_estimate_v1:
                    content_status.append("Cost Estimate")
                if case.value_projection_v1:
                    content_status.append("Value Projection")
                if case.financial_summary_v1:
                    content_status.append("Financial Summary")
                
                if content_status:
                    print(f"   📊 Generated Content: {', '.join(content_status)}")
                else:
                    print(f"   📊 Generated Content: None")
        else:
            print("\n❌ No business cases found for this user")
            print("💡 This could mean:")
            print("   - Cases were created with a different user ID")
            print("   - Cases are stored in a different collection")
            print("   - Database connection issues")
            print("   - Cases were deleted")
        
        # Test direct Firestore access
        print(f"\n🔍 Testing direct Firestore access...")
        try:
            # Get the raw Firestore client
            db_client = firestore_service._db
            
            # List all documents in the business cases collection
            cases_ref = db_client.collection("businessCases")
            all_docs = list(cases_ref.limit(10).stream())
            
            print(f"📊 Found {len(all_docs)} documents in businessCases collection")
            
            if all_docs:
                print("\n📋 Raw Documents Found:")
                for i, doc in enumerate(all_docs, 1):
                    doc_data = doc.to_dict()
                    print(f"\n{i}. Document ID: {doc.id}")
                    print(f"   Keys: {list(doc_data.keys())}")
                    if 'title' in doc_data:
                        print(f"   Title: {doc_data.get('title', 'N/A')}")
                    if 'user_id' in doc_data:
                        print(f"   User ID: {doc_data.get('user_id', 'N/A')}")
                    if 'status' in doc_data:
                        print(f"   Status: {doc_data.get('status', 'N/A')}")
                    if 'created_at' in doc_data:
                        print(f"   Created: {doc_data.get('created_at', 'N/A')}")
            
        except Exception as direct_error:
            print(f"❌ Direct Firestore access failed: {direct_error}")
            print(f"📊 Traceback: {traceback.format_exc()}")
        
        # Test PRD generation functionality
        print(f"\n🤖 Testing PRD generation capability...")
        try:
            from app.agents.orchestrator_agent import OrchestratorAgent
            orchestrator = OrchestratorAgent()
            print("✅ OrchestratorAgent initialized successfully")
            
            # Check if agents are available
            try:
                pm_agent = orchestrator.product_manager_agent
                print("✅ ProductManagerAgent available")
            except Exception as agent_error:
                print(f"❌ ProductManagerAgent error: {agent_error}")
            
        except Exception as orchestrator_error:
            print(f"❌ OrchestratorAgent error: {orchestrator_error}")
            print(f"📊 Traceback: {traceback.format_exc()}")
        
    except Exception as e:
        print(f"❌ Database access test failed: {e}")
        print(f"📊 Full traceback: {traceback.format_exc()}")

async def main():
    await test_database_access()

if __name__ == "__main__":
    asyncio.run(main()) 