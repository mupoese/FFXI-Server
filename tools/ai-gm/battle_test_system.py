#!/usr/bin/env python3
"""
AI-GM Battle Test System
Provides automated GM battle testing and player assistance capabilities
"""

import os
import sys
import json
import time
import logging
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class BattleTestConfig:
    """Configuration for GM battle tests"""
    test_duration_minutes: int = 10
    mob_level_range: Tuple[int, int] = (10, 75)
    spawn_location_radius: float = 50.0
    respawn_delay_seconds: int = 30
    auto_assist_enabled: bool = True
    recording_enabled: bool = True
    analytics_enabled: bool = True

@dataclass
class MobTestData:
    """Data for mob testing"""
    mob_id: int
    mob_name: str
    level: int
    zone_id: int
    family: str
    spawn_pos: Tuple[float, float, float]
    hp_pool: int
    special_attacks: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    immunities: List[str] = field(default_factory=list)
    behavior_type: str = "aggressive"
    difficulty_rating: float = 1.0

@dataclass
class BattleTestSession:
    """GM battle test session"""
    session_id: str
    gm_id: int
    gm_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    zone_id: int = 0
    zone_name: str = ""
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    announcement_text: str = ""
    public_demonstration: bool = True
    safety_warning_level: str = "moderate"  # low, moderate, high, extreme
    mobs_tested: List[MobTestData] = field(default_factory=list)
    damage_dealt: int = 0
    damage_received: int = 0
    abilities_used: List[str] = field(default_factory=list)
    test_results: Dict[str, Any] = field(default_factory=dict)
    assisted_players: List[str] = field(default_factory=list)

@dataclass
class PlayerAssistRequest:
    """Player assistance request"""
    request_id: str
    player_id: int
    player_name: str
    zone_id: int
    position: Tuple[float, float, float]
    issue_type: str
    description: str
    urgency: str = "normal"  # low, normal, high, emergency
    timestamp: datetime = field(default_factory=datetime.now)
    assigned_gm: Optional[str] = None
    status: str = "pending"  # pending, assigned, in_progress, resolved, cancelled

class GMBattleTestSystem:
    """Main GM battle test system"""
    
    def __init__(self):
        self.logger = logging.getLogger('AI-GM-BattleTest')
        self.active_sessions: Dict[str, BattleTestSession] = {}
        self.assist_requests: Dict[str, PlayerAssistRequest] = {}
        self.test_configs: Dict[str, BattleTestConfig] = {}
        self.mob_database: Dict[int, MobTestData] = {}
        self.battle_analytics: List[Dict] = []
        
        # Load mob database and configurations
        self._load_mob_database()
        self._load_test_configs()
    
    def _load_mob_database(self):
        """Load mob database for testing"""
        # This would typically load from the game's mob database
        # For now, we'll create some example mobs
        example_mobs = [
            MobTestData(
                mob_id=17461280, mob_name="Goblin Thug", level=15, zone_id=106,
                family="Goblin", spawn_pos=(100.0, 0.0, 100.0), hp_pool=500,
                special_attacks=["Bomb Toss", "Paralysis"], behavior_type="aggressive"
            ),
            MobTestData(
                mob_id=17534976, mob_name="Orc Fighter", level=25, zone_id=112,
                family="Orc", spawn_pos=(150.0, 0.0, 150.0), hp_pool=1200,
                special_attacks=["Slam", "War Cry"], behavior_type="aggressive"
            ),
            MobTestData(
                mob_id=17289216, mob_name="Greater Pugil", level=45, zone_id=103,
                family="Pugil", spawn_pos=(200.0, -5.0, 200.0), hp_pool=3500,
                special_attacks=["Water Spout", "Intimidate"], behavior_type="territorial"
            ),
            MobTestData(
                mob_id=17355776, mob_name="Ancient Dragon", level=75, zone_id=130,
                family="Dragon", spawn_pos=(0.0, 0.0, 0.0), hp_pool=15000,
                special_attacks=["Flame Breath", "Wing Buffet", "Spike Flail"],
                immunities=["Sleep", "Bind"], difficulty_rating=5.0
            )
        ]
        
        for mob in example_mobs:
            self.mob_database[mob.mob_id] = mob
        
        self.logger.info(f"Loaded {len(self.mob_database)} mobs for testing")
    
    def _load_test_configs(self):
        """Load battle test configurations"""
        default_configs = {
            "quick_test": BattleTestConfig(
                test_duration_minutes=5,
                mob_level_range=(10, 30),
                auto_assist_enabled=True
            ),
            "standard_test": BattleTestConfig(
                test_duration_minutes=10,
                mob_level_range=(20, 50),
                auto_assist_enabled=True
            ),
            "advanced_test": BattleTestConfig(
                test_duration_minutes=20,
                mob_level_range=(40, 75),
                auto_assist_enabled=False,
                analytics_enabled=True
            ),
            "endgame_test": BattleTestConfig(
                test_duration_minutes=30,
                mob_level_range=(65, 75),
                auto_assist_enabled=False,
                recording_enabled=True,
                analytics_enabled=True
            )
        }
        
        self.test_configs.update(default_configs)
        self.logger.info(f"Loaded {len(self.test_configs)} test configurations")
    
    def create_battle_test_session(self, gm_id: int, gm_name: str, 
                                 zone_id: int, zone_name: str = "", 
                                 gm_position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                                 config_name: str = "standard_test", 
                                 announcement: str = "", public_demo: bool = True) -> str:
        """Create a new battle test session with announcement capabilities"""
        try:
            session_id = f"bt_{gm_id}_{int(time.time())}"
            
            if config_name not in self.test_configs:
                config_name = "standard_test"
            
            session = BattleTestSession(
                session_id=session_id,
                gm_id=gm_id,
                gm_name=gm_name,
                start_time=datetime.now(),
                zone_id=zone_id,
                zone_name=zone_name,
                location=gm_position,
                announcement_text=announcement,
                public_demonstration=public_demo,
                safety_warning_level=self._determine_safety_level(config_name)
            )
            
            self.active_sessions[session_id] = session
            
            # Send server-wide announcement if it's a public demonstration
            if public_demo:
                self._send_battle_test_announcement(session, config_name)
            
            self.logger.info(f"Created battle test session {session_id} for GM {gm_name}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error creating battle test session: {e}")
            return ""
    
    def spawn_test_mob(self, session_id: str, mob_request: Dict[str, Any]) -> Dict[str, Any]:
        """Spawn a mob for battle testing"""
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": "Invalid session"}
            
            session = self.active_sessions[session_id]
            config = self.test_configs.get("standard_test")  # Default config
            
            # Determine mob to spawn
            if "mob_id" in mob_request:
                mob_id = mob_request["mob_id"]
                if mob_id not in self.mob_database:
                    return {"success": False, "error": "Unknown mob ID"}
                mob_data = self.mob_database[mob_id]
            else:
                # Auto-select appropriate mob
                mob_data = self._select_test_mob(session.zone_id, config)
                if not mob_data:
                    return {"success": False, "error": "No suitable mobs found"}
            
            # Calculate spawn position
            gm_pos = mob_request.get("gm_position", (0.0, 0.0, 0.0))
            spawn_pos = self._calculate_spawn_position(gm_pos, config.spawn_location_radius)
            
            # Create spawn command data
            spawn_data = {
                "mob_id": mob_data.mob_id,
                "mob_name": mob_data.mob_name,
                "level": mob_data.level,
                "zone_id": session.zone_id,
                "position": spawn_pos,
                "hp": mob_data.hp_pool,
                "special_attacks": mob_data.special_attacks,
                "behavior": mob_data.behavior_type,
                "session_id": session_id,
                "spawn_time": datetime.now().isoformat()
            }
            
            # Add to session
            session.mobs_tested.append(mob_data)
            
            # Send mob spawn announcement if session is public
            announcement_result = None
            if session.public_demonstration:
                announcement_result = self.send_mob_spawn_announcement(session_id, mob_data)
            
            self.logger.info(f"Spawned {mob_data.mob_name} for battle test session {session_id}")
            
            return {
                "success": True,
                "spawn_data": spawn_data,
                "mob_info": {
                    "name": mob_data.mob_name,
                    "level": mob_data.level,
                    "family": mob_data.family,
                    "hp": mob_data.hp_pool,
                    "difficulty": mob_data.difficulty_rating
                },
                "announcement": announcement_result
            }
            
        except Exception as e:
            self.logger.error(f"Error spawning test mob: {e}")
            return {"success": False, "error": str(e)}
    
    def _select_test_mob(self, zone_id: int, config: BattleTestConfig) -> Optional[MobTestData]:
        """Select appropriate mob for testing based on zone and config"""
        suitable_mobs = []
        
        for mob in self.mob_database.values():
            # Check level range
            if config.mob_level_range[0] <= mob.level <= config.mob_level_range[1]:
                # Prefer mobs from the same zone, but allow others
                priority = 1 if mob.zone_id == zone_id else 0.5
                suitable_mobs.append((mob, priority))
        
        if not suitable_mobs:
            return None
        
        # Sort by priority and select randomly from top candidates
        suitable_mobs.sort(key=lambda x: x[1], reverse=True)
        top_candidates = [mob for mob, priority in suitable_mobs[:5]]
        
        return random.choice(top_candidates) if top_candidates else None
    
    def _calculate_spawn_position(self, gm_pos: Tuple[float, float, float], 
                                radius: float) -> Tuple[float, float, float]:
        """Calculate appropriate spawn position near GM"""
        angle = random.uniform(0, 2 * 3.14159)
        distance = random.uniform(radius * 0.5, radius)
        
        x = gm_pos[0] + distance * random.uniform(-1, 1)
        y = gm_pos[1]
        z = gm_pos[2] + distance * random.uniform(-1, 1)
        
        return (round(x, 2), round(y, 2), round(z, 2))
    
    def record_battle_action(self, session_id: str, action_data: Dict[str, Any]):
        """Record battle action for analytics"""
        try:
            if session_id not in self.active_sessions:
                return
            
            session = self.active_sessions[session_id]
            
            action_type = action_data.get("type", "unknown")
            
            if action_type == "damage_dealt":
                session.damage_dealt += action_data.get("amount", 0)
            elif action_type == "damage_received":
                session.damage_received += action_data.get("amount", 0)
            elif action_type == "ability_used":
                ability = action_data.get("ability", "")
                if ability:
                    session.abilities_used.append(ability)
            
            # Store detailed analytics
            analytics_entry = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "action": action_data
            }
            self.battle_analytics.append(analytics_entry)
            
        except Exception as e:
            self.logger.error(f"Error recording battle action: {e}")
    
    def end_battle_test_session(self, session_id: str) -> Dict[str, Any]:
        """End a battle test session and generate report"""
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": "Session not found"}
            
            session = self.active_sessions[session_id]
            session.end_time = datetime.now()
            
            # Generate session report
            duration = (session.end_time - session.start_time).total_seconds() / 60
            
            report = {
                "session_id": session_id,
                "gm_name": session.gm_name,
                "duration_minutes": round(duration, 2),
                "mobs_tested": len(session.mobs_tested),
                "total_damage_dealt": session.damage_dealt,
                "total_damage_received": session.damage_received,
                "abilities_used": len(set(session.abilities_used)),
                "players_assisted": len(session.assisted_players),
                "mob_details": [
                    {
                        "name": mob.mob_name,
                        "level": mob.level,
                        "family": mob.family,
                        "difficulty": mob.difficulty_rating
                    }
                    for mob in session.mobs_tested
                ]
            }
            
            # Store completed session
            session.test_results = report
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            self.logger.info(f"Battle test session {session_id} completed")
            
            return {"success": True, "report": report}
            
        except Exception as e:
            self.logger.error(f"Error ending battle test session: {e}")
            return {"success": False, "error": str(e)}
    
    def create_assist_request(self, player_id: int, player_name: str, 
                            zone_id: int, position: Tuple[float, float, float],
                            issue_type: str, description: str, urgency: str = "normal") -> str:
        """Create a player assistance request"""
        try:
            request_id = f"assist_{player_id}_{int(time.time())}"
            
            request = PlayerAssistRequest(
                request_id=request_id,
                player_id=player_id,
                player_name=player_name,
                zone_id=zone_id,
                position=position,
                issue_type=issue_type,
                description=description,
                urgency=urgency
            )
            
            self.assist_requests[request_id] = request
            
            self.logger.info(f"Created assist request {request_id} for player {player_name}")
            return request_id
            
        except Exception as e:
            self.logger.error(f"Error creating assist request: {e}")
            return ""
    
    def assign_gm_to_request(self, request_id: str, gm_name: str, 
                           auto_spawn_for_demo: bool = False) -> Dict[str, Any]:
        """Assign a GM to handle an assistance request"""
        try:
            if request_id not in self.assist_requests:
                return {"success": False, "error": "Request not found"}
            
            request = self.assist_requests[request_id]
            request.assigned_gm = gm_name
            request.status = "assigned"
            
            response = {
                "success": True,
                "request_info": {
                    "player_name": request.player_name,
                    "zone_id": request.zone_id,
                    "position": request.position,
                    "issue_type": request.issue_type,
                    "description": request.description,
                    "urgency": request.urgency
                }
            }
            
            # If this is a combat-related request and auto_spawn_for_demo is enabled
            if auto_spawn_for_demo and request.issue_type in ["stuck_in_combat", "mob_assistance"]:
                # Create a battle test session for this assistance
                session_id = self.create_battle_test_session(
                    gm_id=9999,  # Use special GM ID for assist sessions
                    gm_name=gm_name,
                    zone_id=request.zone_id,
                    config_name="quick_test"
                )
                
                if session_id:
                    # Spawn an appropriate mob for the GM to demonstrate
                    mob_spawn = self.spawn_test_mob(session_id, {
                        "gm_position": request.position,
                        "level_preference": "moderate"
                    })
                    
                    response["demo_session"] = {
                        "session_id": session_id,
                        "mob_spawned": mob_spawn.get("success", False),
                        "instructions": "GM can now battle the spawned mob to demonstrate combat mechanics to the player"
                    }
            
            self.logger.info(f"Assigned GM {gm_name} to assist request {request_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error assigning GM to request: {e}")
            return {"success": False, "error": str(e)}
    
    def resolve_assist_request(self, request_id: str, resolution_notes: str) -> bool:
        """Mark an assistance request as resolved"""
        try:
            if request_id not in self.assist_requests:
                return False
            
            request = self.assist_requests[request_id]
            request.status = "resolved"
            
            # Add to resolved list for any active battle test sessions
            for session in self.active_sessions.values():
                if request.assigned_gm == session.gm_name:
                    session.assisted_players.append(request.player_name)
            
            self.logger.info(f"Resolved assist request {request_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resolving assist request: {e}")
            return False
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active battle test sessions"""
        sessions = []
        
        for session in self.active_sessions.values():
            duration = (datetime.now() - session.start_time).total_seconds() / 60
            
            sessions.append({
                "session_id": session.session_id,
                "gm_name": session.gm_name,
                "zone_id": session.zone_id,
                "duration_minutes": round(duration, 2),
                "mobs_tested": len(session.mobs_tested),
                "damage_dealt": session.damage_dealt,
                "players_assisted": len(session.assisted_players)
            })
        
        return sessions
    
    def get_pending_assist_requests(self, urgency_filter: str = None) -> List[Dict[str, Any]]:
        """Get list of pending assistance requests"""
        requests = []
        
        for request in self.assist_requests.values():
            if request.status in ["pending", "assigned"]:
                if urgency_filter and request.urgency != urgency_filter:
                    continue
                
                age_minutes = (datetime.now() - request.timestamp).total_seconds() / 60
                
                requests.append({
                    "request_id": request.request_id,
                    "player_name": request.player_name,
                    "zone_id": request.zone_id,
                    "issue_type": request.issue_type,
                    "description": request.description,
                    "urgency": request.urgency,
                    "age_minutes": round(age_minutes, 2),
                    "assigned_gm": request.assigned_gm,
                    "status": request.status
                })
        
        # Sort by urgency and age
        urgency_priority = {"emergency": 0, "high": 1, "normal": 2, "low": 3}
        requests.sort(key=lambda x: (urgency_priority.get(x["urgency"], 2), x["age_minutes"]))
        
        return requests
    
    def get_battle_analytics(self, session_id: str = None) -> Dict[str, Any]:
        """Get battle analytics data"""
        if session_id:
            # Get analytics for specific session
            session_data = [a for a in self.battle_analytics if a["session_id"] == session_id]
            return {"session_id": session_id, "actions": session_data}
        else:
            # Get overall analytics
            total_sessions = len(self.active_sessions) + len([
                a for a in self.battle_analytics 
                if a.get("session_id", "").startswith("bt_")
            ])
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": len(self.active_sessions),
                "total_actions_recorded": len(self.battle_analytics),
                "recent_actions": self.battle_analytics[-10:] if self.battle_analytics else []
            }
    
    def _determine_safety_level(self, config_name: str) -> str:
        """Determine safety warning level based on test configuration"""
        safety_levels = {
            "quick_test": "low",
            "standard_test": "moderate", 
            "advanced_test": "high",
            "endgame_test": "extreme"
        }
        return safety_levels.get(config_name, "moderate")
    
    def _send_battle_test_announcement(self, session: BattleTestSession, config_name: str):
        """Send server-wide announcement for battle test session"""
        try:
            # Format location string
            loc_str = f"({session.location[0]:.1f}, {session.location[1]:.1f}, {session.location[2]:.1f})"
            
            # Create safety warning based on level
            safety_warnings = {
                "low": "⚠️  Low-level players welcome to observe",
                "moderate": "⚠️  Mid-level players (25+) recommended", 
                "high": "⚠️  High-level players only (50+) - Combat may be dangerous",
                "extreme": "⚠️  EXTREME DANGER - Endgame content testing - Keep safe distance!"
            }
            
            safety_msg = safety_warnings.get(session.safety_warning_level, "⚠️  Use caution when observing")
            
            # Build announcement message
            announcement_parts = [
                f"🛡️ GM BATTLE DEMONSTRATION STARTING 🛡️",
                f"GM: {session.gm_name}",
                f"Location: {session.zone_name} {loc_str}",
                f"Test Type: {config_name.replace('_', ' ').title()}",
                safety_msg
            ]
            
            # Add custom comment if provided
            if session.announcement_text.strip():
                announcement_parts.append(f"Comment: {session.announcement_text}")
            
            announcement_parts.append("Players may observe from a safe distance")
            
            # Join all parts into final message
            full_announcement = "\n".join(announcement_parts)
            
            # Log the announcement for server broadcast
            self.logger.info(f"Battle test announcement for session {session.session_id}:")
            self.logger.info(full_announcement)
            
            # Store announcement data for external broadcasting
            announcement_data = {
                "type": "battle_test_announcement",
                "session_id": session.session_id,
                "gm_name": session.gm_name,
                "zone_name": session.zone_name,
                "location": session.location,
                "config_type": config_name,
                "safety_level": session.safety_warning_level,
                "custom_message": session.announcement_text,
                "full_message": full_announcement,
                "timestamp": datetime.now().isoformat()
            }
            
            # This would be used by the AI-GM service to broadcast via game server
            return announcement_data
            
        except Exception as e:
            self.logger.error(f"Error sending battle test announcement: {e}")
            return None
    
    def update_session_announcement(self, session_id: str, new_announcement: str) -> bool:
        """Update announcement text for an active session"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            old_announcement = session.announcement_text
            session.announcement_text = new_announcement
            
            self.logger.info(f"Updated announcement for session {session_id}: '{old_announcement}' -> '{new_announcement}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating session announcement: {e}")
            return False
    
    def send_mob_spawn_announcement(self, session_id: str, mob_data: MobTestData) -> Dict[str, Any]:
        """Send announcement when spawning a test mob"""
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": "Session not found"}
            
            session = self.active_sessions[session_id]
            
            # Create mob spawn announcement
            mob_announcement = [
                f"🗡️ GM {session.gm_name} spawning test mob:",
                f"Mob: {mob_data.mob_name} (Level {mob_data.level})",
                f"Location: {session.zone_name} ({session.location[0]:.1f}, {session.location[1]:.1f}, {session.location[2]:.1f})",
                f"Family: {mob_data.family}"
            ]
            
            # Add special warnings for dangerous mobs
            if mob_data.level >= 60:
                mob_announcement.append("⚠️ HIGH LEVEL MOB - Keep safe distance!")
            elif mob_data.level >= 40:
                mob_announcement.append("⚠️ Moderate level mob - Lower level players stay back")
            
            if mob_data.special_attacks:
                mob_announcement.append(f"Special Attacks: {', '.join(mob_data.special_attacks[:3])}")
            
            announcement_text = "\n".join(mob_announcement)
            
            announcement_data = {
                "type": "mob_spawn_announcement", 
                "session_id": session_id,
                "gm_name": session.gm_name,
                "mob_name": mob_data.mob_name,
                "mob_level": mob_data.level,
                "location": session.location,
                "zone_name": session.zone_name,
                "full_message": announcement_text,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Mob spawn announcement for session {session_id}: {mob_data.mob_name}")
            return {"success": True, "announcement": announcement_data}
            
        except Exception as e:
            self.logger.error(f"Error sending mob spawn announcement: {e}")
            return {"success": False, "error": str(e)}

# Example usage and testing
if __name__ == "__main__":
    # Initialize battle test system
    battle_system = GMBattleTestSystem()
    
    # Create a test session
    session_id = battle_system.create_battle_test_session(
        gm_id=12345,
        gm_name="GM-TestUser",
        zone_id=106  # West Sarutabaruta
    )
    
    print(f"Created test session: {session_id}")
    
    # Spawn a test mob
    spawn_result = battle_system.spawn_test_mob(session_id, {
        "gm_position": (100.0, 0.0, 100.0)
    })
    
    print(f"Spawn result: {spawn_result}")
    
    # Create an assist request
    assist_id = battle_system.create_assist_request(
        player_id=67890,
        player_name="TestPlayer",
        zone_id=106,
        position=(120.0, 0.0, 120.0),
        issue_type="stuck_in_combat",
        description="Player needs help with a difficult mob",
        urgency="normal"
    )
    
    print(f"Created assist request: {assist_id}")
    
    # Assign GM to the request
    assign_result = battle_system.assign_gm_to_request(assist_id, "GM-TestUser", auto_spawn_for_demo=True)
    
    print(f"Assignment result: {assign_result}")
    
    # Show system status
    print("Active sessions:", battle_system.get_active_sessions())
    print("Pending requests:", battle_system.get_pending_assist_requests())