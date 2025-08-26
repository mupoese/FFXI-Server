#!/usr/bin/env python3
"""
Log Management System for LandSandBoat Server
Manages development logs, file structure tracking, and automated maintenance
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import sys

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
LOGS_DIR = PROJECT_ROOT / "logs" / "development"

def ensure_logs_directory():
    """Ensure the logs directory structure exists"""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

def calculate_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    try:
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()[:8]  # First 8 characters
    except Exception:
        return "unknown"

def log_file_operation(action, filepath, description=""):
    """Log file operations to the file structure log"""
    ensure_logs_directory()
    
    timestamp = datetime.now().isoformat() + 'Z'
    relative_path = str(Path(filepath).relative_to(PROJECT_ROOT))
    
    log_entry = f"[{timestamp}] {action} {relative_path} \"{description}\"\n"
    
    structure_log = LOGS_DIR / "file_structure.log"
    with open(structure_log, 'a') as f:
        f.write(log_entry)

def log_change(action, filepath, description=""):
    """Log changes to the changelog"""
    ensure_logs_directory()
    
    timestamp = datetime.now().isoformat() + 'Z'
    file_hash = calculate_file_hash(filepath) if Path(filepath).exists() else "none"
    relative_path = str(Path(filepath).relative_to(PROJECT_ROOT))
    
    log_entry = f"[{timestamp}] [{file_hash}] {action} {relative_path} \"{description}\"\n"
    
    changelog = LOGS_DIR / "changelog.log"
    with open(changelog, 'a') as f:
        f.write(log_entry)

def log_changelog_entry(component, description, pr_number="", contributors=""):
    """Log a changelog-ready entry for future integration"""
    ensure_logs_directory()
    
    timestamp = datetime.now().isoformat() + 'Z'
    entry_hash = hashlib.md5(f"{timestamp}{component}{description}".encode()).hexdigest()[:8]
    
    log_entry = f"[{timestamp}] [{entry_hash}] CHANGELOG [{component}] {description}"
    if pr_number:
        log_entry += f" PR#{pr_number}"
    if contributors:
        log_entry += f" ({contributors})"
    log_entry += "\n"
    
    changelog_entries = LOGS_DIR / "changelog_entries.log"
    with open(changelog_entries, 'a') as f:
        f.write(log_entry)

def log_prompt_logic(phase, description, improvements=""):
    """Log SWE agent thinking process"""
    ensure_logs_directory()
    
    timestamp = datetime.now().isoformat() + 'Z'
    prompt_hash = hashlib.md5(f"{timestamp}{phase}{description}".encode()).hexdigest()[:8]
    
    log_entry = f"[{timestamp}] [{prompt_hash}] {phase} \"{description}\""
    if improvements:
        log_entry += f" IMPROVEMENTS: \"{improvements}\""
    log_entry += "\n"
    
    promptlog = LOGS_DIR / "promptlog.log"
    with open(promptlog, 'a') as f:
        f.write(log_entry)

def update_package_status(package_name, version, status, location, notes=""):
    """Update package status in packages log"""
    ensure_logs_directory()
    
    timestamp = datetime.now().isoformat() + 'Z'
    log_entry = f"[{timestamp}] {package_name} {version} {status} {location} \"{notes}\"\n"
    
    packages_log = LOGS_DIR / "packageslog.log"
    with open(packages_log, 'a') as f:
        f.write(log_entry)

def update_dependency_status(dependency_name, version, status, location, notes=""):
    """Update dependency status in dependencies log"""
    ensure_logs_directory()
    
    timestamp = datetime.now().isoformat() + 'Z'
    log_entry = f"[{timestamp}] {dependency_name} {version} {status} {location} \"{notes}\"\n"
    
    dependencies_log = LOGS_DIR / "dependencieslog.log"
    with open(dependencies_log, 'a') as f:
        f.write(log_entry)

def scan_project_files():
    """Scan project for new or modified files"""
    print("🔍 Scanning project files...")
    
    # Directories to scan
    scan_dirs = ["src", "scripts", "tools", "cmake", "documentation", ".github"]
    file_count = 0
    new_files = []
    
    for scan_dir in scan_dirs:
        dir_path = PROJECT_ROOT / scan_dir
        if not dir_path.exists():
            continue
            
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                file_count += 1
                
                # Check if file is already logged
                relative_path = str(file_path.relative_to(PROJECT_ROOT))
                
                # Simple check - could be more sophisticated
                structure_log = LOGS_DIR / "file_structure.log"
                if structure_log.exists():
                    with open(structure_log, 'r') as f:
                        log_content = f.read()
                        if relative_path not in log_content:
                            new_files.append(file_path)
                else:
                    new_files.append(file_path)
    
    print(f"  📁 Scanned {file_count} files across {len(scan_dirs)} directories")
    print(f"  📄 Found {len(new_files)} new files to log")
    
    # Log new files
    for file_path in new_files[:10]:  # Limit to first 10 to avoid spam
        file_size = file_path.stat().st_size
        log_file_operation("DISCOVERED", file_path, f"File size: {file_size} bytes")
    
    if len(new_files) > 10:
        print(f"  ⚠ Limited logging to first 10 files ({len(new_files)} total)")

def cleanup_old_logs():
    """Archive old log entries to prevent bloat"""
    print("🧹 Cleaning up old log entries...")
    
    cutoff_date = datetime.now() - timedelta(days=90)  # Archive entries older than 90 days
    
    for log_file in LOGS_DIR.glob("*.log"):
        if not log_file.exists():
            continue
            
        lines_kept = 0
        lines_archived = 0
        temp_content = []
        
        with open(log_file, 'r') as f:
            for line in f:
                # Extract timestamp from log entry
                if line.startswith('[') and ']' in line:
                    try:
                        timestamp_str = line[1:line.index(']')]
                        if timestamp_str.endswith('Z'):
                            timestamp_str = timestamp_str[:-1]
                        entry_date = datetime.fromisoformat(timestamp_str)
                        
                        if entry_date > cutoff_date:
                            temp_content.append(line)
                            lines_kept += 1
                        else:
                            lines_archived += 1
                    except (ValueError, IndexError):
                        # Keep lines with invalid timestamps
                        temp_content.append(line)
                        lines_kept += 1
                else:
                    # Keep non-timestamp lines (headers, etc.)
                    temp_content.append(line)
                    lines_kept += 1
        
        if lines_archived > 0:
            # Write back the cleaned content
            with open(log_file, 'w') as f:
                f.writelines(temp_content)
            
            print(f"  📋 {log_file.name}: Kept {lines_kept} entries, archived {lines_archived}")

def generate_summary_report():
    """Generate a summary report of recent activity"""
    print("📊 Generating summary report...")
    
    report_file = LOGS_DIR / f"summary_report_{datetime.now().strftime('%Y%m%d')}.md"
    
    with open(report_file, 'w') as f:
        f.write(f"# Development Summary Report\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        
        # Analyze each log file
        for log_file in LOGS_DIR.glob("*.log"):
            if not log_file.exists():
                continue
                
            f.write(f"## {log_file.stem.title()}\n\n")
            
            # Count recent entries (last 7 days)
            recent_count = 0
            with open(log_file, 'r') as log_f:
                for line in log_f:
                    if line.startswith('['):
                        try:
                            timestamp_str = line[1:line.index(']')]
                            if timestamp_str.endswith('Z'):
                                timestamp_str = timestamp_str[:-1]
                            entry_date = datetime.fromisoformat(timestamp_str)
                            
                            if entry_date > datetime.now() - timedelta(days=7):
                                recent_count += 1
                        except (ValueError, IndexError):
                            pass
            
            f.write(f"- Recent entries (last 7 days): {recent_count}\n")
            f.write(f"- Log file size: {log_file.stat().st_size} bytes\n\n")
    
    print(f"  📄 Report saved to: {report_file}")

def validate_log_integrity():
    """Validate the integrity of log files"""
    print("🔍 Validating log file integrity...")
    
    issues_found = 0
    
    for log_file in LOGS_DIR.glob("*.log"):
        if not log_file.exists():
            continue
            
        try:
            with open(log_file, 'r') as f:
                line_count = 0
                for line_num, line in enumerate(f, 1):
                    line_count += 1
                    
                    # Basic validation: check timestamp format
                    if line.strip() and line.startswith('['):
                        if ']' not in line:
                            print(f"  ❌ {log_file.name}:{line_num} Invalid timestamp format")
                            issues_found += 1
                
                print(f"  ✓ {log_file.name}: {line_count} lines validated")
                
        except Exception as e:
            print(f"  ❌ {log_file.name}: Error reading file - {e}")
            issues_found += 1
    
    if issues_found == 0:
        print("  ✅ All log files passed integrity check")
    else:
        print(f"  ⚠ Found {issues_found} integrity issues")

def main():
    """Main log management function"""
    parser = argparse.ArgumentParser(description="LandSandBoat Log Management System")
    parser.add_argument('--scan', action='store_true', help='Scan for new project files')
    parser.add_argument('--cleanup', action='store_true', help='Archive old log entries')
    parser.add_argument('--report', action='store_true', help='Generate summary report')
    parser.add_argument('--validate', action='store_true', help='Validate log integrity')
    parser.add_argument('--all', action='store_true', help='Run all maintenance tasks')
    
    # Commands for manual logging
    parser.add_argument('--log-file', help='Log a file operation')
    parser.add_argument('--action', help='Action type for file operation')
    parser.add_argument('--description', help='Description for log entry')
    parser.add_argument('--log-changelog', help='Log a changelog entry')
    parser.add_argument('--component', help='Component tag for changelog entry')
    parser.add_argument('--pr-number', help='PR number for changelog entry')
    parser.add_argument('--contributors', help='Contributors for changelog entry')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    ensure_logs_directory()
    
    print("🚀 LandSandBoat Log Management System")
    print("=" * 50)
    
    if args.log_changelog and args.component:
        log_changelog_entry(args.component, args.log_changelog, 
                          args.pr_number or "", args.contributors or "")
        print(f"✅ Logged changelog entry: [{args.component}] {args.log_changelog}")
        return
    
    if args.log_file and args.action:
        log_file_operation(args.action, args.log_file, args.description or "")
        log_change(args.action, args.log_file, args.description or "")
        print(f"✅ Logged {args.action} for {args.log_file}")
        return
    
    if args.scan or args.all:
        scan_project_files()
    
    if args.cleanup or args.all:
        cleanup_old_logs()
    
    if args.report or args.all:
        generate_summary_report()
    
    if args.validate or args.all:
        validate_log_integrity()
    
    print("\n✅ Log management tasks completed")

if __name__ == "__main__":
    main()