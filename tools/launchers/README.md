# Launcher and Client Management Tools

This directory contains game launcher tools, client management utilities, and FFXI-specific tools.

## Tools

### Game Launchers
- `ffxi_launcher.py` - Main FFXI launcher (moved from launcher_build/ffxi/)
- `testworkflowserver_launcher.py` - Test workflow launcher (moved from launcher_build/testworkflowserver/)

### Client Management
- `ffxi_client_manager.py` - FFXI client management and coordination
- `ffxi_content_delivery.py` - Content delivery and updates
- `ffxi_content_manager.py` - Content management system

## Usage

### FFXI Launcher
```bash
python ffxi_launcher.py
```

### Client Management
```bash
python ffxi_client_manager.py
```

### Content Management
```bash
python ffxi_content_manager.py
python ffxi_content_delivery.py
```

## Features

- FFXI client launcher with configuration management
- Content delivery and update system
- Client state management
- Multi-client coordination
- Test workflow integration

## Configuration

Launcher tools use:
- Game client configuration files
- Network settings from `../../settings/network.lua`
- Client-specific configuration options

## Integration

Launcher tools integrate with:
- FFXI game client
- Server infrastructure
- Content delivery systems
- Testing frameworks