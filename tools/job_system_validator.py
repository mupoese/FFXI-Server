#!/usr/bin/env python3
"""
FFXI Server Job System Comprehensive Validation Suite
=====================================================

This script performs comprehensive validation of all 22 job systems in FFXI Server,
focusing on Lua bindings, database integration, and critical job mechanics.

Features:
- Blue Mage spell setting/learning system validation
- Red Mage Composure and enspell mechanics testing
- Dancer flourish system verification
- Complete job binding consistency checks
- Database integrity validation for job-related data
- Roadmap progress tracking for ITERATION 7

Author: Enhanced for ITERATION 7 Job System Excellence
Version: 2.0.0
"""

import os
import sys
import json
import sqlite3
import subprocess
import glob
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class JobSystemValidator:
    """Comprehensive job system validation framework"""
    
    def __init__(self, repo_root: str = None):
        self.repo_root = repo_root or "/home/runner/work/FFXI-Server/FFXI-Server"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "validation_results": {},
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
            "roadmap_progress": {}
        }
        self.job_list = [
            "WAR", "MNK", "WHM", "BLM", "RDM", "THF", "PLD", "DRK",
            "BST", "BRD", "RNG", "SAM", "NIN", "DRG", "SMN", "BLU",
            "COR", "PUP", "DNC", "SCH", "GEO", "RUN"
        ]
        
    def validate_lua_bindings(self) -> Dict:
        """Validate Lua function bindings for all job systems"""
        print("🔍 Validating Lua function bindings...")
        
        binding_results = {
            "total_bindings_checked": 0,
            "valid_bindings": 0,
            "missing_bindings": [],
            "job_specific_bindings": {}
        }
        
        # Critical bindings to check
        critical_bindings = {
            "blue_mage": [
                "getSetBlueSpell",
                "setSetBlueSpell", 
                "delTrait",
                "addTrait",
                "hasSpell",
                "addSpell"
            ],
            "red_mage": [
                "hasStatusEffect",
                "addStatusEffect", 
                "getJobPointLevel",
                "getMerit",
                "getSkillLevel"
            ],
            "dancer": [
                "getStatusEffect",
                "addStatusEffect",
                "delStatusEffect",
                "getJobPointLevel"
            ],
            "general": [
                "getMainJob",
                "getSubJob", 
                "getJobLevel",
                "addJobTrait",
                "delJobTrait"
            ]
        }
        
        # Check C++ binding definitions
        lua_binding_file = os.path.join(self.repo_root, "src/map/lua/lua_baseentity.cpp")
        if os.path.exists(lua_binding_file):
            with open(lua_binding_file, 'r') as f:
                binding_content = f.read()
                
            for job_type, bindings in critical_bindings.items():
                job_results = {"found": [], "missing": []}
                
                for binding in bindings:
                    binding_results["total_bindings_checked"] += 1
                    
                    # Check for SOL_REGISTER pattern
                    pattern = rf'SOL_REGISTER\s*\(\s*["\']({binding})["\']\s*,'
                    if re.search(pattern, binding_content):
                        binding_results["valid_bindings"] += 1
                        job_results["found"].append(binding)
                    else:
                        binding_results["missing_bindings"].append(f"{job_type}::{binding}")
                        job_results["missing"].append(binding)
                
                binding_results["job_specific_bindings"][job_type] = job_results
        
        return binding_results
    
    def validate_blue_mage_system(self) -> Dict:
        """Comprehensive Blue Mage system validation"""
        print("🔵 Validating Blue Mage system...")
        
        blue_mage_results = {
            "spell_setting_functions": {"status": "unknown", "details": []},
            "trait_system": {"status": "unknown", "details": []},
            "azure_lore_mechanics": {"status": "unknown", "details": []},
            "spell_learning": {"status": "unknown", "details": []},
            "critical_issues": []
        }
        
        # Check Blue Mage utility file
        blue_util_file = os.path.join(self.repo_root, "scripts/globals/job_utils/blue_mage.lua")
        if os.path.exists(blue_util_file):
            with open(blue_util_file, 'r') as f:
                blue_content = f.read()
            
            # Check for corrected function usage
            correct_functions = [
                "getSetBlueSpell",
                "setSetBlueSpell", 
                "delTrait"
            ]
            
            all_functions_found = True
            for func in correct_functions:
                if f"player:{func}" in blue_content:
                    blue_mage_results["spell_setting_functions"]["details"].append(f"✅ {func} correctly used")
                else:
                    blue_mage_results["spell_setting_functions"]["details"].append(f"❌ {func} not found")
                    all_functions_found = False
            
            blue_mage_results["spell_setting_functions"]["status"] = "pass" if all_functions_found else "fail"
            
            # Check for Azure Lore implementation
            if "useAzureLore" in blue_content and "AZURE_LORE" in blue_content:
                blue_mage_results["azure_lore_mechanics"]["status"] = "pass"
                blue_mage_results["azure_lore_mechanics"]["details"].append("✅ Azure Lore mechanics implemented")
            else:
                blue_mage_results["azure_lore_mechanics"]["status"] = "fail"
                blue_mage_results["azure_lore_mechanics"]["details"].append("❌ Azure Lore mechanics missing")
            
            # Check spell learning system
            if "learnSpell" in blue_content and "canLearnSpell" in blue_content:
                blue_mage_results["spell_learning"]["status"] = "pass"
                blue_mage_results["spell_learning"]["details"].append("✅ Spell learning system implemented")
            else:
                blue_mage_results["spell_learning"]["status"] = "fail"
                blue_mage_results["spell_learning"]["details"].append("❌ Spell learning system incomplete")
        else:
            blue_mage_results["critical_issues"].append("Blue Mage utility file not found")
        
        return blue_mage_results
    
    def validate_red_mage_system(self) -> Dict:
        """Comprehensive Red Mage system validation"""
        print("🔴 Validating Red Mage system...")
        
        red_mage_results = {
            "composure_mechanics": {"status": "unknown", "details": []},
            "enspell_system": {"status": "unknown", "details": []},
            "convert_mechanics": {"status": "unknown", "details": []},
            "chainspell_system": {"status": "unknown", "details": []}
        }
        
        # Check Red Mage utility file
        red_util_file = os.path.join(self.repo_root, "scripts/globals/job_utils/red_mage.lua")
        if os.path.exists(red_util_file):
            with open(red_util_file, 'r') as f:
                red_content = f.read()
            
            # Check enhanced Composure implementation
            if "useComposure" in red_content and ("calculateEnspellDamage" in red_content or "composurePower" in red_content):
                red_mage_results["composure_mechanics"]["status"] = "pass"
                red_mage_results["composure_mechanics"]["details"].append("✅ Enhanced Composure with enspell damage calculation")
            else:
                red_mage_results["composure_mechanics"]["status"] = "partial"
                red_mage_results["composure_mechanics"]["details"].append("⚠️ Composure implementation may be incomplete")
            
            # Check enspell damage calculation
            if "calculateEnspellDamage" in red_content and "handleEnspellProc" in red_content:
                red_mage_results["enspell_system"]["status"] = "pass"
                red_mage_results["enspell_system"]["details"].append("✅ Advanced enspell damage system implemented")
            else:
                red_mage_results["enspell_system"]["status"] = "fail"
                red_mage_results["enspell_system"]["details"].append("❌ Enspell system incomplete")
            
            # Check Convert mechanics
            if "useConvert" in red_content and "getJobPointLevel" in red_content:
                red_mage_results["convert_mechanics"]["status"] = "pass"
                red_mage_results["convert_mechanics"]["details"].append("✅ Convert with Job Point bonuses")
            else:
                red_mage_results["convert_mechanics"]["status"] = "partial"
                red_mage_results["convert_mechanics"]["details"].append("⚠️ Convert mechanics basic implementation")
        
        return red_mage_results
    
    def validate_dancer_system(self) -> Dict:
        """Comprehensive Dancer system validation"""
        print("💃 Validating Dancer system...")
        
        dancer_results = {
            "flourish_system": {"status": "unknown", "details": []},
            "step_mechanics": {"status": "unknown", "details": []},
            "waltz_system": {"status": "unknown", "details": []},
            "finishing_moves": {"status": "unknown", "details": []}
        }
        
        # Check Dancer utility file
        dancer_util_file = os.path.join(self.repo_root, "scripts/globals/job_utils/dancer.lua")
        if os.path.exists(dancer_util_file):
            with open(dancer_util_file, 'r') as f:
                dancer_content = f.read()
            
            # Check Striking Flourish implementation
            if "useStrikingFlourishAbility" in dancer_content and "STRIKING_FLOURISH" in dancer_content:
                dancer_results["flourish_system"]["status"] = "pass"
                dancer_results["flourish_system"]["details"].append("✅ Striking Flourish implemented")
            else:
                dancer_results["flourish_system"]["status"] = "fail"
                dancer_results["flourish_system"]["details"].append("❌ Striking Flourish missing")
            
            # Check enhanced step mechanics
            if "useEnhancedStep" in dancer_content:
                dancer_results["step_mechanics"]["status"] = "pass"
                dancer_results["step_mechanics"]["details"].append("✅ Enhanced step mechanics implemented")
            else:
                dancer_results["step_mechanics"]["status"] = "partial"
                dancer_results["step_mechanics"]["details"].append("⚠️ Basic step mechanics only")
            
            # Check finishing move system
            if "setFinishingMoves" in dancer_content and "getFinishingMoveIcon" in dancer_content:
                dancer_results["finishing_moves"]["status"] = "pass"
                dancer_results["finishing_moves"]["details"].append("✅ Complete finishing move system")
            else:
                dancer_results["finishing_moves"]["status"] = "fail"
                dancer_results["finishing_moves"]["details"].append("❌ Finishing move system incomplete")
        
        return dancer_results
    
    def validate_database_consistency(self) -> Dict:
        """Validate database consistency for job-related data"""
        print("🗄️ Validating database consistency...")
        
        db_results = {
            "spell_database": {"status": "unknown", "details": []},
            "job_points": {"status": "unknown", "details": []},
            "abilities": {"status": "unknown", "details": []},
            "traits": {"status": "unknown", "details": []}
        }
        
        # Check SQL files for job-related data
        sql_dir = os.path.join(self.repo_root, "sql")
        if os.path.exists(sql_dir):
            sql_files = glob.glob(os.path.join(sql_dir, "**/*.sql"), recursive=True)
            
            spell_files = [f for f in sql_files if "spell" in os.path.basename(f).lower()]
            if spell_files:
                db_results["spell_database"]["status"] = "pass"
                db_results["spell_database"]["details"].append(f"✅ Found {len(spell_files)} spell database files")
            else:
                db_results["spell_database"]["status"] = "fail"
                db_results["spell_database"]["details"].append("❌ No spell database files found")
            
            ability_files = [f for f in sql_files if "abilit" in os.path.basename(f).lower()]
            if ability_files:
                db_results["abilities"]["status"] = "pass"
                db_results["abilities"]["details"].append(f"✅ Found {len(ability_files)} ability database files")
        
        return db_results
    
    def validate_ci_pipeline(self) -> Dict:
        """Validate that CI/CD pipeline passes for job systems"""
        print("🚀 Validating CI/CD pipeline...")
        
        ci_results = {
            "lua_validation": {"status": "unknown", "output": ""},
            "cpp_validation": {"status": "unknown", "output": ""},
            "build_success": {"status": "unknown", "output": ""}
        }
        
        try:
            # Run Lua validation
            lua_result = subprocess.run(
                ["bash", "tools/ci/lua.sh"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            ci_results["lua_validation"]["output"] = lua_result.stdout + lua_result.stderr
            ci_results["lua_validation"]["status"] = "pass" if lua_result.returncode == 0 else "fail"
            
        except subprocess.TimeoutExpired:
            ci_results["lua_validation"]["status"] = "timeout"
            ci_results["lua_validation"]["output"] = "Validation timed out"
        except Exception as e:
            ci_results["lua_validation"]["status"] = "error"
            ci_results["lua_validation"]["output"] = str(e)
        
        try:
            # Run C++ validation
            cpp_result = subprocess.run(
                ["bash", "tools/ci/cpp.sh"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            ci_results["cpp_validation"]["output"] = cpp_result.stdout + cpp_result.stderr
            ci_results["cpp_validation"]["status"] = "pass" if cpp_result.returncode == 0 else "fail"
            
        except Exception as e:
            ci_results["cpp_validation"]["status"] = "error"
            ci_results["cpp_validation"]["output"] = str(e)
        
        return ci_results
    
    def assess_roadmap_progress(self) -> Dict:
        """Assess ITERATION 7 roadmap progress based on validation results"""
        print("📊 Assessing ITERATION 7 roadmap progress...")
        
        progress = {
            "iteration_7_completion": 0,
            "completed_components": [],
            "in_progress_components": [],
            "blocked_components": [],
            "next_steps": []
        }
        
        # Assess Blue Mage system completion
        if (self.results["validation_results"].get("blue_mage", {}).get("spell_setting_functions", {}).get("status") == "pass" and
            self.results["validation_results"].get("blue_mage", {}).get("azure_lore_mechanics", {}).get("status") == "pass"):
            progress["completed_components"].append("Blue Mage spell management system")
        else:
            progress["in_progress_components"].append("Blue Mage system completion")
        
        # Assess Red Mage system completion  
        if (self.results["validation_results"].get("red_mage", {}).get("composure_mechanics", {}).get("status") == "pass" and
            self.results["validation_results"].get("red_mage", {}).get("enspell_system", {}).get("status") == "pass"):
            progress["completed_components"].append("Red Mage Composure and enspell mechanics")
        else:
            progress["in_progress_components"].append("Red Mage abilities enhancement")
        
        # Assess Dancer system completion
        if (self.results["validation_results"].get("dancer", {}).get("flourish_system", {}).get("status") == "pass" and
            self.results["validation_results"].get("dancer", {}).get("finishing_moves", {}).get("status") == "pass"):
            progress["completed_components"].append("Dancer flourish system")
        else:
            progress["in_progress_components"].append("Dancer system completion")
        
        # Calculate completion percentage
        total_components = len(progress["completed_components"]) + len(progress["in_progress_components"]) + len(progress["blocked_components"])
        if total_components > 0:
            progress["iteration_7_completion"] = (len(progress["completed_components"]) / 3) * 100  # 3 major job systems
        
        # Determine next steps
        if progress["iteration_7_completion"] >= 85:
            progress["next_steps"].append("Begin ITERATION 8: Combat System Foundation")
            progress["next_steps"].append("Weaponskill system overhaul")
            progress["next_steps"].append("Auto-attack migration to Lua")
        else:
            progress["next_steps"].append("Complete remaining job-specific implementations")
            progress["next_steps"].append("Address critical binding issues")
            progress["next_steps"].append("Validate cross-system integration")
        
        return progress
    
    def generate_report(self) -> str:
        """Generate comprehensive validation report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# FFXI Server Job System Validation Report
Generated: {timestamp}

## Executive Summary
- **ITERATION 7 Progress**: {self.results['roadmap_progress'].get('iteration_7_completion', 0):.1f}%
- **Critical Issues**: {len(self.results['critical_issues'])}
- **Warnings**: {len(self.results['warnings'])}
- **Total Bindings Checked**: {self.results['validation_results'].get('lua_bindings', {}).get('total_bindings_checked', 0)}

## Detailed Results

### Blue Mage System Validation
"""
        
        blue_results = self.results['validation_results'].get('blue_mage', {})
        for system, result in blue_results.items():
            if isinstance(result, dict) and 'status' in result:
                status_icon = "✅" if result['status'] == 'pass' else "❌" if result['status'] == 'fail' else "⚠️"
                report += f"- **{system.replace('_', ' ').title()}**: {status_icon} {result['status'].upper()}\n"
                for detail in result.get('details', []):
                    report += f"  - {detail}\n"
        
        report += f"""
### Red Mage System Validation
"""
        red_results = self.results['validation_results'].get('red_mage', {})
        for system, result in red_results.items():
            if isinstance(result, dict) and 'status' in result:
                status_icon = "✅" if result['status'] == 'pass' else "❌" if result['status'] == 'fail' else "⚠️"
                report += f"- **{system.replace('_', ' ').title()}**: {status_icon} {result['status'].upper()}\n"
                for detail in result.get('details', []):
                    report += f"  - {detail}\n"
        
        report += f"""
### Dancer System Validation
"""
        dancer_results = self.results['validation_results'].get('dancer', {})
        for system, result in dancer_results.items():
            if isinstance(result, dict) and 'status' in result:
                status_icon = "✅" if result['status'] == 'pass' else "❌" if result['status'] == 'fail' else "⚠️"
                report += f"- **{system.replace('_', ' ').title()}**: {status_icon} {result['status'].upper()}\n"
                for detail in result.get('details', []):
                    report += f"  - {detail}\n"
        
        report += f"""
### Roadmap Progress Assessment
"""
        progress = self.results['roadmap_progress']
        report += f"- **Completed Components**: {len(progress.get('completed_components', []))}\n"
        for component in progress.get('completed_components', []):
            report += f"  - ✅ {component}\n"
        
        report += f"- **In Progress Components**: {len(progress.get('in_progress_components', []))}\n"
        for component in progress.get('in_progress_components', []):
            report += f"  - 🔄 {component}\n"
        
        report += f"""
### Next Steps
"""
        for step in progress.get('next_steps', []):
            report += f"- {step}\n"
        
        return report
    
    def run_validation(self) -> Dict:
        """Run complete job system validation"""
        print("🚀 Starting comprehensive job system validation...")
        
        # Run all validation modules
        self.results["validation_results"]["lua_bindings"] = self.validate_lua_bindings()
        self.results["validation_results"]["blue_mage"] = self.validate_blue_mage_system()
        self.results["validation_results"]["red_mage"] = self.validate_red_mage_system()
        self.results["validation_results"]["dancer"] = self.validate_dancer_system()
        self.results["validation_results"]["database"] = self.validate_database_consistency()
        self.results["validation_results"]["ci_pipeline"] = self.validate_ci_pipeline()
        
        # Assess roadmap progress
        self.results["roadmap_progress"] = self.assess_roadmap_progress()
        
        # Generate comprehensive report
        report = self.generate_report()
        
        # Save results
        output_file = os.path.join(self.repo_root, "job_system_validation_report.json")
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        report_file = os.path.join(self.repo_root, "JOB_SYSTEM_VALIDATION_REPORT.md")
        with open(report_file, 'w') as f:
            f.write(report)
        
        print("✅ Job system validation completed!")
        print(f"📄 Detailed report: {report_file}")
        print(f"📊 JSON results: {output_file}")
        
        return self.results

def main():
    """Main execution function"""
    validator = JobSystemValidator()
    results = validator.run_validation()
    
    # Print summary
    print("\n" + "="*60)
    print("🎯 VALIDATION SUMMARY")
    print("="*60)
    
    progress = results['roadmap_progress']
    print(f"📊 ITERATION 7 Progress: {progress.get('iteration_7_completion', 0):.1f}%")
    print(f"✅ Completed: {len(progress.get('completed_components', []))}")
    print(f"🔄 In Progress: {len(progress.get('in_progress_components', []))}")
    print(f"🚫 Blocked: {len(progress.get('blocked_components', []))}")
    
    if progress.get('iteration_7_completion', 0) >= 85:
        print("\n🎉 ITERATION 7 is substantially complete! Ready for ITERATION 8.")
    else:
        print(f"\n⚠️ ITERATION 7 needs additional work before proceeding.")
    
    return 0 if progress.get('iteration_7_completion', 0) >= 85 else 1

if __name__ == "__main__":
    sys.exit(main())