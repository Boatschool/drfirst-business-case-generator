#!/bin/bash

# DrFirst Backend Convenience Startup Script
# This script automatically detects the correct directory and starts the backend server
# It can be run from anywhere in the project structure

echo "🚀 DrFirst Backend - Smart Directory Detection & Startup"
echo "========================================================="

# Function to find the project root directory
find_project_root() {
    local current_dir="$(pwd)"
    local search_dir="$current_dir"
    
    # Look for key project indicators going up the directory tree
    while [ "$search_dir" != "/" ]; do
        if [ -f "$search_dir/firebase.json" ] && [ -d "$search_dir/backend" ] && [ -d "$search_dir/frontend" ]; then
            echo "$search_dir"
            return 0
        fi
        search_dir="$(dirname "$search_dir")"
    done
    
    return 1
}

# Function to validate project structure
validate_project_structure() {
    local project_root="$1"
    
    echo "🔍 Validating project structure..."
    
    # Check for required directories
    local required_dirs=("backend" "frontend" "scripts" "docs")
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$project_root/$dir" ]; then
            echo "❌ Missing required directory: $dir"
            return 1
        fi
        echo "   ✅ Found: $dir/"
    done
    
    # Check for required files
    local required_files=("backend/app/main.py" "backend/start_server_fixed.sh" "firebase.json")
    for file in "${required_files[@]}"; do
        if [ ! -f "$project_root/$file" ]; then
            echo "❌ Missing required file: $file"
            return 1
        fi
        echo "   ✅ Found: $file"
    done
    
    return 0
}

# Function to check backend directory structure
validate_backend_structure() {
    local backend_dir="$1/backend"
    
    echo "🔍 Validating backend structure..."
    
    # Check for critical backend files and directories
    local backend_items=(
        "app/main.py"
        "app/__init__.py"
        "app/services"
        "app/api"
        "app/core"
        "requirements.txt"
    )
    
    for item in "${backend_items[@]}"; do
        if [ ! -e "$backend_dir/$item" ]; then
            echo "❌ Missing backend component: $item"
            return 1
        fi
        echo "   ✅ Found: backend/$item"
    done
    
    return 0
}

# Main execution starts here
echo "📍 Current directory: $(pwd)"
echo "🔍 Searching for project root directory..."

# Find the project root
PROJECT_ROOT=$(find_project_root)
if [ $? -ne 0 ] || [ -z "$PROJECT_ROOT" ]; then
    echo ""
    echo "❌ ERROR: Could not locate DrFirst project root directory!"
    echo ""
    echo "💡 This script expects to be run from within the DrFirst project structure."
    echo "   The project root should contain:"
    echo "   - backend/ directory"
    echo "   - frontend/ directory" 
    echo "   - firebase.json file"
    echo "   - scripts/ directory"
    echo ""
    echo "📂 Current directory contents:"
    ls -la
    echo ""
    echo "🔧 Possible solutions:"
    echo "   1. Navigate to the project root directory first"
    echo "   2. Ensure you're in the correct project"
    echo "   3. Check if the project structure is intact"
    exit 1
fi

echo "✅ Found project root: $PROJECT_ROOT"

# Validate project structure
if ! validate_project_structure "$PROJECT_ROOT"; then
    echo ""
    echo "❌ ERROR: Invalid project structure detected!"
    echo "💡 Some required files or directories are missing."
    echo "🔧 Please ensure the project is properly set up."
    exit 1
fi

# Validate backend structure
if ! validate_backend_structure "$PROJECT_ROOT"; then
    echo ""
    echo "❌ ERROR: Invalid backend structure detected!"
    echo "💡 Some required backend files or directories are missing."
    echo "🔧 Please ensure the backend is properly set up."
    exit 1
fi

echo "✅ Project structure validation passed!"

# Check if the backend startup script exists and is executable
BACKEND_SCRIPT="$PROJECT_ROOT/backend/start_server_fixed.sh"
if [ ! -f "$BACKEND_SCRIPT" ]; then
    echo "❌ Error: Backend startup script not found at '$BACKEND_SCRIPT'"
    exit 1
fi

# Make sure the script is executable
chmod +x "$BACKEND_SCRIPT"

echo ""
echo "📁 Project root: $PROJECT_ROOT"
echo "🎯 Backend directory: $PROJECT_ROOT/backend"
echo "🚀 Startup script: $BACKEND_SCRIPT"
echo ""
echo "🔄 Delegating to backend startup script..."
echo "========================================================="
echo ""

# Navigate to backend directory and run the startup script
cd "$PROJECT_ROOT/backend" || {
    echo "❌ Failed to navigate to backend directory"
    exit 1
}

# Verify we're in the right place before starting
if [ ! -f "app/main.py" ]; then
    echo "❌ ERROR: Not in the correct backend directory!"
    echo "📁 Current directory: $(pwd)"
    echo "💡 Expected to find app/main.py here"
    exit 1
fi

echo "✅ Successfully navigated to backend directory: $(pwd)"
echo "🚀 Starting backend server..."
echo ""

# Execute the backend startup script
exec ./start_server_fixed.sh 