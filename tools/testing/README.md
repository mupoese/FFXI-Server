# Testing Tools

This directory contains testing frameworks, validation suites, and system testing tools.

## Tools

### System Testing
- `docker_system_test.py` - Docker system validation (moved from docker/scripts/)
- `docker_test_suite.py` - Comprehensive Docker testing
- `system_test_report.py` - System testing reports (moved from root)

### Database Testing  
- `test_database_setup.py` - Database setup testing (moved from root)

### Network Testing
- `network_bonding_manager.py` - Network bonding management
- `network_bonding_test_runner.py` - Network bonding test execution
- `network_bonding_test_suite.py` - Comprehensive network bonding tests

## Usage

### Docker Testing
```bash
python docker_test_suite.py
python docker_system_test.py
```

### Database Testing
```bash
python test_database_setup.py
```

### Network Bonding Testing
```bash
python network_bonding_test_suite.py
python network_bonding_test_runner.py
```

### System Reports
```bash
python system_test_report.py
```

## Integration

Testing tools integrate with:
- CI/CD pipelines for automated testing
- Docker infrastructure for container validation
- Network bonding systems for connectivity testing
- Database systems for data integrity validation

## Output

Testing tools generate:
- Test reports in `../../docs/reports/`
- System validation results
- Performance benchmarks
- Integration test results