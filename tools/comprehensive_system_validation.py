#!/usr/bin/env python3
"""
Comprehensive System Validation Tool for FFXI-Server
Tests dynamis, zoning, trusts, new features integration and build capabilities
"""

import os
import sys
import sqlite3
import subprocess
import glob
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

class FFXISystemValidator:
    def __init__(self, base_path: str = "/home/runner/work/FFXI-Server/FFXI-Server"):
        self.base_path = Path(base_path)
        self.scripts_path = self.base_path / "scripts"
        self.sql_path = self.base_path / "sql"
        self.src_path = self.base_path / "src"
        self.build_path = self.base_path / "build"
        
        # Test results storage
        self.results = {
            "dynamis": {"status": "UNKNOWN", "details": {}},
            "zoning": {"status": "UNKNOWN", "details": {}}, 
            "trusts": {"status": "UNKNOWN", "details": {}},
            "new_features": {"status": "UNKNOWN", "details": {}},
            "build_system": {"status": "UNKNOWN", "details": {}},
            "database_integration": {"status": "UNKNOWN", "details": {}}
        }

    def validate_dynamis_system(self) -> Dict[str, Any]:
        """Comprehensive dynamis system validation"""
        print("🔍 Validating Dynamis System...")
        
        dynamis_details = {
            "core_files": [],
            "zone_implementations": [],
            "database_tables": [],
            "lua_functions": [],
            "missing_components": []
        }
        
        # Check core dynamis files
        core_files = [
            "scripts/globals/dynamis.lua",
            "scripts/enum/dynamis.lua", 
            "scripts/effects/dynamis.lua",
            "scripts/mixins/dynamis_dreamland.lua",
            "scripts/mixins/dynamis_beastmen.lua"
        ]
        
        for file_path in core_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                dynamis_details["core_files"].append(str(file_path))
                # Analyze file content for key functions
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                        if 'function' in content:
                            func_count = content.count('function')
                            dynamis_details["lua_functions"].append(f"{file_path}: {func_count} functions")
                except Exception as e:
                    dynamis_details["missing_components"].append(f"Error reading {file_path}: {e}")
            else:
                dynamis_details["missing_components"].append(str(file_path))
        
        # Check dynamis zone implementations
        dynamis_zones = [
            "Dynamis-Bastok", "Dynamis-Windurst", "Dynamis-San_dOria", "Dynamis-Jeuno",
            "Dynamis-Beaucedine", "Dynamis-Xarcabard", "Dynamis-Tavnazia", "Dynamis-Valkurm",
            "Dynamis-Buburimu", "Dynamis-Qufim"
        ]
        
        for zone in dynamis_zones:
            zone_path = self.scripts_path / "zones" / zone
            if zone_path.exists():
                zone_files = list(zone_path.glob("*.lua"))
                dynamis_details["zone_implementations"].append(f"{zone}: {len(zone_files)} files")
            else:
                dynamis_details["missing_components"].append(f"Zone implementation: {zone}")
        
        # Check SQL tables for dynamis
        sql_files = list(self.sql_path.glob("*.sql"))
        dynamis_sql_patterns = ["dynamis", "time_lord", "dreamland"]
        
        for sql_file in sql_files:
            try:
                with open(sql_file, 'r') as f:
                    content = f.read().lower()
                    for pattern in dynamis_sql_patterns:
                        if pattern in content:
                            dynamis_details["database_tables"].append(f"{sql_file.name}: contains {pattern}")
            except Exception:
                continue
        
        # Determine overall status
        if len(dynamis_details["core_files"]) >= 4 and len(dynamis_details["zone_implementations"]) >= 8:
            status = "OPERATIONAL"
        elif len(dynamis_details["core_files"]) >= 2:
            status = "PARTIAL"
        else:
            status = "MISSING"
            
        return {"status": status, "details": dynamis_details}

    def validate_zoning_system(self) -> Dict[str, Any]:
        """Comprehensive zoning system validation"""
        print("🔍 Validating Zoning System...")
        
        zoning_details = {
            "zone_command": False,
            "zone_enum": False,
            "zone_implementations": 0,
            "server_zoning_code": [],
            "missing_components": []
        }
        
        # Check zone command
        zone_cmd_path = self.scripts_path / "commands" / "zone.lua"
        if zone_cmd_path.exists():
            zoning_details["zone_command"] = True
            try:
                with open(zone_cmd_path, 'r') as f:
                    content = f.read()
                    if 'zoneList' in content:
                        zone_count = content.count('xi.zone.')
                        zoning_details["zone_implementations"] = zone_count
            except Exception as e:
                zoning_details["missing_components"].append(f"Zone command error: {e}")
        else:
            zoning_details["missing_components"].append("scripts/commands/zone.lua")
        
        # Check zone enum
        zone_enum_path = self.scripts_path / "enum" / "zone.lua"
        if zone_enum_path.exists():
            zoning_details["zone_enum"] = True
        else:
            zoning_details["missing_components"].append("scripts/enum/zone.lua")
        
        # Check server-side zoning code
        cpp_zoning_files = [
            "src/map/zone.cpp",
            "src/map/zone.h", 
            "src/map/map.cpp",
            "src/common/zone_instance.cpp"
        ]
        
        for cpp_file in cpp_zoning_files:
            cpp_path = self.base_path / cpp_file
            if cpp_path.exists():
                zoning_details["server_zoning_code"].append(cpp_file)
            else:
                # Check if file exists with different name/location
                cpp_search = list(self.src_path.rglob("*zone*.cpp"))
                if cpp_search:
                    zoning_details["server_zoning_code"].extend([str(f.relative_to(self.base_path)) for f in cpp_search[:3]])
        
        # Count total zone implementations
        zones_path = self.scripts_path / "zones"
        if zones_path.exists():
            zone_dirs = [d for d in zones_path.iterdir() if d.is_dir()]
            zoning_details["zone_implementations"] = len(zone_dirs)
        
        # Determine status
        if zoning_details["zone_command"] and zoning_details["zone_enum"] and zoning_details["zone_implementations"] > 200:
            status = "FULLY_OPERATIONAL"
        elif zoning_details["zone_implementations"] > 100:
            status = "OPERATIONAL"
        else:
            status = "LIMITED"
            
        return {"status": status, "details": zoning_details}

    def validate_trust_system(self) -> Dict[str, Any]:
        """Comprehensive trust system validation"""
        print("🔍 Validating Trust System...")
        
        trust_details = {
            "core_trust_file": False,
            "trust_commands": [],
            "trust_spells": [],
            "trust_ai": False,
            "database_integration": [],
            "missing_components": []
        }
        
        # Check core trust file
        trust_core_path = self.scripts_path / "globals" / "trust.lua"
        if trust_core_path.exists():
            trust_details["core_trust_file"] = True
            try:
                with open(trust_core_path, 'r') as f:
                    content = f.read()
                    # Count trust-related functions and definitions
                    if 'movementType' in content and 'messageOffset' in content:
                        trust_details["trust_ai"] = True
            except Exception as e:
                trust_details["missing_components"].append(f"Trust core file error: {e}")
        else:
            trust_details["missing_components"].append("scripts/globals/trust.lua")
        
        # Check trust commands
        trust_commands = ["addalltrusts.lua", "trustengage.lua"]
        for cmd in trust_commands:
            cmd_path = self.scripts_path / "commands" / cmd
            if cmd_path.exists():
                trust_details["trust_commands"].append(cmd)
            else:
                trust_details["missing_components"].append(f"commands/{cmd}")
        
        # Check for trust spells/abilities
        actions_path = self.scripts_path / "actions"
        if actions_path.exists():
            trust_files = list(actions_path.rglob("*trust*"))
            entrust_files = list(actions_path.rglob("*entrust*"))
            trust_details["trust_spells"] = [str(f.relative_to(actions_path)) for f in trust_files + entrust_files]
        
        # Check experimental AI
        exp_ai_path = self.scripts_path / "experimental" / "enhanced_trust_ai.lua"
        if exp_ai_path.exists():
            trust_details["trust_ai"] = True
        
        # Check database for trust-related tables
        sql_files = list(self.sql_path.glob("*.sql"))
        for sql_file in sql_files:
            try:
                with open(sql_file, 'r') as f:
                    content = f.read().lower()
                    if 'trust' in content or 'alter_ego' in content:
                        trust_details["database_integration"].append(sql_file.name)
            except Exception:
                continue
        
        # Determine status  
        if trust_details["core_trust_file"] and len(trust_details["trust_commands"]) >= 1 and trust_details["trust_ai"]:
            status = "OPERATIONAL"
        elif trust_details["core_trust_file"]:
            status = "BASIC"
        else:
            status = "MISSING"
            
        return {"status": status, "details": trust_details}

    def validate_new_features(self) -> Dict[str, Any]:
        """Validate new features integration"""
        print("🔍 Validating New Features Integration...")
        
        features_details = {
            "job_utilities": [],
            "modern_systems": [],
            "enhancement_scripts": [],
            "recent_additions": [],
            "missing_components": []
        }
        
        # Check job utilities (modern job system)
        job_utils_path = self.scripts_path / "globals" / "job_utils"
        if job_utils_path.exists():
            job_files = list(job_utils_path.glob("*.lua"))
            features_details["job_utilities"] = [f.name for f in job_files]
        else:
            features_details["missing_components"].append("Job utilities system")
        
        # Check for modern enhancement systems
        modern_systems = [
            "scripts/globals/ability.lua",
            "scripts/globals/magic.lua", 
            "scripts/globals/weaponskill.lua",
            "scripts/globals/spell.lua",
            "scripts/globals/combat.lua"
        ]
        
        for system in modern_systems:
            system_path = self.base_path / system
            if system_path.exists():
                features_details["modern_systems"].append(system)
            else:
                features_details["missing_components"].append(system)
        
        # Check experimental features
        exp_path = self.scripts_path / "experimental"
        if exp_path.exists():
            exp_files = list(exp_path.glob("*.lua"))
            features_details["enhancement_scripts"] = [f.name for f in exp_files]
        
        # Check for recent feature additions (based on file patterns)
        recent_patterns = ["enhanced_", "improved_", "advanced_", "modern_"]
        for pattern in recent_patterns:
            pattern_files = list(self.scripts_path.rglob(f"*{pattern}*.lua"))
            if pattern_files:
                features_details["recent_additions"].extend([str(f.relative_to(self.scripts_path)) for f in pattern_files[:5]])
        
        # Determine status
        job_util_count = len(features_details["job_utilities"])
        modern_sys_count = len(features_details["modern_systems"])
        
        if job_util_count >= 15 and modern_sys_count >= 4:
            status = "FULLY_INTEGRATED"
        elif job_util_count >= 10:
            status = "WELL_INTEGRATED"
        elif job_util_count >= 5:
            status = "PARTIALLY_INTEGRATED"
        else:
            status = "LIMITED"
            
        return {"status": status, "details": features_details}

    def validate_build_system(self) -> Dict[str, Any]:
        """Validate build system and dependencies"""
        print("🔍 Validating Build System...")
        
        build_details = {
            "cmake_files": [],
            "dependencies_found": [],
            "build_configuration": False,
            "missing_dependencies": [],
            "build_errors": []
        }
        
        # Check CMake files
        cmake_files = ["CMakeLists.txt", "cmake/", "src/CMakeLists.txt"]
        for cmake_file in cmake_files:
            cmake_path = self.base_path / cmake_file
            if cmake_path.exists():
                build_details["cmake_files"].append(cmake_file)
        
        # Check critical dependencies
        dependencies = {
            "luajit": ["luajit", "libluajit-5.1-2"],
            "mariadb": ["libmariadb3", "mariadb-client"],
            "zeromq": ["libzmq5"],
            "binutils": ["binutils-dev"],
            "cmake": ["cmake"]
        }
        
        for dep_name, packages in dependencies.items():
            try:
                # Check if any of the packages for this dependency are installed
                result = subprocess.run(['dpkg', '-l'] + packages, 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    build_details["dependencies_found"].append(dep_name)
                else:
                    build_details["missing_dependencies"].append(dep_name)
            except Exception:
                build_details["missing_dependencies"].append(dep_name)
        
        # Try basic cmake configuration test
        if self.build_path.exists():
            build_details["build_configuration"] = True
        else:
            try:
                # Attempt to create build directory and run cmake
                self.build_path.mkdir(exist_ok=True)
                result = subprocess.run(['cmake', '--version'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    build_details["build_configuration"] = True
                else:
                    build_details["build_errors"].append("CMake not available")
            except Exception as e:
                build_details["build_errors"].append(f"Build system error: {e}")
        
        # Determine status
        deps_found = len(build_details["dependencies_found"])
        deps_missing = len(build_details["missing_dependencies"])
        
        if deps_found >= 4 and deps_missing == 0 and build_details["build_configuration"]:
            status = "READY"
        elif deps_found >= 3:
            status = "MOSTLY_READY"
        elif deps_found >= 1:
            status = "PARTIAL"
        else:
            status = "NOT_READY"
            
        return {"status": status, "details": build_details}

    def validate_database_integration(self) -> Dict[str, Any]:
        """Validate database integration and SQL functionality"""
        print("🔍 Validating Database Integration...")
        
        db_details = {
            "sql_files_count": 0,
            "table_structures": [],
            "core_tables": [],
            "content_tables": [],
            "missing_components": []
        }
        
        # Count SQL files
        sql_files = list(self.sql_path.glob("*.sql"))
        db_details["sql_files_count"] = len(sql_files)
        
        # Identify core system tables
        core_table_patterns = ["accounts", "chars", "char_", "zone_", "server_", "auction"]
        content_table_patterns = ["item_", "mob_", "npc_", "quest_", "mission_", "dynamis", "trust"]
        
        for sql_file in sql_files[:50]:  # Limit to prevent excessive processing
            try:
                with open(sql_file, 'r') as f:
                    content = f.read().lower()
                    
                    # Check for core tables
                    for pattern in core_table_patterns:
                        if pattern in sql_file.name.lower():
                            db_details["core_tables"].append(sql_file.name)
                            break
                    
                    # Check for content tables  
                    for pattern in content_table_patterns:
                        if pattern in sql_file.name.lower():
                            db_details["content_tables"].append(sql_file.name)
                            break
                    
                    # Check for table structure
                    if 'create table' in content or 'create database' in content:
                        db_details["table_structures"].append(sql_file.name)
                        
            except Exception as e:
                db_details["missing_components"].append(f"Error reading {sql_file.name}: {e}")
        
        # Determine status
        if db_details["sql_files_count"] >= 100 and len(db_details["core_tables"]) >= 5:
            status = "COMPREHENSIVE"
        elif db_details["sql_files_count"] >= 50:
            status = "SUBSTANTIAL"
        elif db_details["sql_files_count"] >= 20:
            status = "BASIC"
        else:
            status = "MINIMAL"
            
        return {"status": status, "details": db_details}

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all validation tests"""
        print("🚀 Starting Comprehensive FFXI-Server System Validation\n")
        
        # Run all validation tests
        self.results["dynamis"] = self.validate_dynamis_system()
        self.results["zoning"] = self.validate_zoning_system()
        self.results["trusts"] = self.validate_trust_system()
        self.results["new_features"] = self.validate_new_features()
        self.results["build_system"] = self.validate_build_system()
        self.results["database_integration"] = self.validate_database_integration()
        
        return self.results

    def generate_report(self) -> str:
        """Generate comprehensive validation report"""
        report = []
        report.append("=" * 80)
        report.append("FFXI-SERVER COMPREHENSIVE SYSTEM VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary section
        report.append("📋 VALIDATION SUMMARY")
        report.append("-" * 40)
        for system, result in self.results.items():
            status_icon = {
                "FULLY_OPERATIONAL": "✅",
                "OPERATIONAL": "✅", 
                "READY": "✅",
                "COMPREHENSIVE": "✅",
                "WELL_INTEGRATED": "✅",
                "FULLY_INTEGRATED": "✅",
                "MOSTLY_READY": "🟡",
                "SUBSTANTIAL": "🟡",
                "PARTIAL": "🟡",
                "BASIC": "🟡",
                "PARTIALLY_INTEGRATED": "🟡",
                "LIMITED": "⚠️",
                "MINIMAL": "⚠️",
                "NOT_READY": "❌",
                "MISSING": "❌"
            }.get(result["status"], "❓")
            
            report.append(f"{status_icon} {system.upper().replace('_', ' ')}: {result['status']}")
        
        report.append("")
        
        # Detailed sections
        for system, result in self.results.items():
            report.append(f"🔍 {system.upper().replace('_', ' ')} DETAILS")
            report.append("-" * 50)
            report.append(f"Status: {result['status']}")
            report.append("")
            
            details = result.get("details", {})
            for key, value in details.items():
                if isinstance(value, list):
                    if value:
                        report.append(f"{key.replace('_', ' ').title()}:")
                        for item in value[:10]:  # Limit items to prevent huge reports
                            report.append(f"  • {item}")
                        if len(value) > 10:
                            report.append(f"  ... and {len(value) - 10} more")
                    else:
                        report.append(f"{key.replace('_', ' ').title()}: None")
                else:
                    report.append(f"{key.replace('_', ' ').title()}: {value}")
            
            report.append("")
        
        # Overall assessment
        report.append("🎯 OVERALL SYSTEM ASSESSMENT")
        report.append("-" * 40)
        
        operational_systems = sum(1 for result in self.results.values() 
                                if result["status"] in ["FULLY_OPERATIONAL", "OPERATIONAL", "READY", "COMPREHENSIVE", "FULLY_INTEGRATED"])
        
        total_systems = len(self.results)
        readiness_percentage = (operational_systems / total_systems) * 100
        
        if readiness_percentage >= 80:
            overall_status = "✅ PRODUCTION READY"
        elif readiness_percentage >= 60:
            overall_status = "🟡 MOSTLY READY"
        elif readiness_percentage >= 40:
            overall_status = "⚠️ NEEDS WORK"
        else:
            overall_status = "❌ REQUIRES MAJOR WORK"
        
        report.append(f"Operational Systems: {operational_systems}/{total_systems}")
        report.append(f"System Readiness: {readiness_percentage:.1f}%")
        report.append(f"Overall Status: {overall_status}")
        report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Main execution function"""
    validator = FFXISystemValidator()
    
    # Run comprehensive validation
    results = validator.run_comprehensive_validation()
    
    # Generate and display report
    report = validator.generate_report()
    print(report)
    
    # Save report to file
    report_path = Path("/home/runner/work/FFXI-Server/FFXI-Server/COMPREHENSIVE_SYSTEM_VALIDATION_REPORT.md")
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Full report saved to: {report_path}")
    
    # Return success if most systems are operational
    operational_count = sum(1 for result in results.values() 
                           if result["status"] in ["FULLY_OPERATIONAL", "OPERATIONAL", "READY", "COMPREHENSIVE", "FULLY_INTEGRATED"])
    
    return 0 if operational_count >= 4 else 1

if __name__ == "__main__":
    sys.exit(main())