#!/bin/bash
# HITL Financial Estimates Test Runner
# Runs comprehensive tests for the HITL functionality

set -e  # Exit on any error

echo "🚀 HITL Financial Estimates Test Suite"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:3000"}
AUTH_TOKEN=${AUTH_TOKEN:-""}

echo "📋 Configuration:"
echo "   Backend URL: $BACKEND_URL"
echo "   Frontend URL: $FRONTEND_URL"
echo "   Auth Token: ${AUTH_TOKEN:+[SET]}${AUTH_TOKEN:-[NOT SET]}"
echo ""

# Function to check if service is running
check_service() {
    local url=$1
    local name=$2
    
    echo -n "🔍 Checking $name..."
    if curl -s --connect-timeout 5 "$url/health" >/dev/null 2>&1 || curl -s --connect-timeout 5 "$url" >/dev/null 2>&1; then
        echo -e " ${GREEN}✅ Running${NC}"
        return 0
    else
        echo -e " ${RED}❌ Not accessible${NC}"
        return 1
    fi
}

# Function to run backend tests
run_backend_tests() {
    echo ""
    echo "🔧 Running Backend API Tests..."
    echo "─────────────────────────────────"
    
    if [ ! -f "test_hitl_financial_estimates.py" ]; then
        echo -e "${RED}❌ test_hitl_financial_estimates.py not found${NC}"
        return 1
    fi
    
    # Check if requests module is available
    if ! python3 -c "import requests" 2>/dev/null; then
        echo "📦 Installing required Python dependencies..."
        pip3 install requests
    fi
    
    # Run the automated tests
    if [ -n "$AUTH_TOKEN" ]; then
        python3 test_hitl_financial_estimates.py --base-url "$BACKEND_URL" --auth-token "$AUTH_TOKEN"
    else
        python3 test_hitl_financial_estimates.py --base-url "$BACKEND_URL"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Backend tests passed${NC}"
        return 0
    else
        echo -e "${RED}❌ Backend tests failed${NC}"
        return 1
    fi
}

# Function to check frontend
check_frontend() {
    echo ""
    echo "🌐 Frontend Accessibility Check..."
    echo "─────────────────────────────────"
    
    if check_service "$FRONTEND_URL" "Frontend"; then
        echo -e "${GREEN}✅ Frontend is accessible${NC}"
        echo -e "${YELLOW}📝 Run manual tests using: test_hitl_frontend_manual.md${NC}"
        return 0
    else
        echo -e "${RED}❌ Frontend is not accessible${NC}"
        echo "   Please start frontend with: cd frontend && npm run dev"
        return 1
    fi
}

# Function to run smoke tests
run_smoke_tests() {
    echo ""
    echo "💨 Running Smoke Tests..."
    echo "─────────────────────────"
    
    # Test basic API endpoints
    echo "🔍 Testing basic API endpoints..."
    
    # Health check
    if curl -s --connect-timeout 10 "$BACKEND_URL/health" >/dev/null 2>&1; then
        echo -e "   Health endpoint: ${GREEN}✅${NC}"
    else
        echo -e "   Health endpoint: ${RED}❌${NC}"
    fi
    
    # Cases endpoint (should require auth)
    response_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$BACKEND_URL/api/v1/cases" 2>/dev/null || echo "000")
    if [ "$response_code" = "401" ] || [ "$response_code" = "200" ]; then
        echo -e "   Cases endpoint: ${GREEN}✅ (${response_code})${NC}"
    else
        echo -e "   Cases endpoint: ${RED}❌ (${response_code})${NC}"
    fi
    
    echo -e "${GREEN}✅ Smoke tests completed${NC}"
}

# Function to show manual test instructions
show_manual_test_instructions() {
    echo ""
    echo "📖 Manual Testing Instructions"
    echo "═══════════════════════════════"
    echo ""
    echo "1. 📄 Follow the detailed guide in: HITL_FINANCIAL_ESTIMATES_TESTING_GUIDE.md"
    echo "2. 🎯 Use the quick manual script: test_hitl_frontend_manual.md"
    echo "3. 🌐 Open your browser to: $FRONTEND_URL"
    echo ""
    echo "Quick Manual Test Steps:"
    echo "   ✅ Create a new business case"
    echo "   ✅ Wait for financial estimates to generate"
    echo "   ✅ Edit effort estimate and submit for review"
    echo "   ✅ Edit cost estimate and submit for review"
    echo "   ✅ Edit value projection and submit for review"
    echo "   ✅ Verify all changes persist and status updates correctly"
    echo ""
}

# Main execution
main() {
    # Check prerequisites
    echo "🔍 Checking Prerequisites..."
    echo "──────────────────────────"
    
    backend_ok=false
    frontend_ok=false
    
    if check_service "$BACKEND_URL" "Backend"; then
        backend_ok=true
    else
        echo "   Please start backend with: cd backend && uvicorn app.main:app --reload"
    fi
    
    if check_service "$FRONTEND_URL" "Frontend"; then
        frontend_ok=true
    fi
    
    echo ""
    
    # Run tests based on what's available
    if [ "$backend_ok" = true ]; then
        run_smoke_tests
        
        echo ""
        echo -e "${YELLOW}Do you want to run automated backend tests? (y/N):${NC}"
        read -r run_backend
        
        if [[ $run_backend =~ ^[Yy]$ ]]; then
            if run_backend_tests; then
                echo -e "${GREEN}🎉 Backend tests completed successfully!${NC}"
            else
                echo -e "${RED}❌ Backend tests failed. Check the output above.${NC}"
                exit 1
            fi
        fi
    else
        echo -e "${RED}❌ Backend not accessible. Cannot run automated tests.${NC}"
    fi
    
    if [ "$frontend_ok" = true ]; then
        check_frontend
    fi
    
    show_manual_test_instructions
    
    echo ""
    echo "📊 Test Summary"
    echo "════════════════"
    echo -e "Backend Status: $([ "$backend_ok" = true ] && echo "${GREEN}✅ Ready${NC}" || echo "${RED}❌ Not Ready${NC}")"
    echo -e "Frontend Status: $([ "$frontend_ok" = true ] && echo "${GREEN}✅ Ready${NC}" || echo "${RED}❌ Not Ready${NC}")"
    echo ""
    
    if [ "$backend_ok" = true ] && [ "$frontend_ok" = true ]; then
        echo -e "${GREEN}🎉 System is ready for HITL Financial Estimates testing!${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Run the manual frontend tests using the guide above"
        echo "2. Test with different user roles and permissions"
        echo "3. Verify all financial estimate workflows"
        echo ""
    else
        echo -e "${YELLOW}⚠️  Please start the missing services and run tests again.${NC}"
        exit 1
    fi
}

# Help function
show_help() {
    echo "HITL Financial Estimates Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  --backend-url URL   Set backend URL (default: http://localhost:8000)"
    echo "  --frontend-url URL  Set frontend URL (default: http://localhost:3000)"
    echo "  --auth-token TOKEN  Set authentication token"
    echo ""
    echo "Environment Variables:"
    echo "  BACKEND_URL         Backend URL"
    echo "  FRONTEND_URL        Frontend URL"
    echo "  AUTH_TOKEN          Authentication token"
    echo ""
    echo "Examples:"
    echo "  $0                                          # Use defaults"
    echo "  $0 --backend-url http://localhost:8080     # Custom backend URL"
    echo "  AUTH_TOKEN=abc123 $0                       # With auth token"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --backend-url)
            BACKEND_URL="$2"
            shift 2
            ;;
        --frontend-url)
            FRONTEND_URL="$2"
            shift 2
            ;;
        --auth-token)
            AUTH_TOKEN="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main 