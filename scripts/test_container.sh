#!/bin/bash
# Container integration test script
# Validates Docker setup is working properly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:8501"
MAX_WAIT_SECONDS=60
POLL_INTERVAL=2

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0

print_header() {
    echo ""
    echo "============================================"
    echo "$1"
    echo "============================================"
}

print_success() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

print_failure() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

print_warning() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
}

print_info() {
    echo -e "  ℹ $1"
}

# Check if Docker is installed and running
check_docker() {
    print_header "Checking Docker Prerequisites"
    
    if ! command -v docker &> /dev/null; then
        print_failure "Docker is not installed"
        exit 1
    fi
    print_success "Docker is installed"
    
    if ! docker info > /dev/null 2>&1; then
        print_failure "Docker daemon is not running"
        exit 1
    fi
    print_success "Docker daemon is running"
    
    if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
        print_failure "Docker Compose is not available"
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Check for .env file
check_env_file() {
    print_header "Checking Environment Configuration"
    
    if [ ! -f .env ]; then
        print_warning ".env file not found"
        if [ -f .env.example ]; then
            print_info "Copy .env.example to .env and fill in your API keys"
        else
            print_info "Create .env with OPENAI_API_KEY and OPENROUTER_API_KEY"
        fi
        print_info "Continuing without .env (containers may fail without API keys)"
    else
        print_success ".env file exists"
        
        # Check for required variables (without exposing values)
        if grep -q "OPENAI_API_KEY=" .env && ! grep -q "OPENAI_API_KEY=$" .env; then
            print_success "OPENAI_API_KEY is set"
        else
            print_warning "OPENAI_API_KEY may not be set"
        fi
        
        if grep -q "OPENROUTER_API_KEY=" .env && ! grep -q "OPENROUTER_API_KEY=$" .env; then
            print_success "OPENROUTER_API_KEY is set"
        else
            print_warning "OPENROUTER_API_KEY may not be set"
        fi
    fi
}

# Build Docker images
build_images() {
    print_header "Building Docker Images"
    
    if docker compose build; then
        print_success "Docker images built successfully"
    else
        print_failure "Docker build failed"
        exit 1
    fi
}

# Start containers
start_containers() {
    print_header "Starting Containers"
    
    # Stop any existing containers first (force remove to handle conflicts)
    docker compose down --remove-orphans 2>/dev/null || true
    docker rm -f ai-interviewer-backend ai-interviewer-frontend 2>/dev/null || true
    
    if docker compose up -d; then
        print_success "Containers started"
    else
        print_failure "Failed to start containers"
        exit 1
    fi
}

# Wait for a service to become healthy
wait_for_health() {
    local url=$1
    local service_name=$2
    local elapsed=0
    
    print_info "Waiting for $service_name to become healthy..."
    
    while [ $elapsed -lt $MAX_WAIT_SECONDS ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            return 0
        fi
        sleep $POLL_INTERVAL
        elapsed=$((elapsed + POLL_INTERVAL))
        echo -n "."
    done
    echo ""
    return 1
}

# Test backend health
test_backend_health() {
    print_header "Testing Backend Health"
    
    if wait_for_health "$BACKEND_URL/health" "Backend"; then
        print_success "Backend is healthy"
        
        # Verify response content
        local response=$(curl -s "$BACKEND_URL/health")
        if echo "$response" | grep -q '"status":"healthy"'; then
            print_success "Backend health response is correct"
        else
            print_failure "Backend health response unexpected: $response"
        fi
    else
        print_failure "Backend failed to become healthy within ${MAX_WAIT_SECONDS}s"
        print_info "Backend logs:"
        docker compose logs backend --tail=50
    fi
}

# Test frontend health
test_frontend_health() {
    print_header "Testing Frontend Health"
    
    if wait_for_health "$FRONTEND_URL/_stcore/health" "Frontend"; then
        print_success "Frontend is healthy"
    else
        print_failure "Frontend failed to become healthy within ${MAX_WAIT_SECONDS}s"
        print_info "Frontend logs:"
        docker compose logs frontend --tail=50
    fi
}

# Test API root endpoint
test_api_root() {
    print_header "Testing API Root Endpoint"
    
    local response=$(curl -s "$BACKEND_URL/")
    if echo "$response" | grep -q '"message":"AI Interviewer Platform API"'; then
        print_success "API root endpoint returns correct message"
    else
        print_failure "API root endpoint unexpected response: $response"
    fi
}

# Test inter-service communication
test_inter_service() {
    print_header "Testing Inter-Service Communication"
    
    # Frontend container should be able to reach backend via Docker network
    local result=$(docker exec ai-interviewer-frontend curl -sf http://backend:8000/health 2>&1)
    if echo "$result" | grep -q '"status":"healthy"'; then
        print_success "Frontend can reach backend via Docker network"
    else
        print_failure "Frontend cannot reach backend: $result"
    fi
}

# Test environment variables in backend
test_env_vars() {
    print_header "Testing Environment Variables"
    
    # Check DATABASE_PATH is set
    if docker exec ai-interviewer-backend printenv DATABASE_PATH | grep -q "interviews.db"; then
        print_success "DATABASE_PATH is configured"
    else
        print_warning "DATABASE_PATH may not be set correctly"
    fi
    
    # Check API keys are present (without showing values)
    if docker exec ai-interviewer-backend printenv OPENAI_API_KEY > /dev/null 2>&1; then
        print_success "OPENAI_API_KEY is present in container"
    else
        print_warning "OPENAI_API_KEY is not set in container"
    fi
    
    if docker exec ai-interviewer-backend printenv OPENROUTER_API_KEY > /dev/null 2>&1; then
        print_success "OPENROUTER_API_KEY is present in container"
    else
        print_warning "OPENROUTER_API_KEY is not set in container"
    fi
}

# Test database initialization
test_database() {
    print_header "Testing Database"
    
    # Check if database file exists in container
    if docker exec ai-interviewer-backend test -f /app/data/interviews.db; then
        print_success "Database file exists"
    else
        print_failure "Database file not found"
    fi
    
    # Check if data volume is mounted
    if docker exec ai-interviewer-backend ls /app/data > /dev/null 2>&1; then
        print_success "Data directory is accessible"
    else
        print_failure "Data directory is not accessible"
    fi
}

# Print summary
print_summary() {
    print_header "Test Summary"
    
    echo ""
    echo -e "  Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "  Tests Failed: ${RED}$TESTS_FAILED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        echo ""
        echo "Services are running at:"
        echo "  - Frontend: $FRONTEND_URL"
        echo "  - Backend:  $BACKEND_URL"
        echo "  - API Docs: $BACKEND_URL/docs"
        echo ""
        echo "To stop: docker compose down"
    else
        echo -e "${RED}Some tests failed. Check logs above for details.${NC}"
        echo ""
        echo "View full logs: docker compose logs"
    fi
}

# Cleanup function
cleanup() {
    if [ "${KEEP_RUNNING:-false}" != "true" ]; then
        print_header "Cleaning Up"
        docker compose down --remove-orphans 2>/dev/null || true
        print_info "Containers stopped"
    else
        print_info "Containers left running (KEEP_RUNNING=true)"
    fi
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --keep-running)
                KEEP_RUNNING=true
                shift
                ;;
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --keep-running  Leave containers running after tests"
                echo "  --skip-build    Skip the Docker build step"
                echo "  --help          Show this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

# Main execution
main() {
    parse_args "$@"
    
    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║   Container Integration Test Suite         ║"
    echo "╚════════════════════════════════════════════╝"
    
    # Change to project root
    cd "$(dirname "$0")/.."
    
    check_docker
    check_env_file
    
    if [ "${SKIP_BUILD:-false}" != "true" ]; then
        build_images
    else
        print_info "Skipping build (--skip-build)"
    fi
    
    start_containers
    
    # Give containers a moment to initialize
    sleep 3
    
    test_backend_health
    test_frontend_health
    test_api_root
    test_inter_service
    test_env_vars
    test_database
    
    print_summary
    
    # Only cleanup if tests failed or --keep-running not set
    if [ $TESTS_FAILED -gt 0 ] && [ "${KEEP_RUNNING:-false}" != "true" ]; then
        cleanup
    elif [ "${KEEP_RUNNING:-false}" != "true" ]; then
        cleanup
    fi
    
    exit $TESTS_FAILED
}

main "$@"

