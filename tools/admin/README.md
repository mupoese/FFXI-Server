# Admin Tools

This directory contains administration and management tools for the FFXI-Server.

## Tools

### Core Admin Tools
- `admin_dashboard.py` - Real-time server monitoring dashboard
- `web_admin.py` - Web-based administration interface  
- `player_analytics.py` - Player behavior and analytics tracking
- `announce.py` - Server-wide announcement system
- `demo_web_admin.py` - Web admin demo interface

### Testing Tools
- `admin_dashboard_test.py` - Admin dashboard testing suite
- `test_web_admin.py` - Web admin interface testing

## Usage

### Real-time Dashboard
```bash
python admin_dashboard.py
```

### Web Administration
```bash
python web_admin.py
# Access at http://localhost:8080
```

### Server Announcements
```bash
python announce.py "Your message here"
```

## Configuration

Most admin tools use configuration from:
- `../web_admin_config.json` - Web admin settings
- `../../settings/network.lua` - Database connection settings

## Security

Admin tools require appropriate permissions and should only be run by authorized administrators.