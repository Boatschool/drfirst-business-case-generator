#!/usr/bin/env python3
"""
Script to set up stub rate card in Firestore for development and testing.
This rate card will be used by the CostAnalystAgent to calculate cost estimates.
"""

import os
import sys
from datetime import datetime, timezone

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from google.cloud import firestore
from app.core.config import settings

def setup_rate_card():
    """
    Creates a stub rate card document in Firestore for CostAnalystAgent to use.
    """
    try:
        # Initialize Firestore client
        db = firestore.Client(project=settings.firebase_project_id)
        print(f"Connected to Firestore project: {settings.firebase_project_id}")
        
        # Define the stub rate card data
        rate_card_data = {
            "name": "Default Development Rates V1",
            "description": "Placeholder rates for initial cost estimation in business case generation.",
            "isActive": True,
            "defaultOverallRate": 100,  # USD per hour fallback rate
            "currency": "USD",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "roles": [
                {
                    "roleName": "Developer",
                    "hourlyRate": 100,
                    "currency": "USD",
                    "description": "Software developer/engineer"
                },
                {
                    "roleName": "Product Manager", 
                    "hourlyRate": 120,
                    "currency": "USD",
                    "description": "Product management and strategy"
                },
                {
                    "roleName": "QA Engineer",
                    "hourlyRate": 85,
                    "currency": "USD", 
                    "description": "Quality assurance and testing"
                },
                {
                    "roleName": "DevOps Engineer",
                    "hourlyRate": 110,
                    "currency": "USD",
                    "description": "DevOps and infrastructure"
                },
                {
                    "roleName": "UI/UX Designer",
                    "hourlyRate": 95,
                    "currency": "USD",
                    "description": "User interface and experience design"
                }
            ]
        }
        
        # Create the document in the rateCards collection
        doc_ref = db.collection("rateCards").document("default_dev_rates")
        doc_ref.set(rate_card_data)
        
        print("✅ Successfully created stub rate card document:")
        print(f"   Document ID: default_dev_rates")
        print(f"   Collection: rateCards")
        print(f"   Default Rate: ${rate_card_data['defaultOverallRate']}/hour")
        print(f"   Roles: {len(rate_card_data['roles'])} defined")
        
        # Verify the document was created
        doc = doc_ref.get()
        if doc.exists:
            print("✅ Rate card document verified in Firestore")
            return True
        else:
            print("❌ Failed to verify rate card document")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up rate card: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Setting up stub rate card in Firestore...")
    success = setup_rate_card()
    
    if success:
        print("\n🎉 Rate card setup complete!")
        print("The CostAnalystAgent can now fetch rates from Firestore.")
    else:
        print("\n💥 Rate card setup failed!")
        print("Check your Firestore configuration and permissions.")
        sys.exit(1) 