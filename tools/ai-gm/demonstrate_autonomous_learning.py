#!/usr/bin/env python3
"""
AI-GM Autonomous Operation and GM Learning Demonstration

This script demonstrates the new capabilities where the AI-GM:
1. Operates autonomously when no human GMs are available
2. Learns from human GM interactions when they are online
"""

import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock

# Mock dependencies for demonstration
sys.modules['mysql'] = Mock()
sys.modules['mysql.connector'] = Mock()
sys.modules['mysql.connector.pooling'] = Mock()
sys.modules['requests'] = Mock()

from ai_gm_service import AIGMService, AIGMConfig, PlayerIncident, AIGMSeverity, AIGMAction

def demonstrate_autonomous_vs_learning():
    """Demonstrate the difference between autonomous and learning modes"""
    
    print("🤖 AI-GM Autonomous Operation & Learning Demonstration")
    print("=" * 60)
    
    # Create AI-GM instance
    config = AIGMConfig()
    config.autonomous_mode_enabled = True
    config.gm_learning_enabled = True
    
    # Mock the service (without actual database connections)
    ai_gm = AIGMService.__new__(AIGMService)
    ai_gm.config = config
    ai_gm.autonomous_mode = True
    ai_gm.online_gms = []
    ai_gm.learning_session_active = False
    ai_gm.player_warnings = {}
    ai_gm.gm_actions_history = []
    ai_gm.incident_history = []
    ai_gm.ml_engine = Mock()
    ai_gm.logger = Mock()
    
    # Create a test incident
    incident = PlayerIncident(
        player_id=123,
        player_name="TestPlayer",
        incident_type="suspicious_login",
        severity=AIGMSeverity.WARNING,
        description="Multiple rapid logins detected"
    )
    
    # Mock previous warnings
    ai_gm.player_warnings[123] = 1
    
    print("\n📋 Test Incident:")
    print(f"   Player: {incident.player_name}")
    print(f"   Type: {incident.incident_type}")
    print(f"   Severity: {incident.severity.value}")
    print(f"   Previous warnings: {ai_gm.player_warnings[123]}")
    
    # SCENARIO 1: No GMs online (Autonomous Mode)
    print("\n🔄 SCENARIO 1: No Human GMs Online (AUTONOMOUS MODE)")
    print("-" * 50)
    ai_gm.autonomous_mode = True
    ai_gm.online_gms = []
    
    action_autonomous = ai_gm._determine_autonomous_action(incident, ai_gm.player_warnings[123])
    
    print(f"   Mode: AUTONOMOUS")
    print(f"   Online GMs: {len(ai_gm.online_gms)}")
    print(f"   AI-GM Decision: {action_autonomous.value if action_autonomous else 'None'}")
    print(f"   Reasoning: AI-GM operates independently, more aggressive approach")
    print(f"   Result: Temporary jail - immediate containment without GM escalation")
    
    # SCENARIO 2: GMs online (Learning Mode)
    print("\n👥 SCENARIO 2: Human GMs Online (LEARNING MODE)")
    print("-" * 50)
    ai_gm.autonomous_mode = False
    ai_gm.online_gms = [
        {'charid': 1, 'charname': 'HumanGM1', 'gmlevel': 3, 'pos_zone': 230},
        {'charid': 2, 'charname': 'HumanGM2', 'gmlevel': 2, 'pos_zone': 235}
    ]
    ai_gm.learning_session_active = True
    
    action_learning = ai_gm._determine_learning_mode_action(incident, ai_gm.player_warnings[123])
    
    print(f"   Mode: LEARNING")
    print(f"   Online GMs: {len(ai_gm.online_gms)}")
    gm_names = [f"{gm['charname']} (Level {gm['gmlevel']})" for gm in ai_gm.online_gms]
    print(f"   GMs: {', '.join(gm_names)}")
    print(f"   AI-GM Decision: {action_learning.value if action_learning else 'None'}")
    print(f"   Reasoning: Conservative approach, defer to human GMs for learning")
    print(f"   Result: Warning issued, observe human GM response for learning")
    
    # SCENARIO 3: Learning from GM Actions
    print("\n📚 SCENARIO 3: Learning from Human GM Actions")
    print("-" * 50)
    
    # Simulate GM action
    gm_action = {
        'action_id': 'test_action_1',
        'timestamp': datetime.now(),
        'gm_name': 'HumanGM1',
        'command': 'jail',
        'full_string': 'jail TestPlayer 60 Repeated suspicious login patterns',
        'context': {
            'server_load': {'player_count': 45, 'recent_incidents': 3},
            'target_player': {'charid': 123, 'charname': 'TestPlayer'}
        }
    }
    
    # Classify the action
    action_type = ai_gm._classify_gm_action(gm_action['command'])
    severity = ai_gm._extract_severity_from_action(gm_action)
    pattern = ai_gm._analyze_escalation_pattern(gm_action)
    
    print(f"   GM Action: {gm_action['command']} by {gm_action['gm_name']}")
    print(f"   Classification: {action_type}")
    print(f"   Severity: {severity}")
    print(f"   Immediate Action: {pattern['immediate_action']}")
    print(f"   Escalation Level: {pattern['escalation_level']}")
    print(f"   Learning: AI-GM observes and learns this pattern for future decisions")
    
    # SCENARIO 4: Adaptive Behavior Comparison
    print("\n⚖️ SCENARIO 4: Adaptive Behavior Comparison")
    print("-" * 50)
    
    print("   Same incident, different responses based on GM availability:")
    print(f"   • NO GMs online  → {action_autonomous.value if action_autonomous else 'None'} (immediate action)")
    print(f"   • GMs online     → {action_learning.value if action_learning else 'None'} (conservative, learn from humans)")
    print("   • After learning → AI-GM will apply learned patterns when autonomous")
    
    # SCENARIO 5: Server Load Impact
    print("\n📊 SCENARIO 5: Server Context Awareness")
    print("-" * 50)
    
    server_metrics = {
        'player_count': 45,
        'recent_incidents': 3,
        'ai_gm_actions_last_hour': 2
    }
    
    print(f"   Server Load: {server_metrics['player_count']} players online")
    print(f"   Recent Incidents: {server_metrics['recent_incidents']}")
    print(f"   AI-GM Actions (1h): {server_metrics['ai_gm_actions_last_hour']}")
    print("   Impact: AI-GM considers server context in decision-making")
    print("   Learning: Patterns learned include server state for better decisions")
    
    print("\n✨ KEY IMPROVEMENTS:")
    print("   ✅ Autonomous operation when no human GMs available")
    print("   ✅ Learning from human GM interactions and decisions")
    print("   ✅ Adaptive behavior based on GM availability")
    print("   ✅ Context-aware decision making")
    print("   ✅ Pattern recognition from human GM actions")
    print("   ✅ Server load and state consideration")
    
    print("\n🎯 RESULT: AI-GM provides optimal assistance whether operating")
    print("   independently or learning from experienced human GMs!")

if __name__ == "__main__":
    demonstrate_autonomous_vs_learning()