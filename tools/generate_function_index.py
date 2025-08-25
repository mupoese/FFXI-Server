#!/usr/bin/env python3
"""
Function Indexing System for LandSandBoat Server

This tool generates comprehensive documentation for:
- C++ classes and functions
- Lua script functions with cross-references
- Python tools API documentation  
- SQL schema with relationships

Usage: python3 generate_function_index.py [--output-dir OUTPUT_DIR] [--component COMPONENT]
"""

import os
import re
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class FunctionInfo:
    """Information about a function or method."""
    name: str
    source_file: str
    line_number: int
    return_type: str
    parameters: List[str]
    description: str
    namespace: str = ""
    class_name: str = ""
    visibility: str = "public"


@dataclass
class ClassInfo:
    """Information about a C++ class."""
    name: str
    source_file: str
    line_number: int
    namespace: str
    description: str
    base_classes: List[str]
    methods: List[FunctionInfo]
    lua_binding: Optional[str] = None


@dataclass
class LuaFunctionInfo:
    """Information about a Lua function."""
    name: str
    source_file: str
    line_number: int
    parameters: List[str]
    description: str
    category: str = ""
    cross_references: List[str] = None
    cpp_binding: Optional[str] = None


@dataclass
class PythonFunctionInfo:
    """Information about a Python function."""
    name: str
    source_file: str
    line_number: int
    parameters: List[str]
    return_type: str
    description: str
    module: str
    is_class_method: bool = False
    class_name: str = ""


@dataclass
class SQLTableInfo:
    """Information about a SQL table."""
    name: str
    source_file: str
    columns: List[Dict[str, str]]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    indexes: List[Dict[str, str]]
    description: str


class FunctionIndexGenerator:
    """Main class for generating function index documentation."""
    
    def __init__(self, output_dir: str = "documentation/function_index"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage for collected information
        self.cpp_classes: List[ClassInfo] = []
        self.cpp_functions: List[FunctionInfo] = []
        self.lua_functions: List[LuaFunctionInfo] = []
        self.python_functions: List[PythonFunctionInfo] = []
        self.sql_tables: List[SQLTableInfo] = []
        
        # Cross-reference mappings
        self.lua_to_cpp_bindings: Dict[str, str] = {}
        self.cpp_to_lua_bindings: Dict[str, str] = {}
        
    def generate_all(self) -> None:
        """Generate documentation for all components."""
        print("🔍 Generating Function Indexing System Documentation...")
        
        print("📋 Analyzing C++ code...")
        self._analyze_cpp_code()
        
        print("🌙 Analyzing Lua scripts...")
        self._analyze_lua_scripts()
        
        print("🐍 Analyzing Python tools...")
        self._analyze_python_tools()
        
        print("🗄️ Analyzing SQL schema...")
        self._analyze_sql_schema()
        
        print("🔗 Building cross-references...")
        self._build_cross_references()
        
        print("📝 Generating documentation...")
        self._generate_documentation()
        
        print(f"✅ Documentation generated in: {self.output_dir}")

    def _analyze_cpp_code(self) -> None:
        """Analyze C++ source files for classes and functions."""
        src_dir = Path("src")
        if not src_dir.exists():
            print("⚠️ Source directory 'src' not found")
            return
            
        for cpp_file in src_dir.rglob("*.cpp"):
            self._parse_cpp_file(cpp_file)
        
        for header_file in src_dir.rglob("*.h"):
            self._parse_cpp_file(header_file)
    
    def _parse_cpp_file(self, file_path: Path) -> None:
        """Parse a single C++ file for functions and classes."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
            current_namespace = ""
            current_class = None
            line_num = 0
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('//') or line.startswith('/*'):
                    continue
                
                # Detect namespace
                if line.startswith('namespace ') and '{' in line:
                    current_namespace = re.search(r'namespace\s+(\w+)', line)
                    if current_namespace:
                        current_namespace = current_namespace.group(1)
                
                # Detect class definitions
                class_match = re.match(r'class\s+(\w+)(?:\s*:\s*public\s+(.+?))?(?:\s*{|;)', line)
                if class_match:
                    class_name = class_match.group(1)
                    base_classes = []
                    if class_match.group(2):
                        base_classes = [cls.strip() for cls in class_match.group(2).split(',')]
                    
                    current_class = ClassInfo(
                        name=class_name,
                        source_file=str(file_path),
                        line_number=line_num,
                        namespace=current_namespace,
                        description="",
                        base_classes=base_classes,
                        methods=[]
                    )
                    self.cpp_classes.append(current_class)
                
                # Detect function definitions
                func_match = re.match(r'(?:auto\s+)?(?:(\w+(?:::\w+)*)::|)(\w+)\s*\(([^)]*)\)(?:\s*->\s*(\w+))?', line)
                if func_match and not line.startswith('#'):
                    class_part = func_match.group(1) or ""
                    func_name = func_match.group(2)
                    params_str = func_match.group(3) or ""
                    return_type = func_match.group(4) or "void"
                    
                    # Parse parameters
                    parameters = []
                    if params_str.strip():
                        for param in params_str.split(','):
                            param = param.strip()
                            if param:
                                parameters.append(param)
                    
                    func_info = FunctionInfo(
                        name=func_name,
                        source_file=str(file_path),
                        line_number=line_num,
                        return_type=return_type,
                        parameters=parameters,
                        description="",
                        namespace=current_namespace,
                        class_name=class_part.split('::')[-1] if class_part else ""
                    )
                    
                    if current_class and class_part:
                        current_class.methods.append(func_info)
                    else:
                        self.cpp_functions.append(func_info)
        
        except Exception as e:
            print(f"⚠️ Error parsing {file_path}: {e}")

    def _analyze_lua_scripts(self) -> None:
        """Analyze Lua script files for functions."""
        scripts_dir = Path("scripts")
        if not scripts_dir.exists():
            print("⚠️ Scripts directory not found")
            return
            
        for lua_file in scripts_dir.rglob("*.lua"):
            if "specs" not in str(lua_file):  # Skip spec files
                self._parse_lua_file(lua_file)
    
    def _parse_lua_file(self, file_path: Path) -> None:
        """Parse a single Lua file for functions."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('--'):
                    continue
                
                # Detect function definitions
                func_match = re.match(r'function\s+([^(]+)\s*\(([^)]*)\)', line)
                if func_match:
                    func_name = func_match.group(1).strip()
                    params_str = func_match.group(2) or ""
                    
                    # Parse parameters
                    parameters = []
                    if params_str.strip():
                        for param in params_str.split(','):
                            param = param.strip()
                            if param:
                                parameters.append(param)
                    
                    # Determine category based on file path
                    category = self._get_lua_category(file_path)
                    
                    lua_func = LuaFunctionInfo(
                        name=func_name,
                        source_file=str(file_path),
                        line_number=line_num,
                        parameters=parameters,
                        description="",
                        category=category,
                        cross_references=[]
                    )
                    self.lua_functions.append(lua_func)
        
        except Exception as e:
            print(f"⚠️ Error parsing Lua file {file_path}: {e}")
    
    def _get_lua_category(self, file_path: Path) -> str:
        """Determine the category of a Lua function based on file path."""
        path_parts = file_path.parts
        if "quests" in path_parts:
            return "quest"
        elif "missions" in path_parts:
            return "mission"
        elif "zones" in path_parts:
            return "zone"
        elif "items" in path_parts:
            return "item"
        elif "globals" in path_parts:
            return "global"
        else:
            return "other"

    def _analyze_python_tools(self) -> None:
        """Analyze Python tools for API documentation."""
        tools_dir = Path("tools")
        if not tools_dir.exists():
            print("⚠️ Tools directory not found")
            return
            
        for py_file in tools_dir.rglob("*.py"):
            self._parse_python_file(py_file)
    
    def _parse_python_file(self, file_path: Path) -> None:
        """Parse a single Python file for functions and classes."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            current_class = None
            for line_num, line in enumerate(lines, 1):
                original_line = line
                line = line.strip()
                
                # Skip comments and empty lines  
                if not line or line.startswith('#'):
                    continue
                
                # Detect class definitions
                class_match = re.match(r'class\s+(\w+)(?:\([^)]*\))?:', line)
                if class_match:
                    current_class = class_match.group(1)
                
                # Detect function definitions
                func_match = re.match(r'def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*(.+?))?:', line)
                if func_match:
                    func_name = func_match.group(1)
                    params_str = func_match.group(2) or ""
                    return_type = func_match.group(3) or "None"
                    
                    # Parse parameters
                    parameters = []
                    if params_str.strip():
                        for param in params_str.split(','):
                            param = param.strip()
                            if param:
                                parameters.append(param)
                    
                    # Get module name from file path
                    module_name = file_path.stem
                    
                    # Look for docstring
                    description = ""
                    if line_num < len(lines):
                        next_lines = lines[line_num:line_num+3]
                        for next_line in next_lines:
                            if '"""' in next_line or "'''" in next_line:
                                description = next_line.strip().strip('"""\'')
                                break
                    
                    py_func = PythonFunctionInfo(
                        name=func_name,
                        source_file=str(file_path),
                        line_number=line_num,
                        parameters=parameters,
                        return_type=return_type,
                        description=description,
                        module=module_name,
                        is_class_method=current_class is not None,
                        class_name=current_class or ""
                    )
                    self.python_functions.append(py_func)
        
        except Exception as e:
            print(f"⚠️ Error parsing Python file {file_path}: {e}")

    def _analyze_sql_schema(self) -> None:
        """Analyze SQL files for schema documentation."""
        sql_dir = Path("sql")
        if not sql_dir.exists():
            print("⚠️ SQL directory not found")
            return
            
        for sql_file in sql_dir.rglob("*.sql"):
            self._parse_sql_file(sql_file)
    
    def _parse_sql_file(self, file_path: Path) -> None:
        """Parse a single SQL file for table definitions."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find CREATE TABLE statements
            table_matches = re.finditer(
                r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\((.*?)\)(?:\s*ENGINE\s*=\s*\w+)?(?:\s*DEFAULT\s+CHARSET\s*=\s*\w+)?;',
                content,
                re.IGNORECASE | re.DOTALL
            )
            
            for match in table_matches:
                table_name = match.group(1)
                table_def = match.group(2)
                
                columns = []
                primary_keys = []
                foreign_keys = []
                indexes = []
                
                # Parse columns
                for column_line in table_def.split(','):
                    column_line = column_line.strip()
                    if not column_line:
                        continue
                    
                    # Skip constraints
                    if any(keyword in column_line.upper() for keyword in ['PRIMARY KEY', 'FOREIGN KEY', 'KEY ', 'INDEX']):
                        continue
                    
                    # Parse column definition
                    col_match = re.match(r'`?(\w+)`?\s+([^,\s]+)(?:\s+(.+?))?$', column_line)
                    if col_match:
                        col_name = col_match.group(1)
                        col_type = col_match.group(2)
                        col_attrs = col_match.group(3) or ""
                        
                        columns.append({
                            'name': col_name,
                            'type': col_type,
                            'attributes': col_attrs
                        })
                
                sql_table = SQLTableInfo(
                    name=table_name,
                    source_file=str(file_path),
                    columns=columns,
                    primary_keys=primary_keys,
                    foreign_keys=foreign_keys,
                    indexes=indexes,
                    description=""
                )
                self.sql_tables.append(sql_table)
        
        except Exception as e:
            print(f"⚠️ Error parsing SQL file {file_path}: {e}")

    def _build_cross_references(self) -> None:
        """Build cross-references between C++ and Lua bindings."""
        # Look for SOL_USERTYPE and SOL_REGISTER patterns
        for cpp_file in Path("src").rglob("*.cpp"):
            try:
                with open(cpp_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Find SOL_USERTYPE bindings
                usertype_matches = re.finditer(r'SOL_USERTYPE\s*\(\s*"([^"]+)"\s*,\s*(\w+)', content)
                for match in usertype_matches:
                    lua_name = match.group(1)
                    cpp_name = match.group(2)
                    self.lua_to_cpp_bindings[lua_name] = cpp_name
                    self.cpp_to_lua_bindings[cpp_name] = lua_name
                
            except Exception as e:
                print(f"⚠️ Error reading {cpp_file} for cross-references: {e}")

    def _generate_documentation(self) -> None:
        """Generate the final documentation files."""
        # Generate main index
        self._generate_main_index()
        
        # Generate component-specific documentation
        self._generate_cpp_documentation()
        self._generate_lua_documentation()
        self._generate_python_documentation()
        self._generate_sql_documentation()
        
        # Generate cross-reference documentation
        self._generate_cross_reference_documentation()
        
        # Generate JSON data files for API consumption
        self._generate_json_data()

    def _generate_main_index(self) -> None:
        """Generate the main index page."""
        index_path = self.output_dir / "index.md"
        
        with open(index_path, 'w') as f:
            f.write("# LandSandBoat Function Index\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Overview\n\n")
            f.write("This documentation provides a comprehensive index of all functions, classes, and schemas in the LandSandBoat server.\n\n")
            
            f.write("## Statistics\n\n")
            f.write(f"- **C++ Classes**: {len(self.cpp_classes)}\n")
            f.write(f"- **C++ Functions**: {len(self.cpp_functions)}\n")
            f.write(f"- **Lua Functions**: {len(self.lua_functions)}\n")
            f.write(f"- **Python Functions**: {len(self.python_functions)}\n")
            f.write(f"- **SQL Tables**: {len(self.sql_tables)}\n\n")
            
            f.write("## Components\n\n")
            f.write("- [C++ API Documentation](cpp_api.md)\n")
            f.write("- [Lua Function Catalog](lua_catalog.md)\n")
            f.write("- [Python Tools API](python_api.md)\n")
            f.write("- [SQL Schema Documentation](sql_schema.md)\n")
            f.write("- [Cross-Reference Guide](cross_references.md)\n\n")
    
    def _generate_cpp_documentation(self) -> None:
        """Generate C++ API documentation."""
        cpp_path = self.output_dir / "cpp_api.md"
        
        with open(cpp_path, 'w') as f:
            f.write("# C++ API Documentation\n\n")
            
            # Group by namespace
            namespaces = {}
            for cls in self.cpp_classes:
                namespace = cls.namespace or "global"
                if namespace not in namespaces:
                    namespaces[namespace] = []
                namespaces[namespace].append(cls)
            
            for namespace, classes in sorted(namespaces.items()):
                f.write(f"## Namespace: {namespace}\n\n")
                
                for cls in sorted(classes, key=lambda x: x.name):
                    f.write(f"### {cls.name}\n\n")
                    f.write(f"**File**: `{cls.source_file}:{cls.line_number}`\n\n")
                    
                    if cls.base_classes:
                        f.write(f"**Inherits from**: {', '.join(cls.base_classes)}\n\n")
                    
                    if cls.lua_binding:
                        f.write(f"**Lua Binding**: `{cls.lua_binding}`\n\n")
                    
                    if cls.methods:
                        f.write("**Methods**:\n\n")
                        for method in sorted(cls.methods, key=lambda x: x.name):
                            params = ", ".join(method.parameters) if method.parameters else ""
                            f.write(f"- `{method.return_type} {method.name}({params})`\n")
                        f.write("\n")

    def _generate_lua_documentation(self) -> None:
        """Generate Lua function catalog."""
        lua_path = self.output_dir / "lua_catalog.md"
        
        with open(lua_path, 'w') as f:
            f.write("# Lua Function Catalog\n\n")
            
            # Group by category
            categories = {}
            for func in self.lua_functions:
                category = func.category or "other"
                if category not in categories:
                    categories[category] = []
                categories[category].append(func)
            
            for category, functions in sorted(categories.items()):
                f.write(f"## {category.title()} Functions\n\n")
                
                for func in sorted(functions, key=lambda x: x.name):
                    f.write(f"### {func.name}\n\n")
                    f.write(f"**File**: `{func.source_file}:{func.line_number}`\n\n")
                    
                    if func.parameters:
                        f.write(f"**Parameters**: {', '.join(func.parameters)}\n\n")
                    
                    if func.cpp_binding:
                        f.write(f"**C++ Binding**: `{func.cpp_binding}`\n\n")

    def _generate_python_documentation(self) -> None:
        """Generate Python tools API documentation."""
        python_path = self.output_dir / "python_api.md"
        
        with open(python_path, 'w') as f:
            f.write("# Python Tools API Documentation\n\n")
            
            # Group by module
            modules = {}
            for func in self.python_functions:
                module = func.module
                if module not in modules:
                    modules[module] = []
                modules[module].append(func)
            
            for module, functions in sorted(modules.items()):
                f.write(f"## Module: {module}\n\n")
                
                for func in sorted(functions, key=lambda x: x.name):
                    f.write(f"### {func.name}\n\n")
                    f.write(f"**File**: `{func.source_file}:{func.line_number}`\n\n")
                    
                    if func.parameters:
                        f.write(f"**Parameters**: {', '.join(func.parameters)}\n\n")
                    
                    f.write(f"**Returns**: `{func.return_type}`\n\n")
                    
                    if func.description:
                        f.write(f"**Description**: {func.description}\n\n")

    def _generate_sql_documentation(self) -> None:
        """Generate SQL schema documentation."""
        sql_path = self.output_dir / "sql_schema.md"
        
        with open(sql_path, 'w') as f:
            f.write("# SQL Schema Documentation\n\n")
            
            for table in sorted(self.sql_tables, key=lambda x: x.name):
                f.write(f"## Table: {table.name}\n\n")
                f.write(f"**File**: `{table.source_file}`\n\n")
                
                if table.columns:
                    f.write("**Columns**:\n\n")
                    f.write("| Column | Type | Attributes |\n")
                    f.write("|--------|------|------------|\n")
                    for col in table.columns:
                        f.write(f"| {col['name']} | {col['type']} | {col['attributes']} |\n")
                    f.write("\n")

    def _generate_cross_reference_documentation(self) -> None:
        """Generate cross-reference documentation."""
        cross_ref_path = self.output_dir / "cross_references.md"
        
        with open(cross_ref_path, 'w') as f:
            f.write("# Cross-Reference Guide\n\n")
            f.write("## C++ to Lua Bindings\n\n")
            
            for cpp_name, lua_name in sorted(self.cpp_to_lua_bindings.items()):
                f.write(f"- `{cpp_name}` → `{lua_name}`\n")
            
            f.write("\n## Lua to C++ Bindings\n\n")
            
            for lua_name, cpp_name in sorted(self.lua_to_cpp_bindings.items()):
                f.write(f"- `{lua_name}` → `{cpp_name}`\n")

    def _generate_json_data(self) -> None:
        """Generate JSON data files for API consumption."""
        json_dir = self.output_dir / "json"
        json_dir.mkdir(exist_ok=True)
        
        # Convert dataclasses to dictionaries for JSON serialization
        data = {
            'cpp_classes': [asdict(cls) for cls in self.cpp_classes],
            'cpp_functions': [asdict(func) for func in self.cpp_functions],
            'lua_functions': [asdict(func) for func in self.lua_functions],
            'python_functions': [asdict(func) for func in self.python_functions],
            'sql_tables': [asdict(table) for table in self.sql_tables],
            'cpp_to_lua_bindings': self.cpp_to_lua_bindings,
            'lua_to_cpp_bindings': self.lua_to_cpp_bindings
        }
        
        with open(json_dir / "function_index.json", 'w') as f:
            json.dump(data, f, indent=2)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate Function Indexing System documentation")
    parser.add_argument(
        "--output-dir", 
        default="documentation/function_index",
        help="Output directory for generated documentation"
    )
    parser.add_argument(
        "--component",
        choices=['cpp', 'lua', 'python', 'sql', 'all'],
        default='all',
        help="Component to analyze (default: all)"
    )
    
    args = parser.parse_args()
    
    generator = FunctionIndexGenerator(args.output_dir)
    
    if args.component == 'all':
        generator.generate_all()
    elif args.component == 'cpp':
        generator._analyze_cpp_code()
        generator._generate_cpp_documentation()
    elif args.component == 'lua':
        generator._analyze_lua_scripts()
        generator._generate_lua_documentation()
    elif args.component == 'python':
        generator._analyze_python_tools()
        generator._generate_python_documentation()
    elif args.component == 'sql':
        generator._analyze_sql_schema()
        generator._generate_sql_documentation()


if __name__ == "__main__":
    main()