#!/bin/bash

# VGM Health Monitoring Script
# Monitors the health of all VGM services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STAGING_URL="${STAGING_HEALTH_URL:-http://staging.vgmgent.be}"
PRODUCTION_URL="${PRODUCTION_HEALTH_URL:-http://vgmgent.be}"
VERCEL_URL="${VERCEL_HEALTH_URL:-https://frontend-1421nmv4j-maemo.vercel.app}"

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

# Function to check HTTP endpoint
check_endpoint() {
    local url="$1"
    local name="$2"
    local timeout="${3:-10}"
    
    print_status "Checking $name at $url..."
    
    if curl -f -s --max-time "$timeout" "$url/health" > /dev/null 2>&1; then
        print_success "$name is healthy"
        return 0
    else
        print_error "$name is unhealthy"
        return 1
    fi
}

# Function to check database connection
check_database() {
    local host="$1"
    local name="$2"
    
    print_status "Checking $name database connection..."
    
    if ssh_exec "cd $DEPLOY_PATH && docker-compose exec -T postgres pg_isready -U postgres" > /dev/null 2>&1; then
        print_success "$name database is healthy"
        return 0
    else
        print_error "$name database is unhealthy"
        return 1
    fi
}

# Function to check Redis connection
check_redis() {
    local host="$1"
    local name="$2"
    
    print_status "Checking $name Redis connection..."
    
    if ssh_exec "cd $DEPLOY_PATH && docker-compose exec -T redis redis-cli ping" > /dev/null 2>&1; then
        print_success "$name Redis is healthy"
        return 0
    else
        print_error "$name Redis is unhealthy"
        return 1
    fi
}

# Function to check disk space
check_disk_space() {
    local host="$1"
    local name="$2"
    local threshold="${3:-90}"
    
    print_status "Checking $name disk space..."
    
    local usage=$(ssh_exec "df -h / | awk 'NR==2 {print \$5}' | sed 's/%//'")
    
    if [[ $usage -lt $threshold ]]; then
        print_success "$name disk usage: ${usage}%"
        return 0
    else
        print_warning "$name disk usage: ${usage}% (threshold: ${threshold}%)"
        return 1
    fi
}

# Function to check memory usage
check_memory() {
    local host="$1"
    local name="$2"
    local threshold="${3:-90}"
    
    print_status "Checking $name memory usage..."
    
    local usage=$(ssh_exec "free | awk 'NR==2{printf \"%.0f\", \$3*100/\$2}'")
    
    if [[ $usage -lt $threshold ]]; then
        print_success "$name memory usage: ${usage}%"
        return 0
    else
        print_warning "$name memory usage: ${usage}% (threshold: ${threshold}%)"
        return 1
    fi
}

# Function to check Docker containers
check_containers() {
    local host="$1"
    local name="$2"
    
    print_status "Checking $name Docker containers..."
    
    local unhealthy=$(ssh_exec "cd $DEPLOY_PATH && docker-compose ps --filter 'health=unhealthy' --format 'table {{.Name}}' | wc -l")
    
    if [[ $unhealthy -eq 0 ]]; then
        print_success "$name all containers are healthy"
        return 0
    else
        print_error "$name has $unhealthy unhealthy containers"
        return 1
    fi
}

# Function to send alert (placeholder)
send_alert() {
    local message="$1"
    print_warning "ALERT: $message"
    # Here you could integrate with Slack, Discord, email, etc.
}

# Main health check function
main() {
    local overall_status=0
    
    print_status "Starting VGM health check..."
    echo "=================================="
    
    # Check Vercel frontend
    if ! check_endpoint "$VERCEL_URL" "Vercel Frontend"; then
        send_alert "Vercel frontend is down"
        overall_status=1
    fi
    
    # Check staging environment
    if [[ -n "$STAGING_HOST" ]]; then
        print_status "Checking staging environment..."
        
        if ! check_endpoint "$STAGING_URL" "Staging Backend"; then
            send_alert "Staging backend is down"
            overall_status=1
        fi
        
        if ! check_database "$STAGING_HOST" "Staging"; then
            send_alert "Staging database is down"
            overall_status=1
        fi
        
        if ! check_redis "$STAGING_HOST" "Staging"; then
            send_alert "Staging Redis is down"
            overall_status=1
        fi
        
        if ! check_containers "$STAGING_HOST" "Staging"; then
            send_alert "Staging containers are unhealthy"
            overall_status=1
        fi
        
        check_disk_space "$STAGING_HOST" "Staging"
        check_memory "$STAGING_HOST" "Staging"
    fi
    
    # Check production environment
    if [[ -n "$PRODUCTION_HOST" ]]; then
        print_status "Checking production environment..."
        
        if ! check_endpoint "$PRODUCTION_URL" "Production Backend"; then
            send_alert "Production backend is down"
            overall_status=1
        fi
        
        if ! check_database "$PRODUCTION_HOST" "Production"; then
            send_alert "Production database is down"
            overall_status=1
        fi
        
        if ! check_redis "$PRODUCTION_HOST" "Production"; then
            send_alert "Production Redis is down"
            overall_status=1
        fi
        
        if ! check_containers "$PRODUCTION_HOST" "Production"; then
            send_alert "Production containers are unhealthy"
            overall_status=1
        fi
        
        check_disk_space "$PRODUCTION_HOST" "Production"
        check_memory "$PRODUCTION_HOST" "Production"
    fi
    
    echo "=================================="
    
    if [[ $overall_status -eq 0 ]]; then
        print_success "All systems are healthy!"
    else
        print_error "Some systems are unhealthy!"
        exit 1
    fi
}

# Run main function
main "$@"
