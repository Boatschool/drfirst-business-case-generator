#!/usr/bin/env python3
"""
Test script for Firestore integration in automated evaluation runner.

This script tests the Firestore persistence functionality without running
the full evaluation suite.
"""

import os
import sys
import json
import uuid
from datetime import datetime, timezone

# Add the backend app to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set required environment variables if missing (for testing purposes)
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'test-secret-key-for-firestore-test'

from google.cloud import firestore

# Import collection constants
from run_automated_evals import (
    AUTOMATED_EVAL_RESULTS_COLLECTION,
    AUTOMATED_EVAL_RUNS_COLLECTION
)

def test_firestore_connection():
    """Test basic Firestore connection and operations."""
    print("🧪 Testing Firestore Connection...")
    
    try:
        # Initialize Firestore client
        db = firestore.Client()
        print("✅ Firestore client initialized successfully")
        
        # Test write operation
        test_doc_id = f"test_{uuid.uuid4()}"
        test_data = {
            "test_timestamp": datetime.now(timezone.utc),
            "test_message": "Firestore integration test"
        }
        
        doc_ref = db.collection("test_collection").document(test_doc_id)
        doc_ref.set(test_data)
        print(f"✅ Test document written: {test_doc_id}")
        
        # Test read operation
        doc = doc_ref.get()
        if doc.exists:
            print("✅ Test document read successfully")
            print(f"   Data: {doc.to_dict()}")
        else:
            print("❌ Test document not found")
            return False
        
        # Clean up test document
        doc_ref.delete()
        print("✅ Test document cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Firestore connection test failed: {e}")
        return False

def test_evaluation_collections():
    """Test operations on the evaluation collections."""
    print("\n🧪 Testing Evaluation Collections...")
    
    try:
        db = firestore.Client()
        
        # Test data for automated evaluation result
        eval_run_id = str(uuid.uuid4())
        test_result_data = {
            "eval_run_id": eval_run_id,
            "golden_dataset_inputId": "test_input_001",
            "agent_name": "TestAgent",
            "case_id": None,
            "trace_id": None,
            "timestamp": datetime.now(timezone.utc),
            "input_payload_summary": "Test input for Firestore integration",
            "live_agent_output_summary_or_ref": "Test agent output summary",
            "validation_results": {
                "test_metric_1": True,
                "test_metric_2": False
            },
            "overall_automated_eval_passed": False,
            "agent_run_status": "SUCCESS",
            "agent_error_message": "",
            "execution_time_ms": 1500,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Save test result
        result_doc_id = f"{eval_run_id}_test_input_001"
        result_ref = db.collection(AUTOMATED_EVAL_RESULTS_COLLECTION).document(result_doc_id)
        result_ref.set(test_result_data)
        print(f"✅ Test evaluation result saved: {result_doc_id}")
        
        # Test data for evaluation run summary
        test_summary_data = {
            "eval_run_id": eval_run_id,
            "run_timestamp_start": datetime.now(timezone.utc),
            "run_timestamp_end": datetime.now(timezone.utc),
            "total_examples_processed": 1,
            "successful_agent_runs": 1,
            "failed_agent_runs": 0,
            "overall_validation_passed_count": 0,
            "dataset_file_used": "test_dataset.json",
            "success_rate_percentage": 100.0,
            "validation_pass_rate_percentage": 0.0,
            "total_evaluation_time_seconds": 5,
            "agent_specific_statistics": {
                "TestAgent": {
                    "total": 1,
                    "successful_runs": 1,
                    "validation_passed": 0,
                    "avg_execution_time_ms": 1500
                }
            }
        }
        
        # Save test summary
        summary_ref = db.collection(AUTOMATED_EVAL_RUNS_COLLECTION).document(eval_run_id)
        summary_ref.set(test_summary_data)
        print(f"✅ Test evaluation run summary saved: {eval_run_id}")
        
        # Verify data can be read back
        result_doc = result_ref.get()
        summary_doc = summary_ref.get()
        
        if result_doc.exists and summary_doc.exists:
            print("✅ Test documents read back successfully")
            print(f"   Result document fields: {list(result_doc.to_dict().keys())}")
            print(f"   Summary document fields: {list(summary_doc.to_dict().keys())}")
        else:
            print("❌ Failed to read back test documents")
            return False
        
        # Clean up test documents
        result_ref.delete()
        summary_ref.delete()
        print("✅ Test documents cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Evaluation collections test failed: {e}")
        return False

def test_query_operations():
    """Test querying operations on evaluation collections."""
    print("\n🧪 Testing Query Operations...")
    
    try:
        db = firestore.Client()
        
        # Create multiple test documents for querying
        eval_run_id = str(uuid.uuid4())
        test_docs = []
        
        for i in range(3):
            result_data = {
                "eval_run_id": eval_run_id,
                "golden_dataset_inputId": f"test_input_{i:03d}",
                "agent_name": "TestAgent",
                "timestamp": datetime.now(timezone.utc),
                "validation_results": {"test_metric": i % 2 == 0},
                "overall_automated_eval_passed": i % 2 == 0,
                "agent_run_status": "SUCCESS",
                "execution_time_ms": 1000 + (i * 100)
            }
            
            doc_id = f"{eval_run_id}_test_input_{i:03d}"
            doc_ref = db.collection(AUTOMATED_EVAL_RESULTS_COLLECTION).document(doc_id)
            doc_ref.set(result_data)
            test_docs.append(doc_ref)
        
        print(f"✅ Created {len(test_docs)} test documents")
        
        # Query by eval_run_id
        query = db.collection(AUTOMATED_EVAL_RESULTS_COLLECTION).where("eval_run_id", "==", eval_run_id)
        docs = list(query.stream())
        print(f"✅ Query by eval_run_id returned {len(docs)} documents")
        
        # Query by agent_name
        query = db.collection(AUTOMATED_EVAL_RESULTS_COLLECTION).where("agent_name", "==", "TestAgent")
        docs = list(query.stream())
        print(f"✅ Query by agent_name returned {len(docs)} documents (may include previous test data)")
        
        # Query by validation result
        query = db.collection(AUTOMATED_EVAL_RESULTS_COLLECTION).where("overall_automated_eval_passed", "==", True)
        docs = list(query.stream())
        print(f"✅ Query by validation result returned {len(docs)} documents")
        
        # Clean up test documents
        for doc_ref in test_docs:
            doc_ref.delete()
        print("✅ Test documents cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Query operations test failed: {e}")
        return False

def main():
    """Run all Firestore integration tests."""
    print("🧪 DrFirst Automated Evaluation - Firestore Integration Test")
    print("=" * 60)
    
    tests = [
        ("Basic Firestore Connection", test_firestore_connection),
        ("Evaluation Collections", test_evaluation_collections),
        ("Query Operations", test_query_operations)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Firestore integration is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check Firestore configuration and credentials.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 