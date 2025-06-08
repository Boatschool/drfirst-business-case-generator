#!/usr/bin/env python3
"""
Debug script to identify where the backend server startup is hanging.
"""

import sys
import time
import traceback

def debug_import(module_name, description):
    """Debug import with timing and error handling"""
    print(f"🔍 Testing import: {module_name} - {description}")
    start_time = time.time()
    
    try:
        if module_name == "app.core.logging_config":
            from app.core.logging_config import setup_logging
            setup_logging()
        elif module_name == "app.auth.firebase_auth":
            from app.auth.firebase_auth import get_current_active_user
        elif module_name == "app.services.auth_service":
            from app.services.auth_service import get_auth_service
            auth_service = get_auth_service()
        elif module_name == "app.services.vertex_ai_service":
            from app.services.vertex_ai_service import vertex_ai_service
        elif module_name == "app.agents.orchestrator_agent":
            from app.agents.orchestrator_agent import OrchestratorAgent
        elif module_name == "app.api.v1.agent_routes":
            from app.api.v1.agent_routes import router
        elif module_name == "app.main":
            from app.main import app
        else:
            __import__(module_name)
        
        duration = time.time() - start_time
        print(f"✅ {module_name}: {duration:.3f}s")
        return True
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ {module_name}: FAILED after {duration:.3f}s")
        print(f"   Error: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def main():
    print("🚀 Backend Startup Debug Test")
    print("=" * 50)
    
    # Test imports in order of dependency
    imports_to_test = [
        ("app.core.logging_config", "Logging configuration"),
        ("app.core.config", "App configuration"),
        ("app.services.auth_service", "Firebase Auth Service"),
        ("app.services.vertex_ai_service", "VertexAI Service"),
        ("app.agents.orchestrator_agent", "Orchestrator Agent"),
        ("app.api.v1.agent_routes", "Agent Routes"),
        ("app.main", "Main FastAPI app"),
    ]
    
    failed_imports = []
    
    for module_name, description in imports_to_test:
        if not debug_import(module_name, description):
            failed_imports.append(module_name)
            break  # Stop on first failure
    
    print("\n" + "=" * 50)
    if failed_imports:
        print(f"❌ FAILED: {len(failed_imports)} imports failed")
        for module in failed_imports:
            print(f"   - {module}")
    else:
        print("✅ SUCCESS: All imports completed successfully")
        
        # Test FastAPI app creation
        print("\n🔍 Testing FastAPI app initialization...")
        try:
            from app.main import app
            print(f"✅ FastAPI app created: {type(app)}")
        except Exception as e:
            print(f"❌ FastAPI app creation failed: {e}")
            print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main() 