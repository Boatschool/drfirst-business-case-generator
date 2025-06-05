#!/usr/bin/env python3
"""
Test runner script for the PRD update functionality.
Sets up environment and runs comprehensive tests.
"""
import os
import sys
import subprocess
from pathlib import Path


def setup_test_environment():
    """Set up the test environment variables."""
    # Set environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["ENVIRONMENT"] = "test"

    # Mock Firebase settings for testing
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
    os.environ["FIREBASE_PROJECT_ID"] = "test-project"

    print("✅ Test environment configured")


def run_unit_tests():
    """Run unit tests."""
    print("\n🧪 Running Unit Tests...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/",
            "-v",
            "--tb=short",
            "--asyncio-mode=auto",
        ],
        capture_output=True,
        text=True,
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


def run_integration_tests():
    """Run integration tests."""
    print("\n🔗 Running Integration Tests...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/integration/",
            "-v",
            "--tb=short",
            "--asyncio-mode=auto",
        ],
        capture_output=True,
        text=True,
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


def run_all_tests():
    """Run all tests with coverage."""
    print("\n📊 Running All Tests with Coverage...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--asyncio-mode=auto",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
        ],
        capture_output=True,
        text=True,
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


def main():
    """Main test runner function."""
    print("🚀 Starting PRD Update Functionality Test Suite")
    print("=" * 60)

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    # Setup environment
    setup_test_environment()

    # Run tests
    unit_success = run_unit_tests()
    integration_success = run_integration_tests()

    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print(f"   Unit Tests: {'✅ PASSED' if unit_success else '❌ FAILED'}")
    print(
        f"   Integration Tests: {'✅ PASSED' if integration_success else '❌ FAILED'}"
    )

    if unit_success and integration_success:
        print("\n🎉 All tests passed! PRD update functionality is working correctly.")
        # Run coverage test
        coverage_success = run_all_tests()
        if coverage_success:
            print("📊 Coverage report generated in htmlcov/ directory")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
