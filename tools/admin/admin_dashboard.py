#!/usr/bin/env python3
"""
LandSandBoat Administrative Dashboard
Real-time server monitoring and management tool
"""

import argparse
import json
import time
import datetime
import sys
import socket
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import sqlite3

# Import dependencies
try:
    import psutil
    import mysql.connector
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.text import Text
    from rich import box
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Install with: pip install psutil mysql-connector-python rich")
    sys.exit(1)

class AdminDashboard:
    """Real-time administrative dashboard for LandSandBoat server"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.console = Console()
        self.config = self._load_config(config_file)
        self.db_pool = None
        self.running = False
        
        # Create admin database if it doesn't exist
        self._init_admin_database()
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "database": {
                "host": "localhost",
                "port": 3306,
                "database": "xidb",
                "user": "root",
                "password": ""
            },
            "servers": {
                "map_server": {"host": "localhost", "port": 54230},
                "login_server": {"host": "localhost", "port": 54001},
                "search_server": {"host": "localhost", "port": 54002}
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
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    self._deep_merge(default_config, user_config)
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load config file: {e}[/yellow]")
        
        return default_config
    
    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """Deep merge configuration dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _init_admin_database(self) -> None:
        """Initialize admin database for storing metrics"""
        db_path = Path("logs/admin_dashboard.db")
        db_path.parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create tables for admin data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS server_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                server_type TEXT NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                memory_mb INTEGER,
                network_bytes_sent INTEGER,
                network_bytes_recv INTEGER,
                active_connections INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                player_count INTEGER,
                peak_concurrent INTEGER,
                new_registrations INTEGER,
                total_playtime_hours REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                resolved_at DATETIME
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            # CPU and memory metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process info for FFXI servers
            server_processes = self._get_server_processes()
            
            return {
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_mb": memory.available // (1024 * 1024),
                    "memory_used_mb": memory.used // (1024 * 1024),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free // (1024 * 1024 * 1024),
                    "network_bytes_sent": network.bytes_sent,
                    "network_bytes_recv": network.bytes_recv
                },
                "servers": server_processes,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            self.console.print(f"[red]Error getting system metrics: {e}[/red]")
            return {}
    
    def _get_server_processes(self) -> Dict[str, Any]:
        """Find and analyze FFXI server processes"""
        servers = {}
        server_names = ["xi_map", "xi_login", "xi_search", "xi_connect"]
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                proc_name = proc.info['name'].lower()
                for server_name in server_names:
                    if server_name in proc_name:
                        servers[server_name] = {
                            "pid": proc.info['pid'],
                            "cpu_percent": proc.info['cpu_percent'] or 0,
                            "memory_mb": proc.info['memory_info'].rss // (1024 * 1024) if proc.info['memory_info'] else 0,
                            "status": "running"
                        }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Check for missing expected servers
        for server_name in server_names:
            if server_name not in servers:
                servers[server_name] = {
                    "pid": None,
                    "cpu_percent": 0,
                    "memory_mb": 0,
                    "status": "not_running"
                }
        
        return servers
    
    def _get_database_metrics(self) -> Dict[str, Any]:
        """Get database connection and performance metrics"""
        try:
            conn = mysql.connector.connect(**self.config["database"])
            cursor = conn.cursor(dictionary=True)
            
            # Get basic database info
            cursor.execute("SELECT COUNT(*) as total_chars FROM chars WHERE active = 1")
            char_count = cursor.fetchone()["total_chars"]
            
            cursor.execute("""
                SELECT COUNT(*) as online_players 
                FROM chars c 
                JOIN accounts a ON c.accid = a.id 
                WHERE a.status = 1
            """)
            online_count = cursor.fetchone()["online_players"]
            
            cursor.execute("SHOW STATUS LIKE 'Connections'")
            total_connections = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            active_connections = cursor.fetchone()["Value"]
            
            conn.close()
            
            return {
                "total_characters": char_count,
                "online_players": online_count,
                "total_connections": int(total_connections),
                "active_connections": int(active_connections)
            }
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not connect to database: {e}[/yellow]")
            return {
                "total_characters": 0,
                "online_players": 0,
                "total_connections": 0,
                "active_connections": 0
            }
    
    def _check_server_connectivity(self) -> Dict[str, bool]:
        """Check if server ports are responsive"""
        connectivity = {}
        
        for server_name, config in self.config["servers"].items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((config["host"], config["port"]))
                connectivity[server_name] = result == 0
                sock.close()
            except Exception:
                connectivity[server_name] = False
        
        return connectivity
    
    def _generate_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate alerts based on threshold violations"""
        alerts = []
        thresholds = self.config["monitoring"]["alert_thresholds"]
        
        if metrics.get("system", {}).get("cpu_percent", 0) > thresholds["cpu_percent"]:
            alerts.append({
                "type": "performance",
                "severity": "warning",
                "message": f"High CPU usage: {metrics['system']['cpu_percent']:.1f}%"
            })
        
        if metrics.get("system", {}).get("memory_percent", 0) > thresholds["memory_percent"]:
            alerts.append({
                "type": "performance",
                "severity": "warning",
                "message": f"High memory usage: {metrics['system']['memory_percent']:.1f}%"
            })
        
        if metrics.get("system", {}).get("disk_percent", 0) > thresholds["disk_percent"]:
            alerts.append({
                "type": "storage",
                "severity": "critical",
                "message": f"Low disk space: {metrics['system']['disk_percent']:.1f}% used"
            })
        
        # Check for offline servers
        for server_name, server_info in metrics.get("servers", {}).items():
            if server_info["status"] == "not_running":
                alerts.append({
                    "type": "server",
                    "severity": "critical",
                    "message": f"Server offline: {server_name}"
                })
        
        return alerts
    
    def _create_dashboard_layout(self, metrics: Dict[str, Any], db_metrics: Dict[str, Any], alerts: List[Dict[str, str]]) -> Layout:
        """Create the rich layout for the dashboard"""
        layout = Layout()
        
        # Split into header and body
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        
        # Header with title and timestamp
        header_text = Text("🎮 LandSandBoat Administrative Dashboard", style="bold blue")
        timestamp_text = Text(f"Last Update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
        layout["header"].update(Panel(f"{header_text}\n{timestamp_text}", box=box.ROUNDED))
        
        # Split body into columns
        layout["body"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        # Left column: metrics
        layout["left"].split_column(
            Layout(name="system"),
            Layout(name="servers"),
            Layout(name="database")
        )
        
        # System metrics table
        system_table = Table(title="System Metrics", box=box.ROUNDED)
        system_table.add_column("Metric", style="cyan")
        system_table.add_column("Value", style="green")
        system_table.add_column("Status", style="yellow")
        
        if metrics.get("system"):
            sys_metrics = metrics["system"]
            system_table.add_row("CPU Usage", f"{sys_metrics['cpu_percent']:.1f}%", 
                                self._get_status_indicator(sys_metrics['cpu_percent'], 80))
            system_table.add_row("Memory Usage", f"{sys_metrics['memory_percent']:.1f}%", 
                                self._get_status_indicator(sys_metrics['memory_percent'], 85))
            system_table.add_row("Disk Usage", f"{sys_metrics['disk_percent']:.1f}%", 
                                self._get_status_indicator(sys_metrics['disk_percent'], 90))
            system_table.add_row("Free Memory", f"{sys_metrics['memory_available_mb']:,} MB", "📊")
            system_table.add_row("Free Disk", f"{sys_metrics['disk_free_gb']:,} GB", "💾")
        
        layout["system"].update(Panel(system_table, title="System Performance"))
        
        # Server status table
        server_table = Table(title="Server Status", box=box.ROUNDED)
        server_table.add_column("Server", style="cyan")
        server_table.add_column("Status", style="green")
        server_table.add_column("CPU %", style="yellow")
        server_table.add_column("Memory MB", style="magenta")
        
        for server_name, server_info in metrics.get("servers", {}).items():
            status_icon = "✅" if server_info["status"] == "running" else "❌"
            server_table.add_row(
                server_name,
                f"{status_icon} {server_info['status']}",
                f"{server_info['cpu_percent']:.1f}",
                f"{server_info['memory_mb']:,}"
            )
        
        layout["servers"].update(Panel(server_table, title="Server Processes"))
        
        # Database metrics table
        db_table = Table(title="Database Metrics", box=box.ROUNDED)
        db_table.add_column("Metric", style="cyan")
        db_table.add_column("Value", style="green")
        
        db_table.add_row("Online Players", f"{db_metrics.get('online_players', 0):,}")
        db_table.add_row("Total Characters", f"{db_metrics.get('total_characters', 0):,}")
        db_table.add_row("DB Connections", f"{db_metrics.get('active_connections', 0)}")
        db_table.add_row("Total DB Queries", f"{db_metrics.get('total_connections', 0):,}")
        
        layout["database"].update(Panel(db_table, title="Database Status"))
        
        # Right column: alerts
        alert_text = ""
        if alerts:
            for alert in alerts[-10:]:  # Show last 10 alerts
                severity_icon = "🔴" if alert["severity"] == "critical" else "🟡"
                alert_text += f"{severity_icon} {alert['message']}\n"
        else:
            alert_text = "✅ No active alerts"
        
        layout["right"].update(Panel(alert_text, title="System Alerts", border_style="red" if alerts else "green"))
        
        return layout
    
    def _get_status_indicator(self, value: float, threshold: float) -> str:
        """Get status indicator based on threshold"""
        if value < threshold * 0.7:
            return "✅"
        elif value < threshold:
            return "⚠️"
        else:
            return "🔴"
    
    def run_monitoring(self) -> None:
        """Run the real-time monitoring dashboard"""
        self.running = True
        refresh_interval = self.config["monitoring"]["refresh_interval"]
        
        try:
            with Live(refresh_per_second=1/refresh_interval) as live:
                while self.running:
                    try:
                        # Gather metrics
                        metrics = self._get_system_metrics()
                        db_metrics = self._get_database_metrics()
                        alerts = self._generate_alerts(metrics)
                        
                        # Store metrics in admin database
                        self._store_metrics(metrics, db_metrics)
                        
                        # Create and update layout
                        layout = self._create_dashboard_layout(metrics, db_metrics, alerts)
                        live.update(layout)
                        
                        time.sleep(refresh_interval)
                        
                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        self.console.print(f"[red]Dashboard error: {e}[/red]")
                        time.sleep(5)
        
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard stopped by user[/yellow]")
        finally:
            self.running = False
    
    def _store_metrics(self, metrics: Dict[str, Any], db_metrics: Dict[str, Any]) -> None:
        """Store metrics in admin database for historical tracking"""
        try:
            db_path = Path("logs/admin_dashboard.db")
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Store system metrics
            if metrics.get("system"):
                sys_metrics = metrics["system"]
                cursor.execute("""
                    INSERT INTO server_metrics 
                    (server_type, cpu_percent, memory_percent, memory_mb, 
                     network_bytes_sent, network_bytes_recv, active_connections)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    "system", 
                    sys_metrics["cpu_percent"],
                    sys_metrics["memory_percent"],
                    sys_metrics["memory_used_mb"],
                    sys_metrics["network_bytes_sent"],
                    sys_metrics["network_bytes_recv"],
                    db_metrics.get("active_connections", 0)
                ))
            
            # Store player activity
            cursor.execute("""
                INSERT INTO player_activity (player_count, peak_concurrent, new_registrations)
                VALUES (?, ?, ?)
            """, (
                db_metrics.get("online_players", 0),
                db_metrics.get("online_players", 0),  # TODO: Track peak separately
                0  # TODO: Track new registrations
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            # Don't spam console with database errors
            pass
    
    def generate_report(self, hours: int = 24) -> None:
        """Generate a comprehensive system report"""
        self.console.print(f"[bold blue]📊 LandSandBoat System Report - Last {hours} hours[/bold blue]")
        
        try:
            db_path = Path("logs/admin_dashboard.db")
            if not db_path.exists():
                self.console.print("[yellow]No historical data available[/yellow]")
                return
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get system performance averages
            cursor.execute("""
                SELECT 
                    AVG(cpu_percent) as avg_cpu,
                    AVG(memory_percent) as avg_memory,
                    MAX(cpu_percent) as max_cpu,
                    MAX(memory_percent) as max_memory
                FROM server_metrics 
                WHERE timestamp >= datetime('now', '-{} hours')
                AND server_type = 'system'
            """.format(hours))
            
            perf_data = cursor.fetchone()
            if perf_data and perf_data[0] is not None:
                table = Table(title="Performance Summary")
                table.add_column("Metric", style="cyan")
                table.add_column("Average", style="green")
                table.add_column("Peak", style="red")
                
                table.add_row("CPU Usage", f"{perf_data[0]:.1f}%", f"{perf_data[2]:.1f}%")
                table.add_row("Memory Usage", f"{perf_data[1]:.1f}%", f"{perf_data[3]:.1f}%")
                
                self.console.print(table)
            
            # Get player activity summary
            cursor.execute("""
                SELECT 
                    AVG(player_count) as avg_players,
                    MAX(player_count) as peak_players,
                    COUNT(*) as data_points
                FROM player_activity 
                WHERE timestamp >= datetime('now', '-{} hours')
            """.format(hours))
            
            player_data = cursor.fetchone()
            if player_data and player_data[0] is not None:
                self.console.print(f"\n[bold green]👥 Player Activity:[/bold green]")
                self.console.print(f"Average Players: {player_data[0]:.1f}")
                self.console.print(f"Peak Players: {player_data[1]}")
                self.console.print(f"Data Points: {player_data[2]}")
            
            conn.close()
            
        except Exception as e:
            self.console.print(f"[red]Error generating report: {e}[/red]")

def main():
    parser = argparse.ArgumentParser(description="LandSandBoat Administrative Dashboard")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--report", type=int, metavar="HOURS", help="Generate report for last N hours")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode")
    
    args = parser.parse_args()
    
    dashboard = AdminDashboard(args.config)
    
    if args.report:
        dashboard.generate_report(args.report)
    else:
        dashboard.run_monitoring()

if __name__ == "__main__":
    main()