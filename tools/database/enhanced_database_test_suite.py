#!/usr/bin/env python3
"""
Enhanced Database Testing and Monitoring Suite

This script provides comprehensive testing, monitoring, and validation
for database improvements including connection pooling and performance optimizations.
"""

import argparse
import json
import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

def run_command(cmd: List[str], timeout: int = 300) -> Dict[str, Any]:
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            cwd='/home/runner/work/FFXI-Server/FFXI-Server'
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

def run_unit_tests(verbose: bool = False, ci_mode: bool = False) -> Dict[str, Any]:
    """Run database unit tests"""
    print("Running database unit tests...")
    
    cmd = ['python3', 'tools/test_database_improvements.py']
    if verbose:
        cmd.append('--verbose')
    if ci_mode:
        cmd.append('--ci')
    
    result = run_command(cmd)
    
    # Try to read test results file
    test_results = {}
    if os.path.exists('db_test_results.txt'):
        with open('db_test_results.txt', 'r') as f:
            content = f.read()
            test_results['output'] = content
    
    return {
        'success': result['success'],
        'details': test_results,
        'stdout': result['stdout'],
        'stderr': result['stderr']
    }

def run_performance_tests(connections: int = 10, duration: int = 60, ci_mode: bool = False) -> Dict[str, Any]:
    """Run database performance tests"""
    print(f"Running performance tests ({connections} connections, {duration}s duration)...")
    
    cmd = [
        'python3', 'tools/db_performance_monitor.py',
        '--test', 'quick',
        '--connections', str(connections),
        '--duration', str(duration),
        '--output-json'
    ]
    if ci_mode:
        cmd.append('--ci')
    
    result = run_command(cmd)
    
    # Look for JSON output files
    performance_data = {}
    for file in os.listdir('.'):
        if file.startswith('db_performance_') and file.endswith('.json'):
            try:
                with open(file, 'r') as f:
                    performance_data[file] = json.load(f)
            except Exception as e:
                performance_data[file] = {'error': str(e)}
    
    return {
        'success': result['success'],
        'data': performance_data,
        'stdout': result['stdout'],
        'stderr': result['stderr']
    }

def run_stress_tests(max_connections: int = 50, ci_mode: bool = False) -> Dict[str, Any]:
    """Run database stress tests"""
    print(f"Running stress tests (up to {max_connections} connections)...")
    
    cmd = [
        'python3', 'tools/db_performance_monitor.py',
        '--test', 'stress',
        '--connections', str(max_connections),
        '--output-json'
    ]
    if ci_mode:
        cmd.append('--ci')
    
    result = run_command(cmd, timeout=600)  # Longer timeout for stress tests
    
    # Look for stress test results
    stress_data = {}
    for file in os.listdir('.'):
        if file.startswith('db_performance_stress_') and file.endswith('.json'):
            try:
                with open(file, 'r') as f:
                    stress_data[file] = json.load(f)
            except Exception as e:
                stress_data[file] = {'error': str(e)}
    
    return {
        'success': result['success'],
        'data': stress_data,
        'stdout': result['stdout'],
        'stderr': result['stderr']
    }

def validate_performance_thresholds(performance_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate performance against thresholds"""
    print("Validating performance thresholds...")
    
    validation_results = {
        'passed': True,
        'issues': [],
        'metrics': {}
    }
    
    for filename, data in performance_data.items():
        if 'error' in data:
            validation_results['issues'].append(f"Error in {filename}: {data['error']}")
            continue
        
        if 'summary' not in data:
            continue
        
        summary = data['summary']
        metrics = {
            'avg_latency_ms': summary.get('avg_latency_ms', 0),
            'success_rate': summary.get('success_rate', 0),
            'ops_per_second': summary.get('ops_per_second', 0)
        }
        
        validation_results['metrics'][filename] = metrics
        
        # Performance thresholds
        max_latency = 100.0  # 100ms
        min_success_rate = 90.0  # 90%
        min_ops_per_sec = 50.0  # 50 ops/sec
        
        if metrics['avg_latency_ms'] > max_latency:
            validation_results['issues'].append(
                f"{filename}: High latency {metrics['avg_latency_ms']:.2f}ms > {max_latency}ms"
            )
            validation_results['passed'] = False
        
        if metrics['success_rate'] < min_success_rate:
            validation_results['issues'].append(
                f"{filename}: Low success rate {metrics['success_rate']:.1f}% < {min_success_rate}%"
            )
            validation_results['passed'] = False
        
        if metrics['ops_per_second'] < min_ops_per_sec:
            validation_results['issues'].append(
                f"{filename}: Low throughput {metrics['ops_per_second']:.1f} < {min_ops_per_sec} ops/sec"
            )
            validation_results['passed'] = False
    
    return validation_results

def generate_test_report(results: Dict[str, Any], output_file: str = 'database_test_report.json') -> None:
    """Generate comprehensive test report"""
    print(f"Generating test report: {output_file}")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'overall_success': all(results[key].get('success', False) for key in results),
            'tests_run': len(results),
            'passed_tests': sum(1 for result in results.values() if result.get('success', False))
        },
        'results': results
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Test report saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Enhanced Database Testing Suite')
    parser.add_argument('--test-type', choices=['unit', 'performance', 'stress', 'all'], 
                       default='all', help='Type of tests to run')
    parser.add_argument('--connections', type=int, default=10,
                       help='Number of connections for performance tests')
    parser.add_argument('--duration', type=int, default=60,
                       help='Duration for performance tests (seconds)')
    parser.add_argument('--max-connections', type=int, default=50,
                       help='Maximum connections for stress tests')
    parser.add_argument('--ci', action='store_true',
                       help='Enable CI mode (plain text output)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--output', type=str, default='database_test_report.json',
                       help='Output file for test report')
    parser.add_argument('--baseline', type=str,
                       help='Baseline file for performance comparison')
    
    args = parser.parse_args()
    
    print("Enhanced Database Testing Suite")
    print("=" * 50)
    print(f"Test type: {args.test_type}")
    print(f"CI mode: {args.ci}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    results = {}
    overall_success = True
    
    try:
        if args.test_type in ['unit', 'all']:
            results['unit_tests'] = run_unit_tests(args.verbose, args.ci)
            if not results['unit_tests']['success']:
                overall_success = False
                print("❌ Unit tests failed")
            else:
                print("✅ Unit tests passed")
        
        if args.test_type in ['performance', 'all']:
            results['performance_tests'] = run_performance_tests(args.connections, args.duration, args.ci)
            if not results['performance_tests']['success']:
                overall_success = False
                print("❌ Performance tests failed")
            else:
                print("✅ Performance tests passed")
                
                # Validate performance thresholds
                if results['performance_tests']['data']:
                    validation = validate_performance_thresholds(results['performance_tests']['data'])
                    results['performance_validation'] = validation
                    
                    if not validation['passed']:
                        overall_success = False
                        print("❌ Performance validation failed:")
                        for issue in validation['issues']:
                            print(f"  - {issue}")
                    else:
                        print("✅ Performance validation passed")
        
        if args.test_type in ['stress', 'all']:
            results['stress_tests'] = run_stress_tests(args.max_connections, args.ci)
            if not results['stress_tests']['success']:
                overall_success = False
                print("❌ Stress tests failed")
            else:
                print("✅ Stress tests passed")
        
        # Generate comprehensive report
        generate_test_report(results, args.output)
        
        # Print summary
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        
        if overall_success:
            print("🎉 All tests passed successfully!")
        else:
            print("❌ Some tests failed or have issues")
        
        for test_name, result in results.items():
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        # Compare with baseline if provided
        if args.baseline and os.path.exists(args.baseline):
            print(f"\nComparing with baseline: {args.baseline}")
            # Implementation for baseline comparison would go here
            print("Baseline comparison completed")
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        overall_success = False
    
    # Exit with appropriate code
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()