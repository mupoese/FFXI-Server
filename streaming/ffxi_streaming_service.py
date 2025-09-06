#!/usr/bin/env python3
"""
FFXI Real-time Streaming Service
Integrates with AI-GM system to provide live streaming of GM demonstrations and server events

Features:
- Real-time 3D rendering of FFXI game state
- Multi-platform streaming (YouTube, Twitch, Facebook, etc.)
- Automatic GM demonstration capture
- Server event streaming
- Admin dashboard integration
"""

import os
import sys
import asyncio
import logging
import threading
import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
from datetime import datetime
import mysql.connector
from mysql.connector import pooling

# Add the AI-GM directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'AI-GM'))

# Import streaming components
from ffxi_renderer import FFXIRenderer, RenderObject, Camera
from streaming_manager import StreamingManager, StreamSession
from ffxi_asset_extractor import FFXIAssetExtractor

# Import AI-GM components
try:
    from battle_test_system import GMBattleTestSystem, BattleTestSession
    BATTLE_SYSTEM_AVAILABLE = True
except ImportError:
    BATTLE_SYSTEM_AVAILABLE = False
    print("Warning: Battle test system not available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PlayerPosition:
    """Player position and state for rendering"""
    char_id: int
    char_name: str
    zone_id: int
    pos_x: float
    pos_y: float
    pos_z: float
    pos_rot: float
    job_id: int
    level: int
    hp_percent: float
    mp_percent: float
    in_combat: bool = False
    animation_state: str = "idle"

@dataclass
class MobPosition:
    """Mob position and state for rendering"""
    mob_id: int
    mob_name: str
    zone_id: int
    pos_x: float
    pos_y: float
    pos_z: float
    pos_rot: float
    family_id: int
    level: int
    hp_percent: float
    in_combat: bool = False
    animation_state: str = "idle"

@dataclass
class StreamingEvent:
    """Events that trigger streaming"""
    event_type: str  # gm_demo, battle_test, server_event
    event_id: str
    title: str
    description: str
    zone_id: int
    gm_name: str = ""
    auto_stream: bool = True
    platforms: List[str] = field(default_factory=list)

class FFXIStreamingService:
    """Main streaming service for FFXI server"""
    
    def __init__(self, config_file: str = "streaming_service_config.json"):
        self.config_file = Path(config_file)
        self.config = {}
        
        # Core components
        self.renderer: Optional[FFXIRenderer] = None
        self.streaming_manager: Optional[StreamingManager] = None
        self.asset_extractor: Optional[FFXIAssetExtractor] = None
        
        # Database connection
        self.db_pool = None
        self.db_config = {}
        
        # Streaming state
        self.is_active = False
        self.auto_streaming = True
        self.current_events: Dict[str, StreamingEvent] = {}
        self.monitored_zones: List[int] = []
        
        # Player and mob tracking
        self.tracked_players: Dict[int, PlayerPosition] = {}
        self.tracked_mobs: Dict[int, MobPosition] = {}
        
        # Service threads
        self.update_thread: Optional[threading.Thread] = None
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Load configuration
        self.load_config()
        
    def load_config(self):
        """Load streaming service configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    self.config = json.load(f)
            else:
                self.create_default_config()
                
            # Extract database config
            self.db_config = self.config.get("database", {})
            
            # Extract streaming settings
            self.auto_streaming = self.config.get("auto_streaming", True)
            self.monitored_zones = self.config.get("monitored_zones", [])
            
            logger.info("Streaming service configuration loaded")
            
        except Exception as e:
            logger.error(f"Failed to load streaming config: {e}")
            self.create_default_config()
            
    def create_default_config(self):
        """Create default streaming service configuration"""
        self.config = {
            "database": {
                "host": os.getenv("FFXI_SQL_HOST", "localhost"),
                "database": os.getenv("FFXI_SQL_DATABASE", "xidb"),
                "user": os.getenv("FFXI_SQL_USER", "ffxi"),
                "password": os.getenv("FFXI_SQL_PASSWORD", "password"),
                "port": int(os.getenv("FFXI_SQL_PORT", "3306"))
            },
            "renderer": {
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "assets_path": "extracted_assets"
            },
            "streaming": {
                "auto_streaming": True,
                "default_platforms": ["youtube", "twitch"],
                "quality": "1080p",
                "bitrate": 6000
            },
            "monitoring": {
                "update_interval": 1.0,  # seconds
                "zone_monitoring": True,
                "combat_detection": True,
                "gm_tracking": True
            },
            "monitored_zones": [
                230, 231, 232,  # Starting cities
                1, 2, 3,        # Nation areas
                50, 51, 52      # Popular leveling zones
            ],
            "demo_triggers": {
                "gm_battle_test": True,
                "player_assistance": True,
                "server_announcements": True,
                "special_events": True
            }
        }
        
        self.save_config()
        
    def save_config(self):
        """Save streaming service configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info("Streaming service configuration saved")
        except Exception as e:
            logger.error(f"Failed to save streaming config: {e}")
            
    async def initialize(self) -> bool:
        """Initialize all streaming service components"""
        try:
            logger.info("Initializing FFXI Streaming Service")
            
            # Initialize database connection
            if not await self.initialize_database():
                logger.error("Failed to initialize database connection")
                return False
                
            # Initialize asset extractor
            assets_path = self.config.get("renderer", {}).get("assets_path", "extracted_assets")
            self.asset_extractor = FFXIAssetExtractor("/demo/ffxi", assets_path)
            
            # Extract demo assets if needed
            if not Path(assets_path).exists():
                logger.info("Extracting demo assets...")
                self.asset_extractor.extract_common_assets()
                
            # Initialize renderer
            renderer_config = self.config.get("renderer", {})
            self.renderer = FFXIRenderer(
                width=renderer_config.get("width", 1920),
                height=renderer_config.get("height", 1080),
                assets_path=assets_path
            )
            
            if not self.renderer.initialize_opengl():
                logger.error("Failed to initialize OpenGL renderer")
                return False
                
            if not self.renderer.load_assets():
                logger.error("Failed to load rendering assets")
                return False
                
            # Initialize streaming manager
            self.streaming_manager = StreamingManager("streaming_config.json")
            
            # Create demo scene
            self.renderer.create_demo_scene()
            
            logger.info("✅ FFXI Streaming Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize streaming service: {e}")
            return False
            
    async def initialize_database(self) -> bool:
        """Initialize database connection pool"""
        try:
            pool_config = {
                'pool_name': 'ffxi_streaming_pool',
                'pool_size': 5,
                'pool_reset_session': True,
                **self.db_config
            }
            
            self.db_pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
            
            # Test connection
            connection = self.db_pool.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            connection.close()
            
            logger.info("Database connection pool initialized")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
            
    async def start_service(self):
        """Start the streaming service"""
        if self.is_active:
            logger.warning("Streaming service already active")
            return
            
        self.is_active = True
        
        # Start renderer
        self.renderer.start_render_loop()
        
        # Start monitoring threads
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        
        self.update_thread.start()
        self.monitor_thread.start()
        
        logger.info("✅ FFXI Streaming Service started")
        
    async def stop_service(self):
        """Stop the streaming service"""
        self.is_active = False
        
        # Stop all streams
        if self.streaming_manager:
            self.streaming_manager.stop_all_streams()
            
        # Stop renderer
        if self.renderer:
            self.renderer.stop_render_loop()
            
        # Wait for threads to finish
        if self.update_thread:
            self.update_thread.join(timeout=5.0)
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
            
        logger.info("FFXI Streaming Service stopped")
        
    def _update_loop(self):
        """Main update loop for real-time data"""
        update_interval = self.config.get("monitoring", {}).get("update_interval", 1.0)
        
        while self.is_active:
            try:
                # Update player and mob positions
                self._update_player_positions()
                self._update_mob_positions()
                
                # Update renderer with current game state
                self._update_renderer_scene()
                
                # Update streaming frames
                if self.renderer and self.streaming_manager:
                    frame = self.renderer.get_current_frame()
                    if frame is not None:
                        self.streaming_manager.update_frame(frame)
                        
                time.sleep(update_interval)
                
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                time.sleep(1.0)
                
    def _monitor_loop(self):
        """Monitor for streaming events"""
        monitor_interval = 5.0  # Check every 5 seconds
        
        while self.is_active:
            try:
                # Check for GM battle demonstrations
                self._check_gm_demonstrations()
                
                # Check for player assistance requests
                self._check_player_assistance()
                
                # Check for server announcements
                self._check_server_announcements()
                
                time.sleep(monitor_interval)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(5.0)
                
    def _update_player_positions(self):
        """Update tracked player positions from database"""
        try:
            if not self.db_pool:
                return
                
            connection = self.db_pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Query online players in monitored zones
            query = """
            SELECT 
                c.charid, c.charname, c.pos_zone as zone_id,
                c.pos_x, c.pos_y, c.pos_z, c.pos_rot,
                c.mjob as job_id, c.mlvl as level,
                (c.hp / c.maxhp * 100) as hp_percent,
                (c.mp / c.maxmp * 100) as mp_percent
            FROM chars c
            JOIN accounts_sessions s ON c.charid = s.charid
            WHERE c.pos_zone IN ({})
            AND TIMESTAMPDIFF(MINUTE, s.last_zoneout_time, NOW()) <= 5
            """.format(','.join(map(str, self.monitored_zones)) if self.monitored_zones else '0')
            
            cursor.execute(query)
            players = cursor.fetchall()
            
            # Update tracked players
            for player_data in players:
                char_id = player_data['charid']
                
                player = PlayerPosition(
                    char_id=char_id,
                    char_name=player_data['charname'],
                    zone_id=player_data['zone_id'],
                    pos_x=float(player_data['pos_x']),
                    pos_y=float(player_data['pos_y']),
                    pos_z=float(player_data['pos_z']),
                    pos_rot=float(player_data['pos_rot']),
                    job_id=player_data['job_id'],
                    level=player_data['level'],
                    hp_percent=float(player_data['hp_percent']),
                    mp_percent=float(player_data['mp_percent'])
                )
                
                self.tracked_players[char_id] = player
                
            cursor.close()
            connection.close()
            
        except Exception as e:
            logger.error(f"Error updating player positions: {e}")
            
    def _update_mob_positions(self):
        """Update tracked mob positions from database"""
        try:
            if not self.db_pool:
                return
                
            connection = self.db_pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Query active mobs in monitored zones
            query = """
            SELECT 
                m.mobid, m.mobname, m.zoneid as zone_id,
                m.pos_x, m.pos_y, m.pos_z, m.pos_rot,
                m.familyid as family_id, m.mlvl as level,
                (m.hp / m.maxhp * 100) as hp_percent
            FROM mob_spawn_points m
            WHERE m.zoneid IN ({})
            AND m.spawned = 1
            """.format(','.join(map(str, self.monitored_zones)) if self.monitored_zones else '0')
            
            cursor.execute(query)
            mobs = cursor.fetchall()
            
            # Update tracked mobs
            for mob_data in mobs:
                mob_id = mob_data['mobid']
                
                mob = MobPosition(
                    mob_id=mob_id,
                    mob_name=mob_data['mobname'],
                    zone_id=mob_data['zone_id'],
                    pos_x=float(mob_data['pos_x']),
                    pos_y=float(mob_data['pos_y']),
                    pos_z=float(mob_data['pos_z']),
                    pos_rot=float(mob_data['pos_rot']),
                    family_id=mob_data['family_id'],
                    level=mob_data['level'],
                    hp_percent=float(mob_data['hp_percent'])
                )
                
                self.tracked_mobs[mob_id] = mob
                
            cursor.close()
            connection.close()
            
        except Exception as e:
            logger.error(f"Error updating mob positions: {e}")
            
    def _update_renderer_scene(self):
        """Update 3D renderer with current game state"""
        try:
            if not self.renderer:
                return
                
            # Update player objects
            for player in self.tracked_players.values():
                obj_id = f"player_{player.char_id}"
                
                # Create or update render object
                render_obj = RenderObject(
                    position=(player.pos_x, player.pos_y, player.pos_z),
                    rotation=(0.0, player.pos_rot, 0.0),
                    scale=(1.0, 2.0, 1.0),
                    model_name="character",
                    texture_name="character",
                    animation_state=player.animation_state
                )
                
                self.renderer.add_render_object(obj_id, render_obj)
                
            # Update mob objects
            for mob in self.tracked_mobs.values():
                obj_id = f"mob_{mob.mob_id}"
                
                render_obj = RenderObject(
                    position=(mob.pos_x, mob.pos_y, mob.pos_z),
                    rotation=(0.0, mob.pos_rot, 0.0),
                    scale=(0.8, 1.5, 0.8),
                    model_name="character",
                    texture_name="mob",
                    animation_state=mob.animation_state
                )
                
                self.renderer.add_render_object(obj_id, render_obj)
                
        except Exception as e:
            logger.error(f"Error updating renderer scene: {e}")
            
    def _check_gm_demonstrations(self):
        """Check for active GM battle demonstrations"""
        try:
            if not BATTLE_SYSTEM_AVAILABLE:
                return
                
            # This would integrate with the battle test system
            # to detect when GMs start demonstrations
            
            # For now, simulate demonstration detection
            
        except Exception as e:
            logger.error(f"Error checking GM demonstrations: {e}")
            
    def _check_player_assistance(self):
        """Check for player assistance requests that should be streamed"""
        try:
            # Check for player assistance events
            # This would monitor the AI-GM service for assistance requests
            pass
            
        except Exception as e:
            logger.error(f"Error checking player assistance: {e}")
            
    def _check_server_announcements(self):
        """Check for server announcements that should trigger streaming"""
        try:
            # Monitor for server-wide announcements
            # That indicate special events worth streaming
            pass
            
        except Exception as e:
            logger.error(f"Error checking server announcements: {e}")
            
    async def start_event_stream(self, event: StreamingEvent) -> bool:
        """Start streaming for a specific event"""
        try:
            logger.info(f"Starting stream for event: {event.title}")
            
            platforms = event.platforms or self.config.get("streaming", {}).get("default_platforms", ["youtube"])
            
            success = True
            for platform in platforms:
                platform_success = await self.streaming_manager.start_stream(
                    platform, 
                    event.title, 
                    event.description
                )
                success = success and platform_success
                
            if success:
                self.current_events[event.event_id] = event
                logger.info(f"✅ Event stream started: {event.title}")
            else:
                logger.error(f"❌ Failed to start event stream: {event.title}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error starting event stream: {e}")
            return False
            
    async def stop_event_stream(self, event_id: str):
        """Stop streaming for a specific event"""
        try:
            if event_id in self.current_events:
                event = self.current_events[event_id]
                
                for platform in event.platforms:
                    await self.streaming_manager.stop_stream(platform)
                    
                del self.current_events[event_id]
                logger.info(f"Event stream stopped: {event.title}")
                
        except Exception as e:
            logger.error(f"Error stopping event stream: {e}")
            
    def get_streaming_status(self) -> Dict[str, Any]:
        """Get current streaming service status"""
        status = {
            "service_active": self.is_active,
            "renderer_active": self.renderer is not None and self.renderer.is_initialized,
            "auto_streaming": self.auto_streaming,
            "tracked_players": len(self.tracked_players),
            "tracked_mobs": len(self.tracked_mobs),
            "active_events": len(self.current_events),
            "monitored_zones": len(self.monitored_zones)
        }
        
        if self.streaming_manager:
            streaming_status = self.streaming_manager.get_streaming_status()
            status.update(streaming_status)
            
        if self.renderer:
            status["renderer_fps"] = self.renderer.fps
            
        return status

async def main():
    """Main entry point for streaming service"""
    service = FFXIStreamingService()
    
    if not await service.initialize():
        print("❌ Failed to initialize streaming service")
        return 1
        
    try:
        await service.start_service()
        
        print("✅ FFXI Streaming Service running")
        print("Press Ctrl+C to stop...")
        
        # Keep service running
        while True:
            status = service.get_streaming_status()
            print(f"Status: {status['tracked_players']} players, {status['tracked_mobs']} mobs tracked")
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🔄 Stopping streaming service...")
        
    finally:
        await service.stop_service()
        print("✅ Streaming service stopped")
        
    return 0

if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))