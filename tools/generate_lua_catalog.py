#!/usr/bin/env python3
"""
Enhanced Lua Function Catalog Generator

This tool extends the existing Lua spec generation to create comprehensive
documentation with cross-references and categorization.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class LuaFunction:
    """Represents a Lua function with metadata."""
    name: str
    file_path: str
    line_number: int
    parameters: List[str]
    description: str
    category: str
    subcategory: str
    lua_binding: Optional[str] = None
    cpp_source: Optional[str] = None
    examples: List[str] = None
    cross_refs: List[str] = None


@dataclass
class LuaGlobal:
    """Represents a Lua global variable or table."""
    name: str
    file_path: str
    line_number: int
    type_info: str
    description: str
    category: str


@dataclass
class LuaBinding:
    """Represents a C++ to Lua binding."""
    lua_name: str
    cpp_class: str
    cpp_file: str
    functions: List[str]
    description: str


class LuaCatalogGenerator:
    """Generates comprehensive Lua function catalog with cross-references."""
    
    def __init__(self, scripts_dir: str = "scripts", output_dir: str = "documentation/lua_catalog"):
        self.scripts_dir = Path(scripts_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Collections
        self.functions: List[LuaFunction] = []
        self.globals: List[LuaGlobal] = []
        self.bindings: List[LuaBinding] = []
        
        # Cross-reference mappings
        self.function_refs: Dict[str, Set[str]] = {}
        self.file_functions: Dict[str, List[str]] = {}
        
        # Categories
        self.categories = {
            'quest': 'Quest System',
            'mission': 'Mission System', 
            'npc': 'NPC Interactions',
            'mob': 'Monster Behavior',
            'zone': 'Zone Management',
            'item': 'Item Handling',
            'spell': 'Spell System',
            'ability': 'Ability System',
            'battlefields': 'Battlefield System',
            'events': 'Event Handling',
            'globals': 'Global Functions',
            'mixins': 'Mixins & Utilities',
            'enum': 'Enumerations',
            'core': 'Core Bindings'
        }
    
    def analyze_lua_scripts(self) -> None:
        """Analyze all Lua scripts in the repository."""
        print("🌙 Analyzing Lua scripts...")
        
        if not self.scripts_dir.exists():
            print("⚠️ Scripts directory not found")
            return
        
        # Process all Lua files
        for lua_file in self.scripts_dir.rglob("*.lua"):
            # Skip generated spec files
            if "specs" in str(lua_file):
                continue
            
            self._analyze_lua_file(lua_file)
        
        # Analyze C++ bindings
        self._analyze_cpp_bindings()
        
        # Build cross-references
        self._build_cross_references()
        
        print(f"📊 Found {len(self.functions)} functions, {len(self.globals)} globals, {len(self.bindings)} bindings")
    
    def _analyze_lua_file(self, file_path: Path) -> None:
        """Analyze a single Lua file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            category, subcategory = self._determine_category(file_path)
            
            # Track functions for this file
            file_functions = []
            
            for line_num, line in enumerate(lines, 1):
                original_line = line
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('--'):
                    continue
                
                # Find function definitions
                func_match = re.match(r'function\s+([^(]+)\s*\(([^)]*)\)', line)
                if func_match:
                    func_name = func_match.group(1).strip()
                    params_str = func_match.group(2).strip()
                    
                    # Parse parameters
                    parameters = []
                    if params_str:
                        parameters = [p.strip() for p in params_str.split(',') if p.strip()]
                    
                    # Look for description in preceding comments
                    description = self._extract_description(lines, line_num - 1)
                    
                    # Look for examples in following comments
                    examples = self._extract_examples(lines, line_num)
                    
                    lua_func = LuaFunction(
                        name=func_name,
                        file_path=str(file_path),
                        line_number=line_num,
                        parameters=parameters,
                        description=description,
                        category=category,
                        subcategory=subcategory,
                        examples=examples or []
                    )
                    
                    self.functions.append(lua_func)
                    file_functions.append(func_name)
                
                # Find global variable definitions
                global_match = re.match(r'(\w+)\s*=\s*{', line)
                if global_match and not line.startswith('local '):
                    global_name = global_match.group(1)
                    description = self._extract_description(lines, line_num - 1)
                    
                    lua_global = LuaGlobal(
                        name=global_name,
                        file_path=str(file_path),
                        line_number=line_num,
                        type_info="table",
                        description=description,
                        category=category
                    )
                    
                    self.globals.append(lua_global)
            
            self.file_functions[str(file_path)] = file_functions
            
        except Exception as e:
            print(f"⚠️ Error analyzing {file_path}: {e}")
    
    def _determine_category(self, file_path: Path) -> Tuple[str, str]:
        """Determine category and subcategory from file path."""
        path_parts = file_path.parts
        
        # Primary category
        category = "other"
        subcategory = ""
        
        if "quests" in path_parts:
            category = "quest"
            # Extract zone name if present
            quest_idx = path_parts.index("quests")
            if quest_idx + 1 < len(path_parts):
                subcategory = path_parts[quest_idx + 1]
        elif "missions" in path_parts:
            category = "mission"
            mission_idx = path_parts.index("missions")
            if mission_idx + 1 < len(path_parts):
                subcategory = path_parts[mission_idx + 1]
        elif "zones" in path_parts:
            category = "zone"
            zone_idx = path_parts.index("zones")
            if zone_idx + 1 < len(path_parts):
                subcategory = path_parts[zone_idx + 1]
        elif "battlefields" in path_parts:
            category = "battlefields"
        elif "globals" in path_parts:
            category = "globals"
        elif "mixins" in path_parts:
            category = "mixins"
        elif "enum" in path_parts:
            category = "enum"
        elif "items" in path_parts:
            category = "item"
        elif "effects" in path_parts:
            category = "spell"
        elif "abilities" in path_parts:
            category = "ability"
        elif "actions" in path_parts:
            category = "ability"
        
        return category, subcategory
    
    def _extract_description(self, lines: List[str], line_num: int) -> str:
        """Extract description from preceding comment lines."""
        description_lines = []
        
        # Look backwards for comment lines
        i = line_num - 1
        while i >= 0:
            line = lines[i].strip()
            if line.startswith('--'):
                # Remove comment markers and clean up
                desc_line = re.sub(r'^--+\s*', '', line).strip()
                if desc_line:
                    description_lines.insert(0, desc_line)
            elif line:  # Non-empty, non-comment line
                break
            i -= 1
        
        return ' '.join(description_lines)
    
    def _extract_examples(self, lines: List[str], start_line: int) -> List[str]:
        """Extract example usage from following comment lines."""
        examples = []
        
        # Look forward for comment lines containing examples
        i = start_line
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('--') and ('example' in line.lower() or 'usage' in line.lower()):
                example_lines = []
                j = i + 1
                while j < len(lines):
                    example_line = lines[j].strip()
                    if example_line.startswith('--'):
                        example_content = re.sub(r'^--+\s*', '', example_line).strip()
                        if example_content:
                            example_lines.append(example_content)
                    elif example_line:
                        break
                    j += 1
                
                if example_lines:
                    examples.append('\n'.join(example_lines))
                break
            elif not line.startswith('--') and line:
                break
            i += 1
        
        return examples
    
    def _analyze_cpp_bindings(self) -> None:
        """Analyze C++ to Lua bindings."""
        print("🔗 Analyzing C++ bindings...")
        
        lua_binding_dir = Path("src/map/lua")
        if not lua_binding_dir.exists():
            return
        
        for cpp_file in lua_binding_dir.glob("*.cpp"):
            self._analyze_binding_file(cpp_file)
    
    def _analyze_binding_file(self, file_path: Path) -> None:
        """Analyze a C++ binding file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find SOL_USERTYPE declarations
            usertype_matches = re.finditer(
                r'SOL_USERTYPE\s*\(\s*"([^"]+)"\s*,\s*(\w+)\s*\)',
                content
            )
            
            for match in usertype_matches:
                lua_name = match.group(1)
                cpp_class = match.group(2)
                
                # Find all SOL_REGISTER calls for this binding
                register_pattern = rf'SOL_REGISTER\s*\(\s*"([^"]+)"\s*,\s*{re.escape(cpp_class)}::(\w+)\s*\)'
                register_matches = re.finditer(register_pattern, content)
                
                functions = []
                for reg_match in register_matches:
                    lua_func_name = reg_match.group(1)
                    cpp_method_name = reg_match.group(2)
                    functions.append(f"{lua_func_name} -> {cpp_method_name}")
                
                # Extract description from comments
                description = self._extract_cpp_description(content, match.start())
                
                binding = LuaBinding(
                    lua_name=lua_name,
                    cpp_class=cpp_class,
                    cpp_file=str(file_path),
                    functions=functions,
                    description=description
                )
                
                self.bindings.append(binding)
                
                # Update function cross-references
                for func in self.functions:
                    if func.name.startswith(lua_name + '.') or func.name.startswith(lua_name + ':'):
                        func.lua_binding = lua_name
                        func.cpp_source = str(file_path)
                        
        except Exception as e:
            print(f"⚠️ Error analyzing binding file {file_path}: {e}")
    
    def _extract_cpp_description(self, content: str, position: int) -> str:
        """Extract description from C++ comments."""
        lines = content[:position].split('\n')
        description_lines = []
        
        # Look backwards for comment lines
        for line in reversed(lines[-10:]):  # Check last 10 lines
            line = line.strip()
            if line.startswith('//'):
                desc_line = re.sub(r'^//+\s*', '', line).strip()
                if desc_line:
                    description_lines.insert(0, desc_line)
            elif line.startswith('/*') or line.startswith('*'):
                desc_line = re.sub(r'^/?\*+\s*', '', line).strip()
                desc_line = re.sub(r'\*/$', '', desc_line).strip()
                if desc_line:
                    description_lines.insert(0, desc_line)
            elif line and not line.startswith('//'):
                break
        
        return ' '.join(description_lines)
    
    def _build_cross_references(self) -> None:
        """Build cross-references between functions."""
        print("🔗 Building cross-references...")
        
        # Build function name index
        func_names = {func.name for func in self.functions}
        
        # For each function, find references to other functions
        for func in self.functions:
            if func.name not in self.function_refs:
                self.function_refs[func.name] = set()
            
            try:
                with open(func.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Find function calls in the content
                for other_name in func_names:
                    if other_name != func.name and other_name in content:
                        self.function_refs[func.name].add(other_name)
            
            except Exception:
                continue
    
    def generate_documentation(self) -> None:
        """Generate comprehensive Lua documentation."""
        print("📝 Generating Lua catalog documentation...")
        
        self._generate_main_catalog()
        self._generate_category_pages()
        self._generate_binding_documentation()
        self._generate_cross_reference_index()
        self._generate_json_data()
        
        print(f"📚 Lua catalog generated in: {self.output_dir}")
    
    def _generate_main_catalog(self) -> None:
        """Generate the main catalog index."""
        catalog_path = self.output_dir / "index.md"
        
        with open(catalog_path, 'w') as f:
            f.write("# Lua Function Catalog\n\n")
            f.write(f"Comprehensive documentation for LandSandBoat Lua scripts.\n\n")
            
            # Statistics
            f.write("## Statistics\n\n")
            f.write(f"- **Functions**: {len(self.functions)}\n")
            f.write(f"- **Global Variables**: {len(self.globals)}\n")
            f.write(f"- **C++ Bindings**: {len(self.bindings)}\n")
            f.write(f"- **Files Analyzed**: {len(self.file_functions)}\n\n")
            
            # Categories
            f.write("## Categories\n\n")
            category_counts = {}
            for func in self.functions:
                category_counts[func.category] = category_counts.get(func.category, 0) + 1
            
            for category, count in sorted(category_counts.items()):
                category_title = self.categories.get(category, category.title())
                f.write(f"- [{category_title}]({category}.md) ({count} functions)\n")
            
            f.write("\n## Special Documentation\n\n")
            f.write("- [C++ Bindings](bindings.md) - C++ to Lua interface documentation\n")
            f.write("- [Cross-References](cross_references.md) - Function call relationships\n")
            f.write("- [Global Variables](globals.md) - Global tables and variables\n\n")
    
    def _generate_category_pages(self) -> None:
        """Generate documentation pages for each category."""
        # Group functions by category
        by_category = {}
        for func in self.functions:
            if func.category not in by_category:
                by_category[func.category] = []
            by_category[func.category].append(func)
        
        # Generate page for each category
        for category, functions in by_category.items():
            category_path = self.output_dir / f"{category}.md"
            category_title = self.categories.get(category, category.title())
            
            with open(category_path, 'w') as f:
                f.write(f"# {category_title} Functions\n\n")
                
                # Group by subcategory
                by_subcategory = {}
                for func in functions:
                    subcat = func.subcategory or "General"
                    if subcat not in by_subcategory:
                        by_subcategory[subcat] = []
                    by_subcategory[subcat].append(func)
                
                for subcategory, subfuncs in sorted(by_subcategory.items()):
                    if len(by_subcategory) > 1:
                        f.write(f"## {subcategory}\n\n")
                    
                    for func in sorted(subfuncs, key=lambda x: x.name):
                        f.write(f"### {func.name}\n\n")
                        f.write(f"**File**: `{func.file_path}:{func.line_number}`\n\n")
                        
                        if func.parameters:
                            f.write(f"**Parameters**: `{', '.join(func.parameters)}`\n\n")
                        
                        if func.description:
                            f.write(f"**Description**: {func.description}\n\n")
                        
                        if func.lua_binding:
                            f.write(f"**C++ Binding**: {func.lua_binding}\n\n")
                        
                        if func.examples:
                            f.write("**Examples**:\n")
                            for example in func.examples:
                                f.write(f"```lua\n{example}\n```\n\n")
                        
                        # Cross-references
                        if func.name in self.function_refs and self.function_refs[func.name]:
                            refs = sorted(list(self.function_refs[func.name]))
                            f.write(f"**Calls**: {', '.join(refs[:5])}")
                            if len(refs) > 5:
                                f.write(f" (and {len(refs) - 5} more)")
                            f.write("\n\n")
    
    def _generate_binding_documentation(self) -> None:
        """Generate C++ binding documentation."""
        bindings_path = self.output_dir / "bindings.md"
        
        with open(bindings_path, 'w') as f:
            f.write("# C++ to Lua Bindings\n\n")
            f.write("Documentation for C++ classes exposed to Lua.\n\n")
            
            for binding in sorted(self.bindings, key=lambda x: x.lua_name):
                f.write(f"## {binding.lua_name}\n\n")
                f.write(f"**C++ Class**: `{binding.cpp_class}`\n\n")
                f.write(f"**Source File**: `{binding.cpp_file}`\n\n")
                
                if binding.description:
                    f.write(f"**Description**: {binding.description}\n\n")
                
                if binding.functions:
                    f.write("**Available Functions**:\n\n")
                    for func_mapping in sorted(binding.functions):
                        f.write(f"- `{func_mapping}`\n")
                    f.write("\n")
    
    def _generate_cross_reference_index(self) -> None:
        """Generate cross-reference index."""
        cross_ref_path = self.output_dir / "cross_references.md"
        
        with open(cross_ref_path, 'w') as f:
            f.write("# Function Cross-References\n\n")
            f.write("This page shows relationships between Lua functions.\n\n")
            
            for func_name, refs in sorted(self.function_refs.items()):
                if refs:
                    f.write(f"## {func_name}\n\n")
                    f.write("**Calls**:\n")
                    for ref in sorted(refs):
                        f.write(f"- {ref}\n")
                    f.write("\n")
    
    def _generate_json_data(self) -> None:
        """Generate JSON data for API consumption."""
        json_dir = self.output_dir / "json"
        json_dir.mkdir(exist_ok=True)
        
        data = {
            'functions': [asdict(func) for func in self.functions],
            'globals': [asdict(global_var) for global_var in self.globals],
            'bindings': [asdict(binding) for binding in self.bindings],
            'cross_references': {k: list(v) for k, v in self.function_refs.items()},
            'categories': self.categories
        }
        
        with open(json_dir / "lua_catalog.json", 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate(self) -> None:
        """Main method to generate the Lua catalog."""
        self.analyze_lua_scripts()
        self.generate_documentation()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Lua function catalog")
    parser.add_argument("--scripts-dir", default="scripts", help="Scripts directory to analyze")
    parser.add_argument("--output-dir", default="documentation/lua_catalog", help="Output directory")
    
    args = parser.parse_args()
    
    generator = LuaCatalogGenerator(args.scripts_dir, args.output_dir)
    generator.generate()


if __name__ == "__main__":
    main()