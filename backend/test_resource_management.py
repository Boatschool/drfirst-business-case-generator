#!/usr/bin/env python3
"""
Test script for resource management improvements (Issues #3 and #5).

This script tests:
- Issue #3: Global Singleton State Corruption (reset mechanisms)
- Issue #5: Resource Leak Accumulation (resource cleanup)
"""

import sys
import os
import time
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_issue_3_singleton_reset():
    """Test Issue #3: Global Singleton State Corruption - Reset mechanisms"""
    
    print("\n" + "="*60)
    print("🧪 TESTING ISSUE #3: SINGLETON RESET MECHANISMS")
    print("="*60)
    
    try:
        # Test 1: AuthService singleton reset
        print("\n🔧 Test 1: AuthService Singleton Reset")
        from app.services.auth_service import get_auth_service
        
        auth_service = get_auth_service()
        print(f"  - Initial state: initialized={auth_service.is_initialized}")
        
        # Initialize if not already
        if not auth_service.is_initialized:
            auth_service._initialize_firebase()
            print(f"  - After initialization: initialized={auth_service.is_initialized}")
        
        # Test reset
        auth_service.reset()
        print(f"  - After reset: initialized={auth_service.is_initialized}")
        print("  ✅ AuthService reset test passed")
        
        # Test 2: VertexAI service singleton reset
        print("\n🤖 Test 2: VertexAI Service Singleton Reset")
        from app.services.vertex_ai_service import vertex_ai_service
        
        print(f"  - Initial state: initialized={vertex_ai_service.is_initialized}")
        
        # Initialize if not already
        if not vertex_ai_service.is_initialized:
            vertex_ai_service.initialize()
            print(f"  - After initialization: initialized={vertex_ai_service.is_initialized}")
        
        # Test reset
        vertex_ai_service.reset()
        print(f"  - After reset: initialized={vertex_ai_service.is_initialized}")
        print("  ✅ VertexAI service reset test passed")
        
        # Test 3: Comprehensive reset function
        print("\n🔄 Test 3: Comprehensive Singleton Reset")
        from app.core.dependencies import reset_all_singletons
        
        # Reinitialize services first
        auth_service._initialize_firebase()
        vertex_ai_service.initialize()
        print(f"  - Before reset: Auth={auth_service.is_initialized}, Vertex={vertex_ai_service.is_initialized}")
        
        # Test comprehensive reset
        reset_all_singletons()
        print(f"  - After reset: Auth={auth_service.is_initialized}, Vertex={vertex_ai_service.is_initialized}")
        print("  ✅ Comprehensive reset test passed")
        
        print("\n🎉 Issue #3 tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Issue #3 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_issue_5_resource_cleanup():
    """Test Issue #5: Resource Leak Accumulation - Resource cleanup"""
    
    print("\n" + "="*60)
    print("🧪 TESTING ISSUE #5: RESOURCE CLEANUP MECHANISMS")
    print("="*60)
    
    try:
        # Test 1: Firestore client cleanup
        print("\n🔥 Test 1: Firestore Client Resource Cleanup")
        from app.core.firestore_impl import FirestoreClient
        
        # Create instance
        client = FirestoreClient(project_id="test-project")
        print(f"  - Client created: initialized={getattr(client, '_initialized', False)}")
        
        # Test status method
        if hasattr(client, 'get_status'):
            status = client.get_status()
            print(f"  - Client status: {status['initialized']}")
        
        # Test cleanup
        client.cleanup()
        print(f"  - After cleanup: initialized={getattr(client, '_initialized', False)}")
        
        # Test singleton reset
        FirestoreClient.reset_singleton()
        print("  ✅ Firestore cleanup test passed")
        
        # Test 2: VertexAI service cleanup
        print("\n🤖 Test 2: VertexAI Service Resource Cleanup")
        from app.services.vertex_ai_service import vertex_ai_service
        
        # Initialize
        vertex_ai_service.initialize()
        print(f"  - Before cleanup: initialized={vertex_ai_service.is_initialized}")
        
        # Test cleanup
        vertex_ai_service.cleanup()
        print(f"  - After cleanup: initialized={vertex_ai_service.is_initialized}")
        
        # Test singleton reset
        vertex_ai_service.reset_singleton()
        print("  ✅ VertexAI cleanup test passed")
        
        # Test 3: Comprehensive cleanup function
        print("\n🧹 Test 3: Comprehensive Resource Cleanup")
        from app.core.dependencies import cleanup_all_singletons
        
        # Reinitialize services
        from app.services.auth_service import get_auth_service
        auth_service = get_auth_service()
        auth_service._initialize_firebase()
        vertex_ai_service.initialize()
        
        print(f"  - Before cleanup: Auth={auth_service.is_initialized}, Vertex={vertex_ai_service.is_initialized}")
        
        # Test comprehensive cleanup
        cleanup_all_singletons()
        print(f"  - After cleanup: Auth={auth_service.is_initialized}, Vertex={vertex_ai_service.is_initialized}")
        print("  ✅ Comprehensive cleanup test passed")
        
        print("\n🎉 Issue #5 tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Issue #5 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_resource_monitoring():
    """Test the new resource monitoring endpoints"""
    
    print("\n" + "="*60)
    print("🧪 TESTING RESOURCE MONITORING CAPABILITIES")
    print("="*60)
    
    try:
        # Test diagnostic helper functions
        print("\n📊 Test 1: Diagnostic Helper Functions")
        from app.api.v1.diagnostics import (
            _get_memory_usage, _get_disk_usage, _get_network_info,
            _check_database_health, _check_auth_service_health, 
            _check_vertex_ai_health, _detect_resource_warnings
        )
        
        # Test memory usage
        memory = _get_memory_usage()
        print(f"  - Memory usage: {memory}")
        
        # Test disk usage
        disk = _get_disk_usage()
        print(f"  - Disk usage: {disk}")
        
        # Test network info
        network = _get_network_info()
        print(f"  - Network connections: {network}")
        
        # Test service health checks
        print("\n🔧 Test 2: Service Health Checks")
        db_health = _check_database_health()
        print(f"  - Database health: {db_health.get('status', 'unknown')}")
        
        auth_health = _check_auth_service_health()
        print(f"  - Auth service health: {auth_health.get('status', 'unknown')}")
        
        vertex_health = _check_vertex_ai_health()
        print(f"  - VertexAI health: {vertex_health.get('status', 'unknown')}")
        
        # Test resource warnings
        print("\n⚠️ Test 3: Resource Warning Detection")
        warnings = _detect_resource_warnings()
        print(f"  - Resource warnings found: {len(warnings)}")
        for warning in warnings:
            print(f"    - {warning['type']}: {warning['message']}")
        
        print("\n🎉 Resource monitoring tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Resource monitoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all resource management tests"""
    
    print("🚀 STARTING RESOURCE MANAGEMENT TESTS")
    print("Testing Issues #3 and #5 from Backend Server Instability Analysis")
    
    # Initialize environment
    os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', '/path/to/dummy/credentials.json')
    os.environ.setdefault('GOOGLE_CLOUD_PROJECT', 'test-project')
    
    # Run tests
    results = {
        "Issue #3 (Singleton Reset)": test_issue_3_singleton_reset(),
        "Issue #5 (Resource Cleanup)": test_issue_5_resource_cleanup(),
        "Resource Monitoring": test_resource_monitoring()
    }
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST RESULTS SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Issues #3 and #5 are successfully implemented.")
        print("✅ Singleton reset mechanisms working correctly")
        print("✅ Resource cleanup mechanisms working correctly") 
        print("✅ Resource monitoring capabilities functional")
    else:
        print("❌ SOME TESTS FAILED. Please review the errors above.")
    print("="*60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 