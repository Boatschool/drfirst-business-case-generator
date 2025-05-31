#!/bin/bash

# DrFirst Business Case Generator - Development Environment Setup Script
# This script sets up the development environment for the project

set -e  # Exit on any error

echo "🚀 Setting up DrFirst Business Case Generator development environment..."

# Check if required tools are installed
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    fi
}

echo "📋 Checking required tools..."
check_command "node"
check_command "npm"
check_command "python3"
check_command "pip"

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Copy environment template
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "⚠️  Please update the .env file with your actual configuration values"
fi

cd ..

# Setup frontend
echo "⚛️  Setting up React frontend..."
cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Copy environment template
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "⚠️  Please update the .env file with your actual configuration values"
fi

cd ..

# Setup browser extension (optional)
echo "🌐 Setting up browser extension..."
cd browser-extension

if [ -f "package.json" ]; then
    echo "Installing browser extension dependencies..."
    npm install
fi

cd ..

echo "✅ Development environment setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Update the .env files in both frontend/ and backend/ directories"
echo "2. Start the backend: cd backend && source venv/bin/activate && python -m app.main"
echo "3. Start the frontend: cd frontend && npm run dev"
echo "4. Visit http://localhost:4000 to see the application"
echo ""
echo "🔧 Additional setup:"
echo "- Configure Google Cloud credentials for Firebase/Firestore"
echo "- Set up VertexAI access for the AI agents"
echo "- Review the documentation in docs/ directory" 