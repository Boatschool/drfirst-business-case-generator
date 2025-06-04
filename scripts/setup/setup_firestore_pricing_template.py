#!/usr/bin/env python3
"""
Script to set up a default pricing template in Firestore for the SalesValueAnalystAgent.
This creates the stub document that the agent will read to guide value projections.
"""

import asyncio
from google.cloud import firestore
from app.core.config import settings

async def setup_pricing_template():
    """Set up the default pricing template document in Firestore."""
    try:
        # Initialize Firestore client
        db = firestore.Client(project=settings.firebase_project_id)
        print("Firestore client initialized successfully")
        
        # Define the pricing template document
        template_data = {
            "name": "Default Value Projection Template V1",
            "description": "Placeholder template for initial value scenarios in healthcare technology projects",
            "isActive": True,
            "structureDefinition": {
                "type": "LowBaseHigh",
                "notes": "Defines low, base, and high value cases for comprehensive scenario modeling"
            },
            "metadata": {
                "version": "1.0",
                "created_by": "system_setup",
                "industry_focus": "healthcare_technology",
                "last_updated": firestore.SERVER_TIMESTAMP
            },
            "guidance": {
                "low_scenario": "Conservative estimates for minimal adoption and basic efficiency gains",
                "base_scenario": "Most likely estimates based on expected user adoption and standard ROI",
                "high_scenario": "Optimistic estimates accounting for high adoption and additional revenue opportunities"
            }
        }
        
        # Reference to the pricing template document
        template_ref = db.collection("pricingTemplates").document("default_value_projection")
        
        # Check if the document already exists
        doc_snapshot = await asyncio.to_thread(template_ref.get)
        
        if doc_snapshot.exists:
            print("⚠️  Pricing template 'default_value_projection' already exists")
            existing_data = doc_snapshot.to_dict()
            print(f"   Existing template: {existing_data.get('name', 'Unknown')}")
            
            # Ask user if they want to overwrite
            response = input("Do you want to overwrite the existing template? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("❌ Setup cancelled - keeping existing template")
                return
        
        # Create or update the document
        await asyncio.to_thread(template_ref.set, template_data)
        print("✅ Successfully created/updated pricing template document")
        print(f"   Document ID: default_value_projection")
        print(f"   Template Name: {template_data['name']}")
        print(f"   Structure Type: {template_data['structureDefinition']['type']}")
        print(f"   Description: {template_data['description']}")
        
        # Verify the document was created
        verification_snapshot = await asyncio.to_thread(template_ref.get)
        if verification_snapshot.exists:
            print("✅ Verification: Document successfully created in Firestore")
        else:
            print("❌ Verification failed: Document not found after creation")
            
    except Exception as e:
        print(f"❌ Error setting up pricing template: {e}")
        raise

if __name__ == "__main__":
    print("🚀 Setting up default pricing template for SalesValueAnalystAgent...")
    print("=" * 60)
    
    try:
        asyncio.run(setup_pricing_template())
        print("=" * 60)
        print("✅ Pricing template setup completed successfully!")
        print("\nThe SalesValueAnalystAgent can now:")
        print("  • Read the pricing template from Firestore")
        print("  • Generate structured value projections")
        print("  • Use low/base/high scenario modeling")
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ Setup failed: {e}")
        exit(1) 