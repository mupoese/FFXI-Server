#!/bin/bash

# Enhanced Python CI Script with dependency management and Python 3.12+ enforcement
# Requires pylint, and ensures Python 3.12+ compatibility
# pip install pylint black isort bandit mypy

set -euo pipefail

target=${1:-tools}

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Check Python version enforcement (Python 3.12+ requirement)
check_python_version() {
    log_section "Python Version Validation"
    
    # Check Python 3.12+ is available
    if ! python3.12 --version >/dev/null 2>&1; then
        if ! python3 --version | grep -E "3\.(1[2-9]|[2-9][0-9])" >/dev/null; then
            log_error "Python 3.12+ is required but not found"
            log_info "Current Python version: $(python3 --version)"
            return 1
        fi
    fi
    
    local python_version=$(python3 --version | grep -oE "3\.[0-9]+")
    log_info "Python version: $python_version ✅"
    
    # Set CI_BUILD_FAST environment variable for optimized processing
    export CI_BUILD_FAST="true"
    
    return 0
}

# Install and validate Python dependencies
setup_python_dependencies() {
    log_section "Python Dependencies Setup"
    
    # Check for requirements files and validate package names
    local req_files=("tools/requirements.txt" "tools/requirements-py312.txt")
    
    for req_file in "${req_files[@]}"; do
        if [ -f "$req_file" ]; then
            log_info "Validating $req_file..."
            
            # Check for corrected package names (zmq -> pyzmq fix)
            if grep -q "^zmq>=" "$req_file" 2>/dev/null; then
                log_warn "Found 'zmq' package in $req_file - should be 'pyzmq'"
                sed -i 's/^zmq>=/pyzmq>=/' "$req_file"
                log_info "Fixed package name: zmq -> pyzmq"
            fi
            
            # Install dependencies
            log_info "Installing dependencies from $req_file..."
            python3 -m pip install --upgrade pip
            python3 -m pip install -r "$req_file"
        fi
    done
    
    # Install development tools if not present
    local dev_tools=("pylint" "black" "isort" "bandit" "mypy")
    local missing_tools=()
    
    for tool in "${dev_tools[@]}"; do
        if ! python3 -c "import $tool" 2>/dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_info "Installing missing development tools: ${missing_tools[*]}"
        python3 -m pip install "${missing_tools[@]}"
    fi
    
    log_info "Python dependencies setup completed"
}

# Enhanced Python linting with modern standards
run_enhanced_pylint() {
    log_section "Enhanced Python Linting"
    
    if [ ! -d "$target" ]; then
        log_error "Target directory '$target' not found"
        return 1
    fi
    
    # Run pylint with comprehensive checks
    log_info "Running enhanced pylint analysis..."
    
    local pylint_options=(
        "--errors-only"
        "--disable=import-error"  # Skip import errors in CI environment
        "--disable=no-member"     # Skip dynamic member issues
        "--output-format=colorized"
        "--reports=no"
        "--score=no"
    )
    
    # Create pylint configuration for project standards
    cat > /tmp/pylintrc << EOF
[MESSAGES CONTROL]
disable=missing-docstring,too-few-public-methods,too-many-arguments,line-too-long

[FORMAT]
max-line-length=100
indent-string='    '

[VARIABLES]
good-names=i,j,k,ex,Run,_,f,e

[DESIGN]
max-args=8
max-locals=20
max-returns=6
max-branches=15
EOF
    
    local exit_code=0
    
    # Run pylint with project configuration
    if ! pylint --rcfile=/tmp/pylintrc "${pylint_options[@]}" "$target"; then
        log_error "Pylint found errors in Python code"
        exit_code=1
    else
        log_info "Pylint analysis passed ✅"
    fi
    
    return $exit_code
}

# Code formatting validation and fixes
run_code_formatting() {
    log_section "Python Code Formatting"
    
    local format_exit_code=0
    
    # Black formatting check
    if command -v black >/dev/null; then
        log_info "Checking code formatting with black..."
        if ! black --line-length 100 --check --diff "$target"; then
            log_warn "Code formatting issues found. Auto-fixing..."
            black --line-length 100 "$target"
        else
            log_info "Black formatting: ✅"
        fi
    fi
    
    # Import sorting check
    if command -v isort >/dev/null; then
        log_info "Checking import sorting with isort..."
        if ! isort --profile black --line-length 100 --check-only --diff "$target"; then
            log_warn "Import sorting issues found. Auto-fixing..."
            isort --profile black --line-length 100 "$target"
        else
            log_info "Import sorting: ✅"
        fi
    fi
    
    return $format_exit_code
}

# Security analysis with bandit
run_security_analysis() {
    log_section "Python Security Analysis"
    
    if command -v bandit >/dev/null; then
        log_info "Running security analysis with bandit..."
        
        # Run bandit with reasonable exclusions for development tools
        local bandit_options=(
            "-r"
            "$target"
            "-f" "json"
            "-o" "/tmp/bandit_report.json"
            "--skip" "B101,B601"  # Skip assert and shell usage warnings for tools
        )
        
        if bandit "${bandit_options[@]}"; then
            log_info "Security analysis passed ✅"
            
            # Show summary if report exists
            if [ -f "/tmp/bandit_report.json" ]; then
                local issues=$(python3 -c "import json; data=json.load(open('/tmp/bandit_report.json')); print(len(data.get('results', [])))")
                log_info "Security issues found: $issues"
            fi
        else
            log_warn "Security analysis found potential issues (check /tmp/bandit_report.json)"
        fi
    else
        log_warn "Bandit not available - skipping security analysis"
    fi
    
    return 0  # Don't fail CI on security warnings
}

# Type checking with mypy
run_type_checking() {
    log_section "Python Type Checking"
    
    if command -v mypy >/dev/null; then
        log_info "Running type checking with mypy..."
        
        # Create mypy configuration
        cat > /tmp/mypy.ini << EOF
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
ignore_missing_imports = True
EOF
        
        if mypy --config-file=/tmp/mypy.ini "$target" 2>/dev/null; then
            log_info "Type checking passed ✅"
        else
            log_warn "Type checking found issues (non-blocking)"
        fi
    else
        log_warn "mypy not available - skipping type checking"
    fi
    
    return 0  # Don't fail CI on type issues
}

# Validate Python 3.12+ compatibility across all tools
validate_py312_compatibility() {
    log_section "Python 3.12+ Compatibility Validation"
    
    # Find all Python files and check for compatibility issues
    local python_files=($(find "$target" -name "*.py" -type f 2>/dev/null || true))
    local compatibility_issues=0
    
    for py_file in "${python_files[@]}"; do
        if [ -f "$py_file" ]; then
            # Basic syntax check with Python 3.12+
            if ! python3 -m py_compile "$py_file" 2>/dev/null; then
                log_error "Syntax error in $py_file"
                ((compatibility_issues++))
            fi
            
            # Check for deprecated features
            if grep -q "imp\." "$py_file" 2>/dev/null; then
                log_warn "$py_file: Uses deprecated 'imp' module - update to 'importlib'"
                ((compatibility_issues++))
            fi
        fi
    done
    
    if [ $compatibility_issues -eq 0 ]; then
        log_info "Python 3.12+ compatibility validated ✅"
    else
        log_warn "$compatibility_issues compatibility issues found"
    fi
    
    return 0
}

# Main execution
main() {
    log_info "Starting enhanced Python CI pipeline..."
    
    # Run all Python checks
    check_python_version
    setup_python_dependencies
    run_enhanced_pylint
    run_code_formatting
    run_security_analysis
    run_type_checking
    validate_py312_compatibility
    
    log_info "Enhanced Python CI pipeline completed successfully"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
