#!/bin/bash
# FFXI Server Comprehensive Deployment Script
# Handles multi-instance deployment, load balancing, and high-load scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

log_section() {
    echo -e "\n${PURPLE}=== $1 ===${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_section "Checking Prerequisites"
    
    local missing_deps=()
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        missing_deps+=("docker-compose")
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # Check required Python packages
    if ! python3 -c "import requests" &> /dev/null; then
        missing_deps+=("python3-requests")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Installing missing dependencies..."
        
        # Install dependencies
        for dep in "${missing_deps[@]}"; do
            case $dep in
                docker)
                    curl -fsSL https://get.docker.com -o get-docker.sh
                    sh get-docker.sh
                    rm get-docker.sh
                    ;;
                docker-compose)
                    pip3 install docker-compose
                    ;;
                python3)
                    apt-get update && apt-get install -y python3 python3-pip
                    ;;
                python3-requests)
                    pip3 install requests mysql-connector-python flask flask-cors pyyaml
                    ;;
            esac
        done
    fi
    
    log_info "All prerequisites satisfied"
}

# Initialize environment
init_environment() {
    log_section "Initializing Environment"
    
    cd "$PROJECT_ROOT"
    
    # Create .env file if it doesn't exist
    if [[ ! -f "$ENV_FILE" ]]; then
        log_info "Creating .env file from template..."
        cp .env.example .env
        log_warn "Please edit .env file with your configuration before deployment"
    fi
    
    # Source environment variables
    if [[ -f "$ENV_FILE" ]]; then
        set -a
        # shellcheck source=/dev/null
        source "$ENV_FILE"
        set +a
        log_info "Environment variables loaded from .env"
    fi
    
    # Create necessary directories
    mkdir -p data/mysql logs docker/haproxy-errors
    
    # Set permissions
    chmod +x docker/*.sh
    chmod +x docker/api/app.py
    
    log_info "Environment initialized"
}

# Configure profiles based on load requirements
configure_profiles() {
    log_section "Configuring Service Profiles"
    
    local profiles="redis,admin"
    
    # Ask user about deployment type
    echo "Select deployment configuration:"
    echo "1) Basic (Single instance, basic monitoring)"
    echo "2) High Availability (Multiple instances, load balancer)"
    echo "3) High Load (Multiple instances, advanced monitoring, bonding)"
    echo "4) Development (All services including debugging tools)"
    echo "5) Custom (Specify profiles manually)"
    
    read -r -p "Choose deployment type [1-5]: " deployment_type
    
    case $deployment_type in
        1)
            profiles="redis,admin"
            ;;
        2)
            profiles="redis,admin,multi-instance,cloudflare"
            ;;
        3)
            profiles="redis,admin,multi-instance,high-load,monitoring,cloudflare"
            export FFXI_ENABLE_BONDING=true
            ;;
        4)
            profiles="redis,admin,multi-instance,monitoring,cloudflare"
            export FFXI_DEBUG_MODE=true
            ;;
        5)
            read -r -p "Enter profiles (comma-separated): " custom_profiles
            profiles="$custom_profiles"
            ;;
        *)
            log_warn "Invalid selection, using basic configuration"
            profiles="redis,admin"
            ;;
    esac
    
    export COMPOSE_PROFILES="$profiles"
    log_info "Configured profiles: $profiles"
    
    # Update .env file
    if grep -q "COMPOSE_PROFILES=" "$ENV_FILE"; then
        sed -i "s/COMPOSE_PROFILES=.*/COMPOSE_PROFILES=$profiles/" "$ENV_FILE"
    else
        echo "COMPOSE_PROFILES=$profiles" >> "$ENV_FILE"
    fi
}

# Configure network bonding if enabled
configure_bonding() {
    if [[ "${FFXI_ENABLE_BONDING:-false}" == "true" ]]; then
        log_section "Configuring Network Bonding"
        
        if [[ $EUID -eq 0 ]]; then
            log_info "Configuring network bonding..."
            bash docker/network_bonding.sh configure
        else
            log_warn "Network bonding requires root privileges"
            log_info "Run 'sudo bash docker/network_bonding.sh configure' after deployment"
        fi
    fi
}

# Configure firewall
configure_firewall() {
    if [[ "${FFXI_ENABLE_FIREWALL:-false}" == "true" ]]; then
        log_section "Configuring Firewall"
        
        if [[ $EUID -eq 0 ]]; then
            log_info "Configuring firewall..."
            bash docker/firewall.sh configure
        else
            log_warn "Firewall configuration requires root privileges"
            log_info "Run 'sudo bash docker/firewall.sh configure' after deployment"
        fi
    fi
}

# Build Docker images
build_images() {
    log_section "Building Docker Images"
    
    log_info "Building FFXI server image..."
    docker-compose build --parallel
    
    log_info "Docker images built successfully"
}

# Deploy services
deploy_services() {
    log_section "Deploying Services"
    
    log_info "Starting services with profiles: $COMPOSE_PROFILES"
    docker-compose up -d
    
    # Wait for services to start
    log_info "Waiting for services to initialize..."
    sleep 30
    
    # Check service health
    check_service_health
}

# Check service health
check_service_health() {
    log_section "Checking Service Health"
    
    local services=("ffxi-database" "ffxi-load-balancer" "ffxi-server-1" "ffxi-api")
    local failed_services=()
    
    for service in "${services[@]}"; do
        if docker-compose ps | grep "$service" | grep -q "Up"; then
            log_info "✓ $service is running"
        else
            log_error "✗ $service is not running"
            failed_services+=("$service")
        fi
    done
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_error "Failed services: ${failed_services[*]}"
        log_info "Check logs with: docker-compose logs <service_name>"
        return 1
    fi
    
    log_info "All core services are healthy"
    return 0
}

# Run comprehensive system test
run_system_test() {
    log_section "Running System Tests"
    
    log_info "Installing test dependencies..."
    pip3 install requests mysql-connector-python >/dev/null 2>&1
    
    log_info "Running comprehensive system test..."
    python3 docker/system_test.py
    
    if [[ -f "/tmp/ffxi_system_test_report.json" ]]; then
        log_info "Test report available at: /tmp/ffxi_system_test_report.json"
        
        # Show test summary
        python3 -c "
import json
with open('/tmp/ffxi_system_test_report.json') as f:
    report = json.load(f)
summary = report['summary']
print(f\"Test Summary: {summary['passed']}/{summary['total_tests']} passed ({summary['success_rate']:.1%})\")
if summary['failed'] > 0:
    print(f\"Failed tests: {summary['failed']}\")
"
    fi
}

# Display connection information
show_connection_info() {
    log_section "Connection Information"
    
    echo -e "${GREEN}FFXI Server Access:${NC}"
    echo "  Login Server: localhost:54001"
    echo "  Data Server:  localhost:54230"
    echo "  Auth Server:  localhost:54231"
    echo "  Config Port:  localhost:51220"
    echo "  Search Port:  localhost:54002"
    echo ""
    
    echo -e "${GREEN}Management Interfaces:${NC}"
    echo "  Admin Panel:      http://localhost:8088"
    echo "  API Endpoint:     http://localhost:5000"
    echo "  Database Admin:   http://localhost:8080 (if admin profile enabled)"
    echo "  Load Balancer:    http://localhost:8404/stats"
    echo ""
    
    if [[ "$COMPOSE_PROFILES" == *"monitoring"* ]]; then
        echo -e "${GREEN}Monitoring Interfaces:${NC}"
        echo "  Grafana:          http://localhost:3000"
        echo "  Prometheus:       http://localhost:9090"
        echo "  NetData:          http://localhost:19999"
        echo ""
    fi
    
    if [[ -n "${CLOUDFLARE_TUNNEL_TOKEN:-}" ]]; then
        echo -e "${GREEN}Cloudflare Tunnel:${NC}"
        echo "  Domain:           ${CLOUDFLARE_DOMAIN:-yourdomain.com}"
        echo "  Login:            https://login.${CLOUDFLARE_DOMAIN:-yourdomain.com}"
        echo "  Admin:            https://admin.${CLOUDFLARE_DOMAIN:-yourdomain.com}"
        echo ""
    fi
    
    echo -e "${GREEN}Default Credentials:${NC}"
    echo "  Database: ${MYSQL_USER:-xiuser} / ${MYSQL_PASSWORD:-xiserver_2024}"
    echo "  API:      admin / ${FFXI_API_SECRET_KEY:-your_secret_key_here_change_this}"
}

# Show management commands
show_management_commands() {
    log_section "Management Commands"
    
    echo -e "${GREEN}Common Operations:${NC}"
    echo "  Start services:           docker-compose up -d"
    echo "  Stop services:            docker-compose down"
    echo "  View logs:                docker-compose logs -f <service>"
    echo "  Restart service:          docker-compose restart <service>"
    echo "  Scale server instances:   docker-compose up -d --scale ffxi-server-1=2"
    echo ""
    
    echo -e "${GREEN}Monitoring:${NC}"
    echo "  System test:              python3 docker/system_test.py"
    echo "  Load balancer stats:      curl http://localhost:8404/stats"
    echo "  API status:               curl http://localhost:5000/health"
    echo "  Bonding status:           bash docker/network_bonding.sh status"
    echo ""
    
    echo -e "${GREEN}Maintenance:${NC}"
    echo "  Database backup:          docker-compose exec db mysqldump -u root -p xidb > backup.sql"
    echo "  Update images:            docker-compose pull && docker-compose up -d"
    echo "  Clean old data:           docker system prune"
}

# Cleanup function
cleanup() {
    log_section "Cleanup"
    
    log_info "Stopping services..."
    docker-compose down
    
    if [[ "${1:-}" == "full" ]]; then
        log_warn "Performing full cleanup (this will remove all data)..."
        docker-compose down -v
        docker system prune -f
        sudo rm -rf data/
    fi
    
    log_info "Cleanup completed"
}

# Update deployment
update_deployment() {
    log_section "Updating Deployment"
    
    log_info "Pulling latest images..."
    docker-compose pull
    
    log_info "Rebuilding custom images..."
    docker-compose build --pull
    
    log_info "Restarting services..."
    docker-compose up -d
    
    log_info "Update completed"
}

# Scale services
scale_services() {
    local scale_config="$1"
    
    log_section "Scaling Services"
    
    if [[ -z "$scale_config" ]]; then
        echo "Available scaling options:"
        echo "  low     - 1 server instance (default)"
        echo "  medium  - 2 server instances"
        echo "  high    - 3 server instances"
        read -r -p "Select scaling option: " scale_config
    fi
    
    case "$scale_config" in
        low)
            docker-compose up -d --scale ffxi-server-1=1
            ;;
        medium)
            export COMPOSE_PROFILES="${COMPOSE_PROFILES},multi-instance"
            docker-compose up -d --scale ffxi-server-1=1 --scale ffxi-server-2=1
            ;;
        high)
            export COMPOSE_PROFILES="${COMPOSE_PROFILES},multi-instance,high-load"
            docker-compose up -d --scale ffxi-server-1=1 --scale ffxi-server-2=1 --scale ffxi-server-3=1
            ;;
        *)
            log_error "Invalid scaling option: $scale_config"
            return 1
            ;;
    esac
    
    log_info "Services scaled to $scale_config configuration"
}

# Main function
main() {
    echo -e "${PURPLE}"
    echo "=================================="
    echo "  FFXI Server Deployment Manager"
    echo "=================================="
    echo -e "${NC}"
    
    case "${1:-deploy}" in
        deploy)
            check_prerequisites
            init_environment
            configure_profiles
            configure_bonding
            configure_firewall
            build_images
            deploy_services
            run_system_test
            show_connection_info
            show_management_commands
            log_info "Deployment completed successfully!"
            ;;
        start)
            init_environment
            deploy_services
            show_connection_info
            ;;
        stop)
            docker-compose down
            log_info "Services stopped"
            ;;
        restart)
            docker-compose restart
            log_info "Services restarted"
            ;;
        status)
            check_service_health
            ;;
        test)
            run_system_test
            ;;
        update)
            update_deployment
            ;;
        scale)
            scale_services "$2"
            ;;
        cleanup)
            cleanup "$2"
            ;;
        info)
            show_connection_info
            show_management_commands
            ;;
        logs)
            if [[ -n "$2" ]]; then
                docker-compose logs -f "$2"
            else
                docker-compose logs -f
            fi
            ;;
        *)
            echo "Usage: $0 {deploy|start|stop|restart|status|test|update|scale|cleanup|info|logs [service]}"
            echo ""
            echo "Commands:"
            echo "  deploy      - Full deployment with configuration"
            echo "  start       - Start existing services"
            echo "  stop        - Stop all services"
            echo "  restart     - Restart all services"
            echo "  status      - Check service health"
            echo "  test        - Run system tests"
            echo "  update      - Update and restart services"
            echo "  scale       - Scale services (low|medium|high)"
            echo "  cleanup     - Stop services and cleanup (add 'full' for complete cleanup)"
            echo "  info        - Show connection and management information"
            echo "  logs        - Show logs (optionally for specific service)"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"