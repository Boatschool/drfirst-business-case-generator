#!/usr/bin/env python3
"""
Test script to identify import-time initialization issues
"""
import sys
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test what gets initialized during imports"""
    print("🧪 TESTING IMPORT-TIME INITIALIZATION")
    print("=" * 60)
    
    # Before importing anything, check initial state
    print("\n1. Initial State Check:")
    print(f"   - Python modules loaded: {len(sys.modules)}")
    
    # Test AuthService import
    print("\n2. Testing AuthService import...")
    start_time = time.time()
    try:
        from app.services.auth_service import get_auth_service
        auth_service = get_auth_service()
        import_time = time.time() - start_time
        print(f"   - AuthService imported in {import_time:.3f}s")
        print(f"   - AuthService initialized: {auth_service.is_initialized}")
    except Exception as e:
        print(f"   - AuthService import failed: {e}")
    
    # Test VertexAI Service import
    print("\n3. Testing VertexAI Service import...")
    start_time = time.time()
    try:
        from app.services.vertex_ai_service import vertex_ai_service
        import_time = time.time() - start_time
        print(f"   - VertexAI Service imported in {import_time:.3f}s")
        print(f"   - VertexAI Service initialized: {vertex_ai_service.is_initialized}")
    except Exception as e:
        print(f"   - VertexAI Service import failed: {e}")
    
    # Test Agent imports
    print("\n4. Testing Agent imports...")
    agents = [
        ('ArchitectAgent', 'app.agents.architect_agent'),
        ('PlannerAgent', 'app.agents.planner_agent'),
        ('SalesValueAnalystAgent', 'app.agents.sales_value_analyst_agent'),
        ('ProductManagerAgent', 'app.agents.product_manager_agent'),
        ('OrchestratorAgent', 'app.agents.orchestrator_agent')
    ]
    
    for agent_name, agent_module in agents:
        start_time = time.time()
        try:
            __import__(agent_module)
            import_time = time.time() - start_time
            print(f"   - {agent_name} imported in {import_time:.3f}s")
        except Exception as e:
            print(f"   - {agent_name} import failed: {e}")
    
    # Test main app import
    print("\n5. Testing main app import...")
    start_time = time.time()
    try:
        from app.main import app
        import_time = time.time() - start_time
        print(f"   - Main app imported in {import_time:.3f}s")
    except Exception as e:
        print(f"   - Main app import failed: {e}")
    
    # Final state check
    print(f"\n6. Final State Check:")
    print(f"   - Total modules loaded: {len(sys.modules)}")
    
    # Check service states again
    try:
        from app.services.auth_service import get_auth_service
        from app.services.vertex_ai_service import vertex_ai_service
        auth_service = get_auth_service()
        print(f"   - AuthService initialized: {auth_service.is_initialized}")
        print(f"   - VertexAI Service initialized: {vertex_ai_service.is_initialized}")
    except Exception as e:
        print(f"   - Error checking final service states: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 IMPORT TEST COMPLETED")

if __name__ == "__main__":
    test_imports() 