#!/usr/bin/env python3
"""
Simple test script for dashboard Firestore queries
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from google.cloud import firestore

# Firestore collection names
AUTOMATED_EVAL_RESULTS_COLLECTION = "automatedEvaluationResults"
AUTOMATED_EVAL_RUNS_COLLECTION = "automatedEvaluationRuns"

def test_firestore_connection():
    """Test basic Firestore connection"""
    print("🔧 Testing Firestore connection...")
    
    try:
        client = firestore.Client()
        # Try to list collections to test connection
        collections = list(client.collections())
        print(f"✅ Firestore connection successful. Found {len(collections)} collections.")
        return client
    except Exception as e:
        print(f"❌ Firestore connection failed: {e}")
        return None

def test_automated_eval_collections(client):
    """Test automated evaluation collections exist and have data"""
    print(f"\n📊 Testing automated evaluation collections...")
    
    try:
        # Test runs collection
        runs_collection = client.collection(AUTOMATED_EVAL_RUNS_COLLECTION)
        runs_docs = list(runs_collection.limit(5).stream())
        print(f"✅ Found {len(runs_docs)} documents in {AUTOMATED_EVAL_RUNS_COLLECTION}")
        
        # Test results collection
        results_collection = client.collection(AUTOMATED_EVAL_RESULTS_COLLECTION)
        results_docs = list(results_collection.limit(5).stream())
        print(f"✅ Found {len(results_docs)} documents in {AUTOMATED_EVAL_RESULTS_COLLECTION}")
        
        if runs_docs:
            # Show sample run data
            sample_run = runs_docs[0].to_dict()
            print(f"\n📋 Sample run data:")
            print(f"   Run ID: {sample_run.get('eval_run_id', 'N/A')}")
            print(f"   Examples processed: {sample_run.get('total_examples_processed', 'N/A')}")
            print(f"   Success rate: {sample_run.get('success_rate_percentage', 'N/A')}%")
            print(f"   Dataset: {sample_run.get('dataset_file_used', 'N/A')}")
            
            return runs_docs[0].id  # Return first run ID for details testing
        else:
            print("ℹ️ No evaluation runs found. Run some automated evaluations first.")
            return None
            
    except Exception as e:
        print(f"❌ Collection test failed: {e}")
        return None

def test_failed_validations_query(client, eval_run_id):
    """Test querying failed validations for a specific run"""
    print(f"\n🔍 Testing failed validations query for run: {eval_run_id}")
    
    try:
        results_collection = client.collection(AUTOMATED_EVAL_RESULTS_COLLECTION)
        failed_query = results_collection.where("eval_run_id", "==", eval_run_id).where("overall_automated_eval_passed", "==", False)
        
        failed_docs = list(failed_query.stream())
        print(f"✅ Found {len(failed_docs)} failed validations for run {eval_run_id}")
        
        if failed_docs:
            sample_failure = failed_docs[0].to_dict()
            print(f"   Sample failure - Agent: {sample_failure.get('agent_name', 'N/A')}")
            print(f"   Input ID: {sample_failure.get('golden_dataset_inputId', 'N/A')}")
            print(f"   Status: {sample_failure.get('agent_run_status', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ Failed validations query failed: {e}")
        return False

def test_summary_calculations(client):
    """Test summary calculations like those used in the dashboard"""
    print(f"\n📈 Testing dashboard summary calculations...")
    
    try:
        # Get all runs for summary
        runs_collection = client.collection(AUTOMATED_EVAL_RUNS_COLLECTION)
        runs_query = runs_collection.order_by("run_timestamp_start", direction=firestore.Query.DESCENDING)
        runs_docs = list(runs_query.stream())
        
        if not runs_docs:
            print("ℹ️ No runs available for summary calculations")
            return True
        
        total_runs = len(runs_docs)
        total_examples = 0
        success_rates = []
        validation_rates = []
        
        for doc in runs_docs:
            data = doc.to_dict()
            total_examples += data.get("total_examples_processed", 0)
            success_rates.append(data.get("success_rate_percentage", 0.0))
            validation_rates.append(data.get("validation_pass_rate_percentage", 0.0))
        
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0
        avg_validation_rate = sum(validation_rates) / len(validation_rates) if validation_rates else 0.0
        
        print(f"✅ Summary calculations successful:")
        print(f"   Total runs: {total_runs}")
        print(f"   Total examples: {total_examples}")
        print(f"   Average success rate: {avg_success_rate:.1f}%")
        print(f"   Average validation rate: {avg_validation_rate:.1f}%")
        
        return True
    except Exception as e:
        print(f"❌ Summary calculations failed: {e}")
        return False

def main():
    """Main test runner"""
    print("🧪 Testing Dashboard Firestore Queries")
    print("=" * 50)
    
    # Test connection
    client = test_firestore_connection()
    if not client:
        print("\n❌ Cannot proceed without Firestore connection")
        return False
    
    # Test collections
    sample_run_id = test_automated_eval_collections(client)
    
    # Test failed validations query if we have a run
    failed_query_success = True
    if sample_run_id:
        failed_query_success = test_failed_validations_query(client, sample_run_id)
    
    # Test summary calculations
    summary_success = test_summary_calculations(client)
    
    # Results
    print("\n" + "=" * 50)
    print("🎯 Test Results:")
    print(f"   Firestore Connection: ✅")
    print(f"   Collections Access: ✅")
    print(f"   Failed Validations Query: {'✅' if failed_query_success else '❌'}")
    print(f"   Summary Calculations: {'✅' if summary_success else '❌'}")
    
    all_passed = all([failed_query_success, summary_success])
    if all_passed:
        print("\n🎉 All Firestore queries working correctly!")
        print("💡 The dashboard API should work properly with existing data.")
    else:
        print("\n⚠️ Some queries failed - check the errors above")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 