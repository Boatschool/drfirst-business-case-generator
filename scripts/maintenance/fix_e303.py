#!/usr/bin/env python3
"""
Script to fix E303 errors (too many blank lines) in case_routes.py
"""

import re

def fix_e303_errors(file_path):
    """Fix E303 errors in the specified file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match import statements followed by two blank lines
    pattern = r'(from app\.agents\.orchestrator_agent import BusinessCaseStatus)\n\n\n'
    replacement = r'\1\n\n'
    
    content = re.sub(pattern, replacement, content)
    
    # More general pattern for any import followed by too many blank lines
    # This matches import statements followed by 3 or more newlines and replaces with just 2
    pattern2 = r'(import [^\n]+)\n\n\n+'
    replacement2 = r'\1\n\n'
    content = re.sub(pattern2, replacement2, content)
    
    # Pattern for from imports followed by too many blank lines
    pattern3 = r'(from [^\n]+ import [^\n]+)\n\n\n+'
    replacement3 = r'\1\n\n'
    content = re.sub(pattern3, replacement3, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed E303 errors in {file_path}")
        return True
    else:
        print(f"No E303 errors found in {file_path}")
        return False

if __name__ == '__main__':
    fix_e303_errors('backend/app/api/v1/case_routes.py') 