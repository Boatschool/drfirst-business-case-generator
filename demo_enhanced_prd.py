#!/usr/bin/env python3
"""
Demonstration of Enhanced PRD Generation with URL Content Summarization
This script shows how the ProductManagerAgent now incorporates web content into PRD generation.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append('./backend')

from app.agents.product_manager_agent import ProductManagerAgent
from app.services.prompt_service import PromptService
from google.cloud import firestore


async def demo_enhanced_prd():
    """Demonstrate enhanced PRD generation with URL content"""
    print("🚀 Enhanced PRD Generation Demo")
    print("=" * 60)
    
    try:
        # Initialize ProductManagerAgent
        print("🤖 Initializing ProductManagerAgent...")
        db = firestore.Client()
        prompt_service = PromptService(db)
        agent = ProductManagerAgent(prompt_service)
        
        # Demo case: Patient Portal Enhancement
        problem_statement = """
        Our current patient portal has low adoption rates (15%) and limited functionality. 
        Patients struggle to access their health records, schedule appointments, and communicate 
        with providers. We need to enhance the portal to improve patient engagement and 
        reduce administrative burden on clinical staff.
        """
        
        case_title = "Patient Portal Enhancement Project"
        
        # Relevant links that provide context
        relevant_links = [
            {
                "name": "Example Healthcare Site",
                "url": "https://httpbin.org/html"  # Test URL with HTML content
            },
            {
                "name": "Healthcare Standards Reference",
                "url": "https://example.com"  # Simple example domain
            },
            {
                "name": "Invalid Reference", 
                "url": "https://non-existent-site-12345.com"  # Will fail gracefully
            }
        ]
        
        print(f"📋 Case Title: {case_title}")
        print(f"📝 Problem Statement: {problem_statement.strip()}")
        print(f"🔗 Processing {len(relevant_links)} relevant links for context...")
        
        # Generate enhanced PRD
        print("\n🎯 Generating Enhanced PRD with URL Context...")
        result = await agent.draft_prd(problem_statement, case_title, relevant_links)
        
        if result.get("status") == "success":
            prd_draft = result.get("prd_draft", {})
            content = prd_draft.get("content_markdown", "")
            
            print("\n✅ Enhanced PRD Generated Successfully!")
            print(f"📊 Content Length: {len(content):,} characters")
            print(f"📋 Sections: {len(prd_draft.get('sections', []))} structured sections")
            
            # Show a preview of the PRD
            print("\n📖 PRD Preview (First 800 characters):")
            print("-" * 60)
            print(content[:800] + "..." if len(content) > 800 else content)
            print("-" * 60)
            
            # Check if URL context was incorporated
            if "Additional Context from Relevant Links" in content:
                print("\n🌐 ✅ URL Content Successfully Incorporated into PRD")
            else:
                print("\n🌐 ⚠️  URL Content Integration: Check logs for details")
            
            # Show generation metadata
            print(f"\n🔧 Generated with: {prd_draft.get('generated_with', 'Unknown')}")
            print(f"📦 Version: {prd_draft.get('version', 'Unknown')}")
            
        else:
            print(f"\n❌ PRD generation failed: {result.get('message', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"\n💥 Demo failed with error: {str(e)}")
        return 1
    
    print("\n🎉 Enhanced PRD Generation Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("  ✅ Web content fetching from multiple URLs")
    print("  ✅ AI-powered content summarization") 
    print("  ✅ Context integration into PRD generation")
    print("  ✅ Graceful error handling for failed URLs")
    print("  ✅ Comprehensive logging and monitoring")
    
    return 0


async def demo_content_summarization():
    """Demonstrate standalone content summarization"""
    print("\n📝 Content Summarization Demo")
    print("=" * 40)
    
    try:
        # Initialize ProductManagerAgent
        db = firestore.Client()
        prompt_service = PromptService(db)
        agent = ProductManagerAgent(prompt_service)
        
        # Sample healthcare IT content
        sample_content = """
        Electronic Health Records (EHR) Implementation Guide
        
        This document outlines best practices for implementing EHR systems in healthcare organizations.
        Key considerations include data migration from legacy systems, staff training requirements,
        workflow integration, and patient data security compliance with HIPAA regulations.
        
        The implementation typically involves several phases:
        1. Assessment and planning (2-3 months)
        2. System configuration and customization (3-4 months) 
        3. Data migration and testing (2-3 months)
        4. Go-live and stabilization (1-2 months)
        5. Post-implementation optimization (ongoing)
        
        Critical success factors include executive sponsorship, dedicated project management,
        comprehensive user training, and robust technical support during transition.
        Budget considerations should include software licensing, hardware infrastructure,
        implementation services, training costs, and ongoing maintenance.
        """
        
        print("📄 Summarizing sample healthcare IT content...")
        summary = await agent.summarize_content(sample_content, "EHR Implementation Guide")
        
        if summary:
            print("\n✅ Summary Generated:")
            print("-" * 40)
            print(summary)
            print("-" * 40)
        else:
            print("\n❌ Summary generation failed")
            
    except Exception as e:
        print(f"\n💥 Summarization demo failed: {str(e)}")


if __name__ == "__main__":
    async def main():
        exit_code = await demo_enhanced_prd()
        await demo_content_summarization()
        return exit_code
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 