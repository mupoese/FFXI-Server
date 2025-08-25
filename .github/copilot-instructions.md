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

### Development Workflow Enhancement (SWE Agent Logic)

When working on this repository, follow this enhanced 11-step process for optimal code quality:

1. **Intentie = Doel** (Intent = Goal)
   - Clearly define what you want to achieve
   - Understand the game mechanics or system being implemented
   - Consider impact on existing functionality

2. **Actie = Plan** (Action = Plan)
   - Create a concrete plan to reach the goal
   - Identify affected files and systems
   - Consider database schema changes if needed

3. **Reactie = Uitvoering** (Reaction = Execution)
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

7. **Correctie** (Correction)
   - Improve the chosen plan to the most optimal version
   - Ensure no conflicts with existing code
   - Optimize for performance and memory usage

8. **Validatie** (Validation)
   - Verify and confirm that the improved plan works correctly
   - Test all affected game systems
   - Ensure compliance with coding standards

9. **Leren** (Learning)
   - Document what was learned and how the code/functionality was improved
   - Update relevant documentation
   - Share knowledge with the development community

10. **Herhalen** (Repeat)
    - If failed or insufficient knowledge gained, repeat from **Intentie**
    - Iterate until the solution meets quality standards
    - Don't hesitate to refactor if a better approach is discovered

11. **Uitkomst** (Outcome)
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

#### Pre-commit Checks
- Run clang-format for C++ code formatting
- Execute cppcheck for static analysis
- Validate Lua syntax with luacheck
- Check for proper license headers
- Scan for security vulnerabilities

#### Dependency Management
- Regularly check for deprecated packages and dependencies
- Update to secure versions when vulnerabilities are found
- Document all external dependencies and their purposes
- Prefer header-only libraries when possible

#### Error Prevention
- Check for truncation issues in string operations
- Validate shell scripts with shellcheck
- Ensure proper file permissions
- Handle edge cases gracefully

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

## Getting Help

- Check existing documentation in `documentation/` directory
- Review similar implementations in the codebase
- Ask questions in GitHub discussions
- Consult the Final Fantasy XI community wikis for retail behavior

## Tools and Resources

- Use `tools/dbtool.py` for database operations
- Run `tools/ci/` scripts for quality checks
- Consult `documentation/` for technical references
- Use existing changelog generation tools

Remember: This is a community-driven project focused on preserving and recreating the Final Fantasy XI experience. Quality, accuracy, and maintainability are our top priorities.