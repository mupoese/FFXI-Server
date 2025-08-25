Tools
========================

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