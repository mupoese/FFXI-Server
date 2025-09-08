#!/bin/bash

# Enhanced General CI Script with comprehensive file validation and build optimizations
# Provides systematic validation of file formatting, encoding, and project standards

set -euo pipefail

target=${1:-.}

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

# Enhanced validation with modern standards and dependency checks
run_enhanced_validation() {
    log_section "Enhanced File Validation"
    
    # Set CI_BUILD_FAST environment variable for optimized processing
    export CI_BUILD_FAST="true"

    
python3 << EOF
import glob
import os
import sys
from pathlib import Path

target = '${target}'

class ValidationStats:
    def __init__(self):
        self.files_checked = 0
        self.issues_found = 0
        self.categories = {
            'newline': 0,
            'tabs': 0,
            'multiple_newlines': 0,
            'encoding': 0
        }
    
    def add_issue(self, category):
        self.issues_found += 1
        self.categories[category] += 1

stats = ValidationStats()

def check_file_encoding(filename):
    """Enhanced encoding validation with UTF-8 BOM detection"""
    try:
        # Check for UTF-8 BOM
        with open(filename, 'rb') as f:
            bom = f.read(3)
            if bom == b'\xef\xbb\xbf':
                print(f"{filename}: Contains UTF-8 BOM - consider removing for compatibility")
                stats.add_issue('encoding')
                return False
        return True
    except Exception as e:
        print(f"{filename}: Error checking encoding: {e}")
        stats.add_issue('encoding')
        return False

def validate_project_structure(filename):
    """Validate project-specific file organization"""
    path = Path(filename)
    
    # Check for proper include hierarchy
    if path.suffix in ['.h', '.hpp'] and 'src/' in str(path):
        if '../' in filename:
            print(f"{filename}: Header file uses relative paths - use absolute project paths")
            stats.add_issue('structure')
    
    # Check for proper namespace usage in headers
    if path.suffix == '.h' and path.stat().st_size > 1000:  # Only check larger headers
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'namespace' not in content and 'extern "C"' not in content:
                    print(f"{filename}: Large header file should consider using namespaces")
        except:
            pass

def check(name):
    """Enhanced file validation with comprehensive checks"""
    if not os.path.isfile(name):
        return
    
    stats.files_checked += 1
    
    # Check encoding first
    if not check_file_encoding(name):
        return
    
    # Validate project structure
    validate_project_structure(name)
    
    try:
        with open(name, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        counter = 0
        newline_counter = 0
        for data in lines:
            counter = counter + 1
            
            # Enhanced newline validation
            if not data.endswith('\n') and counter == len(lines):
                print(f"{name}: No newline at end of file, please add one.")
                stats.add_issue('newline')

            # Enhanced tab detection with context
            if "\t" in data:
                tab_count = data.count('\t')
                print(f"{name}:{counter}: Found {tab_count} tab character(s) in file, please replace these with 4x spaces.")
                stats.add_issue('tabs')

            # Enhanced multiple newline detection
            if data == "\n":
                newline_counter = newline_counter + 1
            else:
                newline_counter = 0

            if newline_counter > 1 or (counter == len(lines) and newline_counter == 1):
                print(f"{name}:{counter}: Found multiple newline characters next to each other, please replace these with single newlines.")
                stats.add_issue('multiple_newlines')
                
    except UnicodeDecodeError:
        print(f"{name}: File contains non-UTF-8 characters - please ensure UTF-8 encoding")
        stats.add_issue('encoding')
    except Exception as e:
        print(f"{name}: Error processing file: {e}")
        stats.add_issue('encoding')

def run_validation():
    """Run comprehensive validation based on target"""
    print("🔍 Enhanced File Validation Analysis")
    print("=" * 60)
    
    if target == '.':
        # Comprehensive project-wide validation
        file_patterns = [
            'scripts/**/*.lua',
            'src/**/*.cpp', 
            'src/**/*.h',
            'sql/**/*.sql',
            'tools/**/*.py',
            'cmake/**/*.cmake',
            'docs/**/*.md'
        ]
        
        for pattern in file_patterns:
            files = list(glob.iglob(pattern, recursive=True))
            for filename in files:
                check(filename)
                
        # Additional project-specific validations
        check_ipc_stubs_symlink()
        check_requirements_consistency()
        
    else:
        check(target)
    
    # Print comprehensive summary
    print("=" * 60)
    print(f"📊 Validation Summary:")
    print(f"   Files checked: {stats.files_checked}")
    print(f"   Total issues: {stats.issues_found}")
    
    if stats.issues_found > 0:
        print(f"   Issue breakdown:")
        for category, count in stats.categories.items():
            if count > 0:
                print(f"     - {category}: {count}")
        print()
        print("❌ File validation found issues. Please address them to maintain code quality.")
        sys.exit(1)
    else:
        print("✅ All file validation checks passed!")
        sys.exit(0)

def check_ipc_stubs_symlink():
    """Validate IPC stubs symlink exists (build system improvement)"""
    symlink_path = "tools/generate_ipc_stubs.py"
    target_path = "tools/development/generate_ipc_stubs.py"
    
    if os.path.exists(target_path):
        if not os.path.exists(symlink_path):
            print(f"Warning: IPC stubs symlink missing. Creating {symlink_path} -> {target_path}")
            try:
                os.symlink(target_path, symlink_path)
                print("✅ IPC stubs symlink created successfully")
            except Exception as e:
                print(f"❌ Failed to create IPC stubs symlink: {e}")
                stats.add_issue('structure')

def check_requirements_consistency():
    """Validate Python requirements file consistency"""
    req_files = ['tools/requirements.txt', 'tools/requirements-py312.txt']
    
    for req_file in req_files:
        if os.path.exists(req_file):
            try:
                with open(req_file, 'r') as f:
                    content = f.read()
                    
                # Check for corrected package names (build system improvements)
                if 'zmq>=' in content and 'pyzmq>=' not in content:
                    print(f"{req_file}: Found 'zmq' package - should be 'pyzmq'")
                    stats.add_issue('structure')
                    
            except Exception as e:
                print(f"Error checking {req_file}: {e}")

if __name__ == "__main__":
    run_validation()
EOF

    local python_exit_code=$?
    return $python_exit_code
}

# Check build system dependencies and create necessary symlinks
check_build_dependencies() {
    log_section "Build System Dependencies"
    
    # Check for LuaJIT installation
    if ! pkg-config --exists luajit 2>/dev/null; then
        log_warn "LuaJIT not found via pkg-config, checking dpkg..."
        if ! dpkg -l | grep -q libluajit-5.1-dev 2>/dev/null; then
            log_error "LuaJIT development libraries not installed"
            log_info "Install with: sudo apt install luajit libluajit-5.1-dev libluajit-5.1-2"
            return 1
        fi
    fi
    
    # Check for binutils-dev (needed for CMake FindBinutils)
    if ! dpkg -l | grep -q binutils-dev 2>/dev/null; then
        log_warn "binutils-dev not installed - needed for CMake configuration"
        log_info "Install with: sudo apt install binutils-dev"
        return 1
    fi
    
    # Ensure IPC stubs symlink exists
    if [ -f "tools/development/generate_ipc_stubs.py" ] && [ ! -L "tools/generate_ipc_stubs.py" ]; then
        log_info "Creating IPC stubs symlink for build system compatibility"
        ln -sf tools/development/generate_ipc_stubs.py tools/generate_ipc_stubs.py
    fi
    
    log_info "Build system dependencies validated"
    return 0
}

# Validate configuration files for UTF-8 BOM and syntax
validate_config_files() {
    log_section "Configuration File Validation"
    
    local config_files=(".clang-format" ".clang-tidy" ".editorconfig")
    local issues_found=0
    
    for config_file in "${config_files[@]}"; do
        if [ -f "$config_file" ]; then
            # Check for UTF-8 BOM
            if file "$config_file" | grep -q "BOM" 2>/dev/null; then
                log_warn "Removing UTF-8 BOM from $config_file"
                sed -i '1s/^\xEF\xBB\xBF//' "$config_file"
                ((issues_found++))
            fi
            
            # Check file is readable
            if [ ! -r "$config_file" ]; then
                log_error "$config_file is not readable"
                ((issues_found++))
            fi
        fi
    done
    
    if [ $issues_found -eq 0 ]; then
        log_info "All configuration files validated successfully"
    else
        log_warn "$issues_found configuration file issues were fixed"
    fi
    
    return 0
}

# Main execution
main() {
    log_info "Starting enhanced general CI validation..."
    
    # Run all validation steps
    check_build_dependencies
    validate_config_files
    run_enhanced_validation
    
    log_info "Enhanced general CI validation completed successfully"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
