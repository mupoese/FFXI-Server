#!/usr/bin/env python3
"""
LandSandBoat Web Administration Panel
Basic web interface for server administration
"""

import json
import os
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

try:
    from flask import Flask, render_template_string, jsonify, request, Response
    import mysql.connector
    import psutil
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Install with: pip install flask mysql-connector-python psutil")
    exit(1)

app = Flask(__name__)

# HTML template for the admin panel
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LandSandBoat Admin Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #1a1a1a; color: #fff; }
        .header { background: #2d2d2d; padding: 1rem; border-bottom: 2px solid #4a90e2; }
        .header h1 { color: #4a90e2; display: inline-block; }
        .status-indicator { float: right; margin-top: 5px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-bottom: 2rem; }
        .card { background: #2d2d2d; padding: 1.5rem; border-radius: 8px; border: 1px solid #444; }
        .card h3 { color: #4a90e2; margin-bottom: 1rem; }
        .metric { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
        .metric-value { font-weight: bold; }
        .server-list { list-style: none; }
        .server-item { background: #1a1a1a; padding: 0.5rem; margin: 0.3rem 0; border-radius: 4px; display: flex; justify-content: space-between; }
        .server-status { padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
        .status-running { background: #27ae60; color: white; }
        .status-stopped { background: #e74c3c; color: white; }
        .alert { background: #e74c3c; color: white; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .warning { background: #f39c12; color: white; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .success { background: #27ae60; color: white; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .btn { background: #4a90e2; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; margin: 0.2rem; }
        .btn:hover { background: #357abd; }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
        .log-container { background: #1a1a1a; padding: 1rem; border-radius: 4px; height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.9rem; }
        .refresh-indicator { display: inline-block; margin-left: 10px; animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .chart-container { height: 200px; background: #1a1a1a; border-radius: 4px; padding: 1rem; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="header">
        <h1>🎮 LandSandBoat Administration Panel</h1>
        <div class="status-indicator">
            <span id="status-text">Loading...</span>
            <span id="refresh-indicator" class="refresh-indicator">⟳</span>
        </div>
    </div>

    <div class="container">
        <div id="alerts-container"></div>

        <div class="grid">
            <div class="card">
                <h3>System Metrics</h3>
                <div class="metric">
                    <span>CPU Usage:</span>
                    <span id="cpu-usage" class="metric-value">--</span>
                </div>
                <div class="metric">
                    <span>Memory Usage:</span>
                    <span id="memory-usage" class="metric-value">--</span>
                </div>
                <div class="metric">
                    <span>Disk Usage:</span>
                    <span id="disk-usage" class="metric-value">--</span>
                </div>
                <div class="metric">
                    <span>Network In:</span>
                    <span id="network-in" class="metric-value">--</span>
                </div>
                <div class="metric">
                    <span>Network Out:</span>
                    <span id="network-out" class="metric-value">--</span>
                </div>
            </div>

            <div class="card">
                <h3>Server Status</h3>
                <ul id="server-list" class="server-list">
                    <li>Loading server information...</li>
                </ul>
            </div>

            <div class="card">
                <h3>Database Info</h3>
                <div class="metric">
                    <span>Online Players:</span>
                    <span id="online-players" class="metric-value">--</span>
                </div>
                <div class="metric">
                    <span>Total Characters:</span>
                    <span id="total-characters" class="metric-value">--</span>
                </div>
                <div class="metric">
                    <span>Database Connections:</span>
                    <span id="db-connections" class="metric-value">--</span>
                </div>
            </div>

            <div class="card">
                <h3>Quick Actions</h3>
                <button class="btn" onclick="restartServer('map')">Restart Map Server</button>
                <button class="btn" onclick="restartServer('login')">Restart Login Server</button>
                <button class="btn btn-danger" onclick="shutdownAll()">Emergency Shutdown</button>
                <button class="btn" onclick="backupDatabase()">Backup Database</button>
                <button class="btn" onclick="refreshData()">Refresh Data</button>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>CPU Usage History</h3>
                <div class="chart-container">
                    <canvas id="cpu-chart"></canvas>
                </div>
            </div>

            <div class="card">
                <h3>Player Activity</h3>
                <div class="chart-container">
                    <canvas id="player-chart"></canvas>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>Recent Server Logs</h3>
            <div id="log-container" class="log-container">
                Loading logs...
            </div>
        </div>
    </div>

    <script>
        let cpuChart, playerChart;
        let systemData = [];
        let playerData = [];
        
        function initCharts() {
            const cpuCtx = document.getElementById('cpu-chart').getContext('2d');
            cpuChart = new Chart(cpuCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU %',
                        data: [],
                        borderColor: '#4a90e2',
                        backgroundColor: 'rgba(74, 144, 226, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#fff' } } },
                    scales: {
                        x: { ticks: { color: '#ccc' }, grid: { color: '#444' } },
                        y: { ticks: { color: '#ccc' }, grid: { color: '#444' }, min: 0, max: 100 }
                    }
                }
            });

            const playerCtx = document.getElementById('player-chart').getContext('2d');
            playerChart = new Chart(playerCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Online Players',
                        data: [],
                        borderColor: '#27ae60',
                        backgroundColor: 'rgba(39, 174, 96, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#fff' } } },
                    scales: {
                        x: { ticks: { color: '#ccc' }, grid: { color: '#444' } },
                        y: { ticks: { color: '#ccc' }, grid: { color: '#444' }, min: 0 }
                    }
                }
            });
        }

        async function refreshData() {
            try {
                document.getElementById('refresh-indicator').style.display = 'inline-block';
                
                const response = await fetch('/api/status');
                const data = await response.json();
                
                updateSystemMetrics(data.system);
                updateServerStatus(data.servers);
                updateDatabaseInfo(data.database);
                updateCharts(data);
                updateAlerts(data.alerts);
                
                document.getElementById('status-text').textContent = 'Connected';
            } catch (error) {
                console.error('Error fetching data:', error);
                document.getElementById('status-text').textContent = 'Connection Error';
            } finally {
                document.getElementById('refresh-indicator').style.display = 'none';
            }
        }

        function updateSystemMetrics(system) {
            document.getElementById('cpu-usage').textContent = system.cpu_percent + '%';
            document.getElementById('memory-usage').textContent = system.memory_percent + '%';
            document.getElementById('disk-usage').textContent = system.disk_percent + '%';
            document.getElementById('network-in').textContent = formatBytes(system.network_bytes_recv);
            document.getElementById('network-out').textContent = formatBytes(system.network_bytes_sent);
        }

        function updateServerStatus(servers) {
            const serverList = document.getElementById('server-list');
            serverList.innerHTML = '';
            
            for (const [name, info] of Object.entries(servers)) {
                const li = document.createElement('li');
                li.className = 'server-item';
                li.innerHTML = `
                    <span>${name}</span>
                    <span class="server-status ${info.status === 'running' ? 'status-running' : 'status-stopped'}">
                        ${info.status === 'running' ? '✅ Running' : '❌ Stopped'}
                    </span>
                `;
                serverList.appendChild(li);
            }
        }

        function updateDatabaseInfo(database) {
            document.getElementById('online-players').textContent = database.online_players;
            document.getElementById('total-characters').textContent = database.total_characters;
            document.getElementById('db-connections').textContent = database.active_connections;
        }

        function updateCharts(data) {
            const now = new Date().toLocaleTimeString();
            
            // Update CPU chart
            if (cpuChart.data.labels.length > 20) {
                cpuChart.data.labels.shift();
                cpuChart.data.datasets[0].data.shift();
            }
            cpuChart.data.labels.push(now);
            cpuChart.data.datasets[0].data.push(data.system.cpu_percent);
            cpuChart.update('none');
            
            // Update player chart
            if (playerChart.data.labels.length > 20) {
                playerChart.data.labels.shift();
                playerChart.data.datasets[0].data.shift();
            }
            playerChart.data.labels.push(now);
            playerChart.data.datasets[0].data.push(data.database.online_players);
            playerChart.update('none');
        }

        function updateAlerts(alerts) {
            const container = document.getElementById('alerts-container');
            container.innerHTML = '';
            
            alerts.forEach(alert => {
                const alertDiv = document.createElement('div');
                alertDiv.className = alert.severity === 'critical' ? 'alert' : 'warning';
                alertDiv.textContent = alert.message;
                container.appendChild(alertDiv);
            });
        }

        function formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        async function restartServer(serverType) {
            if (confirm(`Are you sure you want to restart the ${serverType} server?`)) {
                try {
                    const response = await fetch('/api/restart', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ server: serverType })
                    });
                    const result = await response.json();
                    alert(result.message);
                } catch (error) {
                    alert('Error restarting server: ' + error.message);
                }
            }
        }

        async function shutdownAll() {
            if (confirm('Are you sure you want to shutdown ALL servers? This will disconnect all players!')) {
                try {
                    const response = await fetch('/api/shutdown', { method: 'POST' });
                    const result = await response.json();
                    alert(result.message);
                } catch (error) {
                    alert('Error shutting down servers: ' + error.message);
                }
            }
        }

        async function backupDatabase() {
            if (confirm('Start database backup? This may take a few minutes.')) {
                try {
                    const response = await fetch('/api/backup', { method: 'POST' });
                    const result = await response.json();
                    alert(result.message);
                } catch (error) {
                    alert('Error starting backup: ' + error.message);
                }
            }
        }

        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            refreshData();
            setInterval(refreshData, 5000); // Refresh every 5 seconds
        });
    </script>
</body>
</html>
"""

class WebAdminPanel:
    """Web-based administration panel for LandSandBoat"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.setup_routes()
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration for web admin panel"""
        default_config = {
            "database": {
                "host": "localhost",
                "port": 3306,
                "database": "xidb",
                "user": "root",
                "password": ""
            },
            "web": {
                "host": "0.0.0.0",
                "port": 8080,
                "debug": False
            }
        }
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Simple merge for this basic implementation
                    for key, value in user_config.items():
                        if key in default_config:
                            default_config[key].update(value)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        return default_config
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @app.route('/')
        def dashboard():
            return render_template_string(HTML_TEMPLATE)
        
        @app.route('/api/status')
        def api_status():
            """Get current system status as JSON"""
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # Server processes
                servers = self._get_server_processes()
                
                # Database info
                db_info = self._get_database_info()
                
                # Generate alerts
                alerts = self._generate_alerts(cpu_percent, memory.percent, disk.percent)
                
                return jsonify({
                    "system": {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "disk_percent": disk.percent,
                        "network_bytes_sent": network.bytes_sent,
                        "network_bytes_recv": network.bytes_recv
                    },
                    "servers": servers,
                    "database": db_info,
                    "alerts": alerts,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/restart', methods=['POST'])
        def api_restart():
            """Restart a specific server"""
            try:
                data = request.get_json()
                server_type = data.get('server')
                
                # This is a placeholder - in real implementation, you'd
                # use systemctl, supervisorctl, or similar
                message = f"Restart command sent for {server_type} server"
                
                return jsonify({"success": True, "message": message})
                
            except Exception as e:
                return jsonify({"success": False, "message": str(e)}), 500
        
        @app.route('/api/shutdown', methods=['POST'])
        def api_shutdown():
            """Emergency shutdown of all servers"""
            try:
                # Placeholder for shutdown logic
                message = "Emergency shutdown initiated"
                return jsonify({"success": True, "message": message})
                
            except Exception as e:
                return jsonify({"success": False, "message": str(e)}), 500
        
        @app.route('/api/backup', methods=['POST'])
        def api_backup():
            """Start database backup"""
            try:
                # Placeholder for backup logic
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                message = f"Database backup started: backup_{timestamp}.sql"
                return jsonify({"success": True, "message": message})
                
            except Exception as e:
                return jsonify({"success": False, "message": str(e)}), 500
    
    def _get_server_processes(self) -> Dict[str, Any]:
        """Get information about server processes"""
        servers = {}
        server_names = ["xi_map", "xi_login", "xi_search", "xi_connect"]
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                for server_name in server_names:
                    if server_name in proc_name:
                        servers[server_name] = {"status": "running", "pid": proc.info['pid']}
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Mark missing servers as stopped
        for server_name in server_names:
            if server_name not in servers:
                servers[server_name] = {"status": "stopped", "pid": None}
        
        return servers
    
    def _get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        try:
            conn = mysql.connector.connect(**self.config["database"])
            cursor = conn.cursor(dictionary=True)
            
            # Get player counts
            cursor.execute("SELECT COUNT(*) as total_chars FROM chars WHERE active = 1")
            char_count = cursor.fetchone()["total_chars"]
            
            cursor.execute("""
                SELECT COUNT(*) as online_players 
                FROM chars c 
                JOIN accounts a ON c.accid = a.id 
                WHERE a.status = 1
            """)
            online_count = cursor.fetchone()["online_players"]
            
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            active_connections = cursor.fetchone()["Value"]
            
            conn.close()
            
            return {
                "total_characters": char_count,
                "online_players": online_count,
                "active_connections": int(active_connections)
            }
            
        except Exception as e:
            return {
                "total_characters": 0,
                "online_players": 0,
                "active_connections": 0,
                "error": str(e)
            }
    
    def _generate_alerts(self, cpu: float, memory: float, disk: float) -> List[Dict[str, str]]:
        """Generate system alerts"""
        alerts = []
        
        if cpu > 80:
            alerts.append({
                "severity": "warning",
                "message": f"High CPU usage: {cpu:.1f}%"
            })
        
        if memory > 85:
            alerts.append({
                "severity": "critical",
                "message": f"High memory usage: {memory:.1f}%"
            })
        
        if disk > 90:
            alerts.append({
                "severity": "critical",
                "message": f"Low disk space: {disk:.1f}% used"
            })
        
        return alerts
    
    def run(self):
        """Start the web admin panel"""
        host = self.config["web"]["host"]
        port = self.config["web"]["port"]
        debug = self.config["web"]["debug"]
        
        print(f"🌐 Starting LandSandBoat Web Admin Panel")
        print(f"📍 Access at: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
        print(f"🔧 Debug mode: {'enabled' if debug else 'disabled'}")
        
        app.run(host=host, port=port, debug=debug)

def main():
    parser = argparse.ArgumentParser(description="LandSandBoat Web Administration Panel")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    panel = WebAdminPanel(args.config)
    
    # Override config with command line arguments
    if args.host:
        panel.config["web"]["host"] = args.host
    if args.port:
        panel.config["web"]["port"] = args.port
    if args.debug:
        panel.config["web"]["debug"] = args.debug
    
    panel.run()

if __name__ == "__main__":
    main()