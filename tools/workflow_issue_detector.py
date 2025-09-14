#!/usr/bin/env python3
"""
Workflow Issue Detector and Auto-Fixer

This tool scans all workflow files for common issues and provides automated fixes:
1. Missing Python setup-python@v4 actions
2. Inconsistent Python version enforcement (non-3.12)
3. Package dependency issues (zmq vs pyzmq)
4. Missing system dependencies
5. Workflow syntax issues
6. Configuration conflicts
"""

import os
import sys
import yaml
import json
import re
from pathlib import Path
import argparse
from typing import Dict, List, Any, Tuple, Optional

class WorkflowIssueDetector:
    def __init__(self, repository_path: str, fix_mode: bool = False):
        self.repo_path = Path(repository_path)
        self.workflow_path = self.repo_path / ".github" / "workflows"
        self.fix_mode = fix_mode
        self.issues_found = []
        self.fixes_applied = []
        
    def scan_all_workflows(self) -> Dict[str, Any]:
        """Scan all workflow files for issues."""
        print("🔍 Scanning all workflow files for issues...")
        
        results = {
            'total_workflows': 0,
            'workflows_with_issues': 0,
            'total_issues': 0,
            'issues_by_type': {},
            'workflow_details': {}
        }
        
        # Discover all workflow files
        workflow_files = []
        for pattern in ["*.yml", "*.yaml"]:
            workflow_files.extend(self.workflow_path.glob(pattern))
            # Include manual workflows
            manual_path = self.workflow_path / "manual"
            if manual_path.exists():
                workflow_files.extend(manual_path.glob(pattern))
        
        results['total_workflows'] = len(workflow_files)
        
        for workflow_file in sorted(workflow_files):
            print(f"\n📄 Analyzing: {workflow_file.relative_to(self.repo_path)}")
            workflow_issues = self.analyze_workflow_file(workflow_file)
            
            if workflow_issues['issues']:
                results['workflows_with_issues'] += 1
                results['total_issues'] += len(workflow_issues['issues'])
                
                # Count issues by type
                for issue in workflow_issues['issues']:
                    issue_type = issue['type']
                    if issue_type not in results['issues_by_type']:
                        results['issues_by_type'][issue_type] = 0
                    results['issues_by_type'][issue_type] += 1
            
            results['workflow_details'][str(workflow_file)] = workflow_issues
        
        return results
    
    def analyze_workflow_file(self, workflow_file: Path) -> Dict[str, Any]:
        """Analyze a single workflow file for issues."""
        analysis = {
            'file': str(workflow_file),
            'issues': [],
            'fixes_available': [],
            'syntax_valid': True
        }
        
        try:
            with open(workflow_file, 'r') as f:
                content = f.read()
                
            # Check YAML syntax
            try:
                workflow_data = yaml.safe_load(content)
                analysis['syntax_valid'] = True
            except yaml.YAMLError as e:
                analysis['syntax_valid'] = False
                analysis['issues'].append({
                    'type': 'yaml_syntax',
                    'severity': 'critical',
                    'message': f"YAML syntax error: {e}",
                    'fix_available': False
                })
                return analysis
            
            # Analyze workflow structure
            self._check_python_version_consistency(workflow_data, analysis, workflow_file)
            self._check_missing_python_setup(workflow_data, analysis, workflow_file)
            self._check_dependency_issues(workflow_data, analysis, workflow_file)
            self._check_build_configuration(workflow_data, analysis, workflow_file)
            self._check_workflow_efficiency(workflow_data, analysis, workflow_file)
            
        except Exception as e:
            analysis['issues'].append({
                'type': 'file_read_error',
                'severity': 'critical',
                'message': f"Failed to read workflow file: {e}",
                'fix_available': False
            })
        
        return analysis
    
    def _check_python_version_consistency(self, workflow_data: Dict, analysis: Dict, workflow_file: Path):
        """Check for Python version consistency issues."""
        if 'jobs' not in workflow_data:
            return
        
        python_versions_found = set()
        
        for job_name, job_config in workflow_data['jobs'].items():
            if 'steps' not in job_config:
                continue
                
            for step in job_config['steps']:
                if (step.get('uses', '').startswith('actions/setup-python') and 
                    'with' in step and 'python-version' in step['with']):
                    version = step['with']['python-version']
                    python_versions_found.add(version)
                    
                    if version != '3.12':
                        analysis['issues'].append({
                            'type': 'python_version_inconsistent',
                            'severity': 'high',
                            'message': f"Job '{job_name}' uses Python {version} instead of 3.12",
                            'job': job_name,
                            'fix_available': True,
                            'fix_description': f"Change python-version to '3.12' in {job_name}"
                        })
        
        if len(python_versions_found) > 1:
            analysis['issues'].append({
                'type': 'python_version_mixed',
                'severity': 'medium',
                'message': f"Multiple Python versions found: {', '.join(python_versions_found)}",
                'fix_available': True,
                'fix_description': "Standardize all jobs to use Python 3.12"
            })
    
    def _check_missing_python_setup(self, workflow_data: Dict, analysis: Dict, workflow_file: Path):
        """Check for jobs that need Python but don't set it up."""
        if 'jobs' not in workflow_data:
            return
        
        for job_name, job_config in workflow_data['jobs'].items():
            if 'steps' not in job_config:
                continue
            
            needs_python = False
            has_python_setup = False
            
            for step in job_config['steps']:
                # Check if step needs Python
                run_command = step.get('run', '')
                if ('python' in run_command.lower() or 
                    'pip' in run_command.lower() or
                    step.get('uses', '').startswith('actions/setup-python')):
                    if step.get('uses', '').startswith('actions/setup-python'):
                        has_python_setup = True
                    else:
                        needs_python = True
            
            if needs_python and not has_python_setup:
                analysis['issues'].append({
                    'type': 'missing_python_setup',
                    'severity': 'high',
                    'message': f"Job '{job_name}' uses Python but doesn't set up Python environment",
                    'job': job_name,
                    'fix_available': True,
                    'fix_description': f"Add setup-python@v4 step with python-version: '3.12' to {job_name}"
                })
    
    def _check_dependency_issues(self, workflow_data: Dict, analysis: Dict, workflow_file: Path):
        """Check for dependency-related issues."""
        if 'jobs' not in workflow_data:
            return
        
        for job_name, job_config in workflow_data['jobs'].items():
            if 'steps' not in job_config:
                continue
            
            for step in job_config['steps']:
                run_command = step.get('run', '')
                
                # Check for incorrect package names
                if 'pip install' in run_command and 'zmq>=' in run_command:
                    analysis['issues'].append({
                        'type': 'package_name_error',
                        'severity': 'medium',
                        'message': f"Job '{job_name}' uses 'zmq' package name instead of 'pyzmq'",
                        'job': job_name,
                        'fix_available': True,
                        'fix_description': "Replace 'zmq>=' with 'pyzmq>=' in pip install commands"
                    })
                
                # Check for missing system dependencies
                if ('cmake --build' in run_command and 
                    not any('apt-get install' in s.get('run', '') for s in job_config['steps'])):
                    analysis['issues'].append({
                        'type': 'missing_system_deps',
                        'severity': 'medium',
                        'message': f"Job '{job_name}' builds code but may be missing system dependency installation",
                        'job': job_name,
                        'fix_available': False,
                        'fix_description': "Verify all required system dependencies are installed"
                    })
    
    def _check_build_configuration(self, workflow_data: Dict, analysis: Dict, workflow_file: Path):
        """Check build configuration issues."""
        if 'jobs' not in workflow_data:
            return
        
        for job_name, job_config in workflow_data['jobs'].items():
            if 'steps' not in job_config:
                continue
            
            has_cmake_config = False
            has_cmake_build = False
            
            for step in job_config['steps']:
                run_command = step.get('run', '')
                
                if 'cmake -S' in run_command or 'cmake -B' in run_command:
                    has_cmake_config = True
                
                if 'cmake --build' in run_command:
                    has_cmake_build = True
                    
                    # Check for build optimization flags
                    if '-j' not in run_command and '--parallel' not in run_command:
                        analysis['issues'].append({
                            'type': 'build_not_optimized',
                            'severity': 'low',
                            'message': f"Job '{job_name}' build command not using parallel compilation",
                            'job': job_name,
                            'fix_available': True,
                            'fix_description': "Add -j4 or --parallel 4 to cmake --build command"
                        })
            
            # Check for CMake cache clearing
            if has_cmake_config:
                cache_clear_found = False
                for step in job_config['steps']:
                    run_command = step.get('run', '')
                    if 'rm -f' in run_command and 'CMakeCache.txt' in run_command:
                        cache_clear_found = True
                        break
                
                if not cache_clear_found:
                    analysis['issues'].append({
                        'type': 'cmake_cache_not_cleared',
                        'severity': 'low',
                        'message': f"Job '{job_name}' doesn't clear CMake cache before configuration",
                        'job': job_name,
                        'fix_available': True,
                        'fix_description': "Add 'rm -f build/CMakeCache.txt' before cmake configuration"
                    })
    
    def _check_workflow_efficiency(self, workflow_data: Dict, analysis: Dict, workflow_file: Path):
        """Check for workflow efficiency issues."""
        if 'jobs' not in workflow_data:
            return
        
        # Check for missing concurrency control
        if 'concurrency' not in workflow_data:
            analysis['issues'].append({
                'type': 'missing_concurrency',
                'severity': 'low',
                'message': "Workflow doesn't have concurrency control configured",
                'fix_available': True,
                'fix_description': "Add concurrency group to prevent multiple workflow runs"
            })
        
        # Check for missing timeout configurations
        for job_name, job_config in workflow_data['jobs'].items():
            if 'timeout-minutes' not in job_config:
                analysis['issues'].append({
                    'type': 'missing_timeout',
                    'severity': 'low',
                    'message': f"Job '{job_name}' doesn't have timeout configured",
                    'job': job_name,
                    'fix_available': True,
                    'fix_description': f"Add timeout-minutes to {job_name} job"
                })
    
    def apply_automatic_fixes(self, workflow_file: Path, issues: List[Dict]) -> List[str]:
        """Apply automatic fixes to a workflow file."""
        if not self.fix_mode:
            return []
        
        applied_fixes = []
        
        try:
            with open(workflow_file, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Apply fixes for each issue type
            for issue in issues:
                if not issue.get('fix_available', False):
                    continue
                
                if issue['type'] == 'python_version_inconsistent':
                    content = self._fix_python_version(content, issue)
                    applied_fixes.append(f"Fixed Python version in {issue.get('job', 'unknown job')}")
                
                elif issue['type'] == 'missing_python_setup':
                    content = self._add_python_setup(content, issue)
                    applied_fixes.append(f"Added Python setup to {issue.get('job', 'unknown job')}")
                
                elif issue['type'] == 'package_name_error':
                    content = self._fix_package_names(content)
                    applied_fixes.append("Fixed package names (zmq -> pyzmq)")
                
                elif issue['type'] == 'build_not_optimized':
                    content = self._optimize_build_commands(content)
                    applied_fixes.append("Optimized build commands with parallel compilation")
                
                elif issue['type'] == 'missing_concurrency':
                    content = self._add_concurrency_control(content)
                    applied_fixes.append("Added concurrency control")
            
            # Only write if changes were made
            if content != original_content:
                with open(workflow_file, 'w') as f:
                    f.write(content)
                
                print(f"✅ Applied {len(applied_fixes)} fixes to {workflow_file.name}")
            
        except Exception as e:
            print(f"❌ Error applying fixes to {workflow_file}: {e}")
        
        return applied_fixes
    
    def _fix_python_version(self, content: str, issue: Dict) -> str:
        """Fix Python version to 3.12."""
        pattern = r"python-version:\s*['\"]?[^'\"\\n]+['\"]?"
        replacement = "python-version: '3.12'"
        return re.sub(pattern, replacement, content)
    
    def _add_python_setup(self, content: str, issue: Dict) -> str:
        """Add Python setup step after checkout."""
        job_name = issue.get('job', '')
        if not job_name:
            return content
        
        # Find the job and add Python setup after checkout
        lines = content.split('\n')
        in_target_job = False
        in_steps = False
        checkout_step_end = -1
        
        for i, line in enumerate(lines):
            if f"{job_name}:" in line and not line.strip().startswith('#'):
                in_target_job = True
            elif in_target_job and line.strip().startswith('steps:'):
                in_steps = True
            elif in_target_job and in_steps and 'uses: actions/checkout@v4' in line:
                # Find the end of this step
                j = i + 1
                while j < len(lines) and (lines[j].startswith('      ') or lines[j].strip() == ''):
                    j += 1
                checkout_step_end = j - 1
                break
        
        if checkout_step_end > 0:
            python_setup = [
                "      - name: Set up Python 3.12",
                "        uses: actions/setup-python@v4",
                "        with:",
                "          python-version: '3.12'"
            ]
            lines[checkout_step_end+1:checkout_step_end+1] = python_setup
        
        return '\n'.join(lines)
    
    def _fix_package_names(self, content: str) -> str:
        """Fix package names (zmq -> pyzmq)."""
        return content.replace('zmq>=', 'pyzmq>=')
    
    def _optimize_build_commands(self, content: str) -> str:
        """Add parallel compilation to build commands."""
        pattern = r"cmake --build build(?!\s+.*(?:-j|--parallel))"
        replacement = "cmake --build build --parallel 4"
        return re.sub(pattern, replacement, content)
    
    def _add_concurrency_control(self, content: str) -> str:
        """Add concurrency control to workflow."""
        lines = content.split('\n')
        
        # Find the 'on:' section and add concurrency after it
        on_section_end = -1
        for i, line in enumerate(lines):
            if line.startswith('on:'):
                # Find the end of the 'on:' section
                j = i + 1
                while j < len(lines) and (lines[j].startswith('  ') or lines[j].strip() == ''):
                    j += 1
                on_section_end = j - 1
                break
        
        if on_section_end > 0:
            concurrency_lines = [
                "",
                "concurrency:",
                "  group: ${{ github.workflow }}-${{ github.ref || github.run_id }}",
                "  cancel-in-progress: true"
            ]
            lines[on_section_end+1:on_section_end+1] = concurrency_lines
        
        return '\n'.join(lines)
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive issue report."""
        report = []
        report.append("# Workflow Issues Report")
        report.append(f"Generated: {Path.cwd()}")
        report.append("")
        
        # Summary
        report.append("## Summary")
        report.append(f"- Total workflows analyzed: {results['total_workflows']}")
        report.append(f"- Workflows with issues: {results['workflows_with_issues']}")
        report.append(f"- Total issues found: {results['total_issues']}")
        report.append("")
        
        # Issues by type
        if results['issues_by_type']:
            report.append("## Issues by Type")
            for issue_type, count in sorted(results['issues_by_type'].items()):
                report.append(f"- {issue_type}: {count}")
            report.append("")
        
        # Detailed findings
        report.append("## Detailed Findings")
        for workflow_file, details in results['workflow_details'].items():
            if details['issues']:
                report.append(f"### {Path(workflow_file).name}")
                
                for issue in details['issues']:
                    severity_icon = {"critical": "🔴", "high": "🟡", "medium": "🟠", "low": "🔵"}.get(issue['severity'], "⚪")
                    report.append(f"- {severity_icon} **{issue['type']}** ({issue['severity']}): {issue['message']}")
                    
                    if issue.get('fix_available'):
                        report.append(f"  - 🔧 Fix: {issue.get('fix_description', 'Automatic fix available')}")
                
                report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("1. Run with `--fix` flag to apply automatic fixes")
        report.append("2. Review all critical and high severity issues first")
        report.append("3. Test workflow changes in a feature branch")
        report.append("4. Consider implementing additional CI optimizations")
        
        return '\n'.join(report)
    
    def run_analysis(self) -> None:
        """Run the complete workflow analysis."""
        print("🚀 Starting Workflow Issue Analysis")
        print("=" * 50)
        
        results = self.scan_all_workflows()
        
        # Apply fixes if in fix mode
        if self.fix_mode:
            print("\n🔧 Applying automatic fixes...")
            for workflow_file, details in results['workflow_details'].items():
                if details['issues']:
                    fixes = self.apply_automatic_fixes(Path(workflow_file), details['issues'])
                    self.fixes_applied.extend(fixes)
        
        # Generate report
        report = self.generate_report(results)
        report_file = self.repo_path / "workflow_issues_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: {report_file}")
        
        # Summary
        print("\n" + "=" * 50)
        print("🏁 Analysis Complete")
        print(f"📊 Found {results['total_issues']} issues in {results['workflows_with_issues']}/{results['total_workflows']} workflows")
        
        if self.fix_mode and self.fixes_applied:
            print(f"🔧 Applied {len(self.fixes_applied)} automatic fixes")
            print("✅ Re-run analysis to verify fixes")
        elif results['total_issues'] > 0:
            print("💡 Run with --fix flag to apply automatic fixes")
        else:
            print("✅ No issues found!")

def main():
    parser = argparse.ArgumentParser(description="Detect and fix workflow issues")
    parser.add_argument("--repo", default=".", help="Repository path")
    parser.add_argument("--fix", action="store_true", help="Apply automatic fixes")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without applying")
    
    args = parser.parse_args()
    
    detector = WorkflowIssueDetector(args.repo, fix_mode=args.fix and not args.dry_run)
    detector.run_analysis()

if __name__ == "__main__":
    main()