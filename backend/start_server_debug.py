#!/usr/bin/env python3
"""
Debug server starter to capture startup errors
"""

import os
import sys
import asyncio
import uvicorn
import traceback
from datetime import datetime

# Set up environment
os.environ["PYTHONPATH"] = f"{os.getcwd()}:{os.environ.get('PYTHONPATH', '')}"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/ronwince/.gcp/drfirst-firebase-admin-key.json"

sys.path.insert(0, os.getcwd())

def log_with_timestamp(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def main():
    """Start server with detailed error capture"""
    log_with_timestamp("🚀 Starting DrFirst Backend Server - Debug Mode")
    log_with_timestamp(f"📁 Working directory: {os.getcwd()}")
    log_with_timestamp(f"🔑 GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    try:
        log_with_timestamp("📦 Testing imports...")
        from app.main import app
        log_with_timestamp("✅ Main app imported successfully")
        
        log_with_timestamp("🌐 Starting Uvicorn server...")
        
        # Start server with detailed configuration
        config = uvicorn.Config(
            app="app.main:app",
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=False,
            reload=False,  # Disable reload to avoid process issues
            workers=1
        )
        
        server = uvicorn.Server(config)
        
        log_with_timestamp("🎯 Server configured, starting...")
        server.run()
        
    except KeyboardInterrupt:
        log_with_timestamp("🛑 Server stopped by user")
    except Exception as e:
        log_with_timestamp(f"❌ Server startup failed: {e}")
        log_with_timestamp(f"❌ Error type: {type(e)}")
        traceback.print_exc()
    finally:
        log_with_timestamp("🏁 Server startup attempt completed")

if __name__ == "__main__":
    main() 