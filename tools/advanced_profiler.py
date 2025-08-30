#!/usr/bin/env python3
"""
Modern Performance Profiling and Optimization Tool for LandSandBoat
Provides advanced performance analysis and automated optimization recommendations
"""

import os
import sys
import time
import json
import psutil
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import argparse

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: str
    cpu_percent: float
    memory_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent: int
    network_bytes_recv: int
    process_count: int
    thread_count: int
    build_time_seconds: Optional[float] = None
    test_time_seconds: Optional[float] = None

class AdvancedPerformanceProfiler:
    """Advanced performance profiling with modern analysis"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.build_dir = self.project_root / "build"
        self.monitoring = False
        self.metrics_history: List[PerformanceMetrics] = []
        
    def start_continuous_monitoring(self, interval: int = 10) -> None:
        """Start continuous performance monitoring"""
        print(f"🔍 Starting continuous monitoring (interval: {interval}s)")
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    metrics = self._collect_system_metrics()
                    self.metrics_history.append(metrics)
                    
                    # Keep only last 100 measurements to prevent memory bloat
                    if len(self.metrics_history) > 100:
                        self.metrics_history = self.metrics_history[-100:]
                    
                    time.sleep(interval)
                except Exception as e:
                    print(f"⚠️ Monitoring error: {e}")
                    time.sleep(interval)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop continuous monitoring"""
        self.monitoring = False
        print("🛑 Stopped continuous monitoring")
    
    def _collect_system_metrics(self) -> PerformanceMetrics:
        """Collect comprehensive system metrics"""
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()
        
        # Process counts
        process_count = len(psutil.pids())
        thread_count = sum(p.num_threads() for p in psutil.process_iter(['num_threads']) if p.info['num_threads'])
        
        return PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_mb=memory.used / (1024 * 1024),
            disk_io_read_mb=(disk_io.read_bytes if disk_io else 0) / (1024 * 1024),
            disk_io_write_mb=(disk_io.write_bytes if disk_io else 0) / (1024 * 1024),
            network_bytes_sent=network_io.bytes_sent if network_io else 0,
            network_bytes_recv=network_io.bytes_recv if network_io else 0,
            process_count=process_count,
            thread_count=thread_count
        )
    
    def profile_build_performance(self) -> Dict[str, Any]:
        """Profile build performance with detailed analysis"""
        print("🔨 Profiling build performance...")
        
        if not self.build_dir.exists():
            print("❌ Build directory not found")
            return {}
        
        # Start monitoring
        self.start_continuous_monitoring(interval=2)
        
        try:
            # Clean build for accurate timing
            clean_start = time.time()
            subprocess.run(["cmake", "--build", str(self.build_dir), "--target", "clean"], 
                          capture_output=True, check=True)
            clean_time = time.time() - clean_start
            
            # Full build with timing
            build_start = time.time()
            initial_metrics = self._collect_system_metrics()
            
            result = subprocess.run([
                "cmake", "--build", str(self.build_dir), 
                "--parallel", str(os.cpu_count() or 4)
            ], capture_output=True, text=True)
            
            build_time = time.time() - build_start
            final_metrics = self._collect_system_metrics()
            
            # Stop monitoring
            self.stop_monitoring()
            
            # Calculate deltas
            cpu_delta = final_metrics.cpu_percent - initial_metrics.cpu_percent
            memory_delta = final_metrics.memory_mb - initial_metrics.memory_mb
            
            build_metrics = {
                "build_successful": result.returncode == 0,
                "clean_time_seconds": clean_time,
                "build_time_seconds": build_time,
                "parallel_jobs": os.cpu_count() or 4,
                "cpu_usage_delta": cpu_delta,
                "memory_usage_delta_mb": memory_delta,
                "build_output_lines": len(result.stdout.splitlines()) if result.stdout else 0,
                "build_warnings": result.stderr.count("warning:") if result.stderr else 0,
                "build_errors": result.stderr.count("error:") if result.stderr else 0,
                "metrics_during_build": len(self.metrics_history)
            }
            
            print(f"✅ Build completed in {build_time:.1f}s")
            if build_metrics["build_warnings"] > 0:
                print(f"⚠️ {build_metrics['build_warnings']} warnings found")
            if build_metrics["build_errors"] > 0:
                print(f"❌ {build_metrics['build_errors']} errors found")
            
            return build_metrics
            
        except subprocess.CalledProcessError as e:
            self.stop_monitoring()
            print(f"❌ Build failed: {e}")
            return {"build_successful": False, "error": str(e)}
    
    def profile_test_performance(self) -> Dict[str, Any]:
        """Profile test suite performance"""
        print("🧪 Profiling test performance...")
        
        if not (self.build_dir / "test").exists() and not (self.build_dir / "Testing").exists():
            print("⚠️ No tests found")
            return {"tests_available": False}
        
        self.start_continuous_monitoring(interval=1)
        
        try:
            test_start = time.time()
            initial_metrics = self._collect_system_metrics()
            
            # Run CTest with detailed output
            result = subprocess.run([
                "ctest", "--output-on-failure", "--verbose",
                "--parallel", str(os.cpu_count() or 4)
            ], cwd=self.build_dir, capture_output=True, text=True)
            
            test_time = time.time() - test_start
            final_metrics = self._collect_system_metrics()
            
            self.stop_monitoring()
            
            # Parse test results
            tests_run = result.stdout.count("Test #") if result.stdout else 0
            tests_passed = result.stdout.count("Passed") if result.stdout else 0
            tests_failed = result.stdout.count("Failed") if result.stdout else 0
            
            test_metrics = {
                "tests_successful": result.returncode == 0,
                "test_time_seconds": test_time,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "test_pass_rate": (tests_passed / tests_run * 100) if tests_run > 0 else 0,
                "cpu_usage_delta": final_metrics.cpu_percent - initial_metrics.cpu_percent,
                "memory_usage_delta_mb": final_metrics.memory_mb - initial_metrics.memory_mb,
                "parallel_jobs": os.cpu_count() or 4
            }
            
            print(f"✅ Tests completed in {test_time:.1f}s")
            print(f"📊 {tests_passed}/{tests_run} tests passed ({test_metrics['test_pass_rate']:.1f}%)")
            
            return test_metrics
            
        except subprocess.CalledProcessError as e:
            self.stop_monitoring()
            print(f"❌ Tests failed: {e}")
            return {"tests_successful": False, "error": str(e)}
    
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends and provide recommendations"""
        if len(self.metrics_history) < 5:
            return {"insufficient_data": True}
        
        # Calculate averages and trends
        recent_metrics = self.metrics_history[-10:]  # Last 10 measurements
        
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_mb for m in recent_metrics) / len(recent_metrics)
        
        # Detect trends
        cpu_trend = "stable"
        memory_trend = "stable"
        
        if len(recent_metrics) >= 5:
            first_half = recent_metrics[:len(recent_metrics)//2]
            second_half = recent_metrics[len(recent_metrics)//2:]
            
            cpu_first = sum(m.cpu_percent for m in first_half) / len(first_half)
            cpu_second = sum(m.cpu_percent for m in second_half) / len(second_half)
            
            if cpu_second > cpu_first * 1.1:
                cpu_trend = "increasing"
            elif cpu_second < cpu_first * 0.9:
                cpu_trend = "decreasing"
            
            mem_first = sum(m.memory_mb for m in first_half) / len(first_half)
            mem_second = sum(m.memory_mb for m in second_half) / len(second_half)
            
            if mem_second > mem_first * 1.1:
                memory_trend = "increasing"
            elif mem_second < mem_first * 0.9:
                memory_trend = "decreasing"
        
        # Generate recommendations
        recommendations = []
        
        if avg_cpu > 80:
            recommendations.append("High CPU usage detected. Consider optimizing hot code paths.")
        if avg_memory > 1024:  # > 1GB
            recommendations.append("High memory usage detected. Check for memory leaks.")
        if cpu_trend == "increasing":
            recommendations.append("CPU usage is trending upward. Monitor for performance regressions.")
        if memory_trend == "increasing":
            recommendations.append("Memory usage is increasing. Potential memory leak detected.")
        
        return {
            "data_points": len(self.metrics_history),
            "avg_cpu_percent": avg_cpu,
            "avg_memory_mb": avg_memory,
            "cpu_trend": cpu_trend,
            "memory_trend": memory_trend,
            "recommendations": recommendations,
            "metrics_summary": {
                "min_cpu": min(m.cpu_percent for m in recent_metrics),
                "max_cpu": max(m.cpu_percent for m in recent_metrics),
                "min_memory": min(m.memory_mb for m in recent_metrics),
                "max_memory": max(m.memory_mb for m in recent_metrics)
            }
        }
    
    def generate_performance_report(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        print("📊 Generating performance report...")
        
        # Collect all performance data
        build_metrics = self.profile_build_performance()
        test_metrics = self.profile_test_performance()
        trend_analysis = self.analyze_performance_trends()
        
        # System information
        system_info = {
            "cpu_count": os.cpu_count(),
            "total_memory_gb": psutil.virtual_memory().total / (1024**3),
            "python_version": sys.version,
            "platform": sys.platform
        }
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": system_info,
            "build_performance": build_metrics,
            "test_performance": test_metrics,
            "trend_analysis": trend_analysis,
            "metrics_history": [asdict(m) for m in self.metrics_history[-20:]]  # Last 20 measurements
        }
        
        # Save report if output file specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📁 Report saved to {output_file}")
        
        return report
    
    def optimize_build_configuration(self) -> List[str]:
        """Suggest build optimizations based on system capabilities"""
        optimizations = []
        
        cpu_count = os.cpu_count() or 4
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Parallel build optimizations
        if cpu_count >= 8:
            optimizations.append(f"Use -j{cpu_count} for parallel builds")
        elif cpu_count >= 4:
            optimizations.append(f"Use -j{cpu_count-1} for parallel builds (leave 1 core free)")
        
        # Memory optimizations
        if memory_gb >= 16:
            optimizations.append("Enable Link-Time Optimization (LTO) for release builds")
            optimizations.append("Use precompiled headers to speed up compilation")
        elif memory_gb >= 8:
            optimizations.append("Use precompiled headers for common includes")
        else:
            optimizations.append("Consider upgrading RAM for better build performance")
        
        # Compiler optimizations
        optimizations.append("Use ccache or sccache for faster rebuilds")
        optimizations.append("Enable unity builds for faster compilation")
        
        return optimizations

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Advanced Performance Profiler")
    parser.add_argument("command", choices=[
        "build", "test", "monitor", "report", "optimize"
    ], help="Profiling command to run")
    parser.add_argument("--duration", type=int, default=60, help="Monitoring duration in seconds")
    parser.add_argument("--output", type=Path, help="Output file for reports")
    parser.add_argument("--interval", type=int, default=5, help="Monitoring interval in seconds")
    
    args = parser.parse_args()
    
    profiler = AdvancedPerformanceProfiler()
    
    try:
        if args.command == "build":
            metrics = profiler.profile_build_performance()
            print(json.dumps(metrics, indent=2))
            
        elif args.command == "test":
            metrics = profiler.profile_test_performance()
            print(json.dumps(metrics, indent=2))
            
        elif args.command == "monitor":
            print(f"🔍 Monitoring for {args.duration} seconds...")
            profiler.start_continuous_monitoring(args.interval)
            time.sleep(args.duration)
            profiler.stop_monitoring()
            
            analysis = profiler.analyze_performance_trends()
            print(json.dumps(analysis, indent=2))
            
        elif args.command == "report":
            report = profiler.generate_performance_report(args.output)
            if not args.output:
                print(json.dumps(report, indent=2))
                
        elif args.command == "optimize":
            optimizations = profiler.optimize_build_configuration()
            print("🚀 Build optimization recommendations:")
            for i, opt in enumerate(optimizations, 1):
                print(f"  {i}. {opt}")
        
    except KeyboardInterrupt:
        print("\n⏹️ Profiling interrupted by user")
        profiler.stop_monitoring()
    except Exception as e:
        print(f"❌ Profiling error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()