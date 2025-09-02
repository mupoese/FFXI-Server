#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Comprehensive Build Test Suite for FFXI Server with Python 3.12
Tests all build configurations, dependency compatibility, and Python tools
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
import argparse


class ComprehensiveBuildTest:
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.build_dir = self.repo_root / "build"
        self.results = {
            "python_version": sys.version,
            "tests": {},
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
        
    def run_command(self, cmd, description="", timeout=300):
        """Run a command and capture results"""
        print(f"\n🔄 {description}")
        print(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=self.repo_root
            )
            
            success = result.returncode == 0
            return {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "description": description
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "description": description
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "description": description
            }

    def test_python_environment(self):
        """Test Python 3.12 environment and package installation"""
        print("\n" + "="*60)
        print("🐍 PYTHON 3.12 ENVIRONMENT TESTS")
        print("="*60)
        
        # Test Python version
        test_name = "python_version"
        result = self.run_command([sys.executable, "--version"], "Check Python version")
        self.results["tests"][test_name] = result
        
        if result["success"]:
            version_output = result["stdout"].strip()
            if "3.12" in version_output:
                print(f"✅ {version_output}")
            else:
                print(f"⚠️  Expected Python 3.12, got: {version_output}")
                result["success"] = False
        
        # Test pip functionality
        test_name = "pip_functionality"
        result = self.run_command([sys.executable, "-m", "pip", "--version"], "Check pip functionality")
        self.results["tests"][test_name] = result
        
        if result["success"]:
            print(f"✅ pip: {result['stdout'].strip()}")
        
        # Test Python 3.12 requirements installation
        test_name = "py312_requirements_install"
        requirements_file = self.repo_root / "tools" / "requirements-py312.txt"
        
        if requirements_file.exists():
            result = self.run_command(
                [sys.executable, "-m", "pip", "install", "--dry-run", "-r", str(requirements_file)],
                "Test Python 3.12 requirements compatibility",
                timeout=180
            )
            self.results["tests"][test_name] = result
            
            if result["success"]:
                print("✅ Python 3.12 requirements compatible")
            else:
                print(f"❌ Python 3.12 requirements failed: {result['stderr'][:200]}")
        else:
            self.results["tests"][test_name] = {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "requirements-py312.txt not found",
                "description": "Test Python 3.12 requirements compatibility"
            }

    def test_python_tools(self):
        """Test Python tools compatibility with Python 3.12"""
        print("\n" + "="*60)
        print("🛠️  PYTHON TOOLS COMPATIBILITY TESTS")
        print("="*60)
        
        tools_dir = self.repo_root / "tools"
        python_tools = list(tools_dir.glob("*.py"))
        
        # Test a sample of important Python tools
        important_tools = [
            "dbtool.py",
            "generate_changelog.py", 
            "db_performance_monitor.py",
            "test_database_improvements.py"
        ]
        
        for tool_name in important_tools:
            tool_path = tools_dir / tool_name
            if tool_path.exists():
                test_name = f"tool_{tool_name.replace('.py', '')}"
                result = self.run_command(
                    [sys.executable, str(tool_path), "--help"],
                    f"Test {tool_name} syntax and help",
                    timeout=30
                )
                self.results["tests"][test_name] = result
                
                if result["success"] or "usage:" in result["stdout"].lower():
                    print(f"✅ {tool_name}")
                else:
                    print(f"❌ {tool_name}: {result['stderr'][:100]}")
            else:
                print(f"⚠️  {tool_name} not found")

    def test_cmake_configuration(self):
        """Test CMake configuration and Python detection"""
        print("\n" + "="*60)
        print("🔧 CMAKE CONFIGURATION TESTS")
        print("="*60)
        
        # Clean build directory
        if self.build_dir.exists():
            import shutil
            shutil.rmtree(self.build_dir)
        
        self.build_dir.mkdir(exist_ok=True)
        
        # Test CMake configuration
        test_name = "cmake_configure"
        result = self.run_command(
            ["cmake", "-S", ".", "-B", "build"],
            "CMake configuration",
            timeout=300
        )
        self.results["tests"][test_name] = result
        
        if result["success"]:
            print("✅ CMake configuration successful")
            
            # Check if Python 3.12 was detected
            if "Python_VERSION: 3.12" in result["stdout"]:
                print("✅ Python 3.12 detected by CMake")
            else:
                print("⚠️  Python 3.12 not explicitly detected in CMake output")
        else:
            print(f"❌ CMake configuration failed: {result['stderr'][:200]}")

    def test_build_process(self):
        """Test the actual build process"""
        print("\n" + "="*60)
        print("🏗️  BUILD PROCESS TESTS")
        print("="*60)
        
        if not (self.build_dir / "Makefile").exists():
            print("❌ No Makefile found, skipping build test")
            return
        
        # Test build with limited parallelism for CI stability
        test_name = "build_process"
        result = self.run_command(
            ["cmake", "--build", "build", "-j2"],
            "Build process",
            timeout=600
        )
        self.results["tests"][test_name] = result
        
        if result["success"]:
            print("✅ Build process successful")
            
            # Check for built executables
            executables = ["xi_connect", "xi_map", "xi_search", "xi_world"]
            built_executables = []
            
            for exe in executables:
                exe_path = self.build_dir / exe
                if exe_path.exists():
                    built_executables.append(exe)
                    print(f"✅ {exe} built successfully")
                else:
                    print(f"❌ {exe} not found")
            
            self.results["built_executables"] = built_executables
        else:
            print(f"❌ Build failed: {result['stderr'][:300]}")

    def test_performance_benchmarks(self):
        """Test Python 3.12 performance benchmarks"""
        print("\n" + "="*60)
        print("🚀 PYTHON 3.12 PERFORMANCE TESTS")
        print("="*60)
        
        # Simple performance test
        test_script = '''
import time
import json

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def dict_operations():
    data = {}
    for i in range(10000):
        data[f"key_{i}"] = i * 2
    return len(data)

def json_operations():
    data = {"test": list(range(1000))}
    for _ in range(100):
        serialized = json.dumps(data)
        deserialized = json.loads(serialized)
    return len(deserialized["test"])

start_time = time.time()
fib_result = fibonacci(25)
dict_result = dict_operations()
json_result = json_operations()
end_time = time.time()

print(f"Performance test completed in {end_time - start_time:.2f} seconds")
print(f"Fibonacci(25): {fib_result}")
print(f"Dict operations: {dict_result}")
print(f"JSON operations: {json_result}")
'''
        
        test_name = "performance_benchmark"
        with open(self.repo_root / "temp_perf_test.py", "w") as f:
            f.write(test_script)
        
        try:
            result = self.run_command(
                [sys.executable, "temp_perf_test.py"],
                "Python 3.12 performance benchmark",
                timeout=60
            )
            self.results["tests"][test_name] = result
            
            if result["success"]:
                print("✅ Performance benchmark completed")
                print(result["stdout"])
            else:
                print(f"❌ Performance benchmark failed: {result['stderr']}")
        finally:
            # Clean up temp file
            temp_file = self.repo_root / "temp_perf_test.py"
            if temp_file.exists():
                temp_file.unlink()

    def test_security_features(self):
        """Test Python 3.12 security features and package safety"""
        print("\n" + "="*60)
        print("🔒 SECURITY TESTS")
        print("="*60)
        
        # Test if security packages are available
        security_packages = ["bandit", "safety", "pip-audit"]
        
        for package in security_packages:
            test_name = f"security_{package}"
            result = self.run_command(
                [sys.executable, "-m", package, "--version"],
                f"Test {package} availability",
                timeout=30
            )
            self.results["tests"][test_name] = result
            
            if result["success"]:
                print(f"✅ {package}: {result['stdout'].strip()}")
            else:
                print(f"❌ {package} not available")

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE BUILD TEST REPORT")
        print("="*80)
        
        # Count results
        for test_name, test_result in self.results["tests"].items():
            self.results["summary"]["total"] += 1
            if test_result["success"]:
                self.results["summary"]["passed"] += 1
            else:
                self.results["summary"]["failed"] += 1
        
        # Print summary
        summary = self.results["summary"]
        print(f"\n📈 Test Summary:")
        print(f"   Total tests: {summary['total']}")
        print(f"   Passed: {summary['passed']} ✅")
        print(f"   Failed: {summary['failed']} ❌")
        print(f"   Success rate: {(summary['passed']/summary['total']*100):.1f}%")
        
        # Print failed tests
        if summary["failed"] > 0:
            print(f"\n❌ Failed Tests:")
            for test_name, test_result in self.results["tests"].items():
                if not test_result["success"]:
                    print(f"   - {test_name}: {test_result['description']}")
                    if test_result["stderr"]:
                        print(f"     Error: {test_result['stderr'][:150]}...")
        
        # Save detailed report
        report_file = self.repo_root / "comprehensive_build_test_report.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return summary["failed"] == 0

    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Build Test Suite for Python 3.12")
        print(f"Python version: {sys.version}")
        print(f"Repository: {self.repo_root}")
        
        start_time = time.time()
        
        try:
            self.test_python_environment()
            self.test_python_tools()
            self.test_cmake_configuration()
            self.test_build_process()
            self.test_performance_benchmarks()
            self.test_security_features()
            
            success = self.generate_report()
            
            end_time = time.time()
            print(f"\n⏱️  Total test time: {end_time - start_time:.1f} seconds")
            
            return success
            
        except KeyboardInterrupt:
            print("\n\n❌ Tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n\n❌ Unexpected error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Comprehensive Build Test Suite")
    parser.add_argument("--ci", action="store_true", help="Run in CI mode")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    args = parser.parse_args()
    
    test_suite = ComprehensiveBuildTest()
    
    if args.quick:
        print("🏃 Running quick tests only")
        test_suite.test_python_environment()
        test_suite.test_python_tools()
        success = test_suite.generate_report()
    else:
        success = test_suite.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()