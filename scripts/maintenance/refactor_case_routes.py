#!/usr/bin/env python3
"""
Script to refactor case_routes.py to use dependency injection.
"""

import re

def refactor_case_routes():
    """Refactor the case_routes.py file to use dependency injection."""
    
    # Read the current file
    with open('app/api/v1/case_routes.py', 'r') as f:
        content = f.read()
    
    # 1. Replace firestore.Client() calls
    content = re.sub(
        r'db = firestore\.Client\(project=settings\.firebase_project_id\)',
        '',
        content
    )
    
    # 2. Replace firestore.ArrayUnion with our abstraction
    content = re.sub(
        r'firestore\.ArrayUnion\(([^)]+)\)',
        r'get_array_union(\1)',
        content
    )
    
    # 3. Replace firestore.Increment with our abstraction  
    content = re.sub(
        r'firestore\.Increment\(([^)]+)\)',
        r'get_increment(\1)',
        content
    )
    
    # 4. Add db parameter to function signatures that don't have it
    # Pattern: async def function_name(...current_user: dict = Depends(get_current_active_user))
    def add_db_param(match):
        function_def = match.group(0)
        # Check if db parameter already exists
        if 'db: DatabaseClient' in function_def:
            return function_def
        
        # Add db parameter before the closing parenthesis
        if 'current_user: dict = Depends(get_current_active_user)' in function_def:
            return function_def.replace(
                'current_user: dict = Depends(get_current_active_user)',
                'current_user: dict = Depends(get_current_active_user),\n    db: DatabaseClient = Depends(get_db)'
            )
        elif 'current_user: dict = Depends(lambda: require_dynamic_final_approver_role()())' in function_def:
            return function_def.replace(
                'current_user: dict = Depends(lambda: require_dynamic_final_approver_role()())',
                'current_user: dict = Depends(lambda: require_dynamic_final_approver_role()()),\n    db: DatabaseClient = Depends(get_db)'
            )
        return function_def
    
    # Apply the db parameter addition
    content = re.sub(
        r'async def [^(]+\([^)]*current_user: dict = Depends\([^)]+\)[^)]*\):',
        add_db_param,
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # 5. Import get_increment as well
    content = content.replace(
        'from app.core.dependencies import get_db, get_array_union',
        'from app.core.dependencies import get_db, get_array_union, get_increment'
    )
    
    # Write the refactored content
    with open('app/api/v1/case_routes.py', 'w') as f:
        f.write(content)
    
    print("Successfully refactored case_routes.py")

if __name__ == '__main__':
    refactor_case_routes() 