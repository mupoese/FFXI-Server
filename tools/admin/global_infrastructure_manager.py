#!/usr/bin/env python3
"""
Global Infrastructure Management System
ITERATION 12: Advanced Ecosystem & Global Scale

This module provides comprehensive global infrastructure management
for multi-region FFXI server deployment with CDN integration,
load balancing, and geographic routing.
"""

import asyncio
import logging
import json
import time
import aiohttp
import ssl
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import socket
import subprocess
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RegionStatus(Enum):
    """Server region status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class LoadBalancingStrategy(Enum):
    """Load balancing strategy enumeration"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    GEOGRAPHIC = "geographic"
    PERFORMANCE_BASED = "performance_based"

@dataclass
class ServerNode:
    """Server node configuration and status"""
    node_id: str
    region: str
    hostname: str
    port: int
    capacity: int
    current_load: int = 0
    status: RegionStatus = RegionStatus.HEALTHY
    last_health_check: datetime = field(default_factory=datetime.now)
    response_time: float = 0.0
    player_count: int = 0
    uptime: timedelta = field(default_factory=lambda: timedelta(0))

@dataclass
class RegionCluster:
    """Regional server cluster configuration"""
    region_id: str
    region_name: str
    geographic_zone: str
    primary_nodes: List[ServerNode] = field(default_factory=list)
    secondary_nodes: List[ServerNode] = field(default_factory=list)
    cdn_endpoints: List[str] = field(default_factory=list)
    status: RegionStatus = RegionStatus.HEALTHY
    total_capacity: int = 0
    current_load: int = 0
    player_count: int = 0

class GlobalInfrastructureManager:
    """
    Global Infrastructure Management System
    
    Manages multi-region server deployment, load balancing,
    CDN integration, and geographic routing for FFXI servers.
    """
    
    def __init__(self, config_path: str = "global_infrastructure_config.yaml"):
        self.config_path = config_path
        self.regions: Dict[str, RegionCluster] = {}
        self.load_balancing_strategy = LoadBalancingStrategy.GEOGRAPHIC
        self.health_check_interval = 30  # seconds
        self.failover_threshold = 0.8  # 80% failure rate
        self.monitoring_active = False
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'regions_healthy': 0,
            'total_player_count': 0
        }
        
        self.load_configuration()
    
    def load_configuration(self):
        """Load global infrastructure configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Load regions
            for region_config in config.get('regions', []):
                self.create_region_cluster(region_config)
            
            # Load global settings
            global_config = config.get('global', {})
            self.load_balancing_strategy = LoadBalancingStrategy(
                global_config.get('load_balancing_strategy', 'geographic')
            )
            self.health_check_interval = global_config.get('health_check_interval', 30)
            self.failover_threshold = global_config.get('failover_threshold', 0.8)
            
            logger.info(f"Loaded configuration for {len(self.regions)} regions")
            
        except FileNotFoundError:
            logger.warning(f"Configuration file {self.config_path} not found, using defaults")
            self.create_default_configuration()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.create_default_configuration()
    
    def create_default_configuration(self):
        """Create default global infrastructure configuration"""
        # North America cluster
        na_cluster = RegionCluster(
            region_id="na",
            region_name="North America",
            geographic_zone="americas",
            cdn_endpoints=[
                "https://na-cdn.ffxi-server.org",
                "https://us-east-cdn.ffxi-server.org",
                "https://us-west-cdn.ffxi-server.org"
            ]
        )
        
        # Add North America nodes
        na_cluster.primary_nodes = [
            ServerNode("na-primary-1", "na", "na-srv-01.ffxi-server.org", 54230, 1000),
            ServerNode("na-primary-2", "na", "na-srv-02.ffxi-server.org", 54230, 1000),
        ]
        na_cluster.secondary_nodes = [
            ServerNode("na-secondary-1", "na", "na-srv-03.ffxi-server.org", 54230, 500),
            ServerNode("na-secondary-2", "na", "na-srv-04.ffxi-server.org", 54230, 500),
        ]
        
        # Europe cluster
        eu_cluster = RegionCluster(
            region_id="eu",
            region_name="Europe",
            geographic_zone="emea",
            cdn_endpoints=[
                "https://eu-cdn.ffxi-server.org",
                "https://eu-west-cdn.ffxi-server.org",
                "https://eu-central-cdn.ffxi-server.org"
            ]
        )
        
        # Add Europe nodes
        eu_cluster.primary_nodes = [
            ServerNode("eu-primary-1", "eu", "eu-srv-01.ffxi-server.org", 54230, 800),
            ServerNode("eu-primary-2", "eu", "eu-srv-02.ffxi-server.org", 54230, 800),
        ]
        eu_cluster.secondary_nodes = [
            ServerNode("eu-secondary-1", "eu", "eu-srv-03.ffxi-server.org", 54230, 400),
        ]
        
        # Asia-Pacific cluster
        ap_cluster = RegionCluster(
            region_id="ap",
            region_name="Asia-Pacific",
            geographic_zone="apac",
            cdn_endpoints=[
                "https://ap-cdn.ffxi-server.org",
                "https://jp-cdn.ffxi-server.org",
                "https://au-cdn.ffxi-server.org"
            ]
        )
        
        # Add Asia-Pacific nodes
        ap_cluster.primary_nodes = [
            ServerNode("ap-primary-1", "ap", "ap-srv-01.ffxi-server.org", 54230, 600),
            ServerNode("ap-primary-2", "ap", "ap-srv-02.ffxi-server.org", 54230, 600),
        ]
        ap_cluster.secondary_nodes = [
            ServerNode("ap-secondary-1", "ap", "ap-srv-03.ffxi-server.org", 54230, 300),
        ]
        
        # Register clusters
        self.regions = {
            "na": na_cluster,
            "eu": eu_cluster,
            "ap": ap_cluster
        }
        
        # Calculate total capacities
        for cluster in self.regions.values():
            cluster.total_capacity = (
                sum(node.capacity for node in cluster.primary_nodes) +
                sum(node.capacity for node in cluster.secondary_nodes)
            )
        
        logger.info("Created default global infrastructure configuration")
    
    def create_region_cluster(self, region_config: Dict[str, Any]) -> RegionCluster:
        """Create a region cluster from configuration"""
        cluster = RegionCluster(
            region_id=region_config['region_id'],
            region_name=region_config['region_name'],
            geographic_zone=region_config['geographic_zone'],
            cdn_endpoints=region_config.get('cdn_endpoints', [])
        )
        
        # Create primary nodes
        for node_config in region_config.get('primary_nodes', []):
            node = ServerNode(
                node_id=node_config['node_id'],
                region=cluster.region_id,
                hostname=node_config['hostname'],
                port=node_config['port'],
                capacity=node_config['capacity']
            )
            cluster.primary_nodes.append(node)
        
        # Create secondary nodes
        for node_config in region_config.get('secondary_nodes', []):
            node = ServerNode(
                node_id=node_config['node_id'],
                region=cluster.region_id,
                hostname=node_config['hostname'],
                port=node_config['port'],
                capacity=node_config['capacity']
            )
            cluster.secondary_nodes.append(node)
        
        # Calculate total capacity
        cluster.total_capacity = (
            sum(node.capacity for node in cluster.primary_nodes) +
            sum(node.capacity for node in cluster.secondary_nodes)
        )
        
        self.regions[cluster.region_id] = cluster
        return cluster
    
    async def start_monitoring(self):
        """Start global infrastructure monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        
        logger.info("Starting global infrastructure monitoring")
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self.health_check_loop()),
            asyncio.create_task(self.load_balancing_loop()),
            asyncio.create_task(self.metrics_collection_loop()),
            asyncio.create_task(self.failover_monitoring_loop())
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_monitoring(self):
        """Stop global infrastructure monitoring"""
        self.monitoring_active = False
        if self.session:
            await self.session.close()
        logger.info("Stopped global infrastructure monitoring")
    
    async def health_check_loop(self):
        """Continuous health checking for all regions"""
        while self.monitoring_active:
            try:
                await self.perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(5)
    
    async def perform_health_checks(self):
        """Perform health checks on all server nodes"""
        tasks = []
        
        for cluster in self.regions.values():
            all_nodes = cluster.primary_nodes + cluster.secondary_nodes
            
            for node in all_nodes:
                task = asyncio.create_task(self.check_node_health(node))
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update cluster status based on node health
            self.update_cluster_statuses()
            
            # Log health check results
            healthy_nodes = sum(1 for result in results if result is True)
            total_nodes = len(tasks)
            logger.info(f"Health check completed: {healthy_nodes}/{total_nodes} nodes healthy")
    
    async def check_node_health(self, node: ServerNode) -> bool:
        """Check health of a specific server node"""
        try:
            start_time = time.time()
            
            # Attempt to connect to server
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(node.hostname, node.port),
                timeout=5.0
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            node.response_time = response_time
            node.last_health_check = datetime.now()
            
            # Close connection
            writer.close()
            await writer.wait_closed()
            
            # Update node status
            if response_time < 1.0:  # Less than 1 second is healthy
                node.status = RegionStatus.HEALTHY
            elif response_time < 3.0:  # Less than 3 seconds is degraded
                node.status = RegionStatus.DEGRADED
            else:
                node.status = RegionStatus.OFFLINE
            
            logger.debug(f"Node {node.node_id} health check: {node.status.value} ({response_time:.3f}s)")
            return node.status == RegionStatus.HEALTHY
            
        except Exception as e:
            node.status = RegionStatus.OFFLINE
            node.last_health_check = datetime.now()
            logger.warning(f"Node {node.node_id} health check failed: {e}")
            return False
    
    def update_cluster_statuses(self):
        """Update cluster statuses based on node health"""
        for cluster in self.regions.values():
            all_nodes = cluster.primary_nodes + cluster.secondary_nodes
            healthy_nodes = sum(1 for node in all_nodes if node.status == RegionStatus.HEALTHY)
            total_nodes = len(all_nodes)
            
            if total_nodes == 0:
                cluster.status = RegionStatus.OFFLINE
            elif healthy_nodes == 0:
                cluster.status = RegionStatus.OFFLINE
            elif healthy_nodes / total_nodes < 0.5:  # Less than 50% healthy
                cluster.status = RegionStatus.DEGRADED
            else:
                cluster.status = RegionStatus.HEALTHY
    
    async def load_balancing_loop(self):
        """Continuous load balancing optimization"""
        while self.monitoring_active:
            try:
                await self.optimize_load_distribution()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in load balancing loop: {e}")
                await asyncio.sleep(10)
    
    async def optimize_load_distribution(self):
        """Optimize load distribution across regions"""
        total_load = sum(cluster.current_load for cluster in self.regions.values())
        total_capacity = sum(cluster.total_capacity for cluster in self.regions.values())
        
        if total_capacity == 0:
            return
        
        optimal_distribution = {}
        
        for region_id, cluster in self.regions.items():
            if cluster.status == RegionStatus.HEALTHY:
                optimal_load = int(total_load * (cluster.total_capacity / total_capacity))
                optimal_distribution[region_id] = optimal_load
        
        logger.debug(f"Optimal load distribution: {optimal_distribution}")
    
    async def metrics_collection_loop(self):
        """Continuous metrics collection"""
        while self.monitoring_active:
            try:
                await self.collect_metrics()
                await asyncio.sleep(30)  # Collect every 30 seconds
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(10)
    
    async def collect_metrics(self):
        """Collect global infrastructure metrics"""
        # Reset metrics
        self.metrics['regions_healthy'] = 0
        self.metrics['total_player_count'] = 0
        total_response_time = 0.0
        node_count = 0
        
        for cluster in self.regions.values():
            if cluster.status == RegionStatus.HEALTHY:
                self.metrics['regions_healthy'] += 1
            
            self.metrics['total_player_count'] += cluster.player_count
            
            all_nodes = cluster.primary_nodes + cluster.secondary_nodes
            for node in all_nodes:
                if node.status == RegionStatus.HEALTHY:
                    total_response_time += node.response_time
                    node_count += 1
        
        # Calculate average response time
        if node_count > 0:
            self.metrics['average_response_time'] = total_response_time / node_count
    
    async def failover_monitoring_loop(self):
        """Monitor for failover conditions"""
        while self.monitoring_active:
            try:
                await self.check_failover_conditions()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in failover monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def check_failover_conditions(self):
        """Check if failover is needed for any region"""
        for cluster in self.regions.values():
            primary_nodes = cluster.primary_nodes
            healthy_primary = sum(1 for node in primary_nodes if node.status == RegionStatus.HEALTHY)
            
            if len(primary_nodes) > 0:
                failure_rate = 1.0 - (healthy_primary / len(primary_nodes))
                
                if failure_rate >= self.failover_threshold:
                    await self.trigger_failover(cluster)
    
    async def trigger_failover(self, cluster: RegionCluster):
        """Trigger failover for a degraded region"""
        logger.warning(f"Triggering failover for region {cluster.region_id}")
        
        # Promote secondary nodes to primary
        healthy_secondary = [node for node in cluster.secondary_nodes 
                           if node.status == RegionStatus.HEALTHY]
        
        if healthy_secondary:
            # Move healthy secondary nodes to primary
            for node in healthy_secondary:
                cluster.primary_nodes.append(node)
                cluster.secondary_nodes.remove(node)
                logger.info(f"Promoted node {node.node_id} to primary")
        
        # Update cluster status
        self.update_cluster_statuses()
    
    def get_optimal_region(self, client_location: Optional[str] = None) -> Optional[str]:
        """Get optimal region for client connection"""
        healthy_regions = [
            region_id for region_id, cluster in self.regions.items()
            if cluster.status == RegionStatus.HEALTHY
        ]
        
        if not healthy_regions:
            return None
        
        if self.load_balancing_strategy == LoadBalancingStrategy.GEOGRAPHIC and client_location:
            # Geographic routing logic would go here
            # For now, return first healthy region
            return healthy_regions[0]
        
        elif self.load_balancing_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            # Find region with least load
            min_load = float('inf')
            best_region = None
            
            for region_id in healthy_regions:
                cluster = self.regions[region_id]
                load_ratio = cluster.current_load / cluster.total_capacity
                
                if load_ratio < min_load:
                    min_load = load_ratio
                    best_region = region_id
            
            return best_region
        
        elif self.load_balancing_strategy == LoadBalancingStrategy.PERFORMANCE_BASED:
            # Find region with best performance
            best_performance = float('inf')
            best_region = None
            
            for region_id in healthy_regions:
                cluster = self.regions[region_id]
                avg_response_time = sum(
                    node.response_time for node in cluster.primary_nodes
                ) / max(len(cluster.primary_nodes), 1)
                
                if avg_response_time < best_performance:
                    best_performance = avg_response_time
                    best_region = region_id
            
            return best_region
        
        else:  # Round robin or default
            return healthy_regions[0]
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'global_metrics': self.metrics,
            'regions': {
                region_id: {
                    'status': cluster.status.value,
                    'player_count': cluster.player_count,
                    'capacity': cluster.total_capacity,
                    'load': cluster.current_load,
                    'primary_nodes': len(cluster.primary_nodes),
                    'secondary_nodes': len(cluster.secondary_nodes),
                    'cdn_endpoints': len(cluster.cdn_endpoints)
                }
                for region_id, cluster in self.regions.items()
            },
            'configuration': {
                'load_balancing_strategy': self.load_balancing_strategy.value,
                'health_check_interval': self.health_check_interval,
                'failover_threshold': self.failover_threshold,
                'monitoring_active': self.monitoring_active
            }
        }
    
    def save_configuration(self):
        """Save current configuration to file"""
        config = {
            'global': {
                'load_balancing_strategy': self.load_balancing_strategy.value,
                'health_check_interval': self.health_check_interval,
                'failover_threshold': self.failover_threshold
            },
            'regions': []
        }
        
        for cluster in self.regions.values():
            region_config = {
                'region_id': cluster.region_id,
                'region_name': cluster.region_name,
                'geographic_zone': cluster.geographic_zone,
                'cdn_endpoints': cluster.cdn_endpoints,
                'primary_nodes': [
                    {
                        'node_id': node.node_id,
                        'hostname': node.hostname,
                        'port': node.port,
                        'capacity': node.capacity
                    }
                    for node in cluster.primary_nodes
                ],
                'secondary_nodes': [
                    {
                        'node_id': node.node_id,
                        'hostname': node.hostname,
                        'port': node.port,
                        'capacity': node.capacity
                    }
                    for node in cluster.secondary_nodes
                ]
            }
            config['regions'].append(region_config)
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Configuration saved to {self.config_path}")

# CDN Integration Manager
class CDNManager:
    """CDN Integration and Management System"""
    
    def __init__(self, infrastructure_manager: GlobalInfrastructureManager):
        self.infrastructure = infrastructure_manager
        self.cache_policies = {}
        self.edge_locations = {}
    
    async def optimize_content_delivery(self):
        """Optimize content delivery across CDN network"""
        logger.info("Optimizing CDN content delivery")
        
        for cluster in self.infrastructure.regions.values():
            for endpoint in cluster.cdn_endpoints:
                await self.validate_cdn_endpoint(endpoint)
    
    async def validate_cdn_endpoint(self, endpoint: str) -> bool:
        """Validate CDN endpoint availability"""
        try:
            if self.infrastructure.session:
                async with self.infrastructure.session.get(endpoint) as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"CDN endpoint validation failed for {endpoint}: {e}")
        
        return False

# Example usage and testing
async def main():
    """Main function for testing global infrastructure"""
    infrastructure = GlobalInfrastructureManager()
    
    print("\n🌐 FFXI Global Infrastructure Management System")
    print("=" * 60)
    
    # Start monitoring
    monitoring_task = asyncio.create_task(infrastructure.start_monitoring())
    
    # Let it run for a few iterations
    await asyncio.sleep(10)
    
    # Get status report
    status = infrastructure.get_status_report()
    print(f"\n📊 Global Infrastructure Status:")
    print(f"Monitoring Active: {status['configuration']['monitoring_active']}")
    print(f"Healthy Regions: {status['global_metrics']['regions_healthy']}")
    print(f"Total Players: {status['global_metrics']['total_player_count']}")
    print(f"Average Response Time: {status['global_metrics']['average_response_time']:.3f}s")
    
    print(f"\n🗺️ Regional Status:")
    for region_id, region_data in status['regions'].items():
        print(f"  {region_id.upper()}: {region_data['status']} "
              f"({region_data['primary_nodes']}P/{region_data['secondary_nodes']}S nodes)")
    
    # Test optimal region selection
    optimal_region = infrastructure.get_optimal_region()
    print(f"\n🎯 Optimal Region: {optimal_region}")
    
    # Stop monitoring
    await infrastructure.stop_monitoring()
    monitoring_task.cancel()
    
    print("\n✅ Global infrastructure testing completed!")

if __name__ == "__main__":
    asyncio.run(main())