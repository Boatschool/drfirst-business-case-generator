#!/usr/bin/env python3
"""
Test script for edge cases and error handling in the enhanced PlannerAgent.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.agents.planner_agent import PlannerAgent


async def test_planner_edge_cases():
    """Test edge cases and error handling for the PlannerAgent."""
    
    print("🧪 Testing PlannerAgent Edge Cases...")
    print("=" * 60)
    
    # Initialize the agent
    planner = PlannerAgent()
    
    # Test Case 1: Empty content
    print("\n🔬 Test Case 1: Empty Content")
    print("-" * 30)
    
    result1 = await planner.estimate_effort("", "", "Empty Content Test")
    print_result(result1, "Empty Content")
    
    # Test Case 2: None values
    print("\n🔬 Test Case 2: None Values")
    print("-" * 30)
    
    result2 = await planner.estimate_effort(None, None, "None Values Test")
    print_result(result2, "None Values")
    
    # Test Case 3: Very large content (to test truncation)
    print("\n🔬 Test Case 3: Very Large Content")
    print("-" * 30)
    
    large_content = """
    # Large Healthcare System PRD
    
    This is a very large PRD with lots of content that should be truncated.
    """ + "API integration, database, authentication, reporting, " * 500  # Repeat to make it large
    
    result3 = await planner.estimate_effort(large_content, large_content, "Large Content Test")
    print_result(result3, "Large Content")
    
    # Test Case 4: Test keyword-based estimation directly
    print("\n🔬 Test Case 4: Keyword-Based Estimation")
    print("-" * 30)
    
    keyword_test_content = """
    Healthcare application with:
    - API integration
    - Database operations
    - Machine learning algorithms
    - Real-time notifications
    - HIPAA compliance
    - Mobile app development
    - Third party integrations
    - HL7 FHIR support
    - Payment processing
    - Microservices architecture
    """
    
    # Test the keyword-based method directly
    keyword_result = await planner._keyword_effort_estimation(
        keyword_test_content, 
        keyword_test_content, 
        "Keyword Test"
    )
    
    print("✅ Keyword-Based Estimation Result:")
    print(f"📊 Total Hours: {keyword_result['total_hours']}")
    print(f"⏱️ Duration: {keyword_result['estimated_duration_weeks']} weeks")
    print(f"🎯 Complexity: {keyword_result['complexity_assessment']}")
    print(f"📝 Notes: {keyword_result['notes']}")
    print("\n👥 Role Breakdown:")
    for role in keyword_result['roles']:
        print(f"  • {role['role']}: {role['hours']} hours")
    
    # Test Case 5: Test validation
    print("\n🔬 Test Case 5: Data Validation")
    print("-" * 30)
    
    # Test valid data
    valid_data = {
        "roles": [
            {"role": "Developer", "hours": 100},
            {"role": "QA Engineer", "hours": 50}
        ],
        "total_hours": 150,
        "estimated_duration_weeks": 5,
        "complexity_assessment": "Medium",
        "notes": "Test validation"
    }
    
    is_valid = planner._validate_effort_data(valid_data)
    print(f"✅ Valid data validation: {is_valid}")
    
    # Test invalid data
    invalid_data = {
        "roles": [
            {"role": "Developer"}  # Missing hours
        ],
        "total_hours": 150,
        "estimated_duration_weeks": 5,
        "complexity_assessment": "Invalid",  # Invalid complexity
        "notes": "Test validation"
    }
    
    is_invalid = planner._validate_effort_data(invalid_data)
    print(f"❌ Invalid data validation: {is_invalid}")
    
    print("\n" + "=" * 60)
    print("✅ Edge case testing completed!")


def print_result(result, test_case):
    """Helper function to print test results."""
    
    if result['status'] == 'success':
        effort_data = result['effort_breakdown']
        print(f"✅ {test_case} - Status: {result['status']}")
        print(f"📊 Total Hours: {effort_data['total_hours']}")
        print(f"🎯 Complexity: {effort_data['complexity_assessment']}")
        print(f"📝 Notes: {effort_data['notes'][:100]}...")
    else:
        print(f"❌ {test_case} - Status: {result['status']}")
        print(f"💬 Error: {result['message']}")
    
    print()


if __name__ == "__main__":
    asyncio.run(test_planner_edge_cases()) 