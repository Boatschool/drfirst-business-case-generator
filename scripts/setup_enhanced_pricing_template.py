#!/usr/bin/env python3
"""
Script to set up an enhanced pricing template with isDefault field for the enhanced SalesValueAnalystAgent.
This creates a comprehensive template that demonstrates the AI-powered value projection capabilities.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from google.cloud import firestore
from app.core.config import settings

async def setup_enhanced_pricing_template():
    """Set up an enhanced pricing template with comprehensive guidance."""
    try:
        # Initialize Firestore client
        db = firestore.Client(project=settings.firebase_project_id)
        print("Firestore client initialized successfully")
        
        # Define the enhanced pricing template document
        template_data = {
            "name": "Enhanced Healthcare Value Projection Template V2.0",
            "description": "Comprehensive template for AI-powered value projections in healthcare technology projects with detailed guidance and methodology",
            "version": "2.0",
            "isActive": True,
            "isDefault": True,  # Mark as default for selection
            "structureDefinition": {
                "type": "LowBaseHigh",
                "notes": "Comprehensive low/base/high scenario modeling with AI-powered value generation based on PRD analysis and healthcare industry factors",
                "scenarios": [
                    {
                        "case": "Low",
                        "value": 25000,
                        "description": "Conservative estimate with minimal adoption and basic efficiency gains"
                    },
                    {
                        "case": "Base", 
                        "value": 75000,
                        "description": "Most likely scenario with expected adoption and standard ROI"
                    },
                    {
                        "case": "High",
                        "value": 150000,
                        "description": "Optimistic scenario with high adoption and additional revenue opportunities"
                    }
                ],
                "value_drivers": [
                    "Operational efficiency improvements",
                    "Revenue generation through new capabilities",
                    "Cost savings from process automation",
                    "Productivity gains from improved workflows",
                    "Market expansion opportunities"
                ]
            },
            "guidance": {
                "low_scenario": "Conservative estimates assuming 20-30% adoption rate, minimal workflow changes, and basic efficiency improvements. Focus on proven cost savings and immediate benefits.",
                "base_scenario": "Most likely estimates assuming 50-70% adoption rate, moderate workflow optimization, and standard healthcare technology ROI patterns. Include both direct and indirect benefits.",
                "high_scenario": "Optimistic estimates assuming 80%+ adoption rate, significant workflow transformation, and additional revenue generation opportunities. Consider market expansion and competitive advantages.",
                "industry_factors": "Healthcare technology projects typically see 12-24 month implementation timelines, regulatory compliance requirements, and user training considerations that impact value realization.",
                "risk_factors": "Consider regulatory changes, user adoption challenges, technical integration complexity, and competitive market dynamics."
            },
            "metadata": {
                "version": "2.0",
                "created_by": "enhanced_setup_script",
                "industry_focus": "healthcare_technology",
                "methodology": "AI-powered value projection with template guidance",
                "target_projects": [
                    "Electronic Health Records (EHR) systems",
                    "Patient portal enhancements", 
                    "Clinical workflow automation",
                    "Healthcare data analytics platforms",
                    "Telemedicine and remote care solutions"
                ],
                "last_updated": firestore.SERVER_TIMESTAMP
            },
            "ai_prompt_guidance": {
                "context_factors": [
                    "Healthcare regulatory environment (HIPAA, FDA, etc.)",
                    "Provider workflow integration requirements",
                    "Patient experience and safety considerations",
                    "Data security and privacy requirements",
                    "Interoperability and standards compliance"
                ],
                "valuation_methods": [
                    "Cost-benefit analysis for operational efficiency",
                    "Revenue impact from new service capabilities",
                    "Time savings monetization for clinical staff",
                    "Patient outcome improvement value quantification",
                    "Risk reduction and compliance cost avoidance"
                ],
                "market_benchmarks": {
                    "small_project": "25,000 - 100,000 USD",
                    "medium_project": "100,000 - 500,000 USD", 
                    "large_project": "500,000 - 2,000,000 USD",
                    "enterprise_project": "2,000,000+ USD"
                }
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Reference to the pricing template document
        template_ref = db.collection("pricingTemplates").document("enhanced_healthcare_template_v2")
        
        # Check if the document already exists
        doc_snapshot = await asyncio.to_thread(template_ref.get)
        
        if doc_snapshot.exists:
            print("⚠️  Enhanced pricing template already exists")
            existing_data = doc_snapshot.to_dict()
            print(f"   Existing template: {existing_data.get('name', 'Unknown')}")
            
            # Ask user if they want to overwrite
            response = input("Do you want to overwrite the existing enhanced template? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("❌ Setup cancelled - keeping existing template")
                return
        
        # Create or update the document
        await asyncio.to_thread(template_ref.set, template_data)
        print("✅ Successfully created/updated enhanced pricing template")
        print(f"   Document ID: enhanced_healthcare_template_v2")
        print(f"   Template Name: {template_data['name']}")
        print(f"   Version: {template_data['version']}")
        print(f"   Is Active: {template_data['isActive']}")
        print(f"   Is Default: {template_data['isDefault']}")
        print(f"   Structure Type: {template_data['structureDefinition']['type']}")
        print(f"   Scenarios: {len(template_data['structureDefinition']['scenarios'])}")
        
        # Also update the original template to not be default
        print("\n🔧 Updating original template to not be default...")
        original_ref = db.collection("pricingTemplates").document("default_value_projection")
        original_snapshot = await asyncio.to_thread(original_ref.get)
        
        if original_snapshot.exists:
            await asyncio.to_thread(original_ref.update, {
                "isDefault": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            print("✅ Updated original template to isDefault=False")
        
        # Verify the document was created
        verification_snapshot = await asyncio.to_thread(template_ref.get)
        if verification_snapshot.exists:
            print("✅ Verification: Enhanced template successfully created in Firestore")
        else:
            print("❌ Verification failed: Template not found after creation")
            
    except Exception as e:
        print(f"❌ Error setting up enhanced pricing template: {e}")
        raise

if __name__ == "__main__":
    print("🚀 Setting up enhanced pricing template for SalesValueAnalystAgent...")
    print("=" * 70)
    
    try:
        asyncio.run(setup_enhanced_pricing_template())
        print("=" * 70)
        print("✅ Enhanced pricing template setup completed successfully!")
        print("\nThe enhanced SalesValueAnalystAgent can now:")
        print("  • Use AI-powered value projections with template guidance")
        print("  • Access comprehensive healthcare industry context")
        print("  • Apply sophisticated valuation methodologies") 
        print("  • Generate realistic scenarios based on PRD content")
        print("  • Fall back gracefully to template-based values if needed")
        
    except Exception as e:
        print("=" * 70)
        print(f"❌ Setup failed: {e}")
        exit(1) 