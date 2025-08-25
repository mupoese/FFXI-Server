# Copilot Instructions for LandSandBoat Server

This repository is an open-source server emulator for Final Fantasy XI (FFXI), written primarily in C++ with Lua scripting support.

## Repository Structure and Guidelines

### Core Technologies
- **Languages**: C++20, Lua 5.1, Python 3, SQL (MariaDB)
- **Build System**: CMake 3.20+
- **Dependencies**: MariaDB, LuaJIT, ZeroMQ, spdlog, fmt
- **Platforms**: Linux (primary), Windows (supported)

### Code Organization
- `src/` - C++ source code (common, map, search, login servers)
- `scripts/` - Lua scripts for game logic, NPCs, missions, quests
- `sql/` - Database schema and migrations
- `tools/` - Development and maintenance utilities
- `documentation/` - Technical documentation and references

### Critical CI/CD Requirements

**⚠️ IMPORTANT: Commit Message Formatting Requirements**

All commits MUST follow these strict formatting rules enforced by `tools/ci/git.sh`:

- **Title length**: 10-72 characters (STRICTLY enforced - CI will fail if exceeded)
- **No generic messages**: Avoid "Update filename.ext" style commits  
- **No casual language**: Avoid "oops", "whoops", "lol", "lulz", "kek", "kekw"
- **No pipe characters**: Avoid "|" in commit titles
- **Use multi-line format**: For detailed explanations beyond 72 characters, use commit body

**Examples of GOOD commit titles (≤72 chars):**
- `Add Function Indexing System with documentation` (47 chars)
- `Fix memory leak in packet handler` (33 chars)  
- `Update quest NPC dialogue for Bastok missions` (45 chars)

**Examples of BAD commit titles:**
- `Complete Function Indexing System implementation with documentation and testing` (80 chars - TOO LONG)
- `Update main.cpp` (Generic message)
- `Oops, fix typo` (Casual language)

### Development Workflow Enhancement (SWE Agent Logic)

When working on this repository, follow this enhanced 11-step process for optimal code quality:

1. **Intent**
   - Clearly define what you want to achieve
   - Understand the game mechanics or system being implemented
   - Consider impact on existing functionality

2. **Plan**
   - Create a concrete plan to reach the goal
   - Identify affected files and systems
   - Consider database schema changes if needed

3. **Execute**
   - Execute the plan systematically
   - Follow existing code patterns and conventions
   - Maintain consistency with FFXI retail behavior where applicable

4. **Multiple Outcomes**
   - Evaluate different possible outcomes
   - Consider edge cases and error conditions
   - Assess which result is optimal for the game experience

5. **Test**
   - Test different approaches and choose the best option
   - Use existing test infrastructure where available
   - Validate against retail FFXI behavior when possible

6. **Feedback**
   - Gather information on why the chosen approach works best
   - Document differences from alternatives considered
   - Consider maintainability and performance implications

7. **Correction**
   - Improve the chosen plan to the most optimal version
   - Ensure no conflicts with existing code
   - Optimize for performance and memory usage

8. **Validation**
   - Verify and confirm that the improved plan works correctly
   - Test all affected game systems
   - Ensure compliance with coding standards

9. **Learning**
   - Document what was learned and how the code/functionality was improved
   - Update relevant documentation
   - Share knowledge with the development community

10. **Repeat**
    - If failed or insufficient knowledge gained, repeat from **Intent**
    - Iterate until the solution meets quality standards
    - Don't hesitate to refactor if a better approach is discovered

11. **Outcome**
    - Deliver an improved, validated solution that optimally achieves the original goal
    - Ensure the solution integrates well with the existing codebase
    - Document the final implementation for future reference

### Coding Standards

#### C++ Guidelines
- Follow C++20 modern practices
- Use RAII and smart pointers appropriately
- Prefer `std::format` over printf-style formatting
- Use `constexpr` and `const` where applicable
- Follow the existing naming conventions (CamelCase for classes, snake_case for functions)

#### Lua Guidelines
- Follow existing script patterns in `scripts/` directory
- Use proper indentation (4 spaces)
- Document complex game mechanics with comments
- Maintain compatibility with LuaJIT 5.1

#### Database Guidelines
- Always provide migration scripts for schema changes
- Use appropriate data types for game values
- Consider performance implications of queries
- Document foreign key relationships

### File Management and Organization

#### Directory Structure Requirements
- Keep files in appropriate directories based on functionality
- Maintain clean separation between server components
- Use descriptive file names that reflect their purpose
- Group related functionality together

#### File Headers and Documentation
- All C++ files must include GPLv3 license headers
- Add creation date and purpose documentation to new files
- Update modification timestamps in file headers
- Document complex algorithms and game mechanics

### Quality Assurance Requirements

#### Git Commit Message Standards (tools/ci/git.sh)
- **Title length**: EXACTLY 10-72 characters (CI FAILS if outside this range)
- **Character count**: Always verify with `echo "your title" | wc -c` before committing
- **No pipe characters**: Avoid "|" symbols in commit titles
- **No generic messages**: Never use "Update filename.ext" or similar auto-generated messages
- **No casual language**: Strictly avoid "oops", "whoops", "lol", "lulz", "kek", "kekw"
- **Multi-line commits**: Use commit body (not title) for explanations beyond 72 chars
- **Be descriptive**: Focus on WHAT changed and WHY, not just the file modified

#### General File Format Standards (tools/ci/general.sh)
- **File endings**: All files must end with a single newline character
- **Indentation**: Use 4 spaces instead of tab characters (strictly enforced)
- **Line spacing**: No multiple consecutive newline characters
- **Whitespace**: Remove trailing whitespace from all lines

#### C++ Code Standards (tools/ci/cpp.sh)
- **Memory management**: Use `destroy(ptr)` or `destroy_arr(ptr)` instead of naked `delete`
- **Include paths**: Use absolute paths, not relative includes with "../"
- **AI Events**: Document all `.triggerListener()` calls in `documentation/AI_Events.txt`
- **Static analysis**: Code must pass cppcheck with performance, portability, and information checks
- **Formatting**: Must pass clang-format-18 with project .clang-format configuration

#### Lua Code Standards (tools/ci/lua.sh)
- **Syntax validation**: Code must pass luacheck with project-specific globals
- **Style consistency**: Follow project lua style checker requirements
- **Global usage**: Only use documented global functions and objects
- **Complexity**: Maximum cyclomatic complexity of 30

#### Python Code Standards (tools/ci/python.sh)
- **Linting**: Code must pass pylint and black formatting
- **Dependencies**: Use only packages listed in tools/requirements.txt

#### SQL Standards (tools/ci/sql.sh)
- **Syntax validation**: All SQL files must be syntactically correct
- **Price consistency**: Maintain consistency with price checker validation

#### License Header Requirements (tools/ci/detect_license_headers.py)
- **GPLv3 headers**: All C++ source files must include proper GPLv3 license headers
- **Creation date**: Include creation date and purpose in file headers
- **Modification tracking**: Update modification timestamps appropriately

#### Pre-commit Checks
- **ALWAYS verify commit message length**: Use `echo "your commit title" | wc -c` to count characters
- Run clang-format for C++ code formatting
- Execute cppcheck for static analysis
- Validate Lua syntax with luacheck
- Check for proper license headers
- Scan for security vulnerabilities
- Validate commit message formatting
- Check general file format standards

#### Dependency Management
- **Python packages**: Track all packages in tools/requirements.txt
- **C++ libraries**: Document CMake dependencies (MariaDB, LuaJIT, ZeroMQ, OpenSSL)
- **System packages**: Document required system dependencies for builds
- **Security updates**: Regularly check for deprecated packages and vulnerabilities
- **Version pinning**: Use specific versions for critical dependencies
- **Documentation**: Document all external dependencies and their purposes
- **Header-only preference**: Prefer header-only libraries when possible

#### Error Prevention
- Check for truncation issues in string operations
- Validate shell scripts with shellcheck
- Ensure proper file permissions
- Handle edge cases gracefully
- Follow memory safety guidelines for C++
- Validate all user inputs and database queries

### Testing Guidelines

#### Unit Testing
- Write tests for new C++ functionality where applicable
- Test Lua scripts with game scenario validation
- Verify database migrations work correctly
- Test cross-platform compatibility

#### Integration Testing
- Validate server startup and shutdown procedures
- Test client-server communication protocols
- Verify game mechanics work as expected
- Test performance under load

### Performance Considerations

#### Memory Management
- Use appropriate container types for data structures
- Avoid memory leaks in long-running server processes
- Consider cache-friendly data layouts
- Profile memory usage for large datasets

#### Threading and Concurrency
- Be aware of thread safety in server components
- Use appropriate synchronization primitives
- Avoid race conditions in shared data access
- Consider performance impact of locking

### Game-Specific Guidelines

#### FFXI Retail Accuracy
- Strive for accurate recreation of retail FFXI behavior
- Research retail mechanics before implementing features
- Document deviations from retail when necessary
- Consider player experience and game balance

#### Content Implementation
- Follow existing patterns for NPCs, monsters, and items
- Use appropriate item IDs and stats from retail data
- Implement quests and missions with proper progression
- Ensure proper zone and map functionality

### Contribution Guidelines

#### Code Review Process
- All changes require peer review
- Validate changes against retail FFXI when possible
- Test on multiple platforms before merging
- Document breaking changes thoroughly

#### Community Interaction
- Be respectful and helpful to contributors
- Provide constructive feedback on code reviews
- Share knowledge and best practices
- Help newcomers understand the codebase

### Security Considerations

#### Input Validation
- Validate all user inputs from game clients
- Sanitize database inputs to prevent injection
- Implement rate limiting for network operations
- Handle malformed packets gracefully

#### Access Control
- Implement proper GM command authorization
- Validate player permissions for actions
- Secure administrative interfaces
- Log security-relevant events

### Development Planning and Roadmap

#### Strategic Improvements
- Follow the development roadmap in `ROADMAP.md` for prioritized improvements
- Focus on infrastructure modernization and code quality enhancements
- Plan feature development based on community needs and retail accuracy
- Consider performance and scalability in all architectural decisions

#### Continuous Improvement Process
- Regular assessment of codebase health and technical debt
- Automated dependency tracking with vulnerability monitoring
- Performance benchmarking and optimization initiatives
- Community feedback integration into development priorities

#### Function Indexing and Documentation
- Maintain comprehensive API documentation for all components
- Index functions across C++, Lua, and Python codebases
- Document cross-component interactions and dependencies
- Ensure searchable and accessible developer resources

## Getting Help

- Check existing documentation in `documentation/` directory
- Review similar implementations in the codebase
- Ask questions in GitHub discussions
- Consult the Final Fantasy XI community wikis for retail behavior

## Practical Tips for Contributors

### Commit Message Best Practices
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

**Quick commit message templates (all ≤72 chars):**
- `Add [feature] with [brief description]`
- `Fix [issue] in [component]`
- `Update [component] for [reason]` 
- `Refactor [component] to [improvement]`
- `Remove [deprecated feature/code]`

## Tools and Resources

### Development Tools
- Use `tools/dbtool.py` for database operations and migrations
- Run `tools/ci/` scripts for quality checks and validation
- Use `tools/announce.py` for server-wide messaging
- Use `tools/vulnerability_scanner.py` for security auditing
- Use `tools/price_checker.py` for item price validation
- Use `tools/log_manager.py` for log maintenance

### Documentation and References
- Consult `documentation/` for technical references and specifications
- Review `ROADMAP.md` for development priorities and improvement plans
- Use existing changelog generation tools in `tools/generate_changelog.py`
- Check `tools/requirements.txt` for Python dependency management

### Function Index
Refer to `ROADMAP.md` for comprehensive function indexing including:
- **C++ Core Components**: Server architecture, subsystems, and key classes
- **Python Tools**: Development utilities, CI/CD scripts, and automation tools  
- **Lua Framework**: Game mechanics, quest system, and event handlers
- **Database Schema**: Core tables, relationships, and data structures

### Quality Assurance
- All changes must pass CI/CD pipeline checks defined in `tools/ci/`
- Follow the 11-step development workflow documented above
- Ensure compliance with coding standards for each language
- Validate changes against retail FFXI behavior when applicable

Remember: This is a community-driven project focused on preserving and recreating the Final Fantasy XI experience. Quality, accuracy, and maintainability are our top priorities. Consult the roadmap for current development priorities and improvement plans.
