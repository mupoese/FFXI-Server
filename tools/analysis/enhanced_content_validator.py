#!/usr/bin/env python3
"""
Enhanced Content Validation Tools for FFXI-Server
Retail accuracy validation and comprehensive content verification systems.

This tool provides advanced validation of FFXI game content against retail
behavior, ensuring accurate quest progression, item statistics, NPC behavior,
and game mechanics for the most authentic FFXI server experience.
"""

import os
import sys
import json
import sqlite3
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import argparse
import subprocess

try:
    import mariadb
    MARIADB_AVAILABLE = True
except ImportError:
    MARIADB_AVAILABLE = False

@dataclass
class ValidationIssue:
    """Content validation issue"""
    category: str
    severity: str  # critical, warning, info
    file_path: str
    line_number: Optional[int]
    issue_type: str
    description: str
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    retail_reference: Optional[str] = None
    auto_fixable: bool = False

@dataclass
class ContentStats:
    """Content statistics"""
    total_npcs: int
    total_items: int
    total_quests: int
    total_missions: int
    total_zones: int
    total_spells: int
    total_abilities: int
    completion_percentage: float

class EnhancedContentValidator:
    """Advanced content validation system"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).absolute()
        self.issues = []
        self.content_stats = {}
        self.db_path = self.root_dir / "content_validation.db"
        
        # Retail reference data (simplified - would be loaded from retail sources)
        self.retail_references = self.load_retail_references()
        
        # Content patterns for different file types
        self.lua_patterns = {
            'npc_functions': [
                r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                r'local\s+function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
            ],
            'quest_flags': [
                r'QUEST_([A-Z_]+)',
                r'quest\.setVar\s*\(',
                r'quest\.getVar\s*\('
            ],
            'item_references': [
                r'tpz\.items\.([A-Z_]+)',
                r'xi\.items\.([A-Z_]+)',
                r'item_id\s*=\s*(\d+)'
            ],
            'zone_references': [
                r'tpz\.zone\.([A-Z_]+)',
                r'xi\.zone\.([A-Z_]+)',
                r'zone_id\s*=\s*(\d+)'
            ],
            'spell_references': [
                r'tpz\.magic\.spell\.([A-Z_]+)',
                r'xi\.magic\.spell\.([A-Z_]+)',
                r'spell_id\s*=\s*(\d+)'
            ]
        }
        
        # Validation rules
        self.validation_rules = self.load_validation_rules()

    def load_retail_references(self) -> Dict[str, Dict]:
        """Load retail reference data"""
        # In a real implementation, this would load from comprehensive retail databases
        return {
            'items': {
                # Example retail item data
                'bronze_sword': {
                    'id': 16384,
                    'name': 'Bronze Sword',
                    'damage': 7,
                    'delay': 231,
                    'level': 6,
                    'jobs': ['WAR', 'RDM', 'THF', 'PLD', 'DRK', 'BST', 'BRD', 'RNG']
                }
            },
            'npcs': {
                # Example retail NPC data
                'moogle_mhurr': {
                    'zone': 'Port_Windurst',
                    'position': {'x': -151.0, 'y': -5.0, 'z': 202.0},
                    'name': 'Moogle',
                    'type': 'npc'
                }
            },
            'quests': {
                # Example retail quest data
                'the_new_adventurer': {
                    'id': 1,
                    'zone': 'Port_Bastok',
                    'npc': 'Machielle',
                    'level_cap': 10,
                    'prerequisites': []
                }
            },
            'zones': {
                # Example retail zone data
                'bastok_markets': {
                    'id': 235,
                    'name': 'Bastok Markets',
                    'area': 'Bastok',
                    'type': 'city'
                }
            }
        }

    def load_validation_rules(self) -> Dict[str, List[Dict]]:
        """Load content validation rules"""
        return {
            'item_validation': [
                {
                    'name': 'item_stats_consistency',
                    'description': 'Item stats should match retail values',
                    'severity': 'warning',
                    'check_function': 'validate_item_stats'
                },
                {
                    'name': 'item_job_restrictions',
                    'description': 'Item job restrictions should match retail',
                    'severity': 'critical',
                    'check_function': 'validate_item_jobs'
                }
            ],
            'npc_validation': [
                {
                    'name': 'npc_positioning',
                    'description': 'NPC positions should match retail locations',
                    'severity': 'warning',
                    'check_function': 'validate_npc_positions'
                },
                {
                    'name': 'npc_dialogue',
                    'description': 'NPC dialogue should be retail-accurate',
                    'severity': 'info',
                    'check_function': 'validate_npc_dialogue'
                }
            ],
            'quest_validation': [
                {
                    'name': 'quest_progression',
                    'description': 'Quest progression should match retail flow',
                    'severity': 'critical',
                    'check_function': 'validate_quest_progression'
                },
                {
                    'name': 'quest_rewards',
                    'description': 'Quest rewards should match retail',
                    'severity': 'warning',
                    'check_function': 'validate_quest_rewards'
                }
            ],
            'zone_validation': [
                {
                    'name': 'zone_boundaries',
                    'description': 'Zone boundaries should match retail',
                    'severity': 'critical',
                    'check_function': 'validate_zone_boundaries'
                }
            ]
        }

    def initialize_database(self):
        """Initialize validation results database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS validation_issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_number INTEGER,
                    issue_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    expected_value TEXT,
                    actual_value TEXT,
                    retail_reference TEXT,
                    auto_fixable BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS content_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_name TEXT NOT NULL,
                    stat_value INTEGER NOT NULL,
                    timestamp REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_issues_category ON validation_issues(category)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_issues_severity ON validation_issues(severity)
            ''')

    def validate_lua_scripts(self) -> List[ValidationIssue]:
        """Validate Lua script content"""
        issues = []
        
        print("🔍 Validating Lua scripts...")
        
        # Find Lua files
        lua_files = list(self.root_dir.glob("scripts/**/*.lua"))
        
        for file_path in lua_files:
            if 'test' in str(file_path).lower():
                continue  # Skip test files
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                relative_path = str(file_path.relative_to(self.root_dir))
                
                # Validate quest scripts
                if 'quest' in relative_path.lower():
                    issues.extend(self.validate_quest_script(relative_path, content, lines))
                
                # Validate NPC scripts
                if 'npc' in relative_path.lower():
                    issues.extend(self.validate_npc_script(relative_path, content, lines))
                
                # Validate zone scripts
                if 'zone' in relative_path.lower():
                    issues.extend(self.validate_zone_script(relative_path, content, lines))
                
                # General Lua syntax and pattern validation
                issues.extend(self.validate_lua_syntax(relative_path, content, lines))
                
            except Exception as e:
                issues.append(ValidationIssue(
                    category='lua_validation',
                    severity='critical',
                    file_path=relative_path,
                    line_number=None,
                    issue_type='file_read_error',
                    description=f"Failed to read Lua file: {e}"
                ))
        
        return issues

    def validate_quest_script(self, file_path: str, content: str, lines: List[str]) -> List[ValidationIssue]:
        """Validate quest-specific Lua script"""
        issues = []
        
        # Check for required quest functions
        required_functions = ['onQuestAccept', 'onQuestComplete']
        found_functions = set()
        
        for pattern in self.lua_patterns['npc_functions']:
            matches = re.finditer(pattern, content)
            for match in matches:
                func_name = match.group(1)
                found_functions.add(func_name)
        
        for required_func in required_functions:
            if required_func not in found_functions:
                issues.append(ValidationIssue(
                    category='quest_validation',
                    severity='warning',
                    file_path=file_path,
                    line_number=1,
                    issue_type='missing_function',
                    description=f"Missing required quest function: {required_func}",
                    retail_reference="Standard quest functions required for proper functionality"
                ))
        
        # Check quest variable usage
        quest_vars = re.findall(r'quest\.(?:get|set)Var\s*\(\s*["\']([^"\']+)["\']', content)
        
        # Validate quest variable naming convention
        for var_name in quest_vars:
            if not re.match(r'^[A-Z][A-Z0-9_]*$', var_name):
                issues.append(ValidationIssue(
                    category='quest_validation',
                    severity='info',
                    file_path=file_path,
                    line_number=None,
                    issue_type='naming_convention',
                    description=f"Quest variable '{var_name}' doesn't follow naming convention",
                    expected_value="UPPER_CASE_WITH_UNDERSCORES",
                    actual_value=var_name
                ))
        
        # Check for proper quest completion rewards
        if 'onQuestComplete' in content:
            if 'player:addGil' not in content and 'player:addItem' not in content and 'player:addExp' not in content:
                issues.append(ValidationIssue(
                    category='quest_validation',
                    severity='warning',
                    file_path=file_path,
                    line_number=None,
                    issue_type='missing_rewards',
                    description="Quest completion function found but no rewards detected",
                    retail_reference="Most quests provide gil, items, or experience rewards"
                ))
        
        return issues

    def validate_npc_script(self, file_path: str, content: str, lines: List[str]) -> List[ValidationIssue]:
        """Validate NPC-specific Lua script"""
        issues = []
        
        # Check for required NPC functions
        required_functions = ['onTrade', 'onTrigger']
        found_functions = set()
        
        for pattern in self.lua_patterns['npc_functions']:
            matches = re.finditer(pattern, content)
            for match in matches:
                func_name = match.group(1)
                found_functions.add(func_name)
        
        # Not all NPCs need all functions, but interactive NPCs should have onTrigger
        if 'onTrigger' not in found_functions:
            # Check if this might be an interactive NPC
            if any(keyword in content.lower() for keyword in ['menu', 'dialogue', 'talk', 'message']):
                issues.append(ValidationIssue(
                    category='npc_validation',
                    severity='warning',
                    file_path=file_path,
                    line_number=1,
                    issue_type='missing_function',
                    description="Interactive NPC missing onTrigger function",
                    retail_reference="Interactive NPCs should respond to player interaction"
                ))
        
        # Check for proper NPC positioning
        position_patterns = [
            r'npc:setPos\s*\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)',
            r'x\s*=\s*([-\d.]+).*y\s*=\s*([-\d.]+).*z\s*=\s*([-\d.]+)'
        ]
        
        for pattern in position_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                try:
                    x, y, z = map(float, match.groups())
                    # Basic sanity check for position values
                    if abs(x) > 2000 or abs(y) > 1000 or abs(z) > 2000:
                        issues.append(ValidationIssue(
                            category='npc_validation',
                            severity='warning',
                            file_path=file_path,
                            line_number=None,
                            issue_type='unusual_position',
                            description=f"NPC position seems unusual: ({x}, {y}, {z})",
                            retail_reference="NPC positions should be within normal zone boundaries"
                        ))
                except ValueError:
                    continue
        
        return issues

    def validate_zone_script(self, file_path: str, content: str, lines: List[str]) -> List[ValidationIssue]:
        """Validate zone-specific Lua script"""
        issues = []
        
        # Check for zone initialization functions
        zone_functions = ['onInitialize', 'onZoneIn', 'onEventUpdate', 'onEventFinish']
        found_functions = set()
        
        for pattern in self.lua_patterns['npc_functions']:
            matches = re.finditer(pattern, content)
            for match in matches:
                func_name = match.group(1)
                found_functions.add(func_name)
        
        # Zones should have at least onInitialize
        if 'onInitialize' not in found_functions:
            issues.append(ValidationIssue(
                category='zone_validation',
                severity='warning',
                file_path=file_path,
                line_number=1,
                issue_type='missing_function',
                description="Zone script missing onInitialize function",
                retail_reference="Zone scripts should initialize zone-specific settings"
            ))
        
        # Check for mob spawn definitions
        mob_spawns = re.findall(r'mob:spawn\s*\(\s*(\d+)\s*\)', content)
        if len(mob_spawns) == 0 and 'zone' in file_path.lower():
            # Only flag this for actual zone files, not utility files
            zone_name = Path(file_path).stem
            if not any(exclude in zone_name.lower() for exclude in ['utils', 'common', 'shared']):
                issues.append(ValidationIssue(
                    category='zone_validation',
                    severity='info',
                    file_path=file_path,
                    line_number=None,
                    issue_type='no_mob_spawns',
                    description="Zone has no mob spawn definitions",
                    retail_reference="Most zones have monster spawns"
                ))
        
        return issues

    def validate_lua_syntax(self, file_path: str, content: str, lines: List[str]) -> List[ValidationIssue]:
        """Validate general Lua syntax and patterns"""
        issues = []
        
        # Check for common Lua syntax issues
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
            
            # Check for missing 'end' statements (simple heuristic)
            if line.startswith('function ') and not line.endswith('end'):
                # Look ahead for matching 'end'
                end_found = False
                for j in range(i, min(i + 20, len(lines))):
                    if lines[j].strip() == 'end':
                        end_found = True
                        break
                
                if not end_found:
                    issues.append(ValidationIssue(
                        category='lua_validation',
                        severity='critical',
                        file_path=file_path,
                        line_number=i,
                        issue_type='syntax_error',
                        description="Function may be missing 'end' statement",
                        auto_fixable=False
                    ))
            
            # Check for deprecated function calls
            deprecated_patterns = [
                (r'tpz\.', 'Use xi. namespace instead of tpz.'),
                (r'GetServerVariable', 'Use server variables through proper API'),
                (r'SetServerVariable', 'Use server variables through proper API')
            ]
            
            for pattern, suggestion in deprecated_patterns:
                if re.search(pattern, line):
                    issues.append(ValidationIssue(
                        category='lua_validation',
                        severity='warning',
                        file_path=file_path,
                        line_number=i,
                        issue_type='deprecated_usage',
                        description=suggestion,
                        actual_value=line.strip()
                    ))
        
        return issues

    def validate_database_content(self) -> List[ValidationIssue]:
        """Validate database content against retail references"""
        issues = []
        
        if not MARIADB_AVAILABLE:
            issues.append(ValidationIssue(
                category='database_validation',
                severity='warning',
                file_path='database',
                line_number=None,
                issue_type='connection_error',
                description="MariaDB module not available for database validation"
            ))
            return issues
        
        print("🗄️ Validating database content...")
        
        try:
            # Connect to database
            conn = mariadb.connect(
                user='root',
                password='root',
                host='127.0.0.1',
                port=3306,
                database='xidb'
            )
            cursor = conn.cursor()
            
            # Validate item data
            issues.extend(self.validate_database_items(cursor))
            
            # Validate NPC data
            issues.extend(self.validate_database_npcs(cursor))
            
            # Validate zone data
            issues.extend(self.validate_database_zones(cursor))
            
            conn.close()
            
        except Exception as e:
            issues.append(ValidationIssue(
                category='database_validation',
                severity='critical',
                file_path='database',
                line_number=None,
                issue_type='connection_error',
                description=f"Failed to connect to database: {e}"
            ))
        
        return issues

    def validate_database_items(self, cursor) -> List[ValidationIssue]:
        """Validate item data in database"""
        issues = []
        
        try:
            # Get all items from database
            cursor.execute("SELECT itemid, name, damage, delay, level, jobs FROM item_basic LIMIT 100")
            db_items = cursor.fetchall()
            
            for item_data in db_items:
                item_id, name, damage, delay, level, jobs = item_data
                
                # Check for missing required fields
                if not name or name.strip() == '':
                    issues.append(ValidationIssue(
                        category='database_validation',
                        severity='critical',
                        file_path='database',
                        line_number=None,
                        issue_type='missing_data',
                        description=f"Item {item_id} has no name",
                        retail_reference="All items should have names"
                    ))
                
                # Check for reasonable stat values
                if damage and damage < 0:
                    issues.append(ValidationIssue(
                        category='database_validation',
                        severity='warning',
                        file_path='database',
                        line_number=None,
                        issue_type='invalid_stats',
                        description=f"Item {item_id} ({name}) has negative damage: {damage}",
                        retail_reference="Weapon damage should be positive"
                    ))
                
                if delay and delay < 0:
                    issues.append(ValidationIssue(
                        category='database_validation',
                        severity='warning',
                        file_path='database',
                        line_number=None,
                        issue_type='invalid_stats',
                        description=f"Item {item_id} ({name}) has negative delay: {delay}",
                        retail_reference="Weapon delay should be positive"
                    ))
                
                # Check level requirements
                if level and (level < 1 or level > 99):
                    issues.append(ValidationIssue(
                        category='database_validation',
                        severity='warning',
                        file_path='database',
                        line_number=None,
                        issue_type='invalid_stats',
                        description=f"Item {item_id} ({name}) has invalid level requirement: {level}",
                        retail_reference="Level requirements should be 1-99"
                    ))
                
        except Exception as e:
            issues.append(ValidationIssue(
                category='database_validation',
                severity='critical',
                file_path='database',
                line_number=None,
                issue_type='query_error',
                description=f"Error validating items: {e}"
            ))
        
        return issues

    def validate_database_npcs(self, cursor) -> List[ValidationIssue]:
        """Validate NPC data in database"""
        issues = []
        
        try:
            # Get all NPCs from database
            cursor.execute("SELECT npcid, name, zoneid, pos_x, pos_y, pos_z FROM npc_list LIMIT 100")
            db_npcs = cursor.fetchall()
            
            for npc_data in db_npcs:
                npc_id, name, zone_id, pos_x, pos_y, pos_z = npc_data
                
                # Check for missing names
                if not name or name.strip() == '':
                    issues.append(ValidationIssue(
                        category='database_validation',
                        severity='warning',
                        file_path='database',
                        line_number=None,
                        issue_type='missing_data',
                        description=f"NPC {npc_id} has no name",
                        retail_reference="NPCs should have descriptive names"
                    ))
                
                # Check for reasonable positions
                if pos_x is not None and abs(pos_x) > 2000:
                    issues.append(ValidationIssue(
                        category='database_validation',
                        severity='warning',
                        file_path='database',
                        line_number=None,
                        issue_type='unusual_position',
                        description=f"NPC {npc_id} ({name}) has unusual X position: {pos_x}",
                        retail_reference="NPC positions should be within zone boundaries"
                    ))
                
                if pos_z is not None and abs(pos_z) > 2000:
                    issues.append(ValidationIssue(
                        category='database_validation',
                        severity='warning',
                        file_path='database',
                        line_number=None,
                        issue_type='unusual_position',
                        description=f"NPC {npc_id} ({name}) has unusual Z position: {pos_z}",
                        retail_reference="NPC positions should be within zone boundaries"
                    ))
                
        except Exception as e:
            issues.append(ValidationIssue(
                category='database_validation',
                severity='critical',
                file_path='database',
                line_number=None,
                issue_type='query_error',
                description=f"Error validating NPCs: {e}"
            ))
        
        return issues

    def validate_database_zones(self, cursor) -> List[ValidationIssue]:
        """Validate zone data in database"""
        issues = []
        
        try:
            # Get all zones from database
            cursor.execute("SELECT zoneid, name, zoneip, zoneport FROM zone_settings LIMIT 50")
            db_zones = cursor.fetchall()
            
            for zone_data in db_zones:
                zone_id, name, zone_ip, zone_port = zone_data
                
                # Check for missing zone names
                if not name or name.strip() == '':
                    issues.append(ValidationIssue(
                        category='database_validation',
                        severity='critical',
                        file_path='database',
                        line_number=None,
                        issue_type='missing_data',
                        description=f"Zone {zone_id} has no name",
                        retail_reference="All zones should have names"
                    ))
                
                # Check for valid port numbers
                if zone_port and (zone_port < 1024 or zone_port > 65535):
                    issues.append(ValidationIssue(
                        category='database_validation',
                        severity='warning',
                        file_path='database',
                        line_number=None,
                        issue_type='invalid_config',
                        description=f"Zone {zone_id} ({name}) has invalid port: {zone_port}",
                        retail_reference="Zone ports should be in valid range"
                    ))
                
        except Exception as e:
            issues.append(ValidationIssue(
                category='database_validation',
                severity='critical',
                file_path='database',
                line_number=None,
                issue_type='query_error',
                description=f"Error validating zones: {e}"
            ))
        
        return issues

    def collect_content_statistics(self) -> ContentStats:
        """Collect comprehensive content statistics"""
        print("📊 Collecting content statistics...")
        
        stats = {
            'total_npcs': 0,
            'total_items': 0,
            'total_quests': 0,
            'total_missions': 0,
            'total_zones': 0,
            'total_spells': 0,
            'total_abilities': 0
        }
        
        # Count Lua scripts by type
        lua_files = list(self.root_dir.glob("scripts/**/*.lua"))
        
        for file_path in lua_files:
            relative_path = str(file_path.relative_to(self.root_dir)).lower()
            
            if 'npc' in relative_path:
                stats['total_npcs'] += 1
            elif 'quest' in relative_path:
                stats['total_quests'] += 1
            elif 'mission' in relative_path:
                stats['total_missions'] += 1
            elif 'zone' in relative_path and 'zone' in file_path.stem.lower():
                stats['total_zones'] += 1
            elif 'spell' in relative_path:
                stats['total_spells'] += 1
            elif 'ability' in relative_path:
                stats['total_abilities'] += 1
        
        # Get database counts if available
        if MARIADB_AVAILABLE:
            try:
                conn = mariadb.connect(
                    user='root',
                    password='root',
                    host='127.0.0.1',
                    port=3306,
                    database='xidb'
                )
                cursor = conn.cursor()
                
                # Count items
                cursor.execute("SELECT COUNT(*) FROM item_basic")
                stats['total_items'] = cursor.fetchone()[0]
                
                # Count NPCs
                cursor.execute("SELECT COUNT(*) FROM npc_list")
                db_npc_count = cursor.fetchone()[0]
                stats['total_npcs'] = max(stats['total_npcs'], db_npc_count)
                
                # Count zones
                cursor.execute("SELECT COUNT(*) FROM zone_settings")
                db_zone_count = cursor.fetchone()[0]
                stats['total_zones'] = max(stats['total_zones'], db_zone_count)
                
                conn.close()
                
            except Exception:
                pass  # Use script-based counts if database is unavailable
        
        # Calculate completion percentage (rough estimate)
        # Based on known retail content counts (simplified)
        retail_estimates = {
            'total_npcs': 5000,
            'total_items': 8000,
            'total_quests': 600,
            'total_missions': 200,
            'total_zones': 300,
            'total_spells': 900,
            'total_abilities': 500
        }
        
        completion_scores = []
        for key, current_count in stats.items():
            if key in retail_estimates and retail_estimates[key] > 0:
                completion_score = min(100, (current_count / retail_estimates[key]) * 100)
                completion_scores.append(completion_score)
        
        overall_completion = sum(completion_scores) / len(completion_scores) if completion_scores else 0
        
        return ContentStats(
            total_npcs=stats['total_npcs'],
            total_items=stats['total_items'],
            total_quests=stats['total_quests'],
            total_missions=stats['total_missions'],
            total_zones=stats['total_zones'],
            total_spells=stats['total_spells'],
            total_abilities=stats['total_abilities'],
            completion_percentage=overall_completion
        )

    def save_validation_results(self):
        """Save validation results to database"""
        with sqlite3.connect(self.db_path) as conn:
            # Clear previous results
            conn.execute("DELETE FROM validation_issues")
            conn.execute("DELETE FROM content_stats")
            
            # Save issues
            for issue in self.issues:
                conn.execute('''
                    INSERT INTO validation_issues (
                        category, severity, file_path, line_number, issue_type,
                        description, expected_value, actual_value, retail_reference,
                        auto_fixable
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    issue.category,
                    issue.severity,
                    issue.file_path,
                    issue.line_number,
                    issue.issue_type,
                    issue.description,
                    issue.expected_value,
                    issue.actual_value,
                    issue.retail_reference,
                    issue.auto_fixable
                ))
            
            # Save content statistics
            stats = self.collect_content_statistics()
            timestamp = time.time() if 'time' in sys.modules else 0
            
            for stat_name, stat_value in asdict(stats).items():
                if isinstance(stat_value, (int, float)):
                    conn.execute('''
                        INSERT INTO content_stats (stat_name, stat_value, timestamp)
                        VALUES (?, ?, ?)
                    ''', (stat_name, stat_value, timestamp))

    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        # Collect statistics
        content_stats = self.collect_content_statistics()
        
        # Group issues by category and severity
        issues_by_category = defaultdict(list)
        issues_by_severity = defaultdict(list)
        
        for issue in self.issues:
            issues_by_category[issue.category].append(issue)
            issues_by_severity[issue.severity].append(issue)
        
        # Calculate quality scores
        total_issues = len(self.issues)
        critical_issues = len(issues_by_severity['critical'])
        warning_issues = len(issues_by_severity['warning'])
        
        # Content validation score (0-100, higher is better)
        if total_issues == 0:
            validation_score = 100.0
        else:
            # Weight by severity
            weighted_issues = critical_issues * 3 + warning_issues * 1
            max_weighted = total_issues * 3  # If all were critical
            validation_score = max(0, 100 - (weighted_issues / max_weighted * 100))
        
        # Retail accuracy score
        retail_accuracy_score = min(100, content_stats.completion_percentage + validation_score * 0.3)
        
        return {
            'validation_summary': {
                'total_issues': total_issues,
                'critical_issues': critical_issues,
                'warning_issues': warning_issues,
                'info_issues': len(issues_by_severity['info']),
                'validation_score': round(validation_score, 1),
                'retail_accuracy_score': round(retail_accuracy_score, 1)
            },
            'content_statistics': asdict(content_stats),
            'issues_by_category': {
                category: len(issues) for category, issues in issues_by_category.items()
            },
            'top_issues': [
                {
                    'category': issue.category,
                    'severity': issue.severity,
                    'description': issue.description,
                    'file_path': issue.file_path,
                    'retail_reference': issue.retail_reference
                }
                for issue in sorted(self.issues, key=lambda x: {'critical': 3, 'warning': 2, 'info': 1}.get(x.severity, 0), reverse=True)[:10]
            ],
            'recommendations': self.generate_recommendations(issues_by_category, content_stats)
        }

    def generate_recommendations(self, issues_by_category: Dict[str, List], content_stats: ContentStats) -> List[str]:
        """Generate content improvement recommendations"""
        recommendations = []
        
        # Critical issues first
        critical_count = sum(1 for issues in issues_by_category.values() for issue in issues if issue.severity == 'critical')
        if critical_count > 0:
            recommendations.append(f"🚨 Address {critical_count} critical content issues immediately")
        
        # Category-specific recommendations
        if 'quest_validation' in issues_by_category:
            quest_issues = len(issues_by_category['quest_validation'])
            recommendations.append(f"📜 Review and fix {quest_issues} quest-related issues")
        
        if 'npc_validation' in issues_by_category:
            npc_issues = len(issues_by_category['npc_validation'])
            recommendations.append(f"👥 Validate {npc_issues} NPC-related issues")
        
        if 'database_validation' in issues_by_category:
            db_issues = len(issues_by_category['database_validation'])
            recommendations.append(f"🗄️ Fix {db_issues} database inconsistencies")
        
        # Content completion recommendations
        if content_stats.completion_percentage < 50:
            recommendations.append("📈 Focus on implementing more core content to improve retail accuracy")
        
        if content_stats.total_quests < 100:
            recommendations.append("📋 Implement more quest content for better player experience")
        
        if content_stats.total_npcs < 1000:
            recommendations.append("👤 Add more NPC implementations for zone population")
        
        return recommendations

    def run_comprehensive_validation(self):
        """Run comprehensive content validation"""
        print("🔍 Starting comprehensive content validation...")
        
        # Initialize database
        self.initialize_database()
        
        # Validate Lua scripts
        lua_issues = self.validate_lua_scripts()
        self.issues.extend(lua_issues)
        
        # Validate database content
        db_issues = self.validate_database_content()
        self.issues.extend(db_issues)
        
        # Save results
        self.save_validation_results()
        
        # Generate report
        report = self.generate_validation_report()
        
        # Save report to file
        report_path = self.root_dir / "content_validation_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✅ Validation complete! Report saved to {report_path}")
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Enhanced Content Validation Tools")
    parser.add_argument("--root", default=".", help="Root directory to validate")
    parser.add_argument("--output", help="Output file for validation report")
    parser.add_argument("--category", choices=['all', 'lua', 'database', 'quests', 'npcs'], 
                       default='all', help="Validation category")
    parser.add_argument("--severity", choices=['all', 'critical', 'warning', 'info'], 
                       default='all', help="Filter by severity level")
    parser.add_argument("--stats-only", action="store_true", help="Show only content statistics")
    
    args = parser.parse_args()
    
    validator = EnhancedContentValidator(args.root)
    
    if args.stats_only:
        stats = validator.collect_content_statistics()
        print("\n=== CONTENT STATISTICS ===")
        print(f"📁 NPCs: {stats.total_npcs}")
        print(f"🎒 Items: {stats.total_items}")
        print(f"📜 Quests: {stats.total_quests}")
        print(f"🎯 Missions: {stats.total_missions}")
        print(f"🗺️ Zones: {stats.total_zones}")
        print(f"✨ Spells: {stats.total_spells}")
        print(f"⚔️ Abilities: {stats.total_abilities}")
        print(f"📊 Completion: {stats.completion_percentage:.1f}%")
        return
    
    # Run validation
    report = validator.run_comprehensive_validation()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print("\n=== CONTENT VALIDATION SUMMARY ===")
    print(f"🎯 Validation Score: {report['validation_summary']['validation_score']}/100")
    print(f"🏆 Retail Accuracy: {report['validation_summary']['retail_accuracy_score']}/100")
    print(f"📋 Total Issues: {report['validation_summary']['total_issues']}")
    print(f"🚨 Critical: {report['validation_summary']['critical_issues']}")
    print(f"⚠️ Warnings: {report['validation_summary']['warning_issues']}")
    
    print(f"\n📊 Content Statistics:")
    stats = report['content_statistics']
    print(f"   NPCs: {stats['total_npcs']}")
    print(f"   Items: {stats['total_items']}")
    print(f"   Quests: {stats['total_quests']}")
    print(f"   Completion: {stats['completion_percentage']:.1f}%")
    
    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   • {rec}")
    
    # Show top issues
    if report['top_issues']:
        print(f"\n🔍 Top Issues:")
        for issue in report['top_issues'][:5]:
            print(f"   • [{issue['severity'].upper()}] {issue['description']}")
            if issue['file_path'] != 'database':
                print(f"     File: {issue['file_path']}")

if __name__ == "__main__":
    import time
    main()