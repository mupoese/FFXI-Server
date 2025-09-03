# GitHub Copilot Instructions for FFXI Server

<repository_context>
<project_description>
This repository is an open-source server emulator for Final Fantasy XI (FFXI), written primarily in C++ with Lua scripting support for game mechanics, database-driven content, and cross-platform deployment.
</project_description>

<key_technologies>
- **Primary Languages**: C++20, Lua 5.1, Python 3.12+, SQL (MariaDB)
- **Build System**: CMake 3.20+ with cross-platform support
- **Core Dependencies**: MariaDB, LuaJIT, ZeroMQ, spdlog, fmt, OpenSSL
- **Supported Platforms**: Linux (primary), Windows, macOS
- **CI/CD**: GitHub Actions with multi-platform validation
</key_technologies>

<mcp_integration_context>
This repository leverages Model Context Protocol (MCP) for enhanced tool integration and automated development workflows. All Copilot instructions are designed to work seamlessly with MCP tool calls for repository analysis, code generation, and workflow management.
</mcp_integration_context>
</repository_context>

<critical_workflow_analysis_framework>

<comprehensive_methodology>
**MANDATORY EXECUTION PROTOCOL**: Before addressing ANY development task, comment, or workflow issue, ALWAYS execute this comprehensive analysis methodology to prevent incomplete fixes and ensure systematic resolution.

<workflow_discovery_phase>
<complete_inventory_protocol>
- **Enumerate ALL Workflows**: Execute `find .github/workflows -name "*.yml" -o -name "*.yaml" | sort` to discover every workflow file
- **Categorize by Function**: Group workflows by purpose (build, test, security, deployment, maintenance)
- **Map Dependencies**: Identify workflow interdependencies and shared resources
- **Platform Matrix**: Document Windows/macOS/Linux coverage across all workflows
- **Trigger Analysis**: Catalog all trigger conditions (PR events, pushes, schedules, manual dispatch)
- **Workflow Documentation**: Create comprehensive inventory with purpose and scope for each workflow
</complete_inventory_protocol>

<mcp_workflow_analysis_tools>
Use these MCP tool calls for systematic workflow analysis:
```bash
# MCP-enabled workflow discovery
str_replace_editor view .github/workflows/
github-mcp-server-list_workflows owner repo

# Cross-platform analysis
bash "grep -r 'runs-on:' .github/workflows/ | sort | uniq -c"
bash "find .github/workflows -name '*.yml' -exec echo '=== {} ===' \; -exec cat {} \;"
```
</mcp_workflow_analysis_tools>
</workflow_discovery_phase>

<failure_analysis_phase>
<systematic_error_detection>
- **Multi-Workflow Pattern Analysis**: Identify failure patterns across ALL workflow files, not just the failing one
- **Root Cause Investigation**: Use MCP tools to trace underlying causes beyond surface symptoms  
- **Platform-Specific Diagnosis**: Analyze platform-specific failures (Windows vs Linux vs macOS)
- **Dependency Chain Analysis**: Map package dependencies and version conflicts across all platforms
- **Configuration Validation**: Check CodeQL, clang-format, and other tool configurations for conflicts
- **Resource Constraint Analysis**: Identify build timeouts, memory issues, and performance bottlenecks
</systematic_error_detection>

<mcp_error_analysis_commands>
```bash
# Systematic error pattern detection
bash "grep -r 'python-version' .github/workflows/ | grep -v '3.12'"
bash "for file in .github/workflows/*.yml; do echo 'Validating $file...'; python3 -c 'import yaml; yaml.safe_load(open(\"$file\"))' || echo 'SYNTAX ERROR in $file'; done"

# Cross-platform consistency validation
github-mcp-server-list_workflow_runs owner repo workflow_id
github-mcp-server-get_job_logs owner repo --failed_only=true --run_id=XXXXX
```
</mcp_error_analysis_commands>
</failure_analysis_phase>

<consistency_validation_phase>
<python_version_enforcement>
**CRITICAL REQUIREMENT**: All workflows MUST enforce Python 3.12+ consistently across ALL platforms and workflow jobs.

<validation_protocol>
- **Universal Python Setup**: Every workflow job using Python MUST include `setup-python@v4` with `python-version: '3.12'`
- **Cross-Platform Uniformity**: Windows, macOS, and Linux workflows MUST use identical Python configurations
- **Requirements Synchronization**: All requirements files MUST be compatible with Python 3.12+
- **Package Compatibility**: All Python packages MUST support Python 3.12+ with verified compatibility
- **CI Pipeline Integration**: Python version enforcement MUST be validated in every CI pipeline execution
</validation_protocol>

<mcp_python_validation_tools>
```bash
# Comprehensive Python 3.12 validation
bash "grep -r 'python-version' .github/workflows/ | sort"
bash "for file in .github/workflows/*.yml; do if grep -q 'python\|pip' '$file' && ! grep -q 'setup-python' '$file'; then echo '❌ $file uses Python but missing setup-python action'; fi; done"

# Requirements file consistency check
str_replace_editor view tools/requirements.txt
str_replace_editor view tools/requirements-py312.txt
```
</mcp_python_validation_tools>
</consistency_validation_phase>

<comprehensive_fix_implementation_phase>
<systematic_resolution_protocol>
- **Universal Application**: When fixing issues, apply consistent solutions across ALL relevant workflows simultaneously
- **Platform-Specific Validation**: Test and validate fixes on Windows, macOS, and Linux independently
- **Incremental Testing**: Implement fixes incrementally with immediate validation after each change
- **Regression Prevention**: Ensure all fixes maintain existing functionality without introducing new issues
- **Documentation Integration**: Update workflow documentation, comments, and README files to reflect changes
</systematic_resolution_protocol>

<mcp_fix_implementation_commands>
```bash
# Apply fixes across all workflows systematically
str_replace_editor str_replace .github/workflows/build.yml
str_replace_editor str_replace .github/workflows/codeql_analysis.yml
# Continue for all workflow files...

# Validate fixes immediately
bash "cmake --build build --parallel 4"
bash "python3 tools/ci/python.sh"
bash "tools/ci/cpp.sh"
```
</mcp_fix_implementation_commands>
</comprehensive_fix_implementation_phase>

<end_to_end_validation_phase>
<complete_system_testing>
- **Cross-Platform Execution**: Validate that workflows execute successfully on all supported platforms
- **Dependency Integration**: Verify all dependencies install correctly and function as expected
- **Complete Build Cycles**: Test entire build and test cycles from start to finish
- **Error Detection Verification**: Confirm proper error detection, reporting, and handling mechanisms
- **Performance Impact Assessment**: Ensure fixes don't introduce performance regressions or timeout issues
</complete_system_testing>

<mcp_validation_commands>
```bash
# End-to-end workflow validation
github-mcp-server-list_workflow_runs owner repo workflow_id --status=completed
github-mcp-server-get_workflow_run_usage owner repo run_id

# Performance and resource validation
bash "grep -r 'timeout' .github/workflows/ | sort"
bash "grep -r 'concurrency' .github/workflows/ | sort"
```
</mcp_validation_commands>
</end_to_end_validation_phase>

<documentation_and_monitoring_phase>
<systematic_improvement_integration>
- **Comprehensive Change Documentation**: Document all changes with detailed rationale and impact analysis
- **Continuous Monitoring Setup**: Establish ongoing workflow health monitoring and alerting systems
- **Preventive Measures Implementation**: Implement systematic measures to prevent recurrence of similar issues
- **Knowledge Transfer Protocol**: Update team knowledge base and documentation for future reference
- **Optimization Identification**: Continuously identify and implement workflow optimization opportunities
</systematic_improvement_integration>
</documentation_and_monitoring_phase>

</comprehensive_methodology>
</critical_workflow_analysis_framework>

<workflow_failure_patterns>

<systematic_pattern_recognition>

<python_version_inconsistencies>
<problem_identification>
- Missing `setup-python@v4` actions in workflow jobs that require Python
- Inconsistent Python versions across different platforms (3.9 vs 3.12)
- Package dependency conflicts arising from Python version mismatches
- Requirements files not properly updated for Python version enforcement changes
</problem_identification>

<resolution_protocol>
- **Universal Python Setup**: Add `setup-python@v4` with `python-version: '3.12'` to ALL workflow jobs using Python
- **Cross-Platform Validation**: Ensure identical Python configuration across Windows, macOS, and Linux
- **Requirements Synchronization**: Update all requirements files to support Python 3.12+
- **Dependency Verification**: Validate package compatibility with Python 3.12+
</resolution_protocol>
</python_version_inconsistencies>

<dependency_management_failures>
<common_issues>
- Package name errors (e.g., `zmq` instead of `pyzmq`)
- Version conflicts between different requirements files across platforms
- Missing platform-specific dependencies for builds
- Incorrect package installation order causing build failures
</common_issues>

<mcp_dependency_resolution>
```bash
# Fix package name errors systematically
str_replace_editor str_replace tools/requirements.txt "zmq>=" "pyzmq>="
str_replace_editor str_replace tools/requirements-py312.txt "zmq>=" "pyzmq>="

# Validate dependency consistency
bash "python3 -c 'import pkg_resources; [print(f\"✅ {req.project_name}: Valid\") for req in pkg_resources.parse_requirements(open(\"tools/requirements.txt\"))]'"
```
</mcp_dependency_resolution>
</dependency_management_failures>

<build_system_complications>
<identified_problems>
- CMake cache conflicts between different build configurations
- Compiler version inconsistencies across platforms
- Missing critical build dependencies for specific platforms
- Timeout issues in resource-intensive compilation processes
</identified_problems>

<systematic_solutions>
- **Cache Management**: Implement proper CMake cache clearing between builds
- **Compiler Standardization**: Ensure consistent compiler versions across all platforms
- **Dependency Documentation**: Maintain comprehensive platform-specific dependency lists
- **Timeout Optimization**: Implement `CI_BUILD_FAST` environment variables and parallel builds
</systematic_solutions>
</build_system_complications>

<configuration_conflicts>
<critical_issues>
- CodeQL configuration file syntax errors and conflicting query specifications
- Clang-format configuration UTF-8 BOM issues preventing proper parsing
- Template file formatting inconsistencies with clang-format requirements
- Conflicting tool configurations between workflow and config files
</critical_issues>

<mcp_configuration_fixes>
```bash
# Configuration file validation
bash "file -bi .clang-format"
bash "hexdump -C .clang-format | head -1"

# UTF-8 BOM removal
bash "sed -i '1s/^\xEF\xBB\xBF//' .clang-format"

# Configuration testing
bash "clang-format-18 --dump-config > /dev/null"
```
</mcp_configuration_fixes>
</configuration_conflicts>

</systematic_pattern_recognition>
</workflow_failure_patterns>

<systematic_fix_approach>
<universal_resolution_protocol>
**Always Fix ALL Related Issues Simultaneously**:
- **Python Version Enforcement**: When fixing Python versions, update ALL workflow files across all platforms
- **Dependency Management**: When resolving dependency issues, validate ALL platforms and requirements files  
- **Build Configuration**: When fixing build issues, validate across ALL build configurations and platforms
- **Tool Configuration**: When fixing configuration issues, check ALL related config files and templates

**Cross-Platform Validation Requirements**:
- **Linux Validation**: Test builds with both GCC and Clang compilers
- **Windows Validation**: Test builds in both Debug and Release configurations  
- **macOS Validation**: Test builds with proper ARM64/Intel optimization settings
- **Python Consistency**: Verify Python 3.12+ functionality across all supported platforms

**Consistency Enforcement Standards**:
- **Identical Setup Actions**: Use identical `setup-python@v4` configuration across all workflows
- **Synchronized Dependencies**: Maintain consistent package versions in all requirements files
- **Uniform Error Handling**: Apply consistent error handling and timeout settings across platforms
- **Standardized Installation**: Ensure consistent dependency installation patterns and procedures
</universal_resolution_protocol>

<mcp_systematic_validation>
```bash
# Universal workflow validation
bash "for file in .github/workflows/*.yml; do if grep -q 'python\|pip' '$file' && ! grep -q 'setup-python@v4' '$file'; then echo 'Fixing Python setup in $file...'; sed -i '/uses: actions\/checkout@v4/a\      - name: Set up Python 3.12\n        uses: actions/setup-python@v4\n        with:\n          python-version: '\''3.12'\''' '$file'; fi; done"

# Cross-platform consistency verification  
bash "grep -r 'python-version' .github/workflows/ | grep -v '3.12'"
github-mcp-server-list_workflows owner repo
```
</mcp_systematic_validation>
</systematic_fix_approach>

<workflow_integration_requirements>
This comprehensive workflow analysis methodology MUST be integrated into ALL development activities:
- **Issue Resolution**: Execute complete workflow analysis before addressing any specific technical issue
- **Feature Development**: Ensure workflow consistency before implementing any new features or capabilities
- **Code Reviews**: Validate ALL workflow files for consistency and correctness during review process
- **Documentation Updates**: Verify workflow impact and consistency when updating documentation
- **Emergency Fixes**: Even urgent fixes MUST maintain complete workflow consistency and validation
</workflow_integration_requirements>

<repository_architecture>

<core_technology_stack>
<programming_languages>
- **C++20**: Primary server implementation language with modern features and standards
- **Lua 5.1**: Scripting engine for game logic, NPCs, missions, and quest systems  
- **Python 3.12+**: Development tools, CI/CD automation, and administrative utilities
- **SQL (MariaDB)**: Database schema, content storage, and player data management
</programming_languages>

<build_and_infrastructure>
- **Build System**: CMake 3.20+ with cross-platform configuration and dependency management
- **Core Dependencies**: MariaDB, LuaJIT, ZeroMQ, spdlog, fmt, OpenSSL for secure communications
- **Supported Platforms**: Linux (primary development), Windows (supported), macOS (supported)
- **CI/CD Pipeline**: GitHub Actions with comprehensive multi-platform validation and testing
</build_and_infrastructure>
</core_technology_stack>

<codebase_organization>
<directory_structure>
- **`src/`**: C++ source code for all server components (common, map, search, login servers)
- **`scripts/`**: Lua scripts implementing game logic, NPC behaviors, missions, and quest systems
- **`sql/`**: Database schema definitions, migrations, and content data structures
- **`tools/`**: Development utilities, maintenance scripts, and CI/CD automation tools
- **`documentation/`**: Technical documentation, API references, and development guides
- **`.github/`**: Workflow definitions, issue templates, and repository automation configurations
</directory_structure>

<mcp_codebase_exploration>
```bash
# Repository structure analysis
str_replace_editor view /home/runner/work/FFXI-Server/FFXI-Server/
str_replace_editor view /home/runner/work/FFXI-Server/FFXI-Server/src/
str_replace_editor view /home/runner/work/FFXI-Server/FFXI-Server/tools/

# Workflow analysis
str_replace_editor view /home/runner/work/FFXI-Server/FFXI-Server/.github/workflows/
github-mcp-server-list_workflows owner repo
```
</mcp_codebase_exploration>
</codebase_organization>

</repository_architecture>

<critical_ci_cd_compliance>

<commit_message_standards>
<enforcement_protocol>
⚠️ **CRITICAL ENFORCEMENT**: All commits MUST follow strict formatting rules enforced by `tools/ci/git.sh`. Failure to comply will result in CI pipeline failures.

<mandatory_requirements>
- **Title Length**: EXACTLY 10-72 characters (strictly enforced - CI FAILS if outside this range)
- **Character Verification**: Always validate with `echo "your title" | wc -c` before committing
- **Content Restrictions**: No pipe characters ("|"), no generic messages like "Update filename.ext"
- **Language Standards**: Strictly avoid casual language ("oops", "whoops", "lol", "lulz", "kek", "kekw")
- **Multi-line Format**: Use commit body (not title) for detailed explanations beyond 72 characters
- **Descriptive Focus**: Emphasize WHAT changed and WHY, not just which file was modified
</mandatory_requirements>

<mcp_commit_validation>
```bash
# Commit message length validation
bash "echo 'Your commit message here' | wc -c"

# Example validation (good)
bash "echo 'Complete Function Indexing System with docs and tests' | wc -c"
# Output: 55 (includes newline, so actual title is 54 chars - ACCEPTABLE)

# Example validation (bad)
bash "echo 'Complete Function Indexing System implementation with documentation and testing' | wc -c"  
# Output: 81 (includes newline, so actual title is 80 chars - TOO LONG, CI WILL FAIL)
```
</mcp_commit_validation>

<approved_templates>
All templates must be ≤72 characters:
- **`Add [feature] with [brief description]`**
- **`Fix [issue] in [component]`** 
- **`Update [component] for [reason]`**
- **`Refactor [component] to [improvement]`**
- **`Remove [deprecated feature/code]`**
</approved_templates>
</enforcement_protocol>
</commit_message_standards>

<code_quality_standards>

<general_file_formatting>
<tools_reference>
Validation Tool: `tools/ci/general.sh`
</tools_reference>

<mandatory_standards>
- **File Endings**: All files MUST end with exactly one newline character
- **Indentation**: Use 4 spaces instead of tab characters (strictly enforced by CI)
- **Line Spacing**: No multiple consecutive newline characters allowed
- **Whitespace**: Remove all trailing whitespace from every line
</mandatory_standards>

<mcp_formatting_validation>
```bash
# File format validation
bash "tools/ci/general.sh"
bash "git diff --check"  # Detect whitespace issues
```
</mcp_formatting_validation>
</general_file_formatting>

<cpp_development_standards>
<tools_reference>
Validation Tools: `tools/ci/cpp.sh`, clang-format-18, cppcheck
</tools_reference>

<core_requirements>
- **Memory Management**: Use `destroy(ptr)` or `destroy_arr(ptr)` instead of naked `delete` operations
- **Include Paths**: Use absolute paths, avoid relative includes with "../" patterns  
- **AI Events**: Document all `.triggerListener()` calls in `documentation/AI_Events.txt`
- **Static Analysis**: Code MUST pass cppcheck with performance, portability, and information checks
- **Code Formatting**: MUST pass clang-format-18 with project `.clang-format` configuration
</core_requirements>

<configuration_validation>
<utf8_bom_detection>
- **Issue**: UTF-8 Byte Order Mark (BOM) in configuration files prevents proper parsing
- **Detection**: Check files (especially `.clang-format`) for BOM presence  
- **Resolution**: Remove BOM using `sed -i '1s/^\xEF\xBB\xBF//' filename`
</utf8_bom_detection>

<template_file_requirements>
- **Pre-formatting**: Template files (*.in) must be pre-formatted to match clang-format-18 output
- **Validation**: Test template files with `clang-format-18 --dry-run --Werror` before committing
- **CMake Integration**: Ensure CMake-generated files comply with formatting standards
</template_file_requirements>
</configuration_validation>

<mcp_cpp_validation>
```bash
# Configuration testing and validation
bash "file -bi .clang-format"
bash "hexdump -C .clang-format | head -1"
bash "clang-format-18 --dump-config > /dev/null"

# UTF-8 BOM removal if detected
bash "sed -i '1s/^\xEF\xBB\xBF//' .clang-format"

# Template validation workflow
bash "cmake -B build -S ."
bash "clang-format-18 --dry-run --Werror build/src/common/version.cpp"
bash "clang-format-18 -i src/common/version.cpp.in"

# Complete C++ validation pipeline
bash "mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Debug .. && make -j$(nproc) && cd .. && tools/ci/cpp.sh"
```
</mcp_cpp_validation>
</cpp_development_standards>

<lua_scripting_standards>
<tools_reference>
Validation Tool: `tools/ci/lua.sh`
</tools_reference>

<requirements>
- **Syntax Validation**: Code MUST pass luacheck with project-specific global configurations
- **Style Consistency**: Follow project lua style checker requirements and conventions
- **Global Usage**: Only use documented global functions and objects from the game engine
- **Complexity Limits**: Maximum cyclomatic complexity of 30 for maintainability
</requirements>

<mcp_lua_validation>
```bash
# Lua validation pipeline
bash "tools/ci/lua.sh"
str_replace_editor view scripts/  # Examine existing Lua patterns
```
</mcp_lua_validation>
</lua_scripting_standards>

<python_development_standards>
<tools_reference>
Validation Tool: `tools/ci/python.sh`
</tools_reference>

<requirements>
- **Linting Compliance**: Code MUST pass pylint and black formatting standards
- **Dependency Management**: Use ONLY packages listed in `tools/requirements.txt` and `tools/requirements-py312.txt`
- **Version Compatibility**: All code MUST be compatible with Python 3.12+ exclusively
</requirements>

<mcp_python_validation>
```bash
# Python validation and dependency checking
bash "tools/ci/python.sh"
str_replace_editor view tools/requirements.txt
str_replace_editor view tools/requirements-py312.txt
bash "python3 -m pip list --format=freeze"
```
</mcp_python_validation>
</python_development_standards>

<sql_database_standards>
<tools_reference>
Validation Tool: `tools/ci/sql.sh`
</tools_reference>

<requirements>
- **Syntax Validation**: All SQL files MUST be syntactically correct and executable
- **Price Consistency**: Maintain consistency with price checker validation requirements
- **Schema Integrity**: Ensure proper foreign key relationships and data integrity constraints
</requirements>

<mcp_sql_validation>
```bash
# SQL validation pipeline
bash "tools/ci/sql.sh"
str_replace_editor view sql/  # Review database schema structure
```
</mcp_sql_validation>
</sql_database_standards>

<license_header_compliance>
<tools_reference>
Validation Tool: `tools/ci/detect_license_headers.py`
</tools_reference>

<mandatory_requirements>
- **GPLv3 Headers**: All C++ source files MUST include proper GPLv3 license headers
- **Creation Documentation**: Include creation date and purpose description in file headers
- **Modification Tracking**: Update modification timestamps appropriately for significant changes
</mandatory_requirements>

<mcp_license_validation>
```bash
# License header validation
bash "python3 tools/ci/detect_license_headers.py"
str_replace_editor view src/  # Review existing license header patterns
```
</mcp_license_validation>
</license_header_compliance>

</code_quality_standards>

<comprehensive_troubleshooting_guide>

<systematic_failure_diagnosis>

<complete_error_collection_protocol>
**Step 1: Comprehensive Information Gathering**
```bash
# Complete workflow failure information collection
bash "find .github/workflows -name '*.yml' -exec echo '=== {} ===' \; -exec cat {} \;"

# YAML syntax validation across all workflows
bash "for file in .github/workflows/*.yml; do echo 'Validating $file...'; python3 -c 'import yaml; yaml.safe_load(open(\"$file\"))' 2>&1 | grep -v '^$' || echo '✅ $file syntax valid'; done"

# Python setup consistency analysis
str_replace_editor create /tmp/python_analysis.py "
import yaml, glob, re
workflows = glob.glob('.github/workflows/*.yml')
python_setups = []
for wf in workflows:
    with open(wf) as f:
        content = f.read()
        if re.search(r'python|pip', content, re.I):
            python_setups.append((wf, 'setup-python' in content, re.findall(r'python-version.*[\'\"([^\'\"]+)', content)))
for wf, has_setup, versions in python_setups:
    print(f'{wf}: setup={has_setup}, versions={versions}')
"
bash "python3 /tmp/python_analysis.py"
```
</complete_error_collection_protocol>

<cross_platform_issue_detection>
**Step 2: Platform-Specific Analysis**
```bash
# Platform distribution analysis
bash "grep -r 'runs-on:' .github/workflows/ | sort | uniq -c"

# Windows-specific configuration analysis
bash "grep -A 10 -B 2 'windows' .github/workflows/*.yml"

# macOS-specific configuration analysis
bash "grep -A 10 -B 2 'macos' .github/workflows/*.yml"

# Linux configuration analysis
bash "grep -A 10 -B 2 'ubuntu' .github/workflows/*.yml"
```
</cross_platform_issue_detection>

<dependency_package_analysis>
**Step 3: Comprehensive Dependency Analysis**
```bash
# Package installation pattern analysis
bash "grep -r 'pip install' .github/workflows/ | sort | uniq"

# Requirements file reference validation
bash "grep -r 'requirements' .github/workflows/ | sort"

# Cross-file dependency conflict detection
str_replace_editor create /tmp/dependency_analysis.py "
import re, os
req_files = ['tools/requirements.txt', 'tools/requirements-py312.txt']
packages = {}
for req_file in [f for f in req_files if os.path.exists(f)]:
    with open(req_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                if match:
                    pkg = match.group(1)
                    packages.setdefault(pkg, []).append((req_file, line))

conflicts = {pkg: files for pkg, files in packages.items() if len(set(line for _, line in files)) > 1}
if conflicts:
    print('❌ Package version conflicts:')
    for pkg, files in conflicts.items():
        print(f'  {pkg}: {files}')
else:
    print('✅ No package conflicts found')
"
bash "python3 /tmp/dependency_analysis.py"
```
</dependency_package_analysis>

</systematic_failure_diagnosis>

<specific_failure_pattern_resolutions>

<python_version_enforcement_failures>
<problem_description>
**Issue**: Inconsistent Python versions across workflows leading to package conflicts and build failures
</problem_description>

<mcp_systematic_solution>
```bash
# Universal Python 3.12 enforcement across ALL workflows
bash "for file in .github/workflows/*.yml; do if grep -q 'python\|pip' '$file' && ! grep -q 'setup-python@v4' '$file'; then echo 'Fixing Python setup in $file...'; sed -i '/uses: actions\/checkout@v4/a\      - name: Set up Python 3.12\n        uses: actions/setup-python@v4\n        with:\n          python-version: '\''3.12'\''' '$file'; fi; done"

# Verification of Python 3.12 enforcement
bash "grep -r 'python-version' .github/workflows/ | grep -v '3.12'"

# MCP validation using GitHub API
github-mcp-server-list_workflows owner repo
github-mcp-server-get_workflow_run owner repo run_id
```
</mcp_systematic_solution>
</python_version_enforcement_failures>

<codeql_configuration_conflicts>
<problem_description>
**Issue**: CodeQL configuration file conflicts causing "security-and-quality security-extended is not a .ql file" errors
</problem_description>

<mcp_resolution_protocol>
```bash
# CodeQL workflow configuration analysis
str_replace_editor view .github/workflows/codeql_analysis.yml

# CodeQL config file validation
str_replace_editor view .github/codeql/codeql-config.yml

# Configuration conflict resolution
str_replace_editor create /tmp/codeql_fix.py "
import yaml
import os

# Read CodeQL workflow
with open('.github/workflows/codeql_analysis.yml', 'r') as f:
    workflow = yaml.safe_load(f)

# Check for conflicting query specifications
init_step = None
for job in workflow.get('jobs', {}).values():
    for step in job.get('steps', []):
        if step.get('uses', '').startswith('github/codeql-action/init'):
            init_step = step
            break

if init_step and 'config-file' in init_step.get('with', {}):
    print('✅ CodeQL uses config file properly')
else:
    print('⚠️ CodeQL configuration may need adjustment')
"
bash "python3 /tmp/codeql_fix.py"
```
</mcp_resolution_protocol>
</codeql_configuration_conflicts>

<build_performance_optimization>
<problem_description>
**Issue**: Build timeouts and performance bottlenecks in resource-intensive compilation
</problem_description>

<mcp_optimization_strategy>
```bash
# Build optimization environment variable addition
bash "for file in .github/workflows/*.yml; do if grep -q 'cmake.*build' '$file'; then echo 'Adding build optimization to $file...'; if ! grep -q 'CI_BUILD_FAST' '$file'; then sed -i '/cmake.*build/i\        env:\n          CI_BUILD_FAST: \"true\"' '$file'; fi; fi; done"

# Parallel build optimization
bash "sed -i 's/cmake --build build$/cmake --build build --parallel 4/g' .github/workflows/*.yml"
bash "sed -i 's/-j2/-j4/g' .github/workflows/*.yml"

# Timeout configuration management
bash "for file in .github/workflows/*.yml; do if grep -q 'Build\|build' '$file' && ! grep -q 'timeout-minutes' '$file'; then echo 'Adding timeout to build steps in $file...'; sed -i '/name:.*[Bb]uild/a\        timeout-minutes: 30' '$file'; fi; done"
```
</mcp_optimization_strategy>
</build_performance_optimization>

<package_dependency_resolution>
<problem_description>
**Issue**: Package name errors and dependency conflicts across requirements files
</problem_description>

<mcp_dependency_management>
```bash
# Package name error correction
bash "for req_file in tools/requirements*.txt; do if [ -f '$req_file' ]; then echo 'Fixing package names in $req_file...'; sed -i 's/^zmq>=/pyzmq>=/g' '$req_file'; sed -i 's/^mysql-connector-python/mysql-connector-python/g' '$req_file'; fi; done"

# Python 3.12 compatibility validation
str_replace_editor create /tmp/package_validation.py "
import pkg_resources
import sys

req_files = ['tools/requirements.txt', 'tools/requirements-py312.txt']
for req_file in [f for f in req_files if __import__('os').path.exists(f)]:
    print(f'Validating {req_file}...')
    try:
        with open(req_file) as f:
            requirements = f.read()
        
        # Check for Python 3.12+ incompatible packages
        incompatible = []
        for line in requirements.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    req = pkg_resources.Requirement.parse(line)
                    print(f'  ✅ {req.project_name}: Valid requirement')
                except Exception as e:
                    incompatible.append(f'{line}: {e}')
        
        if incompatible:
            print(f'❌ Issues in {req_file}:')
            for issue in incompatible:
                print(f'    {issue}')
        else:
            print(f'✅ {req_file}: All requirements valid')
            
    except Exception as e:
        print(f'❌ Error reading {req_file}: {e}')
"
bash "python3 /tmp/package_validation.py"
```
</mcp_dependency_management>
</package_dependency_resolution>

</specific_failure_pattern_resolutions>

<configuration_management>

<file_encoding_issues>
<utf8_bom_detection>
- **Problem**: UTF-8 BOM in `.clang-format`, `.clang-tidy`, and configuration files prevents proper parsing
- **Detection Method**: Check files for BOM presence using file analysis tools
- **Resolution**: Remove BOM using sed commands and verify configuration readability
</utf8_bom_detection>

<mcp_configuration_validation>
```bash
# UTF-8 BOM detection and removal
bash "file -bi .clang-format"
bash "hexdump -C .clang-format | head -1"
bash "sed -i '1s/^\xEF\xBB\xBF//' .clang-format"

# Configuration syntax validation
bash "clang-format-18 --dump-config > /dev/null"

# YAML syntax validation across all workflows
bash "for file in .github/workflows/*.yml; do python3 -c 'import yaml; yaml.safe_load(open(\"$file\"))' || echo \"YAML SYNTAX ERROR in $file\"; done"
```
</mcp_configuration_validation>
</file_encoding_issues>

<template_file_management>
<formatting_requirements>
- **Pre-formatting**: Template files (*.in) must be pre-formatted to match clang-format-18 output expectations
- **Validation Process**: Test generated files with formatting tools before committing templates
- **CMake Integration**: Ensure CMake variable substitution doesn't break formatting compliance
</formatting_requirements>

<mcp_template_validation>
```bash
# Template formatting validation workflow
bash "cmake -B build -S ."
bash "clang-format-18 --dry-run --Werror build/src/common/version.cpp"
bash "clang-format-18 -i src/common/version.cpp.in"

# Build system integration testing
bash "cmake --build . --parallel"
bash "tools/ci/cpp.sh"
bash "git diff --check"
```
</mcp_template_validation>
</template_file_management>

</configuration_management>

</comprehensive_troubleshooting_guide>
<development_workflow_optimization>

<enhanced_11_step_methodology>
<systematic_development_process>
When working on this repository, follow this enhanced 11-step process for optimal code quality and comprehensive workflow integration:

<step_1_intent_definition>
- **Clear Objective Establishment**: Precisely define what you want to achieve within the FFXI game mechanics context
- **System Impact Assessment**: Understand how changes affect game mechanics, server components, and player experience
- **Existing Functionality Preservation**: Consider impact on current functionality and backward compatibility requirements
</step_1_intent_definition>

<step_2_comprehensive_planning>
- **Concrete Plan Creation**: Develop detailed implementation strategy with workflow analysis integration
- **Affected Systems Identification**: Map all affected files, systems, and cross-component dependencies
- **Database Schema Considerations**: Plan any database schema changes with migration script requirements
</step_2_comprehensive_planning>

<step_3_systematic_execution>
- **Pattern-Based Implementation**: Execute plan following existing code patterns and architectural conventions
- **FFXI Retail Consistency**: Maintain consistency with retail FFXI behavior and established game mechanics
- **Workflow Integration**: Ensure all changes comply with comprehensive workflow analysis methodology
</step_3_systematic_execution>

<step_4_outcome_evaluation>
- **Multiple Scenario Assessment**: Evaluate different possible outcomes and implementation approaches
- **Edge Case Analysis**: Consider edge cases, error conditions, and exceptional scenarios
- **Optimal Experience Selection**: Assess which result provides the best game experience and code maintainability
</step_4_outcome_evaluation>

<step_5_comprehensive_testing>
- **Multi-Approach Validation**: Test different implementation approaches and select the optimal solution
- **Infrastructure Integration**: Utilize existing test infrastructure and CI/CD pipeline validation
- **Retail Behavior Validation**: Validate implementation against known retail FFXI behavior patterns
</step_5_comprehensive_testing>

<step_6_feedback_integration>
- **Performance Analysis**: Gather data on why the chosen approach provides optimal results
- **Alternative Documentation**: Document differences from other approaches considered during development
- **Maintainability Assessment**: Consider long-term maintainability and performance implications
</step_6_feedback_integration>

<step_7_optimization_correction>
- **Plan Refinement**: Improve the chosen implementation to the most optimal and efficient version
- **Conflict Resolution**: Ensure no conflicts with existing codebase and established patterns
- **Performance Optimization**: Optimize for memory usage, processing efficiency, and resource utilization
</step_7_optimization_correction>

<step_8_comprehensive_validation>
- **Implementation Verification**: Verify and confirm that the improved plan functions correctly across all scenarios
- **System Integration Testing**: Test all affected game systems and server components thoroughly
- **Standards Compliance**: Ensure full compliance with coding standards and workflow requirements
</step_8_comprehensive_validation>

<step_9_knowledge_documentation>
- **Learning Documentation**: Document insights gained and improvements made to code functionality
- **Reference Updates**: Update relevant documentation, README files, and developer guides
- **Community Knowledge Sharing**: Share knowledge and best practices with the development community
</step_9_knowledge_documentation>

<step_10_iterative_refinement>
- **Quality Assessment**: If results are insufficient, repeat from Intent Definition with gained knowledge
- **Standards Adherence**: Iterate until solution meets all quality standards and workflow requirements
- **Refactoring Readiness**: Don't hesitate to refactor if a superior approach is discovered during development
</step_10_iterative_refinement>

<step_11_delivery_optimization>
- **Optimal Solution Delivery**: Deliver improved, validated solution that optimally achieves the original objective
- **Codebase Integration**: Ensure seamless integration with existing codebase and architectural patterns
- **Implementation Documentation**: Document final implementation comprehensively for future reference and maintenance
</step_11_delivery_optimization>
</systematic_development_process>

<mcp_workflow_integration>
```bash
# Integrate MCP tools throughout development workflow
str_replace_editor view /path/to/files  # Code exploration
github-mcp-server-list_workflows owner repo  # Workflow analysis
bash "tools/ci/python.sh"  # Validation integration
report_progress "commit message" "progress description"  # Progress tracking
```
</mcp_workflow_integration>
</enhanced_11_step_methodology>

<dependency_management_framework>

<comprehensive_dependency_tracking>
<python_package_management>
- **Central Tracking**: All Python packages tracked in `tools/requirements.txt` and `tools/requirements-py312.txt`
- **Version Compatibility**: Ensure all packages support Python 3.12+ with verified compatibility testing
- **Security Monitoring**: Regular vulnerability scanning and deprecated package identification
- **Installation Validation**: Test package installation across all supported platforms (Windows, macOS, Linux)
</python_package_management>

<cpp_library_dependencies>
- **Core Libraries**: Document CMake dependencies (MariaDB, LuaJIT, ZeroMQ, OpenSSL, spdlog, fmt)
- **Build System Integration**: Maintain CMake configuration for cross-platform dependency resolution
- **Version Pinning**: Use specific versions for critical dependencies to ensure build reproducibility
- **Header-Only Preference**: Prefer header-only libraries when possible to reduce build complexity
</cpp_library_dependencies>

<system_package_requirements>
- **Platform Documentation**: Document required system dependencies for each supported platform
- **Installation Scripts**: Provide automated installation scripts for development environment setup
- **CI Integration**: Ensure CI pipelines properly install and validate all system dependencies
- **Update Procedures**: Establish procedures for updating system dependencies across all platforms
</system_package_requirements>

<mcp_dependency_validation>
```bash
# Comprehensive dependency validation
str_replace_editor view tools/requirements.txt
str_replace_editor view tools/requirements-py312.txt
bash "python3 -c 'import pkg_resources; [print(f\"✅ {req.project_name}\") for req in pkg_resources.parse_requirements(open(\"tools/requirements.txt\"))]'"

# System dependency verification
bash "cmake --version && python3 --version && mariadb --version"
```
</mcp_dependency_validation>
</comprehensive_dependency_tracking>

<error_prevention_framework>
<proactive_quality_measures>
- **String Operation Safety**: Check for truncation issues and buffer overflows in string operations
- **Script Validation**: Validate all shell scripts with shellcheck for syntax and logic errors
- **Permission Management**: Ensure proper file permissions for security and functionality
- **Exception Handling**: Handle edge cases gracefully with comprehensive error recovery mechanisms
- **Memory Safety**: Follow strict memory safety guidelines for C++ development
- **Input Validation**: Validate all user inputs and database queries to prevent injection attacks
</proactive_quality_measures>

<mcp_error_prevention>
```bash
# Proactive error detection
bash "shellcheck tools/*.sh"
bash "find . -name '*.cpp' -exec cppcheck {} \;"
bash "python3 -m py_compile tools/*.py"
```
</mcp_error_prevention>
</error_prevention_framework>

</development_workflow_optimization>

<comprehensive_testing_framework>

<unit_testing_protocols>
<cpp_testing_requirements>
- **New Functionality Testing**: Write comprehensive tests for all new C++ functionality with full coverage
- **Component Integration**: Test individual components and their interactions with existing systems
- **Cross-Platform Validation**: Ensure tests pass on Windows, macOS, and Linux environments
- **Performance Benchmarking**: Include performance tests for critical path functionality
</cpp_testing_requirements>

<lua_script_validation>
- **Game Scenario Testing**: Test Lua scripts with realistic game scenario validation
- **NPC Behavior Verification**: Validate NPC interactions, dialogue, and quest progression
- **Game Mechanics Testing**: Test combat mechanics, item interactions, and player progression systems
- **Retail Accuracy Validation**: Compare script behavior against known retail FFXI mechanics
</lua_script_validation>

<database_testing_standards>
- **Migration Verification**: Verify all database migrations work correctly and are reversible
- **Data Integrity Testing**: Test foreign key constraints, data validation, and referential integrity
- **Performance Testing**: Validate query performance and database optimization strategies
- **Cross-Platform Database Testing**: Ensure database compatibility across different MariaDB versions
</database_testing_standards>

<mcp_testing_integration>
```bash
# Comprehensive testing workflow
bash "python3 tools/comprehensive_build_test.py --ci"
bash "tools/ci/cpp.sh && tools/ci/lua.sh && tools/ci/python.sh"
str_replace_editor view tests/  # Review existing test patterns
github-mcp-server-list_workflow_runs owner repo workflow_id --status=completed
```
</mcp_testing_integration>
</unit_testing_protocols>

<integration_testing_framework>
<server_component_testing>
- **Startup/Shutdown Validation**: Validate complete server startup and shutdown procedures
- **Component Communication**: Test inter-server communication protocols and data synchronization
- **Resource Management**: Test memory usage, connection handling, and resource cleanup
- **Error Recovery**: Test system recovery from various failure scenarios
</server_component_testing>

<client_server_communication>
- **Protocol Testing**: Test all client-server communication protocols and packet handling
- **Connection Reliability**: Validate connection stability and reconnection mechanisms
- **Data Synchronization**: Test player data synchronization and state management
- **Security Validation**: Test authentication, authorization, and data protection mechanisms
</client_server_communication>

<game_mechanics_validation>
- **Retail Accuracy**: Verify game mechanics work exactly as expected in retail FFXI
- **Player Progression**: Test experience systems, skill advancement, and character development
- **Combat Systems**: Validate damage calculations, status effects, and combat mechanics
- **Economic Systems**: Test item trading, auction house functionality, and in-game economy
</game_mechanics_validation>

<performance_testing_requirements>
- **Load Testing**: Test server performance under realistic player loads
- **Resource Monitoring**: Monitor CPU, memory, and network resource utilization
- **Scalability Testing**: Test system behavior as player count increases
- **Stress Testing**: Validate system stability under extreme conditions
</performance_testing_requirements>

<mcp_integration_testing>
```bash
# Integration testing workflow
bash "python3 tools/enhanced_database_test_suite.py"
bash "python3 tools/network_bonding_test_suite.py"
github-mcp-server-get_workflow_run_usage owner repo run_id
```
</mcp_integration_testing>
</integration_testing_framework>

</comprehensive_testing_framework>

<performance_optimization_framework>

<memory_management_optimization>
<data_structure_efficiency>
- **Container Selection**: Use appropriate container types optimized for specific data access patterns
- **Cache-Friendly Layouts**: Consider memory layout optimization for frequently accessed data structures
- **Memory Pool Management**: Implement object pooling for frequently allocated/deallocated objects
- **Profiling Integration**: Profile memory usage patterns for large datasets and optimize accordingly
</data_structure_efficiency>

<server_process_optimization>
- **Memory Leak Prevention**: Implement comprehensive memory leak detection and prevention in long-running processes
- **Resource Monitoring**: Continuously monitor memory usage patterns and implement automatic cleanup
- **Garbage Collection**: Implement efficient cleanup strategies for temporary objects and buffers
- **Memory Mapping**: Use memory-mapped files for large static data sets when appropriate
</server_process_optimization>

<mcp_memory_optimization>
```bash
# Memory profiling and optimization
bash "valgrind --tool=memcheck --leak-check=full ./server"
bash "python3 tools/performance_monitor.py --memory"
```
</mcp_memory_optimization>
</memory_management_optimization>

<concurrency_threading_optimization>
<thread_safety_implementation>
- **Server Component Safety**: Ensure thread safety in all multi-threaded server components
- **Synchronization Primitives**: Use appropriate mutexes, locks, and atomic operations efficiently
- **Race Condition Prevention**: Implement comprehensive race condition detection and prevention strategies
- **Lock Performance**: Consider performance impact of locking mechanisms and optimize critical paths
</thread_safety_implementation>

<concurrent_processing_optimization>
- **Work Distribution**: Implement efficient work distribution across available CPU cores
- **Lock-Free Algorithms**: Use lock-free data structures where possible for high-performance scenarios
- **Thread Pool Management**: Implement efficient thread pool management for task processing
- **Asynchronous Processing**: Use asynchronous I/O and processing for network and disk operations
</concurrent_processing_optimization>

<mcp_concurrency_optimization>
```bash
# Concurrency analysis and optimization
bash "python3 tools/advanced_profiler.py --threading"
bash "cppcheck --enable=all --check-config src/"
```
</mcp_concurrency_optimization>
</concurrency_threading_optimization>

</performance_optimization_framework>

<ffxi_game_development_standards>

<retail_accuracy_framework>
<behavioral_consistency_requirements>
- **Accurate Recreation**: Strive for pixel-perfect recreation of retail FFXI behavior and game mechanics
- **Research-Based Implementation**: Research retail mechanics thoroughly before implementing any game features
- **Deviation Documentation**: Document any necessary deviations from retail behavior with detailed justification
- **Player Experience Priority**: Consider overall player experience and game balance in all implementation decisions
</behavioral_consistency_requirements>

<validation_methodology>
- **Retail Comparison**: Use retail FFXI behavior as the gold standard for all game mechanics validation
- **Community Resources**: Leverage community wikis, guides, and historical data for accuracy verification
- **Testing Protocols**: Implement comprehensive testing protocols to validate retail accuracy
- **Feedback Integration**: Integrate community feedback to identify and correct behavioral discrepancies
</validation_methodology>

<mcp_retail_validation>
```bash
# Retail accuracy validation tools
str_replace_editor view scripts/  # Review game mechanic implementations
str_replace_editor view sql/  # Validate database content accuracy
bash "python3 tools/price_checker.py"  # Validate item price accuracy
```
</mcp_retail_validation>
</retail_accuracy_framework>

<content_implementation_standards>
<npc_monster_item_development>
- **Existing Pattern Adherence**: Follow established patterns for NPCs, monsters, and items consistently
- **Retail Data Integration**: Use appropriate item IDs, statistics, and behavior data from retail sources
- **Database Consistency**: Ensure all content integrates properly with existing database schema
- **Cross-Reference Validation**: Validate content against multiple retail data sources for accuracy
</npc_monster_item_development>

<quest_mission_implementation>
- **Progression Logic**: Implement quests and missions with proper progression logic and state management
- **Dialogue Accuracy**: Ensure NPC dialogue matches retail text and progression triggers
- **Reward Systems**: Implement accurate reward systems matching retail quest completion benefits
- **Dependency Management**: Properly handle quest dependencies and prerequisite requirements
</quest_mission_implementation>

<zone_map_functionality>
- **Geographic Accuracy**: Ensure proper zone layouts and geographic features match retail implementations
- **Connection Logic**: Implement accurate zone connection logic and transition mechanics
- **NPC Placement**: Position NPCs accurately according to retail zone layouts
- **Environmental Features**: Include all environmental features, weather systems, and zone-specific mechanics
</zone_map_functionality>

<mcp_content_validation>
```bash
# Content implementation validation
str_replace_editor view scripts/zones/  # Zone-specific implementations
str_replace_editor view scripts/quests/  # Quest progression logic
bash "python3 tools/generate_lua_catalog.py"  # Content catalog generation
```
</mcp_content_validation>
</content_implementation_standards>

</ffxi_game_development_standards>

<community_collaboration_framework>

<code_review_excellence>
<review_process_standards>
- **Mandatory Peer Review**: All changes require thorough peer review before integration
- **Retail Validation**: Validate all changes against retail FFXI behavior when applicable
- **Multi-Platform Testing**: Test changes on Windows, macOS, and Linux before merging
- **Breaking Change Documentation**: Document all breaking changes thoroughly with migration guides
</review_process_standards>

<review_quality_criteria>
- **Code Standards Compliance**: Ensure all code meets established coding standards and conventions
- **Performance Impact Assessment**: Evaluate performance implications of all proposed changes
- **Security Validation**: Review security implications and validate input handling
- **Documentation Completeness**: Verify adequate documentation for complex changes and new features
</review_quality_criteria>

<mcp_review_integration>
```bash
# Code review automation and validation
github-mcp-server-get_pull_request owner repo pull_number
github-mcp-server-get_pull_request_files owner repo pull_number
bash "tools/ci/cpp.sh && tools/ci/lua.sh && tools/ci/python.sh"
```
</mcp_review_integration>
</code_review_excellence>

<community_engagement_standards>
<contributor_interaction>
- **Respectful Communication**: Maintain respectful and helpful interactions with all contributors
- **Constructive Feedback**: Provide specific, actionable, and constructive feedback on code reviews
- **Knowledge Sharing**: Actively share knowledge, best practices, and development insights
- **Newcomer Support**: Help newcomers understand codebase architecture and development processes
</contributor_interaction>

<collaborative_development>
- **Open Communication**: Maintain open channels for technical discussions and project coordination
- **Documentation Maintenance**: Keep documentation current and accessible for all community members
- **Issue Tracking**: Use clear issue tracking and labeling for effective project management
- **Feature Planning**: Involve community in feature planning and priority discussions
</collaborative_development>

<mcp_community_tools>
```bash
# Community collaboration tools
github-mcp-server-list_issues owner repo --state=open
github-mcp-server-search_issues "label:help-wanted"
bash "python3 tools/generate_changelog.py"
```
</mcp_community_tools>
</community_engagement_standards>

</community_collaboration_framework>

<project_management_framework>

<changelog_management_system>
<landsandboat_format_compliance>
This repository follows the exact changelog format specification used by LandSandBoat/server for consistency and community alignment:

```markdown
## [Project Name] Changelog (YYYY-MM-DD)
- [component] feature description [[#PR](link), [patch](patch-link)] (contributors)
```
</landsandboat_format_compliance>

<component_tag_standardization>
Use these standardized component tags in PR titles and changelog entries for consistent categorization:
- **`[sql]`**: Database schema changes, migrations, and SQL modifications
- **`[lua]`**: Lua script implementations (quests, NPCs, game logic, combat mechanics)
- **`[cpp]`**: C++ core server code changes and architecture modifications
- **`[core]`**: Core server functionality, architecture, and infrastructure changes
- **`[fix]`**: Bug fixes, error corrections, and issue resolutions
- **`[quest]`**: Quest content implementations and quest system modifications
- **`[mission]`**: Mission content, storyline implementations, and progression systems
- **`[documentation]`**: Documentation updates, API references, and development guides
- **`[tools]`**: Development tools, utilities, and automation script improvements
- **`[ci/cd]`**: Continuous integration, deployment, and workflow modifications
</component_tag_standardization>

<automated_changelog_generation>
<generation_workflow>
- **Automation Tool**: Use `tools/generate_changelog.py` for consistent automated changelog generation
- **Release Schedule**: Follow bi-weekly schedule (1st and 15th of each month) matching LandSandBoat practices
- **Storage Format**: Store changelogs in `changelogs/` directory with `changelog-YYYY-MM-DD.md` naming convention
- **Link Integration**: Include both PR links and patch links for comprehensive change tracking
- **Privacy Protection**: Remove real names from contributor lists for privacy and security
</generation_workflow>

<mcp_changelog_integration>
```bash
# Automated changelog generation and management
bash "python3 tools/generate_changelog.py --format=landsandboat"
str_replace_editor view changelogs/  # Review existing changelog format
github-mcp-server-list_pull_requests owner repo --state=merged
```
</mcp_changelog_integration>
</automated_changelog_generation>

<development_workflow_integration>
<pr_title_standards>
- **Changelog Ready**: PR titles should be immediately usable in changelog entries
- **Component Tagging**: Include appropriate component tags for proper categorization
- **Descriptive Content**: Provide clear, concise descriptions of changes and their impact
- **Infrastructure Documentation**: Document major infrastructure changes in both changelog and ROADMAP.md
</pr_title_standards>

<activity_tracking_integration>
- **Log Management**: Use `tools/log_manager.py` to track development activities alongside changelog entries
- **Progress Monitoring**: Integrate changelog generation with overall project progress tracking
- **Release Coordination**: Coordinate changelog releases with major feature deployments
- **Community Communication**: Use changelogs for community updates and project status communication
</activity_tracking_integration>
</development_workflow_integration>

</changelog_management_system>

<security_compliance_framework>

<input_validation_protocols>
<client_input_security>
- **Comprehensive Validation**: Validate all user inputs from game clients with strict type and range checking
- **Injection Prevention**: Sanitize all database inputs to prevent SQL injection and other injection attacks
- **Rate Limiting**: Implement comprehensive rate limiting for all network operations and API endpoints
- **Malformed Data Handling**: Handle malformed packets and invalid data gracefully with proper error recovery
</client_input_security>

<database_security_standards>
- **Parameterized Queries**: Use parameterized queries exclusively for all database interactions
- **Connection Security**: Implement secure database connections with proper authentication and encryption
- **Data Sanitization**: Sanitize all user-provided data before database storage or processing
- **Access Logging**: Log all database access patterns for security monitoring and audit trails
</database_security_standards>

<mcp_security_validation>
```bash
# Security validation and monitoring
bash "python3 tools/vulnerability_scanner.py"
bash "grep -r 'SQL' src/ | grep -v 'parameterized'"  # Check for non-parameterized queries
bash "tools/ci/python.sh --security"
```
</mcp_security_validation>
</input_validation_protocols>

<access_control_implementation>
<administrative_security>
- **GM Command Authorization**: Implement proper authorization checks for all GM commands and administrative functions
- **Player Permission Validation**: Validate player permissions for all actions and game state modifications
- **Administrative Interface Security**: Secure all administrative interfaces with multi-factor authentication
- **Security Event Logging**: Log all security-relevant events for monitoring and incident response
</administrative_security>

<privilege_management>
- **Least Privilege Principle**: Implement least privilege access for all system components and user roles
- **Role-Based Access Control**: Use role-based access control for player and administrative privileges
- **Session Management**: Implement secure session management with proper timeout and validation
- **Audit Trail Maintenance**: Maintain comprehensive audit trails for all privileged operations
</privilege_management>

<mcp_access_control>
```bash
# Access control validation
str_replace_editor view src/  # Review privilege checking implementations
bash "grep -r 'hasPrivilege\|checkAccess' src/"
bash "python3 tools/admin_dashboard.py --security-audit"
```
</mcp_access_control>
</access_control_implementation>

</security_compliance_framework>

</project_management_framework>

<strategic_development_framework>

<roadmap_driven_development>
<infrastructure_modernization>
- **Roadmap Alignment**: Follow development roadmap in `ROADMAP.md` for prioritized infrastructure improvements
- **Code Quality Focus**: Prioritize infrastructure modernization and comprehensive code quality enhancements
- **Community-Driven Planning**: Plan feature development based on community needs and retail accuracy requirements
- **Scalability Considerations**: Consider performance and scalability implications in all architectural decisions
</infrastructure_modernization>

<continuous_improvement_integration>
- **Codebase Health Assessment**: Regular systematic assessment of codebase health and technical debt management
- **Automated Dependency Tracking**: Implement automated dependency tracking with comprehensive vulnerability monitoring
- **Performance Benchmarking**: Establish performance benchmarking and systematic optimization initiatives
- **Community Feedback Integration**: Integrate community feedback systematically into development priorities and planning
</continuous_improvement_integration>

<mcp_strategic_planning>
```bash
# Strategic development planning and monitoring
str_replace_editor view ROADMAP.md  # Review development priorities
bash "python3 tools/generate_function_index.py"  # Function indexing and documentation
github-mcp-server-search_issues "label:enhancement"
bash "python3 tools/db_optimization_summary.py"
```
</mcp_strategic_planning>
</roadmap_driven_development>

<comprehensive_documentation_framework>
<api_documentation_standards>
- **Component Documentation**: Maintain comprehensive API documentation for all server components
- **Cross-Component Mapping**: Index functions across C++, Lua, and Python codebases with dependency mapping
- **Interaction Documentation**: Document cross-component interactions and architectural dependencies thoroughly
- **Developer Resources**: Ensure searchable and accessible developer resources for all development activities
</api_documentation_standards>

<function_indexing_system>
<comprehensive_indexing>
Refer to `ROADMAP.md` for comprehensive function indexing including:
- **C++ Core Components**: Server architecture, subsystems, key classes, and architectural patterns
- **Python Development Tools**: Development utilities, CI/CD scripts, automation tools, and workflow management
- **Lua Game Framework**: Game mechanics, quest systems, event handlers, and content management
- **Database Schema Architecture**: Core tables, relationships, data structures, and optimization strategies
</comprehensive_indexing>

<mcp_documentation_tools>
```bash
# Comprehensive documentation generation and management
bash "python3 tools/generate_cpp_docs.py"
bash "python3 tools/generate_sql_docs.py"
bash "python3 tools/enhanced_function_indexer.py"
str_replace_editor view documentation/  # Review existing documentation structure
```
</mcp_documentation_tools>
</function_indexing_system>

</comprehensive_documentation_framework>

</strategic_development_framework>

<development_resource_ecosystem>

<comprehensive_tool_integration>
<development_utilities>
- **Database Operations**: Use `tools/dbtool.py` for database operations, migrations, and maintenance tasks
- **Quality Assurance**: Run `tools/ci/` scripts for comprehensive quality checks and validation
- **Server Administration**: Use `tools/announce.py` for server-wide messaging and administrative communications
- **Security Auditing**: Use `tools/vulnerability_scanner.py` for comprehensive security auditing and monitoring
- **Content Validation**: Use `tools/price_checker.py` for item price validation and economic balance
- **Log Management**: Use `tools/log_manager.py` for comprehensive log maintenance and analysis
- **Release Management**: Use `tools/generate_changelog.py` for automated changelog generation and release coordination
</development_utilities>

<mcp_tool_integration>
```bash
# Comprehensive development tool utilization
bash "python3 tools/dbtool.py --help"  # Database management
bash "python3 tools/vulnerability_scanner.py --scan-all"  # Security auditing
bash "python3 tools/comprehensive_build_test.py --ci"  # Build validation
str_replace_editor view tools/  # Tool ecosystem exploration
```
</mcp_tool_integration>
</comprehensive_tool_integration>

<workflow_analysis_automation>
<comprehensive_validation_commands>
```bash
# Complete workflow file discovery and comprehensive analysis
bash "find .github/workflows -name '*.yml' -o -name '*.yaml' | sort"

# Python version consistency validation across all workflows
bash "grep -r 'python-version' .github/workflows/ | sort"

# Missing setup-python action detection
bash "grep -L 'setup-python' .github/workflows/*.yml"

# Package dependency consistency verification
bash "grep -r 'requirements' .github/workflows/ | sort"

# Platform coverage assessment
bash "grep -r 'runs-on:' .github/workflows/ | sort | uniq"

# Workflow trigger consistency validation
bash "grep -r 'on:' .github/workflows/ -A 5"
```
</comprehensive_validation_commands>

<systematic_fix_validation_automation>
```bash
# YAML syntax validation across all workflow files
bash "for file in .github/workflows/*.yml; do echo 'Validating $file...'; python3 -c 'import yaml; yaml.safe_load(open(\"$file\"))' || echo 'SYNTAX ERROR in $file'; done"

# Python 3.12 enforcement comprehensive validation
str_replace_editor create /tmp/python_validation.py "
import os
import yaml
import glob

workflows = glob.glob('.github/workflows/*.yml')
python_issues = []

for workflow_file in workflows:
    with open(workflow_file, 'r') as f:
        try:
            workflow = yaml.safe_load(f)
            jobs = workflow.get('jobs', {})
            
            for job_name, job_config in jobs.items():
                steps = job_config.get('steps', [])
                has_python_setup = False
                python_version = None
                
                for step in steps:
                    if step.get('uses', '').startswith('actions/setup-python'):
                        has_python_setup = True
                        with_config = step.get('with', {})
                        python_version = with_config.get('python-version')
                        
                        if python_version != '3.12':
                            python_issues.append(f'{workflow_file}:{job_name} uses Python {python_version} instead of 3.12')
                
                # Check if job needs Python but doesn't set it up
                needs_python = any('python' in str(step).lower() or 'pip' in str(step).lower() for step in steps)
                if needs_python and not has_python_setup:
                    python_issues.append(f'{workflow_file}:{job_name} needs Python but missing setup-python action')

if python_issues:
    print('❌ Python version issues found:')
    for issue in python_issues:
        print(f'  {issue}')
else:
    print('✅ All workflows properly enforce Python 3.12')
"
bash "python3 /tmp/python_validation.py"
```
</systematic_fix_validation_automation>

<cross_platform_testing_automation>
```bash
# Linux dependency testing simulation
bash "python3 -c 'import subprocess; result = subprocess.run([\"apt-cache\", \"show\", \"libmariadb-dev-compat\"], capture_output=True, text=True); print(\"✅ Linux dependencies available\" if result.returncode == 0 else \"❌ Linux dependency issues\")'"

# Workflow structure validation automation
str_replace_editor create /tmp/workflow_structure_validation.py "
import yaml
import glob

def validate_workflow_structure():
    workflows = glob.glob('.github/workflows/*.yml')
    issues = []
    
    required_sections = ['name', 'on', 'jobs']
    
    for workflow_file in workflows:
        with open(workflow_file, 'r') as f:
            try:
                workflow = yaml.safe_load(f)
                
                # Check required sections
                for section in required_sections:
                    if section not in workflow:
                        issues.append(f'{workflow_file}: Missing required section \'{section}\'')
                
                # Check job structure
                jobs = workflow.get('jobs', {})
                for job_name, job_config in jobs.items():
                    if 'runs-on' not in job_config:
                        issues.append(f'{workflow_file}:{job_name}: Missing \'runs-on\'')
                    
                    if 'steps' not in job_config:
                        issues.append(f'{workflow_file}:{job_name}: Missing \'steps\'')
                        
            except yaml.YAMLError as e:
                issues.append(f'{workflow_file}: YAML syntax error - {e}')
    
    if issues:
        print('❌ Workflow structure issues:')
        for issue in issues:
            print(f'  {issue}')
        return False
    else:
        print('✅ All workflows have valid structure')
        return True

validate_workflow_structure()
"
bash "python3 /tmp/workflow_structure_validation.py"

# Timeout and resource configuration consistency
bash "grep -r 'timeout' .github/workflows/ | sort"
bash "grep -r 'concurrency' .github/workflows/ | sort"
```
</cross_platform_testing_automation>
</workflow_analysis_automation>

<configuration_debugging_automation>
<validation_tools>
- **Configuration Parsing**: `clang-format-18 --dump-config` - Verify clang-format configuration parsing accuracy
- **File Encoding Detection**: `file -bi filename` - Check file encoding and detect BOM presence  
- **Header Analysis**: `hexdump -C filename | head -1` - Examine file headers for UTF-8 BOM bytes (EF BB BF)
</validation_tools>

<template_testing_automation>
- **File Generation**: `cmake -DCMAKE_BUILD_TYPE=Debug ..` - Generate files for comprehensive testing
- **Format Validation**: `clang-format-18 --dry-run --Werror file.cpp` - Test formatting without making changes
- **Comparison Analysis**: `diff -u expected.cpp generated.cpp` - Compare formatting expectations with results
</template_testing_automation>

<build_validation_integration>
- **Compilation Testing**: `cmake --build . --parallel` - Test compilation of all generated files
- **Pipeline Validation**: `tools/ci/cpp.sh` - Run complete C++ validation pipeline
- **Issue Detection**: `git diff --check` - Detect whitespace and formatting issues automatically
</build_validation_integration>
</configuration_debugging_automation>

<documentation_reference_system>
<technical_references>
- **Technical Documentation**: Consult `documentation/` for comprehensive technical references and specifications
- **Development Priorities**: Review `ROADMAP.md` for current development priorities and improvement plans
- **Automation Tools**: Use existing changelog generation tools in `tools/generate_changelog.py`
- **Dependency Management**: Check `tools/requirements.txt` and `tools/requirements-py312.txt` for Python dependency management
- **Format Compliance**: Follow changelog format in `changelogs/` directory matching LandSandBoat/server structure
</technical_references>

<quality_assurance_integration>
- **CI/CD Compliance**: All changes must pass comprehensive CI/CD pipeline checks defined in `tools/ci/`
- **Workflow Adherence**: Follow the enhanced 11-step development workflow documented throughout these instructions
- **Standards Compliance**: Ensure full compliance with coding standards for each programming language
- **Retail Validation**: Validate all changes against retail FFXI behavior when applicable and feasible
</quality_assurance_integration>
</documentation_reference_system>

</development_resource_ecosystem>

<mcp_best_practices_integration>

<systematic_workflow_analysis_for_mcp>
Following GitHub's best practices for Model Context Protocol integration and Copilot coding agents, this repository implements comprehensive workflow analysis requirements optimized for MCP tool utilization:

<comprehensive_analysis_methodology_mcp>
- **Universal Workflow Analysis**: When addressing workflow issues, examine every workflow file in `.github/workflows/` using MCP tools, not just failing ones
- **Cross-Platform Consistency**: Ensure fixes are applied consistently across Windows, macOS, and Linux platforms using systematic MCP validation
- **Systematic Root Cause Analysis**: Identify underlying causes rather than treating symptoms using MCP diagnostic tools
- **Comprehensive Validation**: Test all related components after making changes using integrated MCP testing frameworks
- **Documentation Integration**: Update documentation to reflect workflow improvements using MCP documentation tools
</comprehensive_analysis_methodology_mcp>

<workflow_fix_validation_standards_mcp>
- **Python Version Enforcement**: Verify Python 3.12+ is consistently enforced across ALL workflow jobs using MCP validation scripts
- **Dependency Consistency**: Ensure package versions and installation methods are uniform using MCP dependency analysis
- **Error Handling Uniformity**: Implement consistent error detection and reporting using MCP monitoring tools
- **Performance Optimization**: Address timeout issues and resource constraints systematically using MCP performance analysis
- **Security Configuration**: Maintain consistent security tool configurations using MCP security validation frameworks
</workflow_fix_validation_standards_mcp>

<continuous_improvement_integration_mcp>
- **Proactive Issue Prevention**: Implement measures to prevent similar workflow issues using MCP preventive analysis
- **Monitoring and Alerting**: Establish ongoing workflow health monitoring using MCP monitoring integration
- **Knowledge Base Updates**: Update instructions and documentation based on lessons learned using MCP knowledge management
- **Team Knowledge Sharing**: Document workflow improvements for team benefit using MCP collaboration tools
- **Automated Validation**: Integrate workflow validation into development processes using comprehensive MCP automation
</continuous_improvement_integration_mcp>

</systematic_workflow_analysis_for_mcp>

<essential_mcp_validation_commands>
```bash
# Complete workflow analysis command set optimized for MCP integration
echo "🔍 COMPREHENSIVE WORKFLOW ANALYSIS WITH MCP INTEGRATION"

# Step 1: Workflow Discovery and Inventory using MCP tools
echo "📋 Step 1: MCP-Enhanced Workflow Discovery"
str_replace_editor view .github/workflows/
github-mcp-server-list_workflows owner repo
bash "find .github/workflows -name '*.yml' -o -name '*.yaml' | sort"
bash "echo 'Total workflows: $(find .github/workflows -name \"*.yml\" -o -name \"*.yaml\" | wc -l)'"

# Step 2: Python Version Enforcement Validation with MCP
echo "🐍 Step 2: MCP Python Version Analysis"
bash "grep -r 'python-version' .github/workflows/ | grep -v '3.12' && echo '❌ Non-3.12 versions found' || echo '✅ Python 3.12 enforced'"
github-mcp-server-get_workflow_run owner repo run_id

# Step 3: Cross-Platform Consistency Check with MCP
echo "🌐 Step 3: MCP Platform Coverage Analysis"
bash "echo 'Platforms used:' && grep -r 'runs-on:' .github/workflows/ | cut -d: -f3 | sort | uniq -c"
github-mcp-server-list_workflow_runs owner repo workflow_id

# Step 4: Dependency Analysis with MCP Integration
echo "📦 Step 4: MCP Dependency Consistency Analysis"
bash "echo 'Package installation patterns:' && grep -r 'pip install\|requirements' .github/workflows/ | sort | uniq"
str_replace_editor view tools/requirements.txt
str_replace_editor view tools/requirements-py312.txt

# Step 5: Error Pattern Detection with MCP
echo "🚨 Step 5: MCP Error Pattern Analysis"
bash "grep -r 'timeout\|fail\|error' .github/workflows/ | wc -l | xargs echo 'Error handling references:'"
github-mcp-server-get_job_logs owner repo --failed_only=true --run_id=XXXXX

# Step 6: Configuration Validation with MCP
echo "⚙️ Step 6: MCP Configuration File Analysis"
str_replace_editor view .clang-format
str_replace_editor view .github/codeql/codeql-config.yml
bash "for config in .clang-format .clang-tidy .github/codeql/codeql-config.yml; do if [ -f '$config' ]; then echo '✅ $config exists'; if file '$config' | grep -q 'BOM'; then echo '⚠️  $config has UTF-8 BOM'; fi; else echo '❌ $config missing'; fi; done"

echo "✅ COMPREHENSIVE WORKFLOW ANALYSIS WITH MCP INTEGRATION COMPLETE"
```
</essential_mcp_validation_commands>

</mcp_best_practices_integration>

<conclusion>
**Repository Mission**: This community-driven project is dedicated to preserving and recreating the authentic Final Fantasy XI experience with unwavering commitment to quality, accuracy, and maintainability as our highest priorities.

**Development Philosophy**: Consult the roadmap consistently for current development priorities and systematic improvement plans. All development activities must integrate comprehensive workflow analysis methodology to ensure consistent, high-quality outcomes across all platforms and development scenarios.

**MCP Integration Excellence**: These instructions are optimized for Model Context Protocol integration, enabling seamless tool utilization and automated workflow management for enhanced development efficiency and comprehensive quality assurance.
</conclusion>
