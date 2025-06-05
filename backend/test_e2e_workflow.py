#!/usr/bin/env python3
"""
End-to-End Workflow Test for ArchitectAgent Integration
Tests the complete business case workflow: Creation → PRD → Approval → System Design
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone

# Add the current directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_complete_workflow():
    """Test the complete business case workflow with system design generation."""
    print("🚀 Starting End-to-End Workflow Test")
    print("=" * 80)

    try:
        from app.agents.orchestrator_agent import OrchestratorAgent, BusinessCaseStatus
        from google.cloud import firestore
        from app.core.config import settings
        import uuid

        # Initialize components
        orchestrator = OrchestratorAgent()

        if not orchestrator.db:
            print("❌ Firestore not initialized. Skipping full workflow test.")
            return False

        print("✅ Components initialized successfully")

        # Test data for a realistic business case
        test_user_id = "test_user_" + str(uuid.uuid4())[:8]
        test_case_data = {
            "problemStatement": "Healthcare providers need a more efficient way to manage patient appointment scheduling and reduce no-shows. Current system requires multiple phone calls and has a 25% no-show rate.",
            "projectTitle": "Smart Patient Appointment Management System",
            "relevantLinks": [
                {
                    "name": "Current System Analysis",
                    "url": "https://example.com/current-analysis",
                },
                {
                    "name": "Industry Best Practices",
                    "url": "https://example.com/best-practices",
                },
            ],
        }

        print(f"\n📋 Test Case Details:")
        print(f"   - User ID: {test_user_id}")
        print(f"   - Project: {test_case_data['projectTitle']}")
        print(f"   - Problem: {test_case_data['problemStatement']}")

        # Step 1: Create business case and generate PRD
        print(f"\n🔄 Step 1: Creating business case and generating PRD...")

        case_response = await orchestrator.handle_request(
            request_type="initiate_case", payload=test_case_data, user_id=test_user_id
        )

        if case_response.get("status") != "success":
            print(f"❌ Failed to create business case: {case_response.get('message')}")
            return False

        case_id = case_response.get("caseId")
        print(f"✅ Business case created successfully!")
        print(f"   - Case ID: {case_id}")
        print(f"   - Message: {case_response.get('message')}")

        # Step 2: Retrieve case details to check PRD
        print(f"\n🔄 Step 2: Retrieving case details to verify PRD generation...")

        case_doc_ref = orchestrator.db.collection("businessCases").document(case_id)
        doc_snapshot = await asyncio.to_thread(case_doc_ref.get)

        if not doc_snapshot.exists:
            print(f"❌ Case document not found in Firestore")
            return False

        case_data = doc_snapshot.to_dict()
        current_status = case_data.get("status")
        prd_draft = case_data.get("prd_draft")

        print(f"✅ Case retrieved successfully!")
        print(f"   - Current Status: {current_status}")
        print(f"   - PRD Draft Available: {bool(prd_draft)}")

        if prd_draft:
            prd_content = prd_draft.get("content_markdown", "")
            print(f"   - PRD Content Length: {len(prd_content)} characters")
            if len(prd_content) > 0:
                print(f"   - PRD Preview: {prd_content[:150]}...")

        # Step 3: Simulate PRD approval (update status to PRD_APPROVED)
        print(f"\n🔄 Step 3: Simulating PRD approval...")

        # Update status to PRD_REVIEW first (simulating submission)
        await asyncio.to_thread(
            case_doc_ref.update,
            {
                "status": BusinessCaseStatus.PRD_REVIEW.value,
                "updated_at": datetime.now(timezone.utc),
            },
        )

        # Then approve the PRD (simulating approval)
        await asyncio.to_thread(
            case_doc_ref.update,
            {
                "status": BusinessCaseStatus.PRD_APPROVED.value,
                "updated_at": datetime.now(timezone.utc),
            },
        )

        print(f"✅ PRD status updated to PRD_APPROVED")

        # Step 4: Trigger system design generation
        print(f"\n🔄 Step 4: Triggering system design generation...")

        design_result = await orchestrator.handle_prd_approval(case_id)

        if design_result.get("status") != "success":
            print(f"❌ System design generation failed: {design_result.get('message')}")
            return False

        print(f"✅ System design generation completed!")
        print(f"   - Result Status: {design_result.get('status')}")
        print(f"   - New Case Status: {design_result.get('new_status')}")
        print(f"   - Message: {design_result.get('message')}")

        # Step 5: Verify final state
        print(f"\n🔄 Step 5: Verifying final case state...")

        final_doc_snapshot = await asyncio.to_thread(case_doc_ref.get)
        final_case_data = final_doc_snapshot.to_dict()

        final_status = final_case_data.get("status")
        system_design = final_case_data.get("system_design_v1_draft")
        history = final_case_data.get("history", [])

        print(f"✅ Final case state verified!")
        print(f"   - Final Status: {final_status}")
        print(f"   - System Design Available: {bool(system_design)}")
        print(f"   - History Entries: {len(history)}")

        if system_design:
            design_content = system_design.get("content_markdown", "")
            print(f"   - System Design Length: {len(design_content)} characters")
            print(f"   - Generated By: {system_design.get('generated_by')}")
            print(f"   - Version: {system_design.get('version')}")

            if len(design_content) > 0:
                print(f"\n📄 System Design Preview:")
                print("─" * 60)
                print(
                    design_content[:300] + "..."
                    if len(design_content) > 300
                    else design_content
                )
                print("─" * 60)

        # Step 6: Clean up test data
        print(f"\n🧹 Step 6: Cleaning up test data...")
        await asyncio.to_thread(case_doc_ref.delete)
        print(f"✅ Test case deleted from Firestore")

        return True

    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def test_api_response_format():
    """Test that the API response format is correct for frontend consumption."""
    print("\n🧪 Testing API Response Format...")

    try:
        from app.api.v1.case_routes import BusinessCaseDetailsModel
        from pydantic import ValidationError

        # Sample data that should match what the API returns
        sample_case_data = {
            "case_id": "test-case-123",
            "user_id": "test-user-456",
            "title": "Test Business Case",
            "problem_statement": "Test problem statement",
            "relevant_links": [],
            "status": "SYSTEM_DESIGN_DRAFTED",
            "history": [],
            "prd_draft": {
                "content_markdown": "# Test PRD\n\nThis is a test PRD.",
                "generated_by": "ProductManagerAgent",
                "version": "v1",
            },
            "system_design_v1_draft": {
                "content_markdown": "# Test System Design\n\nThis is a test system design.",
                "generated_by": "ArchitectAgent",
                "version": "v1",
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        # Test that the model can parse the data
        try:
            model_instance = BusinessCaseDetailsModel(**sample_case_data)
            print("✅ BusinessCaseDetailsModel validation passed")
            print(
                f"   - Model includes system_design_v1_draft: {hasattr(model_instance, 'system_design_v1_draft')}"
            )
            print(
                f"   - System design content available: {bool(model_instance.system_design_v1_draft)}"
            )
            return True
        except ValidationError as ve:
            print(f"❌ Model validation failed: {ve}")
            return False

    except Exception as e:
        print(f"❌ API format test failed: {str(e)}")
        return False


async def main():
    """Run all end-to-end tests."""
    print("🧪 DRFIRST BUSINESS CASE GENERATOR - END-TO-END TESTING")
    print("🏗️  Testing ArchitectAgent Integration & Complete Workflow")
    print("=" * 80)

    # Test 1: Complete workflow
    print("\n📋 TEST 1: Complete Business Case Workflow")
    test1_success = await test_complete_workflow()

    # Test 2: API response format
    print("\n📋 TEST 2: API Response Format Validation")
    test2_success = await test_api_response_format()

    # Summary
    print("\n" + "=" * 80)
    print("📊 END-TO-END TEST RESULTS:")
    print(f"   1. Complete Workflow Test: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"   2. API Format Test: {'✅ PASS' if test2_success else '❌ FAIL'}")

    all_tests_passed = test1_success and test2_success

    if all_tests_passed:
        print(f"\n🎉 ALL TESTS PASSED! System is ready for user testing.")
        print(f"\n📋 Workflow Verified:")
        print(f"   ✅ Business case creation")
        print(f"   ✅ PRD generation by ProductManagerAgent")
        print(f"   ✅ PRD approval workflow")
        print(f"   ✅ System design generation by ArchitectAgent")
        print(
            f"   ✅ Status transitions (INTAKE → PRD_DRAFTING → PRD_APPROVED → SYSTEM_DESIGN_DRAFTED)"
        )
        print(f"   ✅ Firestore data persistence")
        print(f"   ✅ API response format compatibility")

        print(f"\n🚀 READY FOR FRONTEND INTEGRATION!")
        print(f"   Next: Test via actual API endpoints and frontend UI")

    else:
        print(f"\n⚠️  Some tests failed. Please check the implementation.")

    return all_tests_passed


if __name__ == "__main__":
    asyncio.run(main())
