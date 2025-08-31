#!/bin/bash
# Network Bonding Configuration for FFXI Server
# High-performance data handling compatible with Windower and Ashita

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BONDING_INTERFACE="bond0"
BONDING_MODE="${FFXI_BONDING_MODE:-balance-xor}"
BONDING_HASH_POLICY="${FFXI_BONDING_HASH_POLICY:-layer3+4}"
MII_MON_INTERVAL="${FFXI_BONDING_MII_MON_INTERVAL:-100}"
export FAILOVER_TIMEOUT="${FFXI_BONDING_FAILOVER_TIMEOUT:-5000}"
BONDING_INTERFACES="${FFXI_BONDING_INTERFACES:-}"

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

# Check if bonding is enabled
check_bonding_enabled() {
    if [[ "${FFXI_ENABLE_BONDING:-false}" != "true" ]]; then
        log_warn "Network bonding is disabled. Set FFXI_ENABLE_BONDING=true to enable."
        exit 0
    fi
}

# Check if running with sufficient privileges
check_privileges() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Install bonding dependencies
install_dependencies() {
    log_info "Installing network bonding dependencies..."
    
    # Update package list
    apt-get update
    
    # Install required packages
    apt-get install -y \
        ifenslave \
        net-tools \
        ethtool \
        bridge-utils \
        iproute2 \
        tcpdump \
        iperf3
    
    log_info "Dependencies installed successfully"
}

# Load bonding kernel module
load_bonding_module() {
    log_info "Loading bonding kernel module..."
    
    # Load bonding module
    modprobe bonding
    
    # Add to modules file for persistence
    if ! grep -q "bonding" /etc/modules; then
        echo "bonding" >> /etc/modules
        log_info "Added bonding module to /etc/modules for persistence"
    fi
    
    # Verify module is loaded
    if lsmod | grep -q bonding; then
        log_info "Bonding module loaded successfully"
    else
        log_error "Failed to load bonding module"
        exit 1
    fi
}

# Detect available network interfaces
detect_interfaces() {
    log_info "Detecting available network interfaces..."
    
    local available_interfaces=()
    
    # Get all network interfaces except loopback and bonding interfaces
    while IFS= read -r interface; do
        if [[ "$interface" != "lo" && "$interface" != bond* && "$interface" != docker* ]]; then
            # Check if interface is up and has a link
            if ip link show "$interface" | grep -q "state UP"; then
                available_interfaces+=("$interface")
                log_debug "Found interface: $interface (UP)"
            else
                log_debug "Found interface: $interface (DOWN)"
            fi
        fi
    done < <(ip link show | grep -E '^[0-9]+:' | awk -F': ' '{print $2}' | cut -d'@' -f1)
    
    if [[ ${#available_interfaces[@]} -eq 0 ]]; then
        log_warn "No suitable interfaces found for bonding"
        return 1
    fi
    
    log_info "Available interfaces: ${available_interfaces[*]}"
    
    # If no interfaces specified, use first two available
    if [[ -z "$BONDING_INTERFACES" ]]; then
        if [[ ${#available_interfaces[@]} -ge 2 ]]; then
            BONDING_INTERFACES="${available_interfaces[0]},${available_interfaces[1]}"
            log_info "Auto-selected interfaces: $BONDING_INTERFACES"
        else
            log_warn "Only ${#available_interfaces[@]} interface(s) available. Bonding requires at least 2."
            return 1
        fi
    fi
    
    return 0
}

# Create bonding interface
create_bonding_interface() {
    log_info "Creating bonding interface: $BONDING_INTERFACE"
    
    # Remove existing bonding interface if it exists
    if ip link show "$BONDING_INTERFACE" &>/dev/null; then
        log_info "Removing existing bonding interface..."
        ip link set "$BONDING_INTERFACE" down
        echo "-$BONDING_INTERFACE" > /sys/class/net/bonding_masters
    fi
    
    # Create new bonding interface
    echo "+$BONDING_INTERFACE" > /sys/class/net/bonding_masters
    
    if ip link show "$BONDING_INTERFACE" &>/dev/null; then
        log_info "Bonding interface $BONDING_INTERFACE created successfully"
    else
        log_error "Failed to create bonding interface"
        exit 1
    fi
}

# Configure bonding parameters
configure_bonding_parameters() {
    log_info "Configuring bonding parameters..."
    
    local bond_path="/sys/class/net/$BONDING_INTERFACE/bonding"
    
    # Set bonding mode
    echo "$BONDING_MODE" > "$bond_path/mode"
    log_info "Set bonding mode: $BONDING_MODE"
    
    # Set hash policy for balance-xor and 802.3ad modes
    if [[ "$BONDING_MODE" == "balance-xor" || "$BONDING_MODE" == "802.3ad" ]]; then
        echo "$BONDING_HASH_POLICY" > "$bond_path/xmit_hash_policy"
        log_info "Set hash policy: $BONDING_HASH_POLICY"
    fi
    
    # Set MII monitoring interval
    echo "$MII_MON_INTERVAL" > "$bond_path/miimon"
    log_info "Set MII monitoring interval: ${MII_MON_INTERVAL}ms"
    
    # Configure additional parameters for high-performance
    
    # Set updelay and downdelay for stability
    echo "200" > "$bond_path/updelay"
    echo "200" > "$bond_path/downdelay"
    log_info "Set up/down delays: 200ms"
    
    # Enable ARP monitoring as backup (if not using LACP)
    if [[ "$BONDING_MODE" != "802.3ad" ]]; then
        echo "5000" > "$bond_path/arp_interval"
        log_info "Set ARP monitoring interval: 5000ms"
    fi
}

# Add slave interfaces to bond
add_slave_interfaces() {
    log_info "Adding slave interfaces to bond..."
    
    IFS=',' read -ra INTERFACES <<< "$BONDING_INTERFACES"
    
    for interface in "${INTERFACES[@]}"; do
        interface=$(echo "$interface" | xargs)  # Trim whitespace
        
        if ! ip link show "$interface" &>/dev/null; then
            log_error "Interface $interface does not exist"
            continue
        fi
        
        log_info "Configuring interface $interface..."
        
        # Bring interface down
        ip link set "$interface" down
        
        # Remove any existing IP configuration
        ip addr flush dev "$interface"
        
        # Set interface to slave mode
        ip link set "$interface" master "$BONDING_INTERFACE"
        
        # Bring interface up
        ip link set "$interface" up
        
        # Verify interface was added to bond
        if grep -q "$interface" "/sys/class/net/$BONDING_INTERFACE/bonding/slaves"; then
            log_info "Successfully added $interface to $BONDING_INTERFACE"
        else
            log_error "Failed to add $interface to $BONDING_INTERFACE"
        fi
    done
}

# Configure bonding interface network settings
configure_bonding_network() {
    log_info "Configuring bonding interface network settings..."
    
    # Bring bonding interface up
    ip link set "$BONDING_INTERFACE" up
    
    # Configure IP address (use DHCP or static based on environment)
    if [[ -n "${FFXI_BONDING_IP:-}" ]]; then
        # Static IP configuration
        ip addr add "${FFXI_BONDING_IP}/24" dev "$BONDING_INTERFACE"
        log_info "Assigned static IP: ${FFXI_BONDING_IP}/24"
        
        if [[ -n "${FFXI_BONDING_GATEWAY:-}" ]]; then
            ip route add default via "${FFXI_BONDING_GATEWAY}" dev "$BONDING_INTERFACE"
            log_info "Set gateway: ${FFXI_BONDING_GATEWAY}"
        fi
    else
        # Try DHCP
        log_info "Attempting DHCP configuration..."
        dhclient "$BONDING_INTERFACE" &
        sleep 5
        
        # Check if IP was assigned
        if ip addr show "$BONDING_INTERFACE" | grep -q "inet "; then
            local assigned_ip
            assigned_ip=$(ip addr show "$BONDING_INTERFACE" | grep "inet " | awk '{print $2}')
            log_info "DHCP assigned IP: $assigned_ip"
        else
            log_warn "DHCP failed, bonding interface has no IP address"
        fi
    fi
}

# Optimize network performance for FFXI
optimize_network_performance() {
    log_info "Optimizing network performance for FFXI..."
    
    # Enable TCP window scaling
    echo 1 > /proc/sys/net/ipv4/tcp_window_scaling
    
    # Increase TCP buffer sizes for high throughput
    echo "4096 87380 6291456" > /proc/sys/net/ipv4/tcp_rmem
    echo "4096 65536 6291456" > /proc/sys/net/ipv4/tcp_wmem
    
    # Increase network buffer sizes
    echo 16777216 > /proc/sys/net/core/rmem_max
    echo 16777216 > /proc/sys/net/core/wmem_max
    echo 262144 > /proc/sys/net/core/rmem_default
    echo 262144 > /proc/sys/net/core/wmem_default
    
    # Optimize for latency (important for gaming)
    echo 1 > /proc/sys/net/ipv4/tcp_low_latency
    echo 1 > /proc/sys/net/ipv4/tcp_no_delay
    
    # Enable TCP timestamps for better RTT estimation
    echo 1 > /proc/sys/net/ipv4/tcp_timestamps
    
    # Optimize network device queue
    for interface in $(echo "$BONDING_INTERFACES" | tr ',' ' '); do
        interface=$(echo "$interface" | xargs)
        if ip link show "$interface" &>/dev/null; then
            # Set tx queue length
            ip link set "$interface" txqueuelen 10000
            
            # Configure ethtool settings if available
            if command -v ethtool &>/dev/null; then
                # Enable hardware offloading features
                ethtool -K "$interface" gso on tso on gro on lro on rx on tx on sg on 2>/dev/null || true
                
                # Set ring buffer sizes
                ethtool -G "$interface" rx 4096 tx 4096 2>/dev/null || true
                
                # Set interrupt coalescing for lower latency
                ethtool -C "$interface" rx-usecs 1 tx-usecs 1 2>/dev/null || true
            fi
        fi
    done
    
    # Configure bonding interface optimizations
    if ip link show "$BONDING_INTERFACE" &>/dev/null; then
        ip link set "$BONDING_INTERFACE" txqueuelen 10000
        ip link set "$BONDING_INTERFACE" mtu 1500
    fi
    
    log_info "Network performance optimizations applied"
}

# Create persistent configuration
create_persistent_config() {
    log_info "Creating persistent network configuration..."
    
    # Create systemd network configuration
    cat > "/etc/systemd/network/10-$BONDING_INTERFACE.netdev" << EOF
[NetDev]
Name=$BONDING_INTERFACE
Kind=bond

[Bond]
Mode=$BONDING_MODE
TransmitHashPolicy=$BONDING_HASH_POLICY
MIIMonitorSec=${MII_MON_INTERVAL}ms
UpDelaySec=200ms
DownDelaySec=200ms
EOF

    # Create network configuration for bonding interface
    cat > "/etc/systemd/network/20-$BONDING_INTERFACE.network" << EOF
[Match]
Name=$BONDING_INTERFACE

[Network]
DHCP=${FFXI_BONDING_DHCP:-yes}
${FFXI_BONDING_IP:+Address=$FFXI_BONDING_IP/24}
${FFXI_BONDING_GATEWAY:+Gateway=$FFXI_BONDING_GATEWAY}
IPForward=yes

[DHCP]
UseDNS=yes
UseRoutes=yes
EOF

    # Create configuration for slave interfaces
    IFS=',' read -ra INTERFACES <<< "$BONDING_INTERFACES"
    for interface in "${INTERFACES[@]}"; do
        interface=$(echo "$interface" | xargs)
        
        cat > "/etc/systemd/network/30-$interface.network" << EOF
[Match]
Name=$interface

[Network]
Bond=$BONDING_INTERFACE
EOF
    done
    
    log_info "Persistent configuration created in /etc/systemd/network/"
    log_info "Configuration will be applied on next reboot"
}

# Test bonding functionality
test_bonding() {
    log_info "Testing bonding functionality..."
    
    # Check bonding status
    if [[ -f "/proc/net/bonding/$BONDING_INTERFACE" ]]; then
        echo -e "\n${GREEN}Bonding Status:${NC}"
        cat "/proc/net/bonding/$BONDING_INTERFACE"
    else
        log_error "Bonding interface $BONDING_INTERFACE not found"
        return 1
    fi
    
    # Test connectivity
    local test_host="${FFXI_BONDING_TEST_HOST:-8.8.8.8}"
    if ping -c 3 -I "$BONDING_INTERFACE" "$test_host" &>/dev/null; then
        log_info "Connectivity test passed (ping to $test_host)"
    else
        log_warn "Connectivity test failed (ping to $test_host)"
    fi
    
    # Performance test with iperf3 if available
    if command -v iperf3 &>/dev/null && [[ -n "${FFXI_BONDING_IPERF_SERVER:-}" ]]; then
        log_info "Running performance test..."
        iperf3 -c "${FFXI_BONDING_IPERF_SERVER}" -t 10 -i 1 --bind-dev "$BONDING_INTERFACE" || true
    fi
    
    return 0
}

# Monitor bonding status
monitor_bonding() {
    log_info "Starting bonding monitor..."
    
    while true; do
        echo -e "\n${BLUE}=== Bonding Status $(date) ===${NC}"
        
        # Show bonding status
        if [[ -f "/proc/net/bonding/$BONDING_INTERFACE" ]]; then
            grep -E "(Bonding Mode|MII Status|Slave Interface)" "/proc/net/bonding/$BONDING_INTERFACE"
        fi
        
        # Show interface statistics
        echo -e "\n${GREEN}Interface Statistics:${NC}"
        grep -E "(${BONDING_INTERFACE}|$(echo "$BONDING_INTERFACES" | tr ',' '|'))" "/proc/net/dev"
        
        sleep 30
    done
}

# Show bonding information
show_bonding_info() {
    echo -e "${GREEN}FFXI Network Bonding Configuration${NC}"
    echo "=================================="
    echo "Bonding Interface: $BONDING_INTERFACE"
    echo "Bonding Mode: $BONDING_MODE"
    echo "Hash Policy: $BONDING_HASH_POLICY"
    echo "MII Monitoring: ${MII_MON_INTERVAL}ms"
    echo "Slave Interfaces: $BONDING_INTERFACES"
    echo ""
    
    if [[ -f "/proc/net/bonding/$BONDING_INTERFACE" ]]; then
        echo -e "${GREEN}Current Status:${NC}"
        cat "/proc/net/bonding/$BONDING_INTERFACE"
    else
        echo "Bonding interface not configured"
    fi
}

# Remove bonding configuration
remove_bonding() {
    log_info "Removing bonding configuration..."
    
    # Remove slave interfaces
    IFS=',' read -ra INTERFACES <<< "$BONDING_INTERFACES"
    for interface in "${INTERFACES[@]}"; do
        interface=$(echo "$interface" | xargs)
        
        if [[ -f "/sys/class/net/$BONDING_INTERFACE/bonding/slaves" ]] && \
           grep -q "$interface" "/sys/class/net/$BONDING_INTERFACE/bonding/slaves"; then
            echo "-$interface" > "/sys/class/net/$BONDING_INTERFACE/bonding/slaves"
            log_info "Removed $interface from bonding"
        fi
    done
    
    # Remove bonding interface
    if ip link show "$BONDING_INTERFACE" &>/dev/null; then
        ip link set "$BONDING_INTERFACE" down
        echo "-$BONDING_INTERFACE" > /sys/class/net/bonding_masters
        log_info "Removed bonding interface $BONDING_INTERFACE"
    fi
    
    # Remove persistent configuration
    rm -f "/etc/systemd/network/10-$BONDING_INTERFACE.netdev"
    rm -f "/etc/systemd/network/20-$BONDING_INTERFACE.network"
    rm -f /etc/systemd/network/30-*.network
    
    log_info "Bonding configuration removed"
}

# Main function
main() {
    echo "FFXI Network Bonding Configuration"
    echo "================================="
    
    case "${1:-configure}" in
        configure)
            check_bonding_enabled
            check_privileges
            install_dependencies
            load_bonding_module
            detect_interfaces || exit 1
            create_bonding_interface
            configure_bonding_parameters
            add_slave_interfaces
            configure_bonding_network
            optimize_network_performance
            create_persistent_config
            test_bonding
            log_info "Network bonding configuration completed successfully!"
            show_bonding_info
            ;;
        status|info)
            show_bonding_info
            ;;
        test)
            test_bonding
            ;;
        monitor)
            monitor_bonding
            ;;
        remove)
            check_privileges
            remove_bonding
            ;;
        *)
            echo "Usage: $0 {configure|status|test|monitor|remove}"
            echo "  configure  - Configure network bonding"
            echo "  status     - Show bonding status"
            echo "  test       - Test bonding functionality"
            echo "  monitor    - Monitor bonding status (continuous)"
            echo "  remove     - Remove bonding configuration"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"