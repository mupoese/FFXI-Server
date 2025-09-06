#!/usr/bin/env python3
"""
Comprehensive Test Suite for Launcher Communication System
Tests compiler, launcher, and server communication with URL fallback
"""

import os
import sys
import json
import time
import tempfile
import subprocess
import requests
import shutil
from pathlib import Path
from typing import Dict, Any, List
import threading
import socket


class LauncherCommunicationTester:
    """Test suite for launcher communication system"""
    
    def __init__(self):
        self.test_results = []
        self.server_process = None
        self.test_env_file = None
        
    def log_test(self, test_name: str, success: bool, message: str = "", details: Dict = None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': time.time()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if details:
            for key, value in details.items():
                print(f"  - {key}: {value}")
    
    def create_test_env(self) -> str:
        """Create test .env file with URL configuration"""
        test_config = """# Test Configuration for Launcher Communication
SERVERNAME=TestServer
TESTSERVER_SERVER_NAME=Test Server
TESTSERVER_SERVER_HOST=localhost
TESTSERVER_LOGIN_PORT=54001
TESTSERVER_MAP_PORT=54230
TESTSERVER_SEARCH_PORT=54002
TESTSERVER_ADMIN_USERNAME=testadmin
TESTSERVER_ADMIN_PASSWORD=testpass123
TESTSERVER_API_SECRET_KEY=test_secret_key_12345
TESTSERVER_SERVER_URL=http://localhost:5000
TESTSERVER_API_BASE_URL=http://localhost:5000/api
TESTSERVER_SERVER_IPV4=127.0.0.1
TESTSERVER_SERVER_IPV6=::1
TESTSERVER_API_PORT=5000
TESTSERVER_WEB_PORT=80
TESTSERVER_WINDOWER_COMPATIBLE=true
TESTSERVER_ASHITA_COMPATIBLE=true
TESTSERVER_AUTO_UPDATE=true
TESTSERVER_CLIENT_TIMEOUT=30000
"""
        
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(test_config)
            self.test_env_file = f.name
        
        return self.test_env_file
    
    def test_env_file_loading(self) -> bool:
        """Test environment file loading"""
        try:
            env_file = self.create_test_env()
            
            # Import the launcher module to test config loading
            sys.path.insert(0, 'tools')
            from enhanced_ffxi_launcher import ServerConfig
            
            config = ServerConfig(env_file)
            
            # Verify configuration loading
            assert config.server_name == 'TestServer'
            assert config.get('SERVER_NAME') == 'Test Server'
            assert config.get('SERVER_URL') == 'http://localhost:5000'
            assert config.get('SERVER_IPV4') == '127.0.0.1'
            assert config.get('SERVER_IPV6') == '::1'
            
            self.log_test("Environment File Loading", True, 
                         "Successfully loaded test configuration", {
                             'server_name': config.server_name,
                             'server_url': config.get('SERVER_URL'),
                             'ipv4_fallback': config.get('SERVER_IPV4'),
                             'ipv6_fallback': config.get('SERVER_IPV6')
                         })
            return True
            
        except Exception as e:
            self.log_test("Environment File Loading", False, str(e))
            return False
    
    def test_build_launcher(self) -> bool:
        """Test launcher build process"""
        try:
            # Run the enhanced build launcher script
            result = subprocess.run([
                sys.executable, 'tools/enhanced_build_launcher.py'
            ], capture_output=True, text=True, timeout=300)
            
            success = result.returncode == 0
            output_dir = Path('launcher_build')
            
            # Check if build artifacts were created
            expected_files = [
                'testserver_launcher.py',
                'testserver_launcher.spec'
            ]
            
            artifacts_found = []
            for file in expected_files:
                if (output_dir / file).exists():
                    artifacts_found.append(file)
            
            if success and artifacts_found:
                self.log_test("Launcher Build Process", True,
                             "Build completed successfully", {
                                 'build_artifacts': artifacts_found,
                                 'output_directory': str(output_dir),
                                 'server_name': 'TestServer'
                             })
            else:
                self.log_test("Launcher Build Process", False,
                             "Build failed or missing artifacts", {
                                 'returncode': result.returncode,
                                 'stdout': result.stdout[:500],
                                 'stderr': result.stderr[:500],
                                 'artifacts_found': artifacts_found
                             })
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            self.log_test("Launcher Build Process", False, "Build process timed out")
            return False
        except Exception as e:
            self.log_test("Launcher Build Process", False, str(e))
            return False
    
    def test_api_server_startup(self) -> bool:
        """Test API server startup"""
        try:
            # Start the API server in background
            env = os.environ.copy()
            env.update({
                'SERVERNAME': 'TestServer',
                'TESTSERVER_API_PORT': '5000',
                'TESTSERVER_ADMIN_USERNAME': 'testadmin',
                'TESTSERVER_ADMIN_PASSWORD': 'testpass123'
            })
            
            # Start server process
            self.server_process = subprocess.Popen([
                sys.executable, 'web/api/app.py'
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            time.sleep(3)
            
            # Test health endpoint
            response = requests.get('http://localhost:5000/health', timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Server Startup", True,
                             "Server started successfully", {
                                 'status': data.get('status'),
                                 'service': data.get('service'),
                                 'port': '5000'
                             })
                return True
            else:
                self.log_test("API Server Startup", False,
                             f"Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("API Server Startup", False, str(e))
            return False
    
    def test_authentication(self) -> bool:
        """Test authentication with API server"""
        try:
            # Test authentication
            auth_response = requests.post('http://localhost:5000/auth/token', 
                                        json={
                                            'username': 'testadmin',
                                            'password': 'testpass123'
                                        }, timeout=10)
            
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                token = auth_data.get('token')
                
                if token:
                    self.log_test("Authentication Test", True,
                                 "Authentication successful", {
                                     'token_received': True,
                                     'token_length': len(token)
                                 })
                    return token
                else:
                    self.log_test("Authentication Test", False, "No token received")
                    return False
            else:
                self.log_test("Authentication Test", False,
                             f"Authentication failed: {auth_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Test", False, str(e))
            return False
    
    def test_api_endpoints(self, token: str) -> bool:
        """Test various API endpoints"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            endpoints = [
                ('/api/status', 'Server Status'),
                ('/api/ports', 'Port Configuration'),
                ('/api/dashboard/metrics', 'Dashboard Metrics'),
                ('/api/compatibility/ashita', 'Ashita Compatibility'),
                ('/api/compatibility/windower', 'Windower Compatibility')
            ]
            
            successful_endpoints = []
            failed_endpoints = []
            
            for endpoint, name in endpoints:
                try:
                    response = requests.get(f'http://localhost:5000{endpoint}', 
                                          headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        successful_endpoints.append(name)
                    else:
                        failed_endpoints.append(f"{name} ({response.status_code})")
                        
                except Exception as e:
                    failed_endpoints.append(f"{name} (error)")
            
            success = len(successful_endpoints) > len(failed_endpoints)
            
            self.log_test("API Endpoints Test", success,
                         f"Tested {len(endpoints)} endpoints", {
                             'successful': successful_endpoints,
                             'failed': failed_endpoints
                         })
            
            return success
            
        except Exception as e:
            self.log_test("API Endpoints Test", False, str(e))
            return False
    
    def test_heartbeat_communication(self, token: str) -> bool:
        """Test launcher heartbeat communication"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            heartbeat_data = {
                'launcher_version': '2.0.0',
                'timestamp': time.time(),
                'server_name': 'TestServer'
            }
            
            response = requests.post('http://localhost:5000/api/launcher/heartbeat',
                                   headers=headers, json=heartbeat_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Heartbeat Communication", True,
                             "Heartbeat communication successful", {
                                 'server_response': data.get('status'),
                                 'server_time': data.get('server_time'),
                                 'launcher_compatible': data.get('launcher_compatible')
                             })
                return True
            else:
                self.log_test("Heartbeat Communication", False,
                             f"Heartbeat failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Heartbeat Communication", False, str(e))
            return False
    
    def test_url_fallback(self) -> bool:
        """Test URL fallback functionality"""
        try:
            sys.path.insert(0, 'tools')
            from enhanced_ffxi_launcher import ServerConfig, ServerAPIClient
            
            # Create config with multiple URLs
            config = ServerConfig(self.test_env_file)
            client = ServerAPIClient(config)
            
            # Test URL determination
            base_url = client._determine_server_url()
            
            # Test connection to each fallback URL
            test_urls = [
                config.get('SERVER_URL'),
                f"http://{config.get('SERVER_IPV4')}:{config.get('API_PORT')}",
                f"http://[{config.get('SERVER_IPV6')}]:{config.get('API_PORT')}"
            ]
            
            working_urls = []
            for url in test_urls:
                if client._test_connection(url):
                    working_urls.append(url)
            
            self.log_test("URL Fallback Test", len(working_urls) > 0,
                         f"Found {len(working_urls)} working URLs", {
                             'base_url': base_url,
                             'working_urls': working_urls,
                             'test_urls': test_urls
                         })
            
            return len(working_urls) > 0
            
        except Exception as e:
            self.log_test("URL Fallback Test", False, str(e))
            return False
    
    def test_launcher_api_integration(self) -> bool:
        """Test full launcher-API integration"""
        try:
            sys.path.insert(0, 'tools')
            from enhanced_ffxi_launcher import ServerConfig, ServerAPIClient
            
            config = ServerConfig(self.test_env_file)
            client = ServerAPIClient(config)
            
            # Test authentication
            auth_result = client.authenticate('testadmin', 'testpass123')
            
            if not auth_result['success']:
                self.log_test("Launcher API Integration", False,
                             "Authentication failed", auth_result)
                return False
            
            # Test server status
            status_result = client.get_server_status()
            server_config_result = client.get_server_config()
            heartbeat_result = client.send_launcher_heartbeat()
            
            successful_calls = sum([
                auth_result['success'],
                status_result.get('success', False),
                server_config_result.get('success', False),
                heartbeat_result.get('success', False)
            ])
            
            self.log_test("Launcher API Integration", successful_calls >= 3,
                         f"Completed {successful_calls}/4 API calls", {
                             'authentication': auth_result['success'],
                             'server_status': status_result.get('success', False),
                             'server_config': server_config_result.get('success', False),
                             'heartbeat': heartbeat_result.get('success', False)
                         })
            
            return successful_calls >= 3
            
        except Exception as e:
            self.log_test("Launcher API Integration", False, str(e))
            return False
    
    def cleanup(self):
        """Clean up test resources"""
        try:
            # Stop server process
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
        except:
            pass
        
        # Remove test env file
        if self.test_env_file and os.path.exists(self.test_env_file):
            os.unlink(self.test_env_file)
        
        print("\n🧹 Cleanup completed")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("🚀 Starting Launcher Communication Test Suite")
        print("=" * 60)
        
        try:
            # Environment tests
            self.test_env_file_loading()
            
            # Build tests
            self.test_build_launcher()
            
            # Server communication tests
            if self.test_api_server_startup():
                time.sleep(2)  # Let server fully start
                
                token = self.test_authentication()
                if token:
                    self.test_api_endpoints(token)
                    self.test_heartbeat_communication(token)
                
                # Advanced tests
                self.test_url_fallback()
                self.test_launcher_api_integration()
            
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Test suite error: {e}")
        finally:
            self.cleanup()
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        # Save detailed results
        report_file = 'launcher_communication_test_report.json'
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': (passed_tests/total_tests)*100
                },
                'test_results': self.test_results,
                'timestamp': time.time()
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return {
            'success': failed_tests == 0,
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests
        }


def main():
    """Main test runner"""
    tester = LauncherCommunicationTester()
    return tester.run_all_tests()


if __name__ == '__main__':
    results = main()
    sys.exit(0 if results['success'] else 1)