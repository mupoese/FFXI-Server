#!/usr/bin/env python3
"""
PlayOnline Content Delivery Integration
Server-side enhancement for FFXI client content management and delivery

This module integrates PlayOnline manifest data with the existing FFXI server
infrastructure to provide enhanced client update capabilities, file validation,
and multi-language content support.
"""

import os
import json
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import mysql.connector
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContentDeliveryConfig:
    """Configuration for PlayOnline content delivery"""
    content_base_path: str = "/opt/ffxi/client_content"
    manifest_version: str = "1.18.15e"
    enable_compression: bool = True
    enable_caching: bool = True
    max_bandwidth_mbps: int = 100
    concurrent_downloads: int = 10
    cache_duration_hours: int = 24
    supported_languages: List[str] = None
    
    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ['EN', 'DE', 'FR', 'US']

class PlayOnlineContentDelivery:
    """Enhanced content delivery system based on PlayOnline architecture"""
    
    def __init__(self, config: ContentDeliveryConfig, db_connection=None):
        self.config = config
        self.db_connection = db_connection
        self.content_cache = {}
        self.download_queue = []
        
        # Initialize content directory structure
        self.init_content_directories()
    
    def init_content_directories(self):
        """Initialize content directory structure"""
        try:
            base_path = Path(self.config.content_base_path)
            base_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories for different content types
            subdirs = [
                'graphics',
                'audio', 
                'database',
                'executable',
                'data',
                'documentation',
                'patches',
                'languages/EN',
                'languages/DE', 
                'languages/FR',
                'languages/US',
                'temp',
                'cache'
            ]
            
            for subdir in subdirs:
                (base_path / subdir).mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Content directories initialized at {base_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize content directories: {e}")
            raise
    
    def get_client_manifest(self, version: str, language: str = 'EN') -> Dict[str, Any]:
        """Get client manifest filtered by version and language"""
        try:
            if not self.db_connection:
                raise Exception("Database connection not available")
            
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Base query for manifest
            base_query = """
            SELECT file_hash, file_path, file_size, file_category, file_extension
            FROM client_manifest 
            WHERE version_id = %s
            """
            
            # Language filtering
            if language != 'ALL':
                # Include language-specific files and non-language-specific files
                query = base_query + """
                AND (file_path LIKE %s OR file_path NOT LIKE '%/EU/%')
                ORDER BY file_category, file_path
                """
                lang_pattern = f"%/EU/{language}/%"
                cursor.execute(query, (version, lang_pattern))
            else:
                query = base_query + " ORDER BY file_category, file_path"
                cursor.execute(query, (version,))
            
            manifest_entries = cursor.fetchall()
            cursor.close()
            
            # Get version information
            version_cursor = self.db_connection.cursor(dictionary=True)
            version_query = """
            SELECT version_id, version_name, total_files, total_size_bytes, release_date
            FROM client_versions 
            WHERE version_id = %s
            """
            version_cursor.execute(version_query, (version,))
            version_info = version_cursor.fetchone()
            version_cursor.close()
            
            # Organize by category
            categories = {}
            total_size = 0
            
            for entry in manifest_entries:
                category = entry['file_category']
                if category not in categories:
                    categories[category] = {
                        'files': [],
                        'count': 0,
                        'size_bytes': 0
                    }
                
                categories[category]['files'].append(entry)
                categories[category]['count'] += 1
                categories[category]['size_bytes'] += entry['file_size']
                total_size += entry['file_size']
            
            manifest = {
                'version': version_info,
                'language': language,
                'categories': categories,
                'total_files': len(manifest_entries),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'manifest_entries': manifest_entries,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return manifest
            
        except Exception as e:
            logger.error(f"Failed to get client manifest: {e}")
            raise
    
    def validate_client_integrity(self, client_files: List[Dict], version: str = None) -> Dict[str, Any]:
        """Validate client file integrity against server manifest"""
        try:
            if version is None:
                version = self.config.manifest_version
            
            # Get server manifest
            server_manifest = self.get_client_manifest(version, 'ALL')
            server_files = {
                entry['file_hash']: entry 
                for entry in server_manifest['manifest_entries']
            }
            
            # Validation results
            validation = {
                'version': version,
                'client_files_checked': len(client_files),
                'server_files_total': len(server_files),
                'validation_status': 'unknown',
                'files': {
                    'valid': [],
                    'missing': [],
                    'corrupted': [],
                    'unknown': []
                },
                'categories': {
                    'executable': {'valid': 0, 'missing': 0, 'corrupted': 0},
                    'data': {'valid': 0, 'missing': 0, 'corrupted': 0},
                    'graphics': {'valid': 0, 'missing': 0, 'corrupted': 0},
                    'audio': {'valid': 0, 'missing': 0, 'corrupted': 0},
                    'other': {'valid': 0, 'missing': 0, 'corrupted': 0}
                },
                'security_issues': [],
                'recommendations': [],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Track client files
            client_hashes = set()
            
            # Validate each client file
            for client_file in client_files:
                file_hash = client_file.get('hash', '')
                file_path = client_file.get('path', '')
                file_size = client_file.get('size', 0)
                
                client_hashes.add(file_hash)
                
                if file_hash in server_files:
                    server_file = server_files[file_hash]
                    category = server_file['file_category']
                    
                    if server_file['file_size'] == file_size:
                        # File is valid
                        validation['files']['valid'].append({
                            'hash': file_hash,
                            'path': file_path,
                            'category': category,
                            'size': file_size
                        })
                        
                        safe_category = category if category in validation['categories'] else 'other'
                        validation['categories'][safe_category]['valid'] += 1
                        
                    else:
                        # File size mismatch (corrupted)
                        validation['files']['corrupted'].append({
                            'hash': file_hash,
                            'path': file_path,
                            'category': category,
                            'expected_size': server_file['file_size'],
                            'actual_size': file_size,
                            'issue': 'size_mismatch'
                        })
                        
                        safe_category = category if category in validation['categories'] else 'other'
                        validation['categories'][safe_category]['corrupted'] += 1
                        
                        # Add security warning for executable files
                        if category == 'executable':
                            validation['security_issues'].append({
                                'type': 'corrupted_executable',
                                'file': file_path,
                                'severity': 'high',
                                'description': 'Corrupted executable file detected'
                            })
                else:
                    # Unknown file (not in server manifest)
                    validation['files']['unknown'].append({
                        'hash': file_hash,
                        'path': file_path,
                        'size': file_size,
                        'issue': 'not_in_manifest'
                    })
                    
                    # Potential security issue for unknown executables
                    if file_path.lower().endswith(('.exe', '.dll')):
                        validation['security_issues'].append({
                            'type': 'unknown_executable',
                            'file': file_path,
                            'severity': 'critical',
                            'description': 'Unknown executable file not in official manifest'
                        })
            
            # Find missing files
            for server_hash, server_file in server_files.items():
                if server_hash not in client_hashes:
                    category = server_file['file_category']
                    
                    validation['files']['missing'].append({
                        'hash': server_hash,
                        'path': server_file['file_path'],
                        'category': category,
                        'size': server_file['file_size'],
                        'priority': self.get_file_priority(category, server_file['file_path'])
                    })
                    
                    safe_category = category if category in validation['categories'] else 'other'
                    validation['categories'][safe_category]['missing'] += 1
            
            # Sort missing files by priority
            validation['files']['missing'].sort(
                key=lambda x: (x['priority'], -x['size'])
            )
            
            # Determine overall validation status
            total_issues = (
                len(validation['files']['missing']) + 
                len(validation['files']['corrupted'])
            )
            
            if total_issues == 0:
                validation['validation_status'] = 'clean'
            elif any(f['category'] == 'executable' for f in validation['files']['missing']):
                validation['validation_status'] = 'critical'
            elif total_issues < 10:
                validation['validation_status'] = 'minor_issues'
            else:
                validation['validation_status'] = 'needs_update'
            
            # Generate recommendations
            validation['recommendations'] = self.generate_recommendations(validation)
            
            return validation
            
        except Exception as e:
            logger.error(f"Failed to validate client integrity: {e}")
            return {
                'error': str(e),
                'validation_status': 'error',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_file_priority(self, category: str, file_path: str) -> int:
        """Get download priority for a file (lower number = higher priority)"""
        priority_map = {
            'executable': 1,
            'data': 2,
            'graphics': 3,
            'audio': 4,
            'documentation': 5
        }
        
        base_priority = priority_map.get(category, 6)
        
        # Boost priority for critical system files
        critical_files = ['pol.exe', 'app.dll', 'polcore.dll', 'version.dat']
        if any(critical in file_path.lower() for critical in critical_files):
            base_priority = 0
        
        return base_priority
    
    def generate_recommendations(self, validation: Dict) -> List[Dict]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Critical security issues
        if validation['security_issues']:
            recommendations.append({
                'type': 'security',
                'priority': 'critical',
                'message': f"Found {len(validation['security_issues'])} security issues that require immediate attention",
                'action': 'Review unknown executables and corrupted files'
            })
        
        # Missing executable files
        missing_executables = [
            f for f in validation['files']['missing'] 
            if f['category'] == 'executable'
        ]
        if missing_executables:
            recommendations.append({
                'type': 'missing_critical',
                'priority': 'high',
                'message': f"Missing {len(missing_executables)} executable files",
                'action': 'Download critical system files immediately'
            })
        
        # Large number of missing files
        total_missing = len(validation['files']['missing'])
        if total_missing > 100:
            recommendations.append({
                'type': 'bulk_update',
                'priority': 'medium', 
                'message': f"Missing {total_missing} files - consider full client reinstall",
                'action': 'Download complete client package'
            })
        
        # Corrupted files
        if validation['files']['corrupted']:
            recommendations.append({
                'type': 'corruption',
                'priority': 'medium',
                'message': f"Found {len(validation['files']['corrupted'])} corrupted files",
                'action': 'Re-download corrupted files'
            })
        
        return recommendations
    
    def create_update_package(self, missing_files: List[Dict], language: str = 'EN') -> Dict[str, Any]:
        """Create optimized update package for missing files"""
        try:
            # Filter files by language preference
            filtered_files = self.filter_files_by_language(missing_files, language)
            
            # Group files by category and priority
            package_groups = {
                'critical': [],      # Executables and essential data
                'important': [],     # Core game data
                'standard': [],      # Graphics and UI
                'optional': []       # Audio and documentation
            }
            
            total_size = 0
            
            for file_info in filtered_files:
                file_size = file_info['size']
                total_size += file_size
                
                # Determine package group
                priority = file_info.get('priority', 5)
                category = file_info['category']
                
                if priority <= 1 or category == 'executable':
                    package_groups['critical'].append(file_info)
                elif priority <= 2 or category == 'data':
                    package_groups['important'].append(file_info)
                elif category in ['graphics', 'database']:
                    package_groups['standard'].append(file_info)
                else:
                    package_groups['optional'].append(file_info)
            
            # Calculate download estimates
            bandwidth_bps = self.config.max_bandwidth_mbps * 1024 * 1024
            estimated_time = total_size / bandwidth_bps if bandwidth_bps > 0 else 0
            
            update_package = {
                'language': language,
                'package_info': {
                    'total_files': len(filtered_files),
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2),
                    'estimated_download_time_seconds': int(estimated_time),
                    'estimated_download_time_formatted': self.format_duration(estimated_time)
                },
                'package_groups': {
                    group: {
                        'files': files,
                        'count': len(files),
                        'size_mb': round(sum(f['size'] for f in files) / (1024 * 1024), 2)
                    }
                    for group, files in package_groups.items()
                    if files  # Only include non-empty groups
                },
                'download_sequence': self.optimize_download_sequence(package_groups),
                'compression_info': {
                    'enabled': self.config.enable_compression,
                    'estimated_compression_ratio': 0.7,  # Typical compression for game assets
                    'compressed_size_mb': round(total_size * 0.7 / (1024 * 1024), 2) if self.config.enable_compression else None
                },
                'recommendations': self.generate_download_recommendations(package_groups, total_size),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return update_package
            
        except Exception as e:
            logger.error(f"Failed to create update package: {e}")
            return {'error': str(e)}
    
    def filter_files_by_language(self, files: List[Dict], language: str) -> List[Dict]:
        """Filter files based on language preference"""
        filtered = []
        
        for file_info in files:
            file_path = file_info['path']
            
            # Check if file is language-specific
            if '/EU/' in file_path:
                # Only include files for the specified language
                if f'/EU/{language}/' in file_path:
                    filtered.append(file_info)
            else:
                # Include non-language-specific files
                filtered.append(file_info)
        
        return filtered
    
    def optimize_download_sequence(self, package_groups: Dict) -> List[Dict]:
        """Optimize download sequence for best user experience"""
        sequence = []
        
        # Download order: critical -> important -> standard -> optional
        group_order = ['critical', 'important', 'standard', 'optional']
        
        for group_name in group_order:
            if group_name in package_groups:
                group_files = package_groups[group_name]
                
                # Sort within group: smallest first for quick wins, then by priority
                sorted_files = sorted(
                    group_files,
                    key=lambda x: (x.get('priority', 5), x['size'])
                )
                
                sequence.extend(sorted_files)
        
        return sequence
    
    def generate_download_recommendations(self, package_groups: Dict, total_size: int) -> List[Dict]:
        """Generate download strategy recommendations"""
        recommendations = []
        
        # Critical files recommendation
        if 'critical' in package_groups and package_groups['critical']:
            critical_count = len(package_groups['critical'])
            recommendations.append({
                'type': 'download_strategy',
                'priority': 'high',
                'message': f"Download {critical_count} critical files first to ensure basic functionality",
                'estimated_time': '< 1 minute'
            })
        
        # Large download recommendation
        total_mb = total_size / (1024 * 1024)
        if total_mb > 100:
            recommendations.append({
                'type': 'bandwidth',
                'priority': 'medium',
                'message': f"Large download ({total_mb:.1f} MB) - consider downloading during off-peak hours",
                'suggestion': 'Use download scheduler or pause/resume functionality'
            })
        
        # Compression recommendation
        if self.config.enable_compression:
            savings_mb = total_size * 0.3 / (1024 * 1024)
            recommendations.append({
                'type': 'optimization',
                'priority': 'info',
                'message': f"Compression enabled - saves approximately {savings_mb:.1f} MB bandwidth",
                'benefit': 'Faster downloads and reduced data usage'
            })
        
        return recommendations
    
    def get_download_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive download and usage statistics"""
        try:
            if not self.db_connection:
                raise Exception("Database connection not available")
            
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Daily download statistics
            daily_query = """
            SELECT 
                DATE(download_start) as date,
                COUNT(*) as total_downloads,
                COUNT(DISTINCT player_id) as unique_players,
                SUM(bytes_downloaded) / (1024 * 1024) as mb_downloaded,
                AVG(TIMESTAMPDIFF(SECOND, download_start, download_complete)) as avg_download_time
            FROM client_file_downloads 
            WHERE download_start >= DATE_SUB(NOW(), INTERVAL %s DAY)
            AND download_status = 'completed'
            GROUP BY DATE(download_start)
            ORDER BY date DESC
            """
            
            cursor.execute(daily_query, (days,))
            daily_stats = cursor.fetchall()
            
            # Category popularity
            category_query = """
            SELECT 
                cm.file_category,
                COUNT(cfd.download_id) as download_count,
                SUM(cm.file_size) / (1024 * 1024) as total_mb,
                AVG(cm.file_size) / (1024 * 1024) as avg_size_mb
            FROM client_file_downloads cfd
            JOIN client_manifest cm ON cfd.file_hash = cm.file_hash
            WHERE cfd.download_start >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY cm.file_category
            ORDER BY download_count DESC
            """
            
            cursor.execute(category_query, (days,))
            category_stats = cursor.fetchall()
            
            # Peak usage analysis
            hourly_query = """
            SELECT 
                HOUR(download_start) as hour,
                COUNT(*) as downloads,
                AVG(bytes_downloaded) / (1024 * 1024) as avg_mb
            FROM client_file_downloads 
            WHERE download_start >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY HOUR(download_start)
            ORDER BY downloads DESC
            """
            
            cursor.execute(hourly_query, (days,))
            hourly_stats = cursor.fetchall()
            
            # Error analysis
            error_query = """
            SELECT 
                download_status,
                COUNT(*) as count,
                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM client_file_downloads 
                                   WHERE download_start >= DATE_SUB(NOW(), INTERVAL %s DAY)) as percentage
            FROM client_file_downloads 
            WHERE download_start >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY download_status
            """
            
            cursor.execute(error_query, (days, days))
            status_stats = cursor.fetchall()
            
            cursor.close()
            
            # Calculate totals and averages
            total_downloads = sum(day['total_downloads'] for day in daily_stats)
            total_mb = sum(day['mb_downloaded'] for day in daily_stats if day['mb_downloaded'])
            
            statistics = {
                'period': {
                    'days': days,
                    'start_date': (datetime.now() - timedelta(days=days)).date().isoformat(),
                    'end_date': datetime.now().date().isoformat()
                },
                'totals': {
                    'downloads': total_downloads,
                    'unique_players': len(set(day['unique_players'] for day in daily_stats if day['unique_players'])),
                    'mb_transferred': round(total_mb, 2),
                    'avg_downloads_per_day': round(total_downloads / max(days, 1), 1)
                },
                'daily_breakdown': daily_stats,
                'category_popularity': category_stats,
                'peak_hours': hourly_stats[:5],  # Top 5 busiest hours
                'success_rate': {
                    'by_status': status_stats,
                    'overall_success_rate': round(
                        next((s['percentage'] for s in status_stats if s['download_status'] == 'completed'), 0), 1
                    )
                },
                'performance_metrics': {
                    'avg_file_size_mb': round(total_mb / max(total_downloads, 1), 3),
                    'bandwidth_utilization': round(total_mb / days / 24, 2),  # MB per hour average
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get download statistics: {e}")
            return {'error': str(e)}
    
    def format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def cleanup_cache(self, max_age_hours: int = None) -> Dict[str, Any]:
        """Clean up old cached content"""
        try:
            if max_age_hours is None:
                max_age_hours = self.config.cache_duration_hours
            
            cache_path = Path(self.config.content_base_path) / 'cache'
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=max_age_hours)
            
            deleted_files = 0
            freed_bytes = 0
            
            for cache_file in cache_path.rglob('*'):
                if cache_file.is_file():
                    file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                    if file_mtime < cutoff_time:
                        file_size = cache_file.stat().st_size
                        cache_file.unlink()
                        deleted_files += 1
                        freed_bytes += file_size
            
            return {
                'deleted_files': deleted_files,
                'freed_mb': round(freed_bytes / (1024 * 1024), 2),
                'cache_retention_hours': max_age_hours,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup cache: {e}")
            return {'error': str(e)}

# Integration functions for existing FFXI server components

def integrate_with_web_interface(app, content_delivery: PlayOnlineContentDelivery):
    """Integrate PlayOnline content delivery with existing web API"""
    
    @app.route('/api/playonline/content/manifest/<version>')
    def get_content_manifest(version):
        """Enhanced manifest endpoint with content delivery features"""
        language = request.args.get('language', 'EN')
        manifest = content_delivery.get_client_manifest(version, language)
        return jsonify(manifest)
    
    @app.route('/api/playonline/content/validate', methods=['POST'])
    def validate_content():
        """Enhanced validation with detailed integrity checking"""
        data = request.get_json()
        client_files = data.get('files', [])
        version = data.get('version', content_delivery.config.manifest_version)
        
        validation = content_delivery.validate_client_integrity(client_files, version)
        return jsonify(validation)
    
    @app.route('/api/playonline/content/update-package', methods=['POST'])
    def create_content_update_package():
        """Create optimized update package"""
        data = request.get_json()
        missing_files = data.get('missing_files', [])
        language = data.get('language', 'EN')
        
        package = content_delivery.create_update_package(missing_files, language)
        return jsonify(package)
    
    @app.route('/api/playonline/content/statistics')
    def get_content_statistics():
        """Get content delivery statistics"""
        days = int(request.args.get('days', 7))
        stats = content_delivery.get_download_statistics(days)
        return jsonify(stats)

def integrate_with_database_schema(db_connection):
    """Ensure database schema supports PlayOnline content delivery"""
    
    cursor = db_connection.cursor()
    
    # Additional indexes for performance
    performance_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_client_manifest_category_priority ON client_manifest(file_category, file_size)",
        "CREATE INDEX IF NOT EXISTS idx_client_downloads_player_status ON client_file_downloads(player_id, download_status)",
        "CREATE INDEX IF NOT EXISTS idx_client_downloads_hourly ON client_file_downloads(DATE(download_start), HOUR(download_start))",
    ]
    
    for index_sql in performance_indexes:
        try:
            cursor.execute(index_sql)
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")
    
    # Additional statistics table for analytics
    stats_table = """
    CREATE TABLE IF NOT EXISTS playonline_content_stats (
        stat_id BIGINT PRIMARY KEY AUTO_INCREMENT,
        stat_date DATE NOT NULL,
        stat_hour TINYINT NOT NULL,
        total_downloads INT DEFAULT 0,
        total_mb_transferred DECIMAL(10,2) DEFAULT 0,
        unique_players INT DEFAULT 0,
        average_speed_mbps DECIMAL(8,3) DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        UNIQUE KEY unique_date_hour (stat_date, stat_hour),
        INDEX idx_stats_date (stat_date)
    )
    """
    
    try:
        cursor.execute(stats_table)
        db_connection.commit()
        logger.info("PlayOnline content delivery database schema ready")
    except Exception as e:
        logger.error(f"Failed to create statistics table: {e}")
    
    cursor.close()

# Factory function for easy integration
def create_playonline_content_delivery(
    config_dict: Dict = None,
    db_connection = None
) -> PlayOnlineContentDelivery:
    """Factory function to create PlayOnline content delivery instance"""
    
    if config_dict is None:
        config_dict = {}
    
    config = ContentDeliveryConfig(**config_dict)
    
    return PlayOnlineContentDelivery(config, db_connection)