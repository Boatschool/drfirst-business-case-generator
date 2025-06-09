#!/bin/bash

# =============================================================================
# Firestore Security Rules Test Runner
# Manages Firebase emulator and runs comprehensive test suite
# =============================================================================

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RULES_FILE="$PROJECT_ROOT/config/firebase/proposed_firestore.rules"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    echo "Firestore Security Rules Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install      Install test dependencies"
    echo "  test         Run all tests with emulator"
    echo "  test:watch   Run tests in watch mode"
    echo "  test:coverage Run tests with coverage report"
    echo "  test:users   Run only users collection tests"
    echo "  test:cases   Run only business cases tests"
    echo "  test:eval    Run only evaluation collections tests"
    echo "  emulator     Start emulator only (for manual testing)"
    echo "  clean        Clean up test artifacts"
    echo ""
    echo "Options:"
    echo "  -h, --help   Show this help message"
    echo "  -v, --verbose Enable verbose output"
    echo "  --keep-alive Keep emulator running after tests"
    echo ""
    echo "Examples:"
    echo "  $0 install               # Install dependencies"
    echo "  $0 test                  # Run all tests"
    echo "  $0 test:coverage         # Run with coverage"
    echo "  $0 test:users            # Test only users collection"
    echo "  $0 emulator              # Start emulator for manual testing"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Firebase CLI is installed
    if ! command -v firebase &> /dev/null; then
        log_error "Firebase CLI is not installed. Please install it first:"
        log_error "npm install -g firebase-tools"
        exit 1
    fi
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Check if rules file exists
    if [[ ! -f "$RULES_FILE" ]]; then
        log_error "Proposed rules file not found: $RULES_FILE"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Install dependencies
install_dependencies() {
    log_info "Installing test dependencies..."
    
    cd "$SCRIPT_DIR"
    
    if [[ ! -f "package.json" ]]; then
        log_error "package.json not found in test directory"
        exit 1
    fi
    
    npm install
    
    log_success "Dependencies installed successfully"
}

# Start Firebase emulator
start_emulator() {
    local background_mode=${1:-false}
    
    log_info "Starting Firebase emulator..."
    
    cd "$PROJECT_ROOT"
    
    # Kill any existing emulator processes
    pkill -f "firebase.*emulators" || true
    sleep 2
    
    # Configure emulator
    export FIRESTORE_EMULATOR_HOST="localhost:8080"
    
    if [[ "$background_mode" == "true" ]]; then
        # Start emulator in background
        firebase emulators:start --only firestore --project demo-project > /dev/null 2>&1 &
        EMULATOR_PID=$!
        
        # Wait for emulator to be ready
        log_info "Waiting for emulator to start..."
        for i in {1..30}; do
            if curl -s http://localhost:8080 > /dev/null 2>&1; then
                log_success "Emulator started successfully (PID: $EMULATOR_PID)"
                return 0
            fi
            sleep 1
        done
        
        log_error "Emulator failed to start within 30 seconds"
        kill $EMULATOR_PID 2>/dev/null || true
        exit 1
    else
        # Start emulator in foreground
        log_info "Starting emulator in foreground mode (Ctrl+C to stop)"
        firebase emulators:start --only firestore --project demo-project
    fi
}

# Stop emulator
stop_emulator() {
    log_info "Stopping Firebase emulator..."
    pkill -f "firebase.*emulators" || true
    sleep 2
    log_success "Emulator stopped"
}

# Run tests
run_tests() {
    local test_pattern=${1:-""}
    local coverage=${2:-false}
    local watch_mode=${3:-false}
    
    cd "$SCRIPT_DIR"
    
    # Set environment variables
    export FIRESTORE_EMULATOR_HOST="localhost:8080"
    
    # Build Jest command
    local jest_cmd="npx jest"
    
    if [[ -n "$test_pattern" ]]; then
        jest_cmd="$jest_cmd --testNamePattern=\"$test_pattern\""
    fi
    
    if [[ "$coverage" == "true" ]]; then
        jest_cmd="$jest_cmd --coverage"
    fi
    
    if [[ "$watch_mode" == "true" ]]; then
        jest_cmd="$jest_cmd --watch"
    fi
    
    # Add verbose flag if set
    if [[ "$VERBOSE" == "true" ]]; then
        jest_cmd="$jest_cmd --verbose"
    fi
    
    log_info "Running tests: $jest_cmd"
    
    # Run tests
    eval $jest_cmd
}

# Run specific test suites
run_users_tests() {
    log_info "Running users collection tests..."
    run_tests "Users Collection Security Rules"
}

run_business_cases_tests() {
    log_info "Running business cases collection tests..."
    run_tests "Business Cases Collection Security Rules"
}

run_evaluation_tests() {
    log_info "Running evaluation collections tests..."
    run_tests "Evaluation Collections Security Rules"
}

# Clean up test artifacts
clean_up() {
    log_info "Cleaning up test artifacts..."
    
    cd "$SCRIPT_DIR"
    
    # Remove coverage directory
    if [[ -d "coverage" ]]; then
        rm -rf coverage
        log_info "Removed coverage directory"
    fi
    
    # Remove node_modules if requested
    if [[ "$1" == "--full" ]]; then
        if [[ -d "node_modules" ]]; then
            rm -rf node_modules
            log_info "Removed node_modules directory"
        fi
    fi
    
    # Stop any running emulators
    stop_emulator
    
    log_success "Cleanup completed"
}

# Validate rules syntax before testing
validate_rules() {
    log_info "Validating rules syntax..."
    
    cd "$PROJECT_ROOT"
    
    if firebase firestore:rules:check --rules="$RULES_FILE" 2>/dev/null; then
        log_success "Rules syntax validation passed"
        return 0
    else
        log_error "Rules syntax validation failed"
        return 1
    fi
}

# Generate test report
generate_report() {
    local coverage_dir="$SCRIPT_DIR/coverage"
    
    if [[ -d "$coverage_dir" ]]; then
        log_info "Test coverage report generated:"
        log_info "  HTML Report: $coverage_dir/lcov-report/index.html"
        log_info "  LCOV File: $coverage_dir/lcov.info"
        
        # Show coverage summary
        if [[ -f "$coverage_dir/coverage-summary.json" ]]; then
            log_info "Coverage Summary:"
            cat "$coverage_dir/coverage-summary.json" | jq '.total' 2>/dev/null || true
        fi
    fi
}

# Main script logic
main() {
    local command=""
    local keep_alive=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --keep-alive)
                keep_alive=true
                shift
                ;;
            install|test|test:watch|test:coverage|test:users|test:cases|test:eval|emulator|clean)
                command=$1
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Show help if no command provided
    if [[ -z "$command" ]]; then
        show_help
        exit 0
    fi
    
    # Check prerequisites for most commands
    if [[ "$command" != "clean" ]]; then
        check_prerequisites
    fi
    
    # Execute the requested command
    case $command in
        install)
            install_dependencies
            ;;
        test)
            validate_rules
            if [[ $? -eq 0 ]]; then
                start_emulator true
                sleep 3
                run_tests "" false false
                if [[ "$keep_alive" == false ]]; then
                    stop_emulator
                fi
            else
                exit 1
            fi
            ;;
        test:watch)
            validate_rules
            if [[ $? -eq 0 ]]; then
                start_emulator true
                sleep 3
                run_tests "" false true
            else
                exit 1
            fi
            ;;
        test:coverage)
            validate_rules
            if [[ $? -eq 0 ]]; then
                start_emulator true
                sleep 3
                run_tests "" true false
                generate_report
                if [[ "$keep_alive" == false ]]; then
                    stop_emulator
                fi
            else
                exit 1
            fi
            ;;
        test:users)
            validate_rules
            if [[ $? -eq 0 ]]; then
                start_emulator true
                sleep 3
                run_users_tests
                if [[ "$keep_alive" == false ]]; then
                    stop_emulator
                fi
            else
                exit 1
            fi
            ;;
        test:cases)
            validate_rules
            if [[ $? -eq 0 ]]; then
                start_emulator true
                sleep 3
                run_business_cases_tests
                if [[ "$keep_alive" == false ]]; then
                    stop_emulator
                fi
            else
                exit 1
            fi
            ;;
        test:eval)
            validate_rules
            if [[ $? -eq 0 ]]; then
                start_emulator true
                sleep 3
                run_evaluation_tests
                if [[ "$keep_alive" == false ]]; then
                    stop_emulator
                fi
            else
                exit 1
            fi
            ;;
        emulator)
            start_emulator false
            ;;
        clean)
            if [[ "$2" == "--full" ]]; then
                clean_up --full
            else
                clean_up
            fi
            ;;
    esac
}

# Cleanup on script exit
trap 'stop_emulator' EXIT

# Run the script
main "$@" 