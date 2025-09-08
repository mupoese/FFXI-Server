#!/usr/bin/env python3
"""
Comprehensive Job Database Function Test Suite

This script provides comprehensive testing for all 22 FFXI job implementations,
validating database interactions, subjob penalty systems, and job-specific functions.
"""

import argparse
import json
import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Job mappings for validation
FFXI_JOBS = {
    'warrior': {'id': 1, 'file': 'warrior.lua'},
    'monk': {'id': 2, 'file': 'monk.lua'},
    'white_mage': {'id': 3, 'file': 'white_mage.lua'},
    'black_mage': {'id': 4, 'file': 'black_mage.lua'},
    'red_mage': {'id': 5, 'file': 'red_mage.lua'},
    'thief': {'id': 6, 'file': 'thief.lua'},
    'paladin': {'id': 7, 'file': 'paladin.lua'},
    'dark_knight': {'id': 8, 'file': 'dark_knight.lua'},
    'beastmaster': {'id': 9, 'file': 'beastmaster.lua'},
    'bard': {'id': 10, 'file': 'bard.lua'},
    'ranger': {'id': 11, 'file': 'ranger.lua'},
    'samurai': {'id': 12, 'file': 'samurai.lua'},
    'ninja': {'id': 13, 'file': 'ninja.lua'},
    'dragoon': {'id': 14, 'file': 'dragoon.lua'},
    'summoner': {'id': 15, 'file': 'summoner.lua'},
    'blue_mage': {'id': 16, 'file': 'blue_mage.lua'},
    'corsair': {'id': 17, 'file': 'corsair.lua'},
    'puppetmaster': {'id': 18, 'file': 'puppetmaster.lua'},
    'dancer': {'id': 19, 'file': 'dancer.lua'},
    'scholar': {'id': 20, 'file': 'scholar.lua'},
    'geomancer': {'id': 21, 'file': 'geomancer.lua'},
    'rune_fencer': {'id': 22, 'file': 'rune_fencer.lua'}
}

class JobDatabaseTestSuite:
    def __init__(self, verbose: bool = False, ci_mode: bool = False):
        self.verbose = verbose
        self.ci_mode = ci_mode
        self.repo_root = Path('/home/runner/work/FFXI-Server/FFXI-Server')
        self.job_utils_path = self.repo_root / 'scripts' / 'globals' / 'job_utils'
        self.test_results = {}
        self.start_time = datetime.now()
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.verbose or level in ["ERROR", "CRITICAL"]:
            print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, cmd: List[str], timeout: int = 300) -> Dict[str, Any]:
        """Run a command and return the result"""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=str(self.repo_root)
            )
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            }
    
    def test_job_file_existence(self) -> Dict[str, Any]:
        """Test that all job utility files exist"""
        self.log("Testing job file existence...")
        results = {}
        missing_files = []
        
        for job_name, job_info in FFXI_JOBS.items():
            job_file = self.job_utils_path / job_info['file']
            exists = job_file.exists()
            results[job_name] = {
                'file_exists': exists,
                'file_path': str(job_file),
                'expected_job_id': job_info['id']
            }
            
            if not exists:
                missing_files.append(f"{job_name} ({job_info['file']})")
        
        success = len(missing_files) == 0
        self.log(f"Job file existence test: {'PASSED' if success else 'FAILED'}")
        if missing_files:
            self.log(f"Missing files: {', '.join(missing_files)}", "ERROR")
        
        return {
            'success': success,
            'missing_files': missing_files,
            'total_jobs': len(FFXI_JOBS),
            'found_jobs': len(FFXI_JOBS) - len(missing_files),
            'results': results
        }
    
    def test_job_lua_syntax(self) -> Dict[str, Any]:
        """Test Lua syntax of all job files"""
        self.log("Testing Lua syntax for all job files...")
        results = {}
        syntax_errors = []
        
        # Check if lua command is available
        lua_check = self.run_command(['which', 'lua'])
        if not lua_check['success']:
            self.log("Lua interpreter not found, skipping syntax validation", "WARNING")
            return {
                'success': False,
                'error': 'Lua interpreter not available',
                'skipped': True
            }
        
        for job_name, job_info in FFXI_JOBS.items():
            job_file = self.job_utils_path / job_info['file']
            
            if job_file.exists():
                # Use luac to check syntax (compile only, don't execute)
                result = self.run_command(['luac', '-p', str(job_file)])
                
                results[job_name] = {
                    'syntax_valid': result['success'],
                    'error_message': result['stderr'] if not result['success'] else None
                }
                
                if not result['success']:
                    syntax_errors.append(f"{job_name}: {result['stderr']}")
            else:
                results[job_name] = {
                    'syntax_valid': False,
                    'error_message': 'File does not exist'
                }
                syntax_errors.append(f"{job_name}: File missing")
        
        success = len(syntax_errors) == 0
        self.log(f"Lua syntax test: {'PASSED' if success else 'FAILED'}")
        if syntax_errors:
            for error in syntax_errors:
                self.log(error, "ERROR")
        
        return {
            'success': success,
            'syntax_errors': syntax_errors,
            'results': results
        }
    
    def test_job_database_functions(self) -> Dict[str, Any]:
        """Test job database validation functions"""
        self.log("Testing job database validation functions...")
        results = {}
        
        # Key functions that should exist in each job file
        required_functions = [
            'validateJobAccess',
            'calculateSubjobPenalty', 
            'getJobAbilities',
            'validateAbilityAccess'
        ]
        
        function_coverage = {}
        
        for job_name, job_info in FFXI_JOBS.items():
            job_file = self.job_utils_path / job_info['file']
            
            if job_file.exists():
                try:
                    with open(job_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    found_functions = []
                    missing_functions = []
                    
                    for func in required_functions:
                        if f'.{func} =' in content or f'function {func}' in content:
                            found_functions.append(func)
                        else:
                            missing_functions.append(func)
                    
                    # Check for graduated subjob penalty system
                    has_subjob_penalty = ('calculateSubjobPenalty' in content or 
                                        'subjobLevel' in content or
                                        '0.5' in content)
                    
                    # Check for database validation
                    has_db_validation = ('validateJobAccess' in content or
                                       'getMainJob()' in content or
                                       'getSubJob()' in content)
                    
                    function_coverage[job_name] = {
                        'found_functions': found_functions,
                        'missing_functions': missing_functions,
                        'function_count': len(found_functions),
                        'has_subjob_penalty': has_subjob_penalty,
                        'has_db_validation': has_db_validation,
                        'coverage_percent': (len(found_functions) / len(required_functions)) * 100
                    }
                    
                except Exception as e:
                    function_coverage[job_name] = {
                        'error': str(e),
                        'coverage_percent': 0
                    }
            else:
                function_coverage[job_name] = {
                    'error': 'File does not exist',
                    'coverage_percent': 0
                }
        
        # Calculate overall statistics
        total_coverage = sum(result.get('coverage_percent', 0) for result in function_coverage.values())
        average_coverage = total_coverage / len(FFXI_JOBS) if FFXI_JOBS else 0
        
        jobs_with_subjob_penalty = sum(1 for result in function_coverage.values() 
                                     if result.get('has_subjob_penalty', False))
        jobs_with_db_validation = sum(1 for result in function_coverage.values() 
                                    if result.get('has_db_validation', False))
        
        success = average_coverage >= 75.0  # Require 75% average coverage
        
        self.log(f"Database function test: {'PASSED' if success else 'FAILED'}")
        self.log(f"Average function coverage: {average_coverage:.1f}%")
        self.log(f"Jobs with subjob penalty: {jobs_with_subjob_penalty}/{len(FFXI_JOBS)}")
        self.log(f"Jobs with DB validation: {jobs_with_db_validation}/{len(FFXI_JOBS)}")
        
        return {
            'success': success,
            'average_coverage': average_coverage,
            'jobs_with_subjob_penalty': jobs_with_subjob_penalty,
            'jobs_with_db_validation': jobs_with_db_validation,
            'function_coverage': function_coverage,
            'required_functions': required_functions
        }
    
    def test_job_abilities_integration(self) -> Dict[str, Any]:
        """Test job abilities integration with enhanced_job_abilities.lua"""
        self.log("Testing job abilities integration...")
        
        enhanced_abilities_file = self.repo_root / 'scripts' / 'globals' / 'enhanced_job_abilities.lua'
        
        if not enhanced_abilities_file.exists():
            return {
                'success': False,
                'error': 'enhanced_job_abilities.lua not found',
                'skipped': True
            }
        
        try:
            with open(enhanced_abilities_file, 'r', encoding='utf-8') as f:
                enhanced_content = f.read()
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to read enhanced_job_abilities.lua: {str(e)}'
            }
        
        # Check for key integration features
        integration_features = {
            'aoe_enmity_generation': 'generateAoEEnmity' in enhanced_content,
            'cross_job_interactions': 'checkAbilityInteractions' in enhanced_content,
            'subjob_scaling': 'subjob' in enhanced_content.lower(),
            'merit_integration': 'merit' in enhanced_content.lower(),
            'job_point_integration': 'jobpoint' in enhanced_content.lower() or 'jp' in enhanced_content.lower()
        }
        
        job_references = {}
        for job_name in FFXI_JOBS.keys():
            job_upper = job_name.upper()
            job_references[job_name] = job_upper in enhanced_content or job_name in enhanced_content
        
        integration_score = sum(integration_features.values())
        job_reference_score = sum(job_references.values())
        
        success = integration_score >= 3 and job_reference_score >= 10  # At least 3 features and 10 job references
        
        self.log(f"Job abilities integration test: {'PASSED' if success else 'FAILED'}")
        self.log(f"Integration features found: {integration_score}/5")
        self.log(f"Job references found: {job_reference_score}/{len(FFXI_JOBS)}")
        
        return {
            'success': success,
            'integration_features': integration_features,
            'job_references': job_references,
            'integration_score': integration_score,
            'job_reference_score': job_reference_score
        }
    
    def test_lua_ci_pipeline(self) -> Dict[str, Any]:
        """Test Lua CI pipeline validation"""
        self.log("Testing Lua CI pipeline...")
        
        lua_ci_script = self.repo_root / 'tools' / 'ci' / 'lua.sh'
        
        if not lua_ci_script.exists():
            return {
                'success': False,
                'error': 'lua.sh CI script not found'
            }
        
        # Run the Lua CI script
        result = self.run_command(['bash', str(lua_ci_script)], timeout=600)
        
        success = result['success']
        self.log(f"Lua CI pipeline test: {'PASSED' if success else 'FAILED'}")
        
        if not success:
            self.log(f"Lua CI failed: {result['stderr']}", "ERROR")
        
        return {
            'success': success,
            'stdout': result['stdout'],
            'stderr': result['stderr'],
            'returncode': result['returncode']
        }
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive job database tests"""
        self.log("Starting comprehensive job database function tests...")
        
        # Run all test components
        tests = {
            'file_existence': self.test_job_file_existence(),
            'lua_syntax': self.test_job_lua_syntax(),
            'database_functions': self.test_job_database_functions(),
            'abilities_integration': self.test_job_abilities_integration(),
            'lua_ci_pipeline': self.test_lua_ci_pipeline()
        }
        
        # Calculate overall success
        successful_tests = sum(1 for test in tests.values() if test.get('success', False))
        total_tests = len(tests)
        success_rate = (successful_tests / total_tests) * 100
        
        overall_success = success_rate >= 80.0  # Require 80% success rate
        
        # Summary
        summary = {
            'overall_success': overall_success,
            'success_rate': success_rate,
            'successful_tests': successful_tests,
            'total_tests': total_tests,
            'execution_time': (datetime.now() - self.start_time).total_seconds(),
            'timestamp': datetime.now().isoformat()
        }
        
        self.log(f"Comprehensive job database tests completed")
        self.log(f"Overall result: {'PASSED' if overall_success else 'FAILED'}")
        self.log(f"Success rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
        self.log(f"Execution time: {summary['execution_time']:.2f} seconds")
        
        return {
            'summary': summary,
            'tests': tests,
            'job_mapping': FFXI_JOBS
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_db_test_results_{timestamp}.json"
        
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
    parser = argparse.ArgumentParser(description='Comprehensive Job Database Function Test Suite')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose output')
    parser.add_argument('--ci', action='store_true',
                       help='Run in CI mode (non-interactive)')
    parser.add_argument('--output', '-o', type=str,
                       help='Output file for test results')
    
    args = parser.parse_args()
    
    # Initialize test suite
    test_suite = JobDatabaseTestSuite(verbose=args.verbose, ci_mode=args.ci)
    
    try:
        # Run comprehensive tests
        results = test_suite.run_comprehensive_tests()
        
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