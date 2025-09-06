#!/usr/bin/env python3
"""
Advanced Performance Monitoring Dashboard for FFXI-Server
Real-time server performance tracking with comprehensive metrics and alerting.

This tool provides real-time monitoring of server performance, database metrics,
network statistics, and player activity with intelligent alerting and optimization
recommendations for FFXI game server operations.
"""

import os
import sys
import time
import json
import sqlite3
import psutil
import socket
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import argparse
import signal

try:
    import mariadb
    MARIADB_AVAILABLE = True
except ImportError:
    MARIADB_AVAILABLE = False

try:
    from flask import Flask, render_template_string, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    timestamp: float
    metric_name: str
    value: float
    unit: str
    category: str
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ServerStatus:
    """Server status information"""
    process_name: str
    pid: Optional[int]
    status: str  # running, stopped, crashed
    cpu_percent: float
    memory_mb: float
    uptime_seconds: float
    connections: int
    last_check: float

class AdvancedPerformanceMonitor:
    """Advanced performance monitoring system"""
    
    def __init__(self, config_path: str = "performance_monitor_config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.metrics_history = deque(maxlen=self.config.get('max_history', 10000))
        self.alerts = deque(maxlen=self.config.get('max_alerts', 1000))
        self.server_processes = {}
        self.monitoring_active = False
        self.db_path = Path("performance_metrics.db")
        self.web_port = self.config.get('web_port', 8080)
        
        # Initialize database
        self.initialize_database()
        
        # Performance thresholds
        self.thresholds = {
            'cpu_percent': {'warning': 70.0, 'critical': 90.0},
            'memory_percent': {'warning': 80.0, 'critical': 95.0},
            'disk_usage_percent': {'warning': 85.0, 'critical': 95.0},
            'network_latency_ms': {'warning': 100.0, 'critical': 500.0},
            'database_connections': {'warning': 80, 'critical': 100},
            'query_time_ms': {'warning': 1000.0, 'critical': 5000.0}
        }
        
        # Server process names
        self.server_processes_config = {
            'xi_connect': {'port': 54001, 'name': 'Login Server'},
            'xi_search': {'port': 54002, 'name': 'Search Server'},
            'xi_map': {'port': 54230, 'name': 'Map Server'},
            'xi_world': {'port': 54003, 'name': 'World Server'}
        }

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            'monitor_interval': 5,
            'database_enabled': True,
            'web_interface_enabled': True,
            'web_port': 8080,
            'alert_email_enabled': False,
            'alert_email': '',
            'max_history': 10000,
            'max_alerts': 1000,
            'retention_days': 30
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def initialize_database(self):
        """Initialize SQLite database for metrics storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    category TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    threshold_type TEXT NOT NULL,
                    threshold_value REAL NOT NULL,
                    message TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS server_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    process_name TEXT NOT NULL,
                    pid INTEGER,
                    status TEXT NOT NULL,
                    cpu_percent REAL,
                    memory_mb REAL,
                    uptime_seconds REAL,
                    connections INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)')

    def collect_system_metrics(self) -> List[PerformanceMetric]:
        """Collect system performance metrics"""
        metrics = []
        timestamp = time.time()
        
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name='cpu_percent',
                value=cpu_percent,
                unit='percent',
                category='system',
                threshold_warning=self.thresholds['cpu_percent']['warning'],
                threshold_critical=self.thresholds['cpu_percent']['critical']
            ))
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name='memory_percent',
                value=memory.percent,
                unit='percent',
                category='system',
                threshold_warning=self.thresholds['memory_percent']['warning'],
                threshold_critical=self.thresholds['memory_percent']['critical']
            ))
            
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name='memory_available_gb',
                value=memory.available / (1024**3),
                unit='GB',
                category='system'
            ))
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name='disk_usage_percent',
                value=(disk.used / disk.total) * 100,
                unit='percent',
                category='system',
                threshold_warning=self.thresholds['disk_usage_percent']['warning'],
                threshold_critical=self.thresholds['disk_usage_percent']['critical']
            ))
            
            # Network metrics
            network = psutil.net_io_counters()
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name='network_bytes_sent',
                value=network.bytes_sent,
                unit='bytes',
                category='network'
            ))
            
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name='network_bytes_recv',
                value=network.bytes_recv,
                unit='bytes',
                category='network'
            ))
            
            # Load average (Unix only)
            if hasattr(os, 'getloadavg'):
                load_avg = os.getloadavg()
                metrics.append(PerformanceMetric(
                    timestamp=timestamp,
                    metric_name='load_average_1min',
                    value=load_avg[0],
                    unit='ratio',
                    category='system'
                ))
                
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
        
        return metrics

    def collect_server_metrics(self) -> List[PerformanceMetric]:
        """Collect FFXI server-specific metrics"""
        metrics = []
        timestamp = time.time()
        
        for process_name, config in self.server_processes_config.items():
            try:
                # Find process
                pid = None
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    if process_name in proc.info['name'] or \
                       any(process_name in arg for arg in (proc.info['cmdline'] or [])):
                        pid = proc.info['pid']
                        break
                
                if pid:
                    proc = psutil.Process(pid)
                    
                    # CPU usage
                    cpu_percent = proc.cpu_percent()
                    metrics.append(PerformanceMetric(
                        timestamp=timestamp,
                        metric_name=f'{process_name}_cpu_percent',
                        value=cpu_percent,
                        unit='percent',
                        category='server',
                        metadata={'process': process_name, 'pid': pid}
                    ))
                    
                    # Memory usage
                    memory_info = proc.memory_info()
                    memory_mb = memory_info.rss / (1024**2)
                    metrics.append(PerformanceMetric(
                        timestamp=timestamp,
                        metric_name=f'{process_name}_memory_mb',
                        value=memory_mb,
                        unit='MB',
                        category='server',
                        metadata={'process': process_name, 'pid': pid}
                    ))
                    
                    # Connection count (if port is accessible)
                    connections = self.count_connections(config['port'])
                    metrics.append(PerformanceMetric(
                        timestamp=timestamp,
                        metric_name=f'{process_name}_connections',
                        value=connections,
                        unit='count',
                        category='server',
                        metadata={'process': process_name, 'port': config['port']}
                    ))
                    
                    # Update server status
                    uptime = time.time() - proc.create_time()
                    self.server_processes[process_name] = ServerStatus(
                        process_name=process_name,
                        pid=pid,
                        status='running',
                        cpu_percent=cpu_percent,
                        memory_mb=memory_mb,
                        uptime_seconds=uptime,
                        connections=connections,
                        last_check=timestamp
                    )
                    
                else:
                    # Server not running
                    self.server_processes[process_name] = ServerStatus(
                        process_name=process_name,
                        pid=None,
                        status='stopped',
                        cpu_percent=0.0,
                        memory_mb=0.0,
                        uptime_seconds=0.0,
                        connections=0,
                        last_check=timestamp
                    )
                    
            except Exception as e:
                print(f"Error collecting metrics for {process_name}: {e}")
        
        return metrics

    def collect_database_metrics(self) -> List[PerformanceMetric]:
        """Collect database performance metrics"""
        metrics = []
        timestamp = time.time()
        
        if not MARIADB_AVAILABLE:
            return metrics
        
        try:
            # Database connection test
            start_time = time.time()
            conn = mariadb.connect(
                user='root',
                password='root',
                host='127.0.0.1',
                port=3306,
                database='xidb'
            )
            
            connection_time = (time.time() - start_time) * 1000
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name='database_connection_time_ms',
                value=connection_time,
                unit='ms',
                category='database'
            ))
            
            cursor = conn.cursor()
            
            # Connection count
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            result = cursor.fetchone()
            if result:
                connections = int(result[1])
                metrics.append(PerformanceMetric(
                    timestamp=timestamp,
                    metric_name='database_connections',
                    value=connections,
                    unit='count',
                    category='database',
                    threshold_warning=self.thresholds['database_connections']['warning'],
                    threshold_critical=self.thresholds['database_connections']['critical']
                ))
            
            # Query time test
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM accounts")
            query_time = (time.time() - start_time) * 1000
            
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name='database_query_time_ms',
                value=query_time,
                unit='ms',
                category='database',
                threshold_warning=self.thresholds['query_time_ms']['warning'],
                threshold_critical=self.thresholds['query_time_ms']['critical']
            ))
            
            # Table sizes
            cursor.execute("""
                SELECT table_name, 
                       round(((data_length + index_length) / 1024 / 1024), 2) as size_mb
                FROM information_schema.tables 
                WHERE table_schema = 'xidb'
                ORDER BY size_mb DESC
                LIMIT 5
            """)
            
            for table_name, size_mb in cursor.fetchall():
                metrics.append(PerformanceMetric(
                    timestamp=timestamp,
                    metric_name=f'table_size_{table_name}_mb',
                    value=float(size_mb),
                    unit='MB',
                    category='database',
                    metadata={'table': table_name}
                ))
            
            conn.close()
            
        except Exception as e:
            print(f"Error collecting database metrics: {e}")
        
        return metrics

    def count_connections(self, port: int) -> int:
        """Count active connections to a specific port"""
        try:
            connections = psutil.net_connections()
            count = 0
            for conn in connections:
                if conn.laddr and conn.laddr.port == port and conn.status == 'ESTABLISHED':
                    count += 1
            return count
        except Exception:
            return 0

    def check_thresholds(self, metric: PerformanceMetric) -> Optional[str]:
        """Check if metric exceeds thresholds"""
        if metric.threshold_critical and metric.value >= metric.threshold_critical:
            return 'critical'
        elif metric.threshold_warning and metric.value >= metric.threshold_warning:
            return 'warning'
        return None

    def generate_alert(self, metric: PerformanceMetric, threshold_type: str):
        """Generate an alert for threshold violation"""
        threshold_value = (metric.threshold_critical if threshold_type == 'critical' 
                          else metric.threshold_warning)
        
        message = (f"{threshold_type.upper()}: {metric.metric_name} is {metric.value}{metric.unit}, "
                  f"exceeding {threshold_type} threshold of {threshold_value}{metric.unit}")
        
        alert = {
            'timestamp': metric.timestamp,
            'metric_name': metric.metric_name,
            'value': metric.value,
            'threshold_type': threshold_type,
            'threshold_value': threshold_value,
            'message': message
        }
        
        self.alerts.append(alert)
        print(f"ALERT: {message}")
        
        # Save to database
        if self.config.get('database_enabled', True):
            self.save_alert_to_db(alert)

    def save_metric_to_db(self, metric: PerformanceMetric):
        """Save metric to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO metrics (
                        timestamp, metric_name, value, unit, category, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    metric.timestamp,
                    metric.metric_name,
                    metric.value,
                    metric.unit,
                    metric.category,
                    json.dumps(metric.metadata) if metric.metadata else None
                ))
        except Exception as e:
            print(f"Error saving metric to database: {e}")

    def save_alert_to_db(self, alert: Dict[str, Any]):
        """Save alert to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO alerts (
                        timestamp, metric_name, value, threshold_type, 
                        threshold_value, message
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    alert['timestamp'],
                    alert['metric_name'],
                    alert['value'],
                    alert['threshold_type'],
                    alert['threshold_value'],
                    alert['message']
                ))
        except Exception as e:
            print(f"Error saving alert to database: {e}")

    def cleanup_old_data(self):
        """Clean up old database records"""
        retention_days = self.config.get('retention_days', 30)
        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Clean up old metrics
                conn.execute('DELETE FROM metrics WHERE timestamp < ?', (cutoff_time,))
                
                # Clean up resolved alerts older than 7 days
                alert_cutoff = time.time() - (7 * 24 * 60 * 60)
                conn.execute('DELETE FROM alerts WHERE timestamp < ? AND resolved = TRUE', 
                           (alert_cutoff,))
                
        except Exception as e:
            print(f"Error cleaning up old data: {e}")

    def get_recent_metrics(self, metric_name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent metrics from database"""
        cutoff_time = time.time() - (hours * 60 * 60)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT timestamp, value, unit 
                    FROM metrics 
                    WHERE metric_name = ? AND timestamp > ?
                    ORDER BY timestamp
                ''', (metric_name, cutoff_time))
                
                return [
                    {'timestamp': row[0], 'value': row[1], 'unit': row[2]}
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            print(f"Error getting recent metrics: {e}")
            return []

    def get_system_summary(self) -> Dict[str, Any]:
        """Get current system summary"""
        try:
            # Get latest metrics for each category
            latest_metrics = {}
            for metric in list(self.metrics_history)[-50:]:  # Last 50 metrics
                latest_metrics[metric.metric_name] = metric
            
            # Server status summary
            servers = {}
            for name, status in self.server_processes.items():
                servers[name] = {
                    'status': status.status,
                    'cpu_percent': status.cpu_percent,
                    'memory_mb': status.memory_mb,
                    'connections': status.connections,
                    'uptime_hours': status.uptime_seconds / 3600 if status.uptime_seconds else 0
                }
            
            # Active alerts
            recent_alerts = [alert for alert in self.alerts if 
                           time.time() - alert['timestamp'] < 3600]  # Last hour
            
            return {
                'timestamp': time.time(),
                'system': {
                    'cpu_percent': latest_metrics.get('cpu_percent', {}).value if 'cpu_percent' in latest_metrics else 0,
                    'memory_percent': latest_metrics.get('memory_percent', {}).value if 'memory_percent' in latest_metrics else 0,
                    'disk_usage_percent': latest_metrics.get('disk_usage_percent', {}).value if 'disk_usage_percent' in latest_metrics else 0
                },
                'servers': servers,
                'alerts': {
                    'count': len(recent_alerts),
                    'critical': len([a for a in recent_alerts if a['threshold_type'] == 'critical']),
                    'warning': len([a for a in recent_alerts if a['threshold_type'] == 'warning'])
                }
            }
            
        except Exception as e:
            print(f"Error generating system summary: {e}")
            return {'error': str(e)}

    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        try:
            # Collect all metrics
            all_metrics = []
            all_metrics.extend(self.collect_system_metrics())
            all_metrics.extend(self.collect_server_metrics())
            all_metrics.extend(self.collect_database_metrics())
            
            # Process metrics
            for metric in all_metrics:
                # Add to history
                self.metrics_history.append(metric)
                
                # Check thresholds
                threshold_violation = self.check_thresholds(metric)
                if threshold_violation:
                    self.generate_alert(metric, threshold_violation)
                
                # Save to database
                if self.config.get('database_enabled', True):
                    self.save_metric_to_db(metric)
            
            # Periodic cleanup
            if len(self.metrics_history) % 1000 == 0:
                self.cleanup_old_data()
                
        except Exception as e:
            print(f"Error in monitoring cycle: {e}")

    def start_monitoring(self):
        """Start the monitoring loop"""
        print("Starting performance monitoring...")
        self.monitoring_active = True
        
        interval = self.config.get('monitor_interval', 5)
        
        try:
            while self.monitoring_active:
                cycle_start = time.time()
                
                self.run_monitoring_cycle()
                
                # Sleep for the remainder of the interval
                cycle_time = time.time() - cycle_start
                sleep_time = max(0, interval - cycle_time)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"Monitoring error: {e}")
        finally:
            self.monitoring_active = False

    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.monitoring_active = False

    def start_web_interface(self):
        """Start the web interface"""
        if not FLASK_AVAILABLE:
            print("Flask not available. Install with: pip install flask")
            return
        
        app = Flask(__name__)
        
        @app.route('/')
        def dashboard():
            return render_template_string(self.get_dashboard_html())
        
        @app.route('/api/summary')
        def api_summary():
            return jsonify(self.get_system_summary())
        
        @app.route('/api/metrics/<metric_name>')
        def api_metrics(metric_name):
            hours = request.args.get('hours', 24, type=int)
            return jsonify(self.get_recent_metrics(metric_name, hours))
        
        @app.route('/api/alerts')
        def api_alerts():
            recent_alerts = [alert for alert in self.alerts if 
                           time.time() - alert['timestamp'] < 86400]  # Last 24 hours
            return jsonify(recent_alerts)
        
        print(f"Starting web interface on port {self.web_port}")
        app.run(host='0.0.0.0', port=self.web_port, debug=False)

    def get_dashboard_html(self) -> str:
        """Get HTML for web dashboard"""
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>FFXI Server Performance Monitor</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #eee; }
        .metric:last-child { border-bottom: none; }
        .metric-value { font-size: 1.2em; font-weight: bold; }
        .status-running { color: #27ae60; }
        .status-stopped { color: #e74c3c; }
        .alert-critical { background: #e74c3c; color: white; padding: 10px; border-radius: 4px; margin: 5px 0; }
        .alert-warning { background: #f39c12; color: white; padding: 10px; border-radius: 4px; margin: 5px 0; }
        .progress-bar { background: #ecf0f1; height: 20px; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #27ae60, #f1c40f, #e74c3c); transition: width 0.3s; }
    </style>
    <script>
        function updateDashboard() {
            fetch('/api/summary')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cpu-value').textContent = data.system.cpu_percent.toFixed(1) + '%';
                    document.getElementById('cpu-bar').style.width = data.system.cpu_percent + '%';
                    
                    document.getElementById('memory-value').textContent = data.system.memory_percent.toFixed(1) + '%';
                    document.getElementById('memory-bar').style.width = data.system.memory_percent + '%';
                    
                    document.getElementById('disk-value').textContent = data.system.disk_usage_percent.toFixed(1) + '%';
                    document.getElementById('disk-bar').style.width = data.system.disk_usage_percent + '%';
                    
                    // Update server status
                    Object.keys(data.servers).forEach(serverName => {
                        const server = data.servers[serverName];
                        const statusElement = document.getElementById(serverName + '-status');
                        if (statusElement) {
                            statusElement.textContent = server.status;
                            statusElement.className = 'status-' + server.status;
                        }
                    });
                    
                    document.getElementById('alert-count').textContent = data.alerts.count;
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                })
                .catch(error => console.error('Error:', error));
        }
        
        setInterval(updateDashboard, 5000);
        window.onload = updateDashboard;
    </script>
</head>
<body>
    <div class="header">
        <h1>🎮 FFXI Server Performance Monitor</h1>
        <p>Real-time monitoring dashboard for LandSandBoat FFXI Server</p>
        <p>Last Update: <span id="last-update">Loading...</span></p>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3>System Performance</h3>
            <div class="metric">
                <span>CPU Usage</span>
                <span class="metric-value" id="cpu-value">0%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="cpu-bar" style="width: 0%"></div>
            </div>
            
            <div class="metric">
                <span>Memory Usage</span>
                <span class="metric-value" id="memory-value">0%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="memory-bar" style="width: 0%"></div>
            </div>
            
            <div class="metric">
                <span>Disk Usage</span>
                <span class="metric-value" id="disk-value">0%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="disk-bar" style="width: 0%"></div>
            </div>
        </div>
        
        <div class="card">
            <h3>Server Status</h3>
            <div class="metric">
                <span>Login Server (xi_connect)</span>
                <span id="xi_connect-status" class="status-stopped">stopped</span>
            </div>
            <div class="metric">
                <span>Search Server (xi_search)</span>
                <span id="xi_search-status" class="status-stopped">stopped</span>
            </div>
            <div class="metric">
                <span>Map Server (xi_map)</span>
                <span id="xi_map-status" class="status-stopped">stopped</span>
            </div>
            <div class="metric">
                <span>World Server (xi_world)</span>
                <span id="xi_world-status" class="status-stopped">stopped</span>
            </div>
        </div>
        
        <div class="card">
            <h3>Alerts</h3>
            <div class="metric">
                <span>Active Alerts</span>
                <span class="metric-value" id="alert-count">0</span>
            </div>
            <div id="alert-list">
                <!-- Alerts will be populated here -->
            </div>
        </div>
        
        <div class="card">
            <h3>Quick Actions</h3>
            <button onclick="location.reload()">🔄 Refresh Dashboard</button><br><br>
            <button onclick="window.open('/api/summary', '_blank')">📊 View Raw Data</button><br><br>
            <button onclick="window.open('/api/alerts', '_blank')">🚨 View All Alerts</button>
        </div>
    </div>
</body>
</html>
        '''

def main():
    parser = argparse.ArgumentParser(description="Advanced Performance Monitor for FFXI Server")
    parser.add_argument("--config", default="performance_monitor_config.json", 
                       help="Configuration file path")
    parser.add_argument("--web-only", action="store_true", 
                       help="Start only web interface")
    parser.add_argument("--monitor-only", action="store_true", 
                       help="Start only monitoring (no web interface)")
    parser.add_argument("--port", type=int, default=8080, 
                       help="Web interface port")
    parser.add_argument("--interval", type=int, default=5, 
                       help="Monitoring interval in seconds")
    
    args = parser.parse_args()
    
    monitor = AdvancedPerformanceMonitor(args.config)
    monitor.web_port = args.port
    monitor.config['monitor_interval'] = args.interval
    
    def signal_handler(signum, frame):
        print("\nShutting down...")
        monitor.stop_monitoring()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if args.web_only:
        monitor.start_web_interface()
    elif args.monitor_only:
        monitor.start_monitoring()
    else:
        # Start both monitoring and web interface
        monitoring_thread = threading.Thread(target=monitor.start_monitoring)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        try:
            monitor.start_web_interface()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()