#!/usr/bin/env python3
"""
Network Bonding Management Script for FFXI Server

This script provides utilities for managing network bonding (link aggregation)
configuration to improve TCP and UDP performance.

Features:
- Linux bonding (802.3ad/LACP) setup and management
- Interface monitoring and health checks
- Performance tuning with kernel parameters
- RSS/RPS configuration for interrupt handling
- Network bonding statistics and monitoring

Author: LandSandBoat Development Team
License: GPL-3.0
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class NetworkInterface:
    """Network interface configuration"""
    name: str
    ip_address: str
    mac_address: str = ""
    status: str = "unknown"
    speed: str = "unknown"
    duplex: str = "unknown"
    rx_bytes: int = 0
    tx_bytes: int = 0
    rx_packets: int = 0
    tx_packets: int = 0
    rx_errors: int = 0
    tx_errors: int = 0

@dataclass
class BondingConfig:
    """Network bonding configuration"""
    bond_name: str = "bond0"
    mode: str = "802.3ad"
    hash_policy: str = "layer3+4"
    miimon: int = 100
    lacp_rate: str = "fast"
    slaves: List[str] = None
    
    def __post_init__(self):
        if self.slaves is None:
            self.slaves = []

class NetworkBondingManager:
    """Network bonding management class"""
    
    def __init__(self):
        self.config = BondingConfig()
        self.interfaces: Dict[str, NetworkInterface] = {}
        
    def check_root_privileges(self) -> bool:
        """Check if running with root privileges"""
        return os.geteuid() == 0
        
    def run_command(self, command: List[str], check: bool = True) -> Tuple[int, str, str]:
        """Run system command and return result"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout if e.stdout else "", e.stderr if e.stderr else str(e)
        except Exception as e:
            return -1, "", str(e)
    
    def discover_interfaces(self) -> List[NetworkInterface]:
        """Discover available network interfaces"""
        interfaces = []
        
        # Use ip command to get interface information
        returncode, stdout, stderr = self.run_command(['ip', 'link', 'show'], check=False)
        if returncode != 0:
            logger.error(f"Failed to discover interfaces: {stderr}")
            return interfaces
            
        current_interface = None
        for line in stdout.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Parse interface line
            if ': ' in line and not line.startswith(' '):
                parts = line.split(': ')
                if len(parts) >= 2:
                    interface_name = parts[1].split('@')[0]  # Remove VLAN info
                    current_interface = NetworkInterface(
                        name=interface_name,
                        ip_address=""
                    )
                    
            # Parse MAC address
            elif current_interface and 'link/ether' in line:
                parts = line.split()
                if len(parts) >= 2:
                    current_interface.mac_address = parts[1]
                    interfaces.append(current_interface)
                    self.interfaces[current_interface.name] = current_interface
                    
        # Get IP addresses
        self._update_interface_ips()
        
        return list(self.interfaces.values())
    
    def _update_interface_ips(self):
        """Update IP addresses for discovered interfaces"""
        returncode, stdout, stderr = self.run_command(['ip', 'addr', 'show'], check=False)
        if returncode != 0:
            return
            
        current_interface = None
        for line in stdout.split('\n'):
            line = line.strip()
            if line.startswith(('1:', '2:', '3:', '4:', '5:', '6:', '7:', '8:', '9:')):
                parts = line.split(': ')
                if len(parts) >= 2:
                    interface_name = parts[1].split('@')[0]
                    if interface_name in self.interfaces:
                        current_interface = self.interfaces[interface_name]
                        
            elif current_interface and 'inet ' in line:
                parts = line.split()
                if len(parts) >= 2:
                    current_interface.ip_address = parts[1].split('/')[0]
    
    def check_bonding_support(self) -> bool:
        """Check if bonding module is available"""
        returncode, stdout, stderr = self.run_command(['modprobe', '-n', 'bonding'], check=False)
        if returncode == 0:
            logger.info("Bonding module is available")
            return True
        else:
            logger.error("Bonding module is not available")
            return False
    
    def load_bonding_module(self) -> bool:
        """Load the bonding kernel module"""
        if not self.check_root_privileges():
            logger.error("Root privileges required to load bonding module")
            return False
            
        returncode, stdout, stderr = self.run_command(['modprobe', 'bonding'], check=False)
        if returncode == 0:
            logger.info("Bonding module loaded successfully")
            return True
        else:
            logger.error(f"Failed to load bonding module: {stderr}")
            return False
    
    def create_bond_interface(self, bond_name: str = None) -> bool:
        """Create a bonded interface"""
        if not self.check_root_privileges():
            logger.error("Root privileges required to create bond interface")
            return False
            
        if bond_name:
            self.config.bond_name = bond_name
            
        # Load bonding module first
        if not self.load_bonding_module():
            return False
        
        # Create bond interface
        bond_path = f"/sys/class/net/bonding_masters"
        try:
            with open(bond_path, 'w') as f:
                f.write(f"+{self.config.bond_name}")
            logger.info(f"Created bond interface: {self.config.bond_name}")
        except Exception as e:
            logger.error(f"Failed to create bond interface: {e}")
            return False
        
        # Configure bonding mode
        mode_path = f"/sys/class/net/{self.config.bond_name}/bonding/mode"
        try:
            with open(mode_path, 'w') as f:
                f.write(self.config.mode)
            logger.info(f"Set bonding mode to: {self.config.mode}")
        except Exception as e:
            logger.error(f"Failed to set bonding mode: {e}")
            return False
        
        # Configure hash policy for balance-xor and 802.3ad modes
        if self.config.mode in ['balance-xor', '802.3ad']:
            hash_path = f"/sys/class/net/{self.config.bond_name}/bonding/xmit_hash_policy"
            try:
                with open(hash_path, 'w') as f:
                    f.write(self.config.hash_policy)
                logger.info(f"Set hash policy to: {self.config.hash_policy}")
            except Exception as e:
                logger.error(f"Failed to set hash policy: {e}")
        
        # Configure MII monitoring
        miimon_path = f"/sys/class/net/{self.config.bond_name}/bonding/miimon"
        try:
            with open(miimon_path, 'w') as f:
                f.write(str(self.config.miimon))
            logger.info(f"Set MII monitoring interval to: {self.config.miimon}ms")
        except Exception as e:
            logger.error(f"Failed to set MII monitoring: {e}")
        
        # Configure LACP rate for 802.3ad mode
        if self.config.mode == '802.3ad':
            lacp_path = f"/sys/class/net/{self.config.bond_name}/bonding/lacp_rate"
            try:
                with open(lacp_path, 'w') as f:
                    f.write(self.config.lacp_rate)
                logger.info(f"Set LACP rate to: {self.config.lacp_rate}")
            except Exception as e:
                logger.error(f"Failed to set LACP rate: {e}")
        
        return True
    
    def add_slave_interface(self, interface_name: str) -> bool:
        """Add a slave interface to the bond"""
        if not self.check_root_privileges():
            logger.error("Root privileges required to add slave interface")
            return False
        
        # Bring interface down first
        returncode, stdout, stderr = self.run_command(['ip', 'link', 'set', interface_name, 'down'], check=False)
        if returncode != 0:
            logger.error(f"Failed to bring down interface {interface_name}: {stderr}")
            return False
        
        # Add to bond
        slaves_path = f"/sys/class/net/{self.config.bond_name}/bonding/slaves"
        try:
            with open(slaves_path, 'w') as f:
                f.write(f"+{interface_name}")
            logger.info(f"Added {interface_name} to bond {self.config.bond_name}")
            self.config.slaves.append(interface_name)
            return True
        except Exception as e:
            logger.error(f"Failed to add slave interface {interface_name}: {e}")
            return False
    
    def remove_slave_interface(self, interface_name: str) -> bool:
        """Remove a slave interface from the bond"""
        if not self.check_root_privileges():
            logger.error("Root privileges required to remove slave interface")
            return False
        
        slaves_path = f"/sys/class/net/{self.config.bond_name}/bonding/slaves"
        try:
            with open(slaves_path, 'w') as f:
                f.write(f"-{interface_name}")
            logger.info(f"Removed {interface_name} from bond {self.config.bond_name}")
            if interface_name in self.config.slaves:
                self.config.slaves.remove(interface_name)
            return True
        except Exception as e:
            logger.error(f"Failed to remove slave interface {interface_name}: {e}")
            return False
    
    def configure_bond_ip(self, ip_address: str, netmask: str = "24") -> bool:
        """Configure IP address for bond interface"""
        if not self.check_root_privileges():
            logger.error("Root privileges required to configure bond IP")
            return False
        
        # Bring bond interface up
        returncode, stdout, stderr = self.run_command(['ip', 'link', 'set', self.config.bond_name, 'up'], check=False)
        if returncode != 0:
            logger.error(f"Failed to bring up bond interface: {stderr}")
            return False
        
        # Configure IP address
        returncode, stdout, stderr = self.run_command([
            'ip', 'addr', 'add', f"{ip_address}/{netmask}", 'dev', self.config.bond_name
        ], check=False)
        if returncode != 0:
            logger.error(f"Failed to configure bond IP: {stderr}")
            return False
        
        logger.info(f"Configured bond interface {self.config.bond_name} with IP {ip_address}/{netmask}")
        return True
    
    def get_bond_status(self) -> Dict:
        """Get bonding interface status"""
        status = {
            "bond_name": self.config.bond_name,
            "mode": self.config.mode,
            "slaves": [],
            "active_slave": "",
            "mii_status": "unknown"
        }
        
        bond_info_path = f"/proc/net/bonding/{self.config.bond_name}"
        if not os.path.exists(bond_info_path):
            status["error"] = "Bond interface not found"
            return status
        
        try:
            with open(bond_info_path, 'r') as f:
                content = f.read()
                
            # Parse bond information
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('Slave Interface:'):
                    slave_name = line.split(':')[1].strip()
                    status["slaves"].append(slave_name)
                elif line.startswith('Currently Active Slave:'):
                    status["active_slave"] = line.split(':')[1].strip()
                elif line.startswith('MII Status:'):
                    status["mii_status"] = line.split(':')[1].strip()
                    
        except Exception as e:
            status["error"] = str(e)
        
        return status
    
    def optimize_network_performance(self) -> bool:
        """Apply network performance optimizations"""
        if not self.check_root_privileges():
            logger.error("Root privileges required for performance optimization")
            return False
        
        optimizations = [
            # TCP optimizations
            ("net.core.rmem_max", "16777216"),
            ("net.core.wmem_max", "16777216"),
            ("net.ipv4.tcp_rmem", "4096 12582912 16777216"),
            ("net.ipv4.tcp_wmem", "4096 12582912 16777216"),
            ("net.ipv4.tcp_window_scaling", "1"),
            ("net.ipv4.tcp_timestamps", "1"),
            ("net.ipv4.tcp_sack", "1"),
            ("net.ipv4.tcp_no_metrics_save", "1"),
            
            # UDP optimizations
            ("net.core.netdev_max_backlog", "5000"),
            ("net.core.netdev_budget", "600"),
            
            # Network device optimizations
            ("net.core.dev_weight", "64"),
        ]
        
        success = True
        for param, value in optimizations:
            returncode, stdout, stderr = self.run_command([
                'sysctl', '-w', f"{param}={value}"
            ], check=False)
            
            if returncode == 0:
                logger.info(f"Set {param} = {value}")
            else:
                logger.error(f"Failed to set {param}: {stderr}")
                success = False
        
        return success
    
    def configure_rss_rps(self) -> bool:
        """Configure Receive Side Scaling (RSS) and Receive Packet Steering (RPS)"""
        if not self.check_root_privileges():
            logger.error("Root privileges required for RSS/RPS configuration")
            return False
        
        # Configure RSS and RPS for bond interface and slaves
        interfaces_to_configure = [self.config.bond_name] + self.config.slaves
        
        for interface in interfaces_to_configure:
            if not os.path.exists(f"/sys/class/net/{interface}"):
                continue
                
            # Configure RPS (Receive Packet Steering)
            rps_cpus_path = f"/sys/class/net/{interface}/queues/rx-0/rps_cpus"
            if os.path.exists(rps_cpus_path):
                try:
                    # Use all available CPUs
                    cpu_count = os.cpu_count()
                    cpu_mask = (1 << cpu_count) - 1
                    with open(rps_cpus_path, 'w') as f:
                        f.write(hex(cpu_mask))
                    logger.info(f"Configured RPS for {interface} with CPU mask {hex(cpu_mask)}")
                except Exception as e:
                    logger.error(f"Failed to configure RPS for {interface}: {e}")
            
            # Configure interrupt coalescing
            returncode, stdout, stderr = self.run_command([
                'ethtool', '-C', interface, 'rx-usecs', '50', 'tx-usecs', '50'
            ], check=False)
            
            if returncode == 0:
                logger.info(f"Configured interrupt coalescing for {interface}")
            else:
                logger.warning(f"Could not configure interrupt coalescing for {interface}: {stderr}")
        
        return True
    
    def get_interface_statistics(self) -> Dict[str, Dict]:
        """Get detailed interface statistics"""
        stats = {}
        
        for interface_name in [self.config.bond_name] + self.config.slaves:
            if not os.path.exists(f"/sys/class/net/{interface_name}"):
                continue
                
            interface_stats = {}
            stats_path = f"/sys/class/net/{interface_name}/statistics"
            
            if os.path.exists(stats_path):
                for stat_file in os.listdir(stats_path):
                    try:
                        with open(os.path.join(stats_path, stat_file), 'r') as f:
                            interface_stats[stat_file] = int(f.read().strip())
                    except:
                        pass
            
            stats[interface_name] = interface_stats
        
        return stats
    
    def remove_bond_interface(self) -> bool:
        """Remove the bond interface"""
        if not self.check_root_privileges():
            logger.error("Root privileges required to remove bond interface")
            return False
        
        # Remove all slave interfaces first
        for slave in self.config.slaves.copy():
            self.remove_slave_interface(slave)
        
        # Bring bond interface down
        returncode, stdout, stderr = self.run_command(['ip', 'link', 'set', self.config.bond_name, 'down'], check=False)
        
        # Remove bond interface
        bond_path = f"/sys/class/net/bonding_masters"
        try:
            with open(bond_path, 'w') as f:
                f.write(f"-{self.config.bond_name}")
            logger.info(f"Removed bond interface: {self.config.bond_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove bond interface: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Network Bonding Management for FFXI Server")
    parser.add_argument('--action', choices=[
        'discover', 'create', 'add-slave', 'remove-slave', 'status', 
        'optimize', 'stats', 'remove', 'configure-rss'
    ], required=True, help="Action to perform")
    
    parser.add_argument('--bond-name', default='bond0', help="Bond interface name")
    parser.add_argument('--mode', default='802.3ad', choices=[
        'balance-rr', 'active-backup', 'balance-xor', 'broadcast', '802.3ad', 'balance-tlb', 'balance-alb'
    ], help="Bonding mode")
    parser.add_argument('--hash-policy', default='layer3+4', choices=[
        'layer2', 'layer3+4', 'layer2+3', 'encap2+3', 'encap3+4'
    ], help="Hash policy for load balancing")
    parser.add_argument('--interface', help="Network interface name")
    parser.add_argument('--ip-address', help="IP address for bond interface")
    parser.add_argument('--netmask', default='24', help="Network mask for bond interface")
    parser.add_argument('--output-json', action='store_true', help="Output results in JSON format")
    parser.add_argument('--verbose', '-v', action='store_true', help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    manager = NetworkBondingManager()
    manager.config.bond_name = args.bond_name
    manager.config.mode = args.mode
    manager.config.hash_policy = args.hash_policy
    
    result = {"success": False, "data": None, "error": None}
    
    try:
        if args.action == 'discover':
            interfaces = manager.discover_interfaces()
            result["success"] = True
            result["data"] = [asdict(iface) for iface in interfaces]
            
        elif args.action == 'create':
            if manager.create_bond_interface():
                if args.ip_address:
                    success = manager.configure_bond_ip(args.ip_address, args.netmask)
                else:
                    success = True
                result["success"] = success
                result["data"] = {"bond_name": manager.config.bond_name}
            
        elif args.action == 'add-slave':
            if not args.interface:
                result["error"] = "Interface name required for add-slave action"
            else:
                result["success"] = manager.add_slave_interface(args.interface)
                
        elif args.action == 'remove-slave':
            if not args.interface:
                result["error"] = "Interface name required for remove-slave action"
            else:
                result["success"] = manager.remove_slave_interface(args.interface)
                
        elif args.action == 'status':
            status = manager.get_bond_status()
            result["success"] = True
            result["data"] = status
            
        elif args.action == 'optimize':
            result["success"] = manager.optimize_network_performance()
            
        elif args.action == 'configure-rss':
            result["success"] = manager.configure_rss_rps()
            
        elif args.action == 'stats':
            stats = manager.get_interface_statistics()
            result["success"] = True
            result["data"] = stats
            
        elif args.action == 'remove':
            result["success"] = manager.remove_bond_interface()
            
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Action failed: {e}")
    
    if args.output_json:
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            logger.info(f"Action '{args.action}' completed successfully")
            if result["data"]:
                logger.info(f"Result: {result['data']}")
        else:
            logger.error(f"Action '{args.action}' failed")
            if result["error"]:
                logger.error(f"Error: {result['error']}")

if __name__ == '__main__':
    main()