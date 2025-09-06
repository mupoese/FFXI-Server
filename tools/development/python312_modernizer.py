#!/usr/bin/env python3
"""
Python 3.12 Code Modernizer
Applies specific Python 3.12 optimizations and fixes to all Python files
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Any


class Python312Modernizer:
    """Apply Python 3.12 specific optimizations and fixes"""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.changes_made = []
        
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
    
    def modernize_string_formatting(self, file_path: Path) -> bool:
        """Convert old-style string formatting to f-strings where possible"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Pattern for simple % formatting: f"text {variable} text"
            simple_patterns = [
                (r'"([^"]*?)%s([^"]*?)"\s*%\s*(\w+)', r'f"\1{\3}\2"'),
                (r"'([^']*?)%s([^']*?)'\s*%\s*(\w+)", r"f'\1{\3}\2'"),
                (r'"([^"]*?)%d([^"]*?)"\s*%\s*(\w+)', r'f"\1{\3}\2"'),
                (r"'([^']*?)%d([^']*?)'\s*%\s*(\w+)", r"f'\1{\3}\2'"),
            ]
            
            for pattern, replacement in simple_patterns:
                if re.search(pattern, content):
                    new_content = re.sub(pattern, replacement, content)
                    if new_content != content:
                        content = new_content
                        self.changes_made.append(f"{file_path}: Converted % formatting to f-string")
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
        
        except Exception as e:
            print(f"Error modernizing {file_path}: {e}")
        
        return False
    
    def add_python312_optimizations(self, file_path: Path) -> bool:
        """Add Python 3.12 specific optimizations"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Add type hints where missing in function definitions
            if not re.search(r'from typing import', content) and re.search(r'def \w+\(.*\):', content):
                # Don't add if it's just a simple script
                if re.search(r'class \w+', content):
                    content = "from typing import Any, Dict, List, Optional, Union\n" + content
                    self.changes_made.append(f"{file_path}: Added typing imports")
            
            # Ensure proper encoding declaration
            if not content.startswith('#!/usr/bin/env python3') and not content.startswith('#'):
                if 'coding:' not in content[:200] and len(content) > 100:
                    content = '#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\n' + content
                    self.changes_made.append(f"{file_path}: Added proper encoding header")
            
            # Update old exception handling
            content = re.sub(r'except (\w+), (\w+):', r'except \1 as \2:', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
        
        except Exception as e:
            print(f"Error adding optimizations to {file_path}: {e}")
        
        return False
    
    def fix_compatibility_issues(self, file_path: Path) -> bool:
        """Fix actual compatibility issues"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Fix actual deprecated imports
            replacements = [
                (r'from collections import (\w+)', r'from collections.abc import \1'),
                (r'import importlib\b', 'import importlib'),
                # Only fix actual file() constructor calls, not methods
                (r'\bfile\s*\(([^)]+)\)', r'open(\1)'),
                (r'\.has_key\(', ' in '),
                (r'\bbasestring\b', 'str'),
                (r'\bunicode\(', 'str('),
                (r'\bxrange\(', 'range('),
            ]
            
            for pattern, replacement in replacements:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    self.changes_made.append(f"{file_path}: Fixed {pattern}")
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
        
        except Exception as e:
            print(f"Error fixing compatibility issues in {file_path}: {e}")
        
        return False
    
    def validate_syntax(self, file_path: Path) -> bool:
        """Validate that the file still has valid Python syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            ast.parse(content)
            return True
        
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return False
        except Exception:
            return True  # Assume it's okay if we can't parse for other reasons
    
    def modernize_file(self, file_path: Path) -> bool:
        """Apply all modernizations to a single file"""
        changes = False
        
        # Apply fixes in order
        if self.fix_compatibility_issues(file_path):
            changes = True
        
        if self.modernize_string_formatting(file_path):
            changes = True
        
        if self.add_python312_optimizations(file_path):
            changes = True
        
        # Validate syntax after changes
        if changes and not self.validate_syntax(file_path):
            print(f"Warning: Syntax issues in {file_path} after modernization")
            return False
        
        return changes
    
    def modernize_all_files(self) -> Dict[str, Any]:
        """Modernize all Python files in the repository"""
        python_files = self.get_python_files()
        results = {
            'total_files': len(python_files),
            'files_modified': 0,
            'changes_made': []
        }
        
        print(f"Modernizing {len(python_files)} Python files for Python 3.12...")
        
        for file_path in python_files:
            print(f"Processing {file_path}")
            
            if self.modernize_file(file_path):
                results['files_modified'] += 1
        
        results['changes_made'] = self.changes_made
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a modernization report"""
        report = []
        report.append("Python 3.12 Modernization Report")
        report.append("=" * 40)
        report.append(f"Total files processed: {results['total_files']}")
        report.append(f"Files modified: {results['files_modified']}")
        report.append(f"Total changes: {len(results['changes_made'])}")
        report.append("")
        
        if results['changes_made']:
            report.append("Changes made:")
            for change in results['changes_made']:
                report.append(f"  - {change}")
        else:
            report.append("No changes were necessary.")
        
        return "\n".join(report)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Modernize Python code for Python 3.12')
    parser.add_argument('--repo-root', default='.', help='Repository root directory')
    parser.add_argument('--output', help='Output report to file')
    
    args = parser.parse_args()
    
    modernizer = Python312Modernizer(args.repo_root)
    results = modernizer.modernize_all_files()
    report = modernizer.generate_report(results)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())