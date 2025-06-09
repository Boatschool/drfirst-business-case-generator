#!/usr/bin/env python3
"""
Minimal startup diagnostic script to identify what's hanging during server startup
"""

import sys
import os
import time
import traceback

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

def test_imports():
    """Test all critical imports step by step"""
    print("🧪 Testing imports step by step...")
    
    try:
        print("  ✓ Testing basic Python imports...")
        import logging
        import time
        from contextlib import asynccontextmanager
        print("  ✓ Basic imports successful")
        
        print("  ✓ Testing FastAPI imports...")
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        print("  ✓ FastAPI imports successful")
        
        print("  ✓ Testing Firebase imports...")
        import firebase_admin
        from firebase_admin import credentials
        print("  ✓ Firebase imports successful")
        
        print("  ✓ Testing app core imports...")
        from app.core.config import settings
        from app.core.logging_config import setup_logging
        print("  ✓ App core imports successful")
        
        print("  ✓ Testing service imports...")
        from app.services.auth_service import get_auth_service
        from app.services.vertex_ai_service import vertex_ai_service
        print("  ✓ Service imports successful")
        
        print("  ✓ Testing router imports...")
        from app.api.v1 import auth_routes, admin_routes, debug_routes
        from app.api.v1.cases import cases_router
        print("  ✓ Router imports successful")
        
        print("🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_service_initialization():
    """Test service initialization step by step"""
    print("\n🔧 Testing service initialization...")
    
    try:
        # Test AuthService initialization
        print("  ✓ Testing AuthService...")
        from app.services.auth_service import get_auth_service
        auth_service = get_auth_service()
        print(f"  ✓ AuthService instance created: {type(auth_service)}")
        
        # Don't actually initialize Firebase here, just test the import
        print("  ✓ AuthService test passed")
        
        # Test VertexAI service
        print("  ✓ Testing VertexAI service...")
        from app.services.vertex_ai_service import vertex_ai_service
        print(f"  ✓ VertexAI service instance: {type(vertex_ai_service)}")
        print("  ✓ VertexAI service test passed")
        
        print("🎉 Service initialization tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        traceback.print_exc()
        return False

def test_app_creation():
    """Test FastAPI app creation"""
    print("\n🚀 Testing FastAPI app creation...")
    
    try:
        from fastapi import FastAPI
        
        # Create a minimal app without lifespan
        app = FastAPI(title="Test App")
        print("  ✓ Basic FastAPI app created")
        
        # Test with lifespan
        from contextlib import asynccontextmanager
        
        @asynccontextmanager
        async def minimal_lifespan(app: FastAPI):
            print("  ✓ Lifespan startup")
            yield
            print("  ✓ Lifespan shutdown")
        
        app_with_lifespan = FastAPI(title="Test App with Lifespan", lifespan=minimal_lifespan)
        print("  ✓ FastAPI app with lifespan created")
        
        print("🎉 App creation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("🔍 DrFirst Backend Startup Diagnostic")
    print("=" * 50)
    
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path[:3]}...")
    print(f"🔑 GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'Not set')}")
    
    success = True
    
    # Test 1: Imports
    if not test_imports():
        success = False
    
    # Test 2: Service initialization
    if success and not test_service_initialization():
        success = False
        
    # Test 3: App creation
    if success and not test_app_creation():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All diagnostic tests passed!")
        print("💡 The issue might be in the actual server startup process")
        print("💡 Try running with: uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level debug")
    else:
        print("❌ Diagnostic tests failed - fix these issues first")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 