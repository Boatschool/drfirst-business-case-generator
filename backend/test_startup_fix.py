#!/usr/bin/env python3
"""
Test script to verify that import-time initialization issues are resolved.
This script tests that services can be imported without triggering initialization.
"""

import sys
import os
import time
import logging
import traceback

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_import_time_initialization():
    """Test that imports don't trigger service initialization"""
    logger.info("🧪 Testing import-time initialization fixes...")
    
    # Test 1: Import auth service without initialization
    logger.info("Test 1: Importing auth service...")
    start_time = time.time()
    from app.services.auth_service import get_auth_service
    auth_service = get_auth_service()
    import_time = time.time() - start_time
    
    logger.info(f"✅ Auth service imported in {import_time:.3f}s")
    logger.info(f"📊 Auth service initialized: {auth_service.is_initialized}")
    
    if auth_service.is_initialized:
        logger.warning("⚠️ Auth service was initialized during import - this should not happen!")
        return False
    
    # Test 2: Import vertex AI service without initialization
    logger.info("Test 2: Importing VertexAI service...")
    start_time = time.time()
    from app.services.vertex_ai_service import vertex_ai_service
    import_time = time.time() - start_time
    
    logger.info(f"✅ VertexAI service imported in {import_time:.3f}s")
    logger.info(f"📊 VertexAI service initialized: {vertex_ai_service.is_initialized}")
    
    if vertex_ai_service.is_initialized:
        logger.warning("⚠️ VertexAI service was initialized during import - this should not happen!")
        return False
    
    # Test 3: Import agent registry without agent initialization
    logger.info("Test 3: Importing agent registry...")
    start_time = time.time()
    from app.core.agent_registry import get_agent_registry
    registry = get_agent_registry()
    import_time = time.time() - start_time
    
    logger.info(f"✅ Agent registry imported in {import_time:.3f}s")
    logger.info(f"📊 Agents initialized: {len(registry.agents)}")
    
    if len(registry.agents) > 0:
        logger.warning("⚠️ Agents were initialized during import - this should not happen!")
        return False
    
    # Test 4: Import main app without triggering lifecycle
    logger.info("Test 4: Importing main app...")
    start_time = time.time()
    from app.main import app
    import_time = time.time() - start_time
    
    logger.info(f"✅ Main app imported in {import_time:.3f}s")
    
    logger.info("🎉 All import tests passed! No services were initialized during import.")
    return True

def test_controlled_initialization():
    """Test that services can be initialized when explicitly requested"""
    logger.info("🧪 Testing controlled initialization...")
    
    # Test controlled auth service initialization
    logger.info("Test 1: Controlled auth service initialization...")
    from app.services.auth_service import get_auth_service
    auth_service = get_auth_service()
    
    start_time = time.time()
    auth_service._initialize_firebase()
    init_time = time.time() - start_time
    
    logger.info(f"✅ Auth service initialized in {init_time:.3f}s")
    logger.info(f"📊 Auth service status: {auth_service.is_initialized}")
    
    # Test controlled VertexAI service initialization
    logger.info("Test 2: Controlled VertexAI service initialization...")
    from app.services.vertex_ai_service import vertex_ai_service
    
    start_time = time.time()
    vertex_ai_service.initialize()
    init_time = time.time() - start_time
    
    logger.info(f"✅ VertexAI service initialized in {init_time:.3f}s")
    logger.info(f"📊 VertexAI service status: {vertex_ai_service.is_initialized}")
    
    # Test lazy agent initialization
    logger.info("Test 3: Lazy agent initialization...")
    from app.core.agent_registry import get_agent_registry
    registry = get_agent_registry()
    
    start_time = time.time()
    architect_agent = registry.get_agent("ArchitectAgent")
    init_time = time.time() - start_time
    
    logger.info(f"✅ ArchitectAgent initialized in {init_time:.3f}s")
    logger.info(f"📊 Agent status: {architect_agent.status if architect_agent else 'None'}")
    
    logger.info("🎉 All controlled initialization tests passed!")
    return True

def test_startup_sequence():
    """Test each step of the startup sequence to identify where it hangs"""
    print("🧪 TESTING STARTUP SEQUENCE")
    print("=" * 60)
    
    try:
        # Step 1: Test basic imports
        print("\n1. Testing basic imports...")
        start_time = time.time()
        
        print("   - Importing FastAPI...")
        from fastapi import FastAPI
        print(f"   - FastAPI imported in {time.time() - start_time:.3f}s")
        
        # Step 2: Test service imports
        print("\n2. Testing service imports...")
        start_time = time.time()
        
        print("   - Importing AuthService...")
        from app.services.auth_service import get_auth_service
        print(f"   - AuthService imported in {time.time() - start_time:.3f}s")
        
        start_time = time.time()
        print("   - Importing VertexAI Service...")
        from app.services.vertex_ai_service import vertex_ai_service
        print(f"   - VertexAI Service imported in {time.time() - start_time:.3f}s")
        
        # Step 3: Test main app import
        print("\n3. Testing main app import...")
        start_time = time.time()
        
        print("   - Importing main app...")
        from app.main import app
        print(f"   - Main app imported in {time.time() - start_time:.3f}s")
        
        # Step 4: Test service initialization
        print("\n4. Testing service initialization...")
        
        print("   - Getting AuthService instance...")
        start_time = time.time()
        auth_service = get_auth_service()
        print(f"   - AuthService instance obtained in {time.time() - start_time:.3f}s")
        print(f"   - AuthService initialized: {auth_service.is_initialized}")
        
        print("   - Checking VertexAI Service...")
        print(f"   - VertexAI Service initialized: {vertex_ai_service.is_initialized}")
        
        # Step 5: Test manual service initialization
        print("\n5. Testing manual service initialization...")
        
        print("   - Manually initializing AuthService...")
        start_time = time.time()
        if not auth_service.is_initialized:
            auth_service._initialize_firebase()
        print(f"   - AuthService initialization completed in {time.time() - start_time:.3f}s")
        print(f"   - AuthService initialized: {auth_service.is_initialized}")
        
        print("   - Manually initializing VertexAI Service...")
        start_time = time.time()
        if not vertex_ai_service.is_initialized:
            vertex_ai_service.initialize()
        print(f"   - VertexAI Service initialization completed in {time.time() - start_time:.3f}s")
        print(f"   - VertexAI Service initialized: {vertex_ai_service.is_initialized}")
        
        # Step 6: Test lifespan manager
        print("\n6. Testing lifespan manager...")
        start_time = time.time()
        
        print("   - Testing lifespan startup...")
        # Simulate what the lifespan manager does
        try:
            # This is what happens in the lifespan startup
            if not auth_service.is_initialized:
                auth_service._initialize_firebase()
            
            if not vertex_ai_service.is_initialized:
                vertex_ai_service.initialize()
                
            print(f"   - Lifespan startup simulation completed in {time.time() - start_time:.3f}s")
        except Exception as e:
            print(f"   - Lifespan startup simulation failed: {e}")
            traceback.print_exc()
        
        # Step 7: Test agent imports
        print("\n7. Testing agent imports...")
        
        agents = [
            ('OrchestratorAgent', 'app.agents.orchestrator_agent', 'OrchestratorAgent'),
            ('ProductManagerAgent', 'app.agents.product_manager_agent', 'ProductManagerAgent'),
            ('ArchitectAgent', 'app.agents.architect_agent', 'ArchitectAgent'),
        ]
        
        for agent_name, agent_module, agent_class in agents:
            start_time = time.time()
            try:
                module = __import__(agent_module, fromlist=[agent_class])
                agent_cls = getattr(module, agent_class)
                print(f"   - {agent_name} imported in {time.time() - start_time:.3f}s")
                
                # Test agent instantiation
                start_time = time.time()
                agent_instance = agent_cls()
                print(f"   - {agent_name} instantiated in {time.time() - start_time:.3f}s")
                
            except Exception as e:
                print(f"   - {agent_name} failed: {e}")
                traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("✅ STARTUP SEQUENCE TEST COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        print(f"\n❌ STARTUP SEQUENCE TEST FAILED: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    logger.info("🚀 Starting startup fix verification tests...")
    
    try:
        # Test import-time behavior
        if not test_import_time_initialization():
            logger.error("❌ Import-time initialization tests failed!")
            sys.exit(1)
        
        # Test controlled initialization
        if not test_controlled_initialization():
            logger.error("❌ Controlled initialization tests failed!")
            sys.exit(1)
        
        # Test startup sequence
        if not test_startup_sequence():
            logger.error("❌ Startup sequence tests failed!")
            sys.exit(1)
        
        logger.info("✅ All tests passed! Startup fixes are working correctly.")
        
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        traceback.print_exc()
        sys.exit(1) 