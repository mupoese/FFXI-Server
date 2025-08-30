#!/usr/bin/env python3
"""
Database CI Optimizations for FFXI Server

This script provides database configuration optimizations specifically for CI environments
to ensure database performance tests pass reliably in GitHub Actions.
"""

import mysql.connector
import sys
import os
import json
from typing import Dict, List, Any

def apply_mysql_ci_optimizations(host: str = 'localhost', user: str = 'root', password: str = 'root') -> bool:
    """Apply MySQL/MariaDB optimizations for CI environment"""
    
    optimizations = [
        # InnoDB optimizations for CI environment
        "SET GLOBAL innodb_buffer_pool_size = 134217728",  # 128MB - reasonable for CI
        "SET GLOBAL innodb_log_file_size = 67108864",      # 64MB - smaller log files for CI
        "SET GLOBAL innodb_flush_log_at_trx_commit = 2",   # Better performance for testing
        "SET GLOBAL innodb_flush_method = 'O_DIRECT'",     # Reduce disk I/O overhead
        "SET GLOBAL innodb_io_capacity = 200",             # Moderate I/O capacity for CI
        "SET GLOBAL innodb_io_capacity_max = 400",         # Max I/O capacity
        
        # Connection and timeout optimizations
        "SET GLOBAL max_connections = 200",                # Support more concurrent connections
        "SET GLOBAL connect_timeout = 30",                 # Longer connection timeout for CI
        "SET GLOBAL wait_timeout = 300",                   # 5 minute wait timeout
        "SET GLOBAL interactive_timeout = 300",            # 5 minute interactive timeout
        
        # Query cache and performance
        "SET GLOBAL query_cache_size = 33554432",          # 32MB query cache
        "SET GLOBAL query_cache_type = 1",                 # Enable query cache
        "SET GLOBAL query_cache_limit = 2097152",          # 2MB max query result size
        
        # Thread and table optimizations
        "SET GLOBAL thread_cache_size = 50",               # Cache threads for reuse
        "SET GLOBAL table_open_cache = 400",               # Cache open tables
        "SET GLOBAL table_definition_cache = 400",         # Cache table definitions
        
        # Temporary table optimizations
        "SET GLOBAL tmp_table_size = 67108864",            # 64MB temp table size
        "SET GLOBAL max_heap_table_size = 67108864",       # 64MB heap table size
        
        # Binary logging optimizations for CI
        "SET GLOBAL sync_binlog = 0",                      # Disable sync for testing performance
        "SET GLOBAL innodb_support_xa = 0",                # Disable XA for better performance
    ]
    
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            autocommit=True
        )
        cursor = conn.cursor()
        
        print("Applying MySQL/MariaDB CI optimizations...")
        
        applied_optimizations = []
        failed_optimizations = []
        
        for optimization in optimizations:
            try:
                cursor.execute(optimization)
                applied_optimizations.append(optimization)
                print(f"✓ Applied: {optimization}")
            except mysql.connector.Error as e:
                failed_optimizations.append((optimization, str(e)))
                print(f"⚠ Failed: {optimization} - {e}")
        
        # Verify some key settings
        print("\nVerifying applied settings:")
        verification_queries = [
            "SHOW VARIABLES LIKE 'innodb_buffer_pool_size'",
            "SHOW VARIABLES LIKE 'max_connections'",
            "SHOW VARIABLES LIKE 'query_cache_size'",
            "SHOW VARIABLES LIKE 'thread_cache_size'"
        ]
        
        for query in verification_queries:
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                print(f"  {result[0]}: {result[1]}")
        
        conn.close()
        
        print(f"\nOptimization Summary:")
        print(f"  Applied: {len(applied_optimizations)}")
        print(f"  Failed: {len(failed_optimizations)}")
        
        # Return success if most optimizations applied
        return len(failed_optimizations) < len(optimizations) / 2
        
    except mysql.connector.Error as e:
        print(f"Failed to connect to database: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def create_optimized_database_schema(host: str = 'localhost', user: str = 'root', password: str = 'root', database: str = 'xidb') -> bool:
    """Create optimized database schema with proper indexes for CI testing"""
    
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            autocommit=True
        )
        cursor = conn.cursor()
        
        print("Creating optimized database indexes for CI performance...")
        
        # Optimized indexes for common FFXI queries
        index_commands = [
            # Character-related indexes
            "CREATE INDEX IF NOT EXISTS idx_chars_nation_hp ON chars(nation, hp)",
            "CREATE INDEX IF NOT EXISTS idx_chars_name_nation ON chars(charname, nation)",
            "CREATE INDEX IF NOT EXISTS idx_chars_zone_pos ON chars(pos_zone, pos_x, pos_y)",
            
            # Item-related indexes  
            "CREATE INDEX IF NOT EXISTS idx_items_price_stack ON items(price, stacksize)",
            "CREATE INDEX IF NOT EXISTS idx_items_name_price ON items(name, price)",
            
            # Account and login indexes
            "CREATE INDEX IF NOT EXISTS idx_accounts_login ON accounts(login)",
            "CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status, priv)",
            
            # Zone and server indexes
            "CREATE INDEX IF NOT EXISTS idx_zone_settings_id ON zone_settings(zoneid, zoneport)",
        ]
        
        applied_indexes = []
        failed_indexes = []
        
        for index_cmd in index_commands:
            try:
                cursor.execute(index_cmd)
                applied_indexes.append(index_cmd)
                print(f"✓ Applied: {index_cmd}")
            except mysql.connector.Error as e:
                # Skip if index already exists or table doesn't exist
                if "already exists" in str(e).lower() or "doesn't exist" in str(e).lower():
                    print(f"ℹ Skipped: {index_cmd} - {e}")
                else:
                    failed_indexes.append((index_cmd, str(e)))
                    print(f"⚠ Failed: {index_cmd} - {e}")
        
        # Analyze tables for better query optimization
        analyze_commands = [
            "ANALYZE TABLE chars",
            "ANALYZE TABLE items", 
            "ANALYZE TABLE accounts",
            "ANALYZE TABLE zone_settings"
        ]
        
        print("\nAnalyzing tables for query optimization...")
        for analyze_cmd in analyze_commands:
            try:
                cursor.execute(analyze_cmd)
                print(f"✓ Analyzed: {analyze_cmd}")
            except mysql.connector.Error as e:
                print(f"⚠ Failed to analyze: {analyze_cmd} - {e}")
        
        conn.close()
        
        print(f"\nIndex Optimization Summary:")
        print(f"  Applied: {len(applied_indexes)}")
        print(f"  Failed: {len(failed_indexes)}")
        
        return len(failed_indexes) < len(index_commands) / 2
        
    except mysql.connector.Error as e:
        print(f"Failed to connect to database: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def validate_database_performance(host: str = 'localhost', user: str = 'root', password: str = 'root', database: str = 'xidb') -> Dict[str, Any]:
    """Validate database performance after optimizations"""
    
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        print("Validating database performance...")
        
        performance_metrics = {}
        
        # Test 1: Simple query performance
        import time
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM chars LIMIT 1")
        cursor.fetchone()
        simple_query_time = (time.time() - start_time) * 1000
        performance_metrics['simple_query_ms'] = simple_query_time
        
        # Test 2: Complex query performance (using optimized indexes)
        start_time = time.time()
        cursor.execute("""
            SELECT c.charid, c.charname, c.nation 
            FROM chars c 
            WHERE c.nation IN (0, 1, 2) 
            ORDER BY c.hp DESC 
            LIMIT 10
        """)
        results = cursor.fetchall()
        complex_query_time = (time.time() - start_time) * 1000
        performance_metrics['complex_query_ms'] = complex_query_time
        
        # Test 3: Connection performance
        start_time = time.time()
        test_conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        test_conn.close()
        connection_time = (time.time() - start_time) * 1000
        performance_metrics['connection_time_ms'] = connection_time
        
        # Get database status
        cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
        result = cursor.fetchone()
        performance_metrics['threads_connected'] = int(result[1]) if result else 0
        
        cursor.execute("SHOW STATUS LIKE 'Questions'")
        result = cursor.fetchone()
        performance_metrics['total_queries'] = int(result[1]) if result else 0
        
        conn.close()
        
        # Performance validation
        validation_results = {
            'metrics': performance_metrics,
            'validation': {
                'simple_query_ok': simple_query_time < 10.0,  # Should be under 10ms
                'complex_query_ok': complex_query_time < 100.0,  # Should be under 100ms
                'connection_ok': connection_time < 50.0,  # Should be under 50ms
            }
        }
        
        print(f"Performance Validation Results:")
        print(f"  Simple query: {simple_query_time:.2f}ms ({'✓' if validation_results['validation']['simple_query_ok'] else '✗'})")
        print(f"  Complex query: {complex_query_time:.2f}ms ({'✓' if validation_results['validation']['complex_query_ok'] else '✗'})")
        print(f"  Connection time: {connection_time:.2f}ms ({'✓' if validation_results['validation']['connection_ok'] else '✗'})")
        print(f"  Active connections: {performance_metrics['threads_connected']}")
        
        return validation_results
        
    except mysql.connector.Error as e:
        print(f"Failed to validate database performance: {e}")
        return {'error': str(e)}
    except Exception as e:
        print(f"Unexpected error during validation: {e}")
        return {'error': str(e)}

def main():
    """Main function for database CI optimizations"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database CI Optimizations for FFXI Server')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--user', default='root', help='Database user')
    parser.add_argument('--password', default='root', help='Database password')
    parser.add_argument('--database', default='xidb', help='Database name')
    parser.add_argument('--optimize', action='store_true', help='Apply MySQL optimizations')
    parser.add_argument('--indexes', action='store_true', help='Create optimized indexes')
    parser.add_argument('--validate', action='store_true', help='Validate performance')
    parser.add_argument('--all', action='store_true', help='Run all optimizations')
    
    args = parser.parse_args()
    
    if args.all:
        args.optimize = True
        args.indexes = True
        args.validate = True
    
    success = True
    
    if args.optimize:
        print("=" * 60)
        print("APPLYING MYSQL/MARIADB OPTIMIZATIONS")
        print("=" * 60)
        success &= apply_mysql_ci_optimizations(args.host, args.user, args.password)
    
    if args.indexes:
        print("\n" + "=" * 60)
        print("CREATING OPTIMIZED DATABASE INDEXES")
        print("=" * 60)
        success &= create_optimized_database_schema(args.host, args.user, args.password, args.database)
    
    if args.validate:
        print("\n" + "=" * 60)
        print("VALIDATING DATABASE PERFORMANCE")
        print("=" * 60)
        validation_results = validate_database_performance(args.host, args.user, args.password, args.database)
        
        if 'error' not in validation_results:
            # Save validation results
            with open('database_optimization_validation.json', 'w') as f:
                json.dump(validation_results, f, indent=2)
            print(f"\nValidation results saved to: database_optimization_validation.json")
            
            # Check if all validations passed
            all_valid = all(validation_results['validation'].values())
            if not all_valid:
                print("⚠ Some performance validations failed")
                success = False
        else:
            print(f"Validation failed: {validation_results['error']}")
            success = False
    
    if success:
        print("\n🎉 All database optimizations completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some optimizations failed - check logs above")
        sys.exit(1)

if __name__ == "__main__":
    main()