# FFXI LandSandBoat Server

<p align="center">
    <img width="256" height="256" src="res/lsb_logo_circle.png">
</p>

Welcome to the LandSandBoat FFXI Server project - a comprehensive open-source server emulator for Final Fantasy XI.

## 🚀 Quick Start

```bash
# Clone and start the server
git clone https://github.com/mupoese/FFXI-Server.git
cd FFXI-Server
docker-compose up -d

# Access the web interface
open http://localhost:8000
```

## 📚 Documentation

All comprehensive documentation has been organized in the [`docs/`](docs/) directory:

- **[Main Documentation](docs/README.md)** - Complete setup and usage guide
- **[Contributing Guide](docs/CONTRIBUTING.md)** - Development guidelines and standards
- **[Roadmap](docs/ROADMAP.md)** - Project development roadmap and progress

### Documentation Structure

```
docs/
├── README.md                    # Main documentation
├── CONTRIBUTING.md              # Contributing guidelines  
├── ROADMAP.md                  # Development roadmap
├── guides/                     # Detailed guides
│   ├── admin-tools/           # Administration guides
│   ├── docker/                # Docker setup and usage
│   ├── networking/            # Network configuration
│   ├── testing/               # Testing documentation
│   └── web-admin/             # Web interface guides
├── summaries/                  # Implementation summaries
└── analysis/                   # Technical analysis documents
```

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
- [Web Admin Guide](docs/guides/web-admin/ENHANCED_WEB_ADMIN_GUIDE.md)
- [Docker Infrastructure](docs/guides/docker/DOCKER_INFRASTRUCTURE_SUMMARY.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.