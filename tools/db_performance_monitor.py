#!/usr/bin/env python3
"""
Database Performance Monitor for FFXI Server

This tool provides comprehensive monitoring and testing of database performance,
connection pooling, and latency optimization for multiple connection scenarios.
"""

import time
import threading
import sqlite3
import json
import argparse
import sys
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import subprocess

try:
    import psutil
    import tabulate
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
except ImportError as e:
    print(f"Required module not found: {e}")
    print("Install with: pip install psutil tabulate rich")
    sys.exit(1)

console = Console()

@dataclass
class ConnectionStats:
    """Database connection statistics"""
    connection_time_ms: float
    query_time_ms: float
    success: bool
    error_message: str = ""
    thread_id: int = 0
    timestamp: float = 0.0

@dataclass 
class PoolMetrics:
    """Connection pool performance metrics"""
    total_connections: int
    active_connections: int
    idle_connections: int
    waiting_requests: int
    total_requests_served: int
    total_connections_created: int
    total_connections_destroyed: int
    average_wait_time_ms: float
    
@dataclass
class PerformanceReport:
    """Comprehensive performance analysis report"""
    test_duration_seconds: float
    total_operations: int
    successful_operations: int
    failed_operations: int
    average_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    max_latency_ms: float
    min_latency_ms: float
    operations_per_second: float
    concurrent_connections: int
    pool_metrics: Optional[PoolMetrics] = None

class DatabasePerformanceMonitor:
    """Main database performance monitoring class"""
    
    def __init__(self, test_db_path: str = "/tmp/db_test.sqlite"):
        self.test_db_path = test_db_path
        self.results_db_path = "/tmp/db_performance_results.sqlite"
        self.setup_test_database()
        self.setup_results_database()
        
    def setup_test_database(self):
        """Create test database for performance testing"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Create test tables similar to FFXI server structure
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_chars (
                charid INTEGER PRIMARY KEY,
                charname TEXT NOT NULL,
                nation INTEGER,
                pos_x REAL,
                pos_y REAL,
                pos_z REAL,
                job_level INTEGER,
                hp INTEGER,
                mp INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_items (
                itemid INTEGER PRIMARY KEY,
                itemname TEXT NOT NULL,
                stacksize INTEGER,
                price INTEGER,
                flags INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert test data
        for i in range(1000):
            cursor.execute("""
                INSERT OR REPLACE INTO test_chars 
                (charid, charname, nation, pos_x, pos_y, pos_z, job_level, hp, mp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (i, f"TestChar{i}", i % 3, float(i), float(i+100), float(i+200), 
                  i % 99 + 1, (i % 500) + 100, (i % 300) + 50))
                  
        for i in range(5000):
            cursor.execute("""
                INSERT OR REPLACE INTO test_items
                (itemid, itemname, stacksize, price, flags)
                VALUES (?, ?, ?, ?, ?)
            """, (i, f"TestItem{i}", (i % 99) + 1, (i % 10000) + 1, i % 1024))
        
        conn.commit()
        conn.close()
        
    def setup_results_database(self):
        """Create database to store performance test results"""
        conn = sqlite3.connect(self.results_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                concurrent_connections INTEGER,
                test_duration_seconds REAL,
                total_operations INTEGER,
                successful_operations INTEGER,
                failed_operations INTEGER,
                avg_latency_ms REAL,
                p95_latency_ms REAL,
                p99_latency_ms REAL,
                max_latency_ms REAL,
                min_latency_ms REAL,
                operations_per_second REAL,
                test_config TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connection_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER,
                thread_id INTEGER,
                connection_time_ms REAL,
                query_time_ms REAL,
                success BOOLEAN,
                error_message TEXT,
                timestamp REAL,
                FOREIGN KEY (test_id) REFERENCES performance_tests (id)
            )
        """)
        
        conn.commit()
        conn.close()

    def simulate_database_operation(self, thread_id: int, operation_type: str = "mixed") -> ConnectionStats:
        """Simulate a database operation with timing"""
        start_time = time.time()
        
        try:
            # Simulate connection time
            conn_start = time.time()
            conn = sqlite3.connect(self.test_db_path)
            conn_time = (time.time() - conn_start) * 1000
            
            # Simulate query time
            query_start = time.time()
            cursor = conn.cursor()
            
            if operation_type == "read" or operation_type == "mixed":
                # Simulate character lookup
                cursor.execute("""
                    SELECT c.charid, c.charname, c.job_level, c.hp, c.mp
                    FROM test_chars c
                    WHERE c.charid = ?
                    ORDER BY c.created_at DESC
                    LIMIT 10
                """, (thread_id % 1000,))
                results = cursor.fetchall()
                
                # Simulate item search
                cursor.execute("""
                    SELECT i.itemid, i.itemname, i.price, i.stacksize
                    FROM test_items i  
                    WHERE i.price > ? AND i.stacksize > ?
                    ORDER BY i.price DESC
                    LIMIT 5
                """, (thread_id % 1000, thread_id % 50))
                results = cursor.fetchall()
                
            if operation_type == "write" or operation_type == "mixed":
                # Simulate character update
                cursor.execute("""
                    UPDATE test_chars 
                    SET pos_x = ?, pos_y = ?, hp = ?
                    WHERE charid = ?
                """, (float(thread_id + time.time()), float(thread_id + time.time() + 100), 
                      (thread_id % 500) + 100, thread_id % 1000))
            
            query_time = (time.time() - query_start) * 1000
            
            conn.commit()
            conn.close()
            
            return ConnectionStats(
                connection_time_ms=conn_time,
                query_time_ms=query_time,
                success=True,
                thread_id=thread_id,
                timestamp=time.time()
            )
            
        except Exception as e:
            return ConnectionStats(
                connection_time_ms=0.0,
                query_time_ms=0.0,
                success=False,
                error_message=str(e),
                thread_id=thread_id,
                timestamp=time.time()
            )

    def run_concurrent_test(self, num_connections: int, duration_seconds: int, 
                           operation_type: str = "mixed") -> PerformanceReport:
        """Run concurrent database operations test"""
        console.print(f"[bold blue]Running concurrent test: {num_connections} connections for {duration_seconds}s[/bold blue]")
        
        results = []
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        def worker(thread_id: int):
            thread_results = []
            while time.time() < end_time:
                stats = self.simulate_database_operation(thread_id, operation_type)
                thread_results.append(stats)
                # Small delay to simulate real-world usage pattern
                time.sleep(0.01)
            return thread_results
        
        # Run concurrent operations
        with ThreadPoolExecutor(max_workers=num_connections) as executor:
            with Progress() as progress:
                task = progress.add_task(f"Testing {num_connections} connections...", total=duration_seconds)
                
                # Submit all workers
                futures = [executor.submit(worker, i) for i in range(num_connections)]
                
                # Monitor progress
                while time.time() < end_time:
                    elapsed = time.time() - start_time
                    progress.update(task, completed=elapsed)
                    time.sleep(0.1)
                
                # Collect results
                for future in as_completed(futures):
                    try:
                        thread_results = future.result()
                        results.extend(thread_results)
                    except Exception as e:
                        console.print(f"[red]Worker error: {e}[/red]")
        
        # Calculate performance metrics
        successful_ops = [r for r in results if r.success]
        failed_ops = [r for r in results if not r.success]
        
        if not successful_ops:
            return PerformanceReport(
                test_duration_seconds=duration_seconds,
                total_operations=len(results),
                successful_operations=0,
                failed_operations=len(failed_ops),
                average_latency_ms=0.0,
                p95_latency_ms=0.0,
                p99_latency_ms=0.0,
                max_latency_ms=0.0,
                min_latency_ms=0.0,
                operations_per_second=0.0,
                concurrent_connections=num_connections
            )
        
        # Calculate latency metrics
        latencies = [r.query_time_ms for r in successful_ops]
        latencies.sort()
        
        n = len(latencies)
        p95_idx = int(0.95 * n)
        p99_idx = int(0.99 * n)
        
        return PerformanceReport(
            test_duration_seconds=duration_seconds,
            total_operations=len(results),
            successful_operations=len(successful_ops),
            failed_operations=len(failed_ops),
            average_latency_ms=sum(latencies) / n,
            p95_latency_ms=latencies[p95_idx] if p95_idx < n else latencies[-1],
            p99_latency_ms=latencies[p99_idx] if p99_idx < n else latencies[-1],
            max_latency_ms=max(latencies),
            min_latency_ms=min(latencies),
            operations_per_second=len(successful_ops) / duration_seconds,
            concurrent_connections=num_connections
        )
    
    def save_test_results(self, test_name: str, report: PerformanceReport, stats: List[ConnectionStats]):
        """Save test results to database"""
        conn = sqlite3.connect(self.results_db_path)
        cursor = conn.cursor()
        
        # Insert performance test record
        cursor.execute("""
            INSERT INTO performance_tests 
            (test_name, concurrent_connections, test_duration_seconds, total_operations,
             successful_operations, failed_operations, avg_latency_ms, p95_latency_ms,
             p99_latency_ms, max_latency_ms, min_latency_ms, operations_per_second, test_config)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (test_name, report.concurrent_connections, report.test_duration_seconds,
              report.total_operations, report.successful_operations, report.failed_operations,
              report.average_latency_ms, report.p95_latency_ms, report.p99_latency_ms,
              report.max_latency_ms, report.min_latency_ms, report.operations_per_second,
              json.dumps(asdict(report))))
        
        test_id = cursor.lastrowid
        
        # Insert individual connection stats
        for stat in stats:
            cursor.execute("""
                INSERT INTO connection_stats
                (test_id, thread_id, connection_time_ms, query_time_ms, success, error_message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (test_id, stat.thread_id, stat.connection_time_ms, stat.query_time_ms,
                  stat.success, stat.error_message, stat.timestamp))
        
        conn.commit()
        conn.close()
    
    def run_comprehensive_test(self):
        """Run comprehensive database performance tests"""
        console.print("[bold green]Starting Comprehensive Database Performance Test[/bold green]")
        
        test_scenarios = [
            (1, 30, "read"),      # Single connection, read-only
            (5, 30, "read"),      # Low concurrency, read-only
            (10, 30, "mixed"),    # Medium concurrency, mixed operations
            (20, 30, "mixed"),    # High concurrency, mixed operations
            (50, 30, "mixed"),    # Very high concurrency, mixed operations
        ]
        
        results = []
        
        for connections, duration, operation_type in test_scenarios:
            test_name = f"concurrent_{connections}conn_{operation_type}_{duration}s"
            report = self.run_concurrent_test(connections, duration, operation_type)
            results.append((test_name, report))
            
            # Display results
            self.display_performance_report(test_name, report)
            
            # Brief pause between tests
            time.sleep(2)
        
        # Display summary
        self.display_test_summary(results)
        
        return results
    
    def display_performance_report(self, test_name: str, report: PerformanceReport):
        """Display performance report in a nice format"""
        table = Table(title=f"Performance Report: {test_name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Duration", f"{report.test_duration_seconds:.1f}s")
        table.add_row("Concurrent Connections", str(report.concurrent_connections))
        table.add_row("Total Operations", str(report.total_operations))
        table.add_row("Successful Operations", str(report.successful_operations))
        table.add_row("Failed Operations", str(report.failed_operations))
        table.add_row("Success Rate", f"{(report.successful_operations/report.total_operations)*100:.1f}%")
        table.add_row("Operations/Second", f"{report.operations_per_second:.1f}")
        table.add_row("Average Latency", f"{report.average_latency_ms:.2f}ms")
        table.add_row("P95 Latency", f"{report.p95_latency_ms:.2f}ms") 
        table.add_row("P99 Latency", f"{report.p99_latency_ms:.2f}ms")
        table.add_row("Max Latency", f"{report.max_latency_ms:.2f}ms")
        table.add_row("Min Latency", f"{report.min_latency_ms:.2f}ms")
        
        console.print(table)
        console.print()
    
    def display_test_summary(self, results: List[tuple]):
        """Display summary of all test results"""
        summary_table = Table(title="Test Summary - Database Performance")
        summary_table.add_column("Test", style="cyan")
        summary_table.add_column("Connections", justify="right")
        summary_table.add_column("Success Rate", justify="right")
        summary_table.add_column("Ops/Sec", justify="right") 
        summary_table.add_column("Avg Latency", justify="right")
        summary_table.add_column("P95 Latency", justify="right")
        
        for test_name, report in results:
            success_rate = (report.successful_operations / report.total_operations) * 100
            summary_table.add_row(
                test_name,
                str(report.concurrent_connections),
                f"{success_rate:.1f}%",
                f"{report.operations_per_second:.1f}",
                f"{report.average_latency_ms:.2f}ms",
                f"{report.p95_latency_ms:.2f}ms"
            )
        
        console.print(summary_table)
        
        # Performance recommendations
        console.print("\n[bold yellow]Performance Recommendations:[/bold yellow]")
        
        # Find best performing configuration
        best_throughput = max(results, key=lambda x: x[1].operations_per_second)
        best_latency = min(results, key=lambda x: x[1].average_latency_ms)
        
        console.print(f"• Best throughput: {best_throughput[0]} ({best_throughput[1].operations_per_second:.1f} ops/sec)")
        console.print(f"• Best latency: {best_latency[0]} ({best_latency[1].average_latency_ms:.2f}ms avg)")
        
        # Check for performance degradation
        latencies = [r[1].average_latency_ms for r in results]
        if max(latencies) > min(latencies) * 3:
            console.print("• [red]Warning: Significant latency increase with higher concurrency[/red]")
            console.print("• Consider implementing connection pooling or optimizing database queries")
        
        if any(r[1].failed_operations > 0 for r in results):
            console.print("• [red]Warning: Some operations failed - check connection limits[/red]")

def main():
    parser = argparse.ArgumentParser(description="Database Performance Monitor for FFXI Server")
    parser.add_argument("--test", choices=["comprehensive", "quick", "stress", "pool"], 
                       default="quick", help="Type of test to run")
    parser.add_argument("--connections", type=int, default=10, 
                       help="Number of concurrent connections")
    parser.add_argument("--duration", type=int, default=30,
                       help="Test duration in seconds")
    parser.add_argument("--operation", choices=["read", "write", "mixed"], 
                       default="mixed", help="Type of operations to test")
    parser.add_argument("--ci", action="store_true", 
                       help="Enable CI mode (plain text output)")
    parser.add_argument("--output-json", action="store_true",
                       help="Output results in JSON format for CI")
    parser.add_argument("--baseline", type=str,
                       help="Baseline JSON file for performance comparison")
    
    args = parser.parse_args()
    
    # Use plain console output for CI
    if args.ci:
        global console
        console = Console(color_system=None, legacy_windows=False)
    
    monitor = DatabasePerformanceMonitor()
    
    try:
        if args.test == "comprehensive":
            monitor.run_comprehensive_test()
        elif args.test == "quick":
            report = monitor.run_concurrent_test(args.connections, args.duration, args.operation)
            monitor.display_performance_report(f"quick_test_{args.connections}conn", report)
            
            # Output JSON for CI if requested
            if args.output_json:
                json_output = {
                    'test_type': 'quick',
                    'connections': args.connections,
                    'duration': args.duration,
                    'summary': {
                        'successful_operations': report.successful_operations,
                        'failed_operations': report.failed_operations,
                        'avg_latency_ms': report.average_latency_ms,
                        'max_latency_ms': report.max_latency_ms,
                        'min_latency_ms': report.min_latency_ms,
                        'p95_latency_ms': report.p95_latency_ms,
                        'p99_latency_ms': report.p99_latency_ms,
                        'ops_per_second': report.operations_per_second,
                        'success_rate': (report.successful_operations / (report.successful_operations + report.failed_operations)) * 100 if (report.successful_operations + report.failed_operations) > 0 else 0
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
                output_filename = f"db_performance_{args.test}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_filename, 'w') as f:
                    json.dump(json_output, f, indent=2)
                
                if args.ci:
                    print(f"Performance results saved to: {output_filename}")
                else:
                    console.print(f"[green]Performance results saved to: {output_filename}[/green]")
                
                # Compare with baseline if provided
                if args.baseline and os.path.exists(args.baseline):
                    with open(args.baseline, 'r') as f:
                        baseline = json.load(f)
                    
                    current_latency = json_output['summary']['avg_latency_ms']
                    baseline_latency = baseline['summary']['avg_latency_ms']
                    latency_change = ((current_latency - baseline_latency) / baseline_latency) * 100
                    
                    current_ops = json_output['summary']['ops_per_second']
                    baseline_ops = baseline['summary']['ops_per_second']
                    ops_change = ((current_ops - baseline_ops) / baseline_ops) * 100
                    
                    if args.ci:
                        print(f"Performance comparison with baseline:")
                        print(f"  Latency change: {latency_change:+.1f}%")
                        print(f"  Throughput change: {ops_change:+.1f}%")
                    else:
                        console.print(f"[yellow]Performance comparison with baseline:[/yellow]")
                        console.print(f"  Latency change: {latency_change:+.1f}%")
                        console.print(f"  Throughput change: {ops_change:+.1f}%")
                    
                    # Set exit code for CI if performance degraded significantly
                    if latency_change > 20 or ops_change < -20:
                        if args.ci:
                            print("❌ Significant performance degradation detected!")
                        else:
                            console.print("[red]❌ Significant performance degradation detected![/red]")
                        sys.exit(1)
                        
        elif args.test == "pool":
            # Test connection pool performance specifically
            if args.ci:
                print(f"Testing connection pool with {args.connections} connections...")
            else:
                console.print(f"[blue]Testing connection pool with {args.connections} connections...[/blue]")
            
            report = monitor.run_concurrent_test(args.connections, args.duration, args.operation)
            monitor.display_performance_report(f"pool_test_{args.connections}conn", report)
            
        elif args.test == "stress":
            # Stress test with increasing load
            stress_results = []
            for connections in [10, 25, 50, 100]:
                if args.ci:
                    print(f"\nStress Test: {connections} connections")
                else:
                    console.print(f"\n[bold red]Stress Test: {connections} connections[/bold red]")
                
                report = monitor.run_concurrent_test(connections, 60, "mixed")
                monitor.display_performance_report(f"stress_{connections}conn", report)
                
                stress_results.append({
                    'connections': connections,
                    'successful_operations': report.successful_operations,
                    'failed_operations': report.failed_operations,
                    'avg_latency_ms': report.average_latency_ms,
                    'ops_per_second': report.operations_per_second
                })
                
                if report.failed_operations > report.successful_operations * 0.1:
                    if args.ci:
                        print(f"Too many failures at {connections} connections, stopping stress test")
                    else:
                        console.print(f"[red]Too many failures at {connections} connections, stopping stress test[/red]")
                    break
            
            # Save stress test results
            if args.output_json:
                stress_output = {
                    'test_type': 'stress',
                    'results': stress_results,
                    'timestamp': datetime.now().isoformat()
                }
                
                output_filename = f"db_performance_stress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_filename, 'w') as f:
                    json.dump(stress_output, f, indent=2)
                    
    except KeyboardInterrupt:
        if args.ci:
            print("\nTest interrupted by user")
        else:
            console.print("\n[yellow]Test interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        if args.ci:
            print(f"Test failed: {e}")
        else:
            console.print(f"[red]Test failed: {e}[/red]")
        sys.exit(1)
        
    if args.ci:
        print("\nDatabase performance testing complete!")
    else:
        console.print("\n[green]Database performance testing complete![/green]")

if __name__ == "__main__":
    main()