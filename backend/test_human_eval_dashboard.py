#!/usr/bin/env python3
"""
Test script for Human Evaluation Dashboard API endpoints.
Tests the new endpoints for human evaluation data.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add the backend app directory to Python path
backend_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(backend_dir))

from api.v1.dashboard_routes import (
    get_human_eval_summary,
    get_human_eval_results,
    get_human_eval_detail
)


async def test_human_eval_dashboard():
    """Test the human evaluation dashboard endpoints"""
    print("🧪 Testing Human Evaluation Dashboard API Endpoints\n")
    
    # Mock user for testing (admin role required)
    mock_user = {
        "uid": "test_admin_uid",
        "email": "admin@test.com"
    }
    
    try:
        # Test 1: Human Evaluation Summary
        print("1️⃣ Testing Human Evaluation Summary...")
        try:
            summary_data = await get_human_eval_summary(current_user=mock_user)
            print(f"✅ Summary retrieved successfully")
            print(f"   Total evaluations: {summary_data.total_evaluations}")
            print(f"   Unique evaluators: {summary_data.unique_evaluators}")
            print(f"   Average score: {summary_data.average_overall_score}")
            print(f"   Score distribution: {summary_data.score_distribution}")
            print(f"   Evaluations by agent: {summary_data.evaluations_by_agent}")
        except Exception as e:
            print(f"❌ Summary test failed: {e}")
        
        print()
        
        # Test 2: Human Evaluation Results List
        print("2️⃣ Testing Human Evaluation Results List...")
        try:
            results_data = await get_human_eval_results(
                page=1,
                limit=10,
                sort_by="evaluation_date",
                order="desc",
                current_user=mock_user
            )
            print(f"✅ Results list retrieved successfully")
            print(f"   Total results: {results_data.total_count}")
            print(f"   Current page: {results_data.current_page}")
            print(f"   Results on this page: {len(results_data.evaluations)}")
            
            # Show first result if available
            if results_data.evaluations:
                first_result = results_data.evaluations[0]
                print(f"   First result: {first_result.submission_id[:20]}...")
                print(f"   Agent: {first_result.agent_name}")
                print(f"   Score: {first_result.overall_quality_score}")
        except Exception as e:
            print(f"❌ Results list test failed: {e}")
        
        print()
        
        # Test 3: Human Evaluation Detail (if we have results)
        print("3️⃣ Testing Human Evaluation Detail...")
        try:
            # First get a submission ID from the results
            results_data = await get_human_eval_results(
                page=1,
                limit=1,
                sort_by="evaluation_date",
                order="desc",
                current_user=mock_user
            )
            
            if results_data.evaluations:
                submission_id = results_data.evaluations[0].submission_id
                detail_data = await get_human_eval_detail(
                    submission_id=submission_id,
                    current_user=mock_user
                )
                print(f"✅ Detail retrieved successfully")
                print(f"   Submission ID: {detail_data.submission_id}")
                print(f"   Agent: {detail_data.agent_name}")
                print(f"   Evaluator: {detail_data.evaluator_email}")
                print(f"   Overall score: {detail_data.overall_quality_score}")
                print(f"   Metrics evaluated: {len(detail_data.metric_scores_and_comments)}")
            else:
                print("⚠️  No evaluations found to test detail endpoint")
        except Exception as e:
            print(f"❌ Detail test failed: {e}")
            
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
    
    print("\n🏁 Human Evaluation Dashboard API Test Complete")


if __name__ == "__main__":
    asyncio.run(test_human_eval_dashboard()) 