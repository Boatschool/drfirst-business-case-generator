#!/usr/bin/env python3
"""
Initialize default agent prompts in Firestore.
Run this script to set up the initial prompts for all agents.
"""

import asyncio
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.prompt_initializer import initialize_default_prompts

async def main():
    """Initialize all default prompts."""
    print("🚀 Initializing default agent prompts...")
    try:
        await initialize_default_prompts()
        print("✅ Prompt initialization complete!")
    except Exception as e:
        print(f"❌ Error initializing prompts: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main()) 