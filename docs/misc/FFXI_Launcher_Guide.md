# FFXI Server Launcher Documentation

## Overview

The FFXI Server Launcher is a comprehensive client management solution that provides seamless integration with Ashita v4 and full .env configuration support. It combines the power of modern launcher technology with the proven Ashita framework for enhanced FFXI client functionality.

## Features

### Core Functionality
- **Dual Interface**: Both GUI and command-line interfaces for different user preferences
- **Ashita v4 Integration**: Full compatibility with Ashita v4 beta framework
- **Configuration Management**: .env file-based configuration with validation
- **Server Status**: Real-time server connectivity checking
- **Client Validation**: Automatic client installation verification

### Advanced Features
- **Auto-Configuration**: Generates Ashita-compatible configuration files automatically
- **Multi-Language Support**: Handles DE/EN/FR/US client variants
- **Update Management**: Integrated with FFXI content delivery system
- **Security Validation**: File integrity checking and corruption detection

## Installation

### Download
1. Visit the FFXI server web interface
2. Navigate to the launcher download section
3. Click "Download Launcher" to get the complete package
4. Extract the ZIP file to your preferred location

### System Requirements
- Windows 7 or newer
- FFXI client installed
- .NET Framework 4.7.2 or newer
- VC++ Redistributable 2015-2022
- 50 MB free disk space
- Internet connection for server communication

## Configuration

### Basic Setup
1. Copy `.env.example` to `.env`
2. Edit the configuration file with your server details:

```bash
# Server Configuration
FFXI_SERVER_NAME=Your Server Name
FFXI_SERVER_HOST=your.server.com
FFXI_LOGIN_PORT=54001
FFXI_MAP_PORT=54230
FFXI_SEARCH_PORT=54002

# Client Configuration
FFXI_CLIENT_PATH=C:\Program Files (x86)\SquareEnix\FINAL FANTASY XI
FFXI_WINDOWER_COMPATIBLE=true
FFXI_ASHITA_COMPATIBLE=true
FFXI_AUTO_UPDATE=true

# Advanced Settings
FFXI_CLIENT_TIMEOUT=30000
```

### Port Configuration
The launcher supports standard FFXI server ports:
- **Login Port**: 54001 (default)
- **Map Port**: 54230 (default)
- **Search Port**: 54002 (default)

## Usage

### GUI Mode
1. Run `FFXI_Launcher.exe`
2. Configure server settings in the "Server Settings" tab
3. Set client path and compatibility options in "Client Settings"
4. Use "Launch" tab to check server status and start the client

### Command Line Mode

#### Generate Configuration
```bash
FFXI_Launcher.exe --generate-config .env ashita_config.ini
```

#### Check Server Status
```bash
FFXI_Launcher.exe --check-server .env
```

## Ashita Integration

### Automatic Configuration
The launcher automatically generates Ashita v4 compatible configuration files with:
- Proper server connection settings
- Optimized performance parameters
- Client compatibility options
- Language and localization settings

### Configuration Templates
Generated configurations include:
- **Boot Configuration**: Server connection and game module settings
- **Display Settings**: Resolution, windowed mode, and graphics options
- **Input Configuration**: Keyboard, mouse, and gamepad settings
- **Plugin Settings**: Ashita plugin and addon configuration

### Example Generated Config
```ini
[ashita.boot]
file = .\bootloader\pol.exe
command = --server your.server.com
gamemodule = ffximain.dll
script = default.txt

[ffxi.registry]
0000 = 6        # Window mode
0001 = 1920      # Screen width
0002 = 1080      # Screen height
0017 = 0         # Windowed mode
0042 = C:\Program Files (x86)\SquareEnix\FINAL FANTASY XI
```

## API Integration

### Server Status API
The launcher integrates with FFXI server APIs for:
- Real-time server status checking
- Client update availability
- File validation and integrity checking
- Download statistics and monitoring

### Endpoints Used
- `/api/ffxi/updates/available` - Check for client updates
- `/api/ffxi/validate` - Validate client files
- `/api/server/status` - Server connectivity status

## Troubleshooting

### Common Issues

#### Launcher Won't Start
- Verify .NET Framework 4.7.2+ is installed
- Check Windows version compatibility (Windows 7+)
- Run as administrator if permission issues occur

#### Server Connection Failed
- Verify server host and port settings in .env file
- Check firewall settings for FFXI ports
- Confirm server is online using status check feature

#### Client Path Issues
- Ensure FFXI client is properly installed
- Verify path points to directory containing `ffximain.dll`
- Check for proper file permissions

#### Ashita Configuration Problems
- Verify Ashita files are present in `ashita/` directory
- Check generated configuration file syntax
- Ensure client compatibility settings are correct

### Debug Mode
Enable debug logging by setting environment variables:
```bash
FFXI_DEBUG_MODE=true
FFXI_LOG_LEVEL=DEBUG
```

## Advanced Configuration

### Network Settings
For servers with special network configurations:
```bash
FFXI_ENABLE_BONDING=true
FFXI_CONNECTION_POOL_SIZE=20
FFXI_TCP_NODELAY=true
FFXI_SOCKET_BUFFER_SIZE=65536
```

### Performance Tuning
```bash
FFXI_ENABLE_HIGH_PERFORMANCE=true
FFXI_ENABLE_CONNECTION_POOLING=true
FFXI_CLIENT_TIMEOUT=30000
FFXI_PACKET_BUFFER_SIZE=8192
```

### Security Options
```bash
FFXI_ENABLE_FIREWALL=true
FFXI_RATE_LIMIT_ENABLED=true
FFXI_MAX_CONNECTIONS_PER_IP=50
```

## Development

### Building from Source
1. Install Python 3.12+ and required dependencies
2. Run the build script:
```bash
python tools/build_launcher.py
```

### Dependencies
- PyInstaller for executable creation
- tkinter for GUI interface
- configparser for configuration management
- urllib for server communication

### Testing
```bash
# Test configuration generation
python tools/ffxi_launcher.py --generate-config test.env test.ini

# Test server connectivity
python tools/ffxi_launcher.py --check-server test.env
```

## License

This launcher is part of the FFXI Server project and follows the same licensing terms. Ashita v4 components are included under their respective licenses.

## Support

For issues and support:
1. Check the troubleshooting section above
2. Review server logs for connection issues
3. Verify configuration file syntax
4. Submit issues to the project repository

## Changelog

### Version 1.0.0
- Initial release with Ashita v4 integration
- .env configuration support
- GUI and CLI interfaces
- Automatic configuration generation
- Server status checking
- Client validation features