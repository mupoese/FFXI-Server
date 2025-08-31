# LandSandBoat Enhanced Web Administration Interface

## Overview

The enhanced web administration interface provides a comprehensive web-based management system for the LandSandBoat FFXI server with real-time monitoring, beautiful responsive design, and integrated Prometheus+Grafana monitoring stack.

## 🌐 Complete Web Interface

### **Homepage (`index.html`)**
- **Beautiful responsive landing page** with modern dark theme design
- **Real-time server status footer** with live updates every 30 seconds:
  - Server status, online player count, and 24-hour trends
  - Server uptime and response times
  - Load balancer status with multi-instance support
  - Database connection health monitoring
  - Direct links to monitoring dashboards
- **Mobile and tablet optimized** with touch-friendly controls
- **Feature showcase** highlighting server capabilities

### **Admin Dashboard (`admin.html`)**
Comprehensive 8-tab administration interface featuring:

#### **🔧 Dashboard Tab**
- System metrics overview (CPU, memory, disk usage)
- Player statistics with trend charts
- Critical alerts and system notifications
- Quick action buttons for common tasks

#### **📊 Monitoring Tab**
- **Embedded Grafana dashboards** with multiple visualization panels
- **Prometheus metrics integration** with custom FFXI recording rules
- Real-time system performance charts
- Database performance monitoring with query analysis

#### **⚖️ Servers Tab**
- **Multi-instance management** with health monitoring
- **HAProxy load balancer statistics** and configuration
- Real-time backend server status and load distribution
- Server instance scaling and management controls

#### **👥 Players Tab**
- Online player management with search capabilities
- Player statistics and character information
- Administrative actions (kick, ban, promote)
- Real-time player activity monitoring

#### **🗄️ Database Tab**
- Database performance monitoring with connection pooling stats
- Query performance analysis and optimization tools
- Real-time connection counts and health metrics
- Database maintenance and backup controls

#### **🌐 Network Tab**
- Port status testing and connectivity monitoring
- Network performance metrics and diagnostics
- Firewall status and configuration
- Connection tracking and analysis

#### **📋 Logs Tab**
- Real-time log viewing with filtering capabilities
- Log level filtering and search functionality
- Export and download options
- Multi-service log aggregation

#### **⚙️ Settings Tab**
- Server configuration management
- System settings and preferences
- User management and permissions
- Monitoring configuration controls

## 📊 Integrated Monitoring Stack

### **Prometheus Integration**
- **FFXI-specific metrics collection** with custom recording rules
- **Advanced alert rules** for server health and performance monitoring
- **Custom metrics endpoints** for game-specific data
- **Performance tracking** with historical data storage

### **Grafana Dashboards**
- **Pre-configured dashboards** with multiple visualization panels:
  - Server performance metrics (CPU, memory, network, disk)
  - Player activity and game statistics
  - Database performance and query analysis
  - Multi-instance load balancer monitoring
- **Real-time updates** with customizable refresh intervals
- **Alert integration** with visual notifications

### **System Monitoring**
- **Node Exporter**: System-level performance metrics
- **MySQL Exporter**: Database performance monitoring
- **AlertManager**: Intelligent alert routing with webhook notifications
- **Custom exporters**: FFXI server-specific metrics collection

## ⚖️ Load Balancer & Multi-Server Support

### **HAProxy Integration**
- **Load balancer statistics** displayed in admin dashboard
- **Real-time backend monitoring** with health checks
- **Traffic distribution visualization** and management
- **Automatic failover detection** and notification

### **Multi-Instance Management**
- **Health monitoring** across multiple FFXI server instances
- **Performance tracking** with individual instance metrics
- **Scaling controls** for dynamic instance management
- **Load distribution analytics** and optimization

## 🔧 Enhanced API Layer

### **REST API Endpoints**
- **Comprehensive server metrics** from Prometheus integration
- **Player management** with search and administrative actions
- **System monitoring** with real-time performance data
- **Configuration management** for server settings

### **Real-time Data**
- **Live updates every 30 seconds** for server status and metrics
- **WebSocket integration** for instant notifications
- **Event streaming** for real-time log monitoring
- **Push notifications** for critical alerts

### **Security Features**
- **Token-based authentication** for admin API access
- **Role-based permissions** for different access levels
- **Input validation** and sanitization
- **CSRF protection** for form submissions

## Technical Implementation

### Database Integration
- **Secure authentication** using existing `accounts` table
- **Character data access** from `chars` and related tables
- **Inventory integration** with `char_inventory` table
- **Auction house data** from `auction_house` table
- **GM level management** through character `gmlevel` field

### Security Features
- **Password hashing** using SHA-256 for secure authentication
- **Session management** with Flask sessions
- **Role-based access control** for different admin functions
- **Input validation** and SQL injection prevention
- **CSRF protection** for form submissions

### Real-time Features
- **Auto-refreshing dashboards** - data updates every 10-30 seconds
- **Live system monitoring** - CPU, memory, disk usage
- **Real-time game data** - Vana'diel time calculation
- **Dynamic user interfaces** - responsive tab system

## Configuration

### Database Configuration
```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "database": "xidb",
    "user": "your_username",
    "password": "your_password"
  }
}
```

### User Management Settings
```json
{
  "user_management": {
    "max_characters_per_user": 2,
    "require_approval": true,
    "admin_email": "admin@landsandboat.local"
  }
}
```

## Installation & Usage

### Quick Start with Docker

```bash
# Start basic server with web interface
docker-compose up -d

# Start with full monitoring stack
COMPOSE_PROFILES=monitoring docker-compose up -d

# Start with all services (admin + monitoring + caching)
COMPOSE_PROFILES=admin,redis,monitoring docker-compose up -d
```

### Access URLs

#### **Main Interfaces**
- **Homepage**: `http://localhost:8000` - Beautiful landing page with server status
- **Admin Dashboard**: `http://localhost:8000/admin.html` - Complete administration interface

#### **Monitoring Stack** (with monitoring profile)
- **Grafana Dashboards**: `http://localhost:3000` - Advanced visualization
- **Prometheus Metrics**: `http://localhost:9090` - Raw metrics collection
- **AlertManager**: `http://localhost:9093` - Alert management

#### **Additional Services** (with admin profile)
- **Database Admin**: `http://localhost:8080` - PhpMyAdmin interface

### Configuration

#### **Environment Variables**
```env
# Database Configuration
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_PASSWORD=your_secure_user_password
MYSQL_DATABASE=xidb
MYSQL_USER=xiuser

# Monitoring Configuration
GRAFANA_ADMIN_PASSWORD=admin
PROMETHEUS_RETENTION=15d

# Cloudflare Tunnel (optional)
CLOUDFLARE_TUNNEL_TOKEN=your_tunnel_token
CLOUDFLARE_DOMAIN=yourdomain.com
```

#### **Docker Profiles**
- **Default**: Basic FFXI server + database + web interface
- **monitoring**: Adds Prometheus + Grafana + Node Exporter + AlertManager
- **admin**: Adds PhpMyAdmin for database management
- **redis**: Adds Redis caching for improved performance
- **cloudflare**: Adds Cloudflare tunnel for external access
- **multi-instance**: Load balancer with multiple server instances

## Features in Detail

### **Real-time Server Status Footer**
The homepage footer displays live server information updated every 30 seconds:
- **Server Status**: Online/offline indicator with uptime
- **Players Online**: Current count with 24-hour trend indicator
- **Load Balancer**: Instance count and health status
- **Database**: Connection count and response time
- **Response Time**: Server latency and performance metrics

### **Comprehensive Admin Dashboard**
The admin dashboard provides full server management through multiple specialized tabs:

#### **Dashboard Overview**
- System resource usage (CPU, memory, disk)
- Player statistics and activity trends
- Critical alerts and notifications
- Quick access to common administrative tasks

#### **Advanced Monitoring**
- Embedded Grafana dashboards with real-time charts
- Prometheus metrics with custom FFXI recording rules
- System performance trends and historical data
- Database query performance and optimization metrics

#### **Multi-Server Management**
- Load balancer statistics and health monitoring
- Individual server instance performance tracking
- Traffic distribution and failover status
- Scaling controls and instance management

### **Mobile and Tablet Support**
- **Responsive design** adapts to all screen sizes
- **Touch-friendly controls** optimized for mobile interaction
- **Adaptive layouts** provide optimal viewing on any device
- **Modern CSS** with smooth animations and transitions

## API Documentation

### **Server Status API**
```bash
# Get real-time server status
GET /api/server/status

# Response:
{
  "status": "online",
  "players_online": 27,
  "uptime": "2d 14h 23m",
  "response_time": "35ms",
  "database_connections": 42,
  "load_balancer": {
    "instances": 2,
    "healthy": 2
  }
}
```

### **Monitoring API**
```bash
# Get Prometheus metrics
GET /api/metrics/prometheus

# Get system performance
GET /api/metrics/system

# Get database performance
GET /api/metrics/database
```

### **Admin Management API**
```bash
# Get player list
GET /api/admin/players

# Server management actions
POST /api/admin/server/restart
POST /api/admin/server/config
```

## Advanced Configuration

### **Prometheus Configuration**
The monitoring stack includes FFXI-specific recording rules:
```yaml
groups:
  - name: ffxi.rules
    rules:
      - record: ffxi:players_online_rate
        expr: rate(ffxi_players_online_total[5m])
      - record: ffxi:database_connections_avg
        expr: avg_over_time(mysql_threads_connected[1m])
```

### **Grafana Dashboard Configuration**
Pre-configured dashboards include:
- **FFXI Server Overview**: Player counts, system metrics, alerts
- **Database Performance**: Query performance, connection pooling
- **System Resources**: CPU, memory, disk, network metrics
- **Load Balancer**: Multi-instance monitoring and traffic distribution

### **Alert Rules**
Custom alert rules for FFXI server monitoring:
```yaml
groups:
  - name: ffxi.alerts
    rules:
      - alert: FFXIServerDown
        expr: up{job="ffxi-server"} == 0
        for: 1m
        annotations:
          summary: "FFXI Server is down"
      
      - alert: HighPlayerLoad
        expr: ffxi_players_online > 100
        for: 5m
        annotations:
          summary: "High player count detected"
```

## Monitoring Stack Details

### **Prometheus Setup**
- **Metrics collection** from all server components
- **Custom recording rules** for FFXI-specific metrics
- **Alert rules** for proactive monitoring
- **Data retention** configurable (default: 15 days)

### **Grafana Integration**
- **Pre-configured data sources** connecting to Prometheus
- **Custom dashboards** for FFXI server monitoring
- **Alert channels** for notifications
- **User authentication** with admin controls

### **Node Exporter Metrics**
- System CPU, memory, disk, and network metrics
- Process monitoring for FFXI server components
- File system monitoring and alerts
- Hardware health monitoring

### **MySQL Exporter Metrics**
- Database connection pool monitoring
- Query performance and slow query tracking
- InnoDB buffer pool statistics
- Replication status and lag monitoring

## Troubleshooting

### **Web Interface Issues**
```bash
# Check web interface availability
curl -f http://localhost:8000

# Check API endpoints
curl -f http://localhost:8000/api/server/status

# View web server logs
docker-compose logs -f web-admin
```

### **Monitoring Stack Issues**
```bash
# Check Prometheus health
curl -f http://localhost:9090/-/healthy

# Check Grafana health
curl -f http://localhost:3000/api/health

# Verify metrics collection
curl http://localhost:9090/api/v1/targets
```

### **Performance Optimization**
- **Enable Redis caching**: Use `COMPOSE_PROFILES=redis,monitoring`
- **Adjust refresh rates**: Configure dashboard update intervals
- **Optimize queries**: Use database performance monitoring
- **Scale instances**: Use multi-instance profile for load distribution

## Database Schema Integration

### Accounts Table Usage
- `id` - Unique account identifier
- `login` - Username for authentication
- `password` - SHA-256 hashed password
- `current_email` - User email address
- `status` - Account status (0=pending, 1=active, 2=banned)
- `priv` - Privilege level (1=user, 2=moderator, 3=admin)
- `content_ids` - Character limit per account

### Characters Table Integration
- `charid` - Character identifier
- `accid` - Links to accounts table
- `charname` - Character name
- `gmlevel` - GM privilege level
- Character stats, position, and game data

## Security Considerations

### Password Security
- SHA-256 hashing for password storage
- No plaintext passwords stored
- Session-based authentication

### Access Control
- Role-based permissions (user/moderator/admin)
- Session validation for all protected routes
- Database query parameterization to prevent SQL injection

### User Data Protection
- Character data only accessible by account owner
- Admin functions restricted to appropriate privilege levels
- Secure session management with Flask sessions

## Customization Options

### Appearance
- Responsive dark theme design
- Mobile-friendly interface
- Customizable CSS styling

### Functionality
- Configurable character limits
- Adjustable approval requirements
- Customizable refresh intervals
- Flexible alert thresholds

## Integration with Existing LandSandBoat Features

### Database Compatibility
- Uses existing database schema
- Compatible with current account/character system
- Integrates with inventory and auction house systems

### Server Integration
- Works alongside existing server processes
- Provides monitoring for xi_map, xi_login, xi_search
- Real-time integration with game data

This enhanced web administration panel provides a comprehensive solution for managing LandSandBoat server users, characters, and administrative functions through a modern web interface.