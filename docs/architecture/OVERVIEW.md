# FFXI-Server Architecture Overview

## Core Components
- **Map Server**: Handles player interactions and world state
- **Login Server**: Manages authentication and character selection  
- **Search Server**: Provides search functionality
- **Database**: MariaDB-based data storage

## Technology Stack
- **C++20**: Core server implementation
- **Lua 5.1**: Scripting engine for game logic
- **Python 3.12+**: Development tools and automation
- **MariaDB**: Database backend
- **CMake**: Build system

## Directory Structure
```
src/           # C++ source code
scripts/       # Lua game scripts
sql/           # Database schema and data
tools/         # Development and admin tools
docs/          # Documentation
.github/       # GitHub workflows and templates
```

## Build System
The project uses CMake with cross-platform support for Linux, Windows, and macOS.

## Coding Standards
- Follow project .clang-format for C++ code
- Use consistent naming conventions
- Include comprehensive documentation
- Write maintainable, secure code
