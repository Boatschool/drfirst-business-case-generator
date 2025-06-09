#!/usr/bin/env python3
"""
Script to automatically fix common linting issues in Python files.
"""

import os
import re
import sys
from pathlib import Path


def fix_blank_lines_with_whitespace(content):
    """Remove whitespace from blank lines."""
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        if line.strip() == '':
            fixed_lines.append('')
        else:
            fixed_lines.append(line)
    return '\n'.join(fixed_lines)


def fix_too_many_blank_lines(content):
    """Fix E303 errors by reducing consecutive blank lines."""
    lines = content.split('\n')
    fixed_lines = []
    blank_line_count = 0
    
    for i, line in enumerate(lines):
        if line.strip() == '':
            blank_line_count += 1
            # For E303 errors, allow maximum of 1 consecutive blank line
            # except after class/function definitions where 2 are allowed
            prev_line = lines[i-1].strip() if i > 0 else ''
            
            # Check if previous line was an import statement or similar
            if prev_line.startswith('from ') or prev_line.startswith('import '):
                # After imports, only allow 1 blank line
                if blank_line_count <= 1:
                    fixed_lines.append(line)
            else:
                # Otherwise allow up to 2 blank lines
                if blank_line_count <= 2:
                    fixed_lines.append(line)
        else:
            blank_line_count = 0
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def ensure_newline_at_end(content):
    """Ensure file ends with exactly one newline."""
    content = content.rstrip('\n') + '\n'
    return content


def fix_f_string_without_placeholders(content):
    """Convert f-strings without placeholders to regular strings."""
    # Look for f"..." or f'...' without {} placeholders
    pattern = r'f(["\'])([^"\']*?)\1'
    
    def replacer(match):
        quote = match.group(1)
        string_content = match.group(2)
        if '{' not in string_content and '}' not in string_content:
            return f'{quote}{string_content}{quote}'
        return match.group(0)
    
    return re.sub(pattern, replacer, content)


def fix_file(file_path):
    """Fix common linting issues in a Python file."""
    print(f"Fixing {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Apply fixes
    content = fix_blank_lines_with_whitespace(content)
    content = fix_too_many_blank_lines(content)
    content = ensure_newline_at_end(content)
    content = fix_f_string_without_placeholders(content)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Fixed {file_path}")
    else:
        print(f"  - No changes needed for {file_path}")


def main():
    """Main function to process all Python files in backend/app and backend/tests."""
    backend_dir = Path('backend')
    
    if not backend_dir.exists():
        print("Error: backend directory not found")
        sys.exit(1)
    
    # Find all Python files
    python_files = []
    for directory in ['app', 'tests']:
        dir_path = backend_dir / directory
        if dir_path.exists():
            python_files.extend(dir_path.rglob('*.py'))
    
    print(f"Found {len(python_files)} Python files to process")
    
    for file_path in python_files:
        fix_file(file_path)
    
    print("Done!")


if __name__ == '__main__':
    main() 