# Configurable Server Branding System

This document explains how to use the new configurable server branding system that allows you to rebrand the entire FFXI server infrastructure with your own server name.

## Overview

The system uses a single environment variable `SERVERNAME` to control all branding throughout the server infrastructure. Instead of hardcoded "FFXI" references, all components dynamically adapt to your server name.

## Quick Start

1. **Set Your Server Name**
   ```bash
   # In your .env file
   SERVERNAME=MyAwesomeServer
   ```

2. **Update Configuration Variables**
   ```bash
   # All settings now use your server name as prefix
   MYAWESOMESERVER_SERVER_NAME=My Awesome Private Server
   MYAWESOMESERVER_SERVER_HOST=myserver.com
   MYAWESOMESERVER_LOGIN_PORT=54001
   MYAWESOMESERVER_MAP_PORT=54230
   MYAWESOMESERVER_SEARCH_PORT=54002
   MYAWESOMESERVER_ADMIN_USERNAME=admin
   MYAWESOMESERVER_ADMIN_PASSWORD=secure_password_123
   ```

3. **Build Your Branded Launcher**
   ```bash
   python tools/enhanced_build_launcher.py
   ```

4. **Start Your Server**
   ```bash
   python web/api/app.py
   ```

## What Changes

### 🚀 Launcher
- **File Name**: `MyAwesomeServer_Launcher.exe` (instead of `FFXI_Launcher.exe`)
- **Window Title**: "MyAwesomeServer Server Launcher"
- **Login Screen**: Shows your server branding
- **Configuration**: All settings use `MYAWESOMESERVER_` prefix

### 🌐 Web Interface
- **Page Title**: "LandSandBoat MyAwesomeServer Server - Welcome to Vana'diel"
- **Content System**: "MyAwesomeServer Content System"
- **Download Links**: Points to `MyAwesomeServer_Launcher.zip`
- **Configuration Examples**: Shows your server name variables

### 🔧 API Endpoints
- **Authentication**: Uses `MYAWESOMESERVER_ADMIN_USERNAME` and `MYAWESOMESERVER_ADMIN_PASSWORD`
- **Database**: Uses `MYAWESOMESERVER_SQL_HOST`, `MYAWESOMESERVER_SQL_DATABASE`, etc.
- **Responses**: Include your server name in JSON responses

### 🗄️ Database
- **Connection Pool**: Named `myawesomeserver_api_pool`
- **Configuration**: Uses your server-specific environment variables
- **Content Path**: `/opt/myawesomeserver/client_content`

## Configuration Examples

### Basic Server Configuration
```bash
# .env file for "WoWClassic" server
SERVERNAME=WoWClassic

# Server settings
WOWCLASSIC_SERVER_NAME=WoW Classic Private Server
WOWCLASSIC_SERVER_HOST=wowclassic.example.com
WOWCLASSIC_LOGIN_PORT=54001
WOWCLASSIC_MAP_PORT=54230
WOWCLASSIC_SEARCH_PORT=54002

# Authentication
WOWCLASSIC_ADMIN_USERNAME=gm_admin
WOWCLASSIC_ADMIN_PASSWORD=super_secure_password

# Database
WOWCLASSIC_SQL_HOST=db.wowclassic.example.com
WOWCLASSIC_SQL_DATABASE=wowclassic_db
WOWCLASSIC_SQL_LOGIN=wowclassic_user
WOWCLASSIC_SQL_PASSWORD=db_password_123
```

### Development Server Configuration
```bash
# .env file for development
SERVERNAME=DevTest

# Development settings
DEVTEST_SERVER_NAME=Development Test Server
DEVTEST_SERVER_HOST=localhost
DEVTEST_LOGIN_PORT=54001
DEVTEST_MAP_PORT=54230
DEVTEST_SEARCH_PORT=54002

# Dev authentication
DEVTEST_ADMIN_USERNAME=dev
DEVTEST_ADMIN_PASSWORD=dev123

# Local database
DEVTEST_SQL_HOST=localhost
DEVTEST_SQL_DATABASE=devtest_db
DEVTEST_SQL_LOGIN=devtest_user
DEVTEST_SQL_PASSWORD=devtest_pass
```

### Production Server Configuration
```bash
# .env file for production
SERVERNAME=EliteFFXI

# Production settings
ELITEFFXI_SERVER_NAME=Elite FFXI - Premium Experience
ELITEFFXI_SERVER_HOST=play.eliteffxi.com
ELITEFFXI_LOGIN_PORT=54001
ELITEFFXI_MAP_PORT=54230
ELITEFFXI_SEARCH_PORT=54002

# Secure authentication
ELITEFFXI_ADMIN_USERNAME=admin_elite
ELITEFFXI_ADMIN_PASSWORD=ultra_secure_password_2024

# Production database
ELITEFFXI_SQL_HOST=db-cluster.eliteffxi.com
ELITEFFXI_SQL_DATABASE=eliteffxi_production
ELITEFFXI_SQL_LOGIN=eliteffxi_app
ELITEFFXI_SQL_PASSWORD=production_db_password
```

## Building and Distribution

### 1. Build Branded Launcher
```bash
# The build script reads your .env file and bakes the configuration into the executable
python tools/enhanced_build_launcher.py

# This creates:
# - launcher_build/yourserver/yourserver_launcher.py (configured source)
# - launcher_build/yourserver/dist/YourServer_Launcher.exe (executable)
# - launcher_build/yourserver/YourServer_Launcher.zip (complete package)
```

### 2. Distribute to Players
The generated package includes:
- `YourServer_Launcher.exe` - Main launcher executable with baked configuration
- `ashita/` - Ashita v4 components for enhanced gameplay
- `.env.example` - Example configuration file for players
- `README.md` - Setup instructions specific to your server

### 3. Player Setup
Players only need to:
1. Download and extract `YourServer_Launcher.zip`
2. (Optional) Copy `.env.example` to `.env` and customize settings
3. Run `YourServer_Launcher.exe`
4. Login with their credentials

## Advanced Configuration

### Custom Branding Beyond Server Name
While the server name controls the main branding, you can customize further:

```bash
# Custom display names
MYSERVER_SERVER_NAME=My Custom Display Name Here
MYSERVER_DESCRIPTION=The best private server experience

# Custom paths and directories
MYSERVER_CLIENT_PATH=C:\\Games\\MyServer\\Client
MYSERVER_CONTENT_PATH=/opt/myserver/content

# Custom networking
MYSERVER_ENABLE_BONDING=true
MYSERVER_BONDING_MODE=balance-xor
MYSERVER_MAX_CONNECTIONS_PER_IP=10
```

### Multi-Instance Support
You can run multiple branded servers on the same machine:

```bash
# First server instance
SERVERNAME=ServerOne
SERVERONE_LOGIN_PORT=54001
SERVERONE_MAP_PORT=54230
SERVERONE_SQL_DATABASE=serverone_db

# Second server instance
SERVERNAME=ServerTwo  
SERVERTWO_LOGIN_PORT=55001
SERVERTWO_MAP_PORT=55230
SERVERTWO_SQL_DATABASE=servertwo_db
```

## Testing Your Configuration

Use the test script to verify your configuration:
```bash
SERVERNAME=YourServerName python tools/test_configurable_server.py
```

This will test:
- ✅ Configuration loading
- ✅ Database connections
- ✅ API branding
- ✅ Build system
- ✅ Web interface adaptation

## Migration from FFXI Hardcoded System

If you have an existing FFXI server installation:

1. **Backup your current .env file**
2. **Add SERVERNAME variable**: `SERVERNAME=FFXI`
3. **Rename existing variables**: `FFXI_SERVER_HOST=...` (if not already using this format)
4. **Test the system**: Run the test script to verify everything works
5. **Rebuild launcher**: Generate new branded launcher package
6. **Update documentation**: Provide new setup instructions to players

## Troubleshooting

### Common Issues

**Q: Launcher shows "FFXI" instead of my server name**
A: Rebuild the launcher after setting SERVERNAME. The branding is baked in during build time.

**Q: Web interface still shows FFXI branding**
A: The web interface updates dynamically via JavaScript. Ensure your API is serving the correct server name in `/api/ports` endpoint.

**Q: Database connection fails**
A: Check that your database environment variables use the correct prefix (e.g., `MYSERVER_SQL_HOST` not `FFXI_SQL_HOST`).

**Q: Authentication doesn't work**
A: Verify `MYSERVER_ADMIN_USERNAME` and `MYSERVER_ADMIN_PASSWORD` are set correctly in your .env file.

### Debug Mode
Enable debug logging:
```bash
MYSERVER_DEBUG_MODE=true
MYSERVER_LOG_LEVEL=DEBUG
```

## API Reference

### Dynamic Endpoints
All API endpoints remain the same (`/api/ffxi/...`) for compatibility, but responses include your server branding:

```json
{
  "server_name": "YourServerName",
  "ports": {
    "LOGIN_DATA_PORT": 54001,
    "MAP_PORT": 54230
  },
  "service": "YourServerName Server Management API"
}
```

### Authentication Response
```json
{
  "token": "...",
  "expires_in": 86400,
  "token_type": "Bearer",
  "server_name": "YourServerName"
}
```

This system provides complete flexibility while maintaining compatibility with existing setups. Your server can have its own unique identity while leveraging the powerful FFXI server infrastructure.