#!/usr/bin/env python3
"""
Admin Role Assignment Script

Assigns the ADMIN role to a user by email address.
"""

import asyncio
import sys
from set_user_role import set_user_role

async def main():
    if len(sys.argv) != 2:
        print("Usage: python set_admin_role.py <email>")
        sys.exit(1)
        
    email = sys.argv[1]
    success = await set_user_role(email, "ADMIN")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 