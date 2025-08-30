# LandSandBoat Administrative Tools Installation & Usage Guide

## 📋 Overview

This guide covers the installation, configuration, and usage of the enhanced administrative tools for LandSandBoat FFXI server emulator.

## 🛠️ Installation

### Prerequisites

1. **Python 3.8+** with pip
2. **LandSandBoat server** installation
3. **MariaDB/MySQL** database access

### Install Python Dependencies

```bash
cd /path/to/landsandboat
pip3 install -r tools/requirements.txt
```

Required packages:
- `mysql-connector-python` - Database connectivity
- `flask` - Web administration panel
- `rich` - Enhanced console output
- `psutil` - System monitoring
- `sqlite3` - Analytics database (included in Python)

### Verify Installation

```bash
python3 tools/test_admin_tools.py
```

## 🎛️ Administrative Dashboard

### Basic Usage

```bash
# Start real-time monitoring dashboard
python3 tools/admin_dashboard.py

# Generate performance report for last 24 hours
python3 tools/admin_dashboard.py --report 24

# Use custom configuration
python3 tools/admin_dashboard.py --config config/admin.json
```

### Configuration

Create `config/admin.json`:

```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "database": "xidb",
    "user": "your_username",
    "password": "your_password"
  },
  "monitoring": {
    "refresh_interval": 2,
    "history_retention_hours": 24,
    "alert_thresholds": {
      "cpu_percent": 80,
      "memory_percent": 85,
      "disk_percent": 90,
      "players_max": 500
    }
  }
}
```

### Dashboard Features

- **Real-time System Metrics**: CPU, memory, disk, network usage
- **Server Process Monitoring**: Track xi_map, xi_login, xi_search processes
- **Database Metrics**: Player counts, connection status
- **Alert System**: Automated warnings for threshold violations
- **Historical Data**: SQLite storage for trend analysis

### Controls

- `Ctrl+C` - Exit dashboard
- `R` - Force refresh (if implemented)
- Dashboard auto-refreshes every 2 seconds (configurable)

## 🌐 Web Administration Panel

### Starting the Web Panel

```bash
# Start with default settings (localhost:8080)
python3 tools/web_admin.py

# Specify host and port
python3 tools/web_admin.py --host 0.0.0.0 --port 8081

# Enable debug mode
python3 tools/web_admin.py --debug

# Use custom configuration
python3 tools/web_admin.py --config config/admin.json
```

### Accessing the Interface

1. Open web browser
2. Navigate to `http://localhost:8080` (or configured address)
3. Dashboard loads automatically with real-time updates

### Web Panel Features

- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Charts**: Live CPU and player activity graphs
- **Server Controls**: Restart servers, emergency shutdown
- **Database Management**: Backup initiation, connection monitoring
- **Alert Display**: Visual notifications for system issues

### API Endpoints

The web panel exposes REST API endpoints:

```bash
# Get system status
curl http://localhost:8080/api/status

# Restart map server
curl -X POST http://localhost:8080/api/restart \
  -H "Content-Type: application/json" \
  -d '{"server": "map"}'

# Emergency shutdown
curl -X POST http://localhost:8080/api/shutdown

# Start database backup
curl -X POST http://localhost:8080/api/backup
```

## 📊 Player Analytics

### Basic Analytics Commands

```bash
# Generate comprehensive analytics report
python3 tools/player_analytics.py --report

# Collect fresh session data
python3 tools/player_analytics.py --collect

# Monitor real-time performance
python3 tools/player_analytics.py --monitor

# Generate report with visualizations (requires matplotlib)
python3 tools/player_analytics.py --report --visualize
```

### Analytics Features

1. **Player Sessions**
   - Session duration analysis
   - Login/logout pattern tracking
   - Activity level categorization

2. **Zone Popularity**
   - Most visited zones
   - Average time spent per zone
   - Player distribution patterns

3. **Retention Analysis**
   - Daily/weekly/monthly retention rates
   - Player lifecycle tracking
   - Churn prediction indicators

4. **Peak Hours Identification**
   - Hourly player distribution
   - Load pattern analysis
   - Capacity planning insights

### Sample Analytics Output

```
📊 LandSandBoat System Report - Last 24 hours

Performance Summary
┏━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┓
┃ Metric      ┃ Average ┃ Peak   ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━┩
│ CPU Usage   │ 45.2%   │ 78.9%  │
│ Memory      │ 62.1%   │ 84.3%  │
└─────────────┴─────────┴────────┘

👥 Player Activity:
Average Players: 127.3
Peak Players: 234
Data Points: 720

🕐 Peak Hours: 19:00, 20:00, 21:00, 22:00
📈 Max Concurrent: 234 players
⚡ Peak Threshold: 164 sessions
```

## 🔧 Configuration Management

### Database Configuration

All tools support the same database configuration format:

```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "database": "xidb", 
    "user": "root",
    "password": "",
    "charset": "utf8mb4",
    "autocommit": true
  }
}
```

### Monitoring Thresholds

Customize alert thresholds in configuration:

```json
{
  "monitoring": {
    "alert_thresholds": {
      "cpu_percent": 80,      // CPU usage warning threshold
      "memory_percent": 85,   // Memory usage warning threshold  
      "disk_percent": 90,     // Disk usage critical threshold
      "players_max": 500,     // Maximum expected players
      "response_time_ms": 100 // Response time threshold
    }
  }
}
```

### Web Panel Configuration

```json
{
  "web": {
    "host": "0.0.0.0",       // Bind to all interfaces
    "port": 8080,            // Web server port
    "debug": false,          // Enable debug mode
    "secret_key": "your-secret-key-here"
  }
}
```

## 📈 Usage Examples

### Daily Server Health Check

```bash
#!/bin/bash
# daily_health_check.sh

echo "🔍 Daily LandSandBoat Health Check"
echo "=================================="

# Run analytics report
python3 tools/player_analytics.py --report > daily_report.txt

# Check for alerts in dashboard
python3 tools/admin_dashboard.py --report 24 | grep -E "(🔴|⚠️)" > alerts.txt

# Send email if alerts found (optional)
if [ -s alerts.txt ]; then
    mail -s "LandSandBoat Alerts" admin@yourserver.com < alerts.txt
fi

echo "✅ Health check complete"
```

### Automated Performance Monitoring

```bash
#!/bin/bash
# performance_monitor.sh

# Collect performance data every 5 minutes
while true; do
    python3 tools/player_analytics.py --monitor
    sleep 300
done
```

### Emergency Response Script

```bash
#!/bin/bash
# emergency_response.sh

echo "🚨 Emergency server response initiated"

# Get current status
curl -s http://localhost:8080/api/status | jq .

# Check for critical alerts
python3 tools/admin_dashboard.py --report 1 | grep "🔴"

# Optional: Automated restart if needed
# curl -X POST http://localhost:8080/api/restart -d '{"server": "map"}'

echo "✅ Emergency response complete"
```

## 🔐 Security Considerations

### Access Control

1. **Web Panel Security**
   - Run behind reverse proxy (nginx/apache)
   - Use HTTPS in production
   - Implement authentication if exposed publicly

2. **Database Security**
   - Use dedicated monitoring user with limited privileges
   - Avoid root access for monitoring
   - Enable SSL connections if available

3. **System Security**
   - Run tools with minimal required privileges
   - Monitor logs directory permissions
   - Regular security updates for dependencies

### Recommended Database User

```sql
-- Create monitoring user with minimal privileges
CREATE USER 'monitor'@'localhost' IDENTIFIED BY 'secure_password';
GRANT SELECT ON xidb.chars TO 'monitor'@'localhost';
GRANT SELECT ON xidb.accounts TO 'monitor'@'localhost';
GRANT SELECT ON xidb.zone_settings TO 'monitor'@'localhost';
GRANT SHOW VIEW ON xidb.* TO 'monitor'@'localhost';
FLUSH PRIVILEGES;
```

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip3 install --user -r tools/requirements.txt
   ```

2. **Database connection failures**
   - Verify database credentials
   - Check MySQL/MariaDB service status
   - Confirm network connectivity

3. **Web panel won't start**
   - Check if port is already in use: `netstat -ln | grep :8080`
   - Try different port: `--port 8081`
   - Check firewall settings

4. **Permission denied on logs directory**
   ```bash
   mkdir -p logs
   chmod 755 logs
   ```

### Debug Mode

Enable debug output for troubleshooting:

```bash
# Dashboard with verbose output
PYTHONPATH=. python3 -v tools/admin_dashboard.py

# Web panel with debug mode
python3 tools/web_admin.py --debug

# Analytics with error details
python3 tools/player_analytics.py --report 2>&1 | tee debug.log
```

### Log Files

Check these locations for diagnostic information:

- `logs/admin_dashboard.db` - Dashboard metrics
- `logs/player_analytics.db` - Analytics data
- `logs/analytics_report_YYYYMMDD_HHMMSS.json` - Generated reports
- Flask debug output when `--debug` is used

## 📞 Support

For issues with the administrative tools:

1. Check this documentation
2. Review troubleshooting section
3. Check GitHub issues
4. Submit bug reports with:
   - Tool version and command used
   - Error messages and logs
   - System configuration details
   - Database configuration (without credentials)

## 🔄 Updates and Maintenance

### Updating Dependencies

```bash
# Check for outdated packages
pip3 list --outdated

# Update all packages
pip3 install -r tools/requirements.txt --upgrade

# Verify tools still work
python3 tools/test_admin_tools.py
```

### Regular Maintenance

1. **Weekly**: Review analytics reports for trends
2. **Monthly**: Update dependencies and run security scans
3. **Quarterly**: Review alert thresholds and adjust as needed
4. **Annually**: Full system performance review and optimization

This completes the comprehensive guide for LandSandBoat's enhanced administrative tools. The tools provide powerful monitoring, analytics, and management capabilities while maintaining ease of use and security best practices.