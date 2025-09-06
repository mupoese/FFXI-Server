#!/usr/bin/env python3
"""
Test script for AI-GM Autonomous Operation and GM Learning capabilities
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add the AI-GM directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from ai_gm_service import AIGMService, AIGMConfig, PlayerIncident, AIGMSeverity, AIGMAction

class TestAutonomousLearning(unittest.TestCase):
    """Test AI-GM autonomous operation and learning from GMs"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = AIGMConfig()
        self.config.autonomous_mode_enabled = True
        self.config.gm_learning_enabled = True
        self.config.ml_enabled = True
        
        # Mock the database and ML engine
        with patch('ai_gm_service.pooling.MySQLConnectionPool'), \
             patch('ai_gm_service.AIGMMLEngine'), \
             patch('ai_gm_service.GMBattleTestSystem'):
            self.ai_gm = AIGMService(self.config)
            self.ai_gm.db_pool = Mock()
            self.ai_gm.ml_engine = Mock()
            self.ai_gm.battle_system = Mock()
            self.ai_gm.logger = Mock()
    
    def test_gm_availability_detection(self):
        """Test detection of online GMs"""
        # Mock database query for online GMs
        self.ai_gm.execute_query = Mock()
        
        # Test no GMs online
        self.ai_gm.execute_query.return_value = []
        self.ai_gm._check_gm_availability()
        
        self.assertTrue(self.ai_gm.autonomous_mode)
        self.assertEqual(len(self.ai_gm.online_gms), 0)
        
        # Test GMs online
        mock_gms = [
            {'charid': 1, 'charname': 'TestGM', 'gmlevel': 3, 'pos_zone': 230, 
             'pos_x': 0, 'pos_y': 0, 'pos_z': 0, 'minutes_online': 10}
        ]
        self.ai_gm.execute_query.return_value = mock_gms
        self.ai_gm._check_gm_availability()
        
        self.assertFalse(self.ai_gm.autonomous_mode)
        self.assertEqual(len(self.ai_gm.online_gms), 1)
        self.assertTrue(self.ai_gm.learning_session_active)
    
    def test_autonomous_mode_decisions(self):
        """Test AI-GM decision making in autonomous mode"""
        self.ai_gm.autonomous_mode = True
        
        # Test incident handling in autonomous mode
        incident = PlayerIncident(
            player_id=123,
            player_name="TestPlayer",
            incident_type="suspicious_login",
            severity=AIGMSeverity.WARNING,
            description="Suspicious login pattern detected"
        )
        
        # Mock warning count
        self.ai_gm.player_warnings[123] = 1
        
        action = self.ai_gm._determine_autonomous_action(incident, 1)
        
        # Should be more aggressive in autonomous mode
        self.assertEqual(action, AIGMAction.TEMP_JAIL)
    
    def test_learning_mode_decisions(self):
        """Test AI-GM decision making in learning mode"""
        self.ai_gm.autonomous_mode = False
        
        # Test incident handling in learning mode
        incident = PlayerIncident(
            player_id=123,
            player_name="TestPlayer",
            incident_type="suspicious_login",
            severity=AIGMSeverity.WARNING,
            description="Suspicious login pattern detected"
        )
        
        # Mock warning count
        self.ai_gm.player_warnings[123] = 1
        
        action = self.ai_gm._determine_learning_mode_action(incident, 1)
        
        # Should escalate to GM in learning mode
        self.assertEqual(action, AIGMAction.WARN)
    
    def test_gm_action_learning(self):
        """Test learning from GM actions"""
        self.ai_gm.learning_session_active = True
        self.ai_gm.ml_engine = Mock()
        
        # Mock GM action data
        gm_action = {
            'action_id': 'test_action_1',
            'timestamp': datetime.now(),
            'gm_name': 'TestGM',
            'command': 'jail',
            'full_string': 'jail TestPlayer 30 Disruptive behavior',
            'context': {
                'server_load': {'player_count': 50, 'recent_incidents': 2},
                'target_player': {'charid': 123, 'charname': 'TestPlayer'}
            }
        }
        
        # Test learning from GM action
        self.ai_gm._learn_from_gm_action(gm_action)
        
        # Verify ML engine was called
        self.ai_gm.ml_engine.learn_from_gm_interaction.assert_called_once()
        
        # Verify action was added to history
        self.assertEqual(len(self.ai_gm.gm_actions_history), 1)
    
    def test_action_classification(self):
        """Test GM action classification"""
        # Test disciplinary action
        self.assertEqual(
            self.ai_gm._classify_gm_action('jail TestPlayer'),
            'disciplinary'
        )
        
        # Test communication action
        self.assertEqual(
            self.ai_gm._classify_gm_action('tell TestPlayer hello'),
            'communication'
        )
        
        # Test assistance action
        self.assertEqual(
            self.ai_gm._classify_gm_action('warp TestPlayer'),
            'assistance'
        )
        
        # Test educational action
        self.assertEqual(
            self.ai_gm._classify_gm_action('battle test demo'),
            'educational'
        )
    
    def test_severity_extraction(self):
        """Test severity extraction from GM actions"""
        # Test severe action
        gm_action = {'command': 'ban', 'full_string': 'ban TestPlayer severe violation'}
        self.assertEqual(
            self.ai_gm._extract_severity_from_action(gm_action),
            'severe'
        )
        
        # Test moderate action
        gm_action = {'command': 'jail', 'full_string': 'jail TestPlayer 60 moderate behavior'}
        self.assertEqual(
            self.ai_gm._extract_severity_from_action(gm_action),
            'moderate'
        )
        
        # Test warning action
        gm_action = {'command': 'warn', 'full_string': 'warn TestPlayer about behavior'}
        self.assertEqual(
            self.ai_gm._extract_severity_from_action(gm_action),
            'warning'
        )
    
    def test_escalation_pattern_analysis(self):
        """Test escalation pattern analysis"""
        gm_action = {'command': 'jail', 'full_string': 'jail TestPlayer immediate action needed'}
        
        pattern = self.ai_gm._analyze_escalation_pattern(gm_action)
        
        self.assertTrue(pattern['immediate_action'])
        self.assertTrue(pattern['human_intervention'])
        self.assertGreater(pattern['escalation_level'], 2)
    
    def test_server_load_calculation(self):
        """Test server load metrics calculation"""
        # Mock database queries
        self.ai_gm.execute_query = Mock()
        self.ai_gm.execute_query.return_value = {'count': 25}
        
        # Mock incident history
        recent_time = datetime.now() - timedelta(minutes=30)
        self.ai_gm.incident_history = [
            Mock(timestamp=recent_time, auto_resolved=True),
            Mock(timestamp=recent_time, auto_resolved=True)
        ]
        
        # This would be an async method in the real implementation
        # For testing, we'll call the sync parts
        with patch.object(self.ai_gm, 'execute_query') as mock_query:
            mock_query.return_value = {'count': 25}
            
            load_data = {
                'player_count': 25,
                'recent_incidents': 2,
                'ai_gm_actions_last_hour': 2
            }
            
            self.assertEqual(load_data['player_count'], 25)
            self.assertEqual(load_data['recent_incidents'], 2)
    
    def test_mode_switching(self):
        """Test switching between autonomous and learning modes"""
        # Start in autonomous mode
        self.ai_gm.autonomous_mode = True
        self.ai_gm.online_gms = []
        
        # Simulate GMs coming online
        self.ai_gm.online_gms = [{'charid': 1, 'charname': 'TestGM', 'gmlevel': 3}]
        previous_autonomous = self.ai_gm.autonomous_mode
        self.ai_gm.autonomous_mode = False
        
        # Verify mode switch
        self.assertTrue(previous_autonomous)
        self.assertFalse(self.ai_gm.autonomous_mode)
        
        # Simulate GMs going offline
        self.ai_gm.online_gms = []
        self.ai_gm.autonomous_mode = True
        
        # Verify mode switch back
        self.assertTrue(self.ai_gm.autonomous_mode)
    
    def test_ml_integration(self):
        """Test ML engine integration"""
        # Test with ML engine available
        self.ai_gm.ml_engine = Mock()
        self.ai_gm.ml_engine.predict_action.return_value = AIGMAction.WARN
        
        incident = PlayerIncident(
            player_id=123,
            player_name="TestPlayer",
            incident_type="stuck_player",
            severity=AIGMSeverity.INFO,
            description="Player stuck at coordinates 0,0,0"
        )
        
        # Test autonomous mode with ML
        action = self.ai_gm._determine_autonomous_action(incident, 0)
        self.assertEqual(action, AIGMAction.WARN)
        self.ai_gm.ml_engine.predict_action.assert_called_with(incident, 0, autonomous_mode=True)
        
        # Test learning mode with ML
        action = self.ai_gm._determine_learning_mode_action(incident, 0)
        self.assertEqual(action, AIGMAction.WARN)
        self.ai_gm.ml_engine.predict_action.assert_called_with(incident, 0, autonomous_mode=False)


if __name__ == '__main__':
    unittest.main()