#!/usr/bin/env python3
"""
Test script for URL content fetching and summarization functionality
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append('./backend')

from app.utils.web_utils import fetch_web_content, validate_url
from app.agents.product_manager_agent import ProductManagerAgent
from app.services.prompt_service import PromptService
from google.cloud import firestore


async def test_web_content_fetching():
    """Test basic web content fetching functionality"""
    print("🌐 Testing Web Content Fetching...")
    
    # Test URLs - using publicly accessible sites
    test_urls = [
        "https://httpbin.org/html",  # Simple HTML test page
        "https://example.com",       # Basic example site
        "https://invalid-url-12345.com",  # Invalid URL to test error handling
        "not-a-url",                # Malformed URL
    ]
    
    for url in test_urls:
        print(f"\n📄 Testing URL: {url}")
        result = await fetch_web_content(url)
        
        print(f"  Success: {result['success']}")
        if result['success']:
            print(f"  Content length: {len(result['content'])} characters")
            print(f"  Title: {result['metadata'].get('title', 'N/A')}")
            print(f"  Content preview: {result['content'][:100]}...")
        else:
            print(f"  Error: {result['error']}")


async def test_url_validation():
    """Test URL validation function"""
    print("\n✅ Testing URL Validation...")
    
    test_cases = [
        ("https://www.example.com", True),
        ("http://example.com", True),
        ("ftp://example.com", True),
        ("example.com", False),
        ("not-a-url", False),
        ("", False),
        (None, False),
    ]
    
    for url, expected in test_cases:
        result = validate_url(url) if url is not None else False
        status = "✅" if result == expected else "❌"
        print(f"  {status} URL: {url} -> {result} (expected: {expected})")


async def test_content_summarization():
    """Test content summarization with ProductManagerAgent"""
    print("\n📝 Testing Content Summarization...")
    
    try:
        # Initialize ProductManagerAgent
        db = firestore.Client()
        prompt_service = PromptService(db)
        agent = ProductManagerAgent(prompt_service)
        
        # Test content for summarization
        test_content = """
        This is a sample article about implementing a new patient portal system.
        The system will allow patients to access their medical records, schedule appointments,
        and communicate with healthcare providers. Key requirements include HIPAA compliance,
        integration with existing EMR systems, and mobile accessibility. The project aims to
        improve patient engagement and reduce administrative overhead for healthcare staff.
        Technical considerations include secure authentication, data encryption, and scalable
        cloud infrastructure. The expected timeline is 6 months with a budget of $500,000.
        """
        
        print("📄 Test content prepared")
        print("🤖 Generating summary...")
        
        summary = await agent.summarize_content(test_content, "Test Article")
        
        if summary:
            print(f"✅ Summary generated successfully:")
            print(f"   {summary}")
        else:
            print("❌ No summary generated")
            
    except Exception as e:
        print(f"❌ Error during summarization test: {str(e)}")
        print("   This might be due to Vertex AI configuration issues")


async def test_full_integration():
    """Test the full integration with ProductManagerAgent.draft_prd"""
    print("\n🔄 Testing Full Integration with PRD Generation...")
    
    try:
        # Initialize ProductManagerAgent
        db = firestore.Client()
        prompt_service = PromptService(db)
        agent = ProductManagerAgent(prompt_service)
        
        # Test data
        problem_statement = "We need a new patient scheduling system to reduce no-shows and improve clinic efficiency."
        case_title = "Smart Patient Scheduling System"
        relevant_links = [
            {
                "name": "Example Healthcare Article",
                "url": "https://httpbin.org/html"  # Simple test URL that returns HTML
            },
            {
                "name": "Invalid Link",
                "url": "https://invalid-domain-12345.com"
            }
        ]
        
        print("🚀 Generating PRD with URL context...")
        result = await agent.draft_prd(problem_statement, case_title, relevant_links)
        
        if result.get("status") == "success":
            prd_draft = result.get("prd_draft", {})
            content = prd_draft.get("content_markdown", "")
            print(f"✅ PRD generated successfully")
            print(f"   Length: {len(content)} characters")
            print(f"   Contains links context: {'Additional Context from Relevant Links' in content}")
        else:
            print(f"❌ PRD generation failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during full integration test: {str(e)}")


async def main():
    """Run all tests"""
    print("🧪 URL Content Fetching and Summarization Test Suite")
    print("=" * 60)
    
    try:
        await test_url_validation()
        await test_web_content_fetching()
        await test_content_summarization()
        await test_full_integration()
        
        print("\n🎉 Test suite completed!")
        print("\nNote: Some tests may fail if:")
        print("  - Vertex AI is not properly configured")
        print("  - Network connectivity issues")
        print("  - GCP authentication problems")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 