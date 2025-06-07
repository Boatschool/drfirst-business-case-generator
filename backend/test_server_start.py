#!/usr/bin/env python3
"""
Test script to start the server directly to verify the app works
"""
import sys
import time
import logging
import asyncio
from contextlib import asynccontextmanager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_app_startup():
    """Test the FastAPI app startup directly"""
    print("🧪 TESTING DIRECT APP STARTUP")
    print("=" * 60)
    
    try:
        # Import the app
        print("\n1. Importing FastAPI app...")
        start_time = time.time()
        from app.main import app
        print(f"   - App imported in {time.time() - start_time:.3f}s")
        
        # Test the lifespan manager directly
        print("\n2. Testing lifespan manager...")
        start_time = time.time()
        
        # Get the lifespan function from the app
        lifespan_func = app.router.lifespan_context
        
        print("   - Starting lifespan context...")
        async with lifespan_func(app) as lifespan_state:
            print(f"   - Lifespan startup completed in {time.time() - start_time:.3f}s")
            
            # Test some basic app functionality
            print("\n3. Testing app functionality...")
            
            # Test that we can access the app
            print(f"   - App title: {app.title}")
            print(f"   - App version: {app.version}")
            
            # Test routes
            routes = [route.path for route in app.routes if hasattr(route, 'path')]
            print(f"   - Number of routes: {len(routes)}")
            print(f"   - Sample routes: {routes[:5]}")
            
            print("\n4. Testing service health...")
            
            # Test AuthService
            from app.services.auth_service import get_auth_service
            auth_service = get_auth_service()
            print(f"   - AuthService initialized: {auth_service.is_initialized}")
            
            # Test VertexAI Service
            from app.services.vertex_ai_service import vertex_ai_service
            print(f"   - VertexAI Service initialized: {vertex_ai_service.is_initialized}")
            
            print("\n5. Simulating server operation...")
            print("   - App is ready to serve requests")
            print("   - Waiting 2 seconds to simulate operation...")
            await asyncio.sleep(2)
            print("   - Simulated operation completed")
            
        print(f"\n   - Lifespan shutdown completed")
        
        print("\n" + "=" * 60)
        print("✅ DIRECT APP STARTUP TEST COMPLETED SUCCESSFULLY")
        return True
        
    except Exception as e:
        print(f"\n❌ DIRECT APP STARTUP TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_app_startup()
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 