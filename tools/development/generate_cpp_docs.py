#!/usr/bin/env python3
"""
Enhanced C++ Documentation Generator using Doxygen

This tool extends the existing .doxygen configuration to generate comprehensive
C++ API documentation with additional features like cross-references and metrics.
"""

import os
import re
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Set, Optional


class DoxygenEnhancer:
    """Enhanced Doxygen documentation generator."""
    
    def __init__(self, source_dir: str = "src", output_dir: str = "documentation/cpp_api"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.doxygen_config = Path(".doxygen")
        self.temp_config = Path("doxygen_enhanced.conf")
        
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        try:
            # Check for doxygen
            result = subprocess.run(['which', 'doxygen'], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ Doxygen not found. Installing...")
                subprocess.run(['sudo', 'apt', 'update'], check=True)
                subprocess.run(['sudo', 'apt', 'install', '-y', 'doxygen', 'graphviz'], check=True)
            
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Doxygen dependencies")
            return False
        except FileNotFoundError:
            print("❌ Package manager not available")
            return False
    
    def create_enhanced_config(self) -> None:
        """Create an enhanced Doxygen configuration."""
        if not self.doxygen_config.exists():
            print("❌ Base .doxygen configuration not found")
            return
        
        # Read the base configuration
        with open(self.doxygen_config, 'r') as f:
            config_content = f.read()
        
        # Enhance the configuration
        enhancements = {
            'OUTPUT_DIRECTORY': str(self.output_dir),
            'EXTRACT_ALL': 'YES',
            'EXTRACT_PRIVATE': 'YES',
            'EXTRACT_STATIC': 'YES',
            'EXTRACT_LOCAL_CLASSES': 'YES',
            'EXTRACT_LOCAL_METHODS': 'YES',
            'EXTRACT_ANON_NSPACES': 'YES',
            'HIDE_UNDOC_MEMBERS': 'NO',
            'HIDE_UNDOC_CLASSES': 'NO',
            'HIDE_FRIEND_COMPOUNDS': 'NO',
            'HIDE_IN_BODY_DOCS': 'NO',
            'INTERNAL_DOCS': 'YES',
            'CASE_SENSE_NAMES': 'YES',
            'HIDE_SCOPE_NAMES': 'NO',
            'HIDE_COMPOUND_REFERENCE': 'NO',
            'SHOW_INCLUDE_FILES': 'YES',
            'SHOW_GROUPED_MEMB_INC': 'NO',
            'FORCE_LOCAL_INCLUDES': 'NO',
            'INLINE_INFO': 'YES',
            'SORT_MEMBER_DOCS': 'YES',
            'SORT_BRIEF_DOCS': 'NO',
            'SORT_MEMBERS_CTORS_1ST': 'NO',
            'SORT_GROUP_NAMES': 'NO',
            'SORT_BY_SCOPE_NAME': 'NO',
            'STRICT_PROTO_MATCHING': 'NO',
            'GENERATE_TODOLIST': 'YES',
            'GENERATE_TESTLIST': 'YES',
            'GENERATE_BUGLIST': 'YES',
            'GENERATE_DEPRECATEDLIST': 'YES',
            'GENERATE_HTML': 'YES',
            'HTML_OUTPUT': 'html',
            'HTML_FILE_EXTENSION': '.html',
            'HTML_HEADER': '',
            'HTML_FOOTER': '',
            'HTML_STYLESHEET': '',
            'HTML_EXTRA_STYLESHEET': '',
            'HTML_EXTRA_FILES': '',
            'HTML_COLORSTYLE_HUE': '220',
            'HTML_COLORSTYLE_SAT': '100',
            'HTML_COLORSTYLE_GAMMA': '80',
            'HTML_TIMESTAMP': 'YES',
            'HTML_DYNAMIC_SECTIONS': 'NO',
            'HTML_INDEX_NUM_ENTRIES': '100',
            'GENERATE_DOCSET': 'NO',
            'GENERATE_HTMLHELP': 'NO',
            'GENERATE_QHP': 'NO',
            'GENERATE_ECLIPSEHELP': 'NO',
            'DISABLE_INDEX': 'NO',
            'GENERATE_TREEVIEW': 'YES',
            'ENUM_VALUES_PER_LINE': '4',
            'TREEVIEW_WIDTH': '250',
            'EXT_LINKS_IN_WINDOW': 'NO',
            'FORMULA_FONTSIZE': '10',
            'FORMULA_TRANSPARENT': 'YES',
            'USE_MATHJAX': 'NO',
            'SEARCHENGINE': 'YES',
            'SERVER_BASED_SEARCH': 'NO',
            'EXTERNAL_SEARCH': 'NO',
            'SEARCHDATA_FILE': 'searchdata.xml',
            'GENERATE_LATEX': 'NO',
            'GENERATE_RTF': 'NO',
            'GENERATE_MAN': 'NO',
            'GENERATE_XML': 'YES',
            'XML_OUTPUT': 'xml',
            'XML_PROGRAMLISTING': 'YES',
            'GENERATE_DOCBOOK': 'NO',
            'GENERATE_AUTOGEN_DEF': 'NO',
            'GENERATE_PERLMOD': 'NO',
            'ENABLE_PREPROCESSING': 'YES',
            'MACRO_EXPANSION': 'YES',
            'EXPAND_ONLY_PREDEF': 'NO',
            'SEARCH_INCLUDES': 'YES',
            'INCLUDE_PATH': '',
            'INCLUDE_FILE_PATTERNS': '',
            'PREDEFINED': 'DOXYGEN_SHOULD_SKIP_THIS',
            'EXPAND_AS_DEFINED': '',
            'SKIP_FUNCTION_MACROS': 'YES',
            'TAGFILES': '',
            'GENERATE_TAGFILE': '',
            'ALLEXTERNALS': 'NO',
            'EXTERNAL_GROUPS': 'YES',
            'EXTERNAL_PAGES': 'YES',
            'PERL_PATH': '/usr/bin/perl',
            'CLASS_DIAGRAMS': 'YES',
            'MSCGEN_PATH': '',
            'DIA_PATH': '',
            'HIDE_UNDOC_RELATIONS': 'YES',
            'HAVE_DOT': 'YES',
            'DOT_NUM_THREADS': '0',
            'DOT_FONTNAME': 'Helvetica',
            'DOT_FONTSIZE': '10',
            'DOT_FONTPATH': '',
            'CLASS_GRAPH': 'YES',
            'COLLABORATION_GRAPH': 'YES',
            'GROUP_GRAPHS': 'YES',
            'UML_LOOK': 'NO',
            'UML_LIMIT_NUM_FIELDS': '10',
            'TEMPLATE_RELATIONS': 'NO',
            'INCLUDE_GRAPH': 'YES',
            'INCLUDED_BY_GRAPH': 'YES',
            'CALL_GRAPH': 'NO',
            'CALLER_GRAPH': 'NO',
            'GRAPHICAL_HIERARCHY': 'YES',
            'DIRECTORY_GRAPH': 'YES',
            'DOT_IMAGE_FORMAT': 'png',
            'INTERACTIVE_SVG': 'NO',
            'DOT_PATH': '',
            'DOTFILE_DIRS': '',
            'MSCFILE_DIRS': '',
            'DIAFILE_DIRS': '',
            'PLANTUML_JAR_PATH': '',
            'PLANTUML_CFG_FILE': '',
            'PLANTUML_INCLUDE_PATH': '',
            'DOT_GRAPH_MAX_NODES': '50',
            'MAX_DOT_GRAPH_DEPTH': '0',
            'DOT_TRANSPARENT': 'NO',
            'DOT_MULTI_TARGETS': 'NO',
            'GENERATE_LEGEND': 'YES',
            'DOT_CLEANUP': 'YES'
        }
        
        # Apply enhancements
        for key, value in enhancements.items():
            pattern = rf'^{key}\s*=.*$'
            replacement = f'{key} = {value}'
            config_content = re.sub(pattern, replacement, config_content, flags=re.MULTILINE)
            
            # If key doesn't exist, add it
            if not re.search(pattern, config_content, re.MULTILINE):
                config_content += f'\n{key} = {value}\n'
        
        # Write enhanced configuration
        with open(self.temp_config, 'w') as f:
            f.write(config_content)
    
    def generate_documentation(self) -> bool:
        """Generate the C++ documentation using Doxygen."""
        try:
            print("🔨 Generating C++ documentation with Doxygen...")
            
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Run Doxygen
            result = subprocess.run(
                ['doxygen', str(self.temp_config)],
                capture_output=True,
                text=True,
                cwd='.'
            )
            
            if result.returncode != 0:
                print(f"❌ Doxygen failed: {result.stderr}")
                return False
            
            print(f"✅ C++ documentation generated in: {self.output_dir}")
            
            # Clean up temporary config
            if self.temp_config.exists():
                self.temp_config.unlink()
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running Doxygen: {e}")
            return False
    
    def create_index_page(self) -> None:
        """Create a custom index page with additional navigation."""
        index_path = self.output_dir / "html" / "custom_index.html"
        
        if not index_path.parent.exists():
            return
        
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>LandSandBoat C++ API Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat-box { background: #ecf0f1; padding: 15px; border-radius: 5px; flex: 1; }
        .links { list-style: none; padding: 0; }
        .links li { margin: 10px 0; }
        .links a { text-decoration: none; color: #3498db; font-weight: bold; }
        .links a:hover { color: #2980b9; }
    </style>
</head>
<body>
    <div class="header">
        <h1>LandSandBoat C++ API Documentation</h1>
        <p>Comprehensive documentation for the C++ codebase</p>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <h3>Classes</h3>
            <p>Browse all C++ classes and their methods</p>
        </div>
        <div class="stat-box">
            <h3>Namespaces</h3>
            <p>Organized by functional areas</p>
        </div>
        <div class="stat-box">
            <h3>Files</h3>
            <p>Source and header file documentation</p>
        </div>
    </div>
    
    <h2>Quick Navigation</h2>
    <ul class="links">
        <li><a href="annotated.html">Class List</a> - All classes with brief descriptions</li>
        <li><a href="hierarchy.html">Class Hierarchy</a> - Inheritance relationships</li>
        <li><a href="namespaces.html">Namespace List</a> - Organized by namespace</li>
        <li><a href="files.html">File List</a> - All source and header files</li>
        <li><a href="functions.html">Function Index</a> - Alphabetical function listing</li>
        <li><a href="globals.html">Global Scope</a> - Global functions and variables</li>
    </ul>
    
    <h2>Key Components</h2>
    <ul class="links">
        <li><a href="namespace_db.html">Database Layer</a> - Database abstraction and utilities</li>
        <li><a href="namespace_settings.html">Settings System</a> - Configuration management</li>
        <li><a href="group__lua__bindings.html">Lua Bindings</a> - C++ to Lua interfaces</li>
    </ul>
    
    <p><a href="index.html">→ Go to Main Documentation</a></p>
</body>
</html>
"""
        
        with open(index_path, 'w') as f:
            f.write(html_content)
    
    def generate(self) -> bool:
        """Main method to generate enhanced C++ documentation."""
        print("🔍 Generating Enhanced C++ Documentation...")
        
        if not self.check_dependencies():
            return False
        
        self.create_enhanced_config()
        
        if not self.generate_documentation():
            return False
        
        self.create_index_page()
        
        print(f"📚 Enhanced C++ documentation available at: {self.output_dir}/html/index.html")
        return True


def main():
    """Main entry point for the enhanced C++ documentation generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate enhanced C++ documentation")
    parser.add_argument("--source-dir", default="src", help="Source directory to document")
    parser.add_argument("--output-dir", default="documentation/cpp_api", help="Output directory")
    
    args = parser.parse_args()
    
    enhancer = DoxygenEnhancer(args.source_dir, args.output_dir)
    success = enhancer.generate()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())