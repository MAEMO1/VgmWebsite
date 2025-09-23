#!/bin/bash

# VGM Advanced Deployment Script
# Supports staging, production, and canary deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="staging"
CANARY_PERCENTAGE=0
ROLLBACK=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Environment to deploy to (staging|production)"
    echo "  -c, --canary PERCENT     Deploy as canary with percentage (0-100)"
    echo "  -r, --rollback           Rollback to previous version"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -e staging                    # Deploy to staging"
    echo "  $0 -e production                 # Deploy to production"
    echo "  $0 -e production -c 10          # Canary deploy 10% traffic"
    echo "  $0 -e production -r             # Rollback production"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -c|--canary)
            CANARY_PERCENTAGE="$2"
            shift 2
            ;;
        -r|--rollback)
            ROLLBACK=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    print_error "Invalid environment: $ENVIRONMENT. Must be 'staging' or 'production'"
    exit 1
fi

# Validate canary percentage
if [[ $CANARY_PERCENTAGE -lt 0 || $CANARY_PERCENTAGE -gt 100 ]]; then
    print_error "Invalid canary percentage: $CANARY_PERCENTAGE. Must be between 0 and 100"
    exit 1
fi

print_status "Starting VGM deployment..."
print_status "Environment: $ENVIRONMENT"
print_status "Canary percentage: $CANARY_PERCENTAGE%"
print_status "Rollback: $ROLLBACK"

# Set environment-specific variables
if [[ "$ENVIRONMENT" == "staging" ]]; then
    SSH_HOST="$STAGING_HOST"
    SSH_USER="$STAGING_USER"
    SSH_KEY="$STAGING_SSH_KEY"
    SSH_PORT="$STAGING_PORT"
    DEPLOY_PATH="/opt/vgm-staging"
    COMPOSE_FILE="docker-compose.staging.yml"
    HEALTH_URL="$STAGING_HEALTH_URL"
else
    SSH_HOST="$PRODUCTION_HOST"
    SSH_USER="$PRODUCTION_USER"
    SSH_KEY="$PRODUCTION_SSH_KEY"
    SSH_PORT="$PRODUCTION_PORT"
    DEPLOY_PATH="/opt/vgm-production"
    COMPOSE_FILE="docker-compose.yml"
    HEALTH_URL="$PRODUCTION_HEALTH_URL"
fi

# Check if required environment variables are set
if [[ -z "$SSH_HOST" || -z "$SSH_USER" || -z "$SSH_KEY" ]]; then
    print_error "Missing required environment variables for $ENVIRONMENT deployment"
    print_error "Please set: ${ENVIRONMENT^^}_HOST, ${ENVIRONMENT^^}_USER, ${ENVIRONMENT^^}_SSH_KEY"
    exit 1
fi

# Function to execute SSH commands
ssh_exec() {
    ssh -i "$SSH_KEY" -p "$SSH_PORT" "$SSH_USER@$SSH_HOST" "$1"
}

# Function to check health
check_health() {
    local url="$1"
    local max_attempts=30
    local attempt=1
    
    print_status "Checking health at $url..."
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$url/health" > /dev/null; then
            print_success "Health check passed!"
            return 0
        fi
        
        print_warning "Health check attempt $attempt/$max_attempts failed, retrying in 10 seconds..."
        sleep 10
        ((attempt++))
    done
    
    print_error "Health check failed after $max_attempts attempts"
    return 1
}

# Function to deploy
deploy() {
    print_status "Deploying to $ENVIRONMENT..."
    
    # Pull latest code
    print_status "Pulling latest code..."
    ssh_exec "cd $DEPLOY_PATH && git pull origin main"
    
    # Build and deploy
    print_status "Building and deploying..."
    ssh_exec "cd $DEPLOY_PATH && docker-compose -f $COMPOSE_FILE down"
    ssh_exec "cd $DEPLOY_PATH && docker-compose -f $COMPOSE_FILE up -d --build"
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check health
    if check_health "$HEALTH_URL"; then
        print_success "Deployment to $ENVIRONMENT completed successfully!"
    else
        print_error "Deployment failed health check"
        exit 1
    fi
}

# Function to rollback
rollback() {
    print_status "Rolling back $ENVIRONMENT..."
    
    ssh_exec "cd $DEPLOY_PATH && git log --oneline -n 2"
    ssh_exec "cd $DEPLOY_PATH && git reset --hard HEAD~1"
    ssh_exec "cd $DEPLOY_PATH && docker-compose -f $COMPOSE_FILE down"
    ssh_exec "cd $DEPLOY_PATH && docker-compose -f $COMPOSE_FILE up -d --build"
    
    # Wait and check health
    sleep 30
    if check_health "$HEALTH_URL"; then
        print_success "Rollback completed successfully!"
    else
        print_error "Rollback failed health check"
        exit 1
    fi
}

# Main execution
if [[ "$ROLLBACK" == true ]]; then
    rollback
else
    deploy
fi

print_success "Deployment script completed!"
