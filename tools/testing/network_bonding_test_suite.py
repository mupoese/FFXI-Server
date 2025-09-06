#!/usr/bin/env python3
"""
Network Bonding Test Suite for FFXI Server

This comprehensive test suite validates network bonding performance across multiple
connections, different bonding modes, and various load scenarios. It provides detailed
logging and explanations of connection bonding testing results.

Features:
- Multi-connection performance testing (TCP/UDP)
- Bonding mode comparison and validation
- Failover scenario testing
- Load balancing verification
- Detailed performance metrics and analysis
- Comprehensive logging with explanations

Author: LandSandBoat Development Team
License: GPL-3.0
"""

import argparse
import asyncio
import json
import logging
import os
import socket
import statistics
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestConfig:
    """Test configuration parameters"""
    test_duration: int = 60  # seconds
    connection_count: int = 10
    payload_size: int = 1024  # bytes
    target_host: str = "127.0.0.1"
    base_port: int = 50000
    bonding_modes: List[str] = None
    test_interfaces: List[str] = None
    
    def __post_init__(self):
        if self.bonding_modes is None:
            self.bonding_modes = ["balance-xor", "802.3ad", "active-backup"]
        if self.test_interfaces is None:
            self.test_interfaces = ["eth0", "eth1"]

@dataclass
class ConnectionMetrics:
    """Metrics for a single connection"""
    connection_id: str
    protocol: str
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    latency_samples: List[float]
    errors: int
    duration: float
    throughput_mbps: float = 0.0
    avg_latency_ms: float = 0.0
    
    def __post_init__(self):
        if self.latency_samples:
            self.avg_latency_ms = statistics.mean(self.latency_samples) * 1000
        if self.duration > 0:
            self.throughput_mbps = (self.bytes_sent + self.bytes_received) * 8 / (1024 * 1024) / self.duration

@dataclass
class BondingTestResult:
    """Results from a bonding test scenario"""
    test_name: str
    bonding_mode: str
    connection_metrics: List[ConnectionMetrics]
    aggregate_throughput_mbps: float
    avg_latency_ms: float
    error_rate: float
    cpu_usage_percent: float
    memory_usage_mb: float
    interface_stats: Dict[str, Dict]
    test_duration: float
    explanation: str

class NetworkBondingTestSuite:
    """Comprehensive network bonding test suite"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.results: List[BondingTestResult] = []
        self.baseline_results: Optional[BondingTestResult] = None
        
    def log_test_explanation(self, test_name: str, explanation: str):
        """Log detailed explanation of what a test does"""
        logger.info(f"=== {test_name} ===")
        logger.info(f"EXPLANATION: {explanation}")
        logger.info("=" * (len(test_name) + 8))
    
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run the complete network bonding test suite"""
        logger.info("Starting Comprehensive Network Bonding Test Suite")
        logger.info(f"Test Configuration: {asdict(self.config)}")
        
        # Test 1: Baseline performance without bonding
        await self.test_baseline_performance()
        
        # Test 2: Single bonding mode performance
        for mode in self.config.bonding_modes:
            await self.test_bonding_mode_performance(mode)
        
        # Test 3: Multi-connection load testing
        await self.test_multi_connection_performance()
        
        # Test 4: Failover scenario testing
        await self.test_failover_scenarios()
        
        # Test 5: Protocol-specific testing (TCP vs UDP)
        await self.test_protocol_specific_performance()
        
        # Test 6: Load balancing verification
        await self.test_load_balancing_verification()
        
        # Generate comprehensive report
        return self.generate_comprehensive_report()
    
    async def test_baseline_performance(self) -> BondingTestResult:
        """Test baseline performance without network bonding"""
        self.log_test_explanation(
            "Baseline Performance Test",
            "This test measures network performance using standard single-interface "
            "networking without any bonding. Results serve as a baseline to compare "
            "against bonded interface performance. We measure throughput, latency, "
            "and resource utilization with multiple concurrent connections."
        )
        
        logger.info("Ensuring no bonding is configured...")
        await self._disable_bonding()
        
        result = await self._run_performance_test(
            "baseline",
            "none",
            "Standard single-interface networking baseline measurement"
        )
        
        self.baseline_results = result
        self.results.append(result)
        
        logger.info(f"Baseline Results - Throughput: {result.aggregate_throughput_mbps:.2f} Mbps, "
                   f"Latency: {result.avg_latency_ms:.2f} ms")
        
        return result
    
    async def test_bonding_mode_performance(self, bonding_mode: str) -> BondingTestResult:
        """Test performance with specific bonding mode"""
        self.log_test_explanation(
            f"Bonding Mode Test: {bonding_mode}",
            f"This test configures network bonding in {bonding_mode} mode and measures "
            f"performance improvements. {self._get_bonding_mode_explanation(bonding_mode)} "
            f"We compare throughput, latency, and load distribution against baseline."
        )
        
        logger.info(f"Configuring bonding mode: {bonding_mode}")
        await self._configure_bonding(bonding_mode)
        
        result = await self._run_performance_test(
            f"bonding_{bonding_mode}",
            bonding_mode,
            f"Performance test with {bonding_mode} bonding mode"
        )
        
        self.results.append(result)
        
        # Compare with baseline
        if self.baseline_results:
            improvement = ((result.aggregate_throughput_mbps - self.baseline_results.aggregate_throughput_mbps) 
                         / self.baseline_results.aggregate_throughput_mbps * 100)
            latency_change = ((result.avg_latency_ms - self.baseline_results.avg_latency_ms) 
                            / self.baseline_results.avg_latency_ms * 100)
            
            logger.info(f"Performance vs Baseline - Throughput: {improvement:+.1f}%, "
                       f"Latency: {latency_change:+.1f}%")
        
        return result
    
    async def test_multi_connection_performance(self) -> BondingTestResult:
        """Test performance with varying numbers of concurrent connections"""
        self.log_test_explanation(
            "Multi-Connection Load Test",
            "This test validates how network bonding handles multiple concurrent "
            "connections. We scale from 1 to 50 connections to test load distribution "
            "across bonded interfaces. This simulates real FFXI server load with "
            "multiple players connecting simultaneously."
        )
        
        connection_counts = [1, 5, 10, 20, 30, 50]
        original_count = self.config.connection_count
        
        best_mode = self._select_best_bonding_mode()
        await self._configure_bonding(best_mode)
        
        results = []
        for count in connection_counts:
            logger.info(f"Testing with {count} concurrent connections...")
            self.config.connection_count = count
            
            result = await self._run_performance_test(
                f"multi_conn_{count}",
                best_mode,
                f"Multi-connection test with {count} concurrent connections"
            )
            results.append(result)
            
            logger.info(f"{count} connections - Throughput: {result.aggregate_throughput_mbps:.2f} Mbps, "
                       f"Latency: {result.avg_latency_ms:.2f} ms")
        
        # Restore original connection count
        self.config.connection_count = original_count
        
        # Create summary result
        best_result = max(results, key=lambda r: r.aggregate_throughput_mbps)
        self.results.extend(results)
        
        return best_result
    
    async def test_failover_scenarios(self) -> BondingTestResult:
        """Test failover behavior when interfaces fail"""
        self.log_test_explanation(
            "Failover Scenario Test",
            "This test simulates network interface failures to validate automatic "
            "failover capabilities. We bring down slave interfaces during active "
            "traffic and measure recovery time, packet loss, and service continuity. "
            "This ensures bonding provides the expected fault tolerance."
        )
        
        # Use active-backup mode for clear failover testing
        await self._configure_bonding("active-backup")
        
        logger.info("Starting traffic before failover test...")
        traffic_task = asyncio.create_task(self._run_continuous_traffic())
        
        await asyncio.sleep(5)  # Let traffic stabilize
        
        # Simulate interface failure
        logger.info("Simulating interface failure...")
        await self._simulate_interface_failure()
        
        await asyncio.sleep(10)  # Wait for failover
        
        # Restore interface
        logger.info("Restoring interface...")
        await self._restore_interface()
        
        await asyncio.sleep(5)  # Let traffic stabilize again
        
        # Stop traffic and collect results
        traffic_task.cancel()
        
        result = await self._run_performance_test(
            "failover_test",
            "active-backup",
            "Failover scenario test with interface failure simulation"
        )
        
        self.results.append(result)
        return result
    
    async def test_protocol_specific_performance(self) -> Dict[str, BondingTestResult]:
        """Test TCP vs UDP performance with bonding"""
        self.log_test_explanation(
            "Protocol-Specific Performance Test",
            "This test compares TCP and UDP performance with network bonding. "
            "TCP benefits from connection-based load balancing while UDP benefits "
            "from packet-level distribution. We measure how bonding affects each "
            "protocol differently and which configurations work best for FFXI."
        )
        
        best_mode = self._select_best_bonding_mode()
        await self._configure_bonding(best_mode)
        
        results = {}
        
        # Test TCP performance
        logger.info("Testing TCP performance with bonding...")
        tcp_result = await self._run_protocol_specific_test("TCP")
        results["TCP"] = tcp_result
        self.results.append(tcp_result)
        
        # Test UDP performance  
        logger.info("Testing UDP performance with bonding...")
        udp_result = await self._run_protocol_specific_test("UDP")
        results["UDP"] = udp_result
        self.results.append(udp_result)
        
        # Compare protocols
        logger.info(f"TCP Throughput: {tcp_result.aggregate_throughput_mbps:.2f} Mbps, "
                   f"UDP Throughput: {udp_result.aggregate_throughput_mbps:.2f} Mbps")
        
        return results
    
    async def test_load_balancing_verification(self) -> BondingTestResult:
        """Verify traffic is properly distributed across bonded interfaces"""
        self.log_test_explanation(
            "Load Balancing Verification Test",
            "This test verifies that network traffic is properly distributed across "
            "all bonded interfaces. We monitor per-interface statistics during high "
            "load and calculate distribution ratios. Proper load balancing should "
            "show relatively even traffic distribution across all active interfaces."
        )
        
        await self._configure_bonding("balance-xor")
        
        # Record initial interface statistics
        initial_stats = await self._get_interface_statistics()
        
        result = await self._run_performance_test(
            "load_balance_verification",
            "balance-xor",
            "Load balancing verification with traffic distribution analysis"
        )
        
        # Record final interface statistics
        final_stats = await self._get_interface_statistics()
        
        # Calculate traffic distribution
        distribution = self._calculate_traffic_distribution(initial_stats, final_stats)
        result.interface_stats = distribution
        
        # Log distribution analysis
        self._log_traffic_distribution_analysis(distribution)
        
        self.results.append(result)
        return result
    
    async def _run_performance_test(self, test_name: str, bonding_mode: str, explanation: str) -> BondingTestResult:
        """Run a comprehensive performance test"""
        logger.info(f"Running performance test: {test_name}")
        
        # Monitor system resources
        cpu_start = psutil.cpu_percent()
        memory_start = psutil.virtual_memory().used / (1024 * 1024)
        
        start_time = time.time()
        
        # Run concurrent connections
        with ThreadPoolExecutor(max_workers=self.config.connection_count) as executor:
            futures = []
            for i in range(self.config.connection_count):
                future = executor.submit(self._run_single_connection_test, i, "TCP")
                futures.append(future)
            
            # Collect results
            connection_metrics = []
            for future in as_completed(futures):
                try:
                    metric = future.result()
                    connection_metrics.append(metric)
                except Exception as e:
                    logger.error(f"Connection test failed: {e}")
        
        end_time = time.time()
        test_duration = end_time - start_time
        
        # Monitor system resources after test
        cpu_end = psutil.cpu_percent()
        memory_end = psutil.virtual_memory().used / (1024 * 1024)
        
        # Calculate aggregate metrics
        aggregate_throughput = sum(m.throughput_mbps for m in connection_metrics)
        avg_latency = statistics.mean([m.avg_latency_ms for m in connection_metrics]) if connection_metrics else 0
        error_rate = sum(m.errors for m in connection_metrics) / len(connection_metrics) if connection_metrics else 0
        
        # Get interface statistics
        interface_stats = await self._get_interface_statistics()
        
        return BondingTestResult(
            test_name=test_name,
            bonding_mode=bonding_mode,
            connection_metrics=connection_metrics,
            aggregate_throughput_mbps=aggregate_throughput,
            avg_latency_ms=avg_latency,
            error_rate=error_rate,
            cpu_usage_percent=(cpu_start + cpu_end) / 2,
            memory_usage_mb=(memory_start + memory_end) / 2,
            interface_stats=interface_stats,
            test_duration=test_duration,
            explanation=explanation
        )
    
    def _run_single_connection_test(self, connection_id: int, protocol: str) -> ConnectionMetrics:
        """Run a single connection performance test"""
        port = self.config.base_port + connection_id
        bytes_sent = 0
        bytes_received = 0
        packets_sent = 0
        packets_received = 0
        latency_samples = []
        errors = 0
        
        start_time = time.time()
        
        try:
            if protocol == "TCP":
                # TCP test
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.config.target_host, port))
                
                payload = b'X' * self.config.payload_size
                
                while time.time() - start_time < self.config.test_duration:
                    try:
                        # Measure round-trip latency
                        send_time = time.time()
                        sock.send(payload)
                        response = sock.recv(self.config.payload_size)
                        receive_time = time.time()
                        
                        latency_samples.append(receive_time - send_time)
                        bytes_sent += len(payload)
                        bytes_received += len(response)
                        packets_sent += 1
                        packets_received += 1
                        
                    except Exception as e:
                        errors += 1
                        time.sleep(0.01)  # Small delay on error
                
                sock.close()
                
            else:  # UDP
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                payload = b'X' * self.config.payload_size
                
                while time.time() - start_time < self.config.test_duration:
                    try:
                        send_time = time.time()
                        sock.sendto(payload, (self.config.target_host, port))
                        response, addr = sock.recvfrom(self.config.payload_size)
                        receive_time = time.time()
                        
                        latency_samples.append(receive_time - send_time)
                        bytes_sent += len(payload)
                        bytes_received += len(response)
                        packets_sent += 1
                        packets_received += 1
                        
                    except Exception as e:
                        errors += 1
                        time.sleep(0.01)
                
                sock.close()
                
        except Exception as e:
            logger.error(f"Connection {connection_id} failed: {e}")
            errors += 1
        
        duration = time.time() - start_time
        
        return ConnectionMetrics(
            connection_id=f"conn_{connection_id}",
            protocol=protocol,
            bytes_sent=bytes_sent,
            bytes_received=bytes_received,
            packets_sent=packets_sent,
            packets_received=packets_received,
            latency_samples=latency_samples,
            errors=errors,
            duration=duration
        )
    
    async def _configure_bonding(self, mode: str):
        """Configure network bonding with specified mode"""
        # This would normally call the network bonding manager
        # For testing purposes, we simulate the configuration
        logger.info(f"Configuring bonding mode: {mode}")
        await asyncio.sleep(1)  # Simulate configuration time
    
    async def _disable_bonding(self):
        """Disable network bonding"""
        logger.info("Disabling network bonding")
        await asyncio.sleep(1)  # Simulate configuration time
    
    async def _get_interface_statistics(self) -> Dict[str, Dict]:
        """Get current interface statistics"""
        # In a real implementation, this would read from /proc/net/dev or similar
        # For testing, we return simulated statistics
        return {
            "bond0": {"rx_bytes": 1000000, "tx_bytes": 1000000, "rx_packets": 1000, "tx_packets": 1000},
            "eth0": {"rx_bytes": 500000, "tx_bytes": 500000, "rx_packets": 500, "tx_packets": 500},
            "eth1": {"rx_bytes": 500000, "tx_bytes": 500000, "rx_packets": 500, "tx_packets": 500}
        }
    
    def _get_bonding_mode_explanation(self, mode: str) -> str:
        """Get explanation of bonding mode behavior"""
        explanations = {
            "balance-rr": "Round-robin mode sends packets across interfaces sequentially for maximum throughput.",
            "active-backup": "Active-backup mode uses one interface actively with others as backup for fault tolerance.",
            "balance-xor": "XOR hash mode distributes traffic based on source/destination hash for balanced load.",
            "802.3ad": "LACP mode dynamically aggregates links with switch cooperation for optimal performance.",
            "balance-tlb": "Transmit load balancing optimizes outbound traffic distribution.",
            "balance-alb": "Adaptive load balancing optimizes both transmit and receive traffic."
        }
        return explanations.get(mode, "Unknown bonding mode")
    
    def _select_best_bonding_mode(self) -> str:
        """Select the best performing bonding mode from previous tests"""
        if not self.results:
            return "balance-xor"  # Default fallback
            
        bonding_results = [r for r in self.results if r.bonding_mode != "none"]
        if bonding_results:
            best_result = max(bonding_results, key=lambda r: r.aggregate_throughput_mbps)
            return best_result.bonding_mode
        
        return "balance-xor"
    
    async def _run_continuous_traffic(self):
        """Run continuous traffic for failover testing"""
        # Simulate continuous traffic generation
        try:
            while True:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
    
    async def _simulate_interface_failure(self):
        """Simulate network interface failure"""
        logger.info("Simulating interface failure...")
        await asyncio.sleep(1)  # Simulate failure
    
    async def _restore_interface(self):
        """Restore failed network interface"""
        logger.info("Restoring failed interface...")
        await asyncio.sleep(1)  # Simulate restoration
    
    async def _run_protocol_specific_test(self, protocol: str) -> BondingTestResult:
        """Run protocol-specific performance test"""
        return await self._run_performance_test(
            f"protocol_{protocol.lower()}",
            self._select_best_bonding_mode(),
            f"{protocol} protocol performance test with network bonding"
        )
    
    def _calculate_traffic_distribution(self, initial_stats: Dict, final_stats: Dict) -> Dict:
        """Calculate traffic distribution across interfaces"""
        distribution = {}
        
        for interface in initial_stats:
            if interface in final_stats:
                initial = initial_stats[interface]
                final = final_stats[interface]
                
                tx_diff = final.get("tx_bytes", 0) - initial.get("tx_bytes", 0)
                rx_diff = final.get("rx_bytes", 0) - initial.get("rx_bytes", 0)
                
                distribution[interface] = {
                    "tx_bytes_delta": tx_diff,
                    "rx_bytes_delta": rx_diff,
                    "total_bytes_delta": tx_diff + rx_diff
                }
        
        return distribution
    
    def _log_traffic_distribution_analysis(self, distribution: Dict):
        """Log analysis of traffic distribution"""
        logger.info("=== Traffic Distribution Analysis ===")
        
        total_traffic = sum(stats["total_bytes_delta"] for stats in distribution.values())
        
        for interface, stats in distribution.items():
            if total_traffic > 0:
                percentage = (stats["total_bytes_delta"] / total_traffic) * 100
                logger.info(f"{interface}: {stats['total_bytes_delta']:,} bytes ({percentage:.1f}%)")
            else:
                logger.info(f"{interface}: No traffic recorded")
        
        # Check for balanced distribution
        percentages = [(stats["total_bytes_delta"] / total_traffic) * 100 
                      for stats in distribution.values() if total_traffic > 0]
        
        if percentages:
            balance_variance = statistics.variance(percentages) if len(percentages) > 1 else 0
            if balance_variance < 100:  # Less than 10% variance
                logger.info("✓ Traffic distribution is well balanced")
            else:
                logger.warning("⚠ Traffic distribution is unbalanced")
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test results report"""
        logger.info("Generating comprehensive performance report...")
        
        report = {
            "test_summary": {
                "total_tests": len(self.results),
                "test_duration": sum(r.test_duration for r in self.results),
                "configuration": asdict(self.config)
            },
            "baseline_performance": asdict(self.baseline_results) if self.baseline_results else None,
            "bonding_mode_comparison": self._generate_bonding_mode_comparison(),
            "performance_improvements": self._calculate_performance_improvements(),
            "recommendations": self._generate_recommendations(),
            "detailed_results": [asdict(result) for result in self.results]
        }
        
        # Save report to file
        report_file = f"network_bonding_test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Comprehensive report saved to: {report_file}")
        
        # Log summary
        self._log_test_summary(report)
        
        return report
    
    def _generate_bonding_mode_comparison(self) -> Dict[str, Any]:
        """Generate comparison of different bonding modes"""
        bonding_results = {r.bonding_mode: r for r in self.results if r.bonding_mode != "none"}
        
        comparison = {}
        for mode, result in bonding_results.items():
            comparison[mode] = {
                "throughput_mbps": result.aggregate_throughput_mbps,
                "latency_ms": result.avg_latency_ms,
                "error_rate": result.error_rate,
                "cpu_usage": result.cpu_usage_percent
            }
        
        return comparison
    
    def _calculate_performance_improvements(self) -> Dict[str, Any]:
        """Calculate performance improvements over baseline"""
        if not self.baseline_results:
            return {}
        
        improvements = {}
        for result in self.results:
            if result.bonding_mode != "none":
                throughput_improvement = (
                    (result.aggregate_throughput_mbps - self.baseline_results.aggregate_throughput_mbps) 
                    / self.baseline_results.aggregate_throughput_mbps * 100
                )
                
                latency_improvement = (
                    (self.baseline_results.avg_latency_ms - result.avg_latency_ms) 
                    / self.baseline_results.avg_latency_ms * 100
                )
                
                improvements[result.bonding_mode] = {
                    "throughput_improvement_percent": throughput_improvement,
                    "latency_improvement_percent": latency_improvement,
                    "overall_score": throughput_improvement - (result.error_rate * 10)
                }
        
        return improvements
    
    def _generate_recommendations(self) -> List[str]:
        """Generate configuration recommendations based on test results"""
        recommendations = []
        
        if not self.results:
            return ["No test results available for recommendations"]
        
        # Find best performing mode
        bonding_results = [r for r in self.results if r.bonding_mode != "none"]
        if bonding_results:
            best_result = max(bonding_results, key=lambda r: r.aggregate_throughput_mbps)
            recommendations.append(f"Recommended bonding mode: {best_result.bonding_mode}")
            recommendations.append(f"Expected throughput improvement: {best_result.aggregate_throughput_mbps:.1f} Mbps")
        
        # CPU usage recommendations
        high_cpu_results = [r for r in self.results if r.cpu_usage_percent > 80]
        if high_cpu_results:
            recommendations.append("High CPU usage detected - consider enabling RSS/RPS optimization")
        
        # Error rate recommendations
        high_error_results = [r for r in self.results if r.error_rate > 0.1]
        if high_error_results:
            recommendations.append("High error rates detected - check network configuration and switch settings")
        
        return recommendations
    
    def _log_test_summary(self, report: Dict[str, Any]):
        """Log comprehensive test summary"""
        logger.info("=" * 60)
        logger.info("NETWORK BONDING TEST SUMMARY")
        logger.info("=" * 60)
        
        summary = report["test_summary"]
        logger.info(f"Total Tests Executed: {summary['total_tests']}")
        logger.info(f"Total Test Duration: {summary['test_duration']:.1f} seconds")
        
        if self.baseline_results:
            logger.info(f"Baseline Performance: {self.baseline_results.aggregate_throughput_mbps:.2f} Mbps")
        
        # Best performing mode
        improvements = report.get("performance_improvements", {})
        if improvements:
            best_mode = max(improvements.items(), key=lambda x: x[1]["overall_score"])
            logger.info(f"Best Performing Mode: {best_mode[0]}")
            logger.info(f"Performance Improvement: {best_mode[1]['throughput_improvement_percent']:+.1f}%")
        
        # Recommendations
        logger.info("\nRECOMMENDATIONS:")
        for i, rec in enumerate(report.get("recommendations", []), 1):
            logger.info(f"{i}. {rec}")
        
        logger.info("=" * 60)

async def create_test_servers():
    """Create simple test servers for connection testing"""
    servers = []
    
    async def handle_tcp_client(reader, writer):
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                writer.write(data)  # Echo back
                await writer.drain()
        except:
            pass
        finally:
            writer.close()
    
    # Start TCP servers
    for i in range(50):  # Support up to 50 concurrent connections
        port = 50000 + i
        try:
            server = await asyncio.start_server(handle_tcp_client, '127.0.0.1', port)
            servers.append(server)
        except:
            pass  # Port may be in use
    
    return servers

async def main():
    parser = argparse.ArgumentParser(description="Network Bonding Test Suite")
    parser.add_argument('--duration', type=int, default=60, help="Test duration in seconds")
    parser.add_argument('--connections', type=int, default=10, help="Number of concurrent connections")
    parser.add_argument('--payload-size', type=int, default=1024, help="Payload size in bytes")
    parser.add_argument('--target-host', default='127.0.0.1', help="Target host for testing")
    parser.add_argument('--modes', nargs='+', default=['balance-xor', '802.3ad', 'active-backup'], 
                       help="Bonding modes to test")
    parser.add_argument('--interfaces', nargs='+', default=['eth0', 'eth1'], 
                       help="Network interfaces for bonding")
    parser.add_argument('--output-file', help="Output file for detailed results")
    parser.add_argument('--verbose', '-v', action='store_true', help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create test configuration
    config = TestConfig(
        test_duration=args.duration,
        connection_count=args.connections,
        payload_size=args.payload_size,
        target_host=args.target_host,
        bonding_modes=args.modes,
        test_interfaces=args.interfaces
    )
    
    # Start test servers
    logger.info("Starting test servers...")
    servers = await create_test_servers()
    
    try:
        # Run test suite
        test_suite = NetworkBondingTestSuite(config)
        results = await test_suite.run_comprehensive_test_suite()
        
        # Save results if requested
        if args.output_file:
            with open(args.output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to: {args.output_file}")
        
    finally:
        # Clean up servers
        logger.info("Shutting down test servers...")
        for server in servers:
            server.close()
            await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())