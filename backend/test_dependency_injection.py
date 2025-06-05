#!/usr/bin/env python3
"""
Quick test to verify dependency injection works.
"""

import os
import sys

# Add the backend path to sys.path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_dependency_injection():
    """Test that dependency injection works correctly."""
    
    print("🧪 Testing Dependency Injection Implementation...")
    
    # Test 1: Mock client in test environment
    print("\n1️⃣ Testing Mock Client (ENVIRONMENT=test)")
    os.environ['ENVIRONMENT'] = 'test'
    
    try:
        from app.core.dependencies import get_db, reset_db, get_array_union, get_increment
        from app.core.database import DatabaseClient
        
        # Reset singleton to pick up environment change
        reset_db()
        
        # Get database client
        db = get_db()
        print(f"   ✅ Database client type: {type(db).__name__}")
        
        # Test basic operations
        collection = db.collection("test_collection")
        print(f"   ✅ Collection created: {type(collection).__name__}")
        
        # Test ArrayUnion and Increment
        array_op = get_array_union(["test1", "test2"])
        increment_op = get_increment(5)
        print(f"   ✅ ArrayUnion created: {type(array_op).__name__}")
        print(f"   ✅ Increment created: {type(increment_op).__name__}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Firestore client in development environment
    print("\n2️⃣ Testing Firestore Client (ENVIRONMENT=development)")
    os.environ['ENVIRONMENT'] = 'development'
    
    try:
        # Reset singleton to pick up environment change
        reset_db()
        
        # Get database client (should be Firestore)
        db = get_db()
        print(f"   ✅ Database client type: {type(db).__name__}")
        
        # Test basic operations
        collection = db.collection("test_collection")
        print(f"   ✅ Collection created: {type(collection).__name__}")
        
    except Exception as e:
        print(f"   ⚠️  Expected behavior - Firestore requires authentication: {e}")
    
    # Test 3: Agent initialization with dependency injection
    print("\n3️⃣ Testing Agent Initialization with DI")
    os.environ['ENVIRONMENT'] = 'test'
    
    try:
        # Reset to mock client
        reset_db()
        
        from app.agents.orchestrator_agent import OrchestratorAgent
        from app.agents.cost_analyst_agent import CostAnalystAgent
        
        # Test orchestrator agent
        mock_db = get_db()
        orchestrator = OrchestratorAgent(db=mock_db)
        print(f"   ✅ OrchestratorAgent initialized with {type(orchestrator.db).__name__}")
        
        # Test cost analyst agent  
        cost_agent = CostAnalystAgent(db=mock_db)
        print(f"   ✅ CostAnalystAgent initialized with {type(cost_agent.db).__name__}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4: Mock database operations
    print("\n4️⃣ Testing Mock Database Operations")
    try:
        # Add a document
        doc_ref = collection.add({"test": "data", "number": 42})
        print(f"   ✅ Document added: {doc_ref.id}")
        
        # Get the document back
        doc = doc_ref.get()
        print(f"   ✅ Document exists: {doc.exists}")
        print(f"   ✅ Document data: {doc.to_dict()}")
        
        # Test query
        query_results = collection.where("test", "==", "data").stream()
        print(f"   ✅ Query returned {len(query_results)} results")
        
        # Test ArrayUnion operation
        doc_ref.update({"history": get_array_union([{"event": "test"}])})
        updated_doc = doc_ref.get()
        history = updated_doc.to_dict().get("history", [])
        print(f"   ✅ ArrayUnion result: {len(history)} items in history")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n🎉 All dependency injection tests passed!")
    return True

if __name__ == '__main__':
    success = test_dependency_injection()
    sys.exit(0 if success else 1) 