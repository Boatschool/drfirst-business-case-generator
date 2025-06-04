#!/usr/bin/env python3
"""
Debug script to test the fuzzy matching logic for role names.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.agents.cost_analyst_agent import CostAnalystAgent

def test_fuzzy_matching():
    """Test the fuzzy matching logic in isolation."""
    
    # Create a rate map similar to what's in Firestore
    rate_map = {
        "Developer": 100,
        "Product Manager": 120,
        "QA Engineer": 85,
        "DevOps Engineer": 110,
        "UI/UX Designer": 95
    }
    
    # Test roles that should be fuzzy matched
    test_roles = [
        "Lead Developer",
        "Senior Developer", 
        "Software Engineer",
        "PM",
        "Quality Engineer",
        "Designer",
        "SRE"
    ]
    
    cost_analyst = CostAnalystAgent()
    
    print("🔍 Testing Fuzzy Matching Logic")
    print("=" * 50)
    print(f"Rate Map: {rate_map}")
    print()
    
    for role in test_roles:
        print(f"Testing role: '{role}'")
        matched_rate, was_fuzzy_matched = cost_analyst._find_fuzzy_rate_match(role, rate_map, 100)
        match_type = "fuzzy match" if was_fuzzy_matched else "default rate"
        print(f"  -> Matched rate: ${matched_rate}/hour ({match_type})")
        print()

if __name__ == "__main__":
    test_fuzzy_matching() 