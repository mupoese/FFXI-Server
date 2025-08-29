#!/usr/bin/env python3
"""
Enhanced Function Indexing System for LandSandBoat Server
Comprehensive documentation generator implementing the Function Indexing System from ROADMAP.md
"""

import os
import sys
import json
import sqlite3
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class FunctionInfo:
    """Represents a function or method across languages"""
    name: str
    file_path: str
    language: str
    signature: str
    return_type: str
    parameters: List[Dict[str, str]]
    docstring: str
    line_number: int
    complexity: int
    is_public: bool
    namespace: str
    cross_references: List[str]

@dataclass
class ClassInfo:
    """Represents a class or namespace"""
    name: str
    file_path: str
    language: str
    methods: List[str]
    inheritance: List[str]
    docstring: str
    line_number: int
    is_public: bool

class EnhancedFunctionIndexer:
    """Enhanced Function Indexing System with cross-language support"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.functions: Dict[str, FunctionInfo] = {}
        self.classes: Dict[str, ClassInfo] = {}
        self.cross_references: Dict[str, Set[str]] = {}
        self.db_path = project_root / "documentation" / "function_index.db"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for function indexing"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS functions (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    language TEXT NOT NULL,
                    signature TEXT,
                    return_type TEXT,
                    parameters TEXT,
                    docstring TEXT,
                    line_number INTEGER,
                    complexity INTEGER,
                    is_public BOOLEAN,
                    namespace TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    language TEXT NOT NULL,
                    methods TEXT,
                    inheritance TEXT,
                    docstring TEXT,
                    line_number INTEGER,
                    is_public BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cross_references (
                    id INTEGER PRIMARY KEY,
                    source_function TEXT NOT NULL,
                    target_function TEXT NOT NULL,
                    reference_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def scan_cpp_files(self):
        """Scan C++ files for functions and classes"""
        cpp_patterns = {
            'function': re.compile(r'^\s*(?:(?:virtual|static|inline|explicit)\s+)*(?:(\w+(?:\s*\*|\s*&)?)\s+)?(\w+)\s*\(([^)]*)\)\s*(?:const)?\s*(?:override)?\s*{?', re.MULTILINE),
            'class': re.compile(r'^\s*class\s+(\w+)(?:\s*:\s*([^{]+))?\s*{', re.MULTILINE),
            'namespace': re.compile(r'^\s*namespace\s+(\w+)\s*{', re.MULTILINE)
        }
        
        cpp_files = list(self.project_root.glob("src/**/*.cpp")) + list(self.project_root.glob("src/**/*.h"))
        
        for file_path in cpp_files:
            self._scan_file_with_patterns(file_path, cpp_patterns, 'cpp')
    
    def scan_lua_files(self):
        """Scan Lua files for functions and global objects"""
        lua_patterns = {
            'function': re.compile(r'^\s*(?:local\s+)?function\s+([.\w:]+)\s*\(([^)]*)\)', re.MULTILINE),
            'global_function': re.compile(r'^\s*(\w+)\s*=\s*function\s*\(([^)]*)\)', re.MULTILINE),
            'table': re.compile(r'^\s*(\w+)\s*=\s*{', re.MULTILINE)
        }
        
        lua_files = list(self.project_root.glob("scripts/**/*.lua"))
        
        for file_path in lua_files:
            self._scan_file_with_patterns(file_path, lua_patterns, 'lua')
    
    def scan_python_files(self):
        """Scan Python files for functions and classes"""
        python_patterns = {
            'function': re.compile(r'^\s*def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([^:]+))?\s*:', re.MULTILINE),
            'class': re.compile(r'^\s*class\s+(\w+)(?:\(([^)]+)\))?\s*:', re.MULTILINE),
            'async_function': re.compile(r'^\s*async\s+def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([^:]+))?\s*:', re.MULTILINE)
        }
        
        python_files = list(self.project_root.glob("tools/**/*.py"))
        
        for file_path in python_files:
            self._scan_file_with_patterns(file_path, python_patterns, 'python')
    
    def _scan_file_with_patterns(self, file_path: Path, patterns: Dict[str, re.Pattern], language: str):
        """Scan a file with given patterns and extract function/class information"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            relative_path = str(file_path.relative_to(self.project_root))
            
            for pattern_type, pattern in patterns.items():
                for match in pattern.finditer(content):
                    line_number = content[:match.start()].count('\n') + 1
                    
                    if pattern_type in ['function', 'global_function', 'async_function']:
                        self._extract_function_info(match, relative_path, language, line_number, content)
                    elif pattern_type in ['class', 'table']:
                        self._extract_class_info(match, relative_path, language, line_number, content)
        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
    
    def _extract_function_info(self, match, file_path: str, language: str, line_number: int, content: str):
        """Extract function information from regex match"""
        if language == 'cpp':
            return_type = match.group(1) or 'void'
            name = match.group(2)
            params = match.group(3)
        elif language in ['lua', 'python']:
            name = match.group(1)
            params = match.group(2)
            return_type = match.group(3) if len(match.groups()) > 2 else 'unknown'
        else:
            return
        
        # Extract docstring/comments before function
        lines = content.split('\n')
        docstring = self._extract_docstring(lines, line_number - 1, language)
        
        # Calculate basic complexity (count of control flow statements)
        func_content = self._extract_function_body(content, match.start(), language)
        complexity = self._calculate_complexity(func_content, language)
        
        # Determine if function is public
        is_public = self._is_public_function(name, func_content, language)
        
        # Extract namespace/scope
        namespace = self._extract_namespace(file_path, name, language)
        
        function_info = FunctionInfo(
            name=name,
            file_path=file_path,
            language=language,
            signature=f"{name}({params})",
            return_type=return_type,
            parameters=self._parse_parameters(params, language),
            docstring=docstring,
            line_number=line_number,
            complexity=complexity,
            is_public=is_public,
            namespace=namespace,
            cross_references=[]
        )
        
        # Store in memory
        full_name = f"{namespace}::{name}" if namespace else name
        self.functions[full_name] = function_info
    
    def _extract_class_info(self, match, file_path: str, language: str, line_number: int, content: str):
        """Extract class information from regex match"""
        name = match.group(1)
        inheritance = match.group(2).split(',') if len(match.groups()) > 1 and match.group(2) else []
        
        lines = content.split('\n')
        docstring = self._extract_docstring(lines, line_number - 1, language)
        
        class_info = ClassInfo(
            name=name,
            file_path=file_path,
            language=language,
            methods=[],
            inheritance=[i.strip() for i in inheritance],
            docstring=docstring,
            line_number=line_number,
            is_public=True
        )
        
        self.classes[name] = class_info
    
    def _extract_docstring(self, lines: List[str], line_index: int, language: str) -> str:
        """Extract docstring or comment block before function/class"""
        docstring_lines = []
        i = line_index - 1
        
        if language == 'cpp':
            # Look for /** */ or /// comments
            while i >= 0 and (lines[i].strip().startswith('///') or 
                            lines[i].strip().startswith('*') or 
                            '*/' in lines[i]):
                docstring_lines.insert(0, lines[i].strip())
                i -= 1
        elif language == 'python':
            # Look for """ docstrings or # comments
            while i >= 0 and (lines[i].strip().startswith('#') or 
                            '"""' in lines[i]):
                docstring_lines.insert(0, lines[i].strip())
                i -= 1
        elif language == 'lua':
            # Look for -- comments
            while i >= 0 and lines[i].strip().startswith('--'):
                docstring_lines.insert(0, lines[i].strip())
                i -= 1
        
        return '\n'.join(docstring_lines)
    
    def _extract_function_body(self, content: str, start_pos: int, language: str) -> str:
        """Extract function body for complexity analysis"""
        lines = content[start_pos:].split('\n')
        if not lines:
            return ""
        
        # Simple heuristic: find matching braces/end keywords
        if language == 'cpp':
            brace_count = 0
            body_lines = []
            for line in lines:
                body_lines.append(line)
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and '{' in line:
                    break
        elif language == 'lua':
            # Look for 'end' keyword
            body_lines = []
            for line in lines:
                body_lines.append(line)
                if line.strip() == 'end':
                    break
        else:  # python
            # Look for next function or class at same indentation
            first_line_indent = len(lines[0]) - len(lines[0].lstrip())
            body_lines = [lines[0]]
            for line in lines[1:]:
                if line.strip() and len(line) - len(line.lstrip()) <= first_line_indent:
                    break
                body_lines.append(line)
        
        return '\n'.join(body_lines)
    
    def _calculate_complexity(self, content: str, language: str) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        if language == 'cpp':
            keywords = ['if', 'else', 'while', 'for', 'switch', 'case', 'catch', '&&', '||', '?']
        elif language == 'python':
            keywords = ['if', 'elif', 'else', 'while', 'for', 'try', 'except', 'and', 'or']
        elif language == 'lua':
            keywords = ['if', 'elseif', 'else', 'while', 'for', 'repeat', 'and', 'or']
        else:
            return complexity
        
        content_lower = content.lower()
        for keyword in keywords:
            complexity += content_lower.count(keyword)
        
        return complexity
    
    def _is_public_function(self, name: str, content: str, language: str) -> bool:
        """Determine if function is public"""
        if language == 'cpp':
            return not (name.startswith('_') or 'private:' in content or 'static' in content)
        elif language == 'python':
            return not name.startswith('_')
        elif language == 'lua':
            return 'local' not in content
        return True
    
    def _extract_namespace(self, file_path: str, name: str, language: str) -> str:
        """Extract namespace or module information"""
        if language == 'cpp':
            if 'src/map/' in file_path:
                return 'ximap'
            elif 'src/common/' in file_path:
                return 'xibase'
            elif 'src/search/' in file_path:
                return 'xisearch'
        elif language == 'lua':
            if 'scripts/globals/' in file_path:
                return 'xi'
            elif 'scripts/zones/' in file_path:
                return 'xi.zones'
        elif language == 'python':
            if 'tools/' in file_path:
                return 'tools'
        
        return ''
    
    def _parse_parameters(self, params_str: str, language: str) -> List[Dict[str, str]]:
        """Parse parameter string into structured data"""
        if not params_str.strip():
            return []
        
        parameters = []
        for param in params_str.split(','):
            param = param.strip()
            if not param:
                continue
            
            param_info = {'name': param, 'type': 'unknown', 'default': None}
            
            if language == 'cpp':
                # Parse "type name" or "type name = default"
                parts = param.split('=')
                if len(parts) > 1:
                    param_info['default'] = parts[1].strip()
                    param = parts[0].strip()
                
                # Extract type and name
                tokens = param.split()
                if len(tokens) >= 2:
                    param_info['type'] = ' '.join(tokens[:-1])
                    param_info['name'] = tokens[-1]
            elif language == 'python':
                # Parse "name: type = default" or "name = default"
                if ':' in param:
                    name_part, type_part = param.split(':', 1)
                    param_info['name'] = name_part.strip()
                    if '=' in type_part:
                        type_part, default_part = type_part.split('=', 1)
                        param_info['default'] = default_part.strip()
                    param_info['type'] = type_part.strip()
                elif '=' in param:
                    name_part, default_part = param.split('=', 1)
                    param_info['name'] = name_part.strip()
                    param_info['default'] = default_part.strip()
            
            parameters.append(param_info)
        
        return parameters
    
    def find_cross_references(self):
        """Find cross-references between functions"""
        for func_name, func_info in self.functions.items():
            # Look for function calls in other functions
            for other_name, other_info in self.functions.items():
                if func_name != other_name:
                    # Simple pattern matching for function calls
                    if self._function_calls_other(other_info, func_info):
                        if other_name not in self.cross_references:
                            self.cross_references[other_name] = set()
                        self.cross_references[other_name].add(func_name)
    
    def _function_calls_other(self, caller: FunctionInfo, callee: FunctionInfo) -> bool:
        """Check if caller function calls callee function"""
        # This is a simplified implementation
        # In a real system, you'd parse the AST or use static analysis
        
        # Read the file and look for function name
        try:
            with open(self.project_root / caller.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Look for function name in caller's file
            return callee.name in content
        except:
            return False
    
    def save_to_database(self):
        """Save all indexed information to SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            # Clear existing data
            conn.execute('DELETE FROM functions')
            conn.execute('DELETE FROM classes')
            conn.execute('DELETE FROM cross_references')
            
            # Insert functions
            for func_info in self.functions.values():
                conn.execute('''
                    INSERT INTO functions (
                        name, file_path, language, signature, return_type, 
                        parameters, docstring, line_number, complexity, 
                        is_public, namespace
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    func_info.name,
                    func_info.file_path,
                    func_info.language,
                    func_info.signature,
                    func_info.return_type,
                    json.dumps(func_info.parameters),
                    func_info.docstring,
                    func_info.line_number,
                    func_info.complexity,
                    func_info.is_public,
                    func_info.namespace
                ))
            
            # Insert classes
            for class_info in self.classes.values():
                conn.execute('''
                    INSERT INTO classes (
                        name, file_path, language, methods, inheritance,
                        docstring, line_number, is_public
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    class_info.name,
                    class_info.file_path,
                    class_info.language,
                    json.dumps(class_info.methods),
                    json.dumps(class_info.inheritance),
                    class_info.docstring,
                    class_info.line_number,
                    class_info.is_public
                ))
            
            # Insert cross-references
            for source, targets in self.cross_references.items():
                for target in targets:
                    conn.execute('''
                        INSERT INTO cross_references (
                            source_function, target_function, reference_type
                        ) VALUES (?, ?, ?)
                    ''', (source, target, 'calls'))
    
    def generate_html_documentation(self):
        """Generate HTML documentation from indexed data"""
        docs_dir = self.project_root / "documentation" / "function_index"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate main index page
        self._generate_main_index(docs_dir)
        
        # Generate language-specific pages
        languages = set(func.language for func in self.functions.values())
        for language in languages:
            self._generate_language_page(docs_dir, language)
        
        # Generate individual function pages
        for func_name, func_info in self.functions.items():
            self._generate_function_page(docs_dir, func_name, func_info)
    
    def _generate_main_index(self, docs_dir: Path):
        """Generate main documentation index page"""
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>LandSandBoat Function Index</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; margin-bottom: 30px; }}
        .stats {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
        .language-section {{ margin-bottom: 30px; }}
        .function-list {{ list-style: none; padding: 0; }}
        .function-item {{ padding: 10px; border-bottom: 1px solid #bdc3c7; }}
        .complexity-high {{ color: #e74c3c; }}
        .complexity-medium {{ color: #f39c12; }}
        .complexity-low {{ color: #27ae60; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>LandSandBoat Function Index</h1>
        <p>Comprehensive API documentation generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>{len(self.functions)}</h3>
            <p>Total Functions</p>
        </div>
        <div class="stat-card">
            <h3>{len(self.classes)}</h3>
            <p>Classes/Objects</p>
        </div>
        <div class="stat-card">
            <h3>{len(set(func.language for func in self.functions.values()))}</h3>
            <p>Languages</p>
        </div>
        <div class="stat-card">
            <h3>{sum(len(refs) for refs in self.cross_references.values())}</h3>
            <p>Cross References</p>
        </div>
    </div>
'''
        
        # Add language sections
        languages = set(func.language for func in self.functions.values())
        for language in sorted(languages):
            lang_functions = [f for f in self.functions.values() if f.language == language]
            html_content += f'''
    <div class="language-section">
        <h2>{language.upper()} Functions ({len(lang_functions)})</h2>
        <ul class="function-list">
'''
            for func in sorted(lang_functions, key=lambda f: f.name):
                complexity_class = 'complexity-low' if func.complexity <= 5 else 'complexity-medium' if func.complexity <= 15 else 'complexity-high'
                html_content += f'''
            <li class="function-item">
                <a href="{language}/{func.name}.html">{func.signature}</a>
                <span class="{complexity_class}"> (complexity: {func.complexity})</span>
                <br><small>{func.file_path}:{func.line_number}</small>
            </li>
'''
            html_content += '''
        </ul>
    </div>
'''
        
        html_content += '''
</body>
</html>
'''
        
        with open(docs_dir / "index.html", 'w') as f:
            f.write(html_content)
    
    def _generate_language_page(self, docs_dir: Path, language: str):
        """Generate documentation page for a specific language"""
        lang_dir = docs_dir / language
        lang_dir.mkdir(exist_ok=True)
        
        lang_functions = [f for f in self.functions.values() if f.language == language]
        
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>{language.upper()} Functions - LandSandBoat</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; margin-bottom: 30px; }}
        .function-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .function-card {{ border: 1px solid #bdc3c7; padding: 15px; border-radius: 5px; }}
        .function-signature {{ font-family: monospace; background: #ecf0f1; padding: 5px; }}
        a {{ text-decoration: none; color: #3498db; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{language.upper()} Functions</h1>
        <p><a href="../index.html">← Back to Main Index</a></p>
    </div>
    
    <div class="function-grid">
'''
        
        for func in sorted(lang_functions, key=lambda f: f.name):
            html_content += f'''
        <div class="function-card">
            <h3><a href="{func.name}.html">{func.name}</a></h3>
            <div class="function-signature">{func.signature}</div>
            <p><strong>File:</strong> {func.file_path}:{func.line_number}</p>
            <p><strong>Complexity:</strong> {func.complexity}</p>
            <p><strong>Namespace:</strong> {func.namespace or 'global'}</p>
            {f'<p><strong>Returns:</strong> {func.return_type}</p>' if func.return_type != 'unknown' else ''}
            {f'<p>{func.docstring[:100]}...</p>' if func.docstring else ''}
        </div>
'''
        
        html_content += '''
    </div>
</body>
</html>
'''
        
        with open(lang_dir / "index.html", 'w') as f:
            f.write(html_content)
    
    def _generate_function_page(self, docs_dir: Path, func_name: str, func_info: FunctionInfo):
        """Generate detailed page for a specific function"""
        lang_dir = docs_dir / func_info.language
        lang_dir.mkdir(exist_ok=True)
        
        # Get cross-references
        called_by = [source for source, targets in self.cross_references.items() if func_name in targets]
        calls = list(self.cross_references.get(func_name, []))
        
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>{func_info.name} - {func_info.language.upper()}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; margin-bottom: 30px; }}
        .function-details {{ background: #ecf0f1; padding: 20px; margin-bottom: 20px; }}
        .signature {{ font-family: monospace; font-size: 18px; margin-bottom: 10px; }}
        .parameters {{ margin: 20px 0; }}
        .parameter {{ margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #3498db; }}
        .cross-refs {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
        .ref-section {{ background: #ecf0f1; padding: 15px; }}
        pre {{ background: #2c3e50; color: white; padding: 15px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{func_info.name}</h1>
        <p><a href="index.html">← Back to {func_info.language.upper()} Functions</a> | <a href="../index.html">Main Index</a></p>
    </div>
    
    <div class="function-details">
        <div class="signature">{func_info.signature}</div>
        <p><strong>File:</strong> {func_info.file_path}:{func_info.line_number}</p>
        <p><strong>Language:</strong> {func_info.language}</p>
        <p><strong>Namespace:</strong> {func_info.namespace or 'global'}</p>
        <p><strong>Return Type:</strong> {func_info.return_type}</p>
        <p><strong>Complexity:</strong> {func_info.complexity}</p>
        <p><strong>Public:</strong> {'Yes' if func_info.is_public else 'No'}</p>
    </div>
'''
        
        if func_info.docstring:
            html_content += f'''
    <div class="documentation">
        <h2>Documentation</h2>
        <pre>{func_info.docstring}</pre>
    </div>
'''
        
        if func_info.parameters:
            html_content += '''
    <div class="parameters">
        <h2>Parameters</h2>
'''
            for param in func_info.parameters:
                html_content += f'''
        <div class="parameter">
            <strong>{param['name']}</strong> ({param['type']})
            {f"<br>Default: {param['default']}" if param['default'] else ""}
        </div>
'''
            html_content += '''
    </div>
'''
        
        if called_by or calls:
            html_content += '''
    <div class="cross-refs">
'''
            if called_by:
                html_content += f'''
        <div class="ref-section">
            <h3>Called By</h3>
            <ul>
'''
                for caller in called_by[:10]:  # Limit to avoid overwhelming
                    html_content += f'<li>{caller}</li>'
                html_content += '''
            </ul>
        </div>
'''
            
            if calls:
                html_content += f'''
        <div class="ref-section">
            <h3>Calls</h3>
            <ul>
'''
                for called in list(calls)[:10]:  # Limit to avoid overwhelming
                    html_content += f'<li>{called}</li>'
                html_content += '''
            </ul>
        </div>
'''
            html_content += '''
    </div>
'''
        
        html_content += '''
</body>
</html>
'''
        
        with open(lang_dir / f"{func_info.name}.html", 'w') as f:
            f.write(html_content)
    
    def run_full_indexing(self):
        """Run complete function indexing process"""
        print("🔍 Starting Enhanced Function Indexing...")
        
        print("  📁 Scanning C++ files...")
        self.scan_cpp_files()
        
        print("  📁 Scanning Lua files...")
        self.scan_lua_files()
        
        print("  📁 Scanning Python files...")
        self.scan_python_files()
        
        print("  🔗 Finding cross-references...")
        self.find_cross_references()
        
        print("  💾 Saving to database...")
        self.save_to_database()
        
        print("  📖 Generating HTML documentation...")
        self.generate_html_documentation()
        
        print(f"✅ Function indexing complete!")
        print(f"   Functions indexed: {len(self.functions)}")
        print(f"   Classes indexed: {len(self.classes)}")
        print(f"   Cross-references: {sum(len(refs) for refs in self.cross_references.values())}")
        print(f"   Documentation: documentation/function_index/index.html")

def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    indexer = EnhancedFunctionIndexer(project_root)
    indexer.run_full_indexing()

if __name__ == "__main__":
    main()