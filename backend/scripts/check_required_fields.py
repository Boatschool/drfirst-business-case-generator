#!/usr/bin/env python3
"""
Script to validate that API models have all required fields.
This prevents issues like missing user_id in BusinessCaseSummary.
"""

import ast
import sys
import os
from typing import List, Dict, Set
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ModelFieldChecker(ast.NodeVisitor):
    """AST visitor to check Pydantic model fields."""
    
    def __init__(self):
        self.models = {}
        self.current_class = None
        self.errors = []
        
    def visit_ClassDef(self, node):
        """Visit class definitions."""
        # Check if this is a Pydantic model
        is_pydantic_model = False
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == 'BaseModel':
                is_pydantic_model = True
                break
            elif isinstance(base, ast.Attribute) and base.attr == 'BaseModel':
                is_pydantic_model = True
                break
        
        if is_pydantic_model:
            self.current_class = node.name
            self.models[node.name] = {
                'fields': {},
                'annotations': {},
                'line': node.lineno
            }
            
            # Process class body
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    field_name = item.target.id
                    field_type = ast.unparse(item.annotation) if item.annotation else 'Any'
                    has_default = item.value is not None
                    
                    self.models[node.name]['fields'][field_name] = {
                        'type': field_type,
                        'has_default': has_default,
                        'required': not has_default,
                        'line': item.lineno
                    }
                    self.models[node.name]['annotations'][field_name] = field_type
        
        self.generic_visit(node)
        self.current_class = None


def check_business_case_summary_fields():
    """Check that BusinessCaseSummary has all required fields."""
    required_fields = {
        'case_id': 'str',
        'user_id': 'str',  # This was missing!
        'title': 'str',
        'status': 'str',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    }
    
    # Find BusinessCaseSummary model
    models_file = Path('app/api/v1/cases/models.py')
    if not models_file.exists():
        print(f"❌ Models file not found: {models_file}")
        return False
    
    with open(models_file, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    checker = ModelFieldChecker()
    checker.visit(tree)
    
    # Check BusinessCaseSummary
    if 'BusinessCaseSummary' not in checker.models:
        print("❌ BusinessCaseSummary model not found!")
        return False
    
    model = checker.models['BusinessCaseSummary']
    errors = []
    
    for field_name, expected_type in required_fields.items():
        if field_name not in model['fields']:
            errors.append(f"Missing required field: {field_name}")
        elif model['fields'][field_name]['required'] is False:
            errors.append(f"Field {field_name} should be required but has default value")
    
    if errors:
        print(f"❌ BusinessCaseSummary validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ BusinessCaseSummary has all required fields")
    return True


def check_api_response_models():
    """Check all API response models for common issues."""
    api_models_files = [
        'app/api/v1/cases/models.py',
        'app/models/agent_models.py'
    ]
    
    all_valid = True
    
    for file_path in api_models_files:
        if not Path(file_path).exists():
            print(f"⚠️ Model file not found: {file_path}")
            continue
            
        print(f"\n🔍 Checking {file_path}...")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        checker = ModelFieldChecker()
        checker.visit(tree)
        
        for model_name, model_info in checker.models.items():
            print(f"  📋 {model_name}:")
            
            if not model_info['fields']:
                print(f"    ⚠️ No fields found (might be empty model)")
                continue
            
            required_fields = [name for name, info in model_info['fields'].items() if info['required']]
            optional_fields = [name for name, info in model_info['fields'].items() if not info['required']]
            
            print(f"    ✅ Required fields: {', '.join(required_fields) if required_fields else 'None'}")
            print(f"    🔧 Optional fields: {', '.join(optional_fields) if optional_fields else 'None'}")
            
            # Check for common issues
            if 'id' in model_info['fields'] and 'user_id' not in model_info['fields']:
                if 'User' not in model_name:  # Skip user models
                    print(f"    ⚠️ Has 'id' but missing 'user_id' - potential ownership issue")
                    all_valid = False
    
    return all_valid


def main():
    """Main validation function."""
    print("🔍 Checking API model required fields...")
    
    # Change to backend directory
    os.chdir(Path(__file__).parent.parent)
    
    valid = True
    
    # Check specific known issues
    if not check_business_case_summary_fields():
        valid = False
    
    # Check all API models
    if not check_api_response_models():
        valid = False
    
    if valid:
        print("\n✅ All API models passed validation!")
        sys.exit(0)
    else:
        print("\n❌ API model validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 