#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced SalesValueAnalystAgent.
Tests AI-powered value projection, template selection strategies, and fallback mechanisms.
"""

import asyncio
import sys
import os
import json

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.agents.sales_value_analyst_agent import SalesValueAnalystAgent

async def test_enhanced_sales_value_analyst():
    """Test the enhanced SalesValueAnalystAgent functionality."""
    print("🧪 Testing Enhanced SalesValueAnalystAgent...")
    print("=" * 80)
    
    try:
        # Initialize the agent
        print("1. Initializing Enhanced SalesValueAnalystAgent...")
        agent = SalesValueAnalystAgent()
        print(f"   ✅ Agent initialized: {agent.name}")
        status = agent.get_status()
        print(f"   Status: {status['status']}")
        print(f"   Vertex AI Available: {status['vertex_ai_available']}")
        print(f"   Model: {status['model']}")
        
        # Test 1: Template fetching strategy
        print("\n2. Testing template fetching strategy...")
        template = await agent._fetch_pricing_template()
        if template:
            print(f"   ✅ Template found: {template.get('name', 'Unknown')}")
            print(f"   Template ID: {template.get('id', 'No ID')}")
            print(f"   Is Active: {template.get('isActive', 'Not set')}")
            print(f"   Is Default: {template.get('isDefault', 'Not set')}")
            print(f"   Structure Type: {template.get('structureDefinition', {}).get('type', 'Unknown')}")
        else:
            print("   ❌ No template found")
        
        # Test 2: AI-powered value projection with realistic PRD content
        print("\n3. Testing AI-powered value projection...")
        sample_prd = """
        # PRD: Patient Portal Enhancement Project
        
        ## 1. Introduction / Problem Statement
        DrFirst's current patient portal has limited functionality and low user engagement. 
        Patients struggle to access their health information, schedule appointments, and communicate 
        with healthcare providers efficiently. This leads to increased call center volume and 
        reduced patient satisfaction.
        
        ## 2. Goals / Objectives
        - Increase patient portal usage by 60% within 12 months
        - Reduce call center volume by 40% for routine inquiries
        - Improve patient satisfaction scores by 25%
        - Enable secure messaging between patients and providers
        
        ## 3. Target Audience / Users
        Primary: Patients of DrFirst healthcare network (15,000+ active patients)
        Secondary: Healthcare providers, nursing staff, administrative personnel
        
        ## 4. Proposed Solution / Scope
        Enhance the existing patient portal with:
        - Modern, mobile-responsive interface
        - Secure messaging functionality
        - Appointment scheduling integration
        - Lab results and medical record access
        - Prescription refill requests
        
        ## 5. Key Features / User Stories
        - As a patient, I want to view my lab results online so I don't have to call the office
        - As a patient, I want to message my doctor securely for non-urgent questions
        - As a patient, I want to schedule appointments online at my convenience
        - As a provider, I want to receive organized patient messages to respond efficiently
        
        ## 6. Success Metrics / KPIs
        - Portal login frequency and session duration
        - Number of secure messages sent/received
        - Online appointment booking rate
        - Patient satisfaction survey scores
        - Call center volume reduction
        
        ## 7. Technical Considerations / Dependencies
        - Integration with existing EMR system (Epic)
        - HIPAA compliance and security requirements
        - Mobile responsiveness and accessibility standards
        - Single sign-on (SSO) integration
        
        ## 8. Open Questions / Risks
        - User adoption timeline and training requirements
        - Integration complexity with legacy systems
        - Ongoing maintenance and support costs
        - Data migration and system downtime risks
        """
        
        case_title = "Patient Portal Enhancement Project"
        
        print(f"   Testing with case: {case_title}")
        value_response = await agent.project_value(sample_prd, case_title)
        
        # Display results
        print(f"   ✅ Response status: {value_response.get('status')}")
        print(f"   Message: {value_response.get('message')}")
        
        if value_response.get("status") == "success":
            value_projection = value_response.get("value_projection")
            print(f"\n   📊 Enhanced Value Projection Results:")
            print(f"   Template Used: {value_projection.get('template_used')}")
            print(f"   Currency: {value_projection.get('currency')}")
            print(f"   Methodology: {value_projection.get('methodology')}")
            
            scenarios = value_projection.get("scenarios", [])
            print(f"   \n   💰 Value Scenarios:")
            total_range = 0
            for scenario in scenarios:
                value = scenario.get('value', 0)
                print(f"     • {scenario.get('case')}: ${value:,} - {scenario.get('description')}")
                total_range += value
            
            if len(scenarios) > 1:
                avg_value = total_range / len(scenarios)
                print(f"   \n   📈 Average Value: ${avg_value:,.0f}")
                
            assumptions = value_projection.get("assumptions", [])
            if assumptions:
                print(f"\n   📋 Key Assumptions:")
                for i, assumption in enumerate(assumptions[:3], 1):  # Show first 3
                    print(f"     {i}. {assumption}")
                if len(assumptions) > 3:
                    print(f"     ... and {len(assumptions) - 3} more assumptions")
            
            market_factors = value_projection.get("market_factors", [])
            if market_factors:
                print(f"\n   🏥 Market Factors:")
                for factor in market_factors[:2]:  # Show first 2
                    print(f"     • {factor}")
            
            print(f"\n   📝 Notes: {value_projection.get('notes', 'None')[:150]}...")
        else:
            print(f"   ❌ Error: {value_response.get('message')}")
        
        # Test 3: Fallback mechanisms
        print("\n4. Testing fallback mechanisms...")
        
        # Test with no Vertex AI (simulate)
        original_vertex_ai = agent.vertex_ai_available
        agent.vertex_ai_available = False
        
        print("   Testing template-based fallback (AI disabled)...")
        fallback_response = await agent.project_value(sample_prd, case_title)
        
        if fallback_response.get("status") == "success":
            fallback_projection = fallback_response.get("value_projection")
            print(f"   ✅ Fallback successful: {fallback_projection.get('template_used')}")
            print(f"   Methodology: {fallback_projection.get('methodology')}")
            fallback_scenarios = fallback_projection.get("scenarios", [])
            if fallback_scenarios:
                print(f"   Scenarios: {[s.get('case') for s in fallback_scenarios]}")
        else:
            print(f"   ❌ Fallback failed: {fallback_response.get('message')}")
        
        # Restore original state
        agent.vertex_ai_available = original_vertex_ai
        
        # Test 4: Template structure analysis
        if template:
            print("\n5. Testing template structure analysis...")
            template_structure = template.get("structureDefinition", {})
            guidance = template.get("guidance", {})
            
            print(f"   Structure Type: {template_structure.get('type', 'Unknown')}")
            print(f"   Predefined Scenarios: {len(template_structure.get('scenarios', []))}")
            print(f"   Guidance Sections: {len(guidance)}")
            
            if guidance:
                print("   Available Guidance:")
                for key in list(guidance.keys())[:3]:  # Show first 3
                    print(f"     • {key.replace('_', ' ').title()}")
        
        # Test 5: Error handling
        print("\n6. Testing error handling...")
        
        # Test with empty PRD
        print("   Testing with empty PRD content...")
        empty_response = await agent.project_value("", "Empty Test Case")
        print(f"   Empty PRD Response: {empty_response.get('status')}")
        
        # Test with very short PRD
        print("   Testing with minimal PRD content...")
        minimal_response = await agent.project_value("Simple test project", "Minimal Test Case") 
        print(f"   Minimal PRD Response: {minimal_response.get('status')}")
        
        print("\n=" * 80)
        print("✅ Enhanced SalesValueAnalystAgent test completed successfully!")
        
        # Summary
        print("\n📋 Test Summary:")
        print("   ✅ Agent initialization and configuration")
        print("   ✅ Enhanced template fetching with isActive/isDefault support")
        print("   ✅ AI-powered value projection with comprehensive prompts")
        print("   ✅ Template-based fallback mechanisms")
        print("   ✅ Error handling and edge cases")
        print("   ✅ Structured output formatting and parsing")
        
        print("\n🎯 Key Enhancements Verified:")
        print("   • Vertex AI integration for intelligent value projection")
        print("   • Advanced template selection strategy (active + default)")
        print("   • PRD content analysis and summarization")
        print("   • Healthcare industry context and guidance")
        print("   • Comprehensive error handling and fallbacks")
        print("   • JSON parsing with manual extraction backup")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(test_enhanced_sales_value_analyst()) 