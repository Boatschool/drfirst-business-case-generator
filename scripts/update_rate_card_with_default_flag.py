#!/usr/bin/env python3
"""
Script to update the existing rate card in Firestore to add the isDefault flag.
This will ensure the enhanced CostAnalystAgent can properly identify the default rate card.
"""

import os
import sys
from datetime import datetime, timezone

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from google.cloud import firestore
from app.core.config import settings

def update_rate_card_with_default_flag():
    """
    Updates the existing rate card document to add the isDefault flag.
    """
    try:
        # Initialize Firestore client
        db = firestore.Client(project=settings.firebase_project_id)
        print(f"Connected to Firestore project: {settings.firebase_project_id}")
        
        # Reference to the existing rate card document
        doc_ref = db.collection("rateCards").document("default_dev_rates")
        
        # Check if the document exists
        doc = doc_ref.get()
        if not doc.exists:
            print("❌ Rate card document 'default_dev_rates' not found")
            print("   Please run setup_firestore_rate_card.py first to create the initial rate card")
            return False
        
        # Update the document to add the isDefault flag
        update_data = {
            "isDefault": True,
            "updated_at": datetime.now(timezone.utc)
        }
        
        doc_ref.update(update_data)
        
        print("✅ Successfully updated rate card document:")
        print(f"   Document ID: default_dev_rates")
        print(f"   Collection: rateCards")
        print(f"   Added field: isDefault = True")
        
        # Verify the update
        updated_doc = doc_ref.get()
        if updated_doc.exists:
            data = updated_doc.to_dict()
            if data.get('isDefault', False):
                print("✅ Rate card update verified in Firestore")
                print(f"   Rate card '{data.get('name', 'Unknown')}' is now marked as default")
                return True
            else:
                print("❌ Failed to verify isDefault flag in updated document")
                return False
        else:
            print("❌ Failed to verify updated rate card document")
            return False
            
    except Exception as e:
        print(f"❌ Error updating rate card: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Updating rate card with isDefault flag...")
    success = update_rate_card_with_default_flag()
    
    if success:
        print("\n🎉 Rate card update complete!")
        print("The enhanced CostAnalystAgent can now properly identify the default rate card.")
    else:
        print("\n💥 Rate card update failed!")
        print("Check your Firestore configuration and ensure the rate card exists.")
        sys.exit(1) 