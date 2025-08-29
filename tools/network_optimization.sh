#!/bin/bash
#
# Network Performance Optimization Script for FFXI Server
# 
# This script applies kernel parameter optimizations and interrupt handling
# configurations to improve TCP and UDP performance with network bonding.
#
# Author: LandSandBoat Development Team
# License: GPL-3.0
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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
    if [[ "${DEBUG:-0}" == "1" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root for system optimization"
        exit 1
    fi
}

# Apply kernel parameter optimizations
optimize_kernel_parameters() {
    log_info "Applying kernel parameter optimizations..."
    
    # TCP/UDP buffer optimizations
    local tcp_udp_params=(
        "net.core.rmem_max=16777216"
        "net.core.wmem_max=16777216"
        "net.core.rmem_default=262144"
        "net.core.wmem_default=262144"
        "net.ipv4.tcp_rmem=4096 12582912 16777216"
        "net.ipv4.tcp_wmem=4096 12582912 16777216"
        "net.ipv4.udp_rmem_min=8192"
        "net.ipv4.udp_wmem_min=8192"
    )
    
    # TCP performance optimizations
    local tcp_performance_params=(
        "net.ipv4.tcp_window_scaling=1"
        "net.ipv4.tcp_timestamps=1"
        "net.ipv4.tcp_sack=1"
        "net.ipv4.tcp_fack=1"
        "net.ipv4.tcp_no_metrics_save=1"
        "net.ipv4.tcp_moderate_rcvbuf=1"
        "net.ipv4.tcp_congestion_control=bbr"
        "net.core.default_qdisc=fq"
    )
    
    # Network device optimizations
    local network_device_params=(
        "net.core.netdev_max_backlog=5000"
        "net.core.netdev_budget=600"
        "net.core.dev_weight=64"
        "net.core.busy_read=50"
        "net.core.busy_poll=50"
    )
    
    # Apply all parameters
    local all_params=("${tcp_udp_params[@]}" "${tcp_performance_params[@]}" "${network_device_params[@]}")
    
    for param in "${all_params[@]}"; do
        log_debug "Setting $param"
        sysctl -w "$param" > /dev/null 2>&1 || log_warn "Failed to set $param"
    done
    
    log_info "Kernel parameters optimized successfully"
}

# Configure Receive Side Scaling (RSS)
configure_rss() {
    local interface="$1"
    log_info "Configuring RSS for interface $interface..."
    
    if ! command -v ethtool &> /dev/null; then
        log_warn "ethtool not found, skipping RSS configuration"
        return 1
    fi
    
    # Check if interface exists
    if [[ ! -d "/sys/class/net/$interface" ]]; then
        log_warn "Interface $interface not found"
        return 1
    fi
    
    # Configure RSS hash key and indirection table
    ethtool -X "$interface" equal 2>/dev/null || log_warn "Could not configure RSS indirection table for $interface"
    
    # Configure RSS hash fields
    ethtool -N "$interface" rx-flow-hash udp4 sdfn 2>/dev/null || log_warn "Could not configure UDP4 RSS hash for $interface"
    ethtool -N "$interface" rx-flow-hash tcp4 sdfn 2>/dev/null || log_warn "Could not configure TCP4 RSS hash for $interface"
    
    log_info "RSS configured for $interface"
}

# Configure Receive Packet Steering (RPS)
configure_rps() {
    local interface="$1"
    log_info "Configuring RPS for interface $interface..."
    
    # Check if interface exists
    if [[ ! -d "/sys/class/net/$interface" ]]; then
        log_warn "Interface $interface not found"
        return 1
    fi
    
    # Get number of CPUs
    local cpu_count
    cpu_count=$(nproc)
    local cpu_mask
    cpu_mask=$((2**cpu_count - 1))
    
    # Configure RPS for all RX queues
    for queue_dir in /sys/class/net/"$interface"/queues/rx-*; do
        if [[ -d "$queue_dir" ]]; then
            local rps_cpus_file="$queue_dir/rps_cpus"
            if [[ -w "$rps_cpus_file" ]]; then
                printf "%x" "$cpu_mask" > "$rps_cpus_file"
                log_debug "Set RPS CPU mask $cpu_mask for $(basename "$queue_dir")"
            fi
        fi
    done
    
    log_info "RPS configured for $interface"
}

# Configure interrupt coalescing
configure_interrupt_coalescing() {
    local interface="$1"
    log_info "Configuring interrupt coalescing for interface $interface..."
    
    if ! command -v ethtool &> /dev/null; then
        log_warn "ethtool not found, skipping interrupt coalescing configuration"
        return 1
    fi
    
    # Check if interface exists
    if [[ ! -d "/sys/class/net/$interface" ]]; then
        log_warn "Interface $interface not found"
        return 1
    fi
    
    # Configure adaptive interrupt coalescing
    ethtool -C "$interface" adaptive-rx on adaptive-tx on 2>/dev/null || log_warn "Could not enable adaptive coalescing for $interface"
    
    # Set moderate interrupt coalescing values
    ethtool -C "$interface" rx-usecs 50 tx-usecs 50 2>/dev/null || log_warn "Could not set interrupt coalescing timers for $interface"
    ethtool -C "$interface" rx-frames 10 tx-frames 10 2>/dev/null || log_warn "Could not set interrupt coalescing frame counts for $interface"
    
    log_info "Interrupt coalescing configured for $interface"
}

# Configure IRQ affinity
configure_irq_affinity() {
    local interface="$1"
    log_info "Configuring IRQ affinity for interface $interface..."
    
    # Find IRQs for the interface
    local irqs
    mapfile -t irqs < <(grep -l "$interface" /proc/irq/*/actions 2>/dev/null | grep -o '/proc/irq/[0-9]*/' | grep -o '[0-9]*' || true)
    
    if [[ ${#irqs[@]} -eq 0 ]]; then
        log_warn "No IRQs found for interface $interface"
        return 1
    fi
    
    local cpu_count
    cpu_count=$(nproc)
    local cpu_index=0
    
    for irq in "${irqs[@]}"; do
        local cpu_mask=$((1 << (cpu_index % cpu_count)))
        if [[ -w "/proc/irq/$irq/smp_affinity" ]]; then
            printf "%x" "$cpu_mask" > "/proc/irq/$irq/smp_affinity"
            log_debug "Set IRQ $irq affinity to CPU $((cpu_index % cpu_count))"
            ((cpu_index++))
        fi
    done
    
    log_info "IRQ affinity configured for $interface (${#irqs[@]} IRQs)"
}

# Configure bonding-specific optimizations
configure_bonding_optimizations() {
    local bond_interface="$1"
    log_info "Configuring bonding-specific optimizations for $bond_interface..."
    
    # Check if bonding interface exists
    if [[ ! -d "/sys/class/net/$bond_interface" ]]; then
        log_warn "Bonding interface $bond_interface not found"
        return 1
    fi
    
    # Configure bonding-specific parameters
    local bonding_params=(
        "net.ipv4.conf.$bond_interface.arp_interval=0"
        "net.ipv4.conf.$bond_interface.arp_ip_target="
        "net.ipv4.conf.$bond_interface.arp_validate=0"
    )
    
    for param in "${bonding_params[@]}"; do
        sysctl -w "$param" > /dev/null 2>&1 || log_warn "Failed to set $param"
    done
    
    # Get slave interfaces
    local slaves_file="/sys/class/net/$bond_interface/bonding/slaves"
    if [[ -r "$slaves_file" ]]; then
        local slaves
        slaves=$(cat "$slaves_file")
        log_info "Optimizing slave interfaces: $slaves"
        
        for slave in $slaves; do
            configure_rss "$slave"
            configure_rps "$slave"
            configure_interrupt_coalescing "$slave"
            configure_irq_affinity "$slave"
        done
    fi
    
    # Configure the bonding interface itself
    configure_rps "$bond_interface"
    
    log_info "Bonding optimizations completed for $bond_interface"
}

# Save optimizations to persist across reboots
save_optimizations() {
    log_info "Saving optimizations for persistence..."
    
    local sysctl_conf="/etc/sysctl.d/99-ffxi-network-optimization.conf"
    
    cat > "$sysctl_conf" << 'EOF'
# FFXI Server Network Optimizations
# Applied automatically by network optimization script

# TCP/UDP Buffer Optimizations
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.core.rmem_default = 262144
net.core.wmem_default = 262144
net.ipv4.tcp_rmem = 4096 12582912 16777216
net.ipv4.tcp_wmem = 4096 12582912 16777216
net.ipv4.udp_rmem_min = 8192
net.ipv4.udp_wmem_min = 8192

# TCP Performance Optimizations
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_sack = 1
net.ipv4.tcp_fack = 1
net.ipv4.tcp_no_metrics_save = 1
net.ipv4.tcp_moderate_rcvbuf = 1
net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq

# Network Device Optimizations
net.core.netdev_max_backlog = 5000
net.core.netdev_budget = 600
net.core.dev_weight = 64
net.core.busy_read = 50
net.core.busy_poll = 50
EOF
    
    log_info "Optimizations saved to $sysctl_conf"
}

# Display current network statistics
show_network_stats() {
    local interface="$1"
    log_info "Network statistics for $interface:"
    
    if [[ -d "/sys/class/net/$interface/statistics" ]]; then
        local stats_dir="/sys/class/net/$interface/statistics"
        echo "  RX Bytes:    $(cat "$stats_dir/rx_bytes" 2>/dev/null || echo "N/A")"
        echo "  TX Bytes:    $(cat "$stats_dir/tx_bytes" 2>/dev/null || echo "N/A")"
        echo "  RX Packets:  $(cat "$stats_dir/rx_packets" 2>/dev/null || echo "N/A")"
        echo "  TX Packets:  $(cat "$stats_dir/tx_packets" 2>/dev/null || echo "N/A")"
        echo "  RX Errors:   $(cat "$stats_dir/rx_errors" 2>/dev/null || echo "N/A")"
        echo "  TX Errors:   $(cat "$stats_dir/tx_errors" 2>/dev/null || echo "N/A")"
        echo "  RX Dropped:  $(cat "$stats_dir/rx_dropped" 2>/dev/null || echo "N/A")"
        echo "  TX Dropped:  $(cat "$stats_dir/tx_dropped" 2>/dev/null || echo "N/A")"
    else
        log_warn "Statistics not available for $interface"
    fi
}

# Main function
main() {
    local action="$1"
    local interface="${2:-}"
    
    case "$action" in
        "optimize-all")
            check_root
            optimize_kernel_parameters
            save_optimizations
            log_info "System optimization completed"
            ;;
        "configure-interface")
            if [[ -z "$interface" ]]; then
                log_error "Interface name required for configure-interface action"
                exit 1
            fi
            check_root
            configure_rss "$interface"
            configure_rps "$interface"
            configure_interrupt_coalescing "$interface"
            configure_irq_affinity "$interface"
            ;;
        "configure-bonding")
            if [[ -z "$interface" ]]; then
                log_error "Bonding interface name required for configure-bonding action"
                exit 1
            fi
            check_root
            configure_bonding_optimizations "$interface"
            ;;
        "show-stats")
            if [[ -z "$interface" ]]; then
                log_error "Interface name required for show-stats action"
                exit 1
            fi
            show_network_stats "$interface"
            ;;
        "help")
            echo "Usage: $0 <action> [interface]"
            echo ""
            echo "Actions:"
            echo "  optimize-all           - Apply all kernel optimizations"
            echo "  configure-interface    - Configure RSS/RPS/IRQ for interface"
            echo "  configure-bonding      - Configure bonding-specific optimizations"
            echo "  show-stats            - Show network statistics for interface"
            echo "  help                  - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 optimize-all"
            echo "  $0 configure-interface eth0"
            echo "  $0 configure-bonding bond0"
            echo "  $0 show-stats bond0"
            ;;
        *)
            log_error "Unknown action: $action"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -eq 0 ]]; then
        main "help"
    else
        main "$@"
    fi
fi