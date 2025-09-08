#!/usr/bin/env python3
"""
Master Test Coordinator for FFXI Server

Coordinates comprehensive job database function tests and build tests
as requested for complete validation of the job implementation system.
"""

import argparse
import json
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class MasterTestCoordinator:
    def __init__(self, verbose: bool = False, ci_mode: bool = False):
        self.verbose = verbose
        self.ci_mode = ci_mode
        self.repo_root = Path('/home/runner/work/FFXI-Server/FFXI-Server')
        self.start_time = datetime.now()
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.verbose or level in ["ERROR", "CRITICAL"]:
            print(f"[{timestamp}] {level}: {message}")
    
    def run_test_suite(self, script_path: Path, args: list = None) -> Dict[str, Any]:
        """Run a test suite and return results"""
        if not script_path.exists():
            return {
                'success': False,
                'error': f'Test script not found: {script_path}'
            }
        
        cmd = ['python3', str(script_path)]
        if args:
            cmd.extend(args)
        
        if self.verbose:
            cmd.append('--verbose')
        if self.ci_mode:
            cmd.append('--ci')
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout
                cwd=str(self.repo_root)
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
                'stderr': 'Test suite timed out after 1 hour',
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
    
    def run_master_tests(self) -> Dict[str, Any]:
        """Run comprehensive job DB and build tests"""
        self.log("Starting Master Test Coordination for FFXI Server")
        self.log("=" * 60)
        
        test_results = {}
        
        # 1. Job Database Function Tests
        self.log("Phase 1: Job Database Function Tests")
        self.log("-" * 40)
        
        job_db_script = self.repo_root / 'tools' / 'testing' / 'comprehensive_job_db_test_suite.py'
        job_db_result = self.run_test_suite(job_db_script)
        test_results['job_database_tests'] = job_db_result
        
        if job_db_result['success']:
            self.log("Job Database Tests: PASSED", "INFO")
        else:
            self.log("Job Database Tests: FAILED", "ERROR")
            if self.verbose:
                self.log(f"Error: {job_db_result['stderr']}", "ERROR")
        
        # 2. Comprehensive Build Tests
        self.log("\nPhase 2: Comprehensive Build Tests")
        self.log("-" * 40)
        
        build_test_script = self.repo_root / 'tools' / 'testing' / 'comprehensive_build_test_suite.py'
        build_test_result = self.run_test_suite(build_test_script)
        test_results['build_tests'] = build_test_result
        
        if build_test_result['success']:
            self.log("Build Tests: PASSED", "INFO")
        else:
            self.log("Build Tests: FAILED", "ERROR")
            if self.verbose:
                self.log(f"Error: {build_test_result['stderr']}", "ERROR")
        
        # 3. Integration Validation
        self.log("\nPhase 3: Integration Validation")
        self.log("-" * 40)
        
        integration_result = self.validate_integration()
        test_results['integration_validation'] = integration_result
        
        if integration_result['success']:
            self.log("Integration Validation: PASSED", "INFO")
        else:
            self.log("Integration Validation: FAILED", "ERROR")
        
        # Calculate overall results
        successful_phases = sum(1 for result in test_results.values() if result.get('success', False))
        total_phases = len(test_results)
        success_rate = (successful_phases / total_phases) * 100
        overall_success = success_rate >= 80.0  # Require 80% success
        
        execution_time = (datetime.now() - self.start_time).total_seconds()
        
        summary = {
            'overall_success': overall_success,
            'success_rate': success_rate,
            'successful_phases': successful_phases,
            'total_phases': total_phases,
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        }
        
        self.log("\n" + "=" * 60)
        self.log("MASTER TEST COORDINATION COMPLETE")
        self.log(f"Overall Result: {'PASSED' if overall_success else 'FAILED'}")
        self.log(f"Success Rate: {success_rate:.1f}% ({successful_phases}/{total_phases})")
        self.log(f"Total Execution Time: {execution_time:.2f} seconds")
        self.log("=" * 60)
        
        return {
            'summary': summary,
            'test_phases': test_results
        }
    
    def validate_integration(self) -> Dict[str, Any]:
        """Validate integration between components"""
        self.log("Validating system integration...")
        
        validation_checks = {
            'job_files_exist': self.check_job_files(),
            'build_system_ready': self.check_build_system(),
            'ci_pipeline_compatible': self.check_ci_compatibility(),
            'test_framework_complete': self.check_test_framework()
        }
        
        successful_checks = sum(1 for check in validation_checks.values() if check.get('success', False))
        total_checks = len(validation_checks)
        
        success = successful_checks >= 3  # At least 3/4 checks should pass
        
        return {
            'success': success,
            'successful_checks': successful_checks,
            'total_checks': total_checks,
            'validation_checks': validation_checks
        }
    
    def check_job_files(self) -> Dict[str, Any]:
        """Check that all job files are present"""
        job_utils_dir = self.repo_root / 'scripts' / 'globals' / 'job_utils'
        
        if not job_utils_dir.exists():
            return {'success': False, 'error': 'job_utils directory not found'}
        
        expected_jobs = [
            'warrior.lua', 'monk.lua', 'white_mage.lua', 'black_mage.lua',
            'red_mage.lua', 'thief.lua', 'paladin.lua', 'dark_knight.lua',
            'beastmaster.lua', 'bard.lua', 'ranger.lua', 'samurai.lua',
            'ninja.lua', 'dragoon.lua', 'summoner.lua', 'blue_mage.lua',
            'corsair.lua', 'puppetmaster.lua', 'dancer.lua', 'scholar.lua',
            'geomancer.lua', 'rune_fencer.lua'
        ]
        
        found_jobs = 0
        for job_file in expected_jobs:
            if (job_utils_dir / job_file).exists():
                found_jobs += 1
        
        success = found_jobs == len(expected_jobs)
        
        return {
            'success': success,
            'found_jobs': found_jobs,
            'expected_jobs': len(expected_jobs),
            'completion_rate': (found_jobs / len(expected_jobs)) * 100
        }
    
    def check_build_system(self) -> Dict[str, Any]:
        """Check build system readiness"""
        cmake_file = self.repo_root / 'CMakeLists.txt'
        
        if not cmake_file.exists():
            return {'success': False, 'error': 'CMakeLists.txt not found'}
        
        # Check for key directories
        required_dirs = ['src', 'scripts', 'sql']
        missing_dirs = []
        
        for dir_name in required_dirs:
            if not (self.repo_root / dir_name).exists():
                missing_dirs.append(dir_name)
        
        success = len(missing_dirs) == 0
        
        return {
            'success': success,
            'missing_directories': missing_dirs,
            'cmake_exists': True
        }
    
    def check_ci_compatibility(self) -> Dict[str, Any]:
        """Check CI pipeline compatibility"""
        workflows_dir = self.repo_root / '.github' / 'workflows'
        ci_scripts_dir = self.repo_root / 'tools' / 'ci'
        
        workflows_exist = workflows_dir.exists() and len(list(workflows_dir.glob('*.yml'))) > 0
        ci_scripts_exist = ci_scripts_dir.exists() and len(list(ci_scripts_dir.glob('*.sh'))) > 0
        
        success = workflows_exist and ci_scripts_exist
        
        return {
            'success': success,
            'workflows_exist': workflows_exist,
            'ci_scripts_exist': ci_scripts_exist
        }
    
    def check_test_framework(self) -> Dict[str, Any]:
        """Check test framework completeness"""
        testing_dir = self.repo_root / 'tools' / 'testing'
        
        if not testing_dir.exists():
            return {'success': False, 'error': 'Testing directory not found'}
        
        required_test_files = [
            'comprehensive_job_db_test_suite.py',
            'comprehensive_build_test_suite.py'
        ]
        
        found_files = 0
        for test_file in required_test_files:
            if (testing_dir / test_file).exists():
                found_files += 1
        
        success = found_files == len(required_test_files)
        
        return {
            'success': success,
            'found_test_files': found_files,
            'required_test_files': len(required_test_files)
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save master test results"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"master_test_results_{timestamp}.json"
        
        output_file = self.repo_root / filename
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.log(f"Master test results saved to: {output_file}")
            return str(output_file)
        except Exception as e:
            self.log(f"Failed to save results: {str(e)}", "ERROR")
            return None

def main():
    parser = argparse.ArgumentParser(description='Master Test Coordinator for FFXI Server')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose output')
    parser.add_argument('--ci', action='store_true',
                       help='Run in CI mode (non-interactive)')
    parser.add_argument('--output', '-o', type=str,
                       help='Output file for test results')
    
    args = parser.parse_args()
    
    # Initialize coordinator
    coordinator = MasterTestCoordinator(verbose=args.verbose, ci_mode=args.ci)
    
    try:
        # Run master tests
        results = coordinator.run_master_tests()
        
        # Save results
        output_file = coordinator.save_results(results, args.output)
        
        # Exit with appropriate code
        success = results['summary']['overall_success']
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        coordinator.log("Test execution interrupted by user", "WARNING")
        sys.exit(130)
    except Exception as e:
        coordinator.log(f"Test execution failed: {str(e)}", "CRITICAL")
        sys.exit(1)

if __name__ == '__main__':
    main()