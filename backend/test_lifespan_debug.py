#!/usr/bin/env python3
"""
Debug script to test the lifespan startup process step by step.
"""

import sys
import time
import traceback
import os

def test_step(step_name, func):
    """Test a step with timing and error handling"""
    print(f"🔍 Testing: {step_name}")
    start_time = time.time()
    
    try:
        result = func()
        duration = time.time() - start_time
        print(f"✅ {step_name}: {duration:.3f}s")
        return True, result
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ {step_name}: FAILED after {duration:.3f}s")
        print(f"   Error: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False, None

def main():
    print("🚀 Lifespan Startup Debug Test")
    print("=" * 50)
    
    # Step 1: Import dependencies
    def import_deps():
        from app.core.dependencies import reset_all_singletons, cleanup_all_singletons
        from app.services.auth_service import get_auth_service
        from app.services.vertex_ai_service import vertex_ai_service
        return reset_all_singletons, cleanup_all_singletons, get_auth_service, vertex_ai_service
    
    success, deps = test_step("Import dependencies", import_deps)
    if not success:
        return
    
    reset_all_singletons, cleanup_all_singletons, get_auth_service, vertex_ai_service = deps
    
    # Step 2: Reset singletons
    def reset_singletons():
        reset_all_singletons()
        return "Reset completed"
    
    success, _ = test_step("Reset singletons", reset_singletons)
    if not success:
        return
    
    # Step 3: Get auth service
    def get_auth():
        auth_service = get_auth_service()
        return auth_service
    
    success, auth_service = test_step("Get auth service", get_auth)
    if not success:
        return
    
    # Step 4: Initialize Firebase (this is likely where it hangs)
    def init_firebase():
        print("   🔥 Starting Firebase initialization...")
        auth_service._initialize_firebase()
        print("   🔥 Firebase initialization completed")
        return "Firebase initialized"
    
    success, _ = test_step("Initialize Firebase", init_firebase)
    if not success:
        return
    
    # Step 5: Initialize VertexAI
    def init_vertex():
        print("   🤖 Starting VertexAI initialization...")
        vertex_ai_service.initialize()
        print("   🤖 VertexAI initialization completed")
        return "VertexAI initialized"
    
    success, _ = test_step("Initialize VertexAI", init_vertex)
    if not success:
        return
    
    print("\n" + "=" * 50)
    print("✅ SUCCESS: All lifespan startup steps completed successfully")
    print(f"🔥 Firebase initialized: {auth_service.is_initialized}")
    print(f"🤖 VertexAI initialized: {vertex_ai_service.is_initialized()}")

if __name__ == "__main__":
    main() 