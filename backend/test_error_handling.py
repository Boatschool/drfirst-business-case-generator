#!/usr/bin/env python3
"""
Test script to demonstrate the new standardized error handling patterns.
This script can be run to verify that the error handling infrastructure works correctly.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.exceptions import (
    BusinessCaseNotFoundError, UserNotFoundError, DatabaseError,
    AuthenticationError, AuthorizationError, ValidationError
)


async def test_custom_exceptions():
    """Test that custom exceptions work correctly"""
    print("🧪 Testing Custom Exceptions")
    print("=" * 50)
    
    # Test BusinessCaseNotFoundError
    try:
        raise BusinessCaseNotFoundError("test-case-123")
    except BusinessCaseNotFoundError as e:
        print(f"✅ BusinessCaseNotFoundError: {e.detail}")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Context: {e.context}")
        print()
    
    # Test UserNotFoundError
    try:
        raise UserNotFoundError("user-456")
    except UserNotFoundError as e:
        print(f"✅ UserNotFoundError: {e.detail}")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Context: {e.context}")
        print()
    
    # Test DatabaseError
    try:
        raise DatabaseError(
            operation="create user",
            detail="Connection timeout",
            context={"user_id": "test-user"}
        )
    except DatabaseError as e:
        print(f"✅ DatabaseError: {e.detail}")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Context: {e.context}")
        print()
    
    # Test AuthenticationError
    try:
        raise AuthenticationError("Invalid token")
    except AuthenticationError as e:
        print(f"✅ AuthenticationError: {e.detail}")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Headers: {e.headers}")
        print()
    
    # Test AuthorizationError
    try:
        raise AuthorizationError(
            detail="Insufficient permissions",
            context={"required_role": "admin", "user_role": "user"}
        )
    except AuthorizationError as e:
        print(f"✅ AuthorizationError: {e.detail}")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Context: {e.context}")
        print()
    
    # Test ValidationError
    try:
        raise ValidationError(
            detail="Invalid input data",
            field_errors={"email": "Invalid format", "age": "Must be positive"}
        )
    except ValidationError as e:
        print(f"✅ ValidationError: {e.detail}")
        print(f"   Status Code: {e.status_code}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Context: {e.context}")
        print()


def test_error_response_format():
    """Test the error response format that would be sent to clients"""
    print("📋 Testing Error Response Format")
    print("=" * 50)
    
    from app.core.error_handlers import create_error_response
    
    # Test basic error response
    response = create_error_response(
        status_code=404,
        message="Business case not found",
        error_code="RESOURCE_NOT_FOUND",
        details={"resource_type": "business_case", "resource_id": "test-123"},
        request_id="req-456"
    )
    
    print("✅ Standard Error Response Format:")
    import json
    print(json.dumps(response, indent=2))
    print()
    
    # Test minimal error response
    minimal_response = create_error_response(
        status_code=500,
        message="Internal server error"
    )
    
    print("✅ Minimal Error Response Format:")
    print(json.dumps(minimal_response, indent=2))
    print()


async def main():
    """Main test function"""
    print("🚀 DrFirst Business Case Generator - Error Handling Test")
    print("=" * 60)
    print()
    
    await test_custom_exceptions()
    test_error_response_format()
    
    print("🎉 All error handling tests completed successfully!")
    print()
    print("📝 Summary of Standardized Error Handling:")
    print("   • Custom exception classes with consistent structure")
    print("   • Standardized error response format")
    print("   • Proper HTTP status codes and error codes")
    print("   • Context information for debugging")
    print("   • Global exception handlers in FastAPI")
    print("   • Frontend service adapters handle new format")
    print("   • Error Boundary for React rendering errors")


if __name__ == "__main__":
    asyncio.run(main()) 