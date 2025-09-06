#!/usr/bin/env python3
"""
FFXI Server Comprehensive System Testing Framework
Tests load balancing, multi-instance support, and network bonding
"""

import os
import sys
import time
import json
import asyncio
import socket
import threading
import subprocess
import concurrent.futures
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FFXISystemTester:
    """Comprehensive testing framework for FFXI server system"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.test_config = {
            'timeout': 30,
            'max_concurrent_connections': 100,
            'load_test_duration': 60,
            'ports': {
                'LOGIN_VIEW_PORT': 54001,
                'LOGIN_DATA_PORT': 54230,
                'LOGIN_AUTH_PORT': 54231,
                'LOGIN_CONF_PORT': 51220,
                'SEARCH_PORT': 54002,
                'ZMQ_PORT': 54003,
                'HTTP_PORT': 8088,
                'API_PORT': 5000,
                'HAPROXY_STATS': 8404
            }
        }
    
    def log_test_result(self, test_name: str, status: str, details: Dict[str, Any] = None):
        """Log test result"""
        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'test_name': test_name,
            'status': status,
            'details': details or {}
        }
        self.test_results.append(result)
        
        if status == 'PASS':
            logger.info(f"✓ {test_name}")
        elif status == 'FAIL':
            logger.error(f"✗ {test_name}: {details}")
        else:
            logger.warning(f"⚠ {test_name}: {status}")
    
    def check_port_connectivity(self, host: str, port: int, timeout: int = 5) -> bool:
        """Check if a port is accessible"""
        try:
            with socket.create_connection((host, port), timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False
    
    def test_basic_connectivity(self) -> bool:
        """Test basic port connectivity"""
        logger.info("Starting basic connectivity tests...")
        
        all_passed = True
        for port_name, port_num in self.test_config['ports'].items():
            if self.check_port_connectivity('localhost', port_num):
                self.log_test_result(f"Port Connectivity - {port_name}:{port_num}", "PASS")
            else:
                self.log_test_result(f"Port Connectivity - {port_name}:{port_num}", "FAIL", 
                                   {"port": port_num, "error": "Connection refused"})
                all_passed = False
        
        return all_passed
    
    def test_docker_containers(self) -> bool:
        """Test Docker container health"""
        logger.info("Testing Docker container health...")
        
        expected_containers = [
            'ffxi-database',
            'ffxi-load-balancer', 
            'ffxi-server-1',
            'ffxi-api'
        ]
        
        all_passed = True
        
        for container in expected_containers:
            try:
                result = subprocess.run(
                    ['docker', 'ps', '--filter', f'name={container}', '--format', '{{.Status}}'],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0 and 'Up' in result.stdout:
                    self.log_test_result(f"Container Health - {container}", "PASS")
                    
                    # Check container health status
                    health_result = subprocess.run(
                        ['docker', 'inspect', '--format', '{{.State.Health.Status}}', container],
                        capture_output=True, text=True, timeout=10
                    )
                    
                    if health_result.returncode == 0:
                        health_status = health_result.stdout.strip()
                        if health_status in ['healthy', '']:  # Empty means no healthcheck
                            self.log_test_result(f"Container Healthcheck - {container}", "PASS")
                        else:
                            self.log_test_result(f"Container Healthcheck - {container}", "FAIL",
                                               {"health_status": health_status})
                            all_passed = False
                    
                else:
                    self.log_test_result(f"Container Health - {container}", "FAIL",
                                       {"error": "Container not running"})
                    all_passed = False
                    
            except Exception as e:
                self.log_test_result(f"Container Health - {container}", "FAIL",
                                   {"error": str(e)})
                all_passed = False
        
        return all_passed
    
    def test_database_connectivity(self) -> bool:
        """Test database connectivity and performance"""
        logger.info("Testing database connectivity...")
        
        try:
            import mysql.connector
            
            config = {
                'host': 'localhost',
                'port': 3306,
                'user': os.environ.get('MYSQL_USER', 'xiuser'),
                'password': os.environ.get('MYSQL_PASSWORD', 'xiserver_2024'),
                'database': os.environ.get('MYSQL_DATABASE', 'xidb'),
                'connection_timeout': 10
            }
            
            # Test basic connection
            conn = mysql.connector.connect(**config)
            self.log_test_result("Database Connection", "PASS")
            
            # Test query performance
            cursor = conn.cursor()
            start_time = time.time()
            cursor.execute("SELECT 1")
            query_time = time.time() - start_time
            
            if query_time < 1.0:  # Should be much faster than 1 second
                self.log_test_result("Database Query Performance", "PASS", 
                                   {"query_time_ms": query_time * 1000})
            else:
                self.log_test_result("Database Query Performance", "FAIL",
                                   {"query_time_ms": query_time * 1000})
                return False
            
            # Test connection pool
            start_time = time.time()
            for i in range(10):
                test_conn = mysql.connector.connect(**config)
                test_conn.close()
            pool_time = time.time() - start_time
            
            self.log_test_result("Database Connection Pool", "PASS",
                               {"pool_test_time_ms": pool_time * 1000})
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            self.log_test_result("Database Connection", "FAIL", {"error": str(e)})
            return False
    
    def test_load_balancer(self) -> bool:
        """Test HAProxy load balancer functionality"""
        logger.info("Testing load balancer...")
        
        try:
            import requests
            
            # Test HAProxy stats page
            response = requests.get('http://localhost:8404/stats', timeout=10)
            if response.status_code == 200:
                self.log_test_result("Load Balancer Stats Page", "PASS")
            else:
                self.log_test_result("Load Balancer Stats Page", "FAIL",
                                   {"status_code": response.status_code})
                return False
            
            # Test load balancing across multiple requests
            login_responses = []
            for i in range(10):
                if self.check_port_connectivity('localhost', 54001):
                    login_responses.append(True)
                else:
                    login_responses.append(False)
                time.sleep(0.1)
            
            success_rate = sum(login_responses) / len(login_responses)
            if success_rate >= 0.8:  # 80% success rate
                self.log_test_result("Load Balancer Distribution", "PASS",
                                   {"success_rate": success_rate})
            else:
                self.log_test_result("Load Balancer Distribution", "FAIL",
                                   {"success_rate": success_rate})
                return False
            
            return True
            
        except Exception as e:
            self.log_test_result("Load Balancer Test", "FAIL", {"error": str(e)})
            return False
    
    def test_api_functionality(self) -> bool:
        """Test FFXI Management API"""
        logger.info("Testing API functionality...")
        
        try:
            import requests
            
            # Test health endpoint
            response = requests.get('http://localhost:5000/health', timeout=10)
            if response.status_code == 200:
                self.log_test_result("API Health Endpoint", "PASS")
            else:
                self.log_test_result("API Health Endpoint", "FAIL",
                                   {"status_code": response.status_code})
                return False
            
            # Test authentication
            auth_data = {
                'username': 'admin',
                'password': os.environ.get('FFXI_API_SECRET_KEY', 'your_secret_key_here_change_this')
            }
            
            auth_response = requests.post('http://localhost:5000/auth/token', 
                                        json=auth_data, timeout=10)
            
            if auth_response.status_code == 200:
                token_data = auth_response.json()
                token = token_data.get('token')
                self.log_test_result("API Authentication", "PASS")
                
                # Test authenticated endpoint
                headers = {'Authorization': f'Bearer {token}'}
                status_response = requests.get('http://localhost:5000/api/status',
                                             headers=headers, timeout=10)
                
                if status_response.status_code == 200:
                    self.log_test_result("API Authenticated Endpoint", "PASS")
                else:
                    self.log_test_result("API Authenticated Endpoint", "FAIL",
                                       {"status_code": status_response.status_code})
                    return False
            else:
                self.log_test_result("API Authentication", "FAIL",
                                   {"status_code": auth_response.status_code})
                return False
            
            return True
            
        except Exception as e:
            self.log_test_result("API Test", "FAIL", {"error": str(e)})
            return False
    
    async def simulate_client_connection(self, host: str, port: int, duration: int = 5) -> bool:
        """Simulate a client connection for load testing"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), 
                timeout=10
            )
            
            # Hold connection for specified duration
            await asyncio.sleep(duration)
            
            writer.close()
            await writer.wait_closed()
            return True
            
        except Exception:
            return False
    
    def test_concurrent_connections(self) -> bool:
        """Test concurrent connection handling"""
        logger.info("Testing concurrent connections...")
        
        async def run_concurrent_test():
            tasks = []
            num_connections = min(50, self.test_config['max_concurrent_connections'])
            
            for i in range(num_connections):
                task = self.simulate_client_connection('localhost', 54001, 2)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful_connections = sum(1 for r in results if r is True)
            
            success_rate = successful_connections / num_connections
            return success_rate
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success_rate = loop.run_until_complete(run_concurrent_test())
            loop.close()
            
            if success_rate >= 0.7:  # 70% success rate for concurrent connections
                self.log_test_result("Concurrent Connections", "PASS",
                                   {"success_rate": success_rate, "connections": 50})
            else:
                self.log_test_result("Concurrent Connections", "FAIL",
                                   {"success_rate": success_rate, "connections": 50})
                return False
            
            return True
            
        except Exception as e:
            self.log_test_result("Concurrent Connections", "FAIL", {"error": str(e)})
            return False
    
    def test_multi_instance_support(self) -> bool:
        """Test multiple server instance support"""
        logger.info("Testing multi-instance support...")
        
        try:
            # Check if multiple server instances are configured
            containers = ['ffxi-server-1', 'ffxi-server-2', 'ffxi-server-3']
            running_instances = []
            
            for container in containers:
                result = subprocess.run(
                    ['docker', 'ps', '--filter', f'name={container}', '--format', '{{.Names}}'],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0 and container in result.stdout:
                    running_instances.append(container)
            
            if len(running_instances) >= 1:
                self.log_test_result("Multi-Instance Support", "PASS",
                                   {"running_instances": len(running_instances), 
                                    "instances": running_instances})
            else:
                self.log_test_result("Multi-Instance Support", "FAIL",
                                   {"running_instances": len(running_instances)})
                return False
            
            return True
            
        except Exception as e:
            self.log_test_result("Multi-Instance Support", "FAIL", {"error": str(e)})
            return False
    
    def test_windower_ashita_compatibility(self) -> bool:
        """Test compatibility settings for Windower and Ashita"""
        logger.info("Testing Windower/Ashita compatibility...")
        
        try:
            import requests
            
            # Get authentication token first
            auth_data = {
                'username': 'admin',
                'password': os.environ.get('FFXI_API_SECRET_KEY', 'your_secret_key_here_change_this')
            }
            
            auth_response = requests.post('http://localhost:5000/auth/token', 
                                        json=auth_data, timeout=10)
            
            if auth_response.status_code != 200:
                self.log_test_result("Compatibility Test - Auth", "FAIL")
                return False
            
            token = auth_response.json().get('token')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test Windower compatibility
            windower_response = requests.get('http://localhost:5000/api/compatibility/windower',
                                           headers=headers, timeout=10)
            
            if windower_response.status_code == 200:
                windower_data = windower_response.json()
                if windower_data.get('compatible'):
                    self.log_test_result("Windower Compatibility", "PASS")
                else:
                    self.log_test_result("Windower Compatibility", "FAIL",
                                       {"data": windower_data})
                    return False
            else:
                self.log_test_result("Windower Compatibility", "FAIL",
                                   {"status_code": windower_response.status_code})
                return False
            
            # Test Ashita compatibility
            ashita_response = requests.get('http://localhost:5000/api/compatibility/ashita',
                                         headers=headers, timeout=10)
            
            if ashita_response.status_code == 200:
                ashita_data = ashita_response.json()
                if ashita_data.get('compatible'):
                    self.log_test_result("Ashita Compatibility", "PASS")
                else:
                    self.log_test_result("Ashita Compatibility", "FAIL",
                                       {"data": ashita_data})
                    return False
            else:
                self.log_test_result("Ashita Compatibility", "FAIL",
                                   {"status_code": ashita_response.status_code})
                return False
            
            return True
            
        except Exception as e:
            self.log_test_result("Compatibility Test", "FAIL", {"error": str(e)})
            return False
    
    def test_network_bonding(self) -> bool:
        """Test network bonding configuration"""
        logger.info("Testing network bonding configuration...")
        
        try:
            # Check if bonding is configured (this is mostly configuration validation)
            bonding_enabled = os.environ.get('FFXI_ENABLE_BONDING', 'false').lower() == 'true'
            
            if bonding_enabled:
                # Test bonding configuration through API
                import requests
                
                auth_data = {
                    'username': 'admin',
                    'password': os.environ.get('FFXI_API_SECRET_KEY', 'your_secret_key_here_change_this')
                }
                
                auth_response = requests.post('http://localhost:5000/auth/token', 
                                            json=auth_data, timeout=10)
                
                if auth_response.status_code == 200:
                    token = auth_response.json().get('token')
                    headers = {'Authorization': f'Bearer {token}'}
                    
                    bonding_data = {
                        'interfaces': ['eth0', 'eth1'],
                        'mode': 'balance-xor'
                    }
                    
                    bonding_response = requests.post('http://localhost:5000/api/bonding/configure',
                                                   json=bonding_data, headers=headers, timeout=10)
                    
                    if bonding_response.status_code == 200:
                        self.log_test_result("Network Bonding Configuration", "PASS")
                    else:
                        self.log_test_result("Network Bonding Configuration", "FAIL",
                                           {"status_code": bonding_response.status_code})
                        return False
                else:
                    self.log_test_result("Network Bonding - Auth", "FAIL")
                    return False
            else:
                self.log_test_result("Network Bonding Configuration", "SKIP",
                                   {"reason": "Bonding not enabled"})
            
            return True
            
        except Exception as e:
            self.log_test_result("Network Bonding Test", "FAIL", {"error": str(e)})
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        skipped_tests = len([r for r in self.test_results if r['status'] == 'SKIP'])
        
        duration = time.time() - self.start_time if self.start_time else 0
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'skipped': skipped_tests,
                'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
                'duration_seconds': duration,
                'timestamp': datetime.utcnow().isoformat()
            },
            'test_results': self.test_results,
            'recommendations': []
        }
        
        # Add recommendations based on results
        if failed_tests > 0:
            report['recommendations'].append("Some tests failed. Check failed test details and container logs.")
        
        if report['summary']['success_rate'] < 0.8:
            report['recommendations'].append("Success rate is below 80%. Consider investigating system performance.")
        
        return report
    
    def run_comprehensive_test(self) -> bool:
        """Run all tests and return overall success"""
        logger.info("Starting comprehensive FFXI server system test...")
        self.start_time = time.time()
        
        test_functions = [
            self.test_basic_connectivity,
            self.test_docker_containers,
            self.test_database_connectivity,
            self.test_load_balancer,
            self.test_api_functionality,
            self.test_concurrent_connections,
            self.test_multi_instance_support,
            self.test_windower_ashita_compatibility,
            self.test_network_bonding
        ]
        
        overall_success = True
        
        for test_func in test_functions:
            try:
                success = test_func()
                if not success:
                    overall_success = False
            except Exception as e:
                logger.error(f"Test {test_func.__name__} crashed: {e}")
                self.log_test_result(test_func.__name__, "FAIL", {"error": str(e)})
                overall_success = False
        
        # Generate and save report
        report = self.generate_report()
        
        with open('/tmp/ffxi_system_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test completed. Report saved to /tmp/ffxi_system_test_report.json")
        logger.info(f"Summary: {report['summary']['passed']}/{report['summary']['total_tests']} tests passed")
        
        return overall_success


def main():
    """Main function"""
    print("FFXI Server Comprehensive System Test")
    print("====================================")
    
    tester = FFXISystemTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed. Check the report for details.")
        return 1


if __name__ == '__main__':
    sys.exit(main())