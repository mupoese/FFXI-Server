<p align="center">
    <img width="256" height="256" src="res/lsb_logo_circle.png">
    <h1 align="center">LandSandBoat</h1>
</p>

<p align="center">
<a href="https://github.com/LandSandBoat/server/actions/workflows/build.yml?query=base"><img src="https://github.com/LandSandBoat/server/actions/workflows/build.yml/badge.svg"/></a>
<a href="https://www.gnu.org/licenses/gpl-3.0"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg"/></a>
<a href="https://github.com/LandSandBoat/server/pulls"><img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat"/></a>
</p>

Welcome to LandSandBoat, an open source server emulator for FFXI.

## Getting Started

A [quick start guide](https://github.com/LandSandBoat/server/wiki/Quick-Start-Guide), the [frequently asked questions](https://github.com/LandSandBoat/server/wiki/Frequently-Asked-Questions), and a table of "[what works](https://github.com/LandSandBoat/server/wiki/What-Works)" are all available on [our wiki](https://github.com/LandSandBoat/server/wiki).

### Docker Quick Start

The fastest way to get a FFXI server running is with Docker:

```bash
# Clone the repository
git clone https://github.com/mupoese/FFXI-Server.git
cd FFXI-Server

# Copy and configure environment
cp .env.example .env
# Edit .env with your database passwords and settings

# Start the server with web interface
docker-compose up -d

# Start with full monitoring stack
COMPOSE_PROFILES=monitoring docker-compose up -d

# View logs
docker-compose logs -f ffxi-server
```

**🌐 Web Interface Access:**
- **Homepage**: `http://localhost:8000` - Beautiful landing page with real-time server status
- **Admin Dashboard**: `http://localhost:8000/admin.html` - Comprehensive 8-tab administration interface
- **Grafana Monitoring**: `http://localhost:3000` - Advanced metrics dashboards (with monitoring profile)
- **Prometheus Metrics**: `http://localhost:9090` - Raw metrics collection (with monitoring profile)

**🎮 Game Server Endpoints:**
- Login: `localhost:54001`
- Game Data: `localhost:54230` 
- Search: `localhost:54002`
- Database Admin: `http://localhost:8080` (optional, add `--profile admin`)

### Docker with Full Monitoring Stack

For complete server monitoring with Prometheus + Grafana:

```bash
# Start with comprehensive monitoring
COMPOSE_PROFILES=monitoring docker-compose up -d

# Or combine with other profiles for full functionality
COMPOSE_PROFILES=redis,admin,monitoring docker-compose up -d
```

**📊 Monitoring Stack Includes:**
- **Prometheus**: Advanced metrics collection with FFXI-specific recording rules
- **Grafana**: Pre-configured dashboards with multiple visualization panels
- **Node Exporter**: System-level performance metrics (CPU, memory, disk, network)
- **MySQL Exporter**: Database performance monitoring and query analysis
- **AlertManager**: Intelligent alert routing with webhook notifications

### Docker with Cloudflare Tunnel

For external access through Cloudflare tunnel:

1. Create a tunnel in [Cloudflare Zero Trust](https://one.dash.cloudflare.com/)
2. Get your tunnel token
3. Configure your `.env` file:
   ```env
   CLOUDFLARE_TUNNEL_TOKEN=your_tunnel_token_here
   CLOUDFLARE_DOMAIN=yourdomain.com
   ```
4. Start with Cloudflare profile:
   ```bash
   docker-compose --profile cloudflare up -d
   ```

**Cloudflare tunnel endpoints:**
- `https://admin.yourdomain.com` - Web admin interface
- `https://login.yourdomain.com` - Login service  
- `https://auth.yourdomain.com` - Authentication
- `https://search.yourdomain.com` - Search service

> **Note:** FFXI uses UDP for game traffic which Cloudflare tunnels don't support directly. For full game access, you may need Cloudflare Spectrum (Enterprise) or direct port access.

## 🌐 Web Administration Interface

LandSandBoat now includes a comprehensive web-based administration system with real-time monitoring capabilities:

### **Homepage (`index.html`)**
- Beautiful, responsive landing page with modern dark theme
- **Real-time server status footer** displaying:
  - Online player count with 24-hour trends
  - Server uptime and response times
  - Load balancer status with instance health
  - Database connection monitoring
- Mobile and tablet optimized with touch-friendly design
- Direct links to admin dashboard and monitoring interfaces

### **Admin Dashboard (`admin.html`)**
Comprehensive 8-tab administration interface featuring:

- **🔧 Dashboard Tab**: System metrics, player statistics, and critical alerts
- **📊 Monitoring Tab**: Embedded Grafana dashboards and Prometheus metrics
- **⚖️ Servers Tab**: Multi-instance management with HAProxy load balancer statistics
- **👥 Players Tab**: Online player management with search and admin actions
- **🗄️ Database Tab**: Performance monitoring with connection pooling stats
- **🌐 Network Tab**: Port status testing and connectivity monitoring
- **📋 Logs Tab**: Real-time log viewing with filtering capabilities
- **⚙️ Settings Tab**: Server configuration management and system controls

### **Integrated Monitoring Stack**
- **Prometheus**: FFXI-specific metrics collection with custom recording and alert rules
- **Grafana**: Pre-configured dashboards with multiple visualization panels
- **Node Exporter**: System performance metrics (CPU, memory, disk, network)
- **MySQL Exporter**: Database performance monitoring with query analysis
- **AlertManager**: Intelligent alert routing with webhook notifications

### **Multi-Server Load Balancing**
- **HAProxy Integration**: Real-time load balancer statistics in admin dashboard
- **Multi-Instance Support**: Health monitoring across multiple FFXI server instances
- **Automatic Failover**: Visual indication of server health and traffic distribution
- **Performance Monitoring**: Live backend response times and load distribution

## Documentation

- **[Function Index](documentation/function_index/index.html)** - Comprehensive API documentation for C++, Lua, Python, and SQL
- **[Web Admin Guide](ENHANCED_WEB_ADMIN_GUIDE.md)** - Complete web interface documentation and usage guide
- **[Docker Infrastructure](DOCKER_INFRASTRUCTURE_SUMMARY.md)** - Docker deployment with monitoring stack setup
- **[Development Guide](documentation/FUNCTION_INDEXING_SYSTEM.md)** - Function Indexing System implementation details
- **[Modernization Summary](MODERNIZATION_SUMMARY.md)** - Recent codebase improvements and modern C++ features
- **[Network Bonding Guide](NETWORK_BONDING.md)** - Network bonding/link aggregation implementation and configuration
- **[Database Improvements](DATABASE_WORKFLOW_IMPROVEMENTS.md)** - Database connection pooling and performance enhancements
- **[Tools Documentation](tools/README.md)** - Development tools and utilities reference

### Developer Tools

The project now includes modern development automation:

```bash
# Complete development workflow
python3 tools/dev_automation.py all

# Individual operations
python3 tools/dev_automation.py setup    # Environment setup with git hooks
python3 tools/dev_automation.py format   # Code formatting (Python + C++)
python3 tools/dev_automation.py lint     # Static analysis and security scanning
python3 tools/dev_automation.py build    # Optimized parallel build
python3 tools/dev_automation.py test     # Comprehensive test suite

# Performance profiling
python3 tools/advanced_profiler.py report --output performance.json

# Enhanced CI/CD pipeline
tools/enhanced_ci_pipeline.sh all

# Docker testing and validation
python3 tools/docker_test_suite.py --verbose --report docker_report.json
tools/docker_validation.sh all
```

## Docker Installation Guide

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) 20.10 or later
- [Docker Compose](https://docs.docker.com/compose/install/) 2.0 or later
- At least 4GB RAM and 10GB disk space

### Installation Steps

1. **Clone and Setup**
   ```bash
   git clone https://github.com/mupoese/FFXI-Server.git
   cd FFXI-Server
   
   # Copy environment configuration
   cp .env.example .env
   ```

2. **Configure Environment**
   Edit `.env` file with your settings:
   ```env
   # Database passwords (change these!)
   MYSQL_ROOT_PASSWORD=your_secure_root_password
   MYSQL_PASSWORD=your_secure_user_password
   
   # Optional: Cloudflare tunnel
   CLOUDFLARE_TUNNEL_TOKEN=your_tunnel_token
   CLOUDFLARE_DOMAIN=yourdomain.com
   ```

3. **Start Basic Server**
   ```bash
   # Start database and FFXI server
   docker-compose up -d
   
   # Check status
   docker-compose ps
   
   # View server logs
   docker-compose logs -f ffxi-server
   ```

4. **Start with Full Monitoring Stack**
   ```bash
   # Include monitoring (Prometheus + Grafana + Node Exporter)
   COMPOSE_PROFILES=monitoring docker-compose up -d
   
   # Or combine with admin tools and caching
   COMPOSE_PROFILES=admin,redis,monitoring docker-compose up -d
   ```

5. **Start with Cloudflare Tunnel**
   ```bash
   # For external access via Cloudflare
   COMPOSE_PROFILES=cloudflare up -d
   ```

**🌐 Access the Web Interface:**
- **Homepage**: `http://localhost:8000` - Server status and information
- **Admin Dashboard**: `http://localhost:8000/admin.html` - Complete administration interface
- **Grafana**: `http://localhost:3000` - Monitoring dashboards (monitoring profile)
- **Prometheus**: `http://localhost:9090` - Metrics collection (monitoring profile)

### Network Ports

The FFXI server uses these ports:

| Port  | Protocol | Service | Description |
|-------|----------|---------|-------------|
| 54001 | TCP      | Login View | Client login interface |
| 54002 | TCP      | Search | Player/linkshell search |
| 54230 | TCP/UDP  | Login Data/Map | Main game data |
| 54231 | TCP      | Login Auth | Authentication |
| 51220 | TCP      | Login Config | Configuration |
| 54003 | TCP      | ZMQ | Inter-service messaging |
| 8000  | HTTP     | Web Interface | Homepage and admin dashboard |
| 3000  | HTTP     | Grafana | Monitoring dashboards (monitoring profile) |
| 9090  | HTTP     | Prometheus | Metrics collection (monitoring profile) |
| 9093  | HTTP     | AlertManager | Alert management (monitoring profile) |
| 9100  | HTTP     | Node Exporter | System metrics (monitoring profile) |
| 9104  | HTTP     | MySQL Exporter | Database metrics (monitoring profile) |
| 3306  | TCP      | Database | MariaDB |
| 8080  | HTTP     | PhpMyAdmin | Database admin (admin profile) |

### Docker Management

**Common Commands:**
```bash
# View running containers
docker-compose ps

# Restart server
docker-compose restart ffxi-server

# View logs
docker-compose logs -f [service-name]

# Start with monitoring stack
COMPOSE_PROFILES=monitoring docker-compose up -d

# Start with all services (admin + monitoring + caching)
COMPOSE_PROFILES=admin,redis,monitoring docker-compose up -d

# Update and rebuild
git pull
docker-compose build --no-cache
docker-compose up -d

# Access web interfaces
open http://localhost:8000              # Homepage with server status
open http://localhost:8000/admin.html   # Admin dashboard
open http://localhost:3000              # Grafana (monitoring profile)
open http://localhost:9090              # Prometheus (monitoring profile)

# Backup database
docker-compose exec db mysqldump -u root -p xidb > backup.sql

# Restore database
docker-compose exec -T db mysql -u root -p xidb < backup.sql

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v
```

**Troubleshooting:**
```bash
# Check web interface health
curl -f http://localhost:8000
curl -f http://localhost:8000/admin.html

# Check container health
docker-compose exec ffxi-server curl -f http://localhost:8000/health

# Access container shell
docker-compose exec ffxi-server /bin/bash

# Check database connection
docker-compose exec ffxi-server mysqladmin ping -h db -u xiuser -p

# View detailed logs
docker-compose logs --timestamps --tail=100 ffxi-server

# Check monitoring stack (if enabled)
curl -f http://localhost:9090/-/healthy  # Prometheus
curl -f http://localhost:3000/api/health # Grafana

# Monitor system resources
docker stats
```

### Cloudflare Tunnel Setup

For external access without port forwarding:

1. **Create Cloudflare Tunnel:**
   - Go to [Cloudflare Zero Trust](https://one.dash.cloudflare.com/)
   - Navigate to Access → Tunnels
   - Create a new tunnel, note the token

2. **Configure DNS:**
   Add these CNAME records to your domain:
   ```
   admin    → your-tunnel-id.cfargotunnel.com
   login    → your-tunnel-id.cfargotunnel.com  
   auth     → your-tunnel-id.cfargotunnel.com
   search   → your-tunnel-id.cfargotunnel.com
   ```

3. **Update Environment:**
   ```env
   CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoiY...
   CLOUDFLARE_DOMAIN=yourdomain.com
   ```

4. **Start with Tunnel:**
   ```bash
   docker-compose --profile cloudflare up -d
   ```

**Limitations:** Cloudflare tunnels only support HTTP/HTTPS and TCP. FFXI's UDP traffic requires either:
- Cloudflare Spectrum (Enterprise plan)
- Direct port forwarding for UDP ports
- VPN solution for game clients

## Interacting with LandSandBoat

### Crashes, warnings, errors, bugs, gameplay issues, visual issues, etc.

Please create a new issue in the [issues tab](https://github.com/LandSandBoat/server/issues) after searching to see if your issue is already logged.

### Balance discussion, technical discussion, meta discussions, etc.

Discussions are similar to forum posts. Please open a new discussion post in the [discussions tab](https://github.com/LandSandBoat/server/discussions) for less directed and more open-ended conversation than issues.

*If you are encountering an issue, please open an issue and not a discussion!* It's much easier for us to track and you're more likely to get resolution through an issue.

## LICENSE

LandSandBoat is licensed under [GNU GPL v3](https://github.com/LandSandBoat/server/blob/base/LICENSE)

## Thanks

Thanks to all contributors past and present, we wouldn't be here without you!

Thanks to GitHub for hosting us, and for all the CI minutes we use!
