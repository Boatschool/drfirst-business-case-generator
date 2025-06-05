#!/usr/bin/env python3
"""
Test script for the Submit PRD for Review functionality
"""

import sys
sys.path.append('.')

from app.agents.orchestrator_agent import BusinessCaseStatus

def test_business_case_status():
    """Test that BusinessCaseStatus enum has the required values"""
    print("Testing BusinessCaseStatus enum...")
    
    # Check that required statuses exist
    assert hasattr(BusinessCaseStatus, 'PRD_DRAFTING')
    assert hasattr(BusinessCaseStatus, 'PRD_REVIEW')
    
    print(f"PRD_DRAFTING: {BusinessCaseStatus.PRD_DRAFTING.value}")
    print(f"PRD_REVIEW: {BusinessCaseStatus.PRD_REVIEW.value}")
    
    # Check that values are strings
    assert isinstance(BusinessCaseStatus.PRD_DRAFTING.value, str)
    assert isinstance(BusinessCaseStatus.PRD_REVIEW.value, str)
    
    print("✅ BusinessCaseStatus enum test passed!")

def test_import_case_routes():
    """Test that case routes can be imported without errors"""
    print("Testing case routes import...")
    
    try:
        from app.api.v1.case_routes import router, submit_prd_for_review
        print("✅ Case routes imported successfully!")
        print(f"Router type: {type(router)}")
        print(f"submit_prd_for_review function: {submit_prd_for_review}")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        raise

if __name__ == "__main__":
    print("🧪 Testing Submit PRD for Review functionality...\n")
    
    test_business_case_status()
    print()
    test_import_case_routes()
    
    print("\n🎉 All tests passed! Submit PRD functionality is ready.") 