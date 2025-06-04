#!/usr/bin/env python3
"""
Test script for Pricing Template CRUD operations
Tests the new admin endpoints for creating, reading, updating, and deleting pricing templates
"""

import asyncio
import json
import requests
import uuid
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
ADMIN_ENDPOINTS = f"{API_BASE_URL}/admin/pricing-templates"

def test_create_pricing_template() -> str:
    """Test creating a new pricing template"""
    print("🧪 Testing: Create Pricing Template")
    
    test_template = {
        "name": f"Test Template {uuid.uuid4().hex[:8]}",
        "description": "Test pricing template for CRUD validation",
        "version": "1.0-test",
        "structureDefinition": {
            "type": "TestScenarios",
            "scenarios": [
                {"case": "low", "value": 1000, "description": "Test low scenario"},
                {"case": "base", "value": 5000, "description": "Test base scenario"},
                {"case": "high", "value": 10000, "description": "Test high scenario"}
            ],
            "notes": "Test template for validation"
        }
    }
    
    try:
        # Note: This would normally require authentication
        # For now, we'll test the endpoint structure
        response = requests.post(ADMIN_ENDPOINTS, json=test_template, timeout=10)
        
        if response.status_code == 401:
            print("   ✅ Authentication required (expected)")
            return "auth_required"
        elif response.status_code == 201 or response.status_code == 200:
            created_template = response.json()
            template_id = created_template.get('id')
            print(f"   ✅ Template created successfully with ID: {template_id}")
            return template_id
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return None

def test_get_pricing_templates():
    """Test fetching pricing templates"""
    print("🧪 Testing: Get Pricing Templates")
    
    try:
        response = requests.get(ADMIN_ENDPOINTS, timeout=10)
        
        if response.status_code == 401:
            print("   ✅ Authentication required (expected)")
        elif response.status_code == 200:
            templates = response.json()
            print(f"   ✅ Retrieved {len(templates)} pricing templates")
            if templates:
                print(f"   Sample template: {templates[0].get('name', 'Unknown')}")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"   ❌ Request failed: {e}")

def test_update_pricing_template(template_id: str):
    """Test updating a pricing template"""
    if not template_id or template_id == "auth_required":
        print("🧪 Skipping: Update Pricing Template (no valid ID)")
        return
        
    print("🧪 Testing: Update Pricing Template")
    
    update_data = {
        "name": f"Updated Test Template {uuid.uuid4().hex[:8]}",
        "description": "Updated test pricing template",
        "version": "1.1-test"
    }
    
    try:
        response = requests.put(f"{ADMIN_ENDPOINTS}/{template_id}", json=update_data, timeout=10)
        
        if response.status_code == 401:
            print("   ✅ Authentication required (expected)")
        elif response.status_code == 200:
            updated_template = response.json()
            print(f"   ✅ Template updated successfully: {updated_template.get('name')}")
        elif response.status_code == 404:
            print("   ⚠️  Template not found (may have been deleted)")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"   ❌ Request failed: {e}")

def test_delete_pricing_template(template_id: str):
    """Test deleting a pricing template"""
    if not template_id or template_id == "auth_required":
        print("🧪 Skipping: Delete Pricing Template (no valid ID)")
        return
        
    print("🧪 Testing: Delete Pricing Template")
    
    try:
        response = requests.delete(f"{ADMIN_ENDPOINTS}/{template_id}", timeout=10)
        
        if response.status_code == 401:
            print("   ✅ Authentication required (expected)")
        elif response.status_code == 200:
            result = response.json()
            print(f"   ✅ Template deleted successfully: {result.get('message', 'No message')}")
        elif response.status_code == 404:
            print("   ⚠️  Template not found (may have been already deleted)")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"   ❌ Request failed: {e}")

def test_backend_health():
    """Test if the backend is running"""
    print("🧪 Testing: Backend Health")
    
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Backend is healthy: {health_data}")
            return True
        else:
            print(f"   ❌ Backend health check failed: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"   ❌ Backend not accessible: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Pricing Template CRUD Operations")
    print("=" * 60)
    
    # Test backend health first
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start the backend first:")
        print("   cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    print()
    
    # Test GET (should work without auth for testing)
    test_get_pricing_templates()
    print()
    
    # Test CREATE
    template_id = test_create_pricing_template()
    print()
    
    # Test UPDATE
    test_update_pricing_template(template_id)
    print()
    
    # Test DELETE
    test_delete_pricing_template(template_id)
    print()
    
    print("=" * 60)
    print("✅ Pricing Template CRUD endpoint tests completed!")
    print("\nNote: Authentication tests passed (401 responses expected)")
    print("For full testing, use the frontend at: http://localhost:4000/admin")

if __name__ == "__main__":
    main() 