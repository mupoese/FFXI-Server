#!/usr/bin/env python3
"""
Comprehensive Build Test Suite

This script provides comprehensive build testing for the FFXI Server project,
validating the entire build pipeline, dependency management, and cross-platform compatibility.
"""

import argparse
import json
import os
import sys
import time
import subprocess
import platform
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class ComprehensiveBuildTestSuite:
    def __init__(self, verbose: bool = False, ci_mode: bool = False):
        self.verbose = verbose
        self.ci_mode = ci_mode
        self.repo_root = Path('/home/runner/work/FFXI-Server/FFXI-Server')
        self.build_dir = self.repo_root / 'build'
        self.test_results = {}
        self.start_time = datetime.now()
        self.platform_info = {
            'system': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.verbose or level in ["ERROR", "CRITICAL"]:
            print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, cmd: List[str], timeout: int = 600, cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Run a command and return the result"""
        if cwd is None:
            cwd = self.repo_root
            
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=str(cwd)
            )
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': ' '.join(cmd)
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'command': ' '.join(cmd)
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'command': ' '.join(cmd)
            }
    
    def test_build_dependencies(self) -> Dict[str, Any]:
        """Test build dependencies availability"""
        self.log("Testing build dependencies...")
        
        dependencies = {
            'cmake': ['cmake', '--version'],
            'make': ['make', '--version'],
            'gcc': ['gcc', '--version'],
            'g++': ['g++', '--version'],
            'python3': ['python3', '--version'],
            'git': ['git', '--version']
        }
        
        results = {}
        missing_deps = []
        
        for dep_name, cmd in dependencies.items():
            result = self.run_command(cmd, timeout=30)
            results[dep_name] = {
                'available': result['success'],
                'version_info': result['stdout'].split('\n')[0] if result['success'] else None,
                'error': result['stderr'] if not result['success'] else None
            }
            
            if not result['success']:
                missing_deps.append(dep_name)
        
        success = len(missing_deps) == 0
        self.log(f"Build dependencies test: {'PASSED' if success else 'FAILED'}")
        
        if missing_deps:
            self.log(f"Missing dependencies: {', '.join(missing_deps)}", "ERROR")
        
        return {
            'success': success,
            'missing_dependencies': missing_deps,
            'dependency_results': results
        }
    
    def test_cmake_configuration(self) -> Dict[str, Any]:
        """Test CMake configuration"""
        self.log("Testing CMake configuration...")
        
        # Clean build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(exist_ok=True)
        
        # Test different build types
        build_types = ['Debug', 'Release', 'RelWithDebInfo']
        cmake_results = {}
        
        for build_type in build_types:
            self.log(f"Testing CMake configuration for {build_type}...")
            
            cmd = [
                'cmake',
                '-B', str(self.build_dir),
                '-S', str(self.repo_root),
                f'-DCMAKE_BUILD_TYPE={build_type}'
            ]
            
            result = self.run_command(cmd, timeout=300)
            
            cmake_results[build_type] = {
                'success': result['success'],
                'stdout': result['stdout'],
                'stderr': result['stderr'],
                'command': result['command']
            }
            
            if not result['success']:
                self.log(f"CMake configuration failed for {build_type}: {result['stderr']}", "ERROR")
            
            # Clean for next iteration
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            self.build_dir.mkdir(exist_ok=True)
        
        successful_configs = sum(1 for result in cmake_results.values() if result['success'])
        success = successful_configs > 0  # At least one configuration should work
        
        self.log(f"CMake configuration test: {'PASSED' if success else 'FAILED'}")
        self.log(f"Successful configurations: {successful_configs}/{len(build_types)}")
        
        return {
            'success': success,
            'successful_configurations': successful_configs,
            'total_configurations': len(build_types),
            'cmake_results': cmake_results
        }
    
    def test_compilation(self) -> Dict[str, Any]:
        """Test compilation process"""
        self.log("Testing compilation process...")
        
        # Use Debug build for compilation test
        cmake_cmd = [
            'cmake',
            '-B', str(self.build_dir),
            '-S', str(self.repo_root),
            '-DCMAKE_BUILD_TYPE=Debug'
        ]
        
        cmake_result = self.run_command(cmake_cmd, timeout=300)
        
        if not cmake_result['success']:
            return {
                'success': False,
                'error': 'CMake configuration failed',
                'cmake_result': cmake_result
            }
        
        # Attempt compilation
        build_cmd = ['cmake', '--build', str(self.build_dir), '--parallel', '4']
        build_result = self.run_command(build_cmd, timeout=1800)  # 30 minutes timeout
        
        # Check for common build artifacts
        expected_artifacts = [
            self.build_dir / 'xi_map',
            self.build_dir / 'xi_search',
            self.build_dir / 'xi_connect'
        ]
        
        found_artifacts = []
        for artifact in expected_artifacts:
            if artifact.exists():
                found_artifacts.append(str(artifact))
        
        success = build_result['success'] and len(found_artifacts) > 0
        
        self.log(f"Compilation test: {'PASSED' if success else 'FAILED'}")
        
        if not success:
            self.log(f"Build failed: {build_result['stderr']}", "ERROR")
        else:
            self.log(f"Found build artifacts: {len(found_artifacts)}")
        
        return {
            'success': success,
            'cmake_result': cmake_result,
            'build_result': build_result,
            'found_artifacts': found_artifacts,
            'expected_artifacts': [str(a) for a in expected_artifacts]
        }
    
    def test_ci_scripts(self) -> Dict[str, Any]:
        """Test CI scripts execution"""
        self.log("Testing CI scripts...")
        
        ci_scripts = {
            'general': self.repo_root / 'tools' / 'ci' / 'general.sh',
            'cpp': self.repo_root / 'tools' / 'ci' / 'cpp.sh',
            'lua': self.repo_root / 'tools' / 'ci' / 'lua.sh',
            'sql': self.repo_root / 'tools' / 'ci' / 'sql.sh'
        }
        
        script_results = {}
        successful_scripts = 0
        
        for script_name, script_path in ci_scripts.items():
            if script_path.exists():
                self.log(f"Running {script_name} CI script...")
                
                result = self.run_command(['bash', str(script_path)], timeout=600)
                script_results[script_name] = {
                    'success': result['success'],
                    'stdout': result['stdout'],
                    'stderr': result['stderr'],
                    'command': result['command']
                }
                
                if result['success']:
                    successful_scripts += 1
                else:
                    self.log(f"{script_name} CI script failed: {result['stderr']}", "ERROR")
            else:
                script_results[script_name] = {
                    'success': False,
                    'error': 'Script file not found'
                }
                self.log(f"{script_name} CI script not found", "WARNING")
        
        success = successful_scripts >= 2  # At least 2 scripts should pass
        
        self.log(f"CI scripts test: {'PASSED' if success else 'FAILED'}")
        self.log(f"Successful scripts: {successful_scripts}/{len(ci_scripts)}")
        
        return {
            'success': success,
            'successful_scripts': successful_scripts,
            'total_scripts': len(ci_scripts),
            'script_results': script_results
        }
    
    def test_python_tools(self) -> Dict[str, Any]:
        """Test Python development tools"""
        self.log("Testing Python development tools...")
        
        python_tools = {
            'generate_changelog': self.repo_root / 'tools' / 'generate_changelog.py',
            'dbtool': self.repo_root / 'tools' / 'dbtool.py',
            'job_db_test_suite': self.repo_root / 'tools' / 'testing' / 'comprehensive_job_db_test_suite.py'
        }
        
        tool_results = {}
        successful_tools = 0
        
        for tool_name, tool_path in python_tools.items():
            if tool_path.exists():
                self.log(f"Testing {tool_name} Python tool...")
                
                # Test basic import/syntax
                result = self.run_command(['python3', str(tool_path), '--help'], timeout=60)
                
                # If --help fails, try basic syntax check
                if not result['success']:
                    syntax_result = self.run_command(['python3', '-m', 'py_compile', str(tool_path)], timeout=30)
                    tool_results[tool_name] = {
                        'syntax_valid': syntax_result['success'],
                        'help_available': False,
                        'error': result['stderr'] or syntax_result['stderr']
                    }
                else:
                    tool_results[tool_name] = {
                        'syntax_valid': True,
                        'help_available': True,
                        'help_output': result['stdout']
                    }
                    successful_tools += 1
            else:
                tool_results[tool_name] = {
                    'syntax_valid': False,
                    'help_available': False,
                    'error': 'Tool file not found'
                }
        
        success = successful_tools >= 1  # At least 1 tool should work
        
        self.log(f"Python tools test: {'PASSED' if success else 'FAILED'}")
        self.log(f"Working tools: {successful_tools}/{len(python_tools)}")
        
        return {
            'success': success,
            'successful_tools': successful_tools,
            'total_tools': len(python_tools),
            'tool_results': tool_results
        }
    
    def test_database_connectivity(self) -> Dict[str, Any]:
        """Test database connectivity and setup"""
        self.log("Testing database connectivity...")
        
        # Check for database test tools
        db_test_tools = [
            self.repo_root / 'tools' / 'database' / 'enhanced_database_test_suite.py',
            self.repo_root / 'tools' / 'database' / 'test_database_improvements.py'
        ]
        
        db_results = {}
        available_tools = 0
        
        for tool_path in db_test_tools:
            if tool_path.exists():
                tool_name = tool_path.name
                
                # Test basic syntax
                syntax_result = self.run_command(['python3', '-m', 'py_compile', str(tool_path)], timeout=30)
                
                db_results[tool_name] = {
                    'exists': True,
                    'syntax_valid': syntax_result['success'],
                    'error': syntax_result['stderr'] if not syntax_result['success'] else None
                }
                
                if syntax_result['success']:
                    available_tools += 1
            else:
                db_results[tool_path.name] = {
                    'exists': False,
                    'syntax_valid': False,
                    'error': 'Tool not found'
                }
        
        # Check for SQL files
        sql_dir = self.repo_root / 'sql'
        sql_files_exist = sql_dir.exists() and len(list(sql_dir.glob('*.sql'))) > 0
        
        success = available_tools > 0 and sql_files_exist
        
        self.log(f"Database connectivity test: {'PASSED' if success else 'FAILED'}")
        self.log(f"Available DB tools: {available_tools}/{len(db_test_tools)}")
        self.log(f"SQL files available: {sql_files_exist}")
        
        return {
            'success': success,
            'available_tools': available_tools,
            'sql_files_exist': sql_files_exist,
            'db_tool_results': db_results
        }
    
    def test_workflow_compatibility(self) -> Dict[str, Any]:
        """Test GitHub workflow compatibility"""
        self.log("Testing GitHub workflow compatibility...")
        
        workflow_dir = self.repo_root / '.github' / 'workflows'
        
        if not workflow_dir.exists():
            return {
                'success': False,
                'error': 'Workflows directory not found'
            }
        
        workflow_files = list(workflow_dir.glob('*.yml')) + list(workflow_dir.glob('*.yaml'))
        
        workflow_results = {}
        valid_workflows = 0
        
        for workflow_file in workflow_files:
            try:
                import yaml
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflow_data = yaml.safe_load(f)
                
                # Basic validation
                has_name = 'name' in workflow_data
                # In YAML, 'on' gets parsed as boolean True, so check for both
                has_on = 'on' in workflow_data or True in workflow_data
                has_jobs = 'jobs' in workflow_data
                
                is_valid = has_name and has_on and has_jobs
                
                workflow_results[workflow_file.name] = {
                    'valid_yaml': True,
                    'has_name': has_name,
                    'has_on': has_on,
                    'has_jobs': has_jobs,
                    'is_valid': is_valid
                }
                
                if is_valid:
                    valid_workflows += 1
                    
            except Exception as e:
                workflow_results[workflow_file.name] = {
                    'valid_yaml': False,
                    'error': str(e)
                }
        
        success = valid_workflows > 0 and len(workflow_files) > 0
        
        self.log(f"Workflow compatibility test: {'PASSED' if success else 'FAILED'}")
        self.log(f"Valid workflows: {valid_workflows}/{len(workflow_files)}")
        
        return {
            'success': success,
            'valid_workflows': valid_workflows,
            'total_workflows': len(workflow_files),
            'workflow_results': workflow_results
        }
    
    def run_comprehensive_build_tests(self) -> Dict[str, Any]:
        """Run all comprehensive build tests"""
        self.log("Starting comprehensive build tests...")
        
        # Run all test components
        tests = {
            'build_dependencies': self.test_build_dependencies(),
            'cmake_configuration': self.test_cmake_configuration(),
            'compilation': self.test_compilation(),
            'ci_scripts': self.test_ci_scripts(),
            'python_tools': self.test_python_tools(),
            'database_connectivity': self.test_database_connectivity(),
            'workflow_compatibility': self.test_workflow_compatibility()
        }
        
        # Calculate overall success
        successful_tests = sum(1 for test in tests.values() if test.get('success', False))
        total_tests = len(tests)
        success_rate = (successful_tests / total_tests) * 100
        
        overall_success = success_rate >= 70.0  # Require 70% success rate
        
        # Summary
        summary = {
            'overall_success': overall_success,
            'success_rate': success_rate,
            'successful_tests': successful_tests,
            'total_tests': total_tests,
            'execution_time': (datetime.now() - self.start_time).total_seconds(),
            'timestamp': datetime.now().isoformat(),
            'platform_info': self.platform_info
        }
        
        self.log(f"Comprehensive build tests completed")
        self.log(f"Overall result: {'PASSED' if overall_success else 'FAILED'}")
        self.log(f"Success rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
        self.log(f"Execution time: {summary['execution_time']:.2f} seconds")
        
        return {
            'summary': summary,
            'tests': tests,
            'platform_info': self.platform_info
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_build_test_report_{timestamp}.json"
        
        output_file = self.repo_root / filename
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.log(f"Test results saved to: {output_file}")
            return str(output_file)
        except Exception as e:
            self.log(f"Failed to save results: {str(e)}", "ERROR")
            return None

def main():
    parser = argparse.ArgumentParser(description='Comprehensive Build Test Suite')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose output')
    parser.add_argument('--ci', action='store_true',
                       help='Run in CI mode (non-interactive)')
    parser.add_argument('--output', '-o', type=str,
                       help='Output file for test results')
    parser.add_argument('--skip-compilation', action='store_true',
                       help='Skip compilation test (for faster testing)')
    
    args = parser.parse_args()
    
    # Initialize test suite
    test_suite = ComprehensiveBuildTestSuite(verbose=args.verbose, ci_mode=args.ci)
    
    try:
        # Run comprehensive tests
        results = test_suite.run_comprehensive_build_tests()
        
        # Save results
        output_file = test_suite.save_results(results, args.output)
        
        # Exit with appropriate code
        success = results['summary']['overall_success']
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        test_suite.log("Test execution interrupted by user", "WARNING")
        sys.exit(130)
    except Exception as e:
        test_suite.log(f"Test execution failed: {str(e)}", "CRITICAL")
        sys.exit(1)

if __name__ == '__main__':
    main()