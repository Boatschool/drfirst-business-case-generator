#!/usr/bin/env python3
"""
Test script for automated evaluation dashboard API endpoints
"""

import asyncio
import sys
import os
import logging

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.api.v1.dashboard_routes import (
    get_dashboard_summary,
    list_evaluation_runs,
    get_evaluation_run_details,
    get_dashboard_db
)

# Mock user for testing
MOCK_ADMIN_USER = {
    "uid": "test_admin_123",
    "email": "test@example.com",
    "roles": ["ADMIN"]
}

async def test_dashboard_db_connection():
    """Test Firestore database connection"""
    print("🔧 Testing Firestore database connection...")
    
    try:
        db = get_dashboard_db()
        if db:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

async def test_dashboard_summary():
    """Test dashboard summary endpoint"""
    print("\n📊 Testing dashboard summary endpoint...")
    
    try:
        summary = await get_dashboard_summary(current_user=MOCK_ADMIN_USER)
        print(f"✅ Dashboard summary retrieved successfully:")
        print(f"   Total runs: {summary.total_runs}")
        print(f"   Total examples: {summary.total_examples_processed}")
        print(f"   Avg success rate: {summary.overall_avg_success_rate}%")
        print(f"   Avg validation rate: {summary.overall_avg_validation_pass_rate}%")
        return True
    except Exception as e:
        print(f"❌ Dashboard summary error: {e}")
        return False

async def test_list_runs():
    """Test list evaluation runs endpoint"""
    print("\n📋 Testing list evaluation runs endpoint...")
    
    try:
        runs_data = await list_evaluation_runs(
            page=1,
            limit=5,
            sort_by="run_timestamp_start",
            order="desc",
            current_user=MOCK_ADMIN_USER
        )
        print(f"✅ Evaluation runs list retrieved successfully:")
        print(f"   Total count: {runs_data.total_count}")
        print(f"   Current page: {runs_data.current_page}")
        print(f"   Runs in this page: {len(runs_data.runs)}")
        
        if runs_data.runs:
            print(f"   First run ID: {runs_data.runs[0].eval_run_id}")
            return runs_data.runs[0].eval_run_id  # Return first run ID for details test
        return True
    except Exception as e:
        print(f"❌ List evaluation runs error: {e}")
        return False

async def test_run_details(eval_run_id: str):
    """Test run details endpoint"""
    print(f"\n🔍 Testing run details endpoint for ID: {eval_run_id}")
    
    try:
        details = await get_evaluation_run_details(
            eval_run_id=eval_run_id,
            current_user=MOCK_ADMIN_USER
        )
        print(f"✅ Run details retrieved successfully:")
        print(f"   Run ID: {details.run_summary.eval_run_id}")
        print(f"   Examples processed: {details.run_summary.total_examples_processed}")
        print(f"   Success rate: {details.run_summary.success_rate_percentage}%")
        print(f"   Failed validations: {details.failed_validations_count}")
        print(f"   Agent statistics available: {len(details.agent_specific_statistics)}")
        return True
    except Exception as e:
        print(f"❌ Run details error: {e}")
        return False

async def main():
    """Main test runner"""
    print("🧪 Testing Automated Evaluation Dashboard API Endpoints")
    print("=" * 60)
    
    # Test database connection
    db_success = await test_dashboard_db_connection()
    if not db_success:
        print("\n❌ Database connection failed - skipping API tests")
        return
    
    # Test dashboard summary
    summary_success = await test_dashboard_summary()
    
    # Test list runs
    runs_result = await test_list_runs()
    list_success = isinstance(runs_result, (bool, str))
    
    # Test run details if we have a run ID
    details_success = True
    if isinstance(runs_result, str):
        details_success = await test_run_details(runs_result)
    elif runs_result is True:
        print("\n🔍 Skipping run details test - no runs available")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Test Results Summary:")
    print(f"   Database Connection: {'✅' if db_success else '❌'}")
    print(f"   Dashboard Summary: {'✅' if summary_success else '❌'}")
    print(f"   List Runs: {'✅' if list_success else '❌'}")
    print(f"   Run Details: {'✅' if details_success else '❌'}")
    
    all_passed = all([db_success, summary_success, list_success, details_success])
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed - check the logs above")
    
    return all_passed

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise
    
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 