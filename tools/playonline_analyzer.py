#!/usr/bin/env python3
"""
PlayOnline Manifest Parser and Analyzer
Utility for processing FFXI PlayOnlineViewer file manifests and patch data

This tool demonstrates integration potential between the original PlayOnline
update system and the modern FFXI server infrastructure.
"""

import os
import sys
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ManifestEntry:
    """Represents a single file entry in PlayOnline manifest"""
    hash: str
    size: int
    path: str
    category: str = ""
    language: str = ""
    
    def __post_init__(self):
        """Auto-categorize file based on path and extension"""
        path_lower = self.path.lower()
        
        # Determine language
        if '/eu/de/' in path_lower:
            self.language = 'DE'
        elif '/eu/en/' in path_lower:
            self.language = 'EN'
        elif '/eu/fr/' in path_lower:
            self.language = 'FR'
        else:
            self.language = 'US'
        
        # Categorize by file type and location
        if path_lower.endswith(('.pfb', '.pib')):
            self.category = 'database'
        elif path_lower.endswith(('.spw', '.bgw')):
            self.category = 'audio'
        elif path_lower.endswith(('.png', '.ang')):
            self.category = 'graphics'
        elif path_lower.endswith(('.dll', '.exe')):
            self.category = 'executable'
        elif path_lower.endswith(('.bin', '.dat')):
            self.category = 'data'
        elif path_lower.endswith(('.txt', '.chm')):
            self.category = 'documentation'
        elif 'patchfiles' in path_lower:
            self.category = 'patch'
        else:
            self.category = 'other'

class PlayOnlineManifestParser:
    """Parser for PlayOnline file manifests and patch configurations"""
    
    def __init__(self, squareenix_path: str):
        self.base_path = Path(squareenix_path)
        self.pol_path = self.base_path / "PlayOnlineViewer"
        self.manifest_entries: List[ManifestEntry] = []
        self.patch_entries: List[ManifestEntry] = []
        
    def parse_manifest_file(self, file_path: Path) -> List[ManifestEntry]:
        """Parse a manifest file (file.txt or patch.txt)"""
        entries = []
        
        if not file_path.exists():
            print(f"Warning: {file_path} not found")
            return entries
            
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            line_num = 0
            for line in f:
                line_num += 1
                line = line.strip()
                
                # Skip empty lines and malformed entries
                if not line or line.count(':') < 2:
                    continue
                    
                try:
                    # Format: hash:size:filepath
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        hash_val = parts[0].strip()
                        size = int(parts[1].strip())
                        path = parts[2].strip()
                        
                        entries.append(ManifestEntry(
                            hash=hash_val,
                            size=size,
                            path=path
                        ))
                except (ValueError, IndexError) as e:
                    print(f"Warning: Malformed line {line_num} in {file_path}: {line}")
                    continue
                    
        return entries
    
    def load_manifests(self):
        """Load both file.txt and patch.txt manifests"""
        # Load main file manifest
        file_manifest_path = self.pol_path / "file.txt"
        self.manifest_entries = self.parse_manifest_file(file_manifest_path)
        print(f"Loaded {len(self.manifest_entries)} entries from file.txt")
        
        # Load patch manifest
        patch_manifest_path = self.pol_path / "patch.txt"
        self.patch_entries = self.parse_manifest_file(patch_manifest_path)
        print(f"Loaded {len(self.patch_entries)} entries from patch.txt")
    
    def get_statistics(self) -> Dict:
        """Generate comprehensive statistics about the manifest"""
        all_entries = self.manifest_entries + self.patch_entries
        
        stats = {
            'total_files': len(all_entries),
            'total_size_bytes': sum(entry.size for entry in all_entries),
            'total_size_mb': sum(entry.size for entry in all_entries) / (1024 * 1024),
            'by_category': {},
            'by_language': {},
            'by_extension': {},
            'largest_files': [],
            'executables': []
        }
        
        # Count by category
        for entry in all_entries:
            stats['by_category'][entry.category] = stats['by_category'].get(entry.category, 0) + 1
            stats['by_language'][entry.language] = stats['by_language'].get(entry.language, 0) + 1
            
            # Count by extension
            ext = Path(entry.path).suffix.lower()
            if ext:
                stats['by_extension'][ext] = stats['by_extension'].get(ext, 0) + 1
        
        # Find largest files (top 10)
        stats['largest_files'] = sorted(all_entries, key=lambda x: x.size, reverse=True)[:10]
        
        # Find all executables
        stats['executables'] = [e for e in all_entries if e.category == 'executable']
        
        return stats
    
    def generate_server_integration_suggestions(self) -> Dict:
        """Generate specific suggestions for FFXI server integration"""
        stats = self.get_statistics()
        
        suggestions = {
            'database_integration': {
                'description': 'Store manifest data in server database for client validation',
                'sql_schema': '''
                    CREATE TABLE client_files (
                        file_hash VARCHAR(64) PRIMARY KEY,
                        file_path VARCHAR(512) NOT NULL,
                        file_size BIGINT NOT NULL,
                        category VARCHAR(50),
                        language_code CHAR(2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE INDEX idx_client_files_category ON client_files(category);
                    CREATE INDEX idx_client_files_language ON client_files(language_code);
                ''',
                'entries_to_store': len(self.manifest_entries + self.patch_entries)
            },
            
            'api_endpoints': {
                'description': 'REST API endpoints for client update system',
                'endpoints': [
                    'GET /api/client/manifest/{version}',
                    'GET /api/client/file/{hash}',
                    'POST /api/client/validate',
                    'GET /api/client/patches/available',
                    'GET /api/client/language/{lang}/files'
                ]
            },
            
            'content_delivery': {
                'description': 'CDN and caching strategy',
                'total_size_mb': round(stats['total_size_mb'], 2),
                'largest_files_mb': [
                    {
                        'path': entry.path,
                        'size_mb': round(entry.size / (1024 * 1024), 2)
                    } for entry in stats['largest_files'][:5]
                ],
                'caching_priority': {
                    'high': ['executable', 'data'],
                    'medium': ['graphics', 'audio'],
                    'low': ['documentation']
                }
            },
            
            'multi_language_support': {
                'description': 'Language-specific content delivery',
                'languages': list(stats['by_language'].keys()),
                'implementation': 'Route requests based on client language preference'
            }
        }
        
        return suggestions
    
    def export_analysis(self, output_file: str):
        """Export complete analysis to JSON file"""
        analysis = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'source_path': str(self.pol_path),
                'version': self.get_version_info()
            },
            'statistics': self.get_statistics(),
            'integration_suggestions': self.generate_server_integration_suggestions(),
            'file_entries': [asdict(entry) for entry in self.manifest_entries[:100]], # Sample entries
            'patch_entries': [asdict(entry) for entry in self.patch_entries[:100]]   # Sample entries
        }
        
        # Convert large file entries to simplified format
        stats = analysis['statistics']
        stats['largest_files'] = [
            {
                'path': entry.path,
                'size_mb': round(entry.size / (1024 * 1024), 2),
                'category': entry.category,
                'language': entry.language
            } for entry in stats['largest_files']
        ]
        
        stats['executables'] = [
            {
                'path': entry.path,
                'size_mb': round(entry.size / (1024 * 1024), 2)
            } for entry in stats['executables']
        ]
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"Analysis exported to {output_file}")
    
    def get_version_info(self) -> str:
        """Extract version information from version.dat"""
        version_file = self.pol_path / "version.dat"
        if version_file.exists():
            try:
                with open(version_file, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read().strip()
            except:
                return "unknown"
        return "not_found"
    
    def print_summary_report(self):
        """Print a human-readable summary report"""
        stats = self.get_statistics()
        suggestions = self.generate_server_integration_suggestions()
        
        print("\n" + "="*80)
        print("PLAYONLINE MANIFEST ANALYSIS REPORT")
        print("="*80)
        
        print(f"\nVERSION: {self.get_version_info()}")
        print(f"ANALYSIS DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\nOVERALL STATISTICS:")
        print(f"  Total Files: {stats['total_files']:,}")
        print(f"  Total Size: {stats['total_size_mb']:.1f} MB")
        
        print(f"\nFILES BY CATEGORY:")
        for category, count in sorted(stats['by_category'].items()):
            print(f"  {category.capitalize():15}: {count:,}")
        
        print(f"\nFILES BY LANGUAGE:")
        for language, count in sorted(stats['by_language'].items()):
            print(f"  {language:15}: {count:,}")
        
        print(f"\nLARGEST FILES:")
        for i, entry in enumerate(stats['largest_files'][:5], 1):
            size_mb = entry.size / (1024 * 1024)
            print(f"  {i}. {entry.path[:60]:<60} {size_mb:8.1f} MB")
        
        print(f"\nEXECUTABLES FOUND:")
        for exe in stats['executables']:
            size_mb = exe.size / (1024 * 1024)
            print(f"  {exe.path:<50} {size_mb:8.1f} MB")
        
        print(f"\nSERVER INTEGRATION OPPORTUNITIES:")
        print(f"  Database Entries: {suggestions['database_integration']['entries_to_store']:,}")
        print(f"  API Endpoints: {len(suggestions['api_endpoints']['endpoints'])}")
        print(f"  CDN Content: {suggestions['content_delivery']['total_size_mb']:.1f} MB")
        print(f"  Languages: {', '.join(suggestions['multi_language_support']['languages'])}")
        
        print("\n" + "="*80)

def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python playonline_analyzer.py <path_to_squareenix_directory>")
        print("Example: python playonline_analyzer.py ./SquareEnix")
        sys.exit(1)
    
    squareenix_path = sys.argv[1]
    
    if not os.path.exists(squareenix_path):
        print(f"Error: Directory {squareenix_path} not found")
        sys.exit(1)
    
    print("Initializing PlayOnline manifest parser...")
    parser = PlayOnlineManifestParser(squareenix_path)
    
    print("Loading manifest files...")
    parser.load_manifests()
    
    # Print summary report
    parser.print_summary_report()
    
    # Export detailed analysis
    output_file = "playonline_analysis.json"
    parser.export_analysis(output_file)
    
    print(f"\nFor detailed integration guidance, see the README.md file in {squareenix_path}")
    print("This analysis provides the foundation for implementing PlayOnline-style")
    print("update capabilities in your FFXI server infrastructure.")

if __name__ == "__main__":
    main()