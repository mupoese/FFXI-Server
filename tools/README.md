# 🛠️ FFXI-Server Tools Directory

**Last Updated**: September 2024 - Complete Reorganization  
**Status**: ✅ **ORGANIZED** - All tools properly categorized

## 🗂️ Organized Tool Structure

The tools directory has been completely reorganized into specialized subdirectories for better maintainability, discoverability, and development workflow integration.

### 📁 Directory Structure

```
tools/
├── admin/              # Administration and management tools (8 files)
├── analysis/           # Analysis and validation tools (11 files) ← Enhanced
├── database/           # Database tools and utilities (5 files)
├── development/        # Development productivity and code generation (17 files)
├── launchers/          # Game launcher and client management (5 files)
├── monitoring/         # Performance monitoring and profiling (5 files)
├── streaming/          # Streaming and asset management (8 files)
├── testing/            # Testing frameworks and validation (11 files)
├── ai-gm/             # AI-GM system tools (11 files) - moved from root
├── ci/                # CI/CD and build tools
├── migrations/        # Database migration scripts
└── manual/            # Manual testing and debugging tools
```

## 🎯 Priority 1: Job Completeness Tools

### 📊 Job Analysis and Validation
```bash
# Primary job completeness analysis
python analysis/job_completeness_analyzer.py

# Repository organization validation  
python analysis/repository_organization_validator.py

# Job system validation
python analysis/job_system_validator.py
```

### 🏗️ Development Tools for Job Implementation
```bash
# Function indexing for job utilities
python development/generate_function_index.py

# Documentation generation
python development/generate_docs.py

# Code quality validation
python development/python312_compatibility_checker.py
```
- **Server Announcements**: `python admin/announce.py "message"` - Broadcast messages

### Analysis and Quality
- **Job Completeness**: `python analysis/job_completeness_analyzer.py` - Job system analysis
- **Quality Metrics**: `python analysis/quality_metrics_dashboard.py` - Quality dashboard
- **Security Testing**: `python analysis/comprehensive_security_test.py` - Security validation

### Development Tools
- **Function Indexing**: `python development/generate_function_index.py` - Code analysis
- **Documentation**: `python development/generate_cpp_docs.py` - Generate docs
- **Changelog**: `python development/generate_changelog.py` - Version tracking

## Database Tool
`python dbtool.py`  
`python dbtool.py backup` - creates a whole database backup in `../sql/backups/`  
`python dbtool.py backup lite` - creates a backup only of tables defined in settings  
`python dbtool.py update` - performs an express update with backup and migrations if necessary  
`python dbtool.py update full` - performs a full update with backup and migrations  
`python dbtool.py migrate` - checks and performs any needed migrations

This tool creates or connects to the database defined in `../settings/network.lua`. It 
allows the user to backup or restore the database, import any `custom.sql` 
stored in `../sql/backups/`, and import the latest SQL files provided by LandSandBoat 
Development. This tool also handles data migrations for character data.

## Price Checker
`python price_checker.py`

This tool checks NPC and guild shop prices to see if anything is being sold for less than the buyback price.

## Festive Moogle Tool
`python give_items.py`

This tool is used to distribute the following items:  
- Nomad Cap  
- Moogle Cap  
- Moogle Rod  
- Harpsichord  
- Stuffed Chocobo  
- Tidal Talisman  
- Destrier Beret  
- Chocobo Shirt  

## Announce
`python announce.py "<your message>"`

Sends `<your message>` to every character, in every zone, on every map process.  

## Development and Quality Assurance Tools

### Vulnerability Scanner
`python vulnerability_scanner.py`

Comprehensive security scanning tool that checks for:
- Python package vulnerabilities (requires pip-audit)
- Node.js package security issues (npm audit)
- System package verification
- C++ code truncation issues
- Shell script validation (requires shellcheck)

Results are logged to development logs and summary reports are generated.

### Log Manager
`python log_manager.py [options]`

Development logging and file tracking system:
- `--scan` - Scan project for new files and update structure log
- `--cleanup` - Archive old log entries to prevent bloat
- `--report` - Generate summary reports of development activity
- `--validate` - Check log file integrity
- `--all` - Run complete maintenance cycle

Integrates with the Dutch SWE Agent methodology for enhanced development tracking.

### Development Workflow
`bash dev_workflow.sh [command]`

Integrated development workflow tool implementing Dutch SWE logic:
- `logic` - Display the 11-step SWE agent methodology
- `deps` - Check development dependencies
- `quality` - Run comprehensive quality assurance checks
- `build` - Build and test the project
- `logs` - Update and validate development logs
- `full` - Execute complete development workflow

## Code Generation and Formatting

### Function Indexing System
`python generate_docs.py [--component COMPONENT] [--output-dir OUTPUT_DIR]`

Comprehensive documentation generation system implementing the Function Indexing System from ROADMAP.md:
- **C++ API Documentation**: Automated Doxygen-based documentation with enhanced features
- **Lua Function Catalog**: Organized function catalog with cross-references and C++ bindings
- **Python Tools API**: Documentation for all development tools and scripts
- **SQL Schema Documentation**: Complete database schema with relationships and data dictionary

**Components**:
- `--component cpp` - Generate C++ API documentation using enhanced Doxygen
- `--component lua` - Generate Lua function catalog with cross-references
- `--component python` - Generate Python tools API documentation
- `--component sql` - Generate SQL schema documentation with relationships
- `--component all` - Generate all components (default)

**Individual Generators**:
- `python generate_cpp_docs.py` - Enhanced C++ documentation with Doxygen
- `python generate_lua_catalog.py` - Lua function catalog with cross-references
- `python generate_sql_docs.py` - SQL schema documentation with relationships
- `python generate_function_index.py` - Main function indexer and orchestrator

### Changelog Generator
`python generate_changelog.py <days|ci> <owner/repo> [title]`

Generates changelog from GitHub repository activity:
- `ci` mode for automated changelog generation
- Custom day ranges for specific periods
- Optional custom titles for server-specific changelogs

### IPC Stub Generator
`python generate_ipc_stubs.py`

Generates Inter-Process Communication stubs for server components.

Setup
========================

## Installing Python
`python3 --version` or `py -3 --version`

**This requires Python 3 and pip.**  
**Website:** https://www.python.org/downloads/  
Download the latest version from the website or check your package manager.

## Installing Dependencies
`pip install -r requirements.txt`

**MariaDB** - MariaDB is required to interact with the database.  
**GitPython** - GitPython is required to compare database versions.  
**PyYAML** - PyYAML is required to read/write settings.  
**Colorama** - Colorama is required to make colored terminal text.  
**zmq** - ZeroMQ is required for sending messages to the server.  
**Pylint** - Pylint is a static code analyser.  
**Black** - Black is a Python code formatter.  

## Development Tools Setup

For enhanced development workflow and quality assurance:

```bash
# Install security scanning tools
pip install pip-audit

# Install shell script validation
# Ubuntu/Debian:
sudo apt install shellcheck
# macOS:
brew install shellcheck

# Make development scripts executable
chmod +x vulnerability_scanner.py
chmod +x log_manager.py  
chmod +x dev_workflow.sh
```

## Other
`./install-systemd-service.sh` - Installs a systemd service for running the servers on Linux.  
`./run_clang_format.sh` - Formats C++ code. Run from repo root.  

## Development Logs

The `../logs/development/` directory contains comprehensive development tracking:
- File structure and organization logs
- Change tracking with hash verification
- Prompt logic and decision-making records
- Package and dependency monitoring
- Security vulnerability tracking

See `../logs/README.md` for detailed documentation of the logging system.  