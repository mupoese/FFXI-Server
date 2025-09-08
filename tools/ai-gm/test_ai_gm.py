#!/usr/bin/env python3
"""
Test suite for AI-GM Service
Basic tests to validate AI-GM functionality
"""

import unittest
import sys
import os
import tempfile
import time
from unittest.mock import Mock, patch, MagicMock

# Add the AI-GM directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ai_gm_service import AIGMService, AIGMConfig, PlayerIncident, AIGMSeverity, AIGMAction

class TestAIGMService(unittest.TestCase):
    """Test cases for AI-GM Service"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary log directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test configuration
        self.config = AIGMConfig()
        self.config.db_host = "test_host"
        self.config.db_name = "test_db"
        self.config.auto_moderation_enabled = True
        self.config.jail_duration_minutes = 30
        
        # Mock database connection
        self.mock_db_pool = Mock()
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_creation(self):
        """Test AI-GM configuration creation"""
        config = AIGMConfig()
        
        self.assertEqual(config.db_host, "localhost")
        self.assertEqual(config.db_port, 3306)
        self.assertEqual(config.auto_moderation_enabled, True)
        self.assertEqual(config.jail_duration_minutes, 30)
        self.assertEqual(config.gm_name, "AI-GM")
        self.assertEqual(config.gm_level, 2)
    
    def test_player_incident_creation(self):
        """Test PlayerIncident creation"""
        incident = PlayerIncident(
            player_id=123,
            player_name="TestPlayer",
            incident_type="test_incident",
            severity=AIGMSeverity.WARNING,
            description="Test incident description"
        )
        
        self.assertEqual(incident.player_id, 123)
        self.assertEqual(incident.player_name, "TestPlayer")
        self.assertEqual(incident.incident_type, "test_incident")
        self.assertEqual(incident.severity, AIGMSeverity.WARNING)
        self.assertEqual(incident.description, "Test incident description")
        self.assertFalse(incident.auto_resolved)
        self.assertIsNone(incident.action_taken)
        self.assertFalse(incident.gm_escalated)
    
    def test_severity_levels(self):
        """Test AI-GM severity levels"""
        self.assertEqual(AIGMSeverity.INFO.value, "info")
        self.assertEqual(AIGMSeverity.WARNING.value, "warning")
        self.assertEqual(AIGMSeverity.MODERATE.value, "moderate")
        self.assertEqual(AIGMSeverity.SEVERE.value, "severe")
        self.assertEqual(AIGMSeverity.CRITICAL.value, "critical")
    
    def test_action_types(self):
        """Test AI-GM action types"""
        self.assertEqual(AIGMAction.WARN.value, "warn")
        self.assertEqual(AIGMAction.TEMP_JAIL.value, "temp_jail")
        self.assertEqual(AIGMAction.JAIL.value, "jail")
        self.assertEqual(AIGMAction.ESCALATE_GM2.value, "escalate_gm2")
        self.assertEqual(AIGMAction.ESCALATE_GM3.value, "escalate_gm3")
    
    @patch('mysql.connector.pooling.MySQLConnectionPool')
    def test_service_initialization(self, mock_pool):
        """Test AI-GM service initialization"""
        # Mock successful initialization
        mock_pool.return_value = self.mock_db_pool
        
        service = AIGMService(self.config)
        
        # Patch os.makedirs to avoid file system operations
        with patch('os.makedirs'):
            result = service.initialize()
        
        self.assertTrue(result)
        self.assertIsNotNone(service.logger)
        self.assertEqual(len(service.incident_history), 0)
        self.assertEqual(len(service.player_warnings), 0)
    
    def test_incident_reporting(self):
        """Test incident reporting functionality"""
        service = AIGMService(self.config)
        service.incident_history = []
        service.player_warnings = {}
        
        incident = PlayerIncident(
            player_id=123,
            player_name="TestPlayer",
            incident_type="test_incident",
            severity=AIGMSeverity.WARNING,
            description="Test incident"
        )
        
        # Mock the execute_action method to avoid database calls
        with patch.object(service, 'execute_action') as mock_execute:
            with patch.object(service, 'determine_action', return_value=AIGMAction.WARN):
                service.report_incident(incident)
        
        # Check that incident was recorded
        self.assertEqual(len(service.incident_history), 1)
        self.assertEqual(service.incident_history[0], incident)
        
        # Check that warning count was incremented
        self.assertEqual(service.player_warnings[123], 1)
    
    def test_action_determination(self):
        """Test action determination logic"""
        service = AIGMService(self.config)
        service.player_warnings = {}
        
        # Test INFO severity - should return WARN for stuck player
        incident_info = PlayerIncident(
            player_id=123,
            player_name="TestPlayer",
            incident_type="stuck_player",
            severity=AIGMSeverity.INFO,
            description="Player stuck"
        )
        action = service.determine_action(incident_info)
        self.assertEqual(action, AIGMAction.WARN)
        
        # Test WARNING severity - first warning should return WARN
        incident_warning = PlayerIncident(
            player_id=123,
            player_name="TestPlayer", 
            incident_type="suspicious_behavior",
            severity=AIGMSeverity.WARNING,
            description="Suspicious behavior detected"
        )
        action = service.determine_action(incident_warning)
        self.assertEqual(action, AIGMAction.WARN)
        
        # Test WARNING severity after escalation threshold - should jail
        service.player_warnings[123] = 3
        action = service.determine_action(incident_warning)
        self.assertEqual(action, AIGMAction.TEMP_JAIL)
        
        # Test SEVERE severity - should escalate to GM3
        incident_severe = PlayerIncident(
            player_id=123,
            player_name="TestPlayer",
            incident_type="exploitation",
            severity=AIGMSeverity.SEVERE,
            description="Exploitation attempt"
        )
        action = service.determine_action(incident_severe)
        self.assertEqual(action, AIGMAction.ESCALATE_GM3)
    
    def test_warning_escalation(self):
        """Test warning escalation system"""
        service = AIGMService(self.config)
        service.player_warnings = {}
        
        incident = PlayerIncident(
            player_id=123,
            player_name="TestPlayer",
            incident_type="minor_violation",
            severity=AIGMSeverity.WARNING,
            description="Minor rule violation"
        )
        
        # First warning
        action = service.determine_action(incident)
        self.assertEqual(action, AIGMAction.WARN)
        
        # Simulate multiple warnings
        service.player_warnings[123] = 1
        action = service.determine_action(incident)
        self.assertEqual(action, AIGMAction.WARN)
        
        service.player_warnings[123] = 2
        action = service.determine_action(incident)
        self.assertEqual(action, AIGMAction.WARN)
        
        # After threshold, should escalate to jail
        service.player_warnings[123] = 3
        action = service.determine_action(incident)
        self.assertEqual(action, AIGMAction.TEMP_JAIL)

class TestAIGMIntegration(unittest.TestCase):
    """Integration tests for AI-GM system"""
    
    def test_complete_incident_flow(self):
        """Test complete incident handling flow"""
        config = AIGMConfig()
        config.auto_moderation_enabled = True
        
        service = AIGMService(config)
        service.incident_history = []
        service.player_warnings = {}
        
        # Create a test incident
        incident = PlayerIncident(
            player_id=456,
            player_name="ProblemPlayer",
            incident_type="disruptive_behavior",
            severity=AIGMSeverity.MODERATE,
            description="Player causing disruption"
        )
        
        # Mock database operations
        with patch.object(service, 'execute_query', return_value=[]):
            with patch.object(service, 'send_warning') as mock_warn:
                with patch.object(service, 'jail_player') as mock_jail:
                    # Report the incident
                    service.report_incident(incident)
                    
                    # Check that appropriate action was taken
                    # MODERATE severity with no prior warnings should result in temp jail
                    self.assertEqual(len(service.incident_history), 1)
                    self.assertEqual(service.player_warnings[456], 1)
                    
                    # The incident should have been processed
                    processed_incident = service.incident_history[0]
                    self.assertIsNotNone(processed_incident.action_taken)

if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestAIGMService))
    suite.addTest(unittest.makeSuite(TestAIGMIntegration))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)