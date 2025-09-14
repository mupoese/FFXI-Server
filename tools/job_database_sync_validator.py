#!/usr/bin/env python3
"""
Job Database Synchronization Validator
======================================

This script validates that all 22 FFXI jobs have proper database entries
synchronized with their Lua utility implementations.

Purpose:
- Identify missing abilities in database vs Lua implementations
- Validate spell accessibility for magic jobs
- Ensure all job utility functions have corresponding database entries
- Generate missing database entries for complete job implementations
"""

import os
import re
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

class JobDatabaseSyncValidator:
    def __init__(self, repo_root="/home/runner/work/FFXI-Server/FFXI-Server"):
        self.repo_root = Path(repo_root)
        self.scripts_dir = self.repo_root / "scripts"
        self.sql_dir = self.repo_root / "sql"
        
        # All 22 FFXI jobs with their IDs
        self.all_jobs = {
            1: "warrior", 2: "monk", 3: "white_mage", 4: "black_mage", 5: "red_mage",
            6: "thief", 7: "paladin", 8: "dark_knight", 9: "beastmaster", 10: "bard",
            11: "ranger", 12: "samurai", 13: "ninja", 14: "dragoon", 15: "summoner",
            16: "blue_mage", 17: "corsair", 18: "puppetmaster", 19: "dancer", 
            20: "scholar", 21: "geomancer", 22: "rune_fencer"
        }
        
        # Track validation results
        self.validation_results = {}
        self.missing_abilities = {}
        self.database_gaps = {}
        
    def analyze_lua_job_abilities(self, job_name: str) -> Dict:
        """Extract abilities from job Lua utility file"""
        lua_file = self.scripts_dir / "globals" / "job_utils" / f"{job_name}.lua"
        
        if not lua_file.exists():
            return {"exists": False, "abilities": [], "functions": 0}
        
        content = lua_file.read_text(encoding='utf-8')
        
        # Extract function definitions (more comprehensive patterns)
        function_patterns = [
            r'function\s+[\w\.]+\.(\w+)',
            r'local\s+function\s+(\w+)',
            r'xi\.job_utils\.[\w_]+\.(\w+)\s*=\s*function',
            r'[\w_]+\.(\w+)\s*=\s*function'
        ]
        
        functions = set()
        for pattern in function_patterns:
            matches = re.findall(pattern, content)
            functions.update(matches)
        
        # Extract ability names from job ability definitions
        abilities = set()
        
        # Look for ability constants and definitions
        ability_patterns = [
            r'xi\.jobAbility\.(\w+)',
            r'xi\.ability\.(\w+)', 
            r'ABILITY_(\w+)',
            r'\[(\w+)\]\s*=.*level.*=',  # ability table definitions
            r'use(\w+)(?:Ability)?',
            r'handle(\w+)(?:Ability)?',
            r'check(\w+)(?:Ability)?',
            r'validate(\w+)',
            r'apply(\w+)(?:Effect)?'
        ]
        
        for pattern in ability_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            abilities.update([match.lower() for match in matches])
        
        # Extract abilities from ability tables/lists
        ability_table_matches = re.findall(r'\[xi\.jobAbility\.(\w+)\]', content)
        abilities.update([match.lower() for match in ability_table_matches])
            
        # Look for spell access patterns for magic jobs
        spells = set()
        if job_name in ['white_mage', 'black_mage', 'red_mage', 'summoner', 'blue_mage', 'scholar', 'geomancer']:
            spell_patterns = [
                r'xi\.magic\.spell\.(\w+)',
                r'SPELL_(\w+)',
                r'canLearn.*?(\w+)',
                r'hasSpell.*?(\w+)',
                r'canCast.*?(\w+)',
                r'\.(\w+)_SPELL'
            ]
            
            for pattern in spell_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                spells.update([match.lower() for match in matches])
        
        return {
            "exists": True,
            "abilities": list(abilities),
            "spells": list(spells),
            "functions": len(functions),
            "file_size": lua_file.stat().st_size,
            "lines": len(content.split('\n'))
        }
    
    def analyze_database_entries(self, job_id: int) -> Dict:
        """Check database entries for a specific job"""
        try:
            # Create temporary database to test SQL files
            test_db = ":memory:"
            conn = sqlite3.connect(test_db)
            cursor = conn.cursor()
            
            # Load abilities table
            abilities_sql = self.sql_dir / "abilities.sql"
            if abilities_sql.exists():
                try:
                    content = abilities_sql.read_text(encoding='utf-8')
                    # Skip problematic statements and focus on INSERT statements
                    insert_statements = re.findall(r'INSERT INTO `abilities`[^;]+;', content, re.IGNORECASE)
                    
                    # Create simplified table for testing
                    cursor.execute("""
                        CREATE TABLE abilities (
                            abilityId INTEGER,
                            name TEXT,
                            job INTEGER,
                            level INTEGER
                        )
                    """)
                    
                    abilities = []
                    for stmt in insert_statements:
                        # Extract values from INSERT statement
                        values_match = re.search(r'VALUES\s*\(([^)]+)\)', stmt)
                        if values_match:
                            values = values_match.group(1).split(',')
                            if len(values) >= 4:
                                try:
                                    ability_id = int(values[0].strip())
                                    name = values[1].strip().strip("'\"")
                                    job = int(values[2].strip())
                                    level = int(values[3].strip())
                                    
                                    if job == job_id:
                                        abilities.append({
                                            "id": ability_id,
                                            "name": name,
                                            "level": level
                                        })
                                        cursor.execute("INSERT INTO abilities VALUES (?, ?, ?, ?)",
                                                     (ability_id, name, job, level))
                                except (ValueError, IndexError):
                                    continue
                    
                    conn.commit()
                    
                    return {
                        "abilities": abilities,
                        "ability_count": len(abilities),
                        "ability_names": [a["name"] for a in abilities]
                    }
                    
                except Exception as e:
                    print(f"Error processing abilities.sql: {e}")
                    return {"abilities": [], "ability_count": 0, "ability_names": []}
            
            conn.close()
            return {"abilities": [], "ability_count": 0, "ability_names": []}
            
        except Exception as e:
            print(f"Database analysis error for job {job_id}: {e}")
            return {"abilities": [], "ability_count": 0, "ability_names": []}
    
    def validate_job_completion(self, job_id: int, job_name: str) -> Dict:
        """Validate complete job implementation against database"""
        print(f"🔍 Validating {job_name.title()} (Job ID: {job_id})...")
        
        # Analyze Lua implementation
        lua_analysis = self.analyze_lua_job_abilities(job_name)
        
        # Analyze database entries
        db_analysis = self.analyze_database_entries(job_id)
        
        # Calculate completion metrics
        lua_ability_count = len(lua_analysis.get("abilities", []))
        db_ability_count = db_analysis.get("ability_count", 0)
        
        # Determine completion status
        if lua_analysis.get("functions", 0) >= 30 and db_ability_count >= 5:
            status = "COMPLETE"
        elif lua_analysis.get("functions", 0) >= 20 and db_ability_count >= 3:
            status = "HIGH"
        elif lua_analysis.get("functions", 0) >= 10:
            status = "MEDIUM"
        else:
            status = "LOW"
        
        # Identify gaps
        lua_abilities = set(lua_analysis.get("abilities", []))
        db_abilities = set(db_analysis.get("ability_names", []))
        
        missing_in_db = lua_abilities - db_abilities
        missing_in_lua = db_abilities - lua_abilities
        
        result = {
            "job_id": job_id,
            "job_name": job_name,
            "status": status,
            "lua_file_exists": lua_analysis.get("exists", False),
            "lua_functions": lua_analysis.get("functions", 0),
            "lua_abilities": lua_ability_count,
            "lua_spells": len(lua_analysis.get("spells", [])),
            "db_abilities": db_ability_count,
            "db_ability_names": db_analysis.get("ability_names", []),
            "missing_in_db": list(missing_in_db),
            "missing_in_lua": list(missing_in_lua),
            "file_size": lua_analysis.get("file_size", 0),
            "lines": lua_analysis.get("lines", 0)
        }
        
        # Print status
        if status == "COMPLETE":
            print(f"  ✅ {status}: {lua_analysis.get('functions', 0)} functions, {db_ability_count} DB abilities")
        else:
            print(f"  ⚠️  {status}: {lua_analysis.get('functions', 0)} functions, {db_ability_count} DB abilities")
            if missing_in_db:
                print(f"    Missing in DB: {', '.join(list(missing_in_db)[:3])}{'...' if len(missing_in_db) > 3 else ''}")
        
        return result
    
    def generate_missing_ability_entries(self, job_results: Dict) -> List[str]:
        """Generate SQL INSERT statements for missing abilities"""
        insert_statements = []
        ability_id_start = 3000  # Start from high ID to avoid conflicts
        
        for job_id, job_name in self.all_jobs.items():
            if job_name in job_results:
                result = job_results[job_name]
                missing_abilities = result.get("missing_in_db", [])
                
                for i, ability in enumerate(missing_abilities):
                    ability_id = ability_id_start + (job_id * 100) + i
                    
                    # Generate reasonable defaults
                    level = min(10 + (i * 5), 75)  # Levels 10-75
                    recast = 60 + (i * 30)  # 60-300 second recast
                    
                    insert_statement = f"""INSERT INTO `abilities` VALUES ({ability_id},'{ability}',{job_id},{level},1,{recast},0,0,0,0,2000,0,6,20.0,0,1,300,0,0,NULL);"""
                    insert_statements.append(insert_statement)
        
        return insert_statements
    
    def run_full_validation(self) -> Dict:
        """Run complete validation for all 22 jobs"""
        print("🚀 FFXI Job Database Synchronization Validation")
        print("=" * 60)
        
        job_results = {}
        complete_jobs = 0
        total_functions = 0
        total_db_abilities = 0
        
        for job_id, job_name in self.all_jobs.items():
            result = self.validate_job_completion(job_id, job_name)
            job_results[job_name] = result
            
            if result["status"] == "COMPLETE":
                complete_jobs += 1
            
            total_functions += result["lua_functions"]
            total_db_abilities += result["db_abilities"]
        
        # Generate completion summary
        summary = {
            "total_jobs": len(self.all_jobs),
            "complete_jobs": complete_jobs,
            "completion_percentage": (complete_jobs / len(self.all_jobs)) * 100,
            "total_lua_functions": total_functions,
            "total_db_abilities": total_db_abilities,
            "job_results": job_results
        }
        
        print(f"\n📊 VALIDATION SUMMARY")
        print(f"Complete Jobs: {complete_jobs}/{len(self.all_jobs)} ({summary['completion_percentage']:.1f}%)")
        print(f"Total Lua Functions: {total_functions}")
        print(f"Total DB Abilities: {total_db_abilities}")
        
        # Generate missing ability inserts
        missing_inserts = self.generate_missing_ability_entries(job_results)
        if missing_inserts:
            print(f"\n📝 Generated {len(missing_inserts)} missing ability INSERT statements")
        
        # Save results
        self.save_results(summary, missing_inserts)
        
        return summary
    
    def save_results(self, summary: Dict, missing_inserts: List[str]):
        """Save validation results and missing ability inserts"""
        # Create reports directory
        reports_dir = self.repo_root / "docs" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results
        results_file = reports_dir / "job_database_sync_validation.json"
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save missing ability inserts
        if missing_inserts:
            inserts_file = self.repo_root / "sql" / "missing_job_abilities.sql"
            with open(inserts_file, 'w') as f:
                f.write("-- Missing Job Abilities - Generated by Job Database Sync Validator\n")
                f.write("-- Add these to abilities.sql to complete job implementations\n\n")
                for insert in missing_inserts:
                    f.write(insert + "\n")
            
            print(f"💾 Missing abilities saved to: {inserts_file}")
        
        print(f"📄 Detailed results saved to: {results_file}")

def main():
    validator = JobDatabaseSyncValidator()
    validator.run_full_validation()
    print("\n✅ Job Database Synchronization Validation Complete!")

if __name__ == "__main__":
    main()