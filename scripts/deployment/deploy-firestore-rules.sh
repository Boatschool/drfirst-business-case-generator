#!/bin/bash

# =============================================================================
# Firestore Security Rules Deployment Script
# Safe deployment with staging validation and rollback capabilities
# =============================================================================

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RULES_DIR="$PROJECT_ROOT/config/firebase"
CURRENT_RULES="$RULES_DIR/firestore.rules"
PROPOSED_RULES="$RULES_DIR/proposed_firestore.rules"
BACKUP_DIR="$RULES_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

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
    echo "Firestore Security Rules Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  validate     Validate proposed rules syntax"
    echo "  test         Run rules testing suite"
    echo "  staging      Deploy to staging environment"
    echo "  production   Deploy to production (requires staging validation)"
    echo "  rollback     Rollback to previous rules version"
    echo "  status       Show current deployment status"
    echo ""
    echo "Options:"
    echo "  -h, --help   Show this help message"
    echo "  -f, --force  Skip staging validation (not recommended)"
    echo "  -v, --verbose Enable verbose output"
    echo ""
    echo "Examples:"
    echo "  $0 validate              # Validate rules syntax"
    echo "  $0 test                  # Run complete test suite"
    echo "  $0 staging               # Deploy to staging"
    echo "  $0 production            # Deploy to production"
    echo "  $0 rollback              # Rollback to previous version"
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
    
    # Check if user is logged in
    if ! firebase projects:list &> /dev/null; then
        log_error "Not logged in to Firebase. Please run: firebase login"
        exit 1
    fi
    
    # Check if proposed rules file exists
    if [[ ! -f "$PROPOSED_RULES" ]]; then
        log_error "Proposed rules file not found: $PROPOSED_RULES"
        exit 1
    fi
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    log_success "Prerequisites check passed"
}

# Backup current rules
backup_current_rules() {
    log_info "Backing up current rules..."
    
    if [[ -f "$CURRENT_RULES" ]]; then
        cp "$CURRENT_RULES" "$BACKUP_DIR/firestore.rules.backup_$TIMESTAMP"
        log_success "Current rules backed up to: firestore.rules.backup_$TIMESTAMP"
    else
        log_warning "No current rules file found to backup"
    fi
}

# Validate rules syntax
validate_rules() {
    log_info "Validating proposed rules syntax..."
    
    # Copy proposed rules to current rules temporarily for validation
    cp "$PROPOSED_RULES" "$CURRENT_RULES.temp"
    
    # Use Firebase CLI to validate rules
    if firebase firestore:rules:check --rules="$CURRENT_RULES.temp" 2>/dev/null; then
        log_success "Rules syntax validation passed"
        rm "$CURRENT_RULES.temp"
        return 0
    else
        log_error "Rules syntax validation failed"
        rm "$CURRENT_RULES.temp"
        return 1
    fi
}

# Run tests
run_tests() {
    log_info "Running Firestore rules test suite..."
    
    cd "$PROJECT_ROOT"
    
    # Check if test dependencies are installed
    if [[ ! -d "node_modules" ]]; then
        log_info "Installing test dependencies..."
        npm install
    fi
    
    # Run the test suite
    if npm test -- --testPathPattern=firestore-rules; then
        log_success "All tests passed"
        return 0
    else
        log_error "Tests failed"
        return 1
    fi
}

# Deploy to staging
deploy_staging() {
    log_info "Deploying rules to staging environment..."
    
    # Copy proposed rules to current rules
    cp "$PROPOSED_RULES" "$CURRENT_RULES"
    
    # Deploy to staging project
    if firebase deploy --only firestore:rules --project drfirst-business-case-staging; then
        log_success "Successfully deployed to staging"
        
        # Create deployment marker
        echo "$TIMESTAMP" > "$BACKUP_DIR/staging_deployment_$TIMESTAMP"
        
        log_info "Please test the staging environment thoroughly before production deployment"
        log_info "Run integration tests and verify all user workflows"
        
        return 0
    else
        log_error "Staging deployment failed"
        return 1
    fi
}

# Deploy to production
deploy_production() {
    local force_deploy=false
    
    if [[ "$1" == "--force" ]]; then
        force_deploy=true
        log_warning "Force deployment enabled - skipping staging validation"
    fi
    
    # Check if staging deployment exists (unless forced)
    if [[ "$force_deploy" == false ]]; then
        if ! ls "$BACKUP_DIR"/staging_deployment_* 1> /dev/null 2>&1; then
            log_error "No staging deployment found. Please deploy to staging first:"
            log_error "$0 staging"
            exit 1
        fi
        
        # Check if staging deployment is recent (within 7 days)
        latest_staging=$(ls -t "$BACKUP_DIR"/staging_deployment_* | head -n1)
        staging_timestamp=$(basename "$latest_staging" | sed 's/staging_deployment_//')
        
        # Convert timestamp to epoch for comparison
        staging_epoch=$(date -d "${staging_timestamp:0:8} ${staging_timestamp:9:2}:${staging_timestamp:11:2}:${staging_timestamp:13:2}" +%s 2>/dev/null || echo "0")
        current_epoch=$(date +%s)
        age_hours=$(( (current_epoch - staging_epoch) / 3600 ))
        
        if [[ $age_hours -gt 168 ]]; then  # 7 days
            log_warning "Staging deployment is older than 7 days. Consider re-testing:"
            log_warning "Last staging deployment: $staging_timestamp"
            read -p "Continue with production deployment? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Production deployment cancelled"
                exit 0
            fi
        fi
    fi
    
    log_info "Deploying rules to production environment..."
    
    # Final confirmation for production
    if [[ "$force_deploy" == false ]]; then
        log_warning "You are about to deploy Firestore security rules to PRODUCTION"
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Production deployment cancelled"
            exit 0
        fi
    fi
    
    # Deploy to production project
    if firebase deploy --only firestore:rules --project drfirst-business-case-production; then
        log_success "Successfully deployed to production"
        
        # Create production deployment marker
        echo "$TIMESTAMP" > "$BACKUP_DIR/production_deployment_$TIMESTAMP"
        
        log_success "Production deployment completed successfully!"
        log_info "Monitor the application for any access issues"
        log_info "Rollback available with: $0 rollback"
        
        return 0
    else
        log_error "Production deployment failed"
        return 1
    fi
}

# Rollback to previous version
rollback() {
    log_warning "Initiating rollback to previous rules version..."
    
    # Find the most recent backup
    if ! ls "$BACKUP_DIR"/firestore.rules.backup_* 1> /dev/null 2>&1; then
        log_error "No backup files found for rollback"
        exit 1
    fi
    
    latest_backup=$(ls -t "$BACKUP_DIR"/firestore.rules.backup_* | head -n1)
    backup_timestamp=$(basename "$latest_backup" | sed 's/firestore.rules.backup_//')
    
    log_info "Rolling back to: $backup_timestamp"
    
    # Confirm rollback
    read -p "Are you sure you want to rollback? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Rollback cancelled"
        exit 0
    fi
    
    # Copy backup to current rules
    cp "$latest_backup" "$CURRENT_RULES"
    
    # Deploy rollback to production
    if firebase deploy --only firestore:rules --project drfirst-business-case-production; then
        log_success "Rollback completed successfully"
        
        # Create rollback marker
        echo "ROLLBACK_TO_$backup_timestamp" > "$BACKUP_DIR/rollback_$TIMESTAMP"
        
    else
        log_error "Rollback deployment failed"
        return 1
    fi
}

# Show deployment status
show_status() {
    log_info "Firestore Rules Deployment Status"
    echo "=================================="
    
    # Show current rules file info
    if [[ -f "$CURRENT_RULES" ]]; then
        echo "Current rules file: $(ls -la "$CURRENT_RULES" | awk '{print $6 " " $7 " " $8}')"
    else
        echo "Current rules file: NOT FOUND"
    fi
    
    # Show proposed rules file info
    if [[ -f "$PROPOSED_RULES" ]]; then
        echo "Proposed rules file: $(ls -la "$PROPOSED_RULES" | awk '{print $6 " " $7 " " $8}')"
    else
        echo "Proposed rules file: NOT FOUND"
    fi
    
    echo ""
    
    # Show recent deployments
    echo "Recent deployments:"
    if ls "$BACKUP_DIR"/staging_deployment_* 1> /dev/null 2>&1; then
        echo "  Latest staging: $(ls -t "$BACKUP_DIR"/staging_deployment_* | head -n1 | xargs basename | sed 's/staging_deployment_//')"
    else
        echo "  Latest staging: NONE"
    fi
    
    if ls "$BACKUP_DIR"/production_deployment_* 1> /dev/null 2>&1; then
        echo "  Latest production: $(ls -t "$BACKUP_DIR"/production_deployment_* | head -n1 | xargs basename | sed 's/production_deployment_//')"
    else
        echo "  Latest production: NONE"
    fi
    
    # Show available backups
    echo ""
    echo "Available backups:"
    if ls "$BACKUP_DIR"/firestore.rules.backup_* 1> /dev/null 2>&1; then
        ls -t "$BACKUP_DIR"/firestore.rules.backup_* | head -n5 | while read backup; do
            timestamp=$(basename "$backup" | sed 's/firestore.rules.backup_//')
            echo "  $timestamp"
        done
    else
        echo "  No backups found"
    fi
}

# Main script logic
main() {
    local command=""
    local force_flag=false
    local verbose_flag=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -f|--force)
                force_flag=true
                shift
                ;;
            -v|--verbose)
                verbose_flag=true
                shift
                ;;
            validate|test|staging|production|rollback|status)
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
    
    # Enable verbose output if requested
    if [[ "$verbose_flag" == true ]]; then
        set -x
    fi
    
    # Check prerequisites for most commands
    if [[ "$command" != "status" ]]; then
        check_prerequisites
    fi
    
    # Execute the requested command
    case $command in
        validate)
            validate_rules
            ;;
        test)
            run_tests
            ;;
        staging)
            backup_current_rules
            validate_rules
            if [[ $? -eq 0 ]]; then
                deploy_staging
            else
                log_error "Validation failed, aborting staging deployment"
                exit 1
            fi
            ;;
        production)
            backup_current_rules
            validate_rules
            if [[ $? -eq 0 ]]; then
                if [[ "$force_flag" == true ]]; then
                    deploy_production --force
                else
                    deploy_production
                fi
            else
                log_error "Validation failed, aborting production deployment"
                exit 1
            fi
            ;;
        rollback)
            rollback
            ;;
        status)
            show_status
            ;;
    esac
}

# Run the script
main "$@" 