#!/usr/bin/env python3
"""
LandSandBoat Player Behavior Analytics
Advanced analytics for player behavior and server optimization
"""

import argparse
import json
import sqlite3
import datetime
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import statistics

try:
    import mysql.connector
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import track
except ImportError as e:
    print(f"Missing dependencies for full analytics: {e}")
    print("Install with: pip install mysql-connector-python")
    # Create mock console for basic functionality
    class Console:
        def print(self, *args, **kwargs):
            print(*args)

class PlayerAnalytics:
    """Advanced player behavior analytics system"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.console = Console()
        self.config = self._load_config(config_file)
        self.analytics_db = Path("logs/player_analytics.db")
        self.analytics_db.parent.mkdir(exist_ok=True)
        self._init_analytics_database()
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load database configuration"""
        default_config = {
            "database": {
                "host": "localhost",
                "port": 3306,
                "database": "xidb",
                "user": "root",
                "password": ""
            },
            "analytics": {
                "retention_days": 30,
                "session_timeout_minutes": 30,
                "peak_hours_threshold": 0.7
            }
        }
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    for key, value in user_config.items():
                        if key in default_config:
                            default_config[key].update(value)
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
        
        return default_config
    
    def _init_analytics_database(self) -> None:
        """Initialize analytics database"""
        conn = sqlite3.connect(str(self.analytics_db))
        cursor = conn.cursor()
        
        # Player session tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                character_name TEXT,
                login_time DATETIME,
                logout_time DATETIME,
                session_duration_minutes INTEGER,
                zone_changes INTEGER DEFAULT 0,
                battles_fought INTEGER DEFAULT 0,
                items_traded INTEGER DEFAULT 0,
                gil_earned INTEGER DEFAULT 0,
                exp_gained INTEGER DEFAULT 0
            )
        """)
        
        # Zone popularity tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS zone_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                zone_id INTEGER,
                zone_name TEXT,
                unique_visitors INTEGER,
                total_time_spent_minutes INTEGER,
                avg_session_duration REAL,
                peak_concurrent INTEGER
            )
        """)
        
        # Player retention metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS retention_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                new_players INTEGER,
                returning_players INTEGER,
                day_1_retention REAL,
                day_7_retention REAL,
                day_30_retention REAL
            )
        """)
        
        # Economic analytics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS economic_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                total_gil_circulation BIGINT,
                auction_house_volume INTEGER,
                bazaar_transactions INTEGER,
                avg_transaction_value INTEGER,
                inflation_rate REAL
            )
        """)
        
        # Performance metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                concurrent_players INTEGER,
                server_response_time_ms REAL,
                database_query_time_ms REAL,
                memory_usage_mb INTEGER,
                cpu_usage_percent REAL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def collect_player_session_data(self) -> None:
        """Collect and analyze player session data"""
        try:
            conn = mysql.connector.connect(**self.config["database"])
            cursor = conn.cursor(dictionary=True)
            
            # Get recent player sessions (simplified - would need actual session tracking)
            cursor.execute("""
                SELECT 
                    c.charid,
                    c.charname,
                    c.lastlogin,
                    c.logout,
                    c.playtime,
                    c.zone,
                    TIMESTAMPDIFF(MINUTE, c.lastlogin, c.logout) as session_minutes
                FROM chars c
                WHERE c.lastlogin >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                AND c.logout IS NOT NULL
                ORDER BY c.lastlogin DESC
            """)
            
            sessions = cursor.fetchall()
            
            # Store in analytics database
            analytics_conn = sqlite3.connect(str(self.analytics_db))
            analytics_cursor = analytics_conn.cursor()
            
            for session in track(sessions, description="Processing sessions..."):
                if session['session_minutes'] and session['session_minutes'] > 0:
                    analytics_cursor.execute("""
                        INSERT INTO player_sessions 
                        (player_id, character_name, login_time, logout_time, session_duration_minutes)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        session['charid'],
                        session['charname'],
                        session['lastlogin'],
                        session['logout'],
                        session['session_minutes']
                    ))
            
            analytics_conn.commit()
            analytics_conn.close()
            conn.close()
            
            self.console.print(f"[green]✅ Processed {len(sessions)} player sessions[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Error collecting session data: {e}[/red]")
    
    def analyze_player_retention(self) -> Dict[str, Any]:
        """Analyze player retention metrics"""
        analytics_conn = sqlite3.connect(str(self.analytics_db))
        cursor = analytics_conn.cursor()
        
        # Calculate retention rates
        cursor.execute("""
            SELECT 
                DATE(login_time) as date,
                COUNT(DISTINCT player_id) as daily_active_users,
                AVG(session_duration_minutes) as avg_session_duration
            FROM player_sessions
            WHERE login_time >= DATE('now', '-30 days')
            GROUP BY DATE(login_time)
            ORDER BY date
        """)
        
        daily_metrics = cursor.fetchall()
        
        # Calculate weekly retention (simplified)
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT player_id) as total_players,
                COUNT(DISTINCT CASE WHEN login_time >= DATE('now', '-7 days') THEN player_id END) as week_active,
                COUNT(DISTINCT CASE WHEN login_time >= DATE('now', '-1 days') THEN player_id END) as day_active
            FROM player_sessions
            WHERE login_time >= DATE('now', '-30 days')
        """)
        
        retention_data = cursor.fetchone()
        
        analytics_conn.close()
        
        if retention_data and retention_data[0] > 0:
            return {
                "total_players_30d": retention_data[0],
                "weekly_retention_rate": (retention_data[1] / retention_data[0]) * 100,
                "daily_retention_rate": (retention_data[2] / retention_data[0]) * 100,
                "daily_metrics": daily_metrics
            }
        
        return {"error": "Insufficient data for retention analysis"}
    
    def analyze_zone_popularity(self) -> List[Dict[str, Any]]:
        """Analyze zone popularity and usage patterns"""
        try:
            conn = mysql.connector.connect(**self.config["database"])
            cursor = conn.cursor(dictionary=True)
            
            # Get zone popularity data
            cursor.execute("""
                SELECT 
                    z.zoneid,
                    z.name,
                    COUNT(DISTINCT c.charid) as unique_visitors,
                    COUNT(*) as total_visits,
                    AVG(c.playtime) as avg_playtime
                FROM chars c
                JOIN zone_settings z ON c.zone = z.zoneid
                WHERE c.lastlogin >= DATE_SUB(NOW(), INTERVAL 7 DAYS)
                GROUP BY z.zoneid, z.name
                HAVING unique_visitors > 0
                ORDER BY unique_visitors DESC
                LIMIT 20
            """)
            
            zone_data = cursor.fetchall()
            conn.close()
            
            return zone_data
            
        except Exception as e:
            self.console.print(f"[red]❌ Error analyzing zones: {e}[/red]")
            return []
    
    def analyze_peak_hours(self) -> Dict[str, Any]:
        """Analyze server peak hours and load patterns"""
        analytics_conn = sqlite3.connect(str(self.analytics_db))
        cursor = analytics_conn.cursor()
        
        # Get hourly player distribution
        cursor.execute("""
            SELECT 
                strftime('%H', login_time) as hour,
                COUNT(*) as sessions,
                COUNT(DISTINCT player_id) as unique_players,
                AVG(session_duration_minutes) as avg_duration
            FROM player_sessions
            WHERE login_time >= DATE('now', '-7 days')
            GROUP BY strftime('%H', login_time)
            ORDER BY hour
        """)
        
        hourly_data = cursor.fetchall()
        analytics_conn.close()
        
        if not hourly_data:
            return {"error": "No session data available"}
        
        # Calculate peak hours
        max_sessions = max(row[1] for row in hourly_data)
        peak_threshold = max_sessions * self.config["analytics"]["peak_hours_threshold"]
        peak_hours = [int(row[0]) for row in hourly_data if row[1] >= peak_threshold]
        
        return {
            "hourly_distribution": hourly_data,
            "peak_hours": peak_hours,
            "max_concurrent": max_sessions,
            "peak_threshold": peak_threshold
        }
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance and analytics report"""
        self.console.print("[bold blue]📊 Generating Performance Analytics Report...[/bold blue]")
        
        # Collect fresh session data
        self.collect_player_session_data()
        
        # Analyze various metrics
        retention_metrics = self.analyze_player_retention()
        zone_popularity = self.analyze_zone_popularity()
        peak_hours = self.analyze_peak_hours()
        
        # Create comprehensive report
        report = {
            "generated_at": datetime.datetime.now().isoformat(),
            "retention_analysis": retention_metrics,
            "zone_popularity": zone_popularity,
            "peak_hours_analysis": peak_hours
        }
        
        # Display report
        self._display_analytics_report(report)
        
        # Save report to file
        report_file = Path(f"logs/analytics_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.console.print(f"[green]📄 Report saved to: {report_file}[/green]")
        
        return report
    
    def _display_analytics_report(self, report: Dict[str, Any]) -> None:
        """Display analytics report in a nice format"""
        
        # Retention metrics table
        if "retention_analysis" in report and "error" not in report["retention_analysis"]:
            retention_table = Table(title="Player Retention Analysis")
            retention_table.add_column("Metric", style="cyan")
            retention_table.add_column("Value", style="green")
            
            retention = report["retention_analysis"]
            retention_table.add_row("Total Players (30d)", f"{retention['total_players_30d']:,}")
            retention_table.add_row("Weekly Retention", f"{retention['weekly_retention_rate']:.1f}%")
            retention_table.add_row("Daily Retention", f"{retention['daily_retention_rate']:.1f}%")
            
            self.console.print(retention_table)
        
        # Zone popularity table
        if report["zone_popularity"]:
            zone_table = Table(title="Top 10 Popular Zones")
            zone_table.add_column("Zone", style="cyan")
            zone_table.add_column("Unique Visitors", style="green")
            zone_table.add_column("Total Visits", style="yellow")
            zone_table.add_column("Avg Playtime", style="magenta")
            
            for zone in report["zone_popularity"][:10]:
                zone_table.add_row(
                    zone["name"] or f"Zone {zone['zoneid']}",
                    f"{zone['unique_visitors']:,}",
                    f"{zone['total_visits']:,}",
                    f"{zone['avg_playtime']:.1f}h" if zone['avg_playtime'] else "N/A"
                )
            
            self.console.print(zone_table)
        
        # Peak hours analysis
        if "peak_hours_analysis" in report and "error" not in report["peak_hours_analysis"]:
            peak_data = report["peak_hours_analysis"]
            
            self.console.print(Panel(
                f"🕐 Peak Hours: {', '.join(f'{h:02d}:00' for h in peak_data['peak_hours'])}\n"
                f"📈 Max Concurrent: {peak_data['max_concurrent']} players\n"
                f"⚡ Peak Threshold: {peak_data['peak_threshold']:.0f} sessions",
                title="Server Peak Hours"
            ))
    
    def monitor_real_time_performance(self) -> None:
        """Monitor and store real-time performance metrics"""
        try:
            conn = mysql.connector.connect(**self.config["database"])
            cursor = conn.cursor(dictionary=True)
            
            # Get current player count
            cursor.execute("""
                SELECT COUNT(*) as concurrent_players
                FROM chars c
                JOIN accounts a ON c.accid = a.id
                WHERE a.status = 1
            """)
            
            player_count = cursor.fetchone()["concurrent_players"]
            
            # Store performance metrics
            analytics_conn = sqlite3.connect(str(self.analytics_db))
            analytics_cursor = analytics_conn.cursor()
            
            analytics_cursor.execute("""
                INSERT INTO performance_analytics 
                (concurrent_players, server_response_time_ms, database_query_time_ms)
                VALUES (?, ?, ?)
            """, (player_count, 0.0, 0.0))  # TODO: Measure actual response times
            
            analytics_conn.commit()
            analytics_conn.close()
            conn.close()
            
            self.console.print(f"[green]📊 Performance data recorded: {player_count} concurrent players[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Error monitoring performance: {e}[/red]")
    
    def create_visualizations(self, report: Dict[str, Any]) -> None:
        """Create data visualizations for the analytics report"""
        try:
            import matplotlib.pyplot as plt
            
            # Set dark theme
            plt.style.use('dark_background')
            
            # Create hourly activity chart
            if "peak_hours_analysis" in report and "hourly_distribution" in report["peak_hours_analysis"]:
                hourly_data = report["peak_hours_analysis"]["hourly_distribution"]
                
                hours = [int(row[0]) for row in hourly_data]
                sessions = [row[1] for row in hourly_data]
                
                plt.figure(figsize=(12, 6))
                plt.bar(hours, sessions, color='#4a90e2', alpha=0.8)
                plt.xlabel('Hour of Day')
                plt.ylabel('Number of Sessions')
                plt.title('Player Activity by Hour')
                plt.xticks(range(0, 24))
                plt.grid(True, alpha=0.3)
                
                chart_file = Path(f"logs/hourly_activity_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                plt.savefig(chart_file, dpi=150, bbox_inches='tight')
                plt.close()
                
                self.console.print(f"[green]📈 Chart saved to: {chart_file}[/green]")
                
        except ImportError:
            self.console.print("[yellow]⚠ Matplotlib not available for visualizations[/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ Error creating visualizations: {e}[/red]")

def main():
    parser = argparse.ArgumentParser(description="LandSandBoat Player Analytics System")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--report", action="store_true", help="Generate analytics report")
    parser.add_argument("--monitor", action="store_true", help="Monitor real-time performance")
    parser.add_argument("--collect", action="store_true", help="Collect session data")
    parser.add_argument("--visualize", action="store_true", help="Create data visualizations")
    
    args = parser.parse_args()
    
    analytics = PlayerAnalytics(args.config)
    
    if args.collect:
        analytics.collect_player_session_data()
    elif args.monitor:
        analytics.monitor_real_time_performance()
    elif args.report:
        report = analytics.generate_performance_report()
        if args.visualize:
            analytics.create_visualizations(report)
    else:
        # Default: generate report
        report = analytics.generate_performance_report()
        if args.visualize:
            analytics.create_visualizations(report)

if __name__ == "__main__":
    main()