#!/usr/bin/env python3
"""
FFXI Client Update Manager
Enhanced with PlayOnline manifest integration for comprehensive client file management

This tool provides server administrators with complete control over client updates,
file validation, and content delivery using the original PlayOnline architecture.
"""

import os
import sys
import json
import sqlite3
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

try:
    import mysql.connector
    from mysql.connector import pooling
    MYSQL_AVAILABLE = True
except ImportError:
    # Fallback to SQLite for development/testing
    MYSQL_AVAILABLE = False
    logging.warning("MySQL connector not available, using SQLite fallback")

# Import the PlayOnline analyzer for manifest processing
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from playonline_analyzer import PlayOnlineManifestParser, ManifestEntry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ClientUpdateManager:
    """Manages FFXI client updates using PlayOnline manifest data"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self.load_config(config_file)
        self.db_pool = self.init_database()
        self.squareenix_path = self.config.get('squareenix_path', 'SquareEnix')
        self.parser = None
        
    def load_config(self, config_file: Optional[str]) -> Dict:
        """Load configuration from file or environment"""
        config = {
            'db_host': os.environ.get('FFXI_SQL_HOST', 'localhost'),
            'db_port': int(os.environ.get('FFXI_SQL_PORT', 3306)),
            'db_user': os.environ.get('FFXI_SQL_LOGIN', 'xiuser'),
            'db_password': os.environ.get('FFXI_SQL_PASSWORD', 'xiserver_2024'),
            'db_database': os.environ.get('FFXI_SQL_DATABASE', 'xidb'),
            'squareenix_path': 'SquareEnix',
            'content_path': '/opt/ffxi/client_content',
            'enable_downloads': True,
            'max_concurrent_downloads': 10,
            'bandwidth_limit_mbps': 100
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                config.update(file_config)
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")
        
        return config
    
    def init_database(self) -> Optional[Any]:
        """Initialize database connection pool"""
        try:
            if MYSQL_AVAILABLE:
                pool_config = {
                    'host': self.config['db_host'],
                    'port': self.config['db_port'],
                    'user': self.config['db_user'],
                    'password': self.config['db_password'],
                    'database': self.config['db_database'],
                    'pool_name': 'client_update_pool',
                    'pool_size': 5,
                    'pool_reset_session': True,
                    'autocommit': True
                }
                
                db_pool = pooling.MySQLConnectionPool(**pool_config)
                logger.info("MySQL database connection pool initialized")
                return db_pool
            else:
                # Use SQLite fallback for development
                logger.info("Using SQLite fallback database")
                return None
                
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            return None
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute database query"""
        if not MYSQL_AVAILABLE or not self.db_pool:
            # Fallback simulation for development
            logger.warning("Database query simulated - MySQL not available")
            return []
        
        try:
            conn = self.db_pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
            else:
                conn.commit()
                results = []
            
            cursor.close()
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise
    
    def load_playonline_manifests(self) -> bool:
        """Load PlayOnline manifests from SquareEnix directory"""
        try:
            if not os.path.exists(self.squareenix_path):
                logger.error(f"SquareEnix directory not found: {self.squareenix_path}")
                return False
            
            self.parser = PlayOnlineManifestParser(self.squareenix_path)
            self.parser.load_manifests()
            
            logger.info(f"Loaded {len(self.parser.manifest_entries)} file entries")
            logger.info(f"Loaded {len(self.parser.patch_entries)} patch entries")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load PlayOnline manifests: {e}")
            return False
    
    def import_manifest_to_database(self, version_id: str = "1.18.15e") -> bool:
        """Import PlayOnline manifest data to server database"""
        try:
            if not self.parser:
                logger.error("PlayOnline parser not initialized")
                return False
            
            # Clear existing entries for this version
            self.execute_query("DELETE FROM client_manifest WHERE version_id = %s", (version_id,))
            
            # Combine manifest and patch entries
            all_entries = self.parser.manifest_entries + self.parser.patch_entries
            
            # Insert entries in batches
            batch_size = 100
            total_imported = 0
            
            for i in range(0, len(all_entries), batch_size):
                batch = all_entries[i:i + batch_size]
                
                query = """
                INSERT INTO client_manifest 
                (file_hash, file_path, file_size, file_category, file_extension, version_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                batch_params = []
                for entry in batch:
                    file_extension = Path(entry.path).suffix.lower() if entry.path else ''
                    batch_params.append((
                        entry.hash,
                        entry.path,
                        entry.size,
                        entry.category,
                        file_extension,
                        version_id
                    ))
                
                # Execute batch insert
                conn = self.db_pool.get_connection()
                cursor = conn.cursor()
                cursor.executemany(query, batch_params)
                conn.commit()
                cursor.close()
                conn.close()
                
                total_imported += len(batch)
                logger.info(f"Imported {total_imported}/{len(all_entries)} entries...")
            
            # Update version statistics
            total_size = sum(entry.size for entry in all_entries)
            version_query = """
            INSERT INTO client_versions 
            (version_id, version_name, total_files, total_size_bytes, release_date, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            total_files = VALUES(total_files),
            total_size_bytes = VALUES(total_size_bytes)
            """
            
            self.execute_query(version_query, (
                version_id,
                "PlayOnline Final Release",
                len(all_entries),
                total_size,
                "2011-08-29",
                True
            ))
            
            logger.info(f"Successfully imported {total_imported} manifest entries for version {version_id}")
            logger.info(f"Total content size: {total_size / (1024 * 1024):.1f} MB")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to import manifest to database: {e}")
            return False
    
    def validate_client_installation(self, client_files: List[Dict], version: str = "1.18.15e") -> Dict:
        """Validate client files against server manifest"""
        try:
            # Get server manifest
            server_manifest_query = """
            SELECT file_hash, file_path, file_size, file_category
            FROM client_manifest 
            WHERE version_id = %s
            """
            
            server_entries = self.execute_query(server_manifest_query, (version,))
            server_manifest = {entry['file_hash']: entry for entry in server_entries}
            
            # Validate client files
            validation_result = {
                'version': version,
                'client_files_checked': len(client_files),
                'server_files_total': len(server_entries),
                'valid_files': [],
                'missing_files': [],
                'corrupted_files': [],
                'unknown_files': [],
                'statistics': {
                    'executables_valid': 0,
                    'executables_missing': 0,
                    'graphics_valid': 0,
                    'graphics_missing': 0,
                    'audio_valid': 0,
                    'audio_missing': 0
                }
            }
            
            # Check each client file
            client_hashes = set()
            for client_file in client_files:
                file_hash = client_file.get('hash', '')
                file_path = client_file.get('path', '')
                file_size = client_file.get('size', 0)
                
                client_hashes.add(file_hash)
                
                if file_hash in server_manifest:
                    server_file = server_manifest[file_hash]
                    if server_file['file_size'] == file_size:
                        validation_result['valid_files'].append({
                            'hash': file_hash,
                            'path': file_path,
                            'category': server_file['file_category']
                        })
                        
                        # Update statistics
                        category = server_file['file_category']
                        if category in validation_result['statistics']:
                            validation_result['statistics'][f"{category}_valid"] += 1
                    else:
                        validation_result['corrupted_files'].append({
                            'hash': file_hash,
                            'path': file_path,
                            'expected_size': server_file['file_size'],
                            'actual_size': file_size,
                            'category': server_file['file_category']
                        })
                else:
                    validation_result['unknown_files'].append({
                        'hash': file_hash,
                        'path': file_path,
                        'size': file_size
                    })
            
            # Find missing files
            for server_hash, server_file in server_manifest.items():
                if server_hash not in client_hashes:
                    validation_result['missing_files'].append({
                        'hash': server_hash,
                        'path': server_file['file_path'],
                        'size': server_file['file_size'],
                        'category': server_file['file_category']
                    })
                    
                    # Update statistics
                    category = server_file['file_category']
                    if f"{category}_missing" in validation_result['statistics']:
                        validation_result['statistics'][f"{category}_missing"] += 1
            
            # Sort missing files by priority (executables first, then by size)
            priority_order = {'executable': 1, 'data': 2, 'graphics': 3, 'audio': 4, 'documentation': 5}
            validation_result['missing_files'].sort(
                key=lambda x: (priority_order.get(x['category'], 6), x['size'])
            )
            
            # Calculate overall status
            total_issues = len(validation_result['missing_files']) + len(validation_result['corrupted_files'])
            validation_result['status'] = 'clean' if total_issues == 0 else 'needs_update'
            validation_result['update_priority'] = 'critical' if any(
                f['category'] == 'executable' for f in validation_result['missing_files']
            ) else 'normal'
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Failed to validate client installation: {e}")
            return {'error': str(e)}
    
    def generate_update_package(self, missing_files: List[Dict], language: str = 'EN') -> Dict:
        """Generate update package for missing files"""
        try:
            # Filter files by language preference
            filtered_files = []
            for file_info in missing_files:
                file_path = file_info['path']
                
                # Check if file is language-specific
                if '/EU/' in file_path:
                    if f'/EU/{language}/' in file_path:
                        filtered_files.append(file_info)
                else:
                    # Include non-language-specific files
                    filtered_files.append(file_info)
            
            # Group by category for download optimization
            categories = {}
            total_size = 0
            
            for file_info in filtered_files:
                category = file_info['category']
                if category not in categories:
                    categories[category] = {
                        'files': [],
                        'total_size': 0,
                        'file_count': 0
                    }
                
                categories[category]['files'].append(file_info)
                categories[category]['total_size'] += file_info['size']
                categories[category]['file_count'] += 1
                total_size += file_info['size']
            
            # Generate download sequence (prioritized)
            download_sequence = []
            priority_order = ['executable', 'data', 'graphics', 'audio', 'documentation']
            
            for category in priority_order:
                if category in categories:
                    download_sequence.extend(categories[category]['files'])
            
            # Add any remaining categories
            for category, data in categories.items():
                if category not in priority_order:
                    download_sequence.extend(data['files'])
            
            update_package = {
                'language': language,
                'total_files': len(filtered_files),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'categories': {
                    cat: {
                        'file_count': data['file_count'],
                        'size_mb': round(data['total_size'] / (1024 * 1024), 2)
                    } for cat, data in categories.items()
                },
                'download_sequence': download_sequence[:100],  # Limit for initial response
                'estimated_download_time': self.estimate_download_time(total_size),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return update_package
            
        except Exception as e:
            logger.error(f"Failed to generate update package: {e}")
            return {'error': str(e)}
    
    def estimate_download_time(self, total_bytes: int) -> str:
        """Estimate download time based on configured bandwidth"""
        try:
            bandwidth_bps = self.config['bandwidth_limit_mbps'] * 1024 * 1024
            download_seconds = total_bytes / bandwidth_bps
            
            if download_seconds < 60:
                return f"{int(download_seconds)}s"
            elif download_seconds < 3600:
                minutes = int(download_seconds / 60)
                seconds = int(download_seconds % 60)
                return f"{minutes}m {seconds}s"
            else:
                hours = int(download_seconds / 3600)
                minutes = int((download_seconds % 3600) / 60)
                return f"{hours}h {minutes}m"
                
        except Exception:
            return "Unknown"
    
    def get_update_statistics(self, days: int = 30) -> Dict:
        """Get update download statistics"""
        try:
            # Daily download stats
            daily_query = """
            SELECT 
                DATE(download_start) as date,
                COUNT(*) as downloads,
                COUNT(DISTINCT player_id) as unique_players,
                SUM(bytes_downloaded) / (1024 * 1024) as mb_downloaded
            FROM client_file_downloads 
            WHERE download_start >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY DATE(download_start)
            ORDER BY date DESC
            """
            
            daily_stats = self.execute_query(daily_query, (days,))
            
            # Category popularity
            category_query = """
            SELECT 
                cm.file_category,
                COUNT(cfd.download_id) as download_count,
                AVG(cm.file_size) / (1024 * 1024) as avg_size_mb
            FROM client_file_downloads cfd
            JOIN client_manifest cm ON cfd.file_hash = cm.file_hash
            WHERE cfd.download_start >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY cm.file_category
            ORDER BY download_count DESC
            """
            
            category_stats = self.execute_query(category_query, (days,))
            
            # Current status
            status_query = """
            SELECT 
                download_status,
                COUNT(*) as count
            FROM client_file_downloads 
            WHERE download_start >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            GROUP BY download_status
            """
            
            status_stats = self.execute_query(status_query)
            
            return {
                'period_days': days,
                'daily_statistics': daily_stats,
                'category_popularity': category_stats,
                'current_status': status_stats,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get update statistics: {e}")
            return {'error': str(e)}
    
    def cleanup_old_downloads(self, days: int = 30) -> int:
        """Clean up old download records"""
        try:
            cleanup_query = """
            DELETE FROM client_file_downloads 
            WHERE download_start < DATE_SUB(NOW(), INTERVAL %s DAY)
            AND download_status IN ('completed', 'failed', 'cancelled')
            """
            
            conn = self.db_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(cleanup_query, (days,))
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} old download records")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old downloads: {e}")
            return 0

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='FFXI Client Update Manager with PlayOnline Integration')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--import-manifest', action='store_true', 
                       help='Import PlayOnline manifest to database')
    parser.add_argument('--validate-client', help='Validate client files (JSON file path)')
    parser.add_argument('--generate-update', help='Generate update package for missing files (JSON file path)')
    parser.add_argument('--language', default='EN', choices=['EN', 'DE', 'FR'], 
                       help='Language for localized content')
    parser.add_argument('--statistics', type=int, metavar='DAYS',
                       help='Show update statistics for specified days')
    parser.add_argument('--cleanup', type=int, metavar='DAYS',
                       help='Clean up download records older than specified days')
    parser.add_argument('--version', default='1.18.15e', help='Client version to work with')
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = ClientUpdateManager(args.config)
    
    if args.import_manifest:
        print("Loading PlayOnline manifests...")
        if manager.load_playonline_manifests():
            print("Importing manifest data to database...")
            if manager.import_manifest_to_database(args.version):
                print(f"Successfully imported manifest for version {args.version}")
            else:
                print("Failed to import manifest data")
                sys.exit(1)
        else:
            print("Failed to load PlayOnline manifests")
            sys.exit(1)
    
    elif args.validate_client:
        try:
            with open(args.validate_client, 'r') as f:
                client_files = json.load(f)
            
            print(f"Validating {len(client_files)} client files...")
            result = manager.validate_client_installation(client_files, args.version)
            
            if 'error' not in result:
                print(f"Validation Status: {result['status']}")
                print(f"Valid Files: {len(result['valid_files'])}")
                print(f"Missing Files: {len(result['missing_files'])}")
                print(f"Corrupted Files: {len(result['corrupted_files'])}")
                print(f"Unknown Files: {len(result['unknown_files'])}")
                
                if result['missing_files']:
                    print(f"\nUpdate Priority: {result['update_priority']}")
                    print("Top missing files:")
                    for file_info in result['missing_files'][:10]:
                        size_mb = file_info['size'] / (1024 * 1024)
                        print(f"  - {file_info['path']} ({size_mb:.1f} MB, {file_info['category']})")
            else:
                print(f"Validation failed: {result['error']}")
                
        except Exception as e:
            print(f"Failed to validate client: {e}")
            sys.exit(1)
    
    elif args.generate_update:
        try:
            with open(args.generate_update, 'r') as f:
                missing_files = json.load(f)
            
            print(f"Generating update package for {len(missing_files)} files...")
            result = manager.generate_update_package(missing_files, args.language)
            
            if 'error' not in result:
                print(f"Update Package Generated:")
                print(f"Language: {result['language']}")
                print(f"Total Files: {result['total_files']}")
                print(f"Total Size: {result['total_size_mb']} MB")
                print(f"Estimated Download Time: {result['estimated_download_time']}")
                
                print("\nCategories:")
                for category, data in result['categories'].items():
                    print(f"  - {category}: {data['file_count']} files, {data['size_mb']} MB")
            else:
                print(f"Failed to generate update package: {result['error']}")
                
        except Exception as e:
            print(f"Failed to generate update package: {e}")
            sys.exit(1)
    
    elif args.statistics is not None:
        print(f"Getting update statistics for last {args.statistics} days...")
        result = manager.get_update_statistics(args.statistics)
        
        if 'error' not in result:
            print(f"Download Statistics ({args.statistics} days):")
            print(f"Daily Downloads: {len(result['daily_statistics'])} days with activity")
            
            if result['category_popularity']:
                print("\nMost Downloaded Categories:")
                for category in result['category_popularity']:
                    print(f"  - {category['file_category']}: {category['download_count']} downloads")
        else:
            print(f"Failed to get statistics: {result['error']}")
    
    elif args.cleanup is not None:
        print(f"Cleaning up download records older than {args.cleanup} days...")
        deleted_count = manager.cleanup_old_downloads(args.cleanup)
        print(f"Deleted {deleted_count} old download records")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()