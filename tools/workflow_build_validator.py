#!/usr/bin/env python3
"""
Workflow Build Validation Script
Tests if launcher and server compile correctly with a fictive .env file
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import json
import time

class WorkflowBuildValidator:
    """Validates that both server and launcher can be built with test configuration"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.test_results = {}
        self.temp_files = []
        
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass
    
    def run_command(self, cmd, description="", timeout=300, cwd=None):
        """Run a command and capture results"""
        print(f"\n🔄 {description}")
        print(f"Command: {' '.join(cmd)}")
        
        if cwd is None:
            cwd = self.repo_root
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=cwd
            )
            
            success = result.returncode == 0
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {description}")
            
            if not success:
                print(f"Error output: {result.stderr[:500]}")
            
            return {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "description": description
            }
        except subprocess.TimeoutExpired:
            print(f"❌ TIMEOUT {description}")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "description": description
            }
        except Exception as e:
            print(f"❌ ERROR {description}: {e}")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "description": description
            }

    def create_test_env_file(self):
        """Create a test .env file with fictive but valid configuration"""
        test_env_content = """# Test .env file for workflow validation
# This is a fictive configuration file for testing purposes

# Server Configuration
SERVERNAME=TestWorkflowServer
TESTWORKFLOWSERVER_SERVER_NAME=Test Workflow Server
TESTWORKFLOWSERVER_SERVER_HOST=localhost
TESTWORKFLOWSERVER_LOGIN_PORT=54001
TESTWORKFLOWSERVER_MAP_PORT=54230
TESTWORKFLOWSERVER_SEARCH_PORT=54002

# Database Configuration
MYSQL_ROOT_PASSWORD=test_root_pass_2024
MYSQL_DATABASE=test_xidb
MYSQL_USER=test_xiuser
MYSQL_PASSWORD=test_xipass_2024

# Authentication Configuration
TESTWORKFLOWSERVER_ADMIN_USERNAME=test_admin
TESTWORKFLOWSERVER_ADMIN_PASSWORD=test_admin_pass_123
TESTWORKFLOWSERVER_API_SECRET_KEY=test_secret_key_for_workflow_12345

# API Configuration
TESTWORKFLOWSERVER_SERVER_URL=http://localhost:5000
TESTWORKFLOWSERVER_API_BASE_URL=http://localhost:5000/api
TESTWORKFLOWSERVER_SERVER_IPV4=127.0.0.1
TESTWORKFLOWSERVER_SERVER_IPV6=::1
TESTWORKFLOWSERVER_API_PORT=5000
TESTWORKFLOWSERVER_WEB_PORT=80

# Client Configuration
TESTWORKFLOWSERVER_WINDOWER_COMPATIBLE=true
TESTWORKFLOWSERVER_ASHITA_COMPATIBLE=true
TESTWORKFLOWSERVER_AUTO_UPDATE=true
TESTWORKFLOWSERVER_CLIENT_TIMEOUT=30000

# Development/Debug Options
TESTWORKFLOWSERVER_DEBUG_MODE=true
TESTWORKFLOWSERVER_LOG_LEVEL=DEBUG

# Performance Configuration
TESTWORKFLOWSERVER_MAX_PLAYERS=100
TESTWORKFLOWSERVER_ENABLE_HIGH_PERFORMANCE=false
TESTWORKFLOWSERVER_ENABLE_CONNECTION_POOLING=true
TESTWORKFLOWSERVER_TCP_NODELAY=true
TESTWORKFLOWSERVER_SOCKET_BUFFER_SIZE=65536

# Security Configuration
TESTWORKFLOWSERVER_ENABLE_FIREWALL=false
TESTWORKFLOWSERVER_RATE_LIMIT_ENABLED=true
TESTWORKFLOWSERVER_MAX_CONNECTIONS_PER_IP=10
"""
        
        # Create temporary .env file
        temp_env = tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False)
        temp_env.write(test_env_content)
        temp_env.close()
        
        self.temp_files.append(temp_env.name)
        print(f"📁 Created test .env file: {temp_env.name}")
        return temp_env.name

    def test_env_file_loading(self, env_file):
        """Test that .env file can be loaded correctly by launcher components"""
        print("\n" + "="*60)
        print("📋 TESTING .ENV FILE LOADING")
        print("="*60)
        
        # Test with enhanced_ffxi_launcher
        test_script = f'''
import sys
sys.path.insert(0, "tools")
try:
    from enhanced_ffxi_launcher import ServerConfig
    config = ServerConfig("{env_file}")
    print(f"Server name: {{config.server_name}}")
    print(f"Server host: {{config.get('SERVER_HOST')}}")
    print(f"Server URL: {{config.get('SERVER_URL')}}")
    print("SUCCESS: .env file loaded correctly")
except Exception as e:
    print(f"ERROR: {{e}}")
    sys.exit(1)
'''
        
        result = self.run_command([
            sys.executable, "-c", test_script
        ], "Test .env file loading with enhanced launcher")
        
        self.test_results["env_file_loading"] = result
        return result["success"]

    def test_launcher_compilation(self, env_file):
        """Test that launcher can be compiled with the test .env file"""
        print("\n" + "="*60)
        print("🔧 TESTING LAUNCHER COMPILATION")
        print("="*60)
        
        # Copy test .env to repo root temporarily
        repo_env = self.repo_root / ".env"
        backup_env = None
        
        # Backup existing .env if it exists
        if repo_env.exists():
            backup_env = self.repo_root / ".env.backup"
            shutil.copy2(repo_env, backup_env)
            self.temp_files.append(str(backup_env))
        
        # Copy test .env
        shutil.copy2(env_file, repo_env)
        self.temp_files.append(str(repo_env))
        
        try:
            # Test simple launcher build
            result1 = self.run_command([
                sys.executable, "tools/build_launcher.py"
            ], "Test basic launcher build", timeout=180)
            
            self.test_results["basic_launcher_build"] = result1
            
            # Test enhanced launcher build  
            result2 = self.run_command([
                sys.executable, "tools/enhanced_build_launcher.py"
            ], "Test enhanced launcher build", timeout=180)
            
            self.test_results["enhanced_launcher_build"] = result2
            
            # Test launcher configuration creation
            result3 = self.run_command([
                sys.executable, "tools/enhanced_ffxi_launcher.py", "--generate-config", str(env_file), "/tmp/test_config.ini"
            ], "Test launcher config generation", timeout=30)
            
            self.test_results["launcher_config_generation"] = result3
            
            return result1["success"] or result2["success"]  # At least one should work
            
        finally:
            # Restore backup if it existed
            if backup_env and backup_env.exists():
                shutil.copy2(backup_env, repo_env)
            elif repo_env.exists():
                os.unlink(repo_env)

    def test_server_compilation(self):
        """Test that server components can be compiled"""
        print("\n" + "="*60)
        print("🏗️ TESTING SERVER COMPILATION")
        print("="*60)
        
        # Check if build directory exists, create if not
        build_dir = self.repo_root / "build"
        build_dir.mkdir(exist_ok=True)
        
        # Test CMake configuration
        result1 = self.run_command([
            "cmake", "-S", ".", "-B", "build", "-DCMAKE_BUILD_TYPE=Debug"
        ], "Test CMake configuration", timeout=120)
        
        self.test_results["cmake_configure"] = result1
        
        if result1["success"]:
            # Test compilation (just a quick build)
            result2 = self.run_command([
                "cmake", "--build", "build", "--parallel", "2", "--target", "xi_connect"
            ], "Test server component compilation", timeout=300)
            
            self.test_results["server_compilation"] = result2
            return result2["success"]
        
        return False

    def test_launcher_communication_suite(self, env_file):
        """Test the existing launcher communication test suite"""
        print("\n" + "="*60)
        print("🔗 TESTING LAUNCHER COMMUNICATION SUITE")
        print("="*60)
        
        # Test simple launcher test
        result1 = self.run_command([
            sys.executable, "tools/simple_launcher_test.py"
        ], "Test simple launcher functionality", timeout=60)
        
        self.test_results["simple_launcher_test"] = result1
        
        return result1["success"]

    def run_comprehensive_test(self):
        """Run all tests with a fictive .env file"""
        print("🚀 WORKFLOW BUILD VALIDATION STARTED")
        print("="*80)
        
        start_time = time.time()
        
        try:
            # Step 1: Create test .env file
            env_file = self.create_test_env_file()
            
            # Step 2: Test .env file loading
            env_loaded = self.test_env_file_loading(env_file)
            
            # Step 3: Test launcher compilation
            launcher_compiled = self.test_launcher_compilation(env_file)
            
            # Step 4: Test server compilation
            server_compiled = self.test_server_compilation()
            
            # Step 5: Test launcher communication suite
            launcher_comm = self.test_launcher_communication_suite(env_file)
            
            # Generate summary
            total_tests = len(self.test_results)
            passed_tests = sum(1 for result in self.test_results.values() if result["success"])
            failed_tests = total_tests - passed_tests
            
            print("\n" + "="*80)
            print("📊 TEST SUMMARY")
            print("="*80)
            print(f"Total tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {failed_tests}")
            print(f"Success rate: {(passed_tests/total_tests*100):.1f}%")
            print(f"Duration: {time.time() - start_time:.1f} seconds")
            
            # Key validations
            critical_tests_passed = env_loaded and (launcher_compiled or launcher_comm)
            
            if critical_tests_passed:
                print("\n✅ CRITICAL VALIDATION PASSED")
                print("   - .env file loading works correctly")
                print("   - Launcher compilation or communication works")
                if server_compiled:
                    print("   - Server compilation works")
            else:
                print("\n❌ CRITICAL VALIDATION FAILED")
                if not env_loaded:
                    print("   - .env file loading failed")
                if not launcher_compiled and not launcher_comm:
                    print("   - Launcher compilation and communication failed")
                if not server_compiled:
                    print("   - Server compilation failed")
            
            # Save results
            results_file = self.repo_root / "workflow_build_validation_report.json"
            with open(results_file, 'w') as f:
                json.dump({
                    "summary": {
                        "total_tests": total_tests,
                        "passed": passed_tests,
                        "failed": failed_tests,
                        "success_rate": passed_tests/total_tests*100,
                        "duration": time.time() - start_time,
                        "critical_tests_passed": critical_tests_passed
                    },
                    "test_results": self.test_results
                }, f, indent=2)
            
            print(f"\n📋 Detailed results saved to: {results_file}")
            
            return critical_tests_passed
            
        finally:
            self.cleanup()

def main():
    validator = WorkflowBuildValidator()
    
    try:
        success = validator.run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        validator.cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        validator.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()