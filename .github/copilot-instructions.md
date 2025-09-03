# Copilot Instructions for LandSandBoat Server

<repository_context>
This repository is an open-source server emulator for Final Fantasy XI (FFXI), written primarily in C++ with Lua scripting support.
</repository_context>

<priority_workflow_function>

<comprehensive_workflow_analysis_methodology>
**CRITICAL**: Before addressing any comment, prompt, or development task, ALWAYS execute this comprehensive workflow analysis methodology:

<step_1_systematic_workflow_discovery>
- **Complete Workflow Inventory**: List ALL workflow files in `.github/workflows/` directory
- **Cross-Reference Analysis**: Check for workflow dependencies and relationships
- **Platform Coverage Assessment**: Verify Windows, macOS, and Linux coverage
- **Trigger Analysis**: Understand when each workflow runs (PR, push, schedule, manual)
- **Documentation**: Create inventory of all workflows and their purposes
</step_1_systematic_workflow_discovery>

<step_2_comprehensive_failure_analysis>
- **Multi-Workflow Error Pattern Detection**: Analyze failures across ALL workflow files, not just the failing one
- **Root Cause Investigation**: Identify underlying causes, not just symptoms
- **Platform-Specific Issues**: Check for platform-specific failure patterns (Windows vs Linux vs macOS)
- **Dependency Conflict Analysis**: Verify package versions and Python versions are consistent
- **Configuration Validation**: Check for configuration file conflicts (CodeQL, clang-format, etc.)
- **Timeout and Resource Analysis**: Identify build timeouts and resource constraints
</step_2_comprehensive_failure_analysis>

<step_3_systematic_consistency_validation>
- **Python Version Enforcement**: Verify Python 3.12+ is enforced across ALL platforms and workflows
- **Package Dependency Consistency**: Ensure all workflows use consistent package versions
- **Build Environment Standardization**: Verify consistent build tools and dependencies
- **Error Handling Uniformity**: Check for consistent error handling patterns
- **Security Configuration**: Validate security tools and configurations are applied uniformly
</step_3_systematic_consistency_validation>

<step_4_comprehensive_fix_implementation>
- **All-Workflow Updates**: When fixing an issue, apply consistent fixes across ALL relevant workflows
- **Platform-Specific Validation**: Test fixes on each platform (Windows, macOS, Linux)
- **Incremental Validation**: Test each fix immediately after implementation
- **Regression Prevention**: Ensure fixes don't break existing functionality
- **Documentation Updates**: Update workflow documentation and comments
</step_4_comprehensive_fix_implementation>

<step_5_end_to_end_validation>
- **Cross-Platform Testing**: Validate workflows work on all supported platforms
- **Dependency Integration Testing**: Ensure all dependencies install and work correctly
- **Build Process Validation**: Verify complete build and test cycles work
- **Error Reporting Verification**: Confirm proper error detection and reporting
- **Performance Impact Assessment**: Check that fixes don't introduce performance regressions
</step_5_end_to_end_validation>

<step_6_systematic_documentation_and_monitoring>
- **Change Documentation**: Document all changes made with rationale
- **Monitoring Setup**: Establish ongoing monitoring for workflow health
- **Preventive Measures**: Implement measures to prevent similar issues
- **Knowledge Transfer**: Update team knowledge and documentation
- **Continuous Improvement**: Identify opportunities for workflow optimization
</step_6_systematic_documentation_and_monitoring>

</comprehensive_workflow_analysis_methodology>

<workflow_failure_pattern_recognition>

<common_failure_patterns>
**Python Version Inconsistencies**:
- Missing `setup-python@v4` actions in workflow jobs
- Inconsistent Python versions across platforms (3.9 vs 3.12)
- Package dependency conflicts due to Python version mismatches
- Requirements files not updated for Python version changes

**Dependency Management Issues**:
- Package name errors (e.g., `zmq` instead of `pyzmq`)
- Version conflicts between different requirements files
- Missing platform-specific dependencies
- Incorrect package installation order

**Build System Problems**:
- CMake cache conflicts between builds
- Compiler version inconsistencies
- Missing build dependencies
- Timeout issues in resource-intensive builds

**Configuration Conflicts**:
- CodeQL configuration file syntax errors
- Clang-format configuration BOM issues
- Conflicting query specifications in CodeQL
- Template file formatting inconsistencies

**Platform-Specific Issues**:
- macOS Homebrew package conflicts
- Windows MSVC build configuration problems
- Linux package manager dependency issues
- Architecture-specific compilation problems
</common_failure_patterns>

<systematic_fix_approach>
**Always Fix ALL Related Issues**:
- When fixing Python version enforcement, update ALL workflow files
- When fixing dependency issues, check ALL platforms and requirements files
- When fixing build issues, validate across ALL build configurations
- When fixing configuration issues, check ALL related config files

**Cross-Platform Validation Requirements**:
- Test Linux builds with GCC and Clang
- Test Windows builds in Debug and Release modes
- Test macOS builds with proper ARM64/Intel optimization
- Verify Python 3.12+ works on all platforms

**Consistency Enforcement**:
- Use identical `setup-python@v4` configuration across all workflows
- Maintain consistent package versions in all requirements files
- Apply uniform error handling and timeout settings
- Ensure consistent dependency installation patterns
</systematic_fix_approach>

</workflow_failure_pattern_recognition>

<workflow_integration>
This comprehensive workflow analysis methodology must be integrated into ALL development activities:
- **Issue Resolution**: Complete workflow analysis before addressing the specific issue
- **Feature Development**: Ensure workflow consistency before adding new features  
- **Code Reviews**: Validate all workflow files for consistency and correctness
- **Documentation Updates**: Check workflow impact of documentation changes
- **Emergency Fixes**: Even urgent fixes must maintain workflow consistency
</workflow_integration>

</priority_workflow_function>

<repository_structure>

<core_technologies>
- **Languages**: C++20, Lua 5.1, Python 3, SQL (MariaDB)
- **Build System**: CMake 3.20+
- **Dependencies**: MariaDB, LuaJIT, ZeroMQ, spdlog, fmt
- **Platforms**: Linux (primary), Windows (supported)
</core_technologies>

<code_organization>
- `src/` - C++ source code (common, map, search, login servers)
- `scripts/` - Lua scripts for game logic, NPCs, missions, quests
- `sql/` - Database schema and migrations
- `tools/` - Development and maintenance utilities
- `documentation/` - Technical documentation and references
</code_organization>

</repository_structure>

<critical_cicd_requirements>

<commit_message_formatting>
⚠️ IMPORTANT: All commits MUST follow strict formatting rules enforced by `tools/ci/git.sh`

<requirements>
- **Title length**: 10-72 characters (STRICTLY enforced - CI will fail if exceeded)
- **No generic messages**: Avoid "Update filename.ext" style commits  
- **No casual language**: Avoid "oops", "whoops", "lol", "lulz", "kek", "kekw"
- **No pipe characters**: Avoid "|" in commit titles
- **Use multi-line format**: For detailed explanations beyond 72 characters, use commit body
</requirements>

<good_examples>
- `Add Function Indexing System with documentation` (47 chars)
- `Fix memory leak in packet handler` (33 chars)  
- `Update quest NPC dialogue for Bastok missions` (45 chars)
</good_examples>

<bad_examples>
- `Complete Function Indexing System implementation with documentation and testing` (80 chars - TOO LONG)
- `Update main.cpp` (Generic message)
- `Oops, fix typo` (Casual language)
</bad_examples>

<note>
If you accidentally create a commit with a title >72 characters, the CI will fail. The only way to fix this is to ensure all future commits follow the proper format, as commit history cannot be rewritten once pushed.
</note>

</commit_message_formatting>

</critical_cicd_requirements>

<development_workflow_enhancement>

<swe_agent_logic>
When working on this repository, follow this enhanced 11-step process for optimal code quality:

<step_1_intent>
- Clearly define what you want to achieve
- Understand the game mechanics or system being implemented
- Consider impact on existing functionality
</step_1_intent>

<step_2_plan>
- Create a concrete plan to reach the goal
- Identify affected files and systems
- Consider database schema changes if needed
</step_2_plan>

<step_3_execute>
- Execute the plan systematically
- Follow existing code patterns and conventions
- Maintain consistency with FFXI retail behavior where applicable
</step_3_execute>

<step_4_multiple_outcomes>
- Evaluate different possible outcomes
- Consider edge cases and error conditions
- Assess which result is optimal for the game experience
</step_4_multiple_outcomes>

<step_5_test>
- Test different approaches and choose the best option
- Use existing test infrastructure where available
- Validate against retail FFXI behavior when possible
</step_5_test>

<step_6_feedback>
- Gather information on why the chosen approach works best
- Document differences from alternatives considered
- Consider maintainability and performance implications
</step_6_feedback>

<step_7_correction>
- Improve the chosen plan to the most optimal version
- Ensure no conflicts with existing code
- Optimize for performance and memory usage
</step_7_correction>

<step_8_validation>
- Verify and confirm that the improved plan works correctly
- Test all affected game systems
- Ensure compliance with coding standards
</step_8_validation>

<step_9_learning>
- Document what was learned and how the code/functionality was improved
- Update relevant documentation
- Share knowledge with the development community
</step_9_learning>

<step_10_repeat>
- If failed or insufficient knowledge gained, repeat from **Intent**
- Iterate until the solution meets quality standards
- Don't hesitate to refactor if a better approach is discovered
</step_10_repeat>

<step_11_outcome>
- Deliver an improved, validated solution that optimally achieves the original goal
- Ensure the solution integrates well with the existing codebase
- Document the final implementation for future reference
</step_11_outcome>

</swe_agent_logic>

</development_workflow_enhancement>

<optimized_ai_development_practices>

<comprehensive_workflow_analysis_practices>
- **Complete System Analysis**: Always analyze ALL workflow files when addressing workflow issues, not just the failing one
- **Cross-Platform Consistency**: Ensure fixes apply consistently across Windows, macOS, and Linux platforms
- **Dependency Chain Validation**: Verify that all dependency installations are consistent and compatible
- **Error Pattern Recognition**: Identify and fix systemic issues that affect multiple workflows
- **Preventive Fix Implementation**: Address root causes to prevent similar issues in the future
</comprehensive_workflow_analysis_practices>

<systematic_workflow_debugging_methodology>
- **Phase 1 - Discovery**: Inventory all workflow files and their purposes
- **Phase 2 - Error Analysis**: Systematically categorize all types of failures
- **Phase 3 - Dependency Mapping**: Understand relationships between workflows and dependencies
- **Phase 4 - Consistency Validation**: Check for version conflicts and configuration mismatches
- **Phase 5 - Comprehensive Fixing**: Apply consistent fixes across all related workflows
- **Phase 6 - End-to-End Testing**: Validate complete workflow functionality
</systematic_workflow_debugging_methodology>

<efficient_problem_analysis>
- **Root Cause Investigation**: Always identify the underlying cause before applying fixes
- **Multi-Factor Analysis**: Consider configuration, template, and build system interactions
- **Systematic Debugging**: Use structured debugging approaches with validation tools
- **Cross-Workflow Impact Assessment**: Understand how changes affect other workflows
- **Platform-Specific Considerations**: Account for differences between operating systems
</efficient_problem_analysis>

<minimal_change_principle>
- **Surgical Modifications**: Make the best and correct possible changes to achieve the best possible outcome
- **Preserve Working Code**: Leverage existing code and ensure compatibility with previous implementations. Only make necessary changes that complement the current codebase while maintaining backwards compatibility with older versions.
- **Incremental Validation**: Test each change immediately after implementation
- **Consistency Maintenance**: Ensure changes maintain consistency across all related files
- **Regression Prevention**: Validate that fixes don't introduce new issues
</minimal_change_principle>

<tool_first_approach>
- **Automated Detection**: Use existing CI tools to identify issues before manual inspection
- **Configuration Validation**: Always verify tool configurations before assuming code issues
- **Template Testing**: Test generated files independently before integrating with build system
- **Workflow Validation Tools**: Use YAML validation and workflow analysis scripts
- **Cross-Platform Testing**: Leverage platform-specific validation tools
</tool_first_approach>

</optimized_ai_development_practices>

<coding_standards>

<cpp_guidelines>
- Follow C++20 modern practices
- Use RAII and smart pointers appropriately
- Prefer `std::format` over printf-style formatting
- Use `constexpr` and `const` where applicable
- Follow the existing naming conventions (CamelCase for classes, snake_case for functions)
</cpp_guidelines>

<lua_guidelines>
- Follow existing script patterns in `scripts/` directory
- Use proper indentation (4 spaces)
- Document complex game mechanics with comments
- Maintain compatibility with LuaJIT 5.1
</lua_guidelines>

<database_guidelines>
- Always provide migration scripts for schema changes
- Use appropriate data types for game values
- Consider performance implications of queries
- Document foreign key relationships
</database_guidelines>

</coding_standards>

<file_management_and_organization>

<directory_structure_requirements>
- Keep files in appropriate directories based on functionality
- Maintain clean separation between server components
- Use descriptive file names that reflect their purpose
- Group related functionality together
</directory_structure_requirements>

<file_headers_and_documentation>
- All C++ files must include GPLv3 license headers
- Add creation date and purpose documentation to new files
- Update modification timestamps in file headers
- Document complex algorithms and game mechanics
</file_headers_and_documentation>

</file_management_and_organization>

<quality_assurance_requirements>

<comprehensive_workflow_validation_standards>

<python_version_enforcement_validation>
**CRITICAL**: All workflows MUST enforce Python 3.12+ consistently across ALL platforms

<validation_requirements>
- **Universal Setup**: Every workflow job that uses Python MUST include `setup-python@v4` with `python-version: '3.12'`
- **Platform Consistency**: Windows, macOS, and Linux workflows MUST use identical Python setup configuration
- **Requirements File Alignment**: All requirements files MUST be compatible with Python 3.12+
- **Package Version Validation**: All Python packages MUST support Python 3.12+
- **CI/CD Integration**: Python version enforcement MUST be validated in CI pipelines
</validation_requirements>

<systematic_validation_process>
```bash
# Step 1: Verify Python 3.12 enforcement across ALL workflows
grep -r "python-version" .github/workflows/ | grep -v "3.12" && echo "❌ Non-3.12 Python versions found" || echo "✅ Python 3.12 enforced"

# Step 2: Check for missing setup-python actions
for file in .github/workflows/*.yml; do
    if grep -q "python\|pip" "$file" && ! grep -q "setup-python" "$file"; then
        echo "❌ $file uses Python but missing setup-python action"
    fi
done

# Step 3: Validate requirements file consistency
python3 -c "
import os
import re
req_files = ['tools/requirements.txt', 'tools/requirements-py312.txt']
for req_file in [f for f in req_files if os.path.exists(f)]:
    print(f'Checking {req_file}...')
    with open(req_file) as f:
        content = f.read()
        if 'zmq>=' in content and 'pyzmq' not in content:
            print(f'❌ {req_file}: Found zmq package instead of pyzmq')
        elif 'pyzmq>=' in content:
            print(f'✅ {req_file}: Correct pyzmq package found')
"
</systematic_validation_process>

</python_version_enforcement_validation>

<workflow_consistency_standards>

<cross_platform_consistency_requirements>
- **Identical Dependencies**: All platforms MUST use consistent package versions and installation methods
- **Uniform Error Handling**: Error detection and reporting MUST be consistent across all platforms
- **Standardized Timeouts**: Build and test timeouts MUST be appropriate for each platform's characteristics
- **Consistent Caching**: Build caching strategies MUST be optimized for each platform
- **Unified Artifact Management**: Artifact upload and download patterns MUST be consistent
</cross_platform_consistency_requirements>

<workflow_structure_validation>
```yaml
# Required structure for ALL workflow files:
name: "workflow_name"
on:
  # Appropriate triggers
concurrency:
  group: ${{ github.workflow }}-${{ github.ref || github.run_id }}
  cancel-in-progress: true
jobs:
  job_name:
    runs-on: platform
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python 3.12
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      # Additional steps...
```
</workflow_structure_validation>

</workflow_consistency_standards>

<systematic_workflow_analysis_checklist>

<pre_fix_analysis_requirements>
- [ ] **Complete Workflow Inventory**: List and categorize ALL workflow files
- [ ] **Failure Pattern Analysis**: Identify common failure patterns across workflows
- [ ] **Dependency Mapping**: Map all dependencies and their versions across platforms
- [ ] **Python Version Audit**: Verify Python 3.12+ enforcement in every workflow
- [ ] **Configuration Consistency**: Check for consistent tool configurations
- [ ] **Platform Coverage Assessment**: Ensure proper Windows/macOS/Linux coverage
- [ ] **Error Handling Review**: Validate error detection and reporting mechanisms
- [ ] **Resource Optimization**: Check timeout settings and resource utilization
</pre_fix_analysis_requirements>

<comprehensive_fix_validation_checklist>
- [ ] **All Workflows Updated**: Consistent fixes applied across ALL relevant workflows
- [ ] **Python 3.12 Enforced**: Every Python-using workflow explicitly sets Python 3.12
- [ ] **Dependencies Validated**: All package installations tested and working
- [ ] **Platform Testing**: Fixes validated on Windows, macOS, and Linux
- [ ] **Error Handling Tested**: Error conditions properly detected and reported
- [ ] **Performance Validated**: No performance regressions introduced
- [ ] **Documentation Updated**: All changes properly documented
- [ ] **Regression Testing**: Existing functionality confirmed working
</comprehensive_fix_validation_checklist>

</systematic_workflow_analysis_checklist>

</comprehensive_workflow_validation_standards>

<git_commit_message_standards>
Tools: `tools/ci/git.sh`

<standards>
- **Title length**: EXACTLY 10-72 characters (CI FAILS if outside this range)
- **Character count**: Always verify with `echo "your title" | wc -c` before committing
- **No pipe characters**: Avoid "|" symbols in commit titles
- **No generic messages**: Never use "Update filename.ext" or similar auto-generated messages
- **No casual language**: Strictly avoid "oops", "whoops", "lol", "lulz", "kek", "kekw"
- **Multi-line commits**: Use commit body (not title) for explanations beyond 72 chars
- **Be descriptive**: Focus on WHAT changed and WHY, not just the file modified
</standards>
</git_commit_message_standards>

<general_file_format_standards>
Tools: `tools/ci/general.sh`

<standards>
- **File endings**: All files must end with a single newline character
- **Indentation**: Use 4 spaces instead of tab characters (strictly enforced)
- **Line spacing**: No multiple consecutive newline characters
- **Whitespace**: Remove trailing whitespace from all lines
</standards>
</general_file_format_standards>

<cpp_code_standards>
Tools: `tools/ci/cpp.sh`

<standards>
- **Memory management**: Use `destroy(ptr)` or `destroy_arr(ptr)` instead of naked `delete`
- **Include paths**: Use absolute paths, not relative includes with "../"
- **AI Events**: Document all `.triggerListener()` calls in `documentation/AI_Events.txt`
- **Static analysis**: Code must pass cppcheck with performance, portability, and information checks
- **Formatting**: Must pass clang-format-18 with project .clang-format configuration
</standards>

<configuration_file_validation>
- **UTF-8 BOM Detection**: Check configuration files (especially `.clang-format`) for UTF-8 Byte Order Mark (BOM) that can prevent proper parsing
- **Template Files**: Ensure template files (*.in) are pre-formatted to match clang-format-18 output to prevent CI failures
- **Generated Files**: Validate that CMake-generated files comply with formatting standards before CI runs
</configuration_file_validation>

<debugging_clang_format_issues>
- **Configuration Testing**: Run `clang-format-18 --dump-config` to verify configuration is being read correctly
- **BOM Removal**: Use `sed -i '1s/^\xEF\xBB\xBF//' filename` to remove UTF-8 BOM from configuration files
- **Template Validation**: Test template file formatting with `clang-format-18 --dry-run --Werror` before committing
</debugging_clang_format_issues>
</cpp_code_standards>

<lua_code_standards>
Tools: `tools/ci/lua.sh`

<standards>
- **Syntax validation**: Code must pass luacheck with project-specific globals
- **Style consistency**: Follow project lua style checker requirements
- **Global usage**: Only use documented global functions and objects
- **Complexity**: Maximum cyclomatic complexity of 30
</standards>
</lua_code_standards>

<python_code_standards>
Tools: `tools/ci/python.sh`

<standards>
- **Linting**: Code must pass pylint and black formatting
- **Dependencies**: Use only packages listed in tools/requirements.txt
</standards>
</python_code_standards>

<sql_standards>
Tools: `tools/ci/sql.sh`

<standards>
- **Syntax validation**: All SQL files must be syntactically correct
- **Price consistency**: Maintain consistency with price checker validation
</standards>
</sql_standards>

<license_header_requirements>
Tools: `tools/ci/detect_license_headers.py`

<requirements>
- **GPLv3 headers**: All C++ source files must include proper GPLv3 license headers
- **Creation date**: Include creation date and purpose in file headers
- **Modification tracking**: Update modification timestamps appropriately
</requirements>
</license_header_requirements>

<pre_commit_checks>
- **ALWAYS verify commit message length**: Use `echo "your commit title" | wc -c` to count characters
- Run clang-format for C++ code formatting
- Execute cppcheck for static analysis
- Validate Lua syntax with luacheck
- Check for proper license headers
- Scan for security vulnerabilities
- Validate commit message formatting
- Check general file format standards
</pre_commit_checks>

<cicd_troubleshooting_guide>

<comprehensive_workflow_failure_diagnosis>

<systematic_failure_analysis_process>
**Step 1: Complete Error Collection**
```bash
# Collect all workflow failure information
find .github/workflows -name "*.yml" -exec echo "=== {} ===" \; -exec cat {} \;

# Check for syntax errors in all workflow files
for file in .github/workflows/*.yml; do
    echo "Validating $file..."
    python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>&1 | grep -v "^$" || echo "✅ $file syntax valid"
done

# Analyze Python setup consistency
python3 << 'EOF'
import yaml, glob, re
workflows = glob.glob('.github/workflows/*.yml')
python_setups = []
for wf in workflows:
    with open(wf) as f:
        content = f.read()
        if re.search(r'python|pip', content, re.I):
            python_setups.append((wf, 'setup-python' in content, re.findall(r'python-version.*[\'"]([^\'\"]+)', content)))
for wf, has_setup, versions in python_setups:
    print(f"{wf}: setup={has_setup}, versions={versions}")
EOF
```

**Step 2: Cross-Platform Issue Detection**
```bash
# Check for platform-specific issues
grep -r "runs-on:" .github/workflows/ | sort | uniq -c

# Validate Windows-specific configurations
grep -A 10 -B 2 "windows" .github/workflows/*.yml

# Check macOS-specific configurations  
grep -A 10 -B 2 "macos" .github/workflows/*.yml

# Verify Linux configurations
grep -A 10 -B 2 "ubuntu" .github/workflows/*.yml
```

**Step 3: Dependency and Package Analysis**
```bash
# Check for package installation inconsistencies
grep -r "pip install" .github/workflows/ | sort | uniq

# Validate requirements file references
grep -r "requirements" .github/workflows/ | sort

# Check for dependency conflicts
python3 << 'EOF'
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
    print("❌ Package version conflicts:")
    for pkg, files in conflicts.items():
        print(f"  {pkg}: {files}")
else:
    print("✅ No package conflicts found")
EOF
```
</systematic_failure_analysis_process>

<specific_failure_pattern_solutions>

<python_version_enforcement_failures>
**Problem**: Inconsistent Python versions across workflows
**Systematic Solution**:
```bash
# Fix ALL workflows to use Python 3.12
for file in .github/workflows/*.yml; do
    if grep -q "python\|pip" "$file" && ! grep -q "setup-python@v4" "$file"; then
        echo "Fixing Python setup in $file..."
        # Insert Python setup after checkout action
        sed -i '/uses: actions\/checkout@v4/a\      - name: Set up Python 3.12\n        uses: actions/setup-python@v4\n        with:\n          python-version: '\''3.12'\''' "$file"
    fi
done

# Verify all Python versions are 3.12
grep -r "python-version" .github/workflows/ | grep -v "3.12"
```
</python_version_enforcement_failures>

<codeql_configuration_conflicts>
**Problem**: CodeQL configuration file conflicts
**Systematic Solution**:
```bash
# Check CodeQL workflow configuration
cat .github/workflows/codeql_analysis.yml

# Validate CodeQL config file
if [ -f .github/codeql/codeql-config.yml ]; then
    echo "Checking CodeQL config file..."
    python3 -c "import yaml; yaml.safe_load(open('.github/codeql/codeql-config.yml'))"
fi

# Fix common CodeQL issues
python3 << 'EOF'
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
    print("✅ CodeQL uses config file properly")
else:
    print("⚠️ CodeQL configuration may need adjustment")
EOF
```
</codeql_configuration_conflicts>

<build_timeout_and_performance_issues>
**Problem**: Build timeouts and performance issues
**Systematic Solution**:
```bash
# Add CI_BUILD_FAST environment variable to lengthy builds
for file in .github/workflows/*.yml; do
    if grep -q "cmake.*build" "$file"; then
        echo "Adding build optimization to $file..."
        # Add CI_BUILD_FAST environment variable
        if ! grep -q "CI_BUILD_FAST" "$file"; then
            sed -i '/cmake.*build/i\        env:\n          CI_BUILD_FAST: "true"' "$file"
        fi
    fi
done

# Optimize parallel builds
sed -i 's/cmake --build build$/cmake --build build --parallel 4/g' .github/workflows/*.yml
sed -i 's/-j2/-j4/g' .github/workflows/*.yml

# Add appropriate timeouts
for file in .github/workflows/*.yml; do
    if grep -q "Build\|build" "$file" && ! grep -q "timeout-minutes" "$file"; then
        echo "Adding timeout to build steps in $file..."
        sed -i '/name:.*[Bb]uild/a\        timeout-minutes: 30' "$file"
    fi
done
```
</build_timeout_and_performance_issues>

<package_dependency_conflicts>
**Problem**: Package name errors and dependency conflicts
**Systematic Solution**:
```bash
# Fix common package name errors
for req_file in tools/requirements*.txt; do
    if [ -f "$req_file" ]; then
        echo "Fixing package names in $req_file..."
        sed -i 's/^zmq>=/pyzmq>=/g' "$req_file"
        sed -i 's/^mysql-connector-python/mysql-connector-python/g' "$req_file"
    fi
done

# Validate Python 3.12 compatibility
python3 << 'EOF'
import pkg_resources
import sys

req_files = ['tools/requirements.txt', 'tools/requirements-py312.txt']
for req_file in [f for f in req_files if __import__('os').path.exists(f)]:
    print(f"Validating {req_file}...")
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
                    print(f"  ✅ {req.project_name}: Valid requirement")
                except Exception as e:
                    incompatible.append(f"{line}: {e}")
        
        if incompatible:
            print(f"❌ Issues in {req_file}:")
            for issue in incompatible:
                print(f"    {issue}")
        else:
            print(f"✅ {req_file}: All requirements valid")
            
    except Exception as e:
        print(f"❌ Error reading {req_file}: {e}")
EOF
```
</package_dependency_conflicts>

</specific_failure_pattern_solutions>

</comprehensive_workflow_failure_diagnosis>

<configuration_file_issues>
- Check for UTF-8 BOM in `.clang-format`, `.clang-tidy`, and other config files
- Verify configuration syntax with respective tool's `--dump-config` or validation flags
- Ensure proper file encoding (UTF-8 without BOM)
- Validate YAML syntax in all workflow files
- Check for conflicting configuration specifications
</configuration_file_issues>

<template_file_formatting>
- Pre-format template files (*.in) to match final formatting requirements
- Test generated files with formatting tools before committing templates
- Include all necessary headers and macros in templates
- Validate CMake variable substitution doesn't break formatting
- Test template compilation with actual variable values
</template_file_formatting>

<build_system_integration>
- Verify CMake variable substitution doesn't break formatting
- Test template compilation with actual variable values
- Validate generated files pass all CI checks
- Ensure build caching works properly across platforms
- Test parallel build configurations
</build_system_integration>

</cicd_troubleshooting_guide>

<dependency_management>
- **Python packages**: Track all packages in tools/requirements.txt
- **C++ libraries**: Document CMake dependencies (MariaDB, LuaJIT, ZeroMQ, OpenSSL)
- **System packages**: Document required system dependencies for builds
- **Security updates**: Regularly check for deprecated packages and vulnerabilities
- **Version pinning**: Use specific versions for critical dependencies
- **Documentation**: Document all external dependencies and their purposes
- **Header-only preference**: Prefer header-only libraries when possible
</dependency_management>

<error_prevention>
- Check for truncation issues in string operations
- Validate shell scripts with shellcheck
- Ensure proper file permissions
- Handle edge cases gracefully
- Follow memory safety guidelines for C++
- Validate all user inputs and database queries
</error_prevention>

</quality_assurance_requirements>

<testing_guidelines>

<unit_testing>
- Write tests for new C++ functionality where applicable
- Test Lua scripts with game scenario validation
- Verify database migrations work correctly
- Test cross-platform compatibility
</unit_testing>

<integration_testing>
- Validate server startup and shutdown procedures
- Test client-server communication protocols
- Verify game mechanics work as expected
- Test performance under load
</integration_testing>

</testing_guidelines>

<performance_considerations>

<memory_management>
- Use appropriate container types for data structures
- Avoid memory leaks in long-running server processes
- Consider cache-friendly data layouts
- Profile memory usage for large datasets
</memory_management>

<threading_and_concurrency>
- Be aware of thread safety in server components
- Use appropriate synchronization primitives
- Avoid race conditions in shared data access
- Consider performance impact of locking
</threading_and_concurrency>

</performance_considerations>

<game_specific_guidelines>

<ffxi_retail_accuracy>
- Strive for accurate recreation of retail FFXI behavior
- Research retail mechanics before implementing features
- Document deviations from retail when necessary
- Consider player experience and game balance
</ffxi_retail_accuracy>

<content_implementation>
- Follow existing patterns for NPCs, monsters, and items
- Use appropriate item IDs and stats from retail data
- Implement quests and missions with proper progression
- Ensure proper zone and map functionality
</content_implementation>

</game_specific_guidelines>

<contribution_guidelines>

<code_review_process>
- All changes require peer review
- Validate changes against retail FFXI when possible
- Test on multiple platforms before merging
- Document breaking changes thoroughly
</code_review_process>

<community_interaction>
- Be respectful and helpful to contributors
- Provide constructive feedback on code reviews
- Share knowledge and best practices
- Help newcomers understand the codebase
</community_interaction>

</contribution_guidelines>

<changelog_management>

<landsandboat_format_compliance>
This repository follows the exact changelog format used by LandSandBoat/server:

```markdown
## [Project Name] Changelog (YYYY-MM-DD)
- [component] feature description [[#PR](link), [patch](patch-link)] (contributors)
```
</landsandboat_format_compliance>

<component_tags>
Use these standard component tags in PR titles and changelog entries:
- `[sql]` - Database schema changes and SQL modifications
- `[lua]` - Lua script implementations (quests, NPCs, game logic)
- `[cpp]` - C++ core server code changes
- `[core]` - Core server functionality and architecture
- `[fix]` - Bug fixes and error corrections
- `[quest]` - Quest content implementations
- `[mission]` - Mission content and storyline
- `[documentation]` - Documentation updates and improvements
- `[tools]` - Development tools and utilities
- `[ci/cd]` - Continuous integration and deployment changes
</component_tags>

<changelog_generation>
- Use `tools/generate_changelog.py` for automated changelog generation
- Follow the bi-weekly schedule (1st and 15th of each month) like LandSandBoat
- Store changelogs in `changelogs/` directory with `changelog-YYYY-MM-DD.md` format
- Include both PR links and patch links for each entry
- Remove real names from contributor lists for privacy
</changelog_generation>

<integration_with_development_workflow>
- PR titles should be changelog-ready with appropriate component tags
- Major infrastructure changes should be documented in both changelog and ROADMAP.md
- Use `tools/log_manager.py` to track development activities alongside changelog entries
</integration_with_development_workflow>

</changelog_management>

<security_considerations>

<input_validation>
- Validate all user inputs from game clients
- Sanitize database inputs to prevent injection
- Implement rate limiting for network operations
- Handle malformed packets gracefully
</input_validation>

<access_control>
- Implement proper GM command authorization
- Validate player permissions for actions
- Secure administrative interfaces
- Log security-relevant events
</access_control>

</security_considerations>

<development_planning_and_roadmap>

<strategic_improvements>
- Follow the development roadmap in `ROADMAP.md` for prioritized improvements
- Focus on infrastructure modernization and code quality enhancements
- Plan feature development based on community needs and retail accuracy
- Consider performance and scalability in all architectural decisions
</strategic_improvements>

<continuous_improvement_process>
- Regular assessment of codebase health and technical debt
- Automated dependency tracking with vulnerability monitoring
- Performance benchmarking and optimization initiatives
- Community feedback integration into development priorities
</continuous_improvement_process>

<function_indexing_and_documentation>
- Maintain comprehensive API documentation for all components
- Index functions across C++, Lua, and Python codebases
- Document cross-component interactions and dependencies
- Ensure searchable and accessible developer resources
</function_indexing_and_documentation>

</development_planning_and_roadmap>

<getting_help>
- Check existing documentation in `documentation/` directory
- Review similar implementations in the codebase
- Ask questions in GitHub discussions
- Consult the Final Fantasy XI community wikis for retail behavior
</getting_help>

<practical_tips_for_contributors>

<commit_message_best_practices>
To avoid CI failures, always check your commit message length before committing:

```bash
# Check character count of your commit title
echo "Your commit message here" | wc -c

# Example: Good commit message (54 characters)
echo "Complete Function Indexing System with docs and tests" | wc -c
# Output: 55 (includes newline, so actual title is 54 chars - GOOD)

# Example: Bad commit message (80 characters) 
echo "Complete Function Indexing System implementation with documentation and testing" | wc -c
# Output: 81 (includes newline, so actual title is 80 chars - TOO LONG)
```

<quick_commit_message_templates>
All ≤72 chars:
- `Add [feature] with [brief description]`
- `Fix [issue] in [component]`
- `Update [component] for [reason]` 
- `Refactor [component] to [improvement]`
- `Remove [deprecated feature/code]`
</quick_commit_message_templates>
</commit_message_best_practices>

<common_cicd_issue_resolution>

<configuration_file_problems>
```bash
# Check for UTF-8 BOM in configuration files
file -bi .clang-format
hexdump -C .clang-format | head -1

# Remove UTF-8 BOM if detected (EF BB BF bytes)
sed -i '1s/^\xEF\xBB\xBF//' .clang-format

# Verify configuration is readable
clang-format-18 --dump-config > /dev/null
```
</configuration_file_problems>

<template_file_formatting_issues>
```bash
# Test template formatting before committing
cmake -B build -S .
clang-format-18 --dry-run --Werror build/src/common/version.cpp

# Fix template formatting to match expected output
clang-format-18 -i src/common/version.cpp.in
```
</template_file_formatting_issues>

<build_and_validation_workflow>
```bash
# Complete validation pipeline
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug ..
make -j$(nproc)
cd .. && tools/ci/cpp.sh
tools/ci/general.sh
```
</build_and_validation_workflow>

</common_cicd_issue_resolution>

</practical_tips_for_contributors>

<tools_and_resources>

<development_tools>
- Use `tools/dbtool.py` for database operations and migrations
- Run `tools/ci/` scripts for quality checks and validation
- Use `tools/announce.py` for server-wide messaging
- Use `tools/vulnerability_scanner.py` for security auditing
- Use `tools/price_checker.py` for item price validation
- Use `tools/log_manager.py` for log maintenance
- Use `tools/generate_changelog.py` for automated changelog generation
</development_tools>

<workflow_analysis_tools>

<comprehensive_workflow_validation>
```bash
# Complete workflow file discovery and analysis
find .github/workflows -name "*.yml" -o -name "*.yaml" | sort

# Validate Python version consistency across all workflows
grep -r "python-version" .github/workflows/ | sort

# Check for missing setup-python actions
grep -L "setup-python" .github/workflows/*.yml

# Verify package dependency consistency
grep -r "requirements" .github/workflows/ | sort

# Check for platform coverage
grep -r "runs-on:" .github/workflows/ | sort | uniq

# Validate workflow trigger consistency
grep -r "on:" .github/workflows/ -A 5
```
</comprehensive_workflow_validation>

<systematic_fix_validation>
```bash
# Test workflow YAML syntax
for file in .github/workflows/*.yml; do
    echo "Validating $file..."
    python3 -c "import yaml; yaml.safe_load(open('$file'))" || echo "SYNTAX ERROR in $file"
done

# Check Python 3.12 enforcement across ALL workflows
python3 << 'EOF'
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
                            python_issues.append(f"{workflow_file}:{job_name} uses Python {python_version} instead of 3.12")
                
                # Check if job needs Python but doesn't set it up
                needs_python = any('python' in str(step).lower() or 'pip' in str(step).lower() for step in steps)
                if needs_python and not has_python_setup:
                    python_issues.append(f"{workflow_file}:{job_name} needs Python but missing setup-python action")

if python_issues:
    print("❌ Python version issues found:")
    for issue in python_issues:
        print(f"  {issue}")
else:
    print("✅ All workflows properly enforce Python 3.12")
EOF

# Validate requirements file consistency
python3 << 'EOF'
import os
import re

req_files = ['tools/requirements.txt', 'tools/requirements-py312.txt']
existing_files = [f for f in req_files if os.path.exists(f)]

if not existing_files:
    print("❌ No requirements files found")
    exit(1)

print("📋 Requirements file analysis:")
for req_file in existing_files:
    with open(req_file, 'r') as f:
        lines = f.readlines()
    
    packages = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            package_match = re.match(r'^([a-zA-Z0-9_-]+)', line)
            if package_match:
                packages.append(package_match.group(1))
    
    print(f"  {req_file}: {len(packages)} packages")
    
    # Check for common problematic packages
    if 'zmq' in packages:
        print(f"    ⚠️  Found 'zmq' package - should be 'pyzmq'")
    if 'pyzmq' in packages:
        print(f"    ✅ Found 'pyzmq' package")
EOF
```
</systematic_fix_validation>

<cross_platform_testing_commands>
```bash
# Test Linux workflow components
python3 -c "
import subprocess
import sys

def test_linux_deps():
    try:
        # Test package installation simulation
        result = subprocess.run(['apt-cache', 'show', 'libmariadb-dev-compat'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print('✅ Linux dependencies available')
        else:
            print('❌ Linux dependency issues')
    except Exception as e:
        print(f'⚠️  Cannot test Linux deps: {e}')

test_linux_deps()
"

# Validate workflow file structure
python3 << 'EOF'
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
                        issues.append(f"{workflow_file}: Missing required section '{section}'")
                
                # Check job structure
                jobs = workflow.get('jobs', {})
                for job_name, job_config in jobs.items():
                    if 'runs-on' not in job_config:
                        issues.append(f"{workflow_file}:{job_name}: Missing 'runs-on'")
                    
                    if 'steps' not in job_config:
                        issues.append(f"{workflow_file}:{job_name}: Missing 'steps'")
                        
            except yaml.YAMLError as e:
                issues.append(f"{workflow_file}: YAML syntax error - {e}")
    
    if issues:
        print("❌ Workflow structure issues:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ All workflows have valid structure")
        return True

validate_workflow_structure()
EOF

# Check for consistent timeout and resource settings
grep -r "timeout" .github/workflows/ | sort
grep -r "concurrency" .github/workflows/ | sort
```
</cross_platform_testing_commands>

</workflow_analysis_tools>

<cicd_debugging_tools>
<configuration_validation>
- `clang-format-18 --dump-config` - Verify clang-format configuration parsing
- `file -bi filename` - Check file encoding and detect BOM presence
- `hexdump -C filename | head -1` - Examine file headers for BOM bytes (EF BB BF)
</configuration_validation>

<template_testing>
- `cmake -DCMAKE_BUILD_TYPE=Debug ..` - Generate files for testing
- `clang-format-18 --dry-run --Werror file.cpp` - Test formatting without changes
- `diff -u expected.cpp generated.cpp` - Compare formatting expectations
</template_testing>

<build_validation>
- `cmake --build . --parallel` - Test compilation of generated files
- `tools/ci/cpp.sh` - Run complete C++ validation pipeline
- `git diff --check` - Detect whitespace and formatting issues
</build_validation>
</cicd_debugging_tools>

<documentation_and_references>
- Consult `documentation/` for technical references and specifications
- Review `ROADMAP.md` for development priorities and improvement plans
- Use existing changelog generation tools in `tools/generate_changelog.py`
- Check `tools/requirements.txt` for Python dependency management
- Follow changelog format in `changelogs/` directory matching LandSandBoat/server structure
</documentation_and_references>

<function_index>
Refer to `ROADMAP.md` for comprehensive function indexing including:
- **C++ Core Components**: Server architecture, subsystems, and key classes
- **Python Tools**: Development utilities, CI/CD scripts, and automation tools  
- **Lua Framework**: Game mechanics, quest system, and event handlers
- **Database Schema**: Core tables, relationships, and data structures
</function_index>

<quality_assurance>
- All changes must pass CI/CD pipeline checks defined in `tools/ci/`
- Follow the 11-step development workflow documented above
- Ensure compliance with coding standards for each language
- Validate changes against retail FFXI behavior when applicable
</quality_assurance>

</tools_and_resources>

<conclusion>
Remember: This is a community-driven project focused on preserving and recreating the Final Fantasy XI experience. Quality, accuracy, and maintainability are our top priorities. Consult the roadmap for current development priorities and improvement plans.
</conclusion>

<github_copilot_agent_best_practices>

<systematic_workflow_analysis_for_copilot_agents>
Following GitHub's best practices for Copilot coding agents, this repository implements comprehensive workflow analysis requirements:

<comprehensive_analysis_methodology>
- **Always Analyze ALL Workflows**: When addressing workflow issues, examine every workflow file in `.github/workflows/`, not just the failing one
- **Cross-Platform Consistency**: Ensure fixes are applied consistently across Windows, macOS, and Linux platforms
- **Systematic Root Cause Analysis**: Identify underlying causes rather than treating symptoms
- **Comprehensive Validation**: Test all related components after making changes
- **Documentation Integration**: Update documentation to reflect workflow improvements
</comprehensive_analysis_methodology>

<workflow_fix_validation_standards>
- **Python Version Enforcement**: Verify Python 3.12+ is consistently enforced across ALL workflow jobs
- **Dependency Consistency**: Ensure package versions and installation methods are uniform
- **Error Handling Uniformity**: Implement consistent error detection and reporting
- **Performance Optimization**: Address timeout issues and resource constraints systematically
- **Security Configuration**: Maintain consistent security tool configurations
</workflow_fix_validation_standards>

<continuous_improvement_integration>
- **Proactive Issue Prevention**: Implement measures to prevent similar workflow issues
- **Monitoring and Alerting**: Establish ongoing workflow health monitoring
- **Knowledge Base Updates**: Update instructions and documentation based on lessons learned
- **Team Knowledge Sharing**: Document workflow improvements for team benefit
- **Automated Validation**: Integrate workflow validation into development processes
</continuous_improvement_integration>

</systematic_workflow_analysis_for_copilot_agents>

<copilot_agent_workflow_commands>

<essential_validation_commands>
```bash
# Complete workflow analysis command set
echo "🔍 COMPREHENSIVE WORKFLOW ANALYSIS"

# Step 1: Workflow Discovery and Inventory
echo "📋 Step 1: Workflow Discovery"
find .github/workflows -name "*.yml" -o -name "*.yaml" | sort
echo "Total workflows: $(find .github/workflows -name "*.yml" -o -name "*.yaml" | wc -l)"

# Step 2: Python Version Enforcement Validation
echo "🐍 Step 2: Python Version Analysis"
grep -r "python-version" .github/workflows/ | grep -v "3.12" && echo "❌ Non-3.12 versions found" || echo "✅ Python 3.12 enforced"

# Step 3: Cross-Platform Consistency Check
echo "🌐 Step 3: Platform Coverage"
echo "Platforms used:"
grep -r "runs-on:" .github/workflows/ | cut -d: -f3 | sort | uniq -c

# Step 4: Dependency Analysis
echo "📦 Step 4: Dependency Consistency"
echo "Package installation patterns:"
grep -r "pip install\|requirements" .github/workflows/ | sort | uniq

# Step 5: Error Pattern Detection
echo "🚨 Step 5: Error Pattern Analysis"
grep -r "timeout\|fail\|error" .github/workflows/ | wc -l | xargs echo "Error handling references:"

# Step 6: Configuration Validation
echo "⚙️ Step 6: Configuration Files"
for config in .clang-format .clang-tidy .github/codeql/codeql-config.yml; do
    if [ -f "$config" ]; then
        echo "✅ $config exists"
        # Check for UTF-8 BOM
        if file "$config" | grep -q "BOM"; then
            echo "⚠️  $config has UTF-8 BOM"
        fi
    else
        echo "❌ $config missing"
    fi
done

echo "✅ COMPREHENSIVE WORKFLOW ANALYSIS COMPLETE"
```
</essential_validation_commands>

<automated_fix_validation>
```bash
# Automated workflow fix validation
echo "🔧 AUTOMATED WORKFLOW FIX VALIDATION"

# Validate Python 3.12 enforcement across all workflows
python3 << 'EOF'
import yaml
import glob
import sys

print("🐍 Validating Python 3.12 enforcement...")
workflows = glob.glob('.github/workflows/*.yml')
issues = []

for workflow_file in workflows:
    with open(workflow_file, 'r') as f:
        workflow = yaml.safe_load(f)
    
    jobs = workflow.get('jobs', {})
    for job_name, job_config in jobs.items():
        steps = job_config.get('steps', [])
        
        # Check if job uses Python
        uses_python = any(
            'python' in str(step).lower() or 
            'pip' in str(step).lower() or
            step.get('uses', '').startswith('actions/setup-python')
            for step in steps
        )
        
        if uses_python:
            # Check for proper Python setup
            python_setup = [step for step in steps if step.get('uses', '').startswith('actions/setup-python')]
            
            if not python_setup:
                issues.append(f"{workflow_file}:{job_name} - Missing setup-python action")
            else:
                for setup in python_setup:
                    version = setup.get('with', {}).get('python-version')
                    if version != '3.12':
                        issues.append(f"{workflow_file}:{job_name} - Python version {version} instead of 3.12")

if issues:
    print("❌ Python version enforcement issues:")
    for issue in issues:
        print(f"  {issue}")
    sys.exit(1)
else:
    print("✅ All workflows properly enforce Python 3.12")
EOF

# Validate YAML syntax in all workflows
echo "📝 Validating YAML syntax..."
for file in .github/workflows/*.yml; do
    python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null && echo "✅ $file" || echo "❌ $file - YAML syntax error"
done

echo "✅ AUTOMATED VALIDATION COMPLETE"
```
</automated_fix_validation>

</copilot_agent_workflow_commands>

</github_copilot_agent_best_practices>
