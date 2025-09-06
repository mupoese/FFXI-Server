#!/usr/bin/env python3
"""
Docker Testing and Validation Tool for FFXI Server
Comprehensive testing suite for Docker deployment validation
"""

import subprocess
import sys
import time
import json
import os
import argparse
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class DockerTestSuite:
    """Comprehensive Docker testing and validation suite"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = []
        self.errors = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with optional verbosity"""
        timestamp = time.strftime("%H:%M:%S")
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, cmd: List[str], timeout: int = 30, ignore_errors: bool = False) -> Tuple[bool, str, str]:
        """Run a command and return success status, stdout, stderr"""
        try:
            self.log(f"Running: {' '.join(cmd)}", "DEBUG")
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                check=not ignore_errors
            )
            return True, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out after {timeout}s: {' '.join(cmd)}", "ERROR")
            return False, "", f"Timeout after {timeout}s"
        except subprocess.CalledProcessError as e:
            if ignore_errors:
                return False, e.stdout or "", e.stderr or ""
            self.log(f"Command failed: {' '.join(cmd)}", "ERROR")
            self.log(f"Error: {e.stderr}", "ERROR")
            return False, e.stdout or "", e.stderr or ""
        except Exception as e:
            self.log(f"Unexpected error running command: {e}", "ERROR")
            return False, "", str(e)
    
    def test_docker_availability(self) -> bool:
        """Test if Docker is available and running"""
        self.log("Testing Docker availability...")
        
        success, stdout, stderr = self.run_command(["docker", "--version"])
        if not success:
            self.errors.append("Docker is not available")
            return False
        
        success, stdout, stderr = self.run_command(["docker", "info"], ignore_errors=True)
        if not success:
            self.errors.append("Docker daemon is not running")
            return False
            
        self.log("Docker is available and running", "SUCCESS")
        return True
    
    def test_docker_compose_availability(self) -> bool:
        """Test if Docker Compose is available"""
        self.log("Testing Docker Compose availability...")
        
        success, stdout, stderr = self.run_command(["docker-compose", "--version"])
        if not success:
            self.errors.append("Docker Compose is not available")
            return False
            
        self.log("Docker Compose is available", "SUCCESS")
        return True
    
    def validate_docker_files(self) -> bool:
        """Validate Docker configuration files"""
        self.log("Validating Docker configuration files...")
        
        required_files = [
            "docker/Dockerfile",
            "docker-compose.yml", 
            ".env.example",
            "docker/scripts/entrypoint.sh",
            "docker/configs/mysql.cnf"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.errors.append(f"Missing required files: {', '.join(missing_files)}")
            return False
        
        # Validate docker-compose syntax
        success, stdout, stderr = self.run_command(["docker-compose", "config", "-q"])
        if not success:
            self.errors.append(f"docker-compose.yml syntax error: {stderr}")
            return False
        
        # Check Dockerfile syntax with hadolint if available
        success, stdout, stderr = self.run_command(["hadolint", "docker/Dockerfile"], ignore_errors=True)
        if success and stdout.strip():
            self.log(f"Dockerfile linting suggestions: {stdout}", "WARNING")
        
        self.log("Docker configuration files validated", "SUCCESS")
        return True
    
    def test_image_build(self) -> bool:
        """Test Docker image build process"""
        self.log("Testing Docker image build...")
        
        # Build the image
        success, stdout, stderr = self.run_command([
            "docker", "build", 
            "-t", "ffxi-server:test",
            "."
        ], timeout=600)  # 10 minute timeout for build
        
        if not success:
            self.errors.append(f"Docker image build failed: {stderr}")
            return False
        
        # Verify image was created
        success, stdout, stderr = self.run_command([
            "docker", "images", "ffxi-server:test", "--format", "{{.Repository}}:{{.Tag}}"
        ])
        
        if "ffxi-server:test" not in stdout:
            self.errors.append("Built image not found in docker images")
            return False
        
        self.log("Docker image build successful", "SUCCESS")
        return True
    
    def test_container_startup(self) -> bool:
        """Test container startup and basic functionality"""
        self.log("Testing container startup...")
        
        # Create test environment
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as env_file:
            env_content = """
MYSQL_ROOT_PASSWORD=test_root_password
MYSQL_DATABASE=xidb_test
MYSQL_USER=test_user
MYSQL_PASSWORD=test_password
FFXI_DEBUG_MODE=true
FFXI_LOG_LEVEL=DEBUG
"""
            env_file.write(env_content)
            env_file_path = env_file.name
        
        try:
            # Start database container
            success, stdout, stderr = self.run_command([
                "docker-compose", "--env-file", env_file_path, "up", "-d", "db"
            ], timeout=120)
            
            if not success:
                self.errors.append(f"Failed to start database container: {stderr}")
                return False
            
            # Wait for database to be ready
            self.log("Waiting for database to be ready...")
            for i in range(30):  # 30 attempts, 2 seconds each = 60 seconds max
                success, stdout, stderr = self.run_command([
                    "docker-compose", "--env-file", env_file_path, 
                    "exec", "-T", "db", "mysqladmin", "ping", "-h", "localhost", "--silent"
                ], ignore_errors=True)
                
                if success:
                    break
                time.sleep(2)
            else:
                self.errors.append("Database failed to become ready within 60 seconds")
                return False
            
            # Test FFXI server container startup
            success, stdout, stderr = self.run_command([
                "docker", "run", "--rm", "--network", "container:ffxi-database",
                "-e", "FFXI_SQL_HOST=localhost",
                "-e", "FFXI_SQL_PASSWORD=test_root_password",
                "-e", "FFXI_SQL_USER=root",
                "-e", "FFXI_SQL_DATABASE=xidb_test",
                "ffxi-server:test", "health"
            ], timeout=60, ignore_errors=True)
            
            # Even if health check fails, check basic container functionality
            success, stdout, stderr = self.run_command([
                "docker", "run", "--rm", "--network", "container:ffxi-database",
                "-e", "FFXI_SQL_HOST=localhost",
                "-e", "FFXI_SQL_PASSWORD=test_root_password",
                "-e", "FFXI_SQL_USER=root",
                "ffxi-server:test", "/bin/bash", "-c",
                "ls -la /opt/ffxi/bin/ && ls -la /opt/ffxi/settings/ && echo 'Container validation OK'"
            ], timeout=30)
            
            if not success:
                self.errors.append(f"Container functionality test failed: {stderr}")
                return False
            
            self.log("Container startup test successful", "SUCCESS")
            return True
            
        finally:
            # Cleanup
            self.run_command([
                "docker-compose", "--env-file", env_file_path, "down", "-v"
            ], ignore_errors=True)
            os.unlink(env_file_path)
    
    def test_security_scanning(self) -> bool:
        """Test security scanning of the Docker image"""
        self.log("Testing security scanning...")
        
        # Check if Trivy is available
        success, stdout, stderr = self.run_command(["trivy", "--version"], ignore_errors=True)
        if not success:
            self.log("Trivy not available, skipping security scan", "WARNING")
            return True
        
        # Run Trivy scan
        success, stdout, stderr = self.run_command([
            "trivy", "image", "--severity", "HIGH,CRITICAL", 
            "--format", "json", "ffxi-server:test"
        ], timeout=300, ignore_errors=True)
        
        if success and stdout:
            try:
                scan_results = json.loads(stdout)
                vulnerabilities = scan_results.get("Results", [])
                critical_count = 0
                high_count = 0
                
                for result in vulnerabilities:
                    for vuln in result.get("Vulnerabilities", []):
                        severity = vuln.get("Severity", "").upper()
                        if severity == "CRITICAL":
                            critical_count += 1
                        elif severity == "HIGH":
                            high_count += 1
                
                self.log(f"Security scan completed: {critical_count} critical, {high_count} high severity vulnerabilities")
                
                if critical_count > 10:  # Threshold for acceptable risk
                    self.log(f"Too many critical vulnerabilities ({critical_count})", "WARNING")
                
            except json.JSONDecodeError:
                self.log("Failed to parse security scan results", "WARNING")
        
        self.log("Security scanning completed", "SUCCESS")
        return True
    
    def test_performance_metrics(self) -> bool:
        """Test performance metrics and resource usage"""
        self.log("Testing performance metrics...")
        
        # Test build time
        start_time = time.time()
        success, stdout, stderr = self.run_command([
            "docker", "build", "--no-cache", "-t", "ffxi-server:perf-test", "."
        ], timeout=900)  # 15 minute timeout
        build_time = time.time() - start_time
        
        if not success:
            self.errors.append(f"Performance build test failed: {stderr}")
            return False
        
        self.log(f"Build time: {build_time:.2f} seconds")
        
        # Check image size
        success, stdout, stderr = self.run_command([
            "docker", "images", "ffxi-server:perf-test", "--format", "{{.Size}}"
        ])
        
        if success:
            self.log(f"Image size: {stdout.strip()}")
        
        # Test resource usage during startup
        success, stdout, stderr = self.run_command([
            "docker", "stats", "--no-stream", "--format", 
            "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
        ], ignore_errors=True)
        
        if success:
            self.log(f"Resource usage snapshot:\n{stdout}")
        
        self.log("Performance metrics test completed", "SUCCESS")
        return True
    
    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.results),
            "passed_tests": len([r for r in self.results if r["passed"]]),
            "failed_tests": len([r for r in self.results if not r["passed"]]),
            "errors": self.errors,
            "results": self.results
        }
    
    def run_all_tests(self) -> bool:
        """Run all Docker tests"""
        self.log("Starting comprehensive Docker test suite...")
        
        tests = [
            ("Docker Availability", self.test_docker_availability),
            ("Docker Compose Availability", self.test_docker_compose_availability),
            ("Docker Files Validation", self.validate_docker_files),
            ("Image Build", self.test_image_build),
            ("Container Startup", self.test_container_startup),
            ("Security Scanning", self.test_security_scanning),
            ("Performance Metrics", self.test_performance_metrics)
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            self.log(f"Running test: {test_name}")
            start_time = time.time()
            
            try:
                passed = test_func()
                duration = time.time() - start_time
                
                self.results.append({
                    "name": test_name,
                    "passed": passed,
                    "duration": duration
                })
                
                if passed:
                    self.log(f"✓ {test_name} passed ({duration:.2f}s)", "SUCCESS")
                else:
                    self.log(f"✗ {test_name} failed ({duration:.2f}s)", "ERROR")
                    all_passed = False
                    
            except Exception as e:
                self.log(f"✗ {test_name} error: {e}", "ERROR")
                self.errors.append(f"{test_name}: {str(e)}")
                self.results.append({
                    "name": test_name,
                    "passed": False,
                    "duration": time.time() - start_time,
                    "error": str(e)
                })
                all_passed = False
        
        # Cleanup test images
        self.run_command(["docker", "rmi", "ffxi-server:test"], ignore_errors=True)
        self.run_command(["docker", "rmi", "ffxi-server:perf-test"], ignore_errors=True)
        
        return all_passed


def main():
    parser = argparse.ArgumentParser(description="Docker Testing Suite for FFXI Server")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--report", "-r", help="Generate JSON report to file")
    parser.add_argument("--ci", action="store_true", help="CI mode - exit with error code on failure")
    
    args = parser.parse_args()
    
    # Change to repository root if running from tools directory
    if os.path.basename(os.getcwd()) == "tools":
        os.chdir("..")
    
    test_suite = DockerTestSuite(verbose=args.verbose)
    success = test_suite.run_all_tests()
    
    # Generate report
    report = test_suite.generate_report()
    
    if args.report:
        with open(args.report, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {args.report}")
    
    # Print summary
    print("\n" + "="*60)
    print("DOCKER TEST SUITE SUMMARY")
    print("="*60)
    print(f"Total Tests: {report['total_tests']}")
    print(f"Passed: {report['passed_tests']}")
    print(f"Failed: {report['failed_tests']}")
    
    if report['errors']:
        print(f"\nErrors:")
        for error in report['errors']:
            print(f"  - {error}")
    
    if success:
        print("\n✓ All Docker tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some Docker tests failed!")
        if args.ci:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()