#!/usr/bin/env python3
"""
Test script for the SalesValueAnalystAgent to verify implementation works correctly.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.agents.sales_value_analyst_agent import SalesValueAnalystAgent

async def test_sales_value_analyst():
    """Test the SalesValueAnalystAgent functionality."""
    print("🧪 Testing SalesValueAnalystAgent...")
    print("=" * 60)
    
    try:
        # Initialize the agent
        print("1. Initializing SalesValueAnalystAgent...")
        agent = SalesValueAnalystAgent()
        print(f"   ✅ Agent initialized: {agent.name}")
        print(f"   Status: {agent.status}")
        
        # Test status method
        print("\n2. Testing get_status() method...")
        status = agent.get_status()
        print(f"   ✅ Status: {status}")
        
        # Test value projection with sample PRD content
        print("\n3. Testing project_value() method...")
        sample_prd = """
        Product Requirements Document
        
        Project: Patient Portal Enhancement
        
        Overview:
        This project aims to enhance the existing patient portal to improve user experience
        and increase patient engagement with healthcare services.
        
        Goals:
        - Improve patient satisfaction scores by 20%
        - Increase portal usage by 50%
        - Reduce call center volume by 30%
        """
        
        case_title = "Patient Portal Enhancement Project"
        
        print(f"   Testing with case: {case_title}")
        value_response = await agent.project_value(sample_prd, case_title)
        
        # Display results
        print(f"   ✅ Response status: {value_response.get('status')}")
        print(f"   Message: {value_response.get('message')}")
        
        if value_response.get("status") == "success":
            value_projection = value_response.get("value_projection")
            print(f"\n   📊 Value Projection Results:")
            print(f"   Template Used: {value_projection.get('template_used')}")
            print(f"   Currency: {value_projection.get('currency')}")
            print(f"   Methodology: {value_projection.get('methodology')}")
            
            scenarios = value_projection.get("scenarios", [])
            print(f"   \n   💰 Value Scenarios:")
            for scenario in scenarios:
                print(f"     • {scenario.get('case')}: ${scenario.get('value'):,} - {scenario.get('description')}")
            
            assumptions = value_projection.get("assumptions", [])
            if assumptions:
                print(f"\n   📋 Assumptions:")
                for assumption in assumptions:
                    print(f"     • {assumption}")
            
            print(f"\n   📝 Notes: {value_projection.get('notes')}")
        else:
            print(f"   ❌ Error: {value_response.get('message')}")
        
        print("\n=" * 60)
        print("✅ SalesValueAnalystAgent test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_sales_value_analyst()) 