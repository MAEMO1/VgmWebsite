#!/bin/bash
# VGM Website - Complete Deployment Script
# This script handles the full deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="vgm-website"
FRONTEND_DIR="frontend"
BACKEND_DIR="."
VERCEL_PROJECT_ID="frontend"
RAILWAY_PROJECT_ID="vgm-website-production"

# Logging functions
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if required tools are installed
    local tools=("node" "npm" "python3" "git")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "Required tool $tool is not installed"
            exit 1
        fi
    done
    
    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        warning "Vercel CLI not found, installing..."
        npm install -g vercel@latest
    fi
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        warning "Railway CLI not found, installing..."
        npm install -g @railway/cli
    fi
    
    log "Prerequisites check completed"
}

# Build frontend
build_frontend() {
    log "Building frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies
    npm ci
    
    # Run linting
    npm run lint
    
    # Run type checking
    npm run type-check
    
    # Build
    npm run build
    
    cd ..
    
    log "Frontend build completed"
}

# Deploy frontend to Vercel
deploy_frontend() {
    log "Deploying frontend to Vercel..."
    
    cd "$FRONTEND_DIR"
    
    # Deploy to Vercel
    vercel --prod --yes
    
    cd ..
    
    log "Frontend deployment completed"
}

# Deploy backend to Railway
deploy_backend() {
    log "Deploying backend to Railway..."
    
    # Login to Railway (requires manual token)
    if [[ -z "$RAILWAY_TOKEN" ]]; then
        warning "RAILWAY_TOKEN not set, please login manually:"
        railway login
    else
        railway login --token "$RAILWAY_TOKEN"
    fi
    
    # Deploy to Railway
    railway up --service backend
    
    log "Backend deployment completed"
}

# Run health checks
health_check() {
    log "Running health checks..."
    
    # Check frontend
    info "Checking frontend health..."
    if curl -f -s https://frontend-maemo.vercel.app > /dev/null; then
        log "Frontend health check passed"
    else
        error "Frontend health check failed"
        return 1
    fi
    
    # Check backend
    info "Checking backend health..."
    if curl -f -s https://vgm-website-production.up.railway.app/health > /dev/null; then
        log "Backend health check passed"
    else
        warning "Backend health check failed (may not be deployed yet)"
    fi
    
    log "Health checks completed"
}

# Update monitoring dashboard
update_monitoring() {
    log "Updating monitoring dashboard..."
    
    # Create a simple status file
    cat > deployment-status.json << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "frontend": {
        "status": "deployed",
        "url": "https://frontend-maemo.vercel.app",
        "last_deploy": "$(date)"
    },
    "backend": {
        "status": "configured",
        "url": "https://vgm-website-production.up.railway.app",
        "last_deploy": "$(date)"
    },
    "domain": {
        "status": "pending",
        "url": "vgm-gent.be",
        "action_required": "domain_registration"
    }
}
EOF
    
    log "Monitoring dashboard updated"
}

# Main deployment function
main() {
    local environment="${1:-production}"
    
    log "Starting VGM Website deployment to $environment"
    echo "=========================================="
    
    check_prerequisites
    build_frontend
    deploy_frontend
    
    if [[ "$environment" == "production" ]]; then
        deploy_backend
    fi
    
    health_check
    update_monitoring
    
    echo "=========================================="
    log "Deployment completed successfully!"
    
    # Show deployment URLs
    info "Deployment URLs:"
    echo "  Frontend: https://frontend-maemo.vercel.app"
    echo "  Backend: https://vgm-website-production.up.railway.app"
    echo "  Monitoring: file://$(pwd)/monitoring-dashboard.html"
}

# Handle command line arguments
case "${1:-production}" in
    production)
        main "production"
        ;;
    staging)
        main "staging"
        ;;
    frontend-only)
        check_prerequisites
        build_frontend
        deploy_frontend
        health_check
        ;;
    health)
        health_check
        ;;
    *)
        echo "Usage: $0 {production|staging|frontend-only|health}"
        echo ""
        echo "Commands:"
        echo "  production    - Full deployment to production"
        echo "  staging       - Deploy to staging environment"
        echo "  frontend-only - Deploy only frontend"
        echo "  health        - Run health checks only"
        exit 1
        ;;
esac
