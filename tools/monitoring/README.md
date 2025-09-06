# Monitoring and Performance Tools

This directory contains performance monitoring, profiling, and system analysis tools.

## Tools

### Performance Monitoring
- `advanced_performance_monitor.py` - Real-time web dashboard at http://localhost:8080
- `performance_monitor.py` - Core performance monitoring
- `advanced_profiler.py` - Threading and concurrency analysis

### Database Performance
- `db_performance_monitor.py` - Database-specific performance tracking

### Network Performance
- `network_bonding_performance_test.py` - Network bonding performance testing

## Usage

### Real-time Performance Dashboard
```bash
python advanced_performance_monitor.py
# Access at http://localhost:8080
```

### Advanced Profiling
```bash
python advanced_profiler.py --threading
```

### Database Performance Monitoring
```bash
python db_performance_monitor.py
```

## Features

- Real-time server process monitoring (xi_connect, xi_search, xi_map, xi_world)
- Database performance tracking and automated alerting
- Memory profiling and optimization recommendations
- Threading and concurrency analysis
- Network performance validation
- Web-based dashboards for real-time monitoring

## Output

Monitoring tools generate:
- Real-time web dashboards
- Performance metrics reports
- Alert notifications
- Profiling analysis reports