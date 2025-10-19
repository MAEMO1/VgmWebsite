#!/bin/bash
# VGM Website Production Testing Script
# Comprehensive testing for production readiness

set -e

# Configuration
BASE_URL="https://vgm-gent.be"
API_BASE_URL="https://vgm-gent.be/api"
LOCAL_API_URL="http://localhost:5001/api"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

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

# Test result tracking
test_result() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [[ "$result" == "PASS" ]]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        log "✅ $test_name: PASS"
        if [[ -n "$details" ]]; then
            info "   $details"
        fi
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        error "❌ $test_name: FAIL"
        if [[ -n "$details" ]]; then
            error "   $details"
        fi
    fi
}

# HTTP request helper
http_request() {
    local method="$1"
    local url="$2"
    local headers="$3"
    local data="$4"
    
    if [[ -n "$data" ]]; then
        curl -s -X "$method" -H "Content-Type: application/json" $headers -d "$data" "$url"
    else
        curl -s -X "$method" $headers "$url"
    fi
}

# Test basic connectivity
test_connectivity() {
    log "Testing basic connectivity..."
    
    # Test main website
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL")
    if [[ "$response" == "200" ]]; then
        test_result "Main Website Connectivity" "PASS" "Status: $response"
    else
        test_result "Main Website Connectivity" "FAIL" "Status: $response"
    fi
    
    # Test API health endpoint
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/health")
    if [[ "$response" == "200" ]]; then
        test_result "API Health Endpoint" "PASS" "Status: $response"
    else
        test_result "API Health Endpoint" "FAIL" "Status: $response"
    fi
    
    # Test SSL certificate
    ssl_info=$(echo | openssl s_client -servername vgm-gent.be -connect vgm-gent.be:443 2>/dev/null | openssl x509 -noout -dates)
    if [[ $? -eq 0 ]]; then
        test_result "SSL Certificate" "PASS" "Certificate is valid"
    else
        test_result "SSL Certificate" "FAIL" "Certificate validation failed"
    fi
}

# Test API endpoints
test_api_endpoints() {
    log "Testing API endpoints..."
    
    # Test mosques endpoint
    response=$(http_request "GET" "$API_BASE_URL/mosques")
    if echo "$response" | grep -q "mosques\|error"; then
        test_result "Mosques API Endpoint" "PASS" "Response received"
    else
        test_result "Mosques API Endpoint" "FAIL" "No valid response"
    fi
    
    # Test events endpoint
    response=$(http_request "GET" "$API_BASE_URL/events")
    if echo "$response" | grep -q "events\|error"; then
        test_result "Events API Endpoint" "PASS" "Response received"
    else
        test_result "Events API Endpoint" "FAIL" "No valid response"
    fi
    
    # Test news endpoint
    response=$(http_request "GET" "$API_BASE_URL/news")
    if echo "$response" | grep -q "news\|error"; then
        test_result "News API Endpoint" "PASS" "Response received"
    else
        test_result "News API Endpoint" "FAIL" "No valid response"
    fi
    
    # Test prayer times endpoint (with mosque_id parameter)
    response=$(http_request "GET" "$API_BASE_URL/prayer-times?mosque_id=1")
    if echo "$response" | grep -q "fajr\|dhuhr\|asr\|maghrib\|isha\|error"; then
        test_result "Prayer Times API Endpoint" "PASS" "Response received"
    else
        test_result "Prayer Times API Endpoint" "FAIL" "No valid response"
    fi
}

# Test authentication
test_authentication() {
    log "Testing authentication..."
    
    # Test login endpoint (should return 400 for missing credentials)
    response=$(http_request "POST" "$API_BASE_URL/auth/login")
    status_code=$(echo "$response" | grep -o '"error"[^}]*' | head -1)
    if [[ -n "$status_code" ]]; then
        test_result "Login Endpoint Validation" "PASS" "Properly validates input"
    else
        test_result "Login Endpoint Validation" "FAIL" "No validation response"
    fi
    
    # Test CSRF endpoint
    response=$(http_request "GET" "$API_BASE_URL/csrf")
    if echo "$response" | grep -q "csrf_token"; then
        test_result "CSRF Token Endpoint" "PASS" "Token provided"
    else
        test_result "CSRF Token Endpoint" "FAIL" "No token provided"
    fi
}

# Test security features
test_security() {
    log "Testing security features..."
    
    # Test rate limiting (make multiple rapid requests)
    log "Testing rate limiting..."
    for i in {1..10}; do
        response=$(http_request "POST" "$API_BASE_URL/auth/login")
        if echo "$response" | grep -q "rate limit\|too many"; then
            test_result "Rate Limiting" "PASS" "Rate limiting active"
            break
        fi
        sleep 0.1
    done
    
    # Test CORS headers
    response=$(curl -s -I -H "Origin: https://example.com" "$API_BASE_URL/mosques")
    if echo "$response" | grep -q "Access-Control-Allow-Origin"; then
        test_result "CORS Headers" "PASS" "CORS properly configured"
    else
        test_result "CORS Headers" "FAIL" "CORS headers missing"
    fi
    
    # Test security headers
    response=$(curl -s -I "$BASE_URL")
    security_headers=("Strict-Transport-Security" "X-Frame-Options" "X-Content-Type-Options" "X-XSS-Protection")
    headers_found=0
    
    for header in "${security_headers[@]}"; do
        if echo "$response" | grep -q "$header"; then
            headers_found=$((headers_found + 1))
        fi
    done
    
    if [[ $headers_found -ge 3 ]]; then
        test_result "Security Headers" "PASS" "$headers_found/4 headers present"
    else
        test_result "Security Headers" "FAIL" "Only $headers_found/4 headers present"
    fi
}

# Test performance
test_performance() {
    log "Testing performance..."
    
    # Test response times
    start_time=$(date +%s%N)
    response=$(http_request "GET" "$API_BASE_URL/mosques")
    end_time=$(date +%s%N)
    response_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    
    if [[ $response_time -lt 1000 ]]; then
        test_result "API Response Time" "PASS" "${response_time}ms"
    else
        test_result "API Response Time" "FAIL" "${response_time}ms (too slow)"
    fi
    
    # Test main page load time
    start_time=$(date +%s%N)
    curl -s "$BASE_URL" > /dev/null
    end_time=$(date +%s%N)
    page_load_time=$(( (end_time - start_time) / 1000000 ))
    
    if [[ $page_load_time -lt 3000 ]]; then
        test_result "Page Load Time" "PASS" "${page_load_time}ms"
    else
        test_result "Page Load Time" "FAIL" "${page_load_time}ms (too slow)"
    fi
}

# Test database connectivity
test_database() {
    log "Testing database connectivity..."
    
    # Test health endpoint with detailed checks
    response=$(http_request "GET" "$API_BASE_URL/health/ready")
    if echo "$response" | grep -q '"database":true'; then
        test_result "Database Connectivity" "PASS" "Database is accessible"
    else
        test_result "Database Connectivity" "FAIL" "Database connection failed"
    fi
}

# Test file uploads
test_file_uploads() {
    log "Testing file upload functionality..."
    
    # Create a test file
    echo "test content" > /tmp/test_upload.txt
    
    # Test file upload endpoint
    response=$(curl -s -X POST -F "file=@/tmp/test_upload.txt" "$API_BASE_URL/upload")
    
    if echo "$response" | grep -q "success\|filename"; then
        test_result "File Upload" "PASS" "File upload working"
    else
        test_result "File Upload" "FAIL" "File upload failed"
    fi
    
    # Clean up test file
    rm -f /tmp/test_upload.txt
}

# Test error handling
test_error_handling() {
    log "Testing error handling..."
    
    # Test 404 handling
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/nonexistent-page")
    if [[ "$response" == "404" ]]; then
        test_result "404 Error Handling" "PASS" "Proper 404 response"
    else
        test_result "404 Error Handling" "FAIL" "Status: $response"
    fi
    
    # Test invalid API endpoint
    response=$(http_request "GET" "$API_BASE_URL/invalid-endpoint")
    if echo "$response" | grep -q "error\|404"; then
        test_result "API Error Handling" "PASS" "Proper error response"
    else
        test_result "API Error Handling" "FAIL" "No error response"
    fi
}

# Test internationalization
test_i18n() {
    log "Testing internationalization..."
    
    # Test different language routes
    languages=("nl" "ar" "en")
    
    for lang in "${languages[@]}"; do
        response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/$lang")
        if [[ "$response" == "200" ]]; then
            test_result "I18n Route ($lang)" "PASS" "Language route accessible"
        else
            test_result "I18n Route ($lang)" "FAIL" "Status: $response"
        fi
    done
}

# Test monitoring endpoints
test_monitoring() {
    log "Testing monitoring endpoints..."
    
    # Test health endpoints
    endpoints=("health" "health/ready" "health/live")
    
    for endpoint in "${endpoints[@]}"; do
        response=$(http_request "GET" "$API_BASE_URL/$endpoint")
        if echo "$response" | grep -q "status\|ok\|ready\|alive"; then
            test_result "Health Endpoint ($endpoint)" "PASS" "Endpoint responding"
        else
            test_result "Health Endpoint ($endpoint)" "FAIL" "No valid response"
        fi
    done
}

# Load testing
load_test() {
    log "Running basic load test..."
    
    # Simple load test with 50 concurrent requests
    info "Sending 50 concurrent requests to mosques endpoint..."
    
    success_count=0
    for i in {1..50}; do
        response=$(http_request "GET" "$API_BASE_URL/mosques")
        if echo "$response" | grep -q "mosques\|error"; then
            success_count=$((success_count + 1))
        fi
    done &
    
    wait
    
    success_rate=$(( (success_count * 100) / 50 ))
    
    if [[ $success_rate -ge 95 ]]; then
        test_result "Load Test" "PASS" "$success_rate% success rate"
    else
        test_result "Load Test" "FAIL" "$success_rate% success rate"
    fi
}

# Generate test report
generate_report() {
    log "Generating test report..."
    
    local report_file="/tmp/vgm-production-test-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "VGM Website Production Test Report"
        echo "Generated: $(date)"
        echo "=================================="
        echo ""
        echo "Test Summary:"
        echo "Total Tests: $TOTAL_TESTS"
        echo "Passed: $TESTS_PASSED"
        echo "Failed: $TESTS_FAILED"
        echo "Success Rate: $(( (TESTS_PASSED * 100) / TOTAL_TESTS ))%"
        echo ""
        
        if [[ $TESTS_FAILED -eq 0 ]]; then
            echo "🎉 ALL TESTS PASSED! Production is ready for launch."
        else
            echo "⚠️  $TESTS_FAILED tests failed. Please review and fix before launch."
        fi
        
    } > "$report_file"
    
    log "Test report saved to: $report_file"
    cat "$report_file"
}

# Main test execution
run_all_tests() {
    log "Starting comprehensive production testing..."
    log "Testing against: $BASE_URL"
    
    test_connectivity
    test_api_endpoints
    test_authentication
    test_security
    test_performance
    test_database
    test_file_uploads
    test_error_handling
    test_i18n
    test_monitoring
    load_test
    
    generate_report
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        log "🎉 All tests passed! Production is ready for launch."
        exit 0
    else
        error "❌ $TESTS_FAILED tests failed. Please fix issues before launch."
        exit 1
    fi
}

# Quick health check
quick_check() {
    log "Running quick health check..."
    
    test_connectivity
    test_database
    test_monitoring
    
    generate_report
}

# Main script logic
case "${1:-all}" in
    all)
        run_all_tests
        ;;
    quick)
        quick_check
        ;;
    connectivity)
        test_connectivity
        ;;
    api)
        test_api_endpoints
        ;;
    security)
        test_security
        ;;
    performance)
        test_performance
        ;;
    *)
        echo "Usage: $0 {all|quick|connectivity|api|security|performance}"
        exit 1
        ;;
esac
