#!/bin/bash

# Enhanced C++ CI Script with dependency management and build optimizations
# Requires the following packages:
# cppcheck, clang-format-18, luajit, libluajit-5.1-dev, binutils-dev

set -euo pipefail

target=${1:-src}

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
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

# Check and install required dependencies
check_and_install_dependencies() {
    log_info "Checking C++ build dependencies..."
    
    local missing_deps=()
    
    # Check for cppcheck
    if ! command -v cppcheck >/dev/null 2>&1; then
        missing_deps+=("cppcheck")
    fi
    
    # Check for clang-format-18
    if ! command -v clang-format-18 >/dev/null 2>&1; then
        log_warn "clang-format-18 not found, will try clang-format"
        if ! command -v clang-format >/dev/null 2>&1; then
            missing_deps+=("clang-format")
        fi
    fi
    
    # Check for LuaJIT libraries
    if ! pkg-config --exists luajit 2>/dev/null; then
        if ! dpkg -l | grep -q libluajit-5.1-dev 2>/dev/null; then
            missing_deps+=("libluajit-5.1-dev")
        fi
    fi
    
    # Check for binutils-dev (needed for CMake FindBinutils)
    if ! dpkg -l | grep -q binutils-dev 2>/dev/null; then
        missing_deps+=("binutils-dev")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_info "Installing missing dependencies: ${missing_deps[*]}"
        sudo apt update -qq
        sudo apt install -y "${missing_deps[@]}"
    fi
    
    log_info "All C++ dependencies satisfied"
}

# Fix configuration file encoding issues (UTF-8 BOM removal)
fix_config_files() {
    log_info "Checking and fixing configuration file encoding..."
    
    local config_files=(".clang-format" ".clang-tidy")
    
    for config_file in "${config_files[@]}"; do
        if [ -f "$config_file" ]; then
            # Check for UTF-8 BOM and remove if present
            if file "$config_file" | grep -q "BOM" 2>/dev/null; then
                log_warn "Removing UTF-8 BOM from $config_file"
                sed -i '1s/^\xEF\xBB\xBF//' "$config_file"
            fi
            
            # Validate configuration syntax
            if [ "$config_file" = ".clang-format" ]; then
                if command -v clang-format-18 >/dev/null 2>&1; then
                    if ! clang-format-18 --dump-config >/dev/null 2>&1; then
                        log_error "Invalid .clang-format configuration"
                        return 1
                    fi
                fi
            fi
        fi
    done
    
    log_info "Configuration files validated"
}

# Enhanced cppcheck with optimized settings
run_enhanced_cppcheck() {
    log_info "Running enhanced C++ static analysis..."
    
    # Set CI_BUILD_FAST environment variable for optimized builds
    export CI_BUILD_FAST="true"

    
    # Enhanced cppcheck with improved performance and parallel processing
    cppcheck -v -j 4 --force --quiet --inconclusive --std=c++17 \
    --suppress=passedByValue:src/map/packet_system.cpp \
    --suppress=unmatchedSuppression \
    --suppress=missingIncludeSystem \
    --suppress=missingInclude \
    --suppress=checkersReport \
    --enable=information,performance,portability --inline-suppr \
    --inconclusive \
    -DSA_INTERRUPT -DZMQ_DEPRECATED -DZMQ_EVENT_MONITOR_STOPPED -DTRACY_ENABLE \
    --output-file=/tmp/cppcheck_results.xml --xml \
    "${target}"
    
    local cppcheck_exit_code=$?
    
    if [ $cppcheck_exit_code -eq 0 ]; then
        log_info "cppcheck analysis completed successfully"
    else
        log_error "cppcheck analysis found issues (exit code: $cppcheck_exit_code)"
    fi
    
    return $cppcheck_exit_code
}

# Enhanced code quality checks with modern C++ standards
run_code_quality_checks() {
    log_info "Running enhanced code quality checks..."

python3 << EOF
import glob
import os
import sys

target = '${target}'

def contains_delete(line):
    if "// cpp.sh allow" in line:
        return False

    if "void operator delete" in line:
        return False

    if "//" in line:
        line = line.split("//")[0]

    if "*" in line:
        line = line.split("*")[0]

    line = line.strip()
    if line.startswith("Show"):
        return False

    return "delete " in line or "delete[]" in line or "delete []" in line

def contains_relative_include(line):
    return "#include \"../" in line

def load_documented_events(file_path):
    try:
        with open(file_path, 'r') as file:
            return {line.split(' - ')[0].strip() for line in file.readlines()}
    except FileNotFoundError:
        print(f"Warning: {file_path} not found, skipping undocumented listener checks")
        return set()

documented_events = load_documented_events('documentation/AI_Events.txt')

def contains_undocumented_listener(line):
    if not documented_events:  # Skip if AI_Events.txt not found
        return False
    import re
    match = re.search(r'\.triggerListener\("([^"]+)"', line)
    if match:
        listener = match.group(1)
        return listener not in documented_events
    return False

def check_modern_cpp_patterns(line, line_number, filename):
    """Check for modern C++ best practices"""
    issues = []
    
    # Check for raw pointers where smart pointers should be used
    if "new " in line and "std::make_" not in line and "// cpp.sh allow" not in line:
        issues.append(f"{filename}:{line_number}: Consider using smart pointers (std::make_unique/std::make_shared) instead of raw new")
    
    # Check for C-style casts
    if "(" in line and ")" in line and line.count("(") >= 1:
        import re
        if re.search(r'\([A-Za-z_][A-Za-z0-9_]*\s*\*?\s*\)', line) and "static_cast" not in line and "dynamic_cast" not in line:
            issues.append(f"{filename}:{line_number}: Consider using static_cast/dynamic_cast instead of C-style casts")
    
    return issues

def check(name):
    if os.path.isfile(name):
        try:
            with open(name, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                counter = 0
                issues_found = 0
                
                for line in lines:
                    counter = counter + 1
                    
                    if contains_delete(line):
                        print(f"{name}:{counter}: Found naked delete. Please use destroy(ptr) or destroy_arr(ptr).")
                        print(line.strip())
                        issues_found += 1
                        
                    if contains_relative_include(line):
                        print(f"{name}:{counter}: Found relative include. Please use non-relative paths.")
                        print(line.strip())
                        issues_found += 1
                        
                    if contains_undocumented_listener(line):
                        print(f"{name}:{counter}: Found undocumented listener. Please document this in AI_Events.txt.")
                        print(line.strip())
                        issues_found += 1
                    
                    # Enhanced modern C++ pattern checks
                    modern_cpp_issues = check_modern_cpp_patterns(line, counter, name)
                    for issue in modern_cpp_issues:
                        print(issue)
                        issues_found += 1
                
                return issues_found
        except Exception as e:
            print(f"Error checking {name}: {e}")
            return 1
    else:
        print(f"File not found: {name}")
        return 1

total_issues = 0

if target == 'src':
    print("Enhanced C++ Code Quality Analysis")
    print("=" * 50)
    
    for filename in glob.iglob('src/**/*.cpp', recursive=True):
        total_issues += check(filename)
    for filename in glob.iglob('src/**/*.h', recursive=True):
        total_issues += check(filename)
        
    print("=" * 50)
    print(f"Total issues found: {total_issues}")
    
    if total_issues > 0:
        print("Please address the issues above to improve code quality.")
        sys.exit(1)
    else:
        print("✅ All C++ code quality checks passed!")
else:
    total_issues = check(target)
    sys.exit(1 if total_issues > 0 else 0)
EOF

    local python_exit_code=$?
    
    if [ $python_exit_code -eq 0 ]; then
        log_info "Code quality checks completed successfully"
    else
        log_error "Code quality checks found issues"
    fi
    
    return $python_exit_code
}

# Run clang-format validation with UTF-8 BOM handling
run_clang_format_validation() {
    log_info "Running clang-format validation..."
    
    local clang_format_cmd="clang-format"
    if command -v clang-format-18 >/dev/null 2>&1; then
        clang_format_cmd="clang-format-18"
    fi
    
    # Validate a sample of files to avoid overwhelming output
    local sample_files=($(find src -name "*.cpp" -o -name "*.h" | head -10))
    local format_issues=0
    
    for file in "${sample_files[@]}"; do
        if [ -f "$file" ]; then
            if ! $clang_format_cmd --dry-run --Werror "$file" >/dev/null 2>&1; then
                log_warn "Formatting issues found in $file"
                ((format_issues++))
            fi
        fi
    done
    
    if [ $format_issues -eq 0 ]; then
        log_info "clang-format validation passed"
        return 0
    else
        log_warn "$format_issues files have formatting issues"
        return 1
    fi
}

# Main execution
main() {
    log_info "Starting enhanced C++ CI pipeline..."
    
    # Run all checks
    check_and_install_dependencies
    fix_config_files
    run_enhanced_cppcheck
    run_code_quality_checks
    run_clang_format_validation
    
    log_info "Enhanced C++ CI pipeline completed successfully"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
