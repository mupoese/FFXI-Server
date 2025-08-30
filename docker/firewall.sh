#!/bin/bash
# FFXI Server Firewall Configuration
# Security hardening and port management for high-load scenarios

set -e

echo "Configuring FFXI Server Firewall..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FFXI_PORTS=(54001 54230 54231 51220 54002 54003 8088)
ADMIN_PORTS=(3306 5000 8404 8080 9090 3000 19999)
ALLOWED_NETWORKS=("172.20.0.0/16" "10.0.0.0/8" "192.168.0.0/16")

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

# Check if running with sufficient privileges
check_privileges() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Install iptables if not present
install_iptables() {
    if ! command -v iptables &> /dev/null; then
        log_info "Installing iptables..."
        apt-get update && apt-get install -y iptables iptables-persistent
    fi
}

# Backup existing rules
backup_rules() {
    log_info "Backing up existing iptables rules..."
    iptables-save > /tmp/iptables_backup_$(date +%Y%m%d_%H%M%S).rules
}

# Clear existing rules
clear_rules() {
    log_info "Clearing existing iptables rules..."
    iptables -F
    iptables -X
    iptables -t nat -F
    iptables -t nat -X
    iptables -t mangle -F
    iptables -t mangle -X
}

# Set default policies
set_default_policies() {
    log_info "Setting default policies..."
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
    iptables -P OUTPUT ACCEPT
}

# Allow loopback traffic
allow_loopback() {
    log_info "Allowing loopback traffic..."
    iptables -I INPUT 1 -i lo -j ACCEPT
    iptables -I OUTPUT 1 -o lo -j ACCEPT
}

# Allow established and related connections
allow_established() {
    log_info "Allowing established and related connections..."
    iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
}

# Allow SSH (for management)
allow_ssh() {
    log_info "Allowing SSH access..."
    iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
}

# Allow FFXI game ports
allow_ffxi_ports() {
    log_info "Configuring FFXI game ports..."
    
    for port in "${FFXI_PORTS[@]}"; do
        # Allow TCP connections
        iptables -A INPUT -p tcp --dport $port -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
        
        # Allow UDP for game data (particularly important for port 54230)
        if [[ $port -eq 54230 ]]; then
            iptables -A INPUT -p udp --dport $port -j ACCEPT
            log_info "Allowing UDP traffic on port $port (game data)"
        fi
        
        log_info "Allowed TCP traffic on port $port"
    done
}

# Allow admin ports with network restrictions
allow_admin_ports() {
    log_info "Configuring administrative ports with network restrictions..."
    
    for port in "${ADMIN_PORTS[@]}"; do
        for network in "${ALLOWED_NETWORKS[@]}"; do
            iptables -A INPUT -p tcp --dport $port -s $network -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
        done
        log_info "Allowed admin access on port $port for trusted networks"
    done
}

# Rate limiting for login attempts
setup_rate_limiting() {
    log_info "Setting up rate limiting for login attempts..."
    
    # Rate limit login port (54001) to prevent brute force
    iptables -A INPUT -p tcp --dport 54001 -m conntrack --ctstate NEW -m limit --limit 10/min --limit-burst 20 -j ACCEPT
    iptables -A INPUT -p tcp --dport 54001 -m conntrack --ctstate NEW -j DROP
    
    # Rate limit API port (5000)
    iptables -A INPUT -p tcp --dport 5000 -m conntrack --ctstate NEW -m limit --limit 30/min --limit-burst 50 -j ACCEPT
    iptables -A INPUT -p tcp --dport 5000 -m conntrack --ctstate NEW -j DROP
    
    log_info "Rate limiting configured for login and API ports"
}

# DDoS protection
setup_ddos_protection() {
    log_info "Configuring DDoS protection..."
    
    # Limit connections per IP
    iptables -A INPUT -p tcp --syn -m connlimit --connlimit-above 50 -j REJECT --reject-with tcp-reset
    
    # Protect against port scans
    iptables -A INPUT -m recent --name portscan --rcheck --seconds 86400 -j DROP
    iptables -A INPUT -m recent --name portscan --remove
    iptables -A INPUT -p tcp -m tcp --dport 139 -m recent --name portscan --set -j LOG --log-prefix "portscan:"
    iptables -A INPUT -p tcp -m tcp --dport 139 -m recent --name portscan --set -j DROP
    
    # Protect against SYN flood
    iptables -A INPUT -p tcp --syn -m limit --limit 2/s --limit-burst 6 -j ACCEPT
    
    log_info "DDoS protection configured"
}

# Docker integration
allow_docker_traffic() {
    log_info "Configuring Docker network integration..."
    
    # Allow Docker bridge network
    iptables -I INPUT -i docker0 -j ACCEPT
    iptables -I OUTPUT -o docker0 -j ACCEPT
    
    # Allow traffic between containers in FFXI network
    iptables -I INPUT -s 172.20.0.0/16 -j ACCEPT
    iptables -I OUTPUT -d 172.20.0.0/16 -j ACCEPT
    
    # Forward traffic for Docker containers
    iptables -I FORWARD -i docker0 -o docker0 -j ACCEPT
    
    log_info "Docker network integration configured"
}

# Logging for security monitoring
setup_logging() {
    log_info "Setting up security logging..."
    
    # Log dropped packets (sample only to avoid log spam)
    iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables_INPUT_denied: " --log-level 7
    iptables -A FORWARD -m limit --limit 5/min -j LOG --log-prefix "iptables_FORWARD_denied: " --log-level 7
    
    log_info "Security logging configured"
}

# Network bonding support
setup_bonding_support() {
    if [[ "${FFXI_ENABLE_BONDING:-false}" == "true" ]]; then
        log_info "Configuring network bonding support..."
        
        # Allow bonding control traffic
        iptables -A INPUT -p tcp --dport 2049 -j ACCEPT  # NFS (if used for bonding)
        
        # Allow LACP (Link Aggregation Control Protocol) if using 802.3ad
        iptables -A INPUT -p slow -j ACCEPT
        
        log_info "Network bonding support configured"
    else
        log_info "Network bonding not enabled, skipping bonding configuration"
    fi
}

# Cloudflare specific rules
setup_cloudflare_rules() {
    if [[ -n "${CLOUDFLARE_TUNNEL_TOKEN:-}" ]]; then
        log_info "Configuring Cloudflare tunnel rules..."
        
        # Allow outbound connections to Cloudflare
        iptables -A OUTPUT -p tcp --dport 443 -d 198.41.192.0/18 -j ACCEPT
        iptables -A OUTPUT -p tcp --dport 443 -d 162.158.0.0/15 -j ACCEPT
        
        # Allow cloudflared health checks
        iptables -A INPUT -p tcp --dport 8081 -s 127.0.0.1 -j ACCEPT
        
        log_info "Cloudflare tunnel rules configured"
    else
        log_info "Cloudflare tunnel not configured, skipping Cloudflare rules"
    fi
}

# Save rules
save_rules() {
    log_info "Saving iptables rules..."
    
    if command -v iptables-save &> /dev/null; then
        iptables-save > /etc/iptables/rules.v4
        log_info "Rules saved to /etc/iptables/rules.v4"
    else
        log_warn "iptables-save not found, rules will not persist after reboot"
    fi
}

# Health check function
health_check() {
    log_info "Performing firewall health check..."
    
    # Check if rules are loaded
    rule_count=$(iptables -L | wc -l)
    if [[ $rule_count -gt 10 ]]; then
        log_info "Firewall rules loaded successfully ($rule_count lines)"
    else
        log_error "Firewall rules may not be loaded correctly"
        return 1
    fi
    
    # Test basic connectivity
    if nc -z localhost 54001 2>/dev/null; then
        log_info "FFXI login port (54001) is accessible"
    else
        log_warn "FFXI login port (54001) is not accessible"
    fi
    
    return 0
}

# Display current rules
show_rules() {
    echo -e "\n${GREEN}Current iptables rules:${NC}"
    iptables -L -n -v --line-numbers
    
    echo -e "\n${GREEN}NAT rules:${NC}"
    iptables -t nat -L -n -v --line-numbers
}

# Main function
main() {
    echo "FFXI Server Firewall Configuration"
    echo "=================================="
    
    # Check if we're in a container
    if [[ -f /.dockerenv ]]; then
        log_warn "Running in Docker container. Some firewall operations may be limited."
        log_info "For full firewall functionality, run this script on the host system."
    fi
    
    case "${1:-configure}" in
        configure)
            check_privileges
            install_iptables
            backup_rules
            clear_rules
            set_default_policies
            allow_loopback
            allow_established
            allow_ssh
            allow_ffxi_ports
            allow_admin_ports
            setup_rate_limiting
            setup_ddos_protection
            allow_docker_traffic
            setup_logging
            setup_bonding_support
            setup_cloudflare_rules
            save_rules
            health_check
            log_info "Firewall configuration completed successfully!"
            ;;
        show)
            show_rules
            ;;
        test)
            health_check
            ;;
        backup)
            backup_rules
            log_info "Firewall rules backed up"
            ;;
        restore)
            if [[ -n "$2" ]]; then
                log_info "Restoring rules from $2"
                iptables-restore < "$2"
            else
                log_error "Please specify backup file to restore"
                exit 1
            fi
            ;;
        *)
            echo "Usage: $0 {configure|show|test|backup|restore <file>}"
            echo "  configure  - Configure firewall rules"
            echo "  show      - Show current rules"
            echo "  test      - Test firewall health"
            echo "  backup    - Backup current rules"
            echo "  restore   - Restore rules from backup"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"