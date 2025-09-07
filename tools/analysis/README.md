# Analysis and Validation Tools

This directory contains comprehensive analysis and validation tools for code quality, job systems, and overall server validation.

## Tools

### Job Analysis
- `job_completeness_analyzer.py` - Complete job system analysis (moved from root)
- `job_system_validator.py` - Job system validation and testing
- `combat_system_validator.py` - Combat mechanics validation

### Comprehensive Validators  
- `comprehensive_iteration_validator.py` - Full iteration validation
- `comprehensive_job_validator.py` - Complete job system validation
- `comprehensive_security_test.py` - Security testing and validation

### Code Analysis
- `modern_cpp20_analyzer.py` - C++20 modernization analysis
- `quality_metrics_dashboard.py` - Real-time quality metrics
- `enhanced_content_validator.py` - FFXI content validation

## Usage

### Job Completeness Analysis
```bash
python job_completeness_analyzer.py
```

### Security Validation
```bash
python comprehensive_security_test.py
```

### Quality Metrics Dashboard
```bash
python quality_metrics_dashboard.py
# Access at http://localhost:8081
```

## Output

Analysis tools generate reports in:
- `../../docs/reports/` - Detailed analysis reports
- `../../docs/analysis/` - Analysis summaries
- Local JSON files for programmatic access

## Integration

These tools integrate with the CI/CD pipeline and can be run as part of automated quality checks.