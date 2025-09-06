# FFXI Server Launcher

## Installation

1. Extract all files to a directory of your choice
2. Copy `.env.example` to `.env` and edit the server settings
3. Run `FFXI_Launcher.exe`

## Configuration

Edit the `.env` file to configure your server connection:

```
FFXI_SERVER_NAME=Your Server Name
FFXI_SERVER_HOST=your.server.com
FFXI_LOGIN_PORT=54001
FFXI_MAP_PORT=54230
FFXI_SEARCH_PORT=54002
FFXI_CLIENT_PATH=C:\Program Files (x86)\SquareEnix\FINAL FANTASY XI
```

## Usage

### GUI Mode
Run `FFXI_Launcher.exe` for the graphical interface.

### Command Line Mode
```bash
FFXI_Launcher.exe --generate-config .env ashita_config.ini
FFXI_Launcher.exe --check-server .env
```

## Requirements

- Windows 7 or newer
- FFXI client installed
- .NET Framework 4.7.2 or newer
- VC++ Redistributable 2015-2022

## Ashita Integration

This launcher includes Ashita v4 integration for enhanced FFXI client functionality:

- Automatic configuration generation
- Client validation and updates
- Windowed mode support
- Plugin and addon compatibility

## Support

For support and updates, visit: https://github.com/mupoese/FFXI-Server
