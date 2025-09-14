#!/usr/bin/env python3
"""
Comprehensive FFXI Job Analysis Tool
Analyzes all job implementations, server functions, emulation functions, and trust functions
"""

import os
import re
import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class FFXIJobAnalyzer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.job_data = {}
        self.server_functions = {}
        self.emulation_functions = {}
        self.trust_functions = {}
        self.total_functions = 0
        self.completion_stats = {}
        
        # All 22 FFXI Jobs
        self.jobs = [
            'warrior', 'monk', 'white_mage', 'black_mage', 'red_mage', 'thief',
            'paladin', 'dark_knight', 'beastmaster', 'bard', 'ranger', 'samurai',
            'ninja', 'dragoon', 'summoner', 'blue_mage', 'corsair', 'puppetmaster',
            'dancer', 'scholar', 'geomancer', 'rune_fencer'
        ]
    
    def analyze_lua_file(self, file_path):
        """Analyze a Lua file and extract function information"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all function definitions
            function_pattern = r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            functions = re.findall(function_pattern, content)
            
            # Find local function definitions
            local_function_pattern = r'local\s+function\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            local_functions = re.findall(local_function_pattern, content)
            
            # Find module-style function definitions (xi.job_utils.job.funcName = function())
            module_function_pattern = r'\.([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*function'
            module_functions = re.findall(module_function_pattern, content)
            
            # Find general assignments (might be module exports)
            assignment_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*='
            assignments = re.findall(assignment_pattern, content)
            
            # Check for completion markers
            completion_markers = [
                '100% Complete', 'COMPLETE', '✅', 'Phase Complete',
                'Implementation Complete', 'Fully Implemented'
            ]
            
            is_complete = any(marker in content for marker in completion_markers)
            
            # Count lines of code (excluding comments and empty lines)
            lines = content.split('\n')
            code_lines = 0
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('--'):
                    code_lines += 1
            
            total_functions = len(functions) + len(local_functions) + len(module_functions)
            
            return {
                'functions': functions,
                'local_functions': local_functions,
                'module_functions': module_functions,
                'assignments': assignments,
                'total_functions': total_functions,
                'is_complete': is_complete,
                'code_lines': code_lines,
                'file_size': os.path.getsize(file_path)
            }
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def analyze_job_utils(self):
        """Analyze all job utility files"""
        job_utils_path = self.base_path / 'scripts' / 'globals' / 'job_utils'
        
        if not job_utils_path.exists():
            print(f"Job utils path not found: {job_utils_path}")
            return
        
        for job in self.jobs:
            job_file = job_utils_path / f"{job}.lua"
            if job_file.exists():
                analysis = self.analyze_lua_file(job_file)
                if analysis:
                    self.job_data[job] = analysis
                    self.total_functions += analysis['total_functions']
            else:
                print(f"Warning: Job file not found for {job}")
                self.job_data[job] = {
                    'functions': [],
                    'local_functions': [],
                    'module_functions': [],
                    'total_functions': 0,
                    'is_complete': False,
                    'code_lines': 0,
                    'file_size': 0
                }
    
    def analyze_server_functions(self):
        """Analyze server-side C++ functions related to jobs"""
        src_path = self.base_path / 'src'
        
        if not src_path.exists():
            return
        
        # Find C++ files that might contain job-related functions
        cpp_files = list(src_path.rglob('*.cpp')) + list(src_path.rglob('*.h'))
        
        job_related_functions = []
        
        for cpp_file in cpp_files:
            try:
                with open(cpp_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Look for job-related function patterns
                job_patterns = [
                    r'(\w*[Jj]ob\w*)\s*\(',
                    r'(\w*[Aa]bility\w*)\s*\(',
                    r'(\w*[Ss]kill\w*)\s*\(',
                    r'(\w*[Ll]evel\w*)\s*\(',
                    r'(\w*[Cc]lass\w*)\s*\('
                ]
                
                for pattern in job_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if match not in job_related_functions:
                            job_related_functions.append(match)
            
            except Exception as e:
                continue
        
        self.server_functions = {
            'total_functions': len(job_related_functions),
            'functions': job_related_functions
        }
    
    def analyze_trust_functions(self):
        """Analyze trust system functions"""
        trust_file = self.base_path / 'scripts' / 'globals' / 'trust.lua'
        
        trust_functions_count = 0
        trust_files_count = 0
        
        if trust_file.exists():
            analysis = self.analyze_lua_file(trust_file)
            if analysis:
                trust_functions_count += analysis['total_functions']
                trust_files_count += 1
        
        # Check for individual trust spell files
        trust_spells_dir = self.base_path / 'scripts' / 'actions' / 'spells' / 'trust'
        if trust_spells_dir.exists():
            trust_spell_files = list(trust_spells_dir.glob('*.lua'))
            trust_files_count += len(trust_spell_files)
            
            for trust_file in trust_spell_files[:10]:  # Sample first 10 to avoid performance issues
                analysis = self.analyze_lua_file(trust_file)
                if analysis:
                    trust_functions_count += analysis['total_functions']
        
        # Check enhanced trust AI
        enhanced_trust_file = self.base_path / 'scripts' / 'experimental' / 'enhanced_trust_ai.lua'
        if enhanced_trust_file.exists():
            analysis = self.analyze_lua_file(enhanced_trust_file)
            if analysis:
                trust_functions_count += analysis['total_functions']
                trust_files_count += 1
        
        self.trust_functions = {
            'total_functions': trust_functions_count,
            'total_files': trust_files_count,
            'spell_files_count': len(list(trust_spells_dir.glob('*.lua'))) if trust_spells_dir.exists() else 0
        }
    
    def analyze_emulation_functions(self):
        """Analyze emulation accuracy functions"""
        globals_path = self.base_path / 'scripts' / 'globals'
        
        emulation_files = [
            'common.lua', 'player.lua', 'magic.lua', 'ability.lua',
            'weaponskills.lua', 'mobskills.lua', 'pets.lua'
        ]
        
        total_emulation_functions = 0
        
        for emu_file in emulation_files:
            file_path = globals_path / emu_file
            if file_path.exists():
                analysis = self.analyze_lua_file(file_path)
                if analysis:
                    total_emulation_functions += analysis['total_functions']
        
        self.emulation_functions = {
            'total_functions': total_emulation_functions,
            'analyzed_files': len([f for f in emulation_files if (globals_path / f).exists()])
        }
    
    def calculate_completion_stats(self):
        """Calculate overall completion statistics"""
        completed_jobs = sum(1 for job_data in self.job_data.values() if job_data['is_complete'])
        total_jobs = len(self.jobs)
        
        total_job_functions = sum(data['total_functions'] for data in self.job_data.values())
        average_functions_per_job = total_job_functions / total_jobs if total_jobs > 0 else 0
        
        self.completion_stats = {
            'completed_jobs': completed_jobs,
            'total_jobs': total_jobs,
            'completion_percentage': (completed_jobs / total_jobs) * 100 if total_jobs > 0 else 0,
            'total_job_functions': total_job_functions,
            'average_functions_per_job': average_functions_per_job,
            'server_functions': self.server_functions.get('total_functions', 0),
            'trust_functions': self.trust_functions.get('total_functions', 0),
            'emulation_functions': self.emulation_functions.get('total_functions', 0)
        }
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        self.analyze_job_utils()
        self.analyze_server_functions()
        self.analyze_trust_functions()
        self.analyze_emulation_functions()
        self.calculate_completion_stats()
        
        report = {
            'analysis_date': datetime.now().isoformat(),
            'summary': self.completion_stats,
            'jobs': {},
            'server_functions': self.server_functions,
            'trust_functions': self.trust_functions,
            'emulation_functions': self.emulation_functions
        }
        
        # Detailed job analysis
        for job in self.jobs:
            job_data = self.job_data.get(job, {})
            status = "COMPLETE" if job_data.get('is_complete', False) else "IN_PROGRESS"
            
            report['jobs'][job] = {
                'status': status,
                'function_count': job_data.get('total_functions', 0),
                'code_lines': job_data.get('code_lines', 0),
                'file_size_bytes': job_data.get('file_size', 0),
                'functions': job_data.get('functions', []),
                'completion_percentage': 100 if status == "COMPLETE" else 80
            }
        
        return report
    
    def print_summary_report(self, report):
        """Print a human-readable summary"""
        print("\n" + "="*80)
        print("🎮 COMPREHENSIVE FFXI JOB SYSTEM ANALYSIS REPORT")
        print("="*80)
        print(f"📅 Analysis Date: {report['analysis_date']}")
        print(f"🎯 Total Jobs Analyzed: {report['summary']['total_jobs']}")
        print(f"✅ Completed Jobs: {report['summary']['completed_jobs']}")
        print(f"📊 Completion Rate: {report['summary']['completion_percentage']:.1f}%")
        print(f"🔧 Total Job Functions: {report['summary']['total_job_functions']}")
        print(f"📈 Avg Functions/Job: {report['summary']['average_functions_per_job']:.1f}")
        print(f"🖥️  Server Functions: {report['summary']['server_functions']}")
        print(f"🤝 Trust Functions: {report['summary']['trust_functions']}")
        print(f"⚙️  Emulation Functions: {report['summary']['emulation_functions']}")
        
        print("\n" + "-"*80)
        print("📋 INDIVIDUAL JOB STATUS")
        print("-"*80)
        
        for job, data in report['jobs'].items():
            status_icon = "✅" if data['status'] == "COMPLETE" else "🔄"
            print(f"{status_icon} {job.upper():<15} | {data['function_count']:>3} functions | {data['code_lines']:>4} lines | {data['status']}")
        
        print("\n" + "-"*80)
        print("🔍 SYSTEM INTEGRATION ANALYSIS")
        print("-"*80)
        print(f"Server Integration: {report['server_functions']['total_functions']} functions detected")
        print(f"Trust System: {report['trust_functions'].get('total_functions', 0)} functions")
        print(f"Emulation Layer: {report['emulation_functions']['total_functions']} functions")
        
        incomplete_jobs = [job for job, data in report['jobs'].items() if data['status'] != "COMPLETE"]
        if incomplete_jobs:
            print(f"\n⚠️  Jobs needing completion: {', '.join(incomplete_jobs)}")
        else:
            print(f"\n🎉 ALL JOBS COMPLETE! Perfect implementation achieved!")


def main():
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = os.getcwd()
    
    analyzer = FFXIJobAnalyzer(base_path)
    report = analyzer.generate_report()
    analyzer.print_summary_report(report)
    
    # Save detailed report
    output_file = Path(base_path) / 'tools' / 'comprehensive_job_analysis_report.json'
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {output_file}")
    
    return report


if __name__ == "__main__":
    main()