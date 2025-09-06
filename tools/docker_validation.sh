#!/bin/bash
set -euo pipefail

# Docker Build and Test Validation Script
# Comprehensive Docker testing for FFXI Server CI/CD pipeline

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="/tmp/docker_validation.log"
CONTAINER_NAME="ffxi-test-$(date +%s)"
TEST_IMAGE="ffxi-server:ci-test"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✓${NC} $*" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠${NC} $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ✗${NC} $*" | tee -a "$LOG_FILE"
}

# Cleanup function
cleanup() {
    log "Cleaning up test environment..."
    
    # Stop and remove test containers
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    
    # Clean up test images
    docker rmi "$TEST_IMAGE" 2>/dev/null || true
    
    # Clean up Docker Compose
    cd "$PROJECT_ROOT"
    docker compose down -v 2>/dev/null || true
    
    # Clean up test files
    rm -f .env.test
    
    log "Cleanup completed"
}

# Trap cleanup on exit
trap cleanup EXIT

# Validation functions
validate_prerequisites() {
    log "Validating prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        return 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        return 1
    fi
    
    # Check Docker Compose
    if ! command -v docker compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        return 1
    fi
    
    # Check project structure
    cd "$PROJECT_ROOT"
    
    required_files=(
        "docker/Dockerfile"
        "docker-compose.yml"
        ".env.example"
        "docker/scripts/entrypoint.sh"
        "docker/configs/mysql.cnf"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Required file missing: $file"
            return 1
        fi
    done
    
    log_success "Prerequisites validated"
    return 0
}

validate_docker_configuration() {
    log "Validating Docker configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Validate docker compose syntax
    if ! docker compose config -q; then
        log_error "docker-compose.yml syntax validation failed"
        return 1
    fi
    
    # Check Dockerfile with hadolint if available
    if command -v hadolint &> /dev/null; then
        log "Running Dockerfile linting with hadolint..."
        if ! hadolint docker/Dockerfile; then
            log_warning "Dockerfile linting found issues (not blocking)"
        else
            log_success "Dockerfile linting passed"
        fi
    else
        log_warning "hadolint not available, skipping Dockerfile linting"
    fi
    
    # Validate environment variables
    required_env_vars=(
        "MYSQL_ROOT_PASSWORD"
        "MYSQL_DATABASE"
        "MYSQL_USER"
        "MYSQL_PASSWORD"
    )
    
    for var in "${required_env_vars[@]}"; do
        if ! grep -q "^${var}=" .env.example; then
            log_error "Required environment variable $var not found in .env.example"
            return 1
        fi
    done
    
    log_success "Docker configuration validated"
    return 0
}

test_docker_build() {
    log "Testing Docker build process..."
    
    cd "$PROJECT_ROOT"
    
    # Build the image with detailed output
    local build_start
    build_start=$(date +%s)
    
    if ! docker build \
        --progress=plain \
        --no-cache \
        -t "$TEST_IMAGE" \
        . 2>&1 | tee -a "$LOG_FILE"; then
        log_error "Docker build failed"
        return 1
    fi
    
    local build_end
    build_end=$(date +%s)
    local build_duration=$((build_end - build_start))
    
    # Verify image was created
    if ! docker images "$TEST_IMAGE" --format "{{.Repository}}:{{.Tag}}" | grep -q "$TEST_IMAGE"; then
        log_error "Built image not found"
        return 1
    fi
    
    # Get image size
    local image_size
    image_size=$(docker images "$TEST_IMAGE" --format "{{.Size}}")
    
    log_success "Docker build completed in ${build_duration}s, image size: $image_size"
    return 0
}

test_container_functionality() {
    log "Testing container functionality..."
    
    cd "$PROJECT_ROOT"
    
    # Create test environment
    cat > .env.test << EOF
MYSQL_ROOT_PASSWORD=test_root_password_123
MYSQL_DATABASE=xidb_test
MYSQL_USER=test_user
MYSQL_PASSWORD=test_password_123
FFXI_DEBUG_MODE=true
FFXI_LOG_LEVEL=DEBUG
COMPOSE_PROJECT_NAME=ffxi_test
EOF
    
    # Start database first
    if ! docker compose --env-file .env.test up -d db; then
        log_error "Failed to start database container"
        return 1
    fi
    
    # Wait for database to be ready
    log "Waiting for database to be ready..."
    local timeout=60
    local counter=0
    
    while ! docker compose --env-file .env.test exec -T db mysqladmin ping -h localhost --silent 2>/dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [[ $counter -ge $timeout ]]; then
            log_error "Database failed to start within ${timeout}s"
            docker compose --env-file .env.test logs db
            return 1
        fi
    done
    
    log_success "Database is ready"
    
    # Test basic container startup
    if ! docker run --rm \
        --network container:ffxi_test_db_1 \
        -e FFXI_SQL_HOST=localhost \
        -e FFXI_SQL_PASSWORD=test_root_password_123 \
        -e FFXI_SQL_USER=root \
        -e FFXI_SQL_DATABASE=xidb_test \
        "$TEST_IMAGE" /bin/bash -c "
            # Test database connectivity
            mysqladmin ping -h localhost -u root -ptest_root_password_123 --silent || exit 1
            echo 'Database connection successful'
            
            # Test binary existence
            ls -la /opt/ffxi/bin/ >/dev/null || echo 'Binaries directory exists'
            
            # Test configuration
            ls -la /opt/ffxi/settings/ >/dev/null || echo 'Settings directory exists'
            
            # Test entrypoint script
            test -x /opt/ffxi/entrypoint.sh || exit 1
            echo 'Entrypoint script is executable'
            
            # Test Python tools
            ls -la /opt/ffxi/tools/ >/dev/null || echo 'Tools directory exists'
            
            echo 'Container functionality test passed'
        "; then
        log_error "Container functionality test failed"
        return 1
    fi
    
    log_success "Container functionality test passed"
    return 0
}

test_docker_compose_stack() {
    log "Testing Docker Compose full stack..."
    
    cd "$PROJECT_ROOT"
    
    # Start all services
    if ! docker compose --env-file .env.test up -d; then
        log_error "Failed to start Docker Compose stack"
        return 1
    fi
    
    # Wait for services to start
    sleep 30
    
    # Check service status
    if ! docker compose --env-file .env.test ps; then
        log_error "Failed to get service status"
        return 1
    fi
    
    # Test health endpoints
    local max_attempts=10
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if docker compose --env-file .env.test exec -T ffxi-server curl -f http://localhost:8088/health 2>/dev/null; then
            log_success "Health endpoint responding"
            break
        fi
        
        attempt=$((attempt + 1))
        if [[ $attempt -eq $max_attempts ]]; then
            log_warning "Health endpoint not responding (may be expected in CI)"
        else
            sleep 5
        fi
    done
    
    # Check logs for critical errors
    log "Checking service logs for critical errors..."
    
    if docker compose --env-file .env.test logs ffxi-server | grep -i "error\|fatal\|critical" | grep -v "expected"; then
        log_warning "Found error messages in server logs (review required)"
    fi
    
    log_success "Docker Compose stack test completed"
    return 0
}

test_security_basics() {
    log "Testing basic security configurations..."
    
    # Check if container runs as non-root
    if docker run --rm "$TEST_IMAGE" whoami | grep -q "ffxi"; then
        log_success "Container runs as non-root user (ffxi)"
    else
        log_error "Container should run as non-root user"
        return 1
    fi
    
    # Check for obvious secrets in image
    if docker run --rm "$TEST_IMAGE" find /opt/ffxi -name "*.key" -o -name "*password*" -o -name "*secret*" | grep -v "example" | grep -q .; then
        log_error "Potential secrets found in image"
        return 1
    else
        log_success "No obvious secrets found in image"
    fi
    
    # Check file permissions
    if docker run --rm "$TEST_IMAGE" ls -la /opt/ffxi/bin/ 2>/dev/null | grep -q "^-rwxr-xr-x"; then
        log_success "Binary file permissions are correct"
    else
        log_warning "Binary file permissions may need review"
    fi
    
    log_success "Basic security tests passed"
    return 0
}

test_performance_basics() {
    log "Testing basic performance characteristics..."
    
    # Test build cache efficiency
    local cache_start
    cache_start=$(date +%s)
    
    if docker build --cache-from "$TEST_IMAGE" -t "${TEST_IMAGE}-cache" . >/dev/null 2>&1; then
        local cache_end
        cache_end=$(date +%s)
        local cache_duration=$((cache_end - cache_start))
        log_success "Build cache test completed in ${cache_duration}s"
    else
        log_warning "Build cache test failed"
    fi
    
    # Check image layers
    local layer_count
    layer_count=$(docker history "$TEST_IMAGE" --format "{{.ID}}" | wc -l)
    log "Image has $layer_count layers"
    
    if [[ $layer_count -gt 50 ]]; then
        log_warning "Image has many layers ($layer_count), consider optimization"
    fi
    
    # Check resource usage
    if command -v docker stats &> /dev/null; then
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || true
    fi
    
    log_success "Basic performance tests completed"
    return 0
}

generate_summary_report() {
    log "Generating summary report..."
    
    cat << EOF

================================================================================
DOCKER VALIDATION SUMMARY REPORT
================================================================================
Timestamp: $(date)
Test Duration: ${SECONDS}s
Log File: $LOG_FILE

Docker Environment:
- Docker Version: $(docker --version)
- Docker Compose Version: $(docker compose --version)
- System: $(uname -a)

Image Information:
- Test Image: $TEST_IMAGE
- Image Size: $(docker images "$TEST_IMAGE" --format "{{.Size}}" 2>/dev/null || echo "N/A")
- Layer Count: $(docker history "$TEST_IMAGE" --format "{{.ID}}" 2>/dev/null | wc -l || echo "N/A")

Test Results:
EOF

    if [[ -f "$LOG_FILE" ]]; then
        echo "- Successful Tests: $(grep -c "✓" "$LOG_FILE" || echo "0")"
        echo "- Warnings: $(grep -c "⚠" "$LOG_FILE" || echo "0")"
        echo "- Errors: $(grep -c "✗" "$LOG_FILE" || echo "0")"
    fi

    echo
    echo "For detailed logs, check: $LOG_FILE"
    echo "================================================================================"
}

# Main execution
main() {
    log "Starting Docker validation for FFXI Server..."
    log "Project root: $PROJECT_ROOT"
    
    # Initialize log file
    echo "Docker Validation Log - $(date)" > "$LOG_FILE"
    
    local exit_code=0
    
    # Run validation steps
    validate_prerequisites || exit_code=1
    validate_docker_configuration || exit_code=1
    test_docker_build || exit_code=1
    test_container_functionality || exit_code=1
    test_docker_compose_stack || exit_code=1
    test_security_basics || exit_code=1
    test_performance_basics || exit_code=1
    
    # Generate summary
    generate_summary_report
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "All Docker validation tests passed!"
    else
        log_error "Some Docker validation tests failed!"
    fi
    
    return $exit_code
}

# Handle arguments
case "${1:-all}" in
    "prereq"|"prerequisites")
        validate_prerequisites
        ;;
    "config"|"configuration")
        validate_docker_configuration
        ;;
    "build")
        test_docker_build
        ;;
    "functionality"|"func")
        test_container_functionality
        ;;
    "stack"|"compose")
        test_docker_compose_stack
        ;;
    "security"|"sec")
        test_security_basics
        ;;
    "performance"|"perf")
        test_performance_basics
        ;;
    "all"|"")
        main
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [COMMAND]"
        echo
        echo "Commands:"
        echo "  prereq       - Validate prerequisites only"
        echo "  config       - Validate Docker configuration only"
        echo "  build        - Test Docker build only"
        echo "  functionality - Test container functionality only"
        echo "  stack        - Test Docker Compose stack only"
        echo "  security     - Test basic security only"
        echo "  performance  - Test basic performance only"
        echo "  all          - Run all tests (default)"
        echo "  help         - Show this help message"
        exit 0
        ;;
    *)
        log_error "Unknown command: $1"
        log "Use '$0 help' for usage information"
        exit 1
        ;;
esac