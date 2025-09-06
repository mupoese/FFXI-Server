#!/usr/bin/env python3
"""
Enhanced Performance Monitoring and Benchmarking Tool for LandSandBoat
Provides comprehensive performance analysis and optimization recommendations
"""

import os
import sys
import time
import json
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse

class PerformanceMonitor:
    """Comprehensive performance monitoring for LandSandBoat development"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.metrics = {}
        self.start_time = time.time()
        
    def monitor_build_performance(self) -> Dict:
        """Monitor build performance metrics"""
        print("🔨 Monitoring build performance...")
        
        build_dir = self.project_root / "build"
        if not build_dir.exists():
            print("  ⚠ Build directory not found")
            return {}
        
        # Monitor system resources during build
        initial_cpu = psutil.cpu_percent(interval=1)
        initial_memory = psutil.virtual_memory()
        
        build_start = time.time()
        
        # Run a test build to measure performance
        try:
            os.chdir(build_dir)
            if self._has_ninja():
                result = subprocess.run(['ninja', 'clean'], capture_output=True, text=True)
                build_result = subprocess.run(['ninja'], capture_output=True, text=True, timeout=300)
            elif self._has_make():
                result = subprocess.run(['make', 'clean'], capture_output=True, text=True)
                build_result = subprocess.run(['make', '-j4'], capture_output=True, text=True, timeout=300)
            else:
                print("  ❌ No build system available")
                return {}
            
            build_time = time.time() - build_start
            
            # Collect final system metrics
            final_cpu = psutil.cpu_percent(interval=1)
            final_memory = psutil.virtual_memory()
            
            metrics = {
                'build_time_seconds': build_time,
                'build_success': build_result.returncode == 0,
                'cpu_usage_percent': {
                    'initial': initial_cpu,
                    'final': final_cpu,
                    'average': (initial_cpu + final_cpu) / 2
                },
                'memory_usage_mb': {
                    'initial': initial_memory.used // (1024 * 1024),
                    'final': final_memory.used // (1024 * 1024),
                    'peak': max(initial_memory.used, final_memory.used) // (1024 * 1024)
                },
                'build_system': 'ninja' if self._has_ninja() else 'make'
            }
            
            print(f"  ✓ Build completed in {build_time:.2f} seconds")
            print(f"  📊 Average CPU usage: {metrics['cpu_usage_percent']['average']:.1f}%")
            print(f"  💾 Peak memory usage: {metrics['memory_usage_mb']['peak']} MB")
            
            return metrics
            
        except subprocess.TimeoutExpired:
            print("  ⚠ Build timed out after 5 minutes")
            return {'build_timeout': True}
        except Exception as e:
            print(f"  ❌ Build monitoring failed: {e}")
            return {}
        finally:
            os.chdir(self.project_root)
    
    def analyze_codebase_metrics(self) -> Dict:
        """Analyze codebase complexity and metrics"""
        print("📊 Analyzing codebase metrics...")
        
        metrics = {
            'file_counts': {},
            'line_counts': {},
            'complexity_estimates': {}
        }
        
        # Count different file types
        cpp_files = list(self.project_root.glob("src/**/*.cpp")) + list(self.project_root.glob("src/**/*.h"))
        lua_files = list(self.project_root.glob("scripts/**/*.lua"))
        python_files = list(self.project_root.glob("tools/**/*.py"))
        sql_files = list(self.project_root.glob("sql/**/*.sql"))
        
        metrics['file_counts'] = {
            'cpp': len(cpp_files),
            'lua': len(lua_files),
            'python': len(python_files),
            'sql': len(sql_files)
        }
        
        # Count lines of code
        for file_type, file_list in [
            ('cpp', cpp_files),
            ('lua', lua_files),
            ('python', python_files),
            ('sql', sql_files)
        ]:
            total_lines = 0
            code_lines = 0
            
            for file_path in file_list[:100]:  # Limit to avoid excessive processing
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                        code_lines += sum(1 for line in lines if line.strip() and not line.strip().startswith(('--', '//', '#')))
                except:
                    continue
            
            metrics['line_counts'][file_type] = {
                'total': total_lines,
                'code': code_lines,
                'files_analyzed': min(len(file_list), 100)
            }
        
        # Estimate complexity
        for file_type in ['cpp', 'lua', 'python']:
            if file_type in metrics['line_counts']:
                lines = metrics['line_counts'][file_type]['code']
                files = metrics['file_counts'][file_type]
                
                if files > 0:
                    avg_lines_per_file = lines / min(files, 100)
                    complexity_score = self._calculate_complexity_score(avg_lines_per_file, files)
                    metrics['complexity_estimates'][file_type] = {
                        'average_lines_per_file': avg_lines_per_file,
                        'complexity_score': complexity_score,
                        'maintainability': self._get_maintainability_rating(complexity_score)
                    }
        
        # Print summary
        print(f"  📁 Files: C++({metrics['file_counts']['cpp']}) Lua({metrics['file_counts']['lua']}) Python({metrics['file_counts']['python']})")
        for file_type, data in metrics['line_counts'].items():
            if data['code'] > 0:
                print(f"  📄 {file_type.upper()}: {data['code']:,} lines of code")
        
        return metrics
    
    def benchmark_tools_performance(self) -> Dict:
        """Benchmark development tools performance"""
        print("⚡ Benchmarking development tools...")
        
        benchmarks = {}
        
        # Benchmark vulnerability scanner
        start_time = time.time()
        try:
            result = subprocess.run(['python3', 'tools/vulnerability_scanner.py'], 
                                  capture_output=True, text=True, timeout=60, cwd=self.project_root)
            vuln_time = time.time() - start_time
            benchmarks['vulnerability_scanner'] = {
                'time_seconds': vuln_time,
                'success': result.returncode == 0,
                'output_lines': len(result.stdout.split('\n'))
            }
            print(f"  🔍 Vulnerability scanner: {vuln_time:.2f}s")
        except subprocess.TimeoutExpired:
            benchmarks['vulnerability_scanner'] = {'timeout': True}
            print("  ⚠ Vulnerability scanner timed out")
        except Exception as e:
            print(f"  ❌ Vulnerability scanner benchmark failed: {e}")
        
        # Benchmark log manager
        start_time = time.time()
        try:
            result = subprocess.run(['python3', 'tools/log_manager.py', '--scan'], 
                                  capture_output=True, text=True, timeout=30, cwd=self.project_root)
            log_time = time.time() - start_time
            benchmarks['log_manager'] = {
                'time_seconds': log_time,
                'success': result.returncode == 0
            }
            print(f"  📝 Log manager: {log_time:.2f}s")
        except Exception as e:
            print(f"  ❌ Log manager benchmark failed: {e}")
        
        # Benchmark CI checks
        ci_scripts = ['general.sh', 'git.sh', 'python.sh']
        for script in ci_scripts:
            script_path = self.project_root / "tools" / "ci" / script
            if script_path.exists():
                start_time = time.time()
                try:
                    result = subprocess.run(['bash', str(script_path)], 
                                          capture_output=True, text=True, timeout=30, cwd=self.project_root)
                    script_time = time.time() - start_time
                    benchmarks[f'ci_{script[:-3]}'] = {
                        'time_seconds': script_time,
                        'success': result.returncode == 0
                    }
                    print(f"  🔧 CI {script}: {script_time:.2f}s")
                except Exception as e:
                    print(f"  ❌ CI {script} benchmark failed: {e}")
        
        return benchmarks
    
    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        print("📋 Generating performance report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_system_info(),
            'build_performance': self.monitor_build_performance(),
            'codebase_metrics': self.analyze_codebase_metrics(),
            'tools_benchmarks': self.benchmark_tools_performance(),
            'recommendations': []
        }
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(report)
        
        # Save report
        report_file = self.project_root / "logs" / "development" / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"  💾 Report saved to: {report_file}")
        return report
    
    def _has_ninja(self) -> bool:
        """Check if ninja build system is available"""
        try:
            subprocess.run(['ninja', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def _has_make(self) -> bool:
        """Check if make build system is available"""
        try:
            subprocess.run(['make', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def _calculate_complexity_score(self, avg_lines: float, file_count: int) -> float:
        """Calculate complexity score based on lines and file count"""
        # Simple heuristic: complexity increases with lines per file and total files
        base_score = min(avg_lines / 100, 1.0)  # Normalize to 0-1
        file_factor = min(file_count / 1000, 1.0)  # Normalize to 0-1
        return (base_score * 0.7) + (file_factor * 0.3)
    
    def _get_maintainability_rating(self, complexity_score: float) -> str:
        """Get maintainability rating from complexity score"""
        if complexity_score < 0.3:
            return "Excellent"
        elif complexity_score < 0.5:
            return "Good"
        elif complexity_score < 0.7:
            return "Fair"
        else:
            return "Needs Attention"
    
    def _get_system_info(self) -> Dict:
        """Get system information"""
        return {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total // (1024**3),
            'disk_free_gb': psutil.disk_usage('.').free // (1024**3),
            'python_version': sys.version.split()[0],
            'platform': sys.platform
        }
    
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Build performance recommendations
        if 'build_performance' in report and 'build_time_seconds' in report['build_performance']:
            build_time = report['build_performance']['build_time_seconds']
            if build_time > 300:  # 5 minutes
                recommendations.append("Consider using ninja build system for faster builds")
                recommendations.append("Enable ccache for C++ compilation caching")
            
            if 'cpu_usage_percent' in report['build_performance']:
                cpu_usage = report['build_performance']['cpu_usage_percent']['average']
                if cpu_usage < 50:
                    recommendations.append("Increase parallel build jobs (-j flag) to utilize more CPU cores")
        
        # Codebase recommendations
        if 'codebase_metrics' in report:
            for lang, metrics in report['codebase_metrics'].get('complexity_estimates', {}).items():
                if metrics['maintainability'] in ['Fair', 'Needs Attention']:
                    recommendations.append(f"Consider refactoring {lang.upper()} code to reduce complexity")
        
        # Tools performance recommendations
        if 'tools_benchmarks' in report:
            for tool, data in report['tools_benchmarks'].items():
                if isinstance(data, dict) and data.get('time_seconds', 0) > 30:
                    recommendations.append(f"Optimize {tool} performance - currently taking {data['time_seconds']:.1f}s")
        
        # System recommendations
        if 'system_info' in report:
            memory_gb = report['system_info']['memory_total_gb']
            if memory_gb < 8:
                recommendations.append("Consider upgrading system memory for better build performance")
            
            disk_free = report['system_info']['disk_free_gb']
            if disk_free < 10:
                recommendations.append("Free up disk space for optimal development environment")
        
        if not recommendations:
            recommendations.append("System performance is optimal - no specific recommendations")
        
        return recommendations

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='LandSandBoat Performance Monitor')
    parser.add_argument('--build', action='store_true', help='Monitor build performance only')
    parser.add_argument('--metrics', action='store_true', help='Analyze codebase metrics only')
    parser.add_argument('--tools', action='store_true', help='Benchmark tools only')
    parser.add_argument('--report', action='store_true', help='Generate full performance report')
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    monitor = PerformanceMonitor(project_root)
    
    print("🚀 LandSandBoat Performance Monitor")
    print("==================================================")
    
    if args.build:
        monitor.monitor_build_performance()
    elif args.metrics:
        monitor.analyze_codebase_metrics()
    elif args.tools:
        monitor.benchmark_tools_performance()
    elif args.report or not any([args.build, args.metrics, args.tools]):
        # Default to full report
        report = monitor.generate_performance_report()
        
        print("\n📊 Performance Summary:")
        print("==================================================")
        if 'build_performance' in report and 'build_time_seconds' in report['build_performance']:
            print(f"Build Time: {report['build_performance']['build_time_seconds']:.2f}s")
        
        if 'codebase_metrics' in report:
            for lang, data in report['codebase_metrics']['file_counts'].items():
                if data > 0:
                    print(f"{lang.upper()} Files: {data}")
        
        print(f"\n💡 Recommendations ({len(report['recommendations'])}):")
        for i, rec in enumerate(report['recommendations'][:5], 1):
            print(f"  {i}. {rec}")
        
        if len(report['recommendations']) > 5:
            print(f"  ... and {len(report['recommendations']) - 5} more (see report)")

if __name__ == "__main__":
    main()