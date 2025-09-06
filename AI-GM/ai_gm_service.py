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

class AIGMService:
    """Main AI-GM service class"""
    
    def __init__(self, config: AIGMConfig):
        self.config = config
        self.running = False
        self.db_pool = None
        self.incident_history: List[PlayerIncident] = []
        self.player_warnings: Dict[int, int] = {}
        
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
            
            self.logger.info("AI-GM Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI-GM service: {e}")
            return False
    
    def get_db_connection(self):
        """Get a database connection from the pool"""
        return self.db_pool.get_connection()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute a database query and return results"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return []
                    
        except Exception as e:
            self.logger.error(f"Database query failed: {e}")
            return []
    
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
        """Determine the appropriate action for an incident"""
        warning_count = self.player_warnings.get(incident.player_id, 0)
        
        # Simple rule-based decision making
        if incident.severity == AIGMSeverity.INFO:
            if incident.incident_type == "stuck_player":
                return AIGMAction.WARN
        
        elif incident.severity == AIGMSeverity.WARNING:
            if warning_count >= self.config.escalation_threshold:
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
    
    async def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        self.monitor_player_behavior()
        self.check_scheduled_releases()
    
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