#!/bin/bash

# DrFirst Business Case Generator - E2E Test Runner
# This script sets up the environment and runs the E2E workflow test

set -e

echo "🎯 DrFirst Business Case Generator - E2E Test Runner"
echo "=" * 60

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.7"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if requirements are installed
echo "🔍 Checking dependencies..."
if ! python3 -c "import requests, httpx" &> /dev/null; then
    echo "📦 Installing requirements..."
    pip3 install -r requirements_e2e.txt
else
    echo "✅ Dependencies already installed"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Set default environment variables if not set
export E2E_API_BASE_URL=${E2E_API_BASE_URL:-"http://localhost:8000"}
export E2E_FIREBASE_API_KEY=${E2E_FIREBASE_API_KEY:-"AIzaSyBSsGH6ihs8GINwee8fBRGI84P3LqbVQ4w"}

echo "🔧 Configuration:"
echo "   API URL: $E2E_API_BASE_URL"
echo "   Firebase Project: drfirst-business-case-gen"

# Check if backend is accessible
echo "🔌 Checking backend connectivity..."
if curl -s --max-time 10 "$E2E_API_BASE_URL/health" > /dev/null; then
    echo "✅ Backend is accessible"
else
    echo "⚠️  Warning: Backend may not be accessible at $E2E_API_BASE_URL"
    echo "   Make sure the backend is running before proceeding."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run the E2E test
echo "🚀 Starting E2E workflow test..."
echo "📋 Test will create a business case and verify complete workflow"
echo "⏱️  Estimated duration: 3-5 minutes"
echo ""

# Run with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
echo "🕐 Test started at: $(date)"

if python3 workflow_e2e_tester.py; then
    echo ""
    echo "🎉 E2E test completed successfully!"
    echo "📄 Check the logs/ directory for detailed reports"
else
    echo ""
    echo "❌ E2E test failed!"
    echo "📄 Check the logs/ directory for error details"
    exit 1
fi

echo "🕐 Test completed at: $(date)" 