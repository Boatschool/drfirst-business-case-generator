#!/usr/bin/env python3
"""
Debug Logging Cleanup Script

This script automatically replaces console.log statements in frontend files
and print statements in backend files with proper logging mechanisms.

Usage:
    python scripts/fix_debug_logging.py [--dry-run] [--frontend-only] [--backend-only]
"""

import os
import re
import argparse
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional


class LoggingFixer:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.changes_made = []
        
    def fix_frontend_file(self, file_path: Path) -> bool:
        """Fix console.log statements in a frontend TypeScript/JavaScript file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Check if file already has Logger import
            has_logger_import = 'from ' in content and 'utils/logger' in content
            
            # Find console.log, console.error, console.warn, console.debug statements
            console_patterns = [
                (r'console\.log\s*\(', 'logger.debug('),
                (r'console\.debug\s*\(', 'logger.debug('),
                (r'console\.info\s*\(', 'logger.info('),
                (r'console\.warn\s*\(', 'logger.warn('),
                (r'console\.error\s*\(', 'logger.error('),
            ]
            
            changes_count = 0
            
            # Count total console statements to replace
            total_console_statements = 0
            for pattern, _ in console_patterns:
                total_console_statements += len(re.findall(pattern, content))
            
            if total_console_statements == 0:
                return False
            
            # Add Logger import if not present
            if not has_logger_import:
                # Find the best place to add the import
                import_lines = []
                lines = content.split('\n')
                
                # Find existing imports
                import_section_end = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_section_end = i
                
                # Add the Logger import after existing imports
                if import_section_end > 0:
                    # Determine the correct relative path
                    depth = len(file_path.relative_to(Path('frontend/src')).parts) - 1
                    relative_path = '../' * depth + 'utils/logger'
                    
                    import_line = f"import Logger from '{relative_path}';"
                    lines.insert(import_section_end + 1, import_line)
                    content = '\n'.join(lines)
                    changes_count += 1
            
            # Check if file already has logger instance
            has_logger_instance = ('logger = Logger.create(' in content or 
                                 'const logger = Logger.create(' in content or
                                 'this.logger = Logger.create(' in content)
            
            # Add logger instance if not present
            if not has_logger_instance and total_console_statements > 0:
                lines = content.split('\n')
                
                # Find a good place to add logger instance
                # Look for class definition or after imports
                insert_point = 0
                component_name = file_path.stem
                
                for i, line in enumerate(lines):
                    if 'class ' in line or 'function ' in line or 'const ' in line:
                        insert_point = i
                        break
                    elif line.strip().startswith('export'):
                        insert_point = i
                        break
                
                # Determine if it's a class or functional component
                is_class = any('class ' in line for line in lines)
                
                if is_class:
                    # For class components, add logger as class property
                    for i, line in enumerate(lines):
                        if 'class ' in line:
                            # Find constructor or first method
                            for j in range(i, len(lines)):
                                if 'constructor(' in lines[j] or ('  ' in lines[j] and '{' in lines[j]):
                                    lines.insert(j + 1, f"  private logger = Logger.create('{component_name}');")
                                    break
                            break
                else:
                    # For functional components, add logger constant
                    lines.insert(insert_point, f"const logger = Logger.create('{component_name}');")
                    lines.insert(insert_point + 1, '')
                
                content = '\n'.join(lines)
                changes_count += 1
            
            # Replace console statements
            for pattern, replacement in console_patterns:
                content, count = re.subn(pattern, replacement, content)
                changes_count += count
            
            # Remove emoji and clean up messages
            console_message_patterns = [
                (r"logger\.(debug|info|warn|error)\('🔗\s*([^']+)'", r"logger.\1('\2'"),
                (r"logger\.(debug|info|warn|error)\('🔑\s*([^']+)'", r"logger.\1('\2'"),
                (r"logger\.(debug|info|warn|error)\('🎫\s*([^']+)'", r"logger.\1('\2'"),
                (r"logger\.(debug|info|warn|error)\('✅\s*([^']+)'", r"logger.\1('\2'"),
                (r"logger\.(debug|info|warn|error)\('❌\s*([^']+)'", r"logger.\1('\2'"),
                (r"logger\.(debug|info|warn|error)\('🔄\s*([^']+)'", r"logger.\1('\2'"),
                (r"logger\.(debug|info|warn|error)\('📝\s*([^']+)'", r"logger.\1('\2'"),
                (r"logger\.(debug|info|warn|error)\('🔓\s*([^']+)'", r"logger.\1('\2'"),
                (r"logger\.(debug|info|warn|error)\('🌐\s*([^']+)'", r"logger.\1('\2'"),
                (r"logger\.(debug|info|warn|error)\('👋\s*([^']+)'", r"logger.\1('\2'"),
                (r"logger\.(debug|info|warn|error)\('👂\s*([^']+)'", r"logger.\1('\2'"),
                (r"logger\.(debug|info|warn|error)\('👤\s*([^']+)'", r"logger.\1('\2'"),
                (r"logger\.(debug|info|warn|error)\('🔧\s*([^']+)'", r"logger.\1('\2'"),
                (r"logger\.(debug|info|warn|error)\('📱\s*([^']+)'", r"logger.\1('\2'"),
            ]
            
            for pattern, replacement in console_message_patterns:
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                self.changes_made.append(f"Frontend: {file_path} - {changes_count} changes")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def fix_backend_file(self, file_path: Path) -> bool:
        """Fix print statements in a backend Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Check if file already has logging import
            has_logging_import = 'import logging' in content
            
            # Find print statements
            print_pattern = r'print\s*\('
            print_matches = re.findall(print_pattern, content)
            
            if len(print_matches) == 0:
                return False
            
            changes_count = 0
            
            # Add logging import if not present
            if not has_logging_import:
                lines = content.split('\n')
                
                # Find the best place to add the import
                import_section_end = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_section_end = i
                
                # Add the logging import
                if import_section_end > 0:
                    lines.insert(import_section_end + 1, 'import logging')
                else:
                    # Add at the beginning after docstring
                    for i, line in enumerate(lines):
                        if '"""' in line:
                            # Find end of docstring
                            for j in range(i + 1, len(lines)):
                                if '"""' in lines[j]:
                                    lines.insert(j + 2, 'import logging')
                                    break
                            break
                        elif line.strip() and not line.startswith('#'):
                            lines.insert(i, 'import logging')
                            break
                
                content = '\n'.join(lines)
                changes_count += 1
            
            # Check if file already has logger instance
            has_logger_instance = ('logger = logging.getLogger(' in content or 
                                 'self.logger = logging.getLogger(' in content)
            
            # Add logger instance if not present
            if not has_logger_instance:
                lines = content.split('\n')
                
                # For class-based files, add logger to __init__ method
                is_class_file = any('class ' in line for line in lines)
                
                if is_class_file:
                    # Add to __init__ method
                    for i, line in enumerate(lines):
                        if 'def __init__(self' in line:
                            # Find where to add logger
                            for j in range(i + 1, len(lines)):
                                if lines[j].strip().startswith('self.') and '=' in lines[j]:
                                    lines.insert(j + 1, '        self.logger = logging.getLogger(__name__)')
                                    break
                            break
                else:
                    # For module-level files, add logger after imports
                    for i, line in enumerate(lines):
                        if (line.strip() and 
                            not line.startswith('#') and 
                            not line.startswith('import') and 
                            not line.startswith('from') and
                            not line.startswith('"""')):
                            lines.insert(i, 'logger = logging.getLogger(__name__)')
                            lines.insert(i + 1, '')
                            break
                
                content = '\n'.join(lines)
                changes_count += 1
            
            # Replace print statements with appropriate logging calls
            # Analyze print content to determine appropriate log level
            def determine_log_level(print_content: str) -> str:
                if any(keyword in print_content.lower() for keyword in ['error', '❌', 'failed', 'exception']):
                    return 'error'
                elif any(keyword in print_content.lower() for keyword in ['warning', '⚠️', 'warn']):
                    return 'warning'
                elif any(keyword in print_content.lower() for keyword in ['debug', '🔍']):
                    return 'debug'
                else:
                    return 'info'
            
            # Find and replace print statements
            def replace_print(match):
                nonlocal changes_count
                changes_count += 1
                full_match = match.group(0)
                
                # Extract the print content
                start = match.start()
                paren_count = 0
                end = start
                
                for i in range(start, len(content)):
                    if content[i] == '(':
                        paren_count += 1
                    elif content[i] == ')':
                        paren_count -= 1
                        if paren_count == 0:
                            end = i + 1
                            break
                
                print_statement = content[start:end]
                
                # Extract the arguments
                args_start = print_statement.find('(') + 1
                args_end = print_statement.rfind(')')
                args = print_statement[args_start:args_end]
                
                # Determine log level
                log_level = determine_log_level(args)
                
                # Clean up emojis and format
                args = re.sub(r'[🔗🔑🎫✅❌🔄📝🔓🌐👋👂👤🔧📱⚠️🔍]', '', args)
                args = args.strip()
                
                # Determine logger prefix
                if 'self.logger' in content:
                    logger_prefix = 'self.logger'
                else:
                    logger_prefix = 'logger'
                
                return f"{logger_prefix}.{log_level}({args})"
            
            content = re.sub(print_pattern, replace_print, content)
            
            if content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                self.changes_made.append(f"Backend: {file_path} - {changes_count} changes")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def find_frontend_files(self) -> List[Path]:
        """Find frontend files that need to be processed"""
        frontend_dir = Path('frontend/src')
        if not frontend_dir.exists():
            return []
        
        files = []
        for ext in ['*.ts', '*.tsx', '*.js', '*.jsx']:
            files.extend(frontend_dir.rglob(ext))
        
        # Filter out files that don't need processing
        exclude_patterns = ['node_modules', '.git', 'dist', 'build', '__tests__', '.test.', '.spec.']
        
        filtered_files = []
        for file in files:
            if not any(pattern in str(file) for pattern in exclude_patterns):
                # Check if file has console statements
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if re.search(r'console\.(log|debug|info|warn|error)\s*\(', content):
                        filtered_files.append(file)
                except:
                    continue
        
        return filtered_files
    
    def find_backend_files(self) -> List[Path]:
        """Find backend files that need to be processed"""
        backend_dir = Path('backend/app')
        if not backend_dir.exists():
            return []
        
        files = list(backend_dir.rglob('*.py'))
        
        # Filter out files that don't need processing
        exclude_patterns = ['__pycache__', '.git', '__tests__', '.test.', '.spec.', 'test_']
        
        filtered_files = []
        for file in files:
            if not any(pattern in str(file) for pattern in exclude_patterns):
                # Check if file has print statements
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if re.search(r'print\s*\(', content):
                        filtered_files.append(file)
                except:
                    continue
        
        return filtered_files
    
    def run(self, frontend_only: bool = False, backend_only: bool = False):
        """Run the logging fix process"""
        print("🔧 Debug Logging Cleanup Script")
        print("=" * 50)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
            print()
        
        total_files = 0
        total_changes = 0
        
        if not backend_only:
            print("📁 Processing Frontend Files...")
            frontend_files = self.find_frontend_files()
            print(f"Found {len(frontend_files)} frontend files with console statements")
            
            for file in frontend_files:
                if self.fix_frontend_file(file):
                    total_files += 1
                    print(f"  ✅ Fixed: {file}")
                elif not self.dry_run:
                    print(f"  ⏭️  Skipped: {file}")
        
        if not frontend_only:
            print("\n📁 Processing Backend Files...")
            backend_files = self.find_backend_files()
            print(f"Found {len(backend_files)} backend files with print statements")
            
            for file in backend_files:
                if self.fix_backend_file(file):
                    total_files += 1
                    print(f"  ✅ Fixed: {file}")
                elif not self.dry_run:
                    print(f"  ⏭️  Skipped: {file}")
        
        print(f"\n📊 Summary:")
        print(f"  Files processed: {total_files}")
        print(f"  Total changes: {len(self.changes_made)}")
        
        if self.changes_made:
            print(f"\n📝 Detailed Changes:")
            for change in self.changes_made:
                print(f"  {change}")
        
        if self.dry_run:
            print(f"\n💡 To apply these changes, run without --dry-run flag")


def main():
    parser = argparse.ArgumentParser(description='Fix debug logging statements')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without modifying files')
    parser.add_argument('--frontend-only', action='store_true',
                       help='Only process frontend files')
    parser.add_argument('--backend-only', action='store_true',
                       help='Only process backend files')
    
    args = parser.parse_args()
    
    # Change to project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    fixer = LoggingFixer(dry_run=args.dry_run)
    fixer.run(frontend_only=args.frontend_only, backend_only=args.backend_only)


if __name__ == '__main__':
    main() 