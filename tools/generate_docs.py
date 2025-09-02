#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Function Indexing System - Main Orchestrator

This script coordinates all documentation generators to create a comprehensive
Function Indexing System for the LandSandBoat server.

Usage: python3 generate_docs.py [--component COMPONENT] [--output-dir OUTPUT_DIR]
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


class DocumentationOrchestrator:
    """Main orchestrator for the Function Indexing System."""
    
    def __init__(self, output_dir: str = "documentation/function_index"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Component generators
        self.generators = {
            'cpp': 'tools/generate_cpp_docs.py',
            'lua': 'tools/generate_lua_catalog.py', 
            'python': 'tools/generate_function_index.py',
            'sql': 'tools/generate_sql_docs.py',
            'main': 'tools/generate_function_index.py'
        }
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        print("🔍 Checking dependencies...")
        
        required_commands = ['python3', 'git']
        missing = []
        
        for cmd in required_commands:
            result = subprocess.run(['which', cmd], capture_output=True)
            if result.returncode != 0:
                missing.append(cmd)
        
        if missing:
            print(f"❌ Missing required commands: {', '.join(missing)}")
            return False
        
        print("✅ All dependencies available")
        return True
    
    def generate_component(self, component: str) -> bool:
        """Generate documentation for a specific component."""
        if component not in self.generators:
            print(f"❌ Unknown component: {component}")
            return False
        
        generator_script = self.generators[component]
        
        if not Path(generator_script).exists():
            print(f"❌ Generator script not found: {generator_script}")
            return False
        
        print(f"🔨 Generating {component} documentation...")
        
        try:
            # Set up component-specific output directories
            if component == 'cpp':
                output_arg = f"--output-dir={self.output_dir}/cpp_api"
            elif component == 'lua':
                output_arg = f"--output-dir={self.output_dir}/lua_catalog"
            elif component == 'sql':
                output_arg = f"--output-dir={self.output_dir}/sql_schema"
            elif component == 'python':
                output_arg = f"--output-dir={self.output_dir}/python_api"
            else:
                output_arg = f"--output-dir={self.output_dir}"
            
            # Run the generator
            cmd = ['python3', generator_script]
            if component != 'main':
                cmd.append(output_arg)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to generate {component} documentation:")
                print(result.stderr)
                return False
            
            print(f"✅ {component.upper()} documentation generated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error generating {component} documentation: {e}")
            return False
    
    def generate_all(self) -> bool:
        """Generate documentation for all components."""
        print("🚀 Starting Function Indexing System generation...")
        
        if not self.check_dependencies():
            return False
        
        # Order of generation is important for cross-references
        components = ['cpp', 'lua', 'sql', 'main']
        failed_components = []
        
        for component in components:
            if not self.generate_component(component):
                failed_components.append(component)
        
        # Generate the main index page
        self._generate_main_index()
        
        if failed_components:
            print(f"⚠️ Some components failed: {', '.join(failed_components)}")
            return False
        
        print(f"🎉 Function Indexing System generated successfully!")
        print(f"📚 Documentation available at: {self.output_dir}/index.html")
        return True
    
    def _generate_main_index(self) -> None:
        """Generate the main index page that ties everything together."""
        index_path = self.output_dir / "index.html"
        
        # Get statistics
        stats = self._collect_statistics()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LandSandBoat Function Index</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 300;
        }}
        
        .header p {{
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            display: block;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .components {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .component-card {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .component-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        
        .component-header {{
            padding: 1rem;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .component-title {{
            margin: 0;
            color: #495057;
            font-size: 1.2rem;
        }}
        
        .component-content {{
            padding: 1rem;
        }}
        
        .component-description {{
            color: #666;
            margin-bottom: 1rem;
            font-size: 0.95rem;
        }}
        
        .component-links {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .component-links li {{
            margin-bottom: 0.5rem;
        }}
        
        .component-links a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .component-links a:hover {{
            text-decoration: underline;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 3rem;
            padding: 2rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .timestamp {{
            color: #666;
            font-size: 0.9rem;
        }}
        
        .quick-search {{
            background: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .search-input {{
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #dee2e6;
            border-radius: 4px;
            font-size: 1rem;
        }}
        
        .search-input:focus {{
            outline: none;
            border-color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>LandSandBoat Function Index</h1>
        <p>Comprehensive documentation and cross-reference system</p>
    </div>
    
    <div class="quick-search">
        <input type="text" class="search-input" placeholder="🔍 Search functions, classes, or tables..." id="searchInput">
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <span class="stat-number">{stats.get('cpp_classes', 0)}</span>
            <span class="stat-label">C++ Classes</span>
        </div>
        <div class="stat-card">
            <span class="stat-number">{stats.get('cpp_functions', 0)}</span>
            <span class="stat-label">C++ Functions</span>
        </div>
        <div class="stat-card">
            <span class="stat-number">{stats.get('lua_functions', 0)}</span>
            <span class="stat-label">Lua Functions</span>
        </div>
        <div class="stat-card">
            <span class="stat-number">{stats.get('python_functions', 0)}</span>
            <span class="stat-label">Python Functions</span>
        </div>
        <div class="stat-card">
            <span class="stat-number">{stats.get('sql_tables', 0)}</span>
            <span class="stat-label">SQL Tables</span>
        </div>
        <div class="stat-card">
            <span class="stat-number">{stats.get('bindings', 0)}</span>
            <span class="stat-label">Lua Bindings</span>
        </div>
    </div>
    
    <div class="components">
        <div class="component-card">
            <div class="component-header">
                <h3 class="component-title">🔧 C++ API Documentation</h3>
            </div>
            <div class="component-content">
                <p class="component-description">
                    Comprehensive documentation for C++ classes, functions, and namespaces with inheritance diagrams and cross-references.
                </p>
                <ul class="component-links">
                    <li><a href="cpp_api/html/index.html">Browse API Documentation</a></li>
                    <li><a href="cpp_api/html/annotated.html">Class List</a></li>
                    <li><a href="cpp_api/html/hierarchy.html">Class Hierarchy</a></li>
                    <li><a href="cpp_api/html/namespaces.html">Namespaces</a></li>
                </ul>
            </div>
        </div>
        
        <div class="component-card">
            <div class="component-header">
                <h3 class="component-title">🌙 Lua Function Catalog</h3>
            </div>
            <div class="component-content">
                <p class="component-description">
                    Organized catalog of Lua functions with categories, cross-references, and C++ binding information.
                </p>
                <ul class="component-links">
                    <li><a href="lua_catalog/index.html">Function Catalog</a></li>
                    <li><a href="lua_catalog/bindings.html">C++ Bindings</a></li>
                    <li><a href="lua_catalog/cross_references.html">Cross-References</a></li>
                    <li><a href="lua_catalog/json/lua_catalog.json">JSON API</a></li>
                </ul>
            </div>
        </div>
        
        <div class="component-card">
            <div class="component-header">
                <h3 class="component-title">🐍 Python Tools API</h3>
            </div>
            <div class="component-content">
                <p class="component-description">
                    Documentation for all Python development tools, scripts, and utilities used in the project.
                </p>
                <ul class="component-links">
                    <li><a href="python_api.html">Python API Overview</a></li>
                    <li><a href="json/function_index.json">JSON Data</a></li>
                </ul>
            </div>
        </div>
        
        <div class="component-card">
            <div class="component-header">
                <h3 class="component-title">🗄️ SQL Schema Documentation</h3>
            </div>
            <div class="component-content">
                <p class="component-description">
                    Complete database schema documentation with table relationships, foreign keys, and data dictionary.
                </p>
                <ul class="component-links">
                    <li><a href="sql_schema/index.html">Schema Overview</a></li>
                    <li><a href="sql_schema/relationships.html">Table Relationships</a></li>
                    <li><a href="sql_schema/data_dictionary.html">Data Dictionary</a></li>
                    <li><a href="sql_schema/json/schema.json">JSON Schema</a></li>
                </ul>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p class="timestamp">
            Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}
        </p>
        <p>
            <a href="https://github.com/LandSandBoat/server">LandSandBoat Server</a> | 
            <a href="../README.md">Documentation Index</a>
        </p>
    </div>
    
    <script>
        // Simple search functionality
        document.getElementById('searchInput').addEventListener('input', function(e) {{
            const searchTerm = e.target.value.toLowerCase();
            // This would be enhanced with actual search functionality
            console.log('Searching for:', searchTerm);
        }});
    </script>
</body>
</html>
"""
        
        with open(index_path, 'w') as f:
            f.write(html_content)
        
        # Also create a markdown version
        md_path = self.output_dir / "index.md"
        with open(md_path, 'w') as f:
            f.write("# LandSandBoat Function Index\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Components\n\n")
            f.write("- [C++ API Documentation](cpp_api/html/index.html)\n")
            f.write("- [Lua Function Catalog](lua_catalog/index.md)\n")
            f.write("- [Python Tools API](python_api.md)\n")
            f.write("- [SQL Schema Documentation](sql_schema/index.md)\n\n")
            
            f.write("## Statistics\n\n")
            for key, value in stats.items():
                f.write(f"- **{key.replace('_', ' ').title()}**: {value}\n")
    
    def _collect_statistics(self) -> dict:
        """Collect statistics from generated documentation."""
        stats = {
            'cpp_classes': 0,
            'cpp_functions': 0,
            'lua_functions': 0,
            'python_functions': 0,
            'sql_tables': 0,
            'bindings': 0
        }
        
        # Try to read JSON data files for accurate counts
        try:
            import json
            
            # Main function index JSON
            main_json = self.output_dir / "json" / "function_index.json"
            if main_json.exists():
                with open(main_json) as f:
                    data = json.load(f)
                    stats['cpp_classes'] = len(data.get('cpp_classes', []))
                    stats['cpp_functions'] = len(data.get('cpp_functions', []))
                    stats['bindings'] = len(data.get('cpp_to_lua_bindings', {}))
            
            # Lua catalog JSON
            lua_json = self.output_dir / "lua_catalog" / "json" / "lua_catalog.json"
            if lua_json.exists():
                with open(lua_json) as f:
                    data = json.load(f)
                    stats['lua_functions'] = len(data.get('functions', []))
            
            # SQL schema JSON
            sql_json = self.output_dir / "sql_schema" / "json" / "schema.json"
            if sql_json.exists():
                with open(sql_json) as f:
                    data = json.load(f)
                    stats['sql_tables'] = len(data.get('tables', {}))
        
        except Exception:
            # If JSON reading fails, use fallback estimates
            pass
        
        return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate Function Indexing System documentation")
    parser.add_argument(
        "--component",
        choices=['cpp', 'lua', 'python', 'sql', 'all'],
        default='all',
        help="Component to generate (default: all)"
    )
    parser.add_argument(
        "--output-dir",
        default="documentation/function_index",
        help="Output directory for generated documentation"
    )
    
    args = parser.parse_args()
    
    orchestrator = DocumentationOrchestrator(args.output_dir)
    
    if args.component == 'all':
        success = orchestrator.generate_all()
    else:
        success = orchestrator.generate_component(args.component)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())