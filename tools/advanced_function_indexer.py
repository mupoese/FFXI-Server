#!/usr/bin/env python3
"""
Advanced Function Indexing System for FFXI-Server
Comprehensive C++/Lua/Python function catalog with enhanced analysis capabilities.

This tool provides detailed function analysis, dependency tracking, and documentation
generation for the entire FFXI-Server codebase following MCP enhancement guidelines.
"""

import os
import re
import json
import ast
import sqlite3
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import subprocess

@dataclass
class FunctionInfo:
    """Comprehensive function information structure"""
    name: str
    file_path: str
    line_number: int
    language: str
    return_type: str = ""
    parameters: List[str] = None
    visibility: str = ""  # public, private, protected
    is_static: bool = False
    is_virtual: bool = False
    is_const: bool = False
    docstring: str = ""
    complexity_score: int = 0
    calls_made: List[str] = None
    called_by: List[str] = None
    class_name: str = ""
    namespace: str = ""
    file_size: int = 0
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []
        if self.calls_made is None:
            self.calls_made = []
        if self.called_by is None:
            self.called_by = []

class AdvancedFunctionIndexer:
    """Advanced function indexing system with comprehensive analysis"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).absolute()
        self.functions: Dict[str, FunctionInfo] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.db_path = self.root_dir / "function_index.db"
        
        # Language-specific patterns
        self.cpp_function_pattern = re.compile(
            r'^\s*(?:(?:inline|static|virtual|explicit|constexpr|consteval|const)\s+)*'
            r'(?:(?:template\s*<[^>]*>\s*)?'
            r'(?:([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*(?:<[^>]*>)?)\s+)?'
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:const\s*)?(?:override\s*)?(?:final\s*)?'
            r'(?:\s*->\s*[a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*(?:<[^>]*>)?)?\s*'
            r'(?:\{|;))',
            re.MULTILINE
        )
        
        self.lua_function_pattern = re.compile(
            r'^\s*(?:local\s+)?function\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*\(',
            re.MULTILINE | re.IGNORECASE
        )
        
        self.python_function_pattern = re.compile(
            r'^\s*(?:async\s+)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            re.MULTILINE
        )
        
    def initialize_database(self):
        """Initialize SQLite database for function storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS functions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_number INTEGER,
                    language TEXT NOT NULL,
                    return_type TEXT,
                    parameters TEXT,
                    visibility TEXT,
                    is_static BOOLEAN,
                    is_virtual BOOLEAN,
                    is_const BOOLEAN,
                    docstring TEXT,
                    complexity_score INTEGER,
                    calls_made TEXT,
                    called_by TEXT,
                    class_name TEXT,
                    namespace TEXT,
                    file_size INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_function_name ON functions(name)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_file_path ON functions(file_path)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_language ON functions(language)
            ''')

    def analyze_cpp_file(self, file_path: Path) -> List[FunctionInfo]:
        """Analyze C++ file for function definitions"""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            lines = content.split('\n')
            file_size = len(lines)
            
            # Find class/namespace context
            current_class = ""
            current_namespace = ""
            brace_level = 0
            
            for i, line in enumerate(lines, 1):
                # Track namespace
                namespace_match = re.match(r'^\s*namespace\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\{', line)
                if namespace_match:
                    current_namespace = namespace_match.group(1)
                
                # Track class
                class_match = re.match(r'^\s*(?:class|struct)\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
                if class_match:
                    current_class = class_match.group(1)
                
                # Find function definitions
                func_match = self.cpp_function_pattern.match(line)
                if func_match:
                    return_type = func_match.group(1) or "void"
                    func_name = func_match.group(2)
                    
                    if func_name and not func_name.startswith('_'):  # Skip system functions
                        # Determine visibility
                        visibility = self._get_cpp_visibility(lines, i)
                        
                        # Check for keywords
                        is_static = 'static' in line
                        is_virtual = 'virtual' in line
                        is_const = 'const' in line.split(')')[-1]
                        
                        # Get parameters
                        params = self._extract_cpp_parameters(line)
                        
                        # Get docstring
                        docstring = self._get_cpp_docstring(lines, i)
                        
                        # Calculate complexity
                        complexity = self._calculate_cpp_complexity(content, func_name)
                        
                        func_info = FunctionInfo(
                            name=func_name,
                            file_path=str(file_path.relative_to(self.root_dir)),
                            line_number=i,
                            language="cpp",
                            return_type=return_type,
                            parameters=params,
                            visibility=visibility,
                            is_static=is_static,
                            is_virtual=is_virtual,
                            is_const=is_const,
                            docstring=docstring,
                            complexity_score=complexity,
                            class_name=current_class,
                            namespace=current_namespace,
                            file_size=file_size
                        )
                        
                        functions.append(func_info)
                        
        except Exception as e:
            print(f"Error analyzing C++ file {file_path}: {e}")
            
        return functions

    def analyze_lua_file(self, file_path: Path) -> List[FunctionInfo]:
        """Analyze Lua file for function definitions"""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            lines = content.split('\n')
            file_size = len(lines)
            
            for i, line in enumerate(lines, 1):
                func_match = self.lua_function_pattern.match(line)
                if func_match:
                    func_name = func_match.group(1)
                    
                    # Get parameters
                    params = self._extract_lua_parameters(line)
                    
                    # Get docstring
                    docstring = self._get_lua_docstring(lines, i)
                    
                    # Calculate complexity
                    complexity = self._calculate_lua_complexity(content, func_name)
                    
                    func_info = FunctionInfo(
                        name=func_name,
                        file_path=str(file_path.relative_to(self.root_dir)),
                        line_number=i,
                        language="lua",
                        parameters=params,
                        docstring=docstring,
                        complexity_score=complexity,
                        file_size=file_size
                    )
                    
                    functions.append(func_info)
                    
        except Exception as e:
            print(f"Error analyzing Lua file {file_path}: {e}")
            
        return functions

    def analyze_python_file(self, file_path: Path) -> List[FunctionInfo]:
        """Analyze Python file for function definitions"""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Parse AST for more accurate analysis
            try:
                tree = ast.parse(content)
                file_size = len(content.split('\n'))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Get parameters
                        params = [arg.arg for arg in node.args.args]
                        
                        # Get docstring
                        docstring = ast.get_docstring(node) or ""
                        
                        # Get return type annotation
                        return_type = ""
                        if node.returns:
                            return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
                        
                        # Calculate complexity
                        complexity = self._calculate_python_complexity(node)
                        
                        func_info = FunctionInfo(
                            name=node.name,
                            file_path=str(file_path.relative_to(self.root_dir)),
                            line_number=node.lineno,
                            language="python",
                            return_type=return_type,
                            parameters=params,
                            docstring=docstring,
                            complexity_score=complexity,
                            file_size=file_size
                        )
                        
                        functions.append(func_info)
                        
            except SyntaxError:
                # Fallback to regex parsing
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    func_match = self.python_function_pattern.match(line)
                    if func_match:
                        func_name = func_match.group(1)
                        params = self._extract_python_parameters(line)
                        
                        func_info = FunctionInfo(
                            name=func_name,
                            file_path=str(file_path.relative_to(self.root_dir)),
                            line_number=i,
                            language="python",
                            parameters=params,
                            file_size=len(lines)
                        )
                        
                        functions.append(func_info)
                        
        except Exception as e:
            print(f"Error analyzing Python file {file_path}: {e}")
            
        return functions

    def _get_cpp_visibility(self, lines: List[str], func_line: int) -> str:
        """Determine C++ function visibility"""
        for i in range(func_line - 1, max(0, func_line - 20), -1):
            line = lines[i].strip()
            if line.endswith(':'):
                if 'private' in line:
                    return 'private'
                elif 'protected' in line:
                    return 'protected'
                elif 'public' in line:
                    return 'public'
        return 'public'  # Default

    def _extract_cpp_parameters(self, line: str) -> List[str]:
        """Extract parameters from C++ function declaration"""
        match = re.search(r'\(([^)]*)\)', line)
        if match:
            params_str = match.group(1).strip()
            if params_str:
                params = [p.strip() for p in params_str.split(',')]
                return [p for p in params if p and p != 'void']
        return []

    def _extract_lua_parameters(self, line: str) -> List[str]:
        """Extract parameters from Lua function declaration"""
        match = re.search(r'\(([^)]*)\)', line)
        if match:
            params_str = match.group(1).strip()
            if params_str:
                return [p.strip() for p in params_str.split(',')]
        return []

    def _extract_python_parameters(self, line: str) -> List[str]:
        """Extract parameters from Python function declaration"""
        match = re.search(r'\(([^)]*)\)', line)
        if match:
            params_str = match.group(1).strip()
            if params_str:
                params = [p.strip().split(':')[0].split('=')[0].strip() 
                         for p in params_str.split(',')]
                return [p for p in params if p and p != 'self']
        return []

    def _get_cpp_docstring(self, lines: List[str], func_line: int) -> str:
        """Extract C++ docstring (comments above function)"""
        docstring_lines = []
        for i in range(func_line - 2, max(0, func_line - 10), -1):
            line = lines[i].strip()
            if line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                docstring_lines.insert(0, line.lstrip('/*').rstrip('*/').strip())
            elif line:
                break
        return ' '.join(docstring_lines)

    def _get_lua_docstring(self, lines: List[str], func_line: int) -> str:
        """Extract Lua docstring (comments above function)"""
        docstring_lines = []
        for i in range(func_line - 2, max(0, func_line - 10), -1):
            line = lines[i].strip()
            if line.startswith('--'):
                docstring_lines.insert(0, line.lstrip('-').strip())
            elif line:
                break
        return ' '.join(docstring_lines)

    def _calculate_cpp_complexity(self, content: str, func_name: str) -> int:
        """Calculate cyclomatic complexity for C++ function"""
        # Simple complexity calculation based on control flow keywords
        complexity_keywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'catch', '&&', '||', '?']
        
        # Find function body
        func_start = content.find(f"{func_name}(")
        if func_start == -1:
            return 1
            
        brace_count = 0
        start_brace_found = False
        func_body = ""
        
        for i, char in enumerate(content[func_start:]):
            if char == '{':
                if not start_brace_found:
                    start_brace_found = True
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if start_brace_found and brace_count == 0:
                    func_body = content[func_start:func_start + i]
                    break
        
        complexity = 1  # Base complexity
        for keyword in complexity_keywords:
            complexity += len(re.findall(r'\b' + keyword + r'\b', func_body))
        
        return complexity

    def _calculate_lua_complexity(self, content: str, func_name: str) -> int:
        """Calculate cyclomatic complexity for Lua function"""
        complexity_keywords = ['if', 'elseif', 'else', 'for', 'while', 'repeat', 'and', 'or']
        
        # Find function body
        func_start = content.find(f"function {func_name}")
        if func_start == -1:
            return 1
            
        end_pos = content.find("end", func_start)
        if end_pos == -1:
            return 1
            
        func_body = content[func_start:end_pos]
        
        complexity = 1  # Base complexity
        for keyword in complexity_keywords:
            complexity += len(re.findall(r'\b' + keyword + r'\b', func_body))
        
        return complexity

    def _calculate_python_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for Python function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                complexity += 1
        
        return complexity

    def analyze_dependencies(self):
        """Analyze function call dependencies"""
        print("Analyzing function dependencies...")
        
        # Build call graph
        for func_key, func_info in self.functions.items():
            file_path = self.root_dir / func_info.file_path
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Find function calls within this function
                calls = self._find_function_calls(content, func_info)
                func_info.calls_made = calls
                
                # Update reverse dependencies
                for called_func in calls:
                    if called_func in self.functions:
                        self.functions[called_func].called_by.append(func_key)
                        
            except Exception as e:
                print(f"Error analyzing dependencies for {func_key}: {e}")

    def _find_function_calls(self, content: str, func_info: FunctionInfo) -> List[str]:
        """Find function calls within a function"""
        calls = []
        
        if func_info.language == "cpp":
            # C++ function calls
            pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
            matches = pattern.findall(content)
            calls.extend([m for m in matches if m in self.functions])
            
        elif func_info.language == "lua":
            # Lua function calls
            pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*\(')
            matches = pattern.findall(content)
            calls.extend([m for m in matches if m in self.functions])
            
        elif func_info.language == "python":
            # Python function calls
            pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
            matches = pattern.findall(content)
            calls.extend([m for m in matches if m in self.functions])
        
        return list(set(calls))

    def save_to_database(self):
        """Save function index to SQLite database"""
        print(f"Saving {len(self.functions)} functions to database...")
        
        with sqlite3.connect(self.db_path) as conn:
            # Clear existing data
            conn.execute("DELETE FROM functions")
            
            # Insert new data
            for func_info in self.functions.values():
                conn.execute('''
                    INSERT INTO functions (
                        name, file_path, line_number, language, return_type,
                        parameters, visibility, is_static, is_virtual, is_const,
                        docstring, complexity_score, calls_made, called_by,
                        class_name, namespace, file_size
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    func_info.name,
                    func_info.file_path,
                    func_info.line_number,
                    func_info.language,
                    func_info.return_type,
                    json.dumps(func_info.parameters),
                    func_info.visibility,
                    func_info.is_static,
                    func_info.is_virtual,
                    func_info.is_const,
                    func_info.docstring,
                    func_info.complexity_score,
                    json.dumps(func_info.calls_made),
                    json.dumps(func_info.called_by),
                    func_info.class_name,
                    func_info.namespace,
                    func_info.file_size
                ))

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        total_functions = len(self.functions)
        
        # Language distribution
        lang_dist = defaultdict(int)
        complexity_dist = defaultdict(int)
        
        for func_info in self.functions.values():
            lang_dist[func_info.language] += 1
            if func_info.complexity_score <= 5:
                complexity_dist['low'] += 1
            elif func_info.complexity_score <= 10:
                complexity_dist['medium'] += 1
            else:
                complexity_dist['high'] += 1
        
        # Find most complex functions
        most_complex = sorted(
            self.functions.values(),
            key=lambda x: x.complexity_score,
            reverse=True
        )[:10]
        
        # Find most called functions
        most_called = sorted(
            self.functions.values(),
            key=lambda x: len(x.called_by),
            reverse=True
        )[:10]
        
        return {
            'total_functions': total_functions,
            'language_distribution': dict(lang_dist),
            'complexity_distribution': dict(complexity_dist),
            'most_complex_functions': [
                {
                    'name': f.name,
                    'file': f.file_path,
                    'complexity': f.complexity_score,
                    'language': f.language
                }
                for f in most_complex
            ],
            'most_called_functions': [
                {
                    'name': f.name,
                    'file': f.file_path,
                    'called_by_count': len(f.called_by),
                    'language': f.language
                }
                for f in most_called
            ]
        }

    def run_analysis(self):
        """Run complete function analysis"""
        print("Starting advanced function indexing...")
        
        # Initialize database
        self.initialize_database()
        
        # File extensions to analyze
        file_patterns = {
            '**/*.cpp': self.analyze_cpp_file,
            '**/*.hpp': self.analyze_cpp_file,
            '**/*.h': self.analyze_cpp_file,
            '**/*.lua': self.analyze_lua_file,
            '**/*.py': self.analyze_python_file
        }
        
        total_files = 0
        for pattern in file_patterns.keys():
            total_files += len(list(self.root_dir.glob(pattern)))
        
        print(f"Found {total_files} files to analyze...")
        
        # Process files
        processed = 0
        for pattern, analyzer_func in file_patterns.items():
            for file_path in self.root_dir.glob(pattern):
                # Skip build directories and external libraries
                if any(skip in str(file_path) for skip in ['build', 'ext', '.git', 'node_modules']):
                    continue
                    
                try:
                    functions = analyzer_func(file_path)
                    for func_info in functions:
                        func_key = f"{func_info.name}@{func_info.file_path}:{func_info.line_number}"
                        self.functions[func_key] = func_info
                    
                    processed += 1
                    if processed % 100 == 0:
                        print(f"Processed {processed}/{total_files} files...")
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        print(f"Processed {processed} files, found {len(self.functions)} functions")
        
        # Analyze dependencies
        self.analyze_dependencies()
        
        # Save to database
        self.save_to_database()
        
        # Generate and save report
        report = self.generate_report()
        
        report_path = self.root_dir / "function_analysis_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Analysis complete! Report saved to {report_path}")
        print(f"Database saved to {self.db_path}")
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Advanced Function Indexing System")
    parser.add_argument("--root", default=".", help="Root directory to analyze")
    parser.add_argument("--output", help="Output file for JSON report")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")
    
    args = parser.parse_args()
    
    if args.quiet:
        # Redirect stdout to devnull
        sys.stdout = open(os.devnull, 'w')
    
    try:
        indexer = AdvancedFunctionIndexer(args.root)
        report = indexer.run_analysis()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
        
        if not args.quiet:
            print("\n=== FUNCTION ANALYSIS SUMMARY ===")
            print(f"Total Functions: {report['total_functions']}")
            print(f"Language Distribution: {report['language_distribution']}")
            print(f"Complexity Distribution: {report['complexity_distribution']}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()