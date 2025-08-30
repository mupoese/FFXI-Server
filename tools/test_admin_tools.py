#!/usr/bin/env python3
"""
Test Suite for LandSandBoat Administrative Tools
Validates functionality of admin dashboard, web panel, and analytics
"""

import os
import sys
import time
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import admin_dashboard
    import player_analytics
    import web_admin
    from rich.console import Console
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

class TestAdminDashboard(unittest.TestCase):
    """Test cases for admin dashboard functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            "database": {
                "host": "localhost",
                "port": 3306,
                "database": "test_xidb",
                "user": "test_user",
                "password": "test_pass"
            },
            "monitoring": {
                "refresh_interval": 1,
                "history_retention_hours": 1,
                "alert_thresholds": {
                    "cpu_percent": 80,
                    "memory_percent": 85,
                    "disk_percent": 90
                }
            }
        }
    
    def test_dashboard_initialization(self):
        """Test dashboard initialization"""
        dashboard = admin_dashboard.AdminDashboard()
        self.assertIsNotNone(dashboard.config)
        self.assertIn("database", dashboard.config)
        self.assertIn("monitoring", dashboard.config)
    
    @patch('admin_dashboard.psutil.cpu_percent')
    @patch('admin_dashboard.psutil.virtual_memory')
    @patch('admin_dashboard.psutil.disk_usage')
    @patch('admin_dashboard.psutil.net_io_counters')
    def test_system_metrics_collection(self, mock_net, mock_disk, mock_memory, mock_cpu):
        """Test system metrics collection"""
        # Mock system metrics
        mock_cpu.return_value = 45.2
        mock_memory.return_value = MagicMock(percent=67.8, available=2048*1024*1024, used=1024*1024*1024)
        mock_disk.return_value = MagicMock(percent=23.4, free=100*1024*1024*1024)
        mock_net.return_value = MagicMock(bytes_sent=1000000, bytes_recv=2000000)
        
        dashboard = admin_dashboard.AdminDashboard()
        metrics = dashboard._get_system_metrics()
        
        self.assertIn("system", metrics)
        self.assertEqual(metrics["system"]["cpu_percent"], 45.2)
        self.assertEqual(metrics["system"]["memory_percent"], 67.8)
        self.assertEqual(metrics["system"]["disk_percent"], 23.4)
    
    @patch('admin_dashboard.psutil.process_iter')
    def test_server_process_detection(self, mock_process_iter):
        """Test server process detection"""
        # Mock processes
        mock_processes = [
            MagicMock(info={'pid': 1234, 'name': 'xi_map', 'cpu_percent': 15.5, 'memory_info': MagicMock(rss=100*1024*1024)}),
            MagicMock(info={'pid': 1235, 'name': 'xi_login', 'cpu_percent': 5.2, 'memory_info': MagicMock(rss=50*1024*1024)}),
        ]
        mock_process_iter.return_value = mock_processes
        
        dashboard = admin_dashboard.AdminDashboard()
        servers = dashboard._get_server_processes()
        
        self.assertIn("xi_map", servers)
        self.assertIn("xi_login", servers)
        self.assertEqual(servers["xi_map"]["status"], "running")
        self.assertEqual(servers["xi_map"]["pid"], 1234)

class TestPlayerAnalytics(unittest.TestCase):
    """Test cases for player analytics functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db = Path(self.temp_dir) / "test_analytics.db"
    
    def test_analytics_initialization(self):
        """Test analytics system initialization"""
        analytics = player_analytics.PlayerAnalytics()
        self.assertIsNotNone(analytics.config)
        self.assertTrue(analytics.analytics_db.parent.exists())
    
    def test_analytics_database_creation(self):
        """Test analytics database schema creation"""
        analytics = player_analytics.PlayerAnalytics()
        
        # Check if database file is created
        self.assertTrue(analytics.analytics_db.exists())
        
        # Check if tables are created
        conn = sqlite3.connect(str(analytics.analytics_db))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'player_sessions',
            'zone_analytics', 
            'retention_metrics',
            'economic_metrics',
            'performance_analytics'
        ]
        
        for table in expected_tables:
            self.assertIn(table, tables)
        
        conn.close()
    
    def test_retention_analysis(self):
        """Test player retention analysis"""
        analytics = player_analytics.PlayerAnalytics()
        
        # Insert test data
        conn = sqlite3.connect(str(analytics.analytics_db))
        cursor = conn.cursor()
        
        # Insert sample session data
        test_sessions = [
            (1, "TestPlayer1", "2024-08-29 10:00:00", "2024-08-29 12:00:00", 120),
            (2, "TestPlayer2", "2024-08-29 14:00:00", "2024-08-29 15:30:00", 90),
            (1, "TestPlayer1", "2024-08-30 10:00:00", "2024-08-30 11:00:00", 60),
        ]
        
        for session in test_sessions:
            cursor.execute("""
                INSERT INTO player_sessions 
                (player_id, character_name, login_time, logout_time, session_duration_minutes)
                VALUES (?, ?, ?, ?, ?)
            """, session)
        
        conn.commit()
        conn.close()
        
        # Test retention analysis
        retention_data = analytics.analyze_player_retention()
        self.assertIn("total_players_30d", retention_data)

class TestWebAdminPanel(unittest.TestCase):
    """Test cases for web admin panel"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_config = {
            "database": {
                "host": "localhost",
                "port": 3306,
                "database": "test_xidb",
                "user": "test_user",
                "password": "test_pass"
            },
            "web": {
                "host": "localhost",
                "port": 8080,
                "debug": True
            }
        }
    
    def test_web_panel_initialization(self):
        """Test web panel initialization"""
        panel = web_admin.WebAdminPanel()
        self.assertIsNotNone(panel.config)
        self.assertIn("database", panel.config)
        self.assertIn("web", panel.config)
    
    @patch('web_admin.psutil.process_iter')
    def test_server_process_detection(self, mock_process_iter):
        """Test server process detection in web panel"""
        # Mock processes
        mock_processes = [
            MagicMock(info={'pid': 1234, 'name': 'xi_map'}),
            MagicMock(info={'pid': 1235, 'name': 'xi_login'}),
        ]
        mock_process_iter.return_value = mock_processes
        
        panel = web_admin.WebAdminPanel()
        servers = panel._get_server_processes()
        
        self.assertIn("xi_map", servers)
        self.assertIn("xi_login", servers)
        self.assertEqual(servers["xi_map"]["status"], "running")
    
    def test_alert_generation(self):
        """Test alert generation logic"""
        panel = web_admin.WebAdminPanel()
        
        # Test high CPU alert
        alerts = panel._generate_alerts(85.0, 70.0, 50.0)
        self.assertTrue(any(alert["message"].startswith("High CPU") for alert in alerts))
        
        # Test high memory alert
        alerts = panel._generate_alerts(70.0, 90.0, 50.0)
        self.assertTrue(any(alert["message"].startswith("High memory") for alert in alerts))
        
        # Test low disk space alert
        alerts = panel._generate_alerts(70.0, 70.0, 95.0)
        self.assertTrue(any(alert["message"].startswith("Low disk") for alert in alerts))

class TestIntegration(unittest.TestCase):
    """Integration tests for administrative tools"""
    
    def test_dashboard_analytics_integration(self):
        """Test integration between dashboard and analytics"""
        dashboard = admin_dashboard.AdminDashboard()
        analytics = player_analytics.PlayerAnalytics()
        
        # Both should be able to access their databases
        self.assertTrue(dashboard.analytics_db.parent.exists())
        self.assertTrue(analytics.analytics_db.exists())
    
    def test_configuration_consistency(self):
        """Test configuration consistency across tools"""
        dashboard = admin_dashboard.AdminDashboard()
        analytics = player_analytics.PlayerAnalytics()
        web_panel = web_admin.WebAdminPanel()
        
        # All should have database configuration
        self.assertIn("database", dashboard.config)
        self.assertIn("database", analytics.config)
        self.assertIn("database", web_panel.config)
        
        # Database configs should have required fields
        for tool_config in [dashboard.config, analytics.config, web_panel.config]:
            db_config = tool_config["database"]
            self.assertIn("host", db_config)
            self.assertIn("port", db_config)
            self.assertIn("database", db_config)
            self.assertIn("user", db_config)

def run_functionality_tests():
    """Run basic functionality tests without mocking"""
    console = Console()
    console.print("[bold blue]🧪 Running Administrative Tools Functionality Tests[/bold blue]")
    
    try:
        # Test 1: Dashboard initialization
        console.print("1. Testing admin dashboard initialization...")
        dashboard = admin_dashboard.AdminDashboard()
        assert dashboard.config is not None
        console.print("[green]✅ Dashboard initialization: PASSED[/green]")
        
        # Test 2: Analytics initialization
        console.print("2. Testing analytics system initialization...")
        analytics = player_analytics.PlayerAnalytics()
        assert analytics.analytics_db.exists()
        console.print("[green]✅ Analytics initialization: PASSED[/green]")
        
        # Test 3: Web panel initialization
        console.print("3. Testing web panel initialization...")
        web_panel = web_admin.WebAdminPanel()
        assert web_panel.config is not None
        console.print("[green]✅ Web panel initialization: PASSED[/green]")
        
        # Test 4: Analytics database schema
        console.print("4. Testing analytics database schema...")
        conn = sqlite3.connect(str(analytics.analytics_db))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['player_sessions', 'zone_analytics', 'retention_metrics']
        for table in expected_tables:
            assert table in tables
        conn.close()
        console.print("[green]✅ Database schema: PASSED[/green]")
        
        # Test 5: Configuration loading
        console.print("5. Testing configuration loading...")
        test_config = {"database": {"host": "test"}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            config_file = f.name
        
        try:
            dashboard = admin_dashboard.AdminDashboard(config_file)
            assert dashboard.config["database"]["host"] == "test"
            console.print("[green]✅ Configuration loading: PASSED[/green]")
        finally:
            os.unlink(config_file)
        
        console.print("\n[bold green]🎉 All functionality tests passed![/bold green]")
        return True
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Functionality test failed: {e}[/bold red]")
        return False

def main():
    """Main test runner"""
    console = Console()
    console.print("[bold blue]🧪 LandSandBoat Administrative Tools Test Suite[/bold blue]")
    
    # Run functionality tests first
    if not run_functionality_tests():
        return 1
    
    # Run unit tests
    console.print("\n[bold blue]🔬 Running Unit Tests[/bold blue]")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestAdminDashboard))
    test_suite.addTest(unittest.makeSuite(TestPlayerAnalytics))
    test_suite.addTest(unittest.makeSuite(TestWebAdminPanel))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    if result.wasSuccessful():
        console.print("\n[bold green]🎉 All tests passed successfully![/bold green]")
        console.print(f"✅ Ran {result.testsRun} tests")
        return 0
    else:
        console.print(f"\n[bold red]❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)[/bold red]")
        console.print(f"📊 Ran {result.testsRun} tests")
        return 1

if __name__ == "__main__":
    exit(main())