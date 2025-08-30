#!/usr/bin/env python3
"""
Integration test for the Function Indexing System.

This script validates that all components of the Function Indexing System
work correctly and produce the expected outputs.
"""

import os
import json
from pathlib import Path


def test_function_indexing_system():
    """Test the complete Function Indexing System."""
    print("🧪 Testing Function Indexing System...")
    
    base_dir = Path("documentation/function_index")
    
    # Test main files exist
    required_files = [
        "index.html",
        "index.md", 
        "cpp_api.md",
        "lua_catalog.md",
        "python_api.md",
        "sql_schema.md",
        "cross_references.md"
    ]
    
    missing_files = []
    for file_name in required_files:
        file_path = base_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    # Test directory structure
    required_dirs = [
        "cpp_api",
        "lua_catalog", 
        "sql_schema",
        "json"
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if not dir_path.exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ Missing required directories: {', '.join(missing_dirs)}")
        return False
    
    # Test JSON API files
    json_files = [
        "json/function_index.json"
    ]
    
    for json_file in json_files:
        json_path = base_dir / json_file
        if not json_path.exists():
            print(f"❌ Missing JSON file: {json_file}")
            return False
        
        try:
            with open(json_path) as f:
                data = json.load(f)
                print(f"✅ {json_file}: {len(data)} top-level keys")
        except Exception as e:
            print(f"❌ Invalid JSON in {json_file}: {e}")
            return False
    
    # Test C++ documentation
    cpp_html = base_dir / "cpp_api" / "html" / "index.html"
    if cpp_html.exists():
        print("✅ C++ HTML documentation generated")
    else:
        print("⚠️ C++ HTML documentation not found (Doxygen may not be available)")
    
    # Test Lua catalog
    lua_json = base_dir / "lua_catalog" / "json" / "lua_catalog.json"
    if lua_json.exists():
        try:
            with open(lua_json) as f:
                lua_data = json.load(f)
                print(f"✅ Lua catalog: {len(lua_data.get('functions', []))} functions, {len(lua_data.get('bindings', []))} bindings")
        except Exception as e:
            print(f"❌ Invalid Lua catalog JSON: {e}")
            return False
    
    # Test SQL schema
    sql_json = base_dir / "sql_schema" / "json" / "schema.json"
    if sql_json.exists():
        try:
            with open(sql_json) as f:
                sql_data = json.load(f)
                print(f"✅ SQL schema: {len(sql_data.get('tables', {}))} tables")
        except Exception as e:
            print(f"❌ Invalid SQL schema JSON: {e}")
            return False
    
    print("🎉 Function Indexing System test completed successfully!")
    return True


def print_statistics():
    """Print statistics about the generated documentation."""
    print("\n📊 Function Indexing System Statistics:")
    
    base_dir = Path("documentation/function_index")
    
    # Main JSON statistics
    main_json = base_dir / "json" / "function_index.json"
    if main_json.exists():
        try:
            with open(main_json) as f:
                data = json.load(f)
                print(f"   C++ Classes: {len(data.get('cpp_classes', []))}")
                print(f"   C++ Functions: {len(data.get('cpp_functions', []))}")
                print(f"   Python Functions: {len(data.get('python_functions', []))}")
                print(f"   C++ to Lua Bindings: {len(data.get('cpp_to_lua_bindings', {}))}")
        except Exception:
            pass
    
    # Lua catalog statistics
    lua_json = base_dir / "lua_catalog" / "json" / "lua_catalog.json"
    if lua_json.exists():
        try:
            with open(lua_json) as f:
                data = json.load(f)
                print(f"   Lua Functions: {len(data.get('functions', []))}")
                print(f"   Lua Globals: {len(data.get('globals', []))}")
                print(f"   Lua Bindings: {len(data.get('bindings', []))}")
        except Exception:
            pass
    
    # SQL schema statistics
    sql_json = base_dir / "sql_schema" / "json" / "schema.json"
    if sql_json.exists():
        try:
            with open(sql_json) as f:
                data = json.load(f)
                print(f"   SQL Tables: {len(data.get('tables', {}))}")
                print(f"   SQL Views: {len(data.get('views', {}))}")
                print(f"   SQL Procedures: {len(data.get('procedures', {}))}")
        except Exception:
            pass


if __name__ == "__main__":
    success = test_function_indexing_system()
    if success:
        print_statistics()
    exit(0 if success else 1)