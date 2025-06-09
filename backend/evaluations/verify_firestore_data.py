#!/usr/bin/env python3
"""
Verification script to check that evaluation data was saved to Firestore.
"""

import os
import sys
from datetime import datetime, timezone

# Add the backend app to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set required environment variables if missing (for testing purposes)
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'test-secret-key-for-verification'

from google.cloud import firestore

# Import collection constants
from run_automated_evals import (
    AUTOMATED_EVAL_RESULTS_COLLECTION,
    AUTOMATED_EVAL_RUNS_COLLECTION
)

def verify_firestore_data():
    """Verify that evaluation data exists in Firestore collections."""
    print("🔍 Verifying Firestore Data...")
    
    try:
        # Initialize Firestore client
        db = firestore.Client()
        print("✅ Firestore client initialized")
        
        # Check evaluation results collection
        print(f"\n📄 Checking {AUTOMATED_EVAL_RESULTS_COLLECTION} collection...")
        results_collection = db.collection(AUTOMATED_EVAL_RESULTS_COLLECTION)
        results_docs = list(results_collection.limit(10).stream())
        
        print(f"   Found {len(results_docs)} documents in results collection")
        
        for doc in results_docs[-3:]:  # Show last 3 documents
            data = doc.to_dict()
            print(f"   📝 Document ID: {doc.id}")
            print(f"      eval_run_id: {data.get('eval_run_id', 'N/A')}")
            print(f"      agent_name: {data.get('agent_name', 'N/A')}")
            print(f"      inputId: {data.get('golden_dataset_inputId', 'N/A')}")
            print(f"      status: {data.get('agent_run_status', 'N/A')}")
            print(f"      validation_passed: {data.get('overall_automated_eval_passed', 'N/A')}")
            print(f"      timestamp: {data.get('timestamp', 'N/A')}")
            print()
        
        # Check evaluation runs collection
        print(f"📋 Checking {AUTOMATED_EVAL_RUNS_COLLECTION} collection...")
        runs_collection = db.collection(AUTOMATED_EVAL_RUNS_COLLECTION)
        runs_docs = list(runs_collection.limit(5).stream())
        
        print(f"   Found {len(runs_docs)} documents in runs collection")
        
        for doc in runs_docs[-2:]:  # Show last 2 documents
            data = doc.to_dict()
            print(f"   📊 Run ID: {doc.id}")
            print(f"      total_examples: {data.get('total_examples_processed', 'N/A')}")
            print(f"      successful_runs: {data.get('successful_agent_runs', 'N/A')}")
            print(f"      validation_passed: {data.get('overall_validation_passed_count', 'N/A')}")
            print(f"      dataset_file: {data.get('dataset_file_used', 'N/A')}")
            print(f"      start_time: {data.get('run_timestamp_start', 'N/A')}")
            print(f"      end_time: {data.get('run_timestamp_end', 'N/A')}")
            print()
        
        # Try to query for recent results
        print("🔍 Querying for recent evaluation results...")
        recent_time = datetime.now(timezone.utc)
        # Query for results from the last hour
        query = results_collection.where("timestamp", ">=", 
                                        datetime(recent_time.year, recent_time.month, 
                                               recent_time.day, recent_time.hour - 1, 
                                               tzinfo=timezone.utc))
        recent_docs = list(query.stream())
        print(f"   Found {len(recent_docs)} recent evaluation results")
        
        if results_docs or runs_docs:
            print("\n✅ SUCCESS: Firestore persistence is working correctly!")
            print(f"   📄 {len(results_docs)} evaluation results found")
            print(f"   📋 {len(runs_docs)} evaluation runs found")
            return True
        else:
            print("\n⚠️ WARNING: No evaluation data found in Firestore")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying Firestore data: {e}")
        return False

def main():
    """Main verification function."""
    print("🔍 DrFirst Automated Evaluation - Firestore Data Verification")
    print("=" * 60)
    
    success = verify_firestore_data()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Verification completed successfully!")
        return 0
    else:
        print("⚠️ Verification found issues. Check Firestore configuration.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 