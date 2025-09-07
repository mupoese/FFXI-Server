# Development Tools

This directory contains development productivity tools, code generation utilities, and documentation systems.

## Tools

### Function Indexing and Analysis
- `advanced_function_indexer.py` - Advanced function analysis with SQLite database
- `enhanced_function_indexer.py` - Enhanced function indexing with cross-references
- `generate_function_index.py` - Main function indexer and orchestrator

### Documentation Generation
- `generate_cpp_docs.py` - C++ code documentation generator
- `generate_sql_docs.py` - SQL schema documentation with relationships  
- `generate_docs.py` - General documentation generator
- `generate_lua_catalog.py` - Lua script catalog and documentation
- `generate_ipc_stubs.py` - IPC stub generation for communication
- `generate_changelog.py` - Automated changelog generation

### Productivity Suite
- `developer_productivity_suite.py` - Complete development productivity tools
- `dev_automation.py` - Development workflow automation

## Usage

### Function Indexing System
```bash
python generate_function_index.py
```

### Documentation Generation
```bash
python generate_cpp_docs.py
python generate_sql_docs.py
python generate_lua_catalog.py
```

### Changelog Generation
```bash
python generate_changelog.py --format=landsandboat
```

## Integration

Development tools integrate with:
- CI/CD pipelines for automated documentation
- Quality metrics for code analysis
- Build systems for development workflow

## Output

Generated documentation and analysis is stored in:
- `../../docs/` - Generated documentation
- `../../documentation/` - Technical documentation
- `function_index.db` - SQLite database of function analysis