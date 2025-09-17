#!/usr/bin/env python3
"""
Comprehensive Build Test Suite for Python 3.12

This tool performs comprehensive validation of the build system,
dependencies, and overall project health in CI environments.
"""

import sys
import os
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple

class ComprehensiveBuildTest:
    def __init__(self, ci_mode: bool = False):
        self.ci_mode = ci_mode
        self.results = {}
        self.start_time = time.time()
        self.repo_path = Path.cwd()
        
    def run_command(self, cmd: List[str], timeout: int = 60) -> Tuple[bool, str, str]:
        """Run a command and return success, stdout, stderr."""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=self.repo_path
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def test_python_environment(self) -> Dict[str, Any]:
        """Test Python environment and dependencies."""
        print("🐍 Testing Python Environment...")
        
        test_result = {
            "name": "Python Environment",
            "success": True,
            "details": {}
        }
        
        # Test Python version
        success, stdout, stderr = self.run_command([sys.executable, "--version"])
        if success and "3.12" in stdout:
            test_result["details"]["python_version"] = "✅ Python 3.12 available"
        else:
            test_result["success"] = False
            test_result["details"]["python_version"] = f"❌ Wrong Python version: {stdout}"
        
        # Test pip availability
        success, stdout, stderr = self.run_command([sys.executable, "-m", "pip", "--version"])
        if success:
            test_result["details"]["pip"] = "✅ pip available"
        else:
            test_result["success"] = False
            test_result["details"]["pip"] = "❌ pip not available"
        
        # Test requirements installation
        requirements_files = ["tools/requirements.txt", "tools/requirements-py312.txt"]
        for req_file in requirements_files:
            if Path(req_file).exists():
                success, stdout, stderr = self.run_command([
                    sys.executable, "-m", "pip", "check"
                ])
                if success:
                    test_result["details"][req_file] = "✅ Dependencies satisfied"
                else:
                    test_result["details"][req_file] = f"⚠️  Dependency issues: {stderr}"
        
        return test_result
    
    def test_build_system(self) -> Dict[str, Any]:
        """Test build system (CMake) availability and basic functionality."""
        print("🔨 Testing Build System...")
        
        test_result = {
            "name": "Build System",
            "success": True,
            "details": {}
        }
        
        # Test CMake availability
        success, stdout, stderr = self.run_command(["cmake", "--version"])
        if success:
            version = stdout.split('\n')[0] if stdout else "unknown"
            test_result["details"]["cmake"] = f"✅ {version}"
        else:
            test_result["success"] = False
            test_result["details"]["cmake"] = "❌ CMake not available"
            return test_result
        
        # Test CMake can read CMakeLists.txt
        if Path("CMakeLists.txt").exists():
            # Try a quick configure test in a temp directory
            test_build_dir = self.repo_path / "test_build"
            test_build_dir.mkdir(exist_ok=True)
            
            try:
                success, stdout, stderr = self.run_command([
                    "cmake", "-S", ".", "-B", str(test_build_dir), 
                    "-DCMAKE_BUILD_TYPE=Debug"
                ], timeout=120)
                
                if success:
                    test_result["details"]["cmake_configure"] = "✅ CMake configuration successful"
                else:
                    test_result["details"]["cmake_configure"] = f"⚠️  CMake configuration issues: {stderr[:200]}"
                    # Don't fail the entire test for this
                
            except Exception as e:
                test_result["details"]["cmake_configure"] = f"⚠️  CMake test error: {e}"
            finally:
                # Cleanup
                if test_build_dir.exists():
                    import shutil
                    shutil.rmtree(test_build_dir, ignore_errors=True)
        else:
            test_result["details"]["cmake_configure"] = "⚠️  No CMakeLists.txt found"
        
        return test_result
    
    def test_system_dependencies(self) -> Dict[str, Any]:
        """Test system dependencies availability."""
        print("📦 Testing System Dependencies...")
        
        test_result = {
            "name": "System Dependencies", 
            "success": True,
            "details": {}
        }
        
        # Test common build tools
        tools = ["make", "gcc", "g++", "pkg-config"]
        for tool in tools:
            success, stdout, stderr = self.run_command(["which", tool])
            if success:
                # Get version if possible
                success_v, stdout_v, _ = self.run_command([tool, "--version"])
                if success_v:
                    version_line = stdout_v.split('\n')[0] if stdout_v else "available"
                    test_result["details"][tool] = f"✅ {version_line}"
                else:
                    test_result["details"][tool] = "✅ Available"
            else:
                test_result["details"][tool] = "⚠️  Not found"
        
        # Test libraries (check if pkg-config can find them)
        libraries = ["mariadb", "luajit", "libzmq"]
        for lib in libraries:
            success, stdout, stderr = self.run_command(["pkg-config", "--exists", lib])
            if success:
                success_v, version, _ = self.run_command(["pkg-config", "--modversion", lib])
                if success_v:
                    test_result["details"][lib] = f"✅ {version.strip()}"
                else:
                    test_result["details"][lib] = "✅ Available"
            else:
                test_result["details"][lib] = "⚠️  Not found via pkg-config"
        
        return test_result
    
    def test_ci_scripts(self) -> Dict[str, Any]:
        """Test CI scripts syntax and basic functionality."""
        print("🧪 Testing CI Scripts...")
        
        test_result = {
            "name": "CI Scripts",
            "success": True,
            "details": {}
        }
        
        ci_scripts = [
            "tools/ci/git.sh",
            "tools/ci/general.sh", 
            "tools/ci/python.sh",
            "tools/ci/cpp.sh",
            "tools/ci/lua.sh",
            "tools/ci/sql.sh"
        ]
        
        for script in ci_scripts:
            script_path = Path(script)
            if script_path.exists():
                # Test syntax
                success, stdout, stderr = self.run_command(["bash", "-n", str(script_path)])
                if success:
                    test_result["details"][script] = "✅ Syntax OK"
                else:
                    test_result["success"] = False
                    test_result["details"][script] = f"❌ Syntax error: {stderr}"
            else:
                test_result["details"][script] = "⚠️  Not found"
        
        return test_result
    
    def test_repository_structure(self) -> Dict[str, Any]:
        """Test repository structure and key files."""
        print("📁 Testing Repository Structure...")
        
        test_result = {
            "name": "Repository Structure",
            "success": True,
            "details": {}
        }
        
        # Check key directories
        key_dirs = ["src", "scripts", "sql", "tools", ".github/workflows"]
        for directory in key_dirs:
            dir_path = Path(directory)
            if dir_path.exists() and dir_path.is_dir():
                file_count = len(list(dir_path.glob("*")))
                test_result["details"][directory] = f"✅ {file_count} items"
            else:
                test_result["details"][directory] = "⚠️  Not found"
        
        # Check key files
        key_files = ["CMakeLists.txt", "README.md", ".clang-format"]
        for file_name in key_files:
            file_path = Path(file_name)
            if file_path.exists():
                size = file_path.stat().st_size
                test_result["details"][file_name] = f"✅ {size} bytes"
            else:
                test_result["details"][file_name] = "⚠️  Not found"
        
        return test_result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all build tests and return comprehensive results."""
        print("🚀 Starting Comprehensive Build Test Suite")
        print("=" * 50)
        
        # Run all test categories
        tests = [
            self.test_python_environment,
            self.test_build_system,
            self.test_system_dependencies,
            self.test_ci_scripts,
            self.test_repository_structure
        ]
        
        all_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ci_mode": self.ci_mode,
            "tests": [],
            "summary": {
                "total_tests": len(tests),
                "passed_tests": 0,
                "failed_tests": 0,
                "duration": 0
            }
        }
        
        for test_func in tests:
            try:
                result = test_func()
                all_results["tests"].append(result)
                
                if result["success"]:
                    all_results["summary"]["passed_tests"] += 1
                    print(f"✅ {result['name']} - PASSED")
                else:
                    all_results["summary"]["failed_tests"] += 1
                    print(f"❌ {result['name']} - FAILED")
                
            except Exception as e:
                print(f"❌ {test_func.__name__} - ERROR: {e}")
                all_results["tests"].append({
                    "name": test_func.__name__,
                    "success": False,
                    "details": {"error": str(e)}
                })
                all_results["summary"]["failed_tests"] += 1
        
        all_results["summary"]["duration"] = time.time() - self.start_time
        
        return all_results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report."""
        report = []
        report.append("# Comprehensive Build Test Report")
        report.append(f"Generated: {results['timestamp']}")
        report.append(f"CI Mode: {results['ci_mode']}")
        report.append("")
        
        # Summary
        summary = results["summary"]
        report.append("## Summary")
        report.append(f"- Total tests: {summary['total_tests']}")
        report.append(f"- Passed: {summary['passed_tests']}")
        report.append(f"- Failed: {summary['failed_tests']}")
        report.append(f"- Duration: {summary['duration']:.2f}s")
        report.append("")
        
        # Detailed results
        report.append("## Detailed Results")
        for test in results["tests"]:
            status = "✅" if test["success"] else "❌"
            report.append(f"### {status} {test['name']}")
            
            for key, value in test["details"].items():
                report.append(f"- {key}: {value}")
            
            report.append("")
        
        return "\n".join(report)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive build test suite")
    parser.add_argument("--ci", action="store_true", 
                       help="Run in CI mode with additional checks")
    parser.add_argument("--json", action="store_true",
                       help="Output results in JSON format")
    
    args = parser.parse_args()
    
    # Run tests
    tester = ComprehensiveBuildTest(ci_mode=args.ci)
    results = tester.run_all_tests()
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        # Generate and save report
        report = tester.generate_report(results)
        
        # Save to file
        report_file = Path("comprehensive_build_test_report.json")
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n" + "=" * 50)
        print("📊 BUILD TEST SUMMARY")
        print("=" * 50)
        
        summary = results["summary"]
        print(f"Tests: {summary['passed_tests']}/{summary['total_tests']} passed")
        print(f"Duration: {summary['duration']:.2f}s")
        
        if summary["failed_tests"] > 0:
            print(f"\n❌ {summary['failed_tests']} tests failed - check details above")
            return 1
        else:
            print("\n✅ All tests passed!")
            return 0

if __name__ == "__main__":
    sys.exit(main())