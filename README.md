# FFXI LandSandBoat Server

<p align="center">
    <img width="256" height="256" src="res/lsb_logo_circle.png">
</p>

**🎉 ITERATION 13 COMPLETE: Advanced AI & Automation** ✅ **174,591 lines implemented**  
**Repository Status**: September 2024 - Clean, tidy, and fully organized

Welcome to the LandSandBoat FFXI Server project - a comprehensive open-source server emulator for Final Fantasy XI with advanced AI automation.

## 📚 Documentation

**[📖 Complete Documentation](DOCUMENTATION.md)** - Single comprehensive guide covering all aspects of the project

## 🚀 Quick Start

```bash
# Clone and start with Docker (recommended)
git clone https://github.com/mupoese/FFXI-Server.git
cd FFXI-Server
cp .env.example .env
docker-compose up -d

# Access web interface
open http://localhost:8000
```

## 🤖 AI Systems (ITERATION 13)

**174,591 lines** of enterprise-grade AI automation implemented:

- **Autonomous System Manager** - Self-healing infrastructure
- **AI Game Master** - Dynamic content generation  
- **Predictive Analytics** - ML-based optimization
- **Intelligent Content Generator** - AI quest creation

## 🏆 Features

- **Complete Job System** - All 22 jobs implemented with graduated subjob system
- **Advanced AI Automation** - Autonomous server management and content generation
- **Modern Web Interface** - Comprehensive admin dashboard with real-time monitoring
- **Docker Support** - Easy deployment with monitoring stack
- **Enhanced Security** - Automated scanning and threat detection
## 🛠️ Development

For development setup, contribution guidelines, and technical details, see the [Complete Documentation](DOCUMENTATION.md).

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Based on the excellent [LandSandBoat](https://github.com/LandSandBoat/server) project
- Thanks to the FFXI private server community
- Special recognition to all contributors and maintainers

## 🐳 Docker Infrastructure

All Docker-related files are organized in the [`docker/`](docker/) directory:

- **[docker-compose.yml](docker/docker-compose.yml)** - Main orchestration file
- **[Dockerfile](docker/Dockerfile)** - Production container build
- **monitoring/** - Prometheus, Grafana, and AlertManager configurations
- **configs/** - Service configuration files
- **scripts/** - Container startup and utility scripts

## 🌐 Web Interface

The modern web administration interface is located in the [`web/`](web/) directory:

- **[Homepage](web/index.html)** - Landing page with real-time server status
- **[Admin Dashboard](web/admin.html)** - Comprehensive administration interface
- **api/** - RESTful API for server management
- **assets/** - CSS, JavaScript, and other web assets

## 📁 Repository Structure

```
.
├── docs/                       # All documentation
├── docker/                     # Docker infrastructure
├── web/                        # Web interface
├── src/                        # C++ source code
├── scripts/                    # Lua game scripts
├── sql/                        # Database schema
├── tools/                      # Development tools
└── [other game assets...]
```

## 🎮 Features

- **Full FFXI Server Emulation** - Complete game world recreation
- **Web Administration** - Modern responsive admin interface
- **Real-time Monitoring** - Prometheus + Grafana integration
- **Multi-instance Support** - Load balancing with HAProxy
- **Docker Deployment** - Production-ready containerization
- **Comprehensive Testing** - Automated quality assurance

## 🔗 Quick Links

- [Complete Setup Guide](docs/README.md)
- [Documentation Index](docs/DOCUMENTATION_INDEX.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)
- [Code of Conduct](docs/CODE_OF_CONDUCT.md)
- [Web Admin Guide](docs/guides/web-admin/ENHANCED_WEB_ADMIN_GUIDE.md)
- [Docker Infrastructure](docs/guides/docker/DOCKER_INFRASTRUCTURE_SUMMARY.md)

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.