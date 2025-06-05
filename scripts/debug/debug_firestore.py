#!/usr/bin/env python3
"""Debug script to check Firestore documents"""

import asyncio
import sys
import os
sys.path.append('.')

from google.cloud import firestore

async def check_firestore():
    print("🔍 Checking Firestore documents...")
    
    try:
        db = firestore.Client(project='drfirst-business-case-gen')
        
        # List all documents in businessCases collection
        docs = await asyncio.to_thread(lambda: list(db.collection('businessCases').stream()))
        print(f"Total business cases: {len(docs)}")
        
        for doc in docs:
            data = doc.to_dict()
            print(f"ID: {doc.id}")
            print(f"  Title: {data.get('title', 'N/A')}")
            print(f"  Status: {data.get('status', 'N/A')}")
            print(f"  User: {data.get('user_id', 'N/A')}")
            print(f"  Created: {data.get('created_at', 'N/A')}")
            print()
            
        # Check rate cards
        rate_docs = await asyncio.to_thread(lambda: list(db.collection('rateCards').stream()))
        print(f"Rate cards: {len(rate_docs)}")
        for doc in rate_docs:
            data = doc.to_dict()
            print(f"Rate Card ID: {doc.id}")
            print(f"  Name: {data.get('name', 'N/A')}")
            print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_firestore()) 