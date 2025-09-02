#!/usr/bin/env python3
"""
Python 3.12 Compatibility Checker
Analyzes all Python files for Python 3.12 compatibility issues and suggests fixes
"""

import ast
import os
import sys
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple
import argparse


class Python312CompatibilityChecker:
    """Check and fix Python 3.12 compatibility issues"""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.issues = []
        self.fixes_applied = []
        
    def get_python_files(self) -> List[Path]:
        """Get all Python files in the repository"""
        python_files = []
        for root, dirs, files in os.walk(self.repo_root):
            # Skip certain directories
            if any(skip_dir in root for skip_dir in ['.git', '__pycache__', '.pytest_cache', 'node_modules']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def check_syntax_compatibility(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check if file syntax is compatible with Python 3.12"""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Try to parse with Python 3.12 AST
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append({
                    'type': 'syntax_error',
                    'file': file_path,
                    'line': e.lineno,
                    'message': str(e),
                    'severity': 'high'
                })
            
            # Check for deprecated features
            issues.extend(self._check_deprecated_features(file_path, content))
            
        except Exception as e:
            issues.append({
                'type': 'read_error',
                'file': file_path,
                'message': f"Could not read file: {e}",
                'severity': 'medium'
            })
        
        return issues
    
    def _check_deprecated_features(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Check for deprecated features that may cause issues in Python 3.12"""
        issues = []
        lines = content.split('\n')
        
        patterns = [
            (r'imp\.', 'imp module is deprecated, use importlib instead'),
            (r'asyncio\.coroutine', 'asyncio.coroutine is deprecated, use async def instead'),
            (r'collections\.[A-Z]', 'Collections ABC moved to collections.abc'),
            (r'platform\.dist\(', 'platform.dist() is removed, use distro package'),
            (r'\.has_key\(', ' in ) is removed, use "in" operator'),
            (r'xrange\(', 'xrange is removed, use range()'),
            (r'str', 'str is removed, use str'),
            (r'unicode\(', 'str() is removed, use str()'),
            (r'\bfile\(', 'file() is removed, use open()'),
            (r'execfile\(', 'execfile() is removed, use exec(open().read())'),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, message in patterns:
                if re.search(pattern, line):
                    issues.append({
                        'type': 'deprecated_feature',
                        'file': file_path,
                        'line': line_num,
                        'message': message,
                        'severity': 'medium'
                    })
        
        return issues
    
    def check_import_compatibility(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check if imports are compatible with Python 3.12"""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse imports
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        issue = self._check_module_compatibility(alias.name)
                        if issue:
                            issues.append({
                                'type': 'import_issue',
                                'file': file_path,
                                'line': node.lineno,
                                'module': alias.name,
                                'message': issue,
                                'severity': 'medium'
                            })
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        issue = self._check_module_compatibility(node.module)
                        if issue:
                            issues.append({
                                'type': 'import_issue',
                                'file': file_path,
                                'line': node.lineno,
                                'module': node.module,
                                'message': issue,
                                'severity': 'medium'
                            })
        
        except Exception as e:
            issues.append({
                'type': 'ast_parse_error',
                'file': file_path,
                'message': f"Could not parse AST: {e}",
                'severity': 'high'
            })
        
        return issues
    
    def _check_module_compatibility(self, module_name: str) -> str:
        """Check if a module has known compatibility issues"""
        compatibility_issues = {
            'imp': 'Use importlib instead',
            'distutils': 'Use setuptools instead',
            'platform.dist': 'Use distro package instead',
        }
        
        for problematic_module, suggestion in compatibility_issues.items():
            if module_name.startswith(problematic_module):
                return suggestion
        
        return None
    
    def check_string_formatting(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check for old-style string formatting that should be updated"""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                # Check for old % formatting
                if re.search(r'\w+\s*%\s*[^"]', line) and 'logging' not in line.lower() and 'strftime' not in line:
                    issues.append({
                        'type': 'string_formatting',
                        'file': file_path,
                        'line': line_num,
                        'message': 'Consider using f-strings or .format() instead of % formatting',
                        'severity': 'low'
                    })
        
        except Exception as e:
            pass  # Non-critical check
        
        return issues
    
    def run_flake8_check(self, file_path: Path) -> List[Dict[str, Any]]:
        """Run flake8 on the file to check for style issues"""
        issues = []
        try:
            result = subprocess.run([
                'python3', '-m', 'flake8', 
                '--max-line-length=120',
                '--ignore=E501,W503',
                str(file_path)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            issues.append({
                                'type': 'style_issue',
                                'file': file_path,
                                'line': int(parts[1]) if parts[1].isdigit() else 0,
                                'message': parts[3].strip(),
                                'severity': 'low'
                            })
        
        except Exception:
            pass  # flake8 not available or other issue
        
        return issues
    
    def apply_common_fixes(self, file_path: Path) -> bool:
        """Apply common Python 3.12 compatibility fixes"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Fix common import issues
            content = re.sub(r'from collections.abc import ', 'from collections.abc import ', content)
            content = re.sub(r'import importlib\b', 'import importlib', content)
            
            # Fix print(statements (if any))
            content = re.sub(r'print\s+([^(].*)', r'print(\1)', content)
            
            # Ensure proper encoding declaration if missing
            if not content.startswith('#!/usr/bin/env python3') and not content.startswith('#'):
                if 'coding:' not in content[:200]:
                    content = '#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n' + content
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied.append(str(file_path))
                return True
        
        except Exception as e:
            print(f"Error applying fixes to {file_path}: {e}")
        
        return False
    
    def analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze a single Python file for Python 3.12 compatibility"""
        issues = []
        
        # Check syntax compatibility
        issues.extend(self.check_syntax_compatibility(file_path))
        
        # Check import compatibility
        issues.extend(self.check_import_compatibility(file_path))
        
        # Check string formatting
        issues.extend(self.check_string_formatting(file_path))
        
        # Run style checks
        issues.extend(self.run_flake8_check(file_path))
        
        return issues
    
    def analyze_all_files(self, fix_issues: bool = False) -> Dict[str, Any]:
        """Analyze all Python files in the repository"""
        python_files = self.get_python_files()
        results = {
            'total_files': len(python_files),
            'files_with_issues': 0,
            'total_issues': 0,
            'issues_by_severity': {'high': 0, 'medium': 0, 'low': 0},
            'files': {}
        }
        
        print(f"Analyzing {len(python_files)} Python files for Python 3.12 compatibility...")
        
        for file_path in python_files:
            print(f"Checking {file_path}")
            
            if fix_issues:
                self.apply_common_fixes(file_path)
            
            file_issues = self.analyze_file(file_path)
            
            if file_issues:
                results['files_with_issues'] += 1
                results['files'][str(file_path)] = file_issues
                results['total_issues'] += len(file_issues)
                
                for issue in file_issues:
                    severity = issue.get('severity', 'medium')
                    results['issues_by_severity'][severity] += 1
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed report"""
        report = []
        report.append("Python 3.12 Compatibility Analysis Report")
        report.append("=" * 50)
        report.append(f"Total files analyzed: {results['total_files']}")
        report.append(f"Files with issues: {results['files_with_issues']}")
        report.append(f"Total issues found: {results['total_issues']}")
        report.append(f"Issues by severity:")
        report.append(f"  High: {results['issues_by_severity']['high']}")
        report.append(f"  Medium: {results['issues_by_severity']['medium']}")
        report.append(f"  Low: {results['issues_by_severity']['low']}")
        report.append("")
        
        if self.fixes_applied:
            report.append(f"Fixes applied to {len(self.fixes_applied)} files:")
            for fixed_file in self.fixes_applied:
                report.append(f"  - {fixed_file}")
            report.append("")
        
        # Group issues by file
        for file_path, issues in results['files'].items():
            if issues:
                report.append(f"File: {file_path}")
                report.append("-" * (len(file_path) + 6))
                for issue in issues:
                    line_info = f" (line {issue['line']})" if 'line' in issue else ""
                    report.append(f"  [{issue['severity'].upper()}] {issue['message']}{line_info}")
                report.append("")
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description='Check Python 3.12 compatibility')
    parser.add_argument('--fix', action='store_true', help='Apply automatic fixes')
    parser.add_argument('--repo-root', default='.', help='Repository root directory')
    parser.add_argument('--output', help='Output report to file')
    
    args = parser.parse_args()
    
    checker = Python312CompatibilityChecker(args.repo_root)
    results = checker.analyze_all_files(fix_issues=args.fix)
    report = checker.generate_report(results)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)
    
    return 0 if results['issues_by_severity']['high'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())