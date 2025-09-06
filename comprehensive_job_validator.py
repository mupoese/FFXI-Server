#!/usr/bin/env python3
"""
Comprehensive Job System Validator
Validates all 21 jobs requested by the user for Lua bindings and database functionality
"""

import os
import re
import json
import sqlite3
import subprocess
from pathlib import Path

class ComprehensiveJobValidator:
    def __init__(self, base_path="/home/runner/work/FFXI-Server/FFXI-Server"):
        self.base_path = Path(base_path)
        self.results = {}
        
        # Jobs to validate as requested by user
        self.jobs_to_check = [
            'warrior', 'monk', 'white_mage', 'black_mage', 'red_mage', 'thief',
            'paladin', 'dark_knight', 'beastmaster', 'bard', 'ranger', 'samurai',
            'ninja', 'dragoon', 'blue_mage', 'puppetmaster', 'corsair', 'dancer', 
            'scholar', 'geomancer', 'rune_fencer'
        ]
        
        # Job ID mapping from enum/job.lua
        self.job_ids = {
            'warrior': 1, 'monk': 2, 'white_mage': 3, 'black_mage': 4, 'red_mage': 5,
            'thief': 6, 'paladin': 7, 'dark_knight': 8, 'beastmaster': 9, 'bard': 10,
            'ranger': 11, 'samurai': 12, 'ninja': 13, 'dragoon': 14, 'summoner': 15,
            'blue_mage': 16, 'corsair': 17, 'puppetmaster': 18, 'dancer': 19,
            'scholar': 20, 'geomancer': 21, 'rune_fencer': 22
        }

    def validate_job_utils_files(self):
        """Check if job utility files exist and analyze their content"""
        job_utils_path = self.base_path / "scripts/globals/job_utils"
        
        for job in self.jobs_to_check:
            job_file = job_utils_path / f"{job}.lua"
            job_result = {
                'file_exists': job_file.exists(),
                'file_size': 0,
                'lines': 0,
                'functions': [],
                'lua_bindings': [],
                'abilities': [],
                'spells': [],
                'issues': []
            }
            
            if job_file.exists():
                try:
                    content = job_file.read_text()
                    job_result['file_size'] = len(content)
                    job_result['lines'] = len(content.split('\n'))
                    
                    # Find functions (both standard and job_utils patterns)
                    functions = re.findall(r'function\s+([^(]+)', content)
                    job_utils_functions = re.findall(r'xi\.job_utils\.\w+\.(\w+)\s*=\s*function', content)
                    all_functions = functions + job_utils_functions
                    job_result['functions'] = all_functions
                    
                    # Find Lua bindings
                    bindings = re.findall(r'xi\.job_utils\.([^.]+)\.(\w+)', content)
                    job_result['lua_bindings'] = list(set([f"{b[0]}.{b[1]}" for b in bindings]))
                    
                    # Find abilities
                    abilities = re.findall(r'xi\.jobAbility\.(\w+)', content)
                    job_result['abilities'] = list(set(abilities))
                    
                    # Find spells
                    spells = re.findall(r'xi\.magic\.spell\.(\w+)', content)
                    job_result['spells'] = list(set(spells))
                    
                except Exception as e:
                    job_result['issues'].append(f"Error reading file: {e}")
            else:
                job_result['issues'].append("Job utility file missing")
            
            self.results[job] = job_result

    def validate_database_integration(self):
        """Check database integration for jobs"""
        # Check SQL files for job-related tables
        sql_path = self.base_path / "sql"
        
        job_related_tables = []
        if sql_path.exists():
            for sql_file in sql_path.rglob("*.sql"):
                try:
                    content = sql_file.read_text()
                    if any(job in content.lower() for job in ['job', 'ability', 'spell', 'trait']):
                        job_related_tables.append(str(sql_file.relative_to(self.base_path)))
                except:
                    continue
        
        # Add database info to results
        for job in self.jobs_to_check:
            if job in self.results:
                self.results[job]['database_tables'] = job_related_tables
                self.results[job]['job_id'] = self.job_ids.get(job, 'Unknown')

    def validate_lua_scripts_integration(self):
        """Check for job-related Lua scripts throughout the codebase"""
        scripts_path = self.base_path / "scripts"
        
        for job in self.jobs_to_check:
            job_scripts = []
            if scripts_path.exists():
                # Search for job-specific scripts
                for lua_file in scripts_path.rglob("*.lua"):
                    try:
                        content = lua_file.read_text()
                        job_patterns = [
                            f"xi.job.{job.upper()[:3]}",  # Job enum
                            f"job_utils.{job}",  # Job utils
                            f"checkJob({self.job_ids.get(job, 0)})",  # Job checks
                            job.replace('_', '').upper()  # Job name variations
                        ]
                        
                        if any(pattern in content for pattern in job_patterns):
                            job_scripts.append(str(lua_file.relative_to(self.base_path)))
                    except:
                        continue
            
            if job in self.results:
                self.results[job]['related_scripts'] = job_scripts[:10]  # Limit to first 10
                self.results[job]['script_count'] = len(job_scripts)

    def validate_job_abilities(self):
        """Validate job abilities and their implementations"""
        abilities_path = self.base_path / "scripts/actions/abilities"
        
        for job in self.jobs_to_check:
            job_abilities = []
            if abilities_path.exists():
                for ability_file in abilities_path.rglob("*.lua"):
                    try:
                        content = ability_file.read_text()
                        # Check if ability is job-specific
                        if f"xi.job.{job.upper()[:3]}" in content or job.replace('_', '') in str(ability_file).lower():
                            job_abilities.append(str(ability_file.relative_to(self.base_path)))
                    except:
                        continue
            
            if job in self.results:
                self.results[job]['job_abilities'] = job_abilities
                self.results[job]['ability_count'] = len(job_abilities)

    def check_missing_jobs(self):
        """Create missing job utility files"""
        missing_jobs = []
        for job in self.jobs_to_check:
            if job in self.results and not self.results[job]['file_exists']:
                missing_jobs.append(job)
        
        return missing_jobs

    def generate_report(self):
        """Generate comprehensive validation report"""
        print("🔍 COMPREHENSIVE JOB SYSTEM VALIDATION")
        print("=" * 60)
        
        total_jobs = len(self.jobs_to_check)
        working_jobs = 0
        
        for job in self.jobs_to_check:
            if job in self.results:
                result = self.results[job]
                status = "✅" if result['file_exists'] and len(result['functions']) > 0 else "❌"
                if result['file_exists'] and len(result['functions']) > 0:
                    working_jobs += 1
                
                print(f"\n{status} {job.upper().replace('_', ' ')}")
                print(f"   File: {'EXISTS' if result['file_exists'] else 'MISSING'}")
                print(f"   Size: {result['file_size']} bytes ({result['lines']} lines)")
                print(f"   Functions: {len(result['functions'])}")
                print(f"   Lua Bindings: {len(result['lua_bindings'])}")
                print(f"   Related Scripts: {result.get('script_count', 0)}")
                print(f"   Job Abilities: {result.get('ability_count', 0)}")
                print(f"   Job ID: {result.get('job_id', 'Unknown')}")
                
                if result['issues']:
                    print(f"   Issues: {', '.join(result['issues'])}")
        
        print(f"\n📊 SUMMARY")
        print(f"   Total Jobs Requested: {total_jobs}")
        print(f"   Working Jobs: {working_jobs}")
        print(f"   Success Rate: {(working_jobs/total_jobs)*100:.1f}%")
        
        missing_jobs = self.check_missing_jobs()
        if missing_jobs:
            print(f"\n❌ MISSING JOB FILES:")
            for job in missing_jobs:
                print(f"   - {job}")
        
        return {
            'total_jobs': total_jobs,
            'working_jobs': working_jobs,
            'success_rate': (working_jobs/total_jobs)*100,
            'missing_jobs': missing_jobs,
            'detailed_results': self.results
        }

    def save_report(self, filename="comprehensive_job_validation_report.json"):
        """Save detailed report to JSON file"""
        report_data = {
            'validation_summary': {
                'total_jobs': len(self.jobs_to_check),
                'working_jobs': sum(1 for job in self.jobs_to_check 
                                  if job in self.results and self.results[job]['file_exists']),
                'missing_jobs': self.check_missing_jobs()
            },
            'detailed_results': self.results,
            'validation_timestamp': subprocess.check_output(['date'], text=True).strip()
        }
        
        with open(self.base_path / filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {filename}")

def main():
    print("Starting Comprehensive Job System Validation...")
    
    validator = ComprehensiveJobValidator()
    
    # Run all validation checks
    validator.validate_job_utils_files()
    validator.validate_database_integration()
    validator.validate_lua_scripts_integration()
    validator.validate_job_abilities()
    
    # Generate and save report
    validator.generate_report()
    validator.save_report()
    
    print("\n✅ Comprehensive Job Validation Complete!")

if __name__ == "__main__":
    main()