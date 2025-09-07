# Database Tools

This directory contains database management, optimization, and testing tools.

## Tools

### Core Database Management
- `dbtool.py` - Main database tool for backup, restore, and migrations
- `database_ci_optimizations.py` - CI/CD database optimization
- `enhanced_database_test_suite.py` - Comprehensive database testing
- `db_optimization_summary.py` - Database performance optimization

### Testing and Validation  
- `test_database_improvements.py` - Database improvement testing

## Usage

### Database Tool
```bash
python dbtool.py                    # Interactive mode
python dbtool.py backup             # Create backup
python dbtool.py backup lite        # Lite backup
python dbtool.py update             # Express update
python dbtool.py update full        # Full update
python dbtool.py migrate            # Run migrations
```

### Database Testing
```bash
python enhanced_database_test_suite.py
```

### Optimization Analysis
```bash
python db_optimization_summary.py
```

## Configuration

Database tools use settings from:
- `../../settings/network.lua` - Database connection configuration
- `../../sql/backups/` - Backup storage directory

## Features

- Automated backup and restore
- Migration management  
- Performance optimization
- Custom SQL import support
- Data integrity validation