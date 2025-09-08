#!/usr/bin/env python3
"""
FFXI Server AI-GM Service
Experimental AI Game Master for automated moderation and player assistance

This service provides:
- Automated problem detection and resolution
- Player behavior monitoring
- Automated disciplinary actions (jailing)
- Communication with players
- Escalation to human GMs when needed
"""

import os
import sys
import json
import time
import logging
import asyncio
import threading
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import mysql.connector
from mysql.connector import pooling

# Add the tools directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))

# Import AI-GM ML and Battle Test modules
try:
    from ml_engine import AIGMMLEngine, PlayerBehaviorData
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML engine not available, running without machine learning capabilities")

try:
    from battle_test_system import GMBattleTestSystem, BattleTestSession, PlayerAssistRequest
    BATTLE_TEST_AVAILABLE = True
except ImportError:
    BATTLE_TEST_AVAILABLE = False
    print("Warning: Battle test system not available, running without battle testing capabilities")

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
    timestamp: datetime = field(default_factory=datetime.now)
    auto_resolved: bool = False
    action_taken: Optional[AIGMAction] = None
    gm_escalated: bool = False

@dataclass
class AIGMConfig:
    """Configuration for AI-GM service"""
    # Database connection
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "xiuser"
    db_password: str = "xiserver_2024"
    db_name: str = "xidb"
    
    # API endpoints
    api_base_url: str = "http://localhost:5000"
    api_secret_key: str = "your_secret_key_here_change_this"
    
    # AI-GM behavior settings
    auto_moderation_enabled: bool = True
    jail_duration_minutes: int = 30
    escalation_threshold: int = 3
    monitoring_interval_seconds: int = 60
    
    # Communication settings
    gm_name: str = "AI-GM"
    gm_level: int = 2
    announce_actions: bool = True
    
    # Machine Learning settings
    ml_enabled: bool = True
    ml_learning_enabled: bool = True
    ml_model_update_interval: int = 1000
    hardware_acceleration: bool = True
    
    # Battle Test settings
    battle_test_enabled: bool = True
    auto_assist_enabled: bool = True
    demo_sessions_enabled: bool = True
    
    # Autonomous operation settings
    autonomous_mode_enabled: bool = True
    gm_learning_enabled: bool = True
    autonomy_level_adjustment: bool = True
    min_gm_level_for_learning: int = 2

class AIGMService:
    """Main AI-GM service class"""
    
    def __init__(self, config: AIGMConfig):
        self.config = config
        self.running = False
        self.db_pool = None
        self.incident_history: List[PlayerIncident] = []
        self.player_warnings: Dict[int, int] = {}
        
        # GM availability tracking
        self.online_gms: List[Dict[str, Any]] = []
        self.gm_availability_last_check = datetime.now()
        self.autonomous_mode = True  # Start in autonomous mode until GMs are detected
        
        # Learning from GM interactions
        self.gm_actions_history: List[Dict[str, Any]] = []
        self.learning_session_active = False
        
        # Initialize ML Engine
        self.ml_engine = None
        if ML_AVAILABLE and config.ml_enabled:
            try:
                self.ml_engine = AIGMMLEngine()
                self.logger.info("AI-GM ML Engine initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize ML engine: {e}")
        
        # Initialize Battle Test System
        self.battle_system = None
        if BATTLE_TEST_AVAILABLE and config.battle_test_enabled:
            try:
                self.battle_system = GMBattleTestSystem()
                self.logger.info("AI-GM Battle Test System initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize battle test system: {e}")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/ai_gm.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AI-GM')
        
    def initialize(self):
        """Initialize the AI-GM service"""
        try:
            # Create logs directory if it doesn't exist
            os.makedirs('logs', exist_ok=True)
            
            # Initialize database connection pool
            self.db_pool = pooling.MySQLConnectionPool(
                pool_name="ai_gm_pool",
                pool_size=5,
                pool_reset_session=True,
                host=self.config.db_host,
                port=self.config.db_port,
                user=self.config.db_user,
                password=self.config.db_password,
                database=self.config.db_name,
                autocommit=True
            )
            
            # Initialize ML engine if available
            if self.ml_engine and self.config.ml_enabled:
                self.ml_engine.load_models()
                self.logger.info("ML models loaded")
                
                # Train initial models with historical data
                historical_data = self._fetch_historical_player_data()
                if historical_data:
                    self._train_ml_models_with_data(historical_data)
            
            self.logger.info("AI-GM Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI-GM service: {e}")
            return False
    
    def get_db_connection(self):
        """Get a database connection from the pool"""
        return self.db_pool.get_connection()
    
    def execute_query(self, query: str, params: tuple = None, fetch_all: bool = True, fetch_one: bool = False) -> List[Dict]:
        """Execute a database query and return results"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    if fetch_one:
                        result = cursor.fetchone()
                        return result if result else {}
                    else:
                        return cursor.fetchall()
                else:
                    conn.commit()
                    return []
                    
        except Exception as e:
            self.logger.error(f"Database query failed: {e}")
            return [] if not fetch_one else {}
    
    def monitor_player_behavior(self):
        """Monitor player behavior for problematic activities"""
        try:
            # Check for rapid login/logout patterns (potential bot behavior)
            recent_logins = self.execute_query("""
                SELECT charid, charname, COUNT(*) as login_count
                FROM char_stats 
                WHERE DATE(last_update) = CURDATE()
                GROUP BY charid, charname
                HAVING login_count > 50
            """)
            
            for player in recent_logins:
                self.report_incident(
                    PlayerIncident(
                        player_id=player['charid'],
                        player_name=player['charname'],
                        incident_type="suspicious_login_pattern",
                        severity=AIGMSeverity.WARNING,
                        description=f"Excessive login activity: {player['login_count']} logins today"
                    )
                )
            
            # Check for players stuck in problematic areas
            stuck_players = self.execute_query("""
                SELECT c.charid, c.charname, c.pos_zone, c.pos_x, c.pos_y, c.pos_z
                FROM chars c
                WHERE c.pos_zone = 0 OR (c.pos_x = 0 AND c.pos_y = 0 AND c.pos_z = 0)
            """)
            
            for player in stuck_players:
                self.report_incident(
                    PlayerIncident(
                        player_id=player['charid'],
                        player_name=player['charname'],
                        incident_type="stuck_player",
                        severity=AIGMSeverity.INFO,
                        description="Player appears to be stuck at invalid coordinates"
                    )
                )
            
            # Check for players who have been jailed for too long
            long_jailed = self.execute_query("""
                SELECT c.charid, c.charname, cv.value as jail_cell
                FROM chars c
                JOIN char_vars cv ON c.charid = cv.charid
                WHERE cv.varname = 'inJail' AND cv.value > 0
            """)
            
            for player in long_jailed:
                # Check jail duration
                jail_time_query = self.execute_query("""
                    SELECT value as jail_time
                    FROM char_vars
                    WHERE charid = %s AND varname = 'jailTime'
                """, (player['charid'],))
                
                if jail_time_query:
                    jail_time = int(jail_time_query[0]['jail_time'])
                    current_time = int(time.time())
                    hours_jailed = (current_time - jail_time) / 3600
                    
                    if hours_jailed > 24:  # Jailed for more than 24 hours
                        self.report_incident(
                            PlayerIncident(
                                player_id=player['charid'],
                                player_name=player['charname'],
                                incident_type="long_jail_time",
                                severity=AIGMSeverity.MODERATE,
                                description=f"Player has been jailed for {hours_jailed:.1f} hours"
                            )
                        )
            
        except Exception as e:
            self.logger.error(f"Error monitoring player behavior: {e}")
    
    def report_incident(self, incident: PlayerIncident):
        """Report and handle a player incident"""
        self.incident_history.append(incident)
        self.logger.info(f"Incident reported: {incident.incident_type} for player {incident.player_name}")
        
        # Increment warning count for player
        if incident.player_id not in self.player_warnings:
            self.player_warnings[incident.player_id] = 0
        self.player_warnings[incident.player_id] += 1
        
        # Determine appropriate action based on severity and history
        action = self.determine_action(incident)
        
        if action and self.config.auto_moderation_enabled:
            self.execute_action(incident, action)
    
    def determine_action(self, incident: PlayerIncident) -> Optional[AIGMAction]:
        """Determine the appropriate action for an incident with adaptive behavior based on GM availability"""
        warning_count = self.player_warnings.get(incident.player_id, 0)
        
        # Adjust decision-making based on GM availability
        if self.autonomous_mode:
            # More proactive when no human GMs available
            return self._determine_autonomous_action(incident, warning_count)
        else:
            # More conservative when human GMs are available (learning mode)
            return self._determine_learning_mode_action(incident, warning_count)
    
    def _determine_autonomous_action(self, incident: PlayerIncident, warning_count: int) -> Optional[AIGMAction]:
        """Determine action when operating autonomously (no human GMs available)"""
        
        # Use ML engine predictions if available
        if self.ml_engine and self.config.ml_enabled:
            ml_action = self.ml_engine.predict_action(incident, warning_count, autonomous_mode=True)
            if ml_action:
                return ml_action
        
        # Enhanced autonomous decision-making
        if incident.severity == AIGMSeverity.INFO:
            if incident.incident_type == "stuck_player":
                return AIGMAction.WARN  # Auto-resolve with warning
        
        elif incident.severity == AIGMSeverity.WARNING:
            if warning_count >= 1:  # Lower threshold in autonomous mode
                return AIGMAction.TEMP_JAIL
            else:
                return AIGMAction.WARN
        
        elif incident.severity == AIGMSeverity.MODERATE:
            if warning_count >= 1:  # More aggressive in autonomous mode
                return AIGMAction.TEMP_JAIL
            else:
                return AIGMAction.WARN
        
        elif incident.severity == AIGMSeverity.SEVERE:
            # Handle more severe cases autonomously when no GMs available
            if warning_count >= 2:
                return AIGMAction.JAIL  # Indefinite jail
            else:
                return AIGMAction.TEMP_JAIL
        
        elif incident.severity == AIGMSeverity.CRITICAL:
            # Still escalate critical issues, but also take immediate action
            return AIGMAction.JAIL  # Immediate containment while notifying admin
        
        return None
    
    def _determine_learning_mode_action(self, incident: PlayerIncident, warning_count: int) -> Optional[AIGMAction]:
        """Determine action when human GMs are available (learning mode)"""
        
        # Use ML engine predictions if available (but be more conservative)
        if self.ml_engine and self.config.ml_enabled:
            ml_action = self.ml_engine.predict_action(incident, warning_count, autonomous_mode=False)
            if ml_action:
                return ml_action
        
        # Conservative decision-making when GMs are available
        if incident.severity == AIGMSeverity.INFO:
            if incident.incident_type == "stuck_player":
                return AIGMAction.WARN
        
        elif incident.severity == AIGMSeverity.WARNING:
            if warning_count >= self.config.escalation_threshold:
                return AIGMAction.ESCALATE_GM2  # Escalate instead of auto-jail
            else:
                return AIGMAction.WARN
        
        elif incident.severity == AIGMSeverity.MODERATE:
            if warning_count >= 2:
                return AIGMAction.ESCALATE_GM2
            else:
                return AIGMAction.WARN
        
        elif incident.severity == AIGMSeverity.SEVERE:
            return AIGMAction.ESCALATE_GM3
        
        elif incident.severity == AIGMSeverity.CRITICAL:
            return AIGMAction.NOTIFY_ADMIN
        
        return None
    
    def execute_action(self, incident: PlayerIncident, action: AIGMAction):
        """Execute the determined action"""
        try:
            incident.action_taken = action
            
            if action == AIGMAction.WARN:
                self.send_warning(incident)
            
            elif action == AIGMAction.TEMP_JAIL:
                self.jail_player(incident, self.config.jail_duration_minutes)
            
            elif action == AIGMAction.JAIL:
                self.jail_player(incident, 0)  # Indefinite
            
            elif action == AIGMAction.ESCALATE_GM2:
                self.escalate_to_gm(incident, 2)
            
            elif action == AIGMAction.ESCALATE_GM3:
                self.escalate_to_gm(incident, 3)
            
            elif action == AIGMAction.NOTIFY_ADMIN:
                self.notify_admin(incident)
            
            incident.auto_resolved = action not in [AIGMAction.ESCALATE_GM2, AIGMAction.ESCALATE_GM3, AIGMAction.NOTIFY_ADMIN]
            
        except Exception as e:
            self.logger.error(f"Failed to execute action {action}: {e}")
    
    def send_warning(self, incident: PlayerIncident):
        """Send a warning message to the player"""
        try:
            # Insert a message that will be delivered to the player
            message = f"[AI-GM Warning] {incident.description}"
            
            # Log the warning in audit table
            self.execute_query("""
                INSERT INTO audit_gm (date_time, gm_name, command, full_string)
                VALUES (NOW(), %s, 'warn', %s)
            """, (self.config.gm_name, f"Warning sent to {incident.player_name}: {incident.description}"))
            
            self.logger.info(f"Warning sent to player {incident.player_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to send warning: {e}")
    
    def jail_player(self, incident: PlayerIncident, duration_minutes: int):
        """Jail a player for the specified duration"""
        try:
            # Set jail variables in database
            current_time = int(time.time())
            
            # Set inJail status
            self.execute_query("""
                INSERT INTO char_vars (charid, varname, value) 
                VALUES (%s, 'inJail', 1)
                ON DUPLICATE KEY UPDATE value = 1
            """, (incident.player_id,))
            
            # Set jail time
            self.execute_query("""
                INSERT INTO char_vars (charid, varname, value)
                VALUES (%s, 'jailTime', %s)
                ON DUPLICATE KEY UPDATE value = %s
            """, (incident.player_id, str(current_time), str(current_time)))
            
            # Set jail duration if specified
            if duration_minutes > 0:
                self.execute_query("""
                    INSERT INTO char_vars (charid, varname, value)
                    VALUES (%s, 'jailDuration', %s)
                    ON DUPLICATE KEY UPDATE value = %s
                """, (incident.player_id, str(duration_minutes), str(duration_minutes)))
            
            # Set jail reason
            self.execute_query("""
                INSERT INTO char_vars (charid, varname, value)
                VALUES (%s, 'jailReason', %s)
                ON DUPLICATE KEY UPDATE value = %s
            """, (incident.player_id, incident.description, incident.description))
            
            # Move player to jail zone if they're online
            self.execute_query("""
                UPDATE chars 
                SET pos_zone = 131, pos_x = -620, pos_y = 11, pos_z = 660
                WHERE charid = %s
            """, (incident.player_id,))
            
            # Log the action
            duration_text = f"{duration_minutes} minutes" if duration_minutes > 0 else "indefinite"
            self.execute_query("""
                INSERT INTO audit_gm (date_time, gm_name, command, full_string)
                VALUES (NOW(), %s, 'jail', %s)
            """, (self.config.gm_name, f"Jailed {incident.player_name} for {duration_text}. Reason: {incident.description}"))
            
            self.logger.info(f"Player {incident.player_name} jailed for {duration_text}")
            
        except Exception as e:
            self.logger.error(f"Failed to jail player: {e}")
    
    def escalate_to_gm(self, incident: PlayerIncident, gm_level: int):
        """Escalate incident to human GM"""
        try:
            incident.gm_escalated = True
            
            # Create a notification for online GMs
            escalation_message = f"[AI-GM ESCALATION] Player: {incident.player_name}, Issue: {incident.description}, Severity: {incident.severity.value}"
            
            # Log escalation
            self.execute_query("""
                INSERT INTO audit_gm (date_time, gm_name, command, full_string)
                VALUES (NOW(), %s, 'escalate', %s)
            """, (self.config.gm_name, escalation_message))
            
            self.logger.warning(f"Escalated incident to GM level {gm_level}: {incident.player_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to escalate to GM: {e}")
    
    def notify_admin(self, incident: PlayerIncident):
        """Notify server admin of critical incident"""
        try:
            admin_message = f"[AI-GM CRITICAL] Immediate admin attention required for player {incident.player_name}: {incident.description}"
            
            # Log critical notification
            self.execute_query("""
                INSERT INTO audit_gm (date_time, gm_name, command, full_string)
                VALUES (NOW(), %s, 'critical', %s)
            """, (self.config.gm_name, admin_message))
            
            self.logger.critical(f"Critical notification sent for player {incident.player_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to notify admin: {e}")
    
    def check_scheduled_releases(self):
        """Check for players who should be released from jail"""
        try:
            # Get all jailed players with duration
            jailed_players = self.execute_query("""
                SELECT c.charid, c.charname, 
                       jt.value as jail_time,
                       jd.value as jail_duration
                FROM chars c
                JOIN char_vars ji ON c.charid = ji.charid AND ji.varname = 'inJail' AND ji.value > 0
                LEFT JOIN char_vars jt ON c.charid = jt.charid AND jt.varname = 'jailTime'
                LEFT JOIN char_vars jd ON c.charid = jd.charid AND jd.varname = 'jailDuration'
                WHERE jd.value IS NOT NULL AND jd.value > 0
            """)
            
            current_time = int(time.time())
            
            for player in jailed_players:
                jail_time = int(player['jail_time']) if player['jail_time'] else current_time
                jail_duration = int(player['jail_duration']) if player['jail_duration'] else 0
                
                if jail_duration > 0:
                    release_time = jail_time + (jail_duration * 60)
                    
                    if current_time >= release_time:
                        self.release_player(player['charid'], player['charname'])
            
        except Exception as e:
            self.logger.error(f"Error checking scheduled releases: {e}")
    
    def release_player(self, player_id: int, player_name: str):
        """Release a player from jail"""
        try:
            # Clear jail variables
            self.execute_query("DELETE FROM char_vars WHERE charid = %s AND varname IN ('inJail', 'jailTime', 'jailDuration', 'jailReason')", (player_id,))
            
            # Reset player position to starting area
            self.execute_query("""
                UPDATE chars 
                SET pos_zone = 230, pos_x = 0, pos_y = 0, pos_z = 0
                WHERE charid = %s
            """, (player_id,))
            
            # Log the release
            self.execute_query("""
                INSERT INTO audit_gm (date_time, gm_name, command, full_string)
                VALUES (NOW(), %s, 'pardon', %s)
            """, (self.config.gm_name, f"Auto-released {player_name} from jail"))
            
            self.logger.info(f"Auto-released player {player_name} from jail")
            
        except Exception as e:
            self.logger.error(f"Failed to release player: {e}")
    
    # ML Integration Methods
    def _fetch_historical_player_data(self) -> List[Dict]:
        """Fetch historical player data for ML training"""
        try:
            # Fetch player behavior data from the last 30 days
            historical_query = """
                SELECT c.charid, c.charname, c.pos_zone, c.pos_x, c.pos_y, c.pos_z,
                       c.hp, c.maxhp, c.mp, c.maxmp, c.mjob, c.mlvl,
                       COALESCE(cv_jail.value, 0) as jail_history,
                       COALESCE(cv_death.value, 0) as death_count,
                       UNIX_TIMESTAMP(c.last_update) as last_update_ts,
                       cs.login_time, cs.logout_time
                FROM chars c
                LEFT JOIN char_vars cv_jail ON c.charid = cv_jail.charid AND cv_jail.varname = 'jailHistory'
                LEFT JOIN char_vars cv_death ON c.charid = cv_death.charid AND cv_death.varname = 'deathCount'
                LEFT JOIN char_stats cs ON c.charid = cs.charid
                WHERE c.last_update >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                LIMIT 10000
            """
            
            return self.execute_query(historical_query)
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}")
            return []
    
    def _train_ml_models_with_data(self, historical_data: List[Dict]):
        """Train ML models with historical data"""
        if not self.ml_engine or not historical_data:
            return
        
        try:
            # Convert to pandas DataFrame for ML processing
            df = self.ml_engine.preprocess_player_data(historical_data)
            
            if len(df) > 50:  # Need sufficient data for training
                self.ml_engine.train_anomaly_detector(df)
                self.ml_engine.train_behavior_classifier(df)
                self.ml_engine.train_neural_network(df)
                
                self.logger.info(f"ML models trained with {len(df)} historical records")
            
        except Exception as e:
            self.logger.error(f"Error training ML models: {e}")
    
    def _analyze_player_with_ml(self, player_data: Dict) -> Dict[str, Any]:
        """Analyze player behavior using ML"""
        if not self.ml_engine:
            return {}
        
        try:
            # Prepare data for ML analysis
            ml_data = {
                'player_id': player_data.get('charid', 0),
                'timestamp': datetime.now(),
                'zone_id': player_data.get('pos_zone', 0),
                'pos_x': player_data.get('pos_x', 0),
                'pos_y': player_data.get('pos_y', 0),
                'pos_z': player_data.get('pos_z', 0),
                'hp_percentage': player_data.get('hp', 0) / max(player_data.get('maxhp', 1), 1),
                'mp_percentage': player_data.get('mp', 0) / max(player_data.get('maxmp', 1), 1),
                'actions_per_minute': 1.0,  # Would need to calculate from activity
                'chat_messages_per_hour': 0,  # Would need to track from chat logs
                'login_duration_minutes': 60.0,  # Would calculate from login time
                'death_count': player_data.get('death_count', 0),
                'jail_history': player_data.get('jail_history', 0),
                'gm_interactions': 0  # Would track from audit logs
            }
            
            return self.ml_engine.predict_player_behavior(ml_data)
            
        except Exception as e:
            self.logger.error(f"Error in ML analysis: {e}")
            return {}
    
    # Battle Test System Integration
    def create_gm_battle_session(self, gm_id: int, gm_name: str, zone_id: int, zone_name: str = "",
                                gm_position: tuple = (0.0, 0.0, 0.0), config_name: str = "standard_test", 
                                announcement: str = "", public_demo: bool = True) -> str:
        """Create a GM battle test session with announcement support"""
        if not self.battle_system:
            return ""
        
        try:
            session_id = self.battle_system.create_battle_test_session(
                gm_id=gm_id,
                gm_name=gm_name, 
                zone_id=zone_id,
                zone_name=zone_name,
                gm_position=gm_position,
                config_name=config_name,
                announcement=announcement,
                public_demo=public_demo
            )
            
            # Send server-wide announcement if it's a public demo
            if public_demo and session_id:
                self.send_server_announcement_for_battle_test(
                    session_id, gm_name, zone_name, config_name, announcement
                )
            
            # Log the session creation
            log_message = f"Battle test session {session_id} created for GM {gm_name}"
            if announcement:
                log_message += f" with announcement: {announcement}"
            if not public_demo:
                log_message += " (private session)"
                
            self.execute_query("""
                INSERT INTO audit_gm (date_time, gm_name, command, full_string)
                VALUES (NOW(), %s, 'battle_test', %s)
            """, (self.config.gm_name, log_message))
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error creating battle session: {e}")
            return ""
    
    def send_server_announcement_for_battle_test(self, session_id: str, gm_name: str, 
                                               zone_name: str, config_name: str, 
                                               custom_message: str = ""):
        """Send server-wide announcement for battle test sessions"""
        try:
            if not self.battle_system or session_id not in self.battle_system.active_sessions:
                return
            
            session = self.battle_system.active_sessions[session_id]
            
            # Get the full announcement from the battle system
            announcement_data = self.battle_system._send_battle_test_announcement(session, config_name)
            
            if announcement_data:
                # Log the announcement
                self.logger.info(f"Server announcement sent for battle test session {session_id}")
                
                # Store announcement in audit log
                self.execute_query("""
                    INSERT INTO audit_gm (date_time, gm_name, command, full_string)
                    VALUES (NOW(), %s, 'server_announcement', %s)
                """, (gm_name, f"Battle test announcement: {announcement_data['full_message'][:200]}..."))
                
                # This is where you would integrate with the actual server's announcement system
                # For example, sending to all connected players via the game server API
                
        except Exception as e:
            self.logger.error(f"Error sending server announcement: {e}")
    
    def update_battle_session_announcement(self, session_id: str, new_announcement: str) -> bool:
        """Update the announcement for an active battle session"""
        try:
            if not self.battle_system:
                return False
            
            result = self.battle_system.update_session_announcement(session_id, new_announcement)
            
            if result:
                self.execute_query("""
                    INSERT INTO audit_gm (date_time, gm_name, command, full_string)
                    VALUES (NOW(), %s, 'announcement_update', %s)
                """, (self.config.gm_name, f"Session {session_id} announcement updated: {new_announcement}"))
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error updating session announcement: {e}")
            return False
    
    def spawn_battle_test_mob(self, session_id: str, gm_position: tuple, 
                             mob_request: Dict = None) -> Dict[str, Any]:
        """Spawn a mob for GM battle testing"""
        if not self.battle_system:
            return {"success": False, "error": "Battle system not available"}
        
        try:
            spawn_request = mob_request or {}
            spawn_request["gm_position"] = gm_position
            
            return self.battle_system.spawn_test_mob(session_id, spawn_request)
            
        except Exception as e:
            self.logger.error(f"Error spawning battle test mob: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_player_assist_request(self, player_id: int, player_name: str,
                                   zone_id: int, position: tuple, issue_type: str,
                                   description: str, urgency: str = "normal") -> str:
        """Handle a player assistance request"""
        if not self.battle_system:
            return ""
        
        try:
            request_id = self.battle_system.create_assist_request(
                player_id, player_name, zone_id, position, issue_type, description, urgency
            )
            
            # Log the assistance request
            self.execute_query("""
                INSERT INTO audit_gm (date_time, gm_name, command, full_string)
                VALUES (NOW(), %s, 'assist_request', %s)
            """, (self.config.gm_name, f"Assist request {request_id} created for {player_name}: {description}"))
            
            # Auto-assign if demo sessions are enabled and it's a combat issue
            if (self.config.demo_sessions_enabled and 
                issue_type in ["stuck_in_combat", "mob_assistance", "combat_help"]):
                
                # Try to find an available GM or create an AI-GM session
                assign_result = self.battle_system.assign_gm_to_request(
                    request_id, self.config.gm_name, auto_spawn_for_demo=True
                )
                
                self.logger.info(f"Auto-assigned AI-GM to assist request {request_id}")
            
            return request_id
            
        except Exception as e:
            self.logger.error(f"Error handling assist request: {e}")
            return ""
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive AI-GM system status"""
        status = {
            "service_running": self.running,
            "database_connected": self.db_pool is not None,
            "incidents_tracked": len(self.incident_history),
            "ml_enabled": self.ml_engine is not None,
            "battle_test_enabled": self.battle_system is not None
        }
        
        # ML Status
        if self.ml_engine:
            status["ml_status"] = self.ml_engine.get_hardware_status()
        
        # Battle Test Status
        if self.battle_system:
            status["active_battle_sessions"] = len(self.battle_system.active_sessions)
            status["pending_assist_requests"] = len([
                r for r in self.battle_system.assist_requests.values() 
                if r.status in ["pending", "assigned"]
            ])
        
        return status
    
    async def run_monitoring_cycle(self):
        """Run one monitoring cycle with adaptive behavior based on GM availability"""
        
        # Check GM availability first to adjust behavior mode
        await self._check_gm_availability()
        
        # Monitor GM actions if in learning mode
        if self.learning_session_active:
            await self._monitor_gm_actions()
        
        # Standard monitoring
        self.monitor_player_behavior()
        self.check_scheduled_releases()
        
        # Enhanced monitoring with ML if available
        if self.ml_engine and self.config.ml_enabled:
            await self._run_ml_enhanced_monitoring()
        
        # Check for pending assist requests if battle system is available
        if self.battle_system and self.config.auto_assist_enabled:
            await self._process_pending_assist_requests()
        
        # Log current operational mode periodically
        if hasattr(self, '_last_mode_log'):
            if (datetime.now() - self._last_mode_log).total_seconds() > 600:  # Every 10 minutes
                self._log_operational_status()
        else:
            self._log_operational_status()
    
    def _log_operational_status(self):
        """Log current operational status"""
        self._last_mode_log = datetime.now()
        
        mode = "AUTONOMOUS" if self.autonomous_mode else "LEARNING"
        gm_count = len(self.online_gms)
        recent_incidents = len([i for i in self.incident_history if (datetime.now() - i.timestamp).total_seconds() < 3600])
        
        status_msg = f"AI-GM Status: {mode} mode | {gm_count} GMs online | {recent_incidents} incidents last hour"
        
        if self.learning_session_active:
            gm_actions_learned = len(self.gm_actions_history)
            status_msg += f" | Learning: {gm_actions_learned} GM actions observed"
        
        self.logger.info(status_msg)
    
    async def _run_ml_enhanced_monitoring(self):
        """Run ML-enhanced player behavior monitoring"""
        try:
            # Get current online players
            online_players = self.execute_query("""
                SELECT c.charid, c.charname, c.pos_zone, c.pos_x, c.pos_y, c.pos_z,
                       c.hp, c.maxhp, c.mp, c.maxmp, c.mjob, c.mlvl,
                       COALESCE(cv_jail.value, 0) as jail_history,
                       COALESCE(cv_death.value, 0) as death_count,
                       UNIX_TIMESTAMP(c.last_update) as last_update_ts
                FROM chars c
                LEFT JOIN char_vars cv_jail ON c.charid = cv_jail.charid AND cv_jail.varname = 'jailHistory'
                LEFT JOIN char_vars cv_death ON c.charid = cv_death.charid AND cv_death.varname = 'deathCount'
                WHERE c.last_update >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)
                LIMIT 100
            """)
            
            for player_data in online_players:
                # Run ML analysis on player
                ml_prediction = self._analyze_player_with_ml(player_data)
                
                if ml_prediction:
                    # Check for high-risk behavior
                    if ml_prediction.get('is_anomaly', False):
                        incident = PlayerIncident(
                            player_id=player_data['charid'],
                            player_name=player_data['charname'],
                            incident_type="ml_anomaly_detected",
                            severity=AIGMSeverity.WARNING,
                            description=f"ML detected anomalous behavior (score: {ml_prediction.get('anomaly_score', 0):.3f})"
                        )
                        self.report_incident(incident)
                    
                    # Check behavior classification
                    behavior_class = ml_prediction.get('behavior_class', 'normal')
                    if behavior_class in ['concerning', 'violation']:
                        severity = AIGMSeverity.MODERATE if behavior_class == 'concerning' else AIGMSeverity.SEVERE
                        incident = PlayerIncident(
                            player_id=player_data['charid'],
                            player_name=player_data['charname'],
                            incident_type="ml_behavior_classification",
                            severity=severity,
                            description=f"ML classified behavior as '{behavior_class}' (confidence: {ml_prediction.get('behavior_confidence', 0):.3f})"
                        )
                        self.report_incident(incident)
                    
                    # Learn from the interaction if learning is enabled
                    if self.config.ml_learning_enabled:
                        outcome = "normal"  # This would be determined by actual GM actions
                        self.ml_engine.learn_from_interaction(player_data, outcome)
                        
        except Exception as e:
            self.logger.error(f"Error in ML-enhanced monitoring: {e}")
    
    async def _process_pending_assist_requests(self):
        """Process pending player assistance requests"""
        try:
            if not self.battle_system:
                return
            
            pending_requests = self.battle_system.get_pending_assist_requests("emergency")
            
            for request in pending_requests:
                if request["status"] == "pending" and request["urgency"] == "emergency":
                    # Auto-assign emergency requests to AI-GM
                    assign_result = self.battle_system.assign_gm_to_request(
                        request["request_id"], 
                        self.config.gm_name,
                        auto_spawn_for_demo=True
                    )
                    
                    if assign_result.get("success", False):
                        self.logger.info(f"Auto-assigned emergency assist request {request['request_id']}")
                        
                        # Escalate to human GMs
                        self.escalate_to_gm(
                            PlayerIncident(
                                player_id=0,  # Unknown player ID from assist request
                                player_name=request["player_name"],
                                incident_type="emergency_assist_request",
                                severity=AIGMSeverity.CRITICAL,
                                description=f"Emergency assistance: {request['description']}"
                            ), 
                            3  # Escalate to GM level 3+
                        )
                        
        except Exception as e:
            self.logger.error(f"Error processing assist requests: {e}")
    
    async def _check_gm_availability(self):
        """Check for online human GMs and adjust AI-GM behavior accordingly"""
        try:
            current_time = datetime.now()
            
            # Check GM availability every 2 minutes
            if (current_time - self.gm_availability_last_check).total_seconds() < 120:
                return
            
            self.gm_availability_last_check = current_time
            
            # Query for online GMs
            online_gms = self.execute_query("""
                SELECT DISTINCT c.charid, c.charname, c.gmlevel, 
                       c.pos_zone, c.pos_x, c.pos_y, c.pos_z,
                       TIMESTAMPDIFF(MINUTE, s.last_zoneout_time, NOW()) as minutes_online
                FROM chars c
                JOIN accounts_sessions s ON c.charid = s.charid
                WHERE c.gmlevel >= %s 
                AND TIMESTAMPDIFF(MINUTE, s.last_zoneout_time, NOW()) <= 5
                ORDER BY c.gmlevel DESC, minutes_online DESC
            """, (self.config.min_gm_level_for_learning,), fetch_all=True)
            
            previous_gm_count = len(self.online_gms)
            self.online_gms = online_gms or []
            current_gm_count = len(self.online_gms)
            
            # Determine if we should be in autonomous mode
            previous_autonomous = self.autonomous_mode
            self.autonomous_mode = current_gm_count == 0
            
            # Log mode changes
            if previous_autonomous != self.autonomous_mode:
                if self.autonomous_mode:
                    self.logger.info(f"Switched to AUTONOMOUS MODE - No human GMs online (was {previous_gm_count} GMs)")
                    self.learning_session_active = False
                else:
                    self.logger.info(f"Switched to LEARNING MODE - {current_gm_count} human GMs online")
                    if self.config.gm_learning_enabled:
                        self.learning_session_active = True
                        self._start_gm_learning_session()
            
            # Log current GM status
            if current_gm_count > 0:
                gm_names = [f"{gm['charname']} (Level {gm['gmlevel']})" for gm in self.online_gms]
                self.logger.debug(f"Online GMs: {', '.join(gm_names)}")
                
        except Exception as e:
            self.logger.error(f"Error checking GM availability: {e}")
    
    def _start_gm_learning_session(self):
        """Start a new GM learning session"""
        try:
            if not self.ml_engine:
                return
            
            self.logger.info("Starting GM learning session - observing human GM actions")
            
            # Clear previous session data
            self.gm_actions_history = []
            
            # Initialize learning session in ML engine
            self.ml_engine.start_learning_session({
                'session_start': datetime.now().isoformat(),
                'online_gms': self.online_gms,
                'learning_mode': 'human_gm_observation'
            })
            
        except Exception as e:
            self.logger.error(f"Error starting GM learning session: {e}")
    
    async def _monitor_gm_actions(self):
        """Monitor and learn from human GM actions"""
        try:
            if not self.learning_session_active or not self.ml_engine:
                return
            
            # Query recent GM actions from audit table
            recent_actions = self.execute_query("""
                SELECT date_time, gm_name, command, full_string
                FROM audit_gm 
                WHERE date_time >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)
                AND gm_name != %s
                ORDER BY date_time DESC
                LIMIT 50
            """, (self.config.gm_name,), fetch_all=True)
            
            if not recent_actions:
                return
            
            # Process each GM action for learning
            for action in recent_actions:
                # Check if this action is new (not already processed)
                action_id = f"{action['date_time']}_{action['gm_name']}_{action['command']}"
                
                if not any(existing['action_id'] == action_id for existing in self.gm_actions_history):
                    gm_action_data = {
                        'action_id': action_id,
                        'timestamp': action['date_time'],
                        'gm_name': action['gm_name'],
                        'command': action['command'],
                        'full_string': action['full_string'],
                        'context': await self._get_action_context(action)
                    }
                    
                    self.gm_actions_history.append(gm_action_data)
                    
                    # Learn from this GM action
                    await self._learn_from_gm_action(gm_action_data)
            
        except Exception as e:
            self.logger.error(f"Error monitoring GM actions: {e}")
    
    async def _get_action_context(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Get context information for a GM action"""
        try:
            context = {
                'server_load': await self._get_server_load(),
                'active_incidents': len([i for i in self.incident_history if (datetime.now() - i.timestamp).total_seconds() < 3600]),
                'time_of_day': action['date_time'].strftime('%H:%M'),
                'day_of_week': action['date_time'].strftime('%A')
            }
            
            # Extract player information if available in the command
            command_str = action.get('full_string', '')
            if 'player' in command_str.lower() or any(char.isalpha() for char in command_str):
                # Try to extract player name from command
                words = command_str.split()
                for word in words:
                    if len(word) > 2 and word.isalpha():
                        player_info = self.execute_query("""
                            SELECT charid, charname, gmlevel, pos_zone, nation
                            FROM chars 
                            WHERE charname LIKE %s
                            LIMIT 1
                        """, (f"%{word}%",), fetch_one=True)
                        
                        if player_info:
                            context['target_player'] = {
                                'charid': player_info['charid'],
                                'charname': player_info['charname'],
                                'zone': player_info['pos_zone'],
                                'nation': player_info['nation']
                            }
                            break
            
            return context
            
        except Exception as e:
            self.logger.error(f"Error getting action context: {e}")
            return {}
    
    async def _get_server_load(self) -> Dict[str, Any]:
        """Get current server load metrics"""
        try:
            # Get player count
            player_count = self.execute_query("""
                SELECT COUNT(*) as count 
                FROM accounts_sessions s
                JOIN chars c ON s.charid = c.charid
                WHERE c.gmlevel = 0
            """, fetch_one=True)
            
            # Get recent incident count
            recent_incidents = len([i for i in self.incident_history if (datetime.now() - i.timestamp).total_seconds() < 1800])
            
            return {
                'player_count': player_count['count'] if player_count else 0,
                'recent_incidents': recent_incidents,
                'ai_gm_actions_last_hour': len([i for i in self.incident_history if i.auto_resolved and (datetime.now() - i.timestamp).total_seconds() < 3600])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting server load: {e}")
            return {'player_count': 0, 'recent_incidents': 0, 'ai_gm_actions_last_hour': 0}
    
    async def _learn_from_gm_action(self, gm_action: Dict[str, Any]):
        """Learn from a specific GM action"""
        try:
            if not self.ml_engine:
                return
            
            command = gm_action.get('command', '').lower()
            context = gm_action.get('context', {})
            
            # Classify the GM action type and extract learning data
            learning_data = {
                'action_type': self._classify_gm_action(command),
                'severity_handling': self._extract_severity_from_action(gm_action),
                'timing': context.get('time_of_day'),
                'server_state': context.get('server_load', {}),
                'escalation_pattern': self._analyze_escalation_pattern(gm_action),
                'outcome': 'human_gm_action'  # This is a human GM decision
            }
            
            # Feed this data to the ML engine for learning
            self.ml_engine.learn_from_gm_interaction(
                action_data=gm_action,
                context_data=context,
                learning_data=learning_data
            )
            
            self.logger.debug(f"Learned from GM action: {command} by {gm_action.get('gm_name')}")
            
        except Exception as e:
            self.logger.error(f"Error learning from GM action: {e}")
    
    def _classify_gm_action(self, command: str) -> str:
        """Classify the type of GM action"""
        if any(word in command for word in ['jail', 'ban', 'kick']):
            return 'disciplinary'
        elif any(word in command for word in ['warn', 'message', 'tell']):
            return 'communication'
        elif any(word in command for word in ['warp', 'teleport', 'goto']):
            return 'assistance'
        elif any(word in command for word in ['spawn', 'item', 'give']):
            return 'administrative'
        elif any(word in command for word in ['battle', 'test', 'demo']):
            return 'educational'
        else:
            return 'other'
    
    def _extract_severity_from_action(self, gm_action: Dict[str, Any]) -> str:
        """Extract the severity level implied by the GM action"""
        command = gm_action.get('command', '').lower()
        full_string = gm_action.get('full_string', '').lower()
        
        if any(word in command for word in ['ban', 'severe']):
            return 'severe'
        elif any(word in command for word in ['jail', 'moderate']):
            return 'moderate'
        elif any(word in command for word in ['warn', 'caution']):
            return 'warning'
        elif any(word in full_string for word in ['emergency', 'urgent', 'critical']):
            return 'critical'
        else:
            return 'info'
    
    def _analyze_escalation_pattern(self, gm_action: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the escalation pattern from the GM action"""
        return {
            'immediate_action': 'jail' in gm_action.get('command', '').lower(),
            'warning_first': 'warn' in gm_action.get('command', '').lower(),
            'escalation_level': self._determine_escalation_level(gm_action),
            'human_intervention': True
        }
    
    def _determine_escalation_level(self, gm_action: Dict[str, Any]) -> int:
        """Determine the escalation level from GM action"""
        command = gm_action.get('command', '').lower()
        
        if any(word in command for word in ['ban', 'severe']):
            return 4
        elif any(word in command for word in ['jail', 'kick']):
            return 3
        elif any(word in command for word in ['warn', 'message']):
            return 2
        else:
            return 1
    
    async def start(self):
        """Start the AI-GM service"""
        if not self.initialize():
            return False
        
        self.running = True
        self.logger.info("AI-GM Service started")
        
        while self.running:
            try:
                await self.run_monitoring_cycle()
                await asyncio.sleep(self.config.monitoring_interval_seconds)
                
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(5)  # Short pause before retrying
        
        self.logger.info("AI-GM Service stopped")
        return True
    
    def _fetch_historical_player_data(self) -> List[Dict]:
        """Fetch historical player data for ML training"""
        try:
            # Get recent player behavior data
            historical_data = self.execute_query("""
                SELECT c.charid, c.charname, c.pos_zone, c.pos_x, c.pos_y, c.pos_z,
                       c.hp, c.maxhp, c.mp, c.maxmp, c.mjob, c.mlvl,
                       COALESCE(cv_jail.value, 0) as jail_history,
                       COALESCE(cv_death.value, 0) as death_count,
                       UNIX_TIMESTAMP(c.last_update) as last_update_ts
                FROM chars c
                LEFT JOIN char_vars cv_jail ON c.charid = cv_jail.charid AND cv_jail.varname = 'jailHistory'
                LEFT JOIN char_vars cv_death ON c.charid = cv_death.charid AND cv_death.varname = 'deathCount'
                WHERE c.last_update >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                LIMIT 1000
            """, fetch_all=True)
            
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}")
            return []
    
    def _train_ml_models_with_data(self, historical_data: List[Dict]):
        """Train ML models with historical data"""
        try:
            if not self.ml_engine or not historical_data:
                return
            
            # Convert to format suitable for ML training
            training_data = []
            for player_data in historical_data:
                # Create synthetic outcomes based on historical patterns
                outcome = 'normal'
                if player_data.get('jail_history', 0) > 0:
                    outcome = 'violation'
                elif player_data.get('death_count', 0) > 10:
                    outcome = 'concerning'
                
                training_example = {
                    **player_data,
                    'outcome': outcome
                }
                training_data.append(training_example)
            
            # Train models
            self.ml_engine.train_models(training_data)
            self.logger.info(f"Trained ML models with {len(training_data)} historical examples")
            
        except Exception as e:
            self.logger.error(f"Error training ML models: {e}")
    
    def _analyze_player_with_ml(self, player_data: Dict) -> Optional[Dict]:
        """Analyze a player using ML models"""
        try:
            if not self.ml_engine:
                return None
            
            return self.ml_engine.predict_player_behavior(player_data)
            
        except Exception as e:
            self.logger.error(f"Error analyzing player with ML: {e}")
            return None
    
    def stop(self):
        """Stop the AI-GM service"""
        self.running = False

def main():
    """Main entry point for AI-GM service"""
    config = AIGMConfig()
    
    # Load configuration from environment variables if available
    config.db_host = os.environ.get('FFXI_SQL_HOST', config.db_host)
    config.db_port = int(os.environ.get('FFXI_SQL_PORT', config.db_port))
    config.db_user = os.environ.get('FFXI_SQL_LOGIN', config.db_user)
    config.db_password = os.environ.get('FFXI_SQL_PASSWORD', config.db_password)
    config.db_name = os.environ.get('FFXI_SQL_DATABASE', config.db_name)
    config.api_secret_key = os.environ.get('FFXI_API_SECRET_KEY', config.api_secret_key)
    
    ai_gm = AIGMService(config)
    
    try:
        asyncio.run(ai_gm.start())
    except KeyboardInterrupt:
        print("\nShutting down AI-GM service...")
        ai_gm.stop()

if __name__ == "__main__":
    main()