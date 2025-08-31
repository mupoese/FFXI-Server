# Copilot Instructions for LandSandBoat Server

<repository_context>
This repository is an open-source server emulator for Final Fantasy XI (FFXI), written primarily in C++ with Lua scripting support.
</repository_context>

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

<efficient_problem_analysis>
- **Root Cause Investigation**: Always identify the underlying cause before applying fixes
- **Multi-Factor Analysis**: Consider configuration, template, and build system interactions
- **Systematic Debugging**: Use structured debugging approaches with validation tools
</efficient_problem_analysis>

<minimal_change_principle>
- **Surgical Modifications**: Make the best and correct possible changes to achieve the best possible outcome
- **Preserve Working Code**: Leverage existing code and ensure compatibility with previous implementations. Only make necessary changes that complement the current codebase while maintaining backwards compatibility with older versions.
- **Incremental Validation**: Test each change immediately after implementation
</minimal_change_principle>

<tool_first_approach>
- **Automated Detection**: Use existing CI tools to identify issues before manual inspection
- **Configuration Validation**: Always verify tool configurations before assuming code issues
- **Template Testing**: Test generated files independently before integrating with build system
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
<configuration_file_issues>
- Check for UTF-8 BOM in `.clang-format`, `.clang-tidy`, and other config files
- Verify configuration syntax with respective tool's `--dump-config` or validation flags
- Ensure proper file encoding (UTF-8 without BOM)
</configuration_file_issues>

<template_file_formatting>
- Pre-format template files (*.in) to match final formatting requirements
- Test generated files with formatting tools before committing templates
- Include all necessary headers and macros in templates
</template_file_formatting>

<build_system_integration>
- Verify CMake variable substitution doesn't break formatting
- Test template compilation with actual variable values
- Validate generated files pass all CI checks
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
