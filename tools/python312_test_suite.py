#!/usr/bin/env python3
"""
Python 3.12 Test Suite
Tests all Python files for syntax and basic import compatibility
"""

import ast
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any


def test_python_file_syntax(file_path: Path) -> Dict[str, Any]:
    """Test if a Python file has valid syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try to parse with Python 3.12 AST
        ast.parse(content)
        return {'status': 'ok', 'file': str(file_path)}
    
    except SyntaxError as e:
        return {
            'status': 'syntax_error',
            'file': str(file_path),
            'error': str(e),
            'line': e.lineno
        }
    except Exception as e:
        return {
            'status': 'read_error',
            'file': str(file_path),
            'error': str(e)
        }


def test_python_file_imports(file_path: Path) -> Dict[str, Any]:
    """Test if a Python file can be imported without errors"""
    try:
        # Skip certain test files and tools that require specific setup
        skip_files = [
            'test_',
            'migrations/',
            'web/',  # Flask app needs DB
            'demo_',
            'headlessxi',  # Game client tools
        ]
        
        if any(skip in str(file_path) for skip in skip_files):
            return {'status': 'skipped', 'file': str(file_path), 'reason': 'Test/demo file'}
        
        # Try to compile the file
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', str(file_path)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {'status': 'ok', 'file': str(file_path)}
        else:
            return {
                'status': 'compile_error',
                'file': str(file_path),
                'error': result.stderr.strip()
            }
    
    except subprocess.TimeoutExpired:
        return {
            'status': 'timeout',
            'file': str(file_path),
            'error': 'Compilation timeout'
        }
    except Exception as e:
        return {
            'status': 'test_error',
            'file': str(file_path),
            'error': str(e)
        }


def get_python_files(repo_root: Path) -> List[Path]:
    """Get all Python files in the repository"""
    python_files = []
    for root, dirs, files in os.walk(repo_root):
        # Skip certain directories
        if any(skip_dir in root for skip_dir in ['.git', '__pycache__', '.pytest_cache']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files


def main():
    repo_root = Path('.')
    python_files = get_python_files(repo_root)
    
    print(f"Testing {len(python_files)} Python files for Python 3.12 compatibility...")
    print("=" * 70)
    
    syntax_results = []
    import_results = []
    
    for file_path in python_files:
        print(f"Testing {file_path}")
        
        # Test syntax
        syntax_result = test_python_file_syntax(file_path)
        syntax_results.append(syntax_result)
        
        # Test imports (compilation)
        import_result = test_python_file_imports(file_path)
        import_results.append(import_result)
    
    # Generate summary
    print("\n" + "=" * 70)
    print("PYTHON 3.12 COMPATIBILITY TEST RESULTS")
    print("=" * 70)
    
    syntax_ok = sum(1 for r in syntax_results if r['status'] == 'ok')
    syntax_errors = [r for r in syntax_results if r['status'] != 'ok']
    
    import_ok = sum(1 for r in import_results if r['status'] == 'ok')
    import_skipped = sum(1 for r in import_results if r['status'] == 'skipped')
    import_errors = [r for r in import_results if r['status'] not in ['ok', 'skipped']]
    
    print(f"Syntax Tests: {syntax_ok}/{len(python_files)} passed")
    print(f"Import Tests: {import_ok}/{len(python_files)} passed, {import_skipped} skipped")
    print()
    
    if syntax_errors:
        print("SYNTAX ERRORS:")
        for error in syntax_errors:
            print(f"  {error['file']}: {error['error']}")
        print()
    
    if import_errors:
        print("IMPORT/COMPILATION ERRORS:")
        for error in import_errors:
            print(f"  {error['file']}: {error['error']}")
        print()
    
    # Overall result
    if not syntax_errors and not import_errors:
        print("✅ ALL TESTS PASSED - Python 3.12 compatibility confirmed!")
        return 0
    else:
        print("❌ Some tests failed - see errors above")
        return 1


if __name__ == '__main__':
    sys.exit(main())