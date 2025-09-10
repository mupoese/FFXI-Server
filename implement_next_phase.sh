#!/bin/bash

# Repository Organization and Cleanup Script
# This script implements the next phase improvements for the FFXI-Server repository

set -euo pipefail

echo "🚀 Starting Next Phase Implementation: Repository Organization"
echo "=========================================================="

# Create organized directory structure
echo "📁 Creating organized directory structure..."

# Create docs directory structure
mkdir -p docs/{api,development,user-guides,architecture,deployment}
mkdir -p .github/{ISSUE_TEMPLATE,PULL_REQUEST_TEMPLATE,workflows}

# Create tools directory structure  
mkdir -p tools/{ci,development,admin,testing}

echo "✅ Directory structure created"

# Organize documentation files
echo "📚 Organizing documentation files..."

# Move documentation to proper locations
if [ -f "WORKFLOW_FIX_CHANGELOG.md" ]; then
    mv WORKFLOW_FIX_CHANGELOG.md docs/development/
    echo "  ✅ Moved workflow fix changelog to docs/development/"
fi

if [ -f "NEXT_PHASE_IMPLEMENTATION.md" ]; then
    mv NEXT_PHASE_IMPLEMENTATION.md docs/development/
    echo "  ✅ Moved next phase implementation plan to docs/development/"
fi

# Create development guides
echo "📖 Creating development guides..."

cat > docs/development/CONTRIBUTING.md << 'EOF'
# Contributing to FFXI-Server

## Development Setup
1. Clone the repository
2. Install dependencies using tools in `/tools/`
3. Run initial setup scripts
4. Follow coding standards outlined below

## Code Quality Standards
- **C++**: Follow project .clang-format configuration
- **Lua**: Use consistent indentation and naming
- **Python**: Follow PEP 8 standards
- **SQL**: Use consistent formatting

## Testing Requirements
- All new features must include tests
- Ensure existing tests continue to pass
- Run full test suite before submitting PRs

## Workflow Guidelines
- Use descriptive commit messages (max 72 characters)
- Create feature branches from latest base
- Submit PRs with comprehensive descriptions
- Ensure CI/CD pipelines pass

## Security Requirements
- Follow security scanning guidelines
- No hardcoded credentials or secrets
- Use secure coding practices
- Report security issues responsibly
EOF

echo "  ✅ Created CONTRIBUTING.md"

# Create architecture documentation
cat > docs/architecture/OVERVIEW.md << 'EOF'
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
EOF

echo "  ✅ Created architecture overview"

# Create deployment guide
cat > docs/deployment/INSTALLATION.md << 'EOF'
# Installation Guide

## System Requirements
- **OS**: Linux (recommended), Windows, or macOS
- **Compiler**: GCC 9+ or Clang 10+ with C++20 support
- **Database**: MariaDB 10.3+
- **Memory**: 4GB+ RAM recommended
- **Storage**: 2GB+ available space

## Quick Start
1. Install system dependencies
2. Clone the repository
3. Run build script: `./tools/ci/enhanced_build_system.sh`
4. Configure database connection
5. Start server components

## Configuration
- Copy example configuration files
- Update database connection settings
- Configure server ports and settings
- Set up SSL certificates (optional)

## Troubleshooting
- Check log files in `logs/` directory
- Verify database connectivity
- Ensure proper file permissions
- Review firewall settings

## Support
- Check documentation in `docs/`
- Review GitHub issues
- Join community discussions
EOF

echo "  ✅ Created installation guide"

echo "🔧 Organizing development tools..."

# Move and organize tools
for tool_script in tools/*.sh; do
    if [[ -f "$tool_script" ]]; then
        case "$(basename "$tool_script")" in
            *ci*|*build*|*test*)
                mkdir -p tools/ci/
                mv "$tool_script" tools/ci/ 2>/dev/null || true
                ;;
            *dev*|*development*)
                mkdir -p tools/development/
                mv "$tool_script" tools/development/ 2>/dev/null || true
                ;;
            *admin*|*management*)
                mkdir -p tools/admin/
                mv "$tool_script" tools/admin/ 2>/dev/null || true
                ;;
        esac
    fi
done

echo "  ✅ Organized development tools"

# Create main README update
echo "📝 Updating main README..."

cat > README_ENHANCED.md << 'EOF'
# 🚢 FFXI-Server (LandSandBoat Fork)

A modern, comprehensive server emulator for Final Fantasy XI with enhanced features and improved development workflow.

## ✨ Key Features
- **Full C++20 Implementation**: Modern, maintainable codebase
- **Comprehensive Lua Scripting**: Extensive game logic customization
- **Advanced CI/CD Pipeline**: Automated testing and deployment
- **Enhanced Security**: Integrated security scanning and monitoring
- **Developer-Friendly**: Extensive documentation and development tools

## 🚀 Quick Start
```bash
# Clone the repository
git clone https://github.com/mupoese/FFXI-Server.git
cd FFXI-Server

# Run automated setup
./tools/setup.sh

# Build the project
mkdir build && cd build
cmake ..
make -j$(nproc)
```

## 📚 Documentation
- **[Installation Guide](docs/deployment/INSTALLATION.md)**: Complete setup instructions
- **[Contributing Guide](docs/development/CONTRIBUTING.md)**: Development guidelines
- **[Architecture Overview](docs/architecture/OVERVIEW.md)**: System architecture
- **[API Documentation](docs/api/)**: API references

## 🛠️ Development
- **Requirements**: C++20, CMake 3.20+, MariaDB 10.3+, Python 3.12+
- **Build System**: CMake with cross-platform support
- **Testing**: Automated test suite with CI/CD integration
- **Code Quality**: Automated linting, formatting, and security scanning

## 🔧 Repository Structure
```
├── src/              # C++ source code
├── scripts/          # Lua game scripts  
├── sql/              # Database schema and data
├── tools/            # Development and admin tools
├── docs/             # Comprehensive documentation
├── .github/          # GitHub workflows and templates
└── tests/            # Test suites
```

## 🤝 Contributing
We welcome contributions! Please read our [Contributing Guide](docs/development/CONTRIBUTING.md) for details on:
- Development setup and workflow
- Code quality standards
- Testing requirements
- Security guidelines

## 📊 Project Status
- ✅ **C++ Compilation**: Fixed and validated
- ✅ **Repository Organization**: Enhanced structure
- 🚧 **CI/CD Pipeline**: Continuously improving
- 🚧 **Documentation**: Expanding coverage

## 🔒 Security
- Regular security scanning with CodeQL
- Automated vulnerability detection
- Security-focused development practices
- Responsible disclosure policy

## 📄 License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- Based on the excellent [LandSandBoat](https://github.com/LandSandBoat/server) project
- Thanks to the FFXI private server community
- Inspired by the original Final Fantasy XI
EOF

echo "  ✅ Enhanced README created"

echo ""
echo "🎉 Next Phase Implementation Complete!"
echo "======================================"
echo ""
echo "✅ Repository structure organized"
echo "✅ Documentation enhanced and centralized"  
echo "✅ Development tools reorganized"
echo "✅ Quality guidelines established"
echo "✅ Enhanced README created"
echo ""
echo "🔄 Recommended next steps:"
echo "   1. Review the organized structure"
echo "   2. Update any remaining documentation"
echo "   3. Test the enhanced development workflow"
echo "   4. Continue with workflow optimizations"
echo ""
echo "📁 New structure ready for enhanced development!"