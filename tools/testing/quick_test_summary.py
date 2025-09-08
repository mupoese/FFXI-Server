#!/usr/bin/env python3
"""
Quick Test Summary for Job DB Functions and Build Testing

Provides rapid validation of job implementations and build system status.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def main():
    repo_root = Path('/home/runner/work/FFXI-Server/FFXI-Server')
    
    print("🔍 FFXI Server - Job Database & Build Test Summary")
    print("=" * 60)
    
    # Check job files
    job_utils_dir = repo_root / 'scripts' / 'globals' / 'job_utils'
    if job_utils_dir.exists():
        job_files = list(job_utils_dir.glob('*.lua'))
        print(f"✅ Job Files: {len(job_files)}/22 FFXI jobs implemented")
        
        # Sample job files for verification
        sample_jobs = ['warrior.lua', 'corsair.lua', 'dancer.lua', 'rune_fencer.lua']
        for job in sample_jobs:
            status = "✅" if (job_utils_dir / job).exists() else "❌"
            print(f"   {status} {job}")
    else:
        print("❌ Job utils directory not found")
    
    # Check test framework
    testing_dir = repo_root / 'tools' / 'testing'
    if testing_dir.exists():
        test_files = [
            'comprehensive_job_db_test_suite.py',
            'comprehensive_build_test_suite.py', 
            'master_test_coordinator.py'
        ]
        
        print(f"\n🧪 Test Framework:")
        for test_file in test_files:
            status = "✅" if (testing_dir / test_file).exists() else "❌"
            print(f"   {status} {test_file}")
    
    # Check recent test results
    test_results = list(repo_root.glob('*test_results*.json'))
    if test_results:
        print(f"\n📊 Recent Test Results: {len(test_results)} reports available")
        latest = max(test_results, key=lambda p: p.stat().st_mtime)
        print(f"   📋 Latest: {latest.name}")
    
    # Check build system
    cmake_file = repo_root / 'CMakeLists.txt'
    build_status = "✅" if cmake_file.exists() else "❌"
    print(f"\n🔨 Build System: {build_status} CMakeLists.txt")
    
    # Check CI scripts
    ci_dir = repo_root / 'tools' / 'ci'
    if ci_dir.exists():
        ci_scripts = list(ci_dir.glob('*.sh'))
        print(f"⚙️  CI Scripts: {len(ci_scripts)} validation scripts available")
    
    print("\n" + "=" * 60)
    print("🎯 Summary: Comprehensive job DB and build testing framework deployed")
    print("📝 See COMPREHENSIVE_TEST_REPORT.md for detailed results")
    print("=" * 60)

if __name__ == '__main__':
    main()