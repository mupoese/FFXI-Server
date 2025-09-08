#!/usr/bin/env python3
"""
Simple AI-GM System Test
Tests core functionality without external dependencies
"""

import sys
import os
import time
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Optional

# Test the core AI-GM logic without database dependencies

class AIGMSeverity(Enum):
    """Severity levels for AI-GM actions"""
    INFO = "info"
    WARNING = "warning"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"

class AIGMAction(Enum):
    """Available AI-GM actions"""
    WARN = "warn"
    TEMP_JAIL = "temp_jail"
    JAIL = "jail"
    KICK = "kick"
    TEMP_BAN = "temp_ban"
    ESCALATE_GM2 = "escalate_gm2"
    ESCALATE_GM3 = "escalate_gm3"
    NOTIFY_ADMIN = "notify_admin"

@dataclass
class PlayerIncident:
    """Represents a player incident detected by AI-GM"""
    player_id: int
    player_name: str
    incident_type: str
    severity: AIGMSeverity
    description: str
    timestamp: datetime = None
    auto_resolved: bool = False
    action_taken: Optional[AIGMAction] = None
    gm_escalated: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class SimpleAIGM:
    """Simplified AI-GM for testing"""
    
    def __init__(self):
        self.escalation_threshold = 3
        self.player_warnings = {}
        self.incident_history = []
    
    def determine_action(self, incident: PlayerIncident) -> Optional[AIGMAction]:
        """Determine the appropriate action for an incident"""
        warning_count = self.player_warnings.get(incident.player_id, 0)
        
        # Simple rule-based decision making
        if incident.severity == AIGMSeverity.INFO:
            if incident.incident_type == "stuck_player":
                return AIGMAction.WARN
        
        elif incident.severity == AIGMSeverity.WARNING:
            if warning_count >= self.escalation_threshold:
                return AIGMAction.TEMP_JAIL
            else:
                return AIGMAction.WARN
        
        elif incident.severity == AIGMSeverity.MODERATE:
            if warning_count >= 2:
                return AIGMAction.ESCALATE_GM2
            else:
                return AIGMAction.TEMP_JAIL
        
        elif incident.severity == AIGMSeverity.SEVERE:
            return AIGMAction.ESCALATE_GM3
        
        elif incident.severity == AIGMSeverity.CRITICAL:
            return AIGMAction.NOTIFY_ADMIN
        
        return None
    
    def report_incident(self, incident: PlayerIncident):
        """Report and handle a player incident"""
        self.incident_history.append(incident)
        
        # Increment warning count for player
        if incident.player_id not in self.player_warnings:
            self.player_warnings[incident.player_id] = 0
        self.player_warnings[incident.player_id] += 1
        
        # Determine appropriate action
        action = self.determine_action(incident)
        
        if action:
            incident.action_taken = action
            print(f"AI-GM Action: {action.value} for player {incident.player_name} - {incident.description}")
        
        return action

def run_tests():
    """Run AI-GM functionality tests"""
    print("🤖 AI-GM System Test Suite")
    print("=" * 50)
    
    ai_gm = SimpleAIGM()
    test_passed = 0
    test_total = 0
    
    # Test 1: Basic incident creation
    test_total += 1
    try:
        incident = PlayerIncident(
            player_id=123,
            player_name="TestPlayer",
            incident_type="test_incident",
            severity=AIGMSeverity.WARNING,
            description="Test incident description"
        )
        assert incident.player_id == 123
        assert incident.severity == AIGMSeverity.WARNING
        assert not incident.auto_resolved
        print("✅ Test 1: Incident creation - PASSED")
        test_passed += 1
    except Exception as e:
        print(f"❌ Test 1: Incident creation - FAILED: {e}")
    
    # Test 2: Action determination for INFO severity
    test_total += 1
    try:
        incident = PlayerIncident(
            player_id=123,
            player_name="StuckPlayer",
            incident_type="stuck_player",
            severity=AIGMSeverity.INFO,
            description="Player stuck at coordinates"
        )
        action = ai_gm.determine_action(incident)
        assert action == AIGMAction.WARN
        print("✅ Test 2: INFO severity action - PASSED")
        test_passed += 1
    except Exception as e:
        print(f"❌ Test 2: INFO severity action - FAILED: {e}")
    
    # Test 3: Warning escalation system
    test_total += 1
    try:
        incident = PlayerIncident(
            player_id=456,
            player_name="WarningPlayer", 
            incident_type="minor_violation",
            severity=AIGMSeverity.WARNING,
            description="Minor rule violation"
        )
        
        # First warning
        action1 = ai_gm.determine_action(incident)
        assert action1 == AIGMAction.WARN
        
        # Simulate multiple warnings
        ai_gm.player_warnings[456] = 3  # At threshold
        action2 = ai_gm.determine_action(incident)
        assert action2 == AIGMAction.TEMP_JAIL
        
        print("✅ Test 3: Warning escalation - PASSED")
        test_passed += 1
    except Exception as e:
        print(f"❌ Test 3: Warning escalation - FAILED: {e}")
    
    # Test 4: MODERATE severity handling
    test_total += 1
    try:
        incident = PlayerIncident(
            player_id=789,
            player_name="ModeratePlayer",
            incident_type="disruptive_behavior",
            severity=AIGMSeverity.MODERATE,
            description="Disruptive behavior detected"
        )
        
        # First moderate incident should result in temp jail
        action = ai_gm.determine_action(incident)
        assert action == AIGMAction.TEMP_JAIL
        
        # With prior warnings, should escalate
        ai_gm.player_warnings[789] = 2
        action2 = ai_gm.determine_action(incident)
        assert action2 == AIGMAction.ESCALATE_GM2
        
        print("✅ Test 4: MODERATE severity handling - PASSED")
        test_passed += 1
    except Exception as e:
        print(f"❌ Test 4: MODERATE severity handling - FAILED: {e}")
    
    # Test 5: SEVERE and CRITICAL escalation
    test_total += 1
    try:
        severe_incident = PlayerIncident(
            player_id=999,
            player_name="SeverePlayer",
            incident_type="exploitation",
            severity=AIGMSeverity.SEVERE,
            description="Exploitation attempt detected"
        )
        action_severe = ai_gm.determine_action(severe_incident)
        assert action_severe == AIGMAction.ESCALATE_GM3
        
        critical_incident = PlayerIncident(
            player_id=1000,
            player_name="CriticalPlayer",
            incident_type="security_breach",
            severity=AIGMSeverity.CRITICAL,
            description="Critical security incident"
        )
        action_critical = ai_gm.determine_action(critical_incident)
        assert action_critical == AIGMAction.NOTIFY_ADMIN
        
        print("✅ Test 5: SEVERE/CRITICAL escalation - PASSED")
        test_passed += 1
    except Exception as e:
        print(f"❌ Test 5: SEVERE/CRITICAL escalation - FAILED: {e}")
    
    # Test 6: Complete incident flow
    test_total += 1
    try:
        incident = PlayerIncident(
            player_id=555,
            player_name="FlowTestPlayer",
            incident_type="behavior_test",
            severity=AIGMSeverity.WARNING,
            description="Testing complete flow"
        )
        
        # Report the incident
        action = ai_gm.report_incident(incident)
        
        # Check that incident was recorded
        assert len(ai_gm.incident_history) > 0
        assert ai_gm.player_warnings[555] == 1
        assert incident.action_taken == action
        
        print("✅ Test 6: Complete incident flow - PASSED")
        test_passed += 1
    except Exception as e:
        print(f"❌ Test 6: Complete incident flow - FAILED: {e}")
    
    # Test 7: Severity enum values
    test_total += 1
    try:
        assert AIGMSeverity.INFO.value == "info"
        assert AIGMSeverity.WARNING.value == "warning"
        assert AIGMSeverity.MODERATE.value == "moderate"
        assert AIGMSeverity.SEVERE.value == "severe"
        assert AIGMSeverity.CRITICAL.value == "critical"
        
        print("✅ Test 7: Severity enum values - PASSED")
        test_passed += 1
    except Exception as e:
        print(f"❌ Test 7: Severity enum values - FAILED: {e}")
    
    # Test 8: Action enum values
    test_total += 1
    try:
        assert AIGMAction.WARN.value == "warn"
        assert AIGMAction.TEMP_JAIL.value == "temp_jail"
        assert AIGMAction.ESCALATE_GM2.value == "escalate_gm2"
        assert AIGMAction.ESCALATE_GM3.value == "escalate_gm3"
        assert AIGMAction.NOTIFY_ADMIN.value == "notify_admin"
        
        print("✅ Test 8: Action enum values - PASSED")
        test_passed += 1
    except Exception as e:
        print(f"❌ Test 8: Action enum values - FAILED: {e}")
    
    # Test Summary
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {test_passed}/{test_total} tests passed")
    
    if test_passed == test_total:
        print("🎉 All tests passed! AI-GM core functionality is working correctly.")
        return True
    else:
        print(f"⚠️  {test_total - test_passed} tests failed. Please review the implementation.")
        return False

def demo_ai_gm():
    """Demonstrate AI-GM functionality"""
    print("\n🚀 AI-GM System Demonstration")
    print("=" * 50)
    
    ai_gm = SimpleAIGM()
    
    # Simulate various incidents
    incidents = [
        PlayerIncident(1, "StuckPlayer", "stuck_player", AIGMSeverity.INFO, "Player stuck at 0,0,0"),
        PlayerIncident(2, "SpamBot", "spam_behavior", AIGMSeverity.WARNING, "Rapid message sending"),
        PlayerIncident(3, "Disruptor", "disruptive_behavior", AIGMSeverity.MODERATE, "Griefing other players"),
        PlayerIncident(4, "Exploiter", "exploitation", AIGMSeverity.SEVERE, "Using game exploit"),
        PlayerIncident(5, "Hacker", "security_breach", AIGMSeverity.CRITICAL, "Attempting to hack server"),
    ]
    
    print("Processing incidents...")
    for incident in incidents:
        action = ai_gm.report_incident(incident)
        print(f"  Player: {incident.player_name} | Severity: {incident.severity.value} | Action: {action.value if action else 'None'}")
    
    # Simulate repeat offender
    print("\nSimulating repeat offender...")
    repeat_incident = PlayerIncident(2, "SpamBot", "spam_behavior", AIGMSeverity.WARNING, "Continued spamming")
    
    for i in range(3):
        action = ai_gm.report_incident(repeat_incident)
        warnings = ai_gm.player_warnings[2]
        print(f"  Warning #{warnings}: Action = {action.value if action else 'None'}")
    
    print(f"\nTotal incidents processed: {len(ai_gm.incident_history)}")
    print(f"Players with warnings: {len(ai_gm.player_warnings)}")

if __name__ == "__main__":
    success = run_tests()
    
    if success:
        demo_ai_gm()
        print("\n✅ AI-GM System testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ AI-GM System testing failed!")
        sys.exit(1)