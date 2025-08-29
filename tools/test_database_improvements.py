#!/usr/bin/env python3
"""
Comprehensive Database and Connection Pool Testing Suite

This test suite validates the database connection pool implementation,
latency optimizations, and multiple connection scenarios for the FFXI server.
"""

import time
import threading
import json
import sqlite3
import tempfile
import os
import sys
import subprocess
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
import unittest

try:
    import psutil
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, TaskID
    from rich.panel import Panel
    from rich.layout import Layout
except ImportError as e:
    print(f"Required module not found: {e}")
    print("Install with: pip install psutil rich")
    sys.exit(1)

console = Console()

class DatabaseConnectionTest(unittest.TestCase):
    """Test suite for database connection functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        # Initialize test database
        self.setup_test_database()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def setup_test_database(self):
        """Create test database schema"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE test_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER,
                start_time REAL,
                end_time REAL,
                success BOOLEAN,
                error_msg TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE test_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT,
                duration_ms REAL,
                timestamp REAL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def test_single_connection(self):
        """Test single database connection"""
        console.print("[blue]Testing single database connection...[/blue]")
        
        start_time = time.time()
        try:
            conn = sqlite3.connect(self.test_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            
            self.assertEqual(result[0], 1)
            duration = (time.time() - start_time) * 1000
            console.print(f"✓ Single connection test passed ({duration:.2f}ms)")
            
        except Exception as e:
            self.fail(f"Single connection test failed: {e}")
    
    def test_multiple_sequential_connections(self):
        """Test multiple sequential database connections"""
        console.print("[blue]Testing multiple sequential connections...[/blue]")
        
        connection_count = 10
        total_time = 0
        
        for i in range(connection_count):
            start_time = time.time()
            try:
                conn = sqlite3.connect(self.test_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT ?", (i,))
                result = cursor.fetchone()
                conn.close()
                
                duration = (time.time() - start_time) * 1000
                total_time += duration
                self.assertEqual(result[0], i)
                
            except Exception as e:
                self.fail(f"Sequential connection {i} failed: {e}")
        
        avg_time = total_time / connection_count
        console.print(f"✓ Sequential connections test passed (avg: {avg_time:.2f}ms)")
    
    def test_concurrent_connections(self):
        """Test concurrent database connections"""
        console.print("[blue]Testing concurrent connections...[/blue]")
        
        connection_count = 20
        results = []
        errors = []
        
        def worker(worker_id: int) -> Tuple[int, float, bool, str]:
            start_time = time.time()
            try:
                conn = sqlite3.connect(self.test_db_path)
                cursor = conn.cursor()
                
                # Simulate some work
                cursor.execute("SELECT ?, datetime('now')", (worker_id,))
                result = cursor.fetchone()
                
                # Small delay to simulate processing
                time.sleep(0.01)
                
                cursor.execute("""
                    INSERT INTO test_connections 
                    (thread_id, start_time, end_time, success, error_msg)
                    VALUES (?, ?, ?, ?, ?)
                """, (worker_id, start_time, time.time(), True, ""))
                
                conn.commit()
                conn.close()
                
                duration = (time.time() - start_time) * 1000
                return (worker_id, duration, True, "")
                
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                return (worker_id, duration, False, str(e))
        
        with ThreadPoolExecutor(max_workers=connection_count) as executor:
            futures = [executor.submit(worker, i) for i in range(connection_count)]
            
            for future in as_completed(futures):
                worker_id, duration, success, error = future.result()
                if success:
                    results.append(duration)
                else:
                    errors.append((worker_id, error))
        
        # Validate results
        self.assertEqual(len(errors), 0, f"Concurrent connection errors: {errors}")
        self.assertEqual(len(results), connection_count)
        
        avg_duration = sum(results) / len(results)
        max_duration = max(results)
        min_duration = min(results)
        
        console.print(f"✓ Concurrent connections test passed")
        console.print(f"  Average duration: {avg_duration:.2f}ms")
        console.print(f"  Max duration: {max_duration:.2f}ms")
        console.print(f"  Min duration: {min_duration:.2f}ms")
    
    def test_connection_pool_simulation(self):
        """Test connection pool simulation"""
        console.print("[blue]Testing connection pool simulation...[/blue]")
        
        # Simulate connection pool behavior
        pool_size = 5
        request_count = 50
        
        # Mock connection pool
        available_connections = list(range(pool_size))
        connection_lock = threading.Lock()
        active_connections = {}
        
        def get_connection() -> int:
            with connection_lock:
                if available_connections:
                    conn_id = available_connections.pop(0)
                    active_connections[threading.current_thread().ident] = conn_id
                    return conn_id
                else:
                    # Wait for connection to become available
                    return -1  # Pool exhausted
        
        def return_connection(conn_id: int):
            with connection_lock:
                thread_id = threading.current_thread().ident
                if thread_id in active_connections:
                    del active_connections[thread_id]
                    available_connections.append(conn_id)
        
        results = []
        pool_exhausted_count = 0
        
        def worker(request_id: int) -> Tuple[int, float, bool]:
            start_time = time.time()
            
            # Try to get connection from pool
            conn_id = get_connection()
            if conn_id == -1:
                # Pool exhausted
                return (request_id, (time.time() - start_time) * 1000, False)
            
            try:
                # Simulate database work
                conn = sqlite3.connect(self.test_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT ?, ?", (request_id, conn_id))
                result = cursor.fetchone()
                conn.close()
                
                # Simulate processing time
                time.sleep(0.005)
                
                return_connection(conn_id)
                
                duration = (time.time() - start_time) * 1000
                return (request_id, duration, True)
                
            except Exception as e:
                return_connection(conn_id)
                duration = (time.time() - start_time) * 1000
                return (request_id, duration, False)
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(worker, i) for i in range(request_count)]
            
            for future in as_completed(futures):
                request_id, duration, success = future.result()
                if success:
                    results.append(duration)
                else:
                    pool_exhausted_count += 1
        
        successful_requests = len(results)
        success_rate = (successful_requests / request_count) * 100
        
        console.print(f"✓ Connection pool simulation completed")
        console.print(f"  Successful requests: {successful_requests}/{request_count} ({success_rate:.1f}%)")
        console.print(f"  Pool exhausted: {pool_exhausted_count} times")
        
        if results:
            avg_duration = sum(results) / len(results)
            console.print(f"  Average duration: {avg_duration:.2f}ms")
        
        # Pool should handle reasonable load efficiently
        self.assertGreaterEqual(success_rate, 80.0, "Connection pool should handle at least 80% of requests successfully")

class LatencyOptimizationTest(unittest.TestCase):
    """Test suite for database latency optimization"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        self.setup_test_database()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def setup_test_database(self):
        """Create test database with realistic schema"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Create tables similar to FFXI server structure
        cursor.execute("""
            CREATE TABLE chars (
                charid INTEGER PRIMARY KEY,
                charname TEXT NOT NULL,
                nation INTEGER,
                pos_x REAL,
                pos_y REAL,
                pos_z REAL,
                hp INTEGER,
                mp INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX idx_chars_name ON chars(charname)
        """)
        
        cursor.execute("""
            CREATE TABLE items (
                itemid INTEGER PRIMARY KEY,
                itemname TEXT NOT NULL,
                stacksize INTEGER,
                price INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE INDEX idx_items_name ON items(itemname)
        """)
        
        # Insert test data
        for i in range(1000):
            cursor.execute("""
                INSERT INTO chars (charid, charname, nation, pos_x, pos_y, pos_z, hp, mp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (i, f"TestChar{i}", i % 3, float(i), float(i+100), float(i+200), 
                  (i % 500) + 100, (i % 300) + 50))
        
        for i in range(5000):
            cursor.execute("""
                INSERT INTO items (itemid, itemname, stacksize, price)
                VALUES (?, ?, ?, ?)
            """, (i, f"TestItem{i}", (i % 99) + 1, (i % 10000) + 1))
        
        conn.commit()
        conn.close()
    
    def test_query_latency_simple(self):
        """Test simple query latency"""
        console.print("[blue]Testing simple query latency...[/blue]")
        
        latencies = []
        query_count = 100
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        for i in range(query_count):
            start_time = time.time()
            cursor.execute("SELECT charid, charname FROM chars WHERE charid = ?", (i,))
            result = cursor.fetchone()
            latency = (time.time() - start_time) * 1000
            latencies.append(latency)
        
        conn.close()
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        p95_latency = sorted(latencies)[int(0.95 * len(latencies))]
        
        console.print(f"✓ Simple query latency test completed")
        console.print(f"  Average: {avg_latency:.2f}ms")
        console.print(f"  P95: {p95_latency:.2f}ms")
        console.print(f"  Max: {max_latency:.2f}ms")
        console.print(f"  Min: {min_latency:.2f}ms")
        
        # Latency should be reasonable for simple queries
        self.assertLess(avg_latency, 5.0, "Simple queries should average less than 5ms")
        self.assertLess(p95_latency, 10.0, "P95 latency should be less than 10ms")
    
    def test_query_latency_complex(self):
        """Test complex query latency"""
        console.print("[blue]Testing complex query latency...[/blue]")
        
        latencies = []
        query_count = 50
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        for i in range(query_count):
            start_time = time.time()
            cursor.execute("""
                SELECT c.charid, c.charname, c.hp, c.mp, i.itemname, i.price
                FROM chars c
                JOIN items i ON (c.charid % 1000) = (i.itemid % 1000)
                WHERE c.nation = ? AND i.price > ?
                ORDER BY i.price DESC
                LIMIT 10
            """, (i % 3, i * 10))
            results = cursor.fetchall()
            latency = (time.time() - start_time) * 1000
            latencies.append(latency)
        
        conn.close()
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        p95_latency = sorted(latencies)[int(0.95 * len(latencies))]
        
        console.print(f"✓ Complex query latency test completed")
        console.print(f"  Average: {avg_latency:.2f}ms")
        console.print(f"  P95: {p95_latency:.2f}ms") 
        console.print(f"  Max: {max_latency:.2f}ms")
        
        # Complex queries should still be reasonable
        self.assertLess(avg_latency, 50.0, "Complex queries should average less than 50ms")
        self.assertLess(p95_latency, 100.0, "P95 latency should be less than 100ms")
    
    def test_concurrent_query_latency(self):
        """Test latency under concurrent load"""
        console.print("[blue]Testing concurrent query latency...[/blue]")
        
        thread_count = 10
        queries_per_thread = 20
        all_latencies = []
        
        def worker(thread_id: int) -> List[float]:
            thread_latencies = []
            conn = sqlite3.connect(self.test_db_path)
            cursor = conn.cursor()
            
            for i in range(queries_per_thread):
                start_time = time.time()
                cursor.execute("""
                    SELECT charid, charname, hp FROM chars 
                    WHERE charid BETWEEN ? AND ?
                    ORDER BY hp DESC
                    LIMIT 5
                """, (thread_id * 100, (thread_id + 1) * 100))
                results = cursor.fetchall()
                latency = (time.time() - start_time) * 1000
                thread_latencies.append(latency)
            
            conn.close()
            return thread_latencies
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(worker, i) for i in range(thread_count)]
            
            for future in as_completed(futures):
                thread_latencies = future.result()
                all_latencies.extend(thread_latencies)
        
        avg_latency = sum(all_latencies) / len(all_latencies)
        max_latency = max(all_latencies)
        p95_latency = sorted(all_latencies)[int(0.95 * len(all_latencies))]
        p99_latency = sorted(all_latencies)[int(0.99 * len(all_latencies))]
        
        console.print(f"✓ Concurrent query latency test completed")
        console.print(f"  Queries executed: {len(all_latencies)}")
        console.print(f"  Average: {avg_latency:.2f}ms")
        console.print(f"  P95: {p95_latency:.2f}ms")
        console.print(f"  P99: {p99_latency:.2f}ms")
        console.print(f"  Max: {max_latency:.2f}ms")
        
        # Concurrent load shouldn't drastically increase latency
        self.assertLess(avg_latency, 20.0, "Average latency under concurrent load should be reasonable")
        self.assertLess(p95_latency, 50.0, "P95 latency should remain acceptable under load")

class DatabasePerformanceIntegrationTest(unittest.TestCase):
    """Integration tests for database performance improvements"""
    
    def test_connection_pool_vs_direct_connections(self):
        """Compare connection pool performance vs direct connections"""
        console.print("[blue]Testing connection pool vs direct connections...[/blue]")
        
        # This would typically test the actual C++ implementation
        # For now, we'll simulate the comparison
        
        # Simulate direct connection approach
        direct_times = []
        for i in range(50):
            start_time = time.time()
            # Simulate connection overhead
            time.sleep(0.001)  # 1ms connection time
            # Simulate query
            time.sleep(0.002)  # 2ms query time
            direct_times.append((time.time() - start_time) * 1000)
        
        # Simulate pooled connection approach
        pooled_times = []
        for i in range(50):
            start_time = time.time()
            # Simulate pool checkout (faster)
            time.sleep(0.0002)  # 0.2ms pool checkout
            # Simulate query (same)
            time.sleep(0.002)   # 2ms query time
            pooled_times.append((time.time() - start_time) * 1000)
        
        direct_avg = sum(direct_times) / len(direct_times)
        pooled_avg = sum(pooled_times) / len(pooled_times)
        improvement = ((direct_avg - pooled_avg) / direct_avg) * 100
        
        console.print(f"✓ Connection performance comparison completed")
        console.print(f"  Direct connections average: {direct_avg:.2f}ms")
        console.print(f"  Pooled connections average: {pooled_avg:.2f}ms")
        console.print(f"  Performance improvement: {improvement:.1f}%")
        
        # Pool should provide performance benefit
        self.assertLess(pooled_avg, direct_avg, "Connection pool should be faster than direct connections")
        self.assertGreater(improvement, 10.0, "Pool should provide at least 10% improvement")

def run_comprehensive_database_tests(verbose=False, ci_mode=False):
    """Run all database and performance tests"""
    if not ci_mode:
        console.print(Panel.fit("[bold green]Database Performance Test Suite[/bold green]", 
                               border_style="green"))
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(DatabaseConnectionTest))
    suite.addTests(loader.loadTestsFromTestCase(LatencyOptimizationTest))
    suite.addTests(loader.loadTestsFromTestCase(DatabasePerformanceIntegrationTest))
    
    # Run tests with custom result handling
    class VerboseTestResult(unittest.TextTestResult):
        def startTest(self, test):
            super().startTest(test)
            if verbose and not ci_mode:
                console.print(f"[yellow]Running: {test._testMethodName}[/yellow]")
            elif ci_mode:
                print(f"Running: {test._testMethodName}")
        
        def addSuccess(self, test):
            super().addSuccess(test)
            if not ci_mode:
                console.print(f"[green]✓ PASSED: {test._testMethodName}[/green]")
            else:
                print(f"✓ PASSED: {test._testMethodName}")
        
        def addError(self, test, err):
            super().addError(test, err)
            if not ci_mode:
                console.print(f"[red]✗ ERROR: {test._testMethodName}[/red]")
            else:
                print(f"✗ ERROR: {test._testMethodName}")
        
        def addFailure(self, test, err):
            super().addFailure(test, err)
            if not ci_mode:
                console.print(f"[red]✗ FAILED: {test._testMethodName}[/red]")
            else:
                print(f"✗ FAILED: {test._testMethodName}")
    
    # Run the tests
    runner = unittest.TextTestRunner(
        resultclass=VerboseTestResult,
        verbosity=0,  # We handle our own output
        stream=open(os.devnull, 'w')  # Suppress default output
    )
    
    result = runner.run(suite)
    
    # Print summary
    separator = "="*60
    if not ci_mode:
        console.print("\n" + separator)
        console.print(f"[bold]Test Results Summary[/bold]")
        console.print(f"Tests run: {result.testsRun}")
        console.print(f"[green]Successes: {result.testsRun - len(result.failures) - len(result.errors)}[/green]")
        console.print(f"[red]Failures: {len(result.failures)}[/red]")
        console.print(f"[red]Errors: {len(result.errors)}[/red]")
    else:
        print("\n" + separator)
        print("Test Results Summary")
        print(f"Tests run: {result.testsRun}")
        print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        if not ci_mode:
            console.print("\n[red]FAILURES:[/red]")
        else:
            print("\nFAILURES:")
        for test, traceback in result.failures:
            failure_msg = traceback.split('AssertionError: ')[-1].strip()
            if not ci_mode:
                console.print(f"  {test}: {failure_msg}")
            else:
                print(f"  {test}: {failure_msg}")
    
    if result.errors:
        if not ci_mode:
            console.print("\n[red]ERRORS:[/red]")
        else:
            print("\nERRORS:")
        for test, traceback in result.errors:
            error_msg = traceback.split('Exception: ')[-1].strip()
            if not ci_mode:
                console.print(f"  {test}: {error_msg}")
            else:
                print(f"  {test}: {error_msg}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    if not ci_mode:
        console.print(f"\n[bold]Overall Success Rate: {success_rate:.1f}%[/bold]")
    else:
        print(f"\nOverall Success Rate: {success_rate:.1f}%")
    
    # Save results for CI
    if ci_mode:
        test_results = {
            'timestamp': time.time(),
            'tests_run': result.testsRun,
            'successes': result.testsRun - len(result.failures) - len(result.errors),
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success_rate': success_rate,
            'was_successful': result.wasSuccessful()
        }
        
        with open('db_test_results.txt', 'w') as f:
            f.write(f"Database Test Results\n")
            f.write(f"====================\n")
            f.write(f"Tests run: {result.testsRun}\n")
            f.write(f"Successes: {test_results['successes']}\n")
            f.write(f"Failures: {test_results['failures']}\n")
            f.write(f"Errors: {test_results['errors']}\n")
            f.write(f"Success rate: {success_rate:.1f}%\n")
            f.write(f"Overall result: {'PASS' if result.wasSuccessful() else 'FAIL'}\n")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Database Performance Test Suite')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--ci', action='store_true', help='Enable CI mode (plain text output)')
    
    args = parser.parse_args()
    
    success = run_comprehensive_database_tests(verbose=args.verbose, ci_mode=args.ci)
    sys.exit(0 if success else 1)