# FFXI LandSandBoat Server

<p align="center">
    <img width="256" height="256" src="res/lsb_logo_circle.png">
</p>

**🔴 CURRENT STATUS: PRIORITY 1 - Job Completeness Initiative** ✅ **10/22 Complete**  
**Repository Reorganized**: September 2024 - All documentation and tools organized

Welcome to the LandSandBoat FFXI Server project - a comprehensive open-source server emulator for Final Fantasy XI.

## 🔴 PRIORITY 1: Job Completeness Initiative ✅ **83.0% Complete**

**CURRENT STATUS**: 10/22 jobs at 100% completion with graduated subjob penalty system

- **Current Completeness**: 83.0% average (10/22 jobs at 100%)
- **Implementation Status**: [Job Completeness Current Status](docs/reports/JOB_COMPLETENESS_CURRENT_STATUS.md)
- **Analysis Results**: [Job Completeness Analysis](docs/reports/JOB_COMPLETENESS_ANALYSIS.md)
- **Roadmap**: [ROADMAP.md](ROADMAP.md) - Updated with current progress

### ✅ Completed Jobs (100% Implementation)
**Scholar, Paladin, Dark Knight, Summoner, Blue Mage, Red Mage, Black Mage, White Mage, Ninja, Geomancer**

**New Feature**: Graduated subjob penalty system - linear scaling from 50% to 100% effectiveness (levels 50-75)

### 🎯 Next Priority Jobs
Rune Fencer (52.5%), Bard (55.0%), Corsair (59.5%), Dancer (67.5%), Samurai (69.0%)

## 🚀 Quick Start

```bash
# Clone and start the server
git clone https://github.com/mupoese/FFXI-Server.git
cd FFXI-Server
docker-compose up -d

# Access the web interface
open http://localhost:8000
```

## 📚 Documentation ✅ **REORGANIZED**

All comprehensive documentation has been organized in the [`docs/`](docs/) directory:

- **[Documentation Index](docs/DOCUMENTATION_INDEX.md)** - ✅ **UPDATED** - Complete documentation guide
- **[Repository Organization Status](docs/REPOSITORY_ORGANIZATION_STATUS.md)** - ✅ **NEW** - Organization completion
- **[Contributing Guide](docs/CONTRIBUTING.md)** - Development guidelines and standards
- **[Roadmap](ROADMAP.md)** - ✅ **UPDATED** - Current progress and priorities

### Priority 1 Documentation
- **[Job Completeness Current Status](docs/reports/JOB_COMPLETENESS_CURRENT_STATUS.md)** - ✅ **NEW** - Complete status
- **[Job Completeness Plan](docs/reports/JOB_COMPLETENESS_PLAN.md)** - ✅ **UPDATED** - Implementation strategy  
- **[Job Analysis Report](docs/reports/JOB_COMPLETENESS_ANALYSIS.md)** - Analysis results

### Repository Organization ✅ **COMPLETED**

```
📁 Repository Structure (September 2024)
├── 🔴 JOB_COMPLETENESS_PLAN.md     # Priority 1 implementation plan
├── 🔴 ROADMAP.md                   # Updated with Priority 1 focus
├── docs/                           # All documentation
│   ├── 📚 DOCUMENTATION_INDEX.md   # Complete documentation guide
│   ├── reports/                   # Analysis and validation reports
│   ├── guides/                    # Setup and usage guides
│   └── systems/                   # Game system documentation
├── tools/                         # 🗂️ COMPLETELY REORGANIZED
│   ├── admin/                     # Administration tools
│   ├── analysis/                  # Job analysis and validation
│   ├── database/                  # Database management
│   ├── development/               # Code generation and docs
│   ├── launchers/                 # Game launcher tools
│   ├── monitoring/                # Performance monitoring
│   ├── streaming/                 # Asset management
│   ├── testing/                   # Testing frameworks
│   └── ai-gm/                     # AI-GM system tools
├── src/                           # C++ source code
├── scripts/                       # Lua game scripts
├── sql/                           # Database schema
├── docker/                        # Docker infrastructure
└── web/                           # Web administration interface
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