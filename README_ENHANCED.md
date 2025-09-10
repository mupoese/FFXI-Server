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
