#!/usr/bin/env python3
"""
AI-GM Streaming Integration
Automatically triggers streaming when GM demonstrations or significant events occur

Features:
- Automatic stream activation for GM battle demonstrations
- Integration with battle test system for live streaming
- Smart scene composition and camera control
- Real-time event detection and streaming coordination
"""

import os
import sys
import asyncio
import logging
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

# Add AI-GM path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'AI-GM'))

# Import streaming components
from ffxi_streaming_service import FFXIStreamingService, StreamingEvent
from ffxi_renderer import FFXIRenderer, RenderObject, Camera

# Import AI-GM components
try:
    from battle_test_system import GMBattleTestSystem, BattleTestSession, PlayerAssistRequest
    BATTLE_SYSTEM_AVAILABLE = True
except ImportError:
    BATTLE_SYSTEM_AVAILABLE = False

try:
    from ai_gm_service import AIGMService, AIGMSeverity
    AI_GM_AVAILABLE = True
except ImportError:
    AI_GM_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StreamingTrigger:
    """Configuration for automatic streaming triggers"""
    trigger_type: str  # gm_demo, battle_test, assistance, announcement
    enabled: bool = True
    auto_platforms: List[str] = None
    min_duration: int = 60  # Minimum seconds before stopping
    announcement_text: str = ""
    zone_filter: List[int] = None

class AIGMStreamingIntegration:
    """Integration between AI-GM system and streaming service"""
    
    def __init__(self, streaming_service: FFXIStreamingService):
        self.streaming_service = streaming_service
        self.triggers: Dict[str, StreamingTrigger] = {}
        self.active_integrations: Dict[str, Any] = {}
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Load default triggers
        self.setup_default_triggers()
        
    def setup_default_triggers(self):
        """Setup default streaming triggers"""
        self.triggers = {
            "gm_battle_demo": StreamingTrigger(
                trigger_type="gm_demo",
                enabled=True,
                auto_platforms=["youtube", "twitch"],
                min_duration=120,
                announcement_text="🎬 GM Battle Demonstration starting! Live stream available.",
                zone_filter=None  # All zones
            ),
            "player_assistance": StreamingTrigger(
                trigger_type="assistance",
                enabled=True,
                auto_platforms=["youtube"],
                min_duration=60,
                announcement_text="📚 GM providing player assistance - Educational stream active.",
                zone_filter=[230, 231, 232]  # Starting cities only
            ),
            "special_events": StreamingTrigger(
                trigger_type="announcement",
                enabled=True,
                auto_platforms=["youtube", "twitch", "facebook"],
                min_duration=300,
                announcement_text="🎪 Special server event in progress! Watch live!",
                zone_filter=None
            ),
            "combat_demonstration": StreamingTrigger(
                trigger_type="battle_test",
                enabled=True,
                auto_platforms=["youtube", "twitch"],
                min_duration=180,
                announcement_text="⚔️ Combat mechanics demonstration - Perfect for learning!",
                zone_filter=None
            )
        }
        
    async def start_monitoring(self):
        """Start monitoring for streaming triggers"""
        if self.monitoring_active:
            logger.warning("Streaming integration monitoring already active")
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("✅ AI-GM Streaming Integration monitoring started")
        
    async def stop_monitoring(self):
        """Stop monitoring for streaming triggers"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
            
        # Stop any active integrations
        for integration_id in list(self.active_integrations.keys()):
            await self.stop_integration(integration_id)
            
        logger.info("AI-GM Streaming Integration monitoring stopped")
        
    def _monitoring_loop(self):
        """Main monitoring loop for streaming triggers"""
        check_interval = 5.0  # Check every 5 seconds
        
        while self.monitoring_active:
            try:
                # Check for GM battle demonstrations
                if BATTLE_SYSTEM_AVAILABLE:
                    self._check_battle_demonstrations()
                    
                # Check for AI-GM activities
                if AI_GM_AVAILABLE:
                    self._check_aigm_activities()
                    
                # Check for server announcements
                self._check_server_announcements()
                
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error in streaming integration monitoring: {e}")
                time.sleep(check_interval)
                
    def _check_battle_demonstrations(self):
        """Check for active GM battle demonstrations"""
        try:
            # This would integrate with the actual battle test system
            # For now, simulate detection
            
            # Check for active battle test sessions
            # if battle_system.has_active_demonstrations():
            #     for session in battle_system.get_active_sessions():
            #         self._handle_battle_demonstration(session)
            
            pass
            
        except Exception as e:
            logger.error(f"Error checking battle demonstrations: {e}")
            
    def _check_aigm_activities(self):
        """Check for AI-GM activities that should trigger streaming"""
        try:
            # Monitor AI-GM service for significant activities
            # This would check the AI-GM service for:
            # - Player assistance sessions
            # - Educational demonstrations
            # - Special interventions
            
            pass
            
        except Exception as e:
            logger.error(f"Error checking AI-GM activities: {e}")
            
    def _check_server_announcements(self):
        """Check for server announcements that should trigger streaming"""
        try:
            # Monitor for server-wide announcements that indicate
            # special events worth streaming
            
            pass
            
        except Exception as e:
            logger.error(f"Error checking server announcements: {e}")
            
    async def handle_gm_demonstration_start(self, gm_name: str, zone_id: int, 
                                          demo_type: str, description: str) -> Optional[str]:
        """Handle the start of a GM demonstration"""
        try:
            trigger = self.triggers.get("gm_battle_demo")
            if not trigger or not trigger.enabled:
                logger.info("GM demonstration streaming trigger disabled")
                return None
                
            # Check zone filter
            if trigger.zone_filter and zone_id not in trigger.zone_filter:
                logger.info(f"Zone {zone_id} not in streaming filter")
                return None
                
            # Create streaming event
            event = StreamingEvent(
                event_type="gm_demonstration",
                event_id=f"gm_demo_{gm_name}_{int(time.time())}",
                title=f"GM {gm_name} - {demo_type} Demonstration",
                description=f"{description} | Zone: {zone_id} | Educational content for players",
                zone_id=zone_id,
                gm_name=gm_name,
                platforms=trigger.auto_platforms or ["youtube"]
            )
            
            # Start streaming
            success = await self.streaming_service.start_event_stream(event)
            if success:
                # Setup camera for demonstration
                await self._setup_demonstration_camera(zone_id, gm_name)
                
                # Store integration info
                self.active_integrations[event.event_id] = {
                    "event": event,
                    "started_at": datetime.now(),
                    "trigger": trigger,
                    "gm_name": gm_name,
                    "zone_id": zone_id
                }
                
                # Send announcement if configured
                if trigger.announcement_text:
                    await self._send_server_announcement(trigger.announcement_text, zone_id)
                    
                logger.info(f"✅ Started streaming for GM demonstration: {event.title}")
                return event.event_id
            else:
                logger.error(f"Failed to start streaming for GM demonstration")
                return None
                
        except Exception as e:
            logger.error(f"Error handling GM demonstration start: {e}")
            return None
            
    async def handle_player_assistance_start(self, player_name: str, gm_name: str, 
                                           zone_id: int, assistance_type: str) -> Optional[str]:
        """Handle the start of player assistance that should be streamed"""
        try:
            trigger = self.triggers.get("player_assistance")
            if not trigger or not trigger.enabled:
                return None
                
            # Check if this type of assistance should be streamed
            educational_types = ["combat_help", "job_demonstration", "mechanic_explanation"]
            if assistance_type not in educational_types:
                return None
                
            # Check zone filter
            if trigger.zone_filter and zone_id not in trigger.zone_filter:
                return None
                
            # Create streaming event
            event = StreamingEvent(
                event_type="player_assistance",
                event_id=f"assist_{player_name}_{int(time.time())}",
                title=f"Player Assistance - {assistance_type}",
                description=f"GM {gm_name} helping {player_name} with {assistance_type}",
                zone_id=zone_id,
                gm_name=gm_name,
                platforms=trigger.auto_platforms or ["youtube"]
            )
            
            # Start streaming
            success = await self.streaming_service.start_event_stream(event)
            if success:
                # Setup camera for assistance
                await self._setup_assistance_camera(zone_id, player_name, gm_name)
                
                self.active_integrations[event.event_id] = {
                    "event": event,
                    "started_at": datetime.now(),
                    "trigger": trigger,
                    "player_name": player_name,
                    "gm_name": gm_name,
                    "zone_id": zone_id
                }
                
                logger.info(f"✅ Started streaming for player assistance: {event.title}")
                return event.event_id
            else:
                logger.error(f"Failed to start streaming for player assistance")
                return None
                
        except Exception as e:
            logger.error(f"Error handling player assistance start: {e}")
            return None
            
    async def handle_special_event_start(self, event_name: str, zone_id: int, 
                                       event_description: str) -> Optional[str]:
        """Handle the start of a special server event"""
        try:
            trigger = self.triggers.get("special_events")
            if not trigger or not trigger.enabled:
                return None
                
            # Create streaming event
            event = StreamingEvent(
                event_type="special_event",
                event_id=f"event_{event_name}_{int(time.time())}",
                title=f"Special Event - {event_name}",
                description=event_description,
                zone_id=zone_id,
                gm_name="Server",
                platforms=trigger.auto_platforms or ["youtube", "twitch"]
            )
            
            # Start streaming
            success = await self.streaming_service.start_event_stream(event)
            if success:
                # Setup camera for event
                await self._setup_event_camera(zone_id, event_name)
                
                self.active_integrations[event.event_id] = {
                    "event": event,
                    "started_at": datetime.now(),
                    "trigger": trigger,
                    "event_name": event_name,
                    "zone_id": zone_id
                }
                
                # Send server-wide announcement
                if trigger.announcement_text:
                    await self._send_server_announcement(trigger.announcement_text)
                    
                logger.info(f"✅ Started streaming for special event: {event.title}")
                return event.event_id
            else:
                logger.error(f"Failed to start streaming for special event")
                return None
                
        except Exception as e:
            logger.error(f"Error handling special event start: {e}")
            return None
            
    async def stop_integration(self, integration_id: str):
        """Stop a specific streaming integration"""
        try:
            if integration_id not in self.active_integrations:
                logger.warning(f"Integration {integration_id} not found")
                return
                
            integration = self.active_integrations[integration_id]
            event = integration["event"]
            
            # Check minimum duration
            elapsed = datetime.now() - integration["started_at"]
            min_duration = timedelta(seconds=integration["trigger"].min_duration)
            
            if elapsed < min_duration:
                logger.info(f"Integration {integration_id} hasn't reached minimum duration yet")
                return
                
            # Stop streaming
            await self.streaming_service.stop_event_stream(event.event_id)
            
            # Remove from active integrations
            del self.active_integrations[integration_id]
            
            logger.info(f"✅ Stopped streaming integration: {integration_id}")
            
        except Exception as e:
            logger.error(f"Error stopping integration {integration_id}: {e}")
            
    async def _setup_demonstration_camera(self, zone_id: int, gm_name: str):
        """Setup camera for GM demonstration"""
        try:
            if not self.streaming_service.renderer:
                return
                
            # Position camera for optimal demonstration viewing
            # This would use actual player positions from the database
            camera_position = (10.0, 8.0, 15.0)  # Behind and above
            target_position = (0.0, 2.0, 0.0)    # Focus on demonstration area
            
            self.streaming_service.renderer.update_camera(
                position=camera_position,
                target=target_position
            )
            
            logger.info(f"Camera positioned for GM {gm_name} demonstration")
            
        except Exception as e:
            logger.error(f"Error setting up demonstration camera: {e}")
            
    async def _setup_assistance_camera(self, zone_id: int, player_name: str, gm_name: str):
        """Setup camera for player assistance"""
        try:
            if not self.streaming_service.renderer:
                return
                
            # Position camera for assistance viewing
            camera_position = (5.0, 6.0, 8.0)
            target_position = (0.0, 1.5, 0.0)
            
            self.streaming_service.renderer.update_camera(
                position=camera_position,
                target=target_position
            )
            
            logger.info(f"Camera positioned for {gm_name} assisting {player_name}")
            
        except Exception as e:
            logger.error(f"Error setting up assistance camera: {e}")
            
    async def _setup_event_camera(self, zone_id: int, event_name: str):
        """Setup camera for special event"""
        try:
            if not self.streaming_service.renderer:
                return
                
            # Position camera for event coverage
            camera_position = (15.0, 12.0, 20.0)  # Wide angle for events
            target_position = (0.0, 3.0, 0.0)
            
            self.streaming_service.renderer.update_camera(
                position=camera_position,
                target=target_position
            )
            
            logger.info(f"Camera positioned for special event: {event_name}")
            
        except Exception as e:
            logger.error(f"Error setting up event camera: {e}")
            
    async def _send_server_announcement(self, message: str, zone_id: Optional[int] = None):
        """Send server announcement about streaming"""
        try:
            # This would integrate with the server's announcement system
            # For now, log the announcement
            
            scope = f"Zone {zone_id}" if zone_id else "Server-wide"
            logger.info(f"[{scope} Announcement] {message}")
            
            # In a real implementation, this would call the server's
            # announcement system to notify players
            
        except Exception as e:
            logger.error(f"Error sending server announcement: {e}")
            
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        return {
            "monitoring_active": self.monitoring_active,
            "active_integrations": len(self.active_integrations),
            "enabled_triggers": sum(1 for trigger in self.triggers.values() if trigger.enabled),
            "triggers": {
                name: {
                    "enabled": trigger.enabled,
                    "platforms": trigger.auto_platforms,
                    "min_duration": trigger.min_duration
                }
                for name, trigger in self.triggers.items()
            },
            "integrations": {
                int_id: {
                    "event_type": integration["event"].event_type,
                    "title": integration["event"].title,
                    "started_at": integration["started_at"].isoformat(),
                    "zone_id": integration.get("zone_id"),
                    "gm_name": integration.get("gm_name")
                }
                for int_id, integration in self.active_integrations.items()
            }
        }

# Example usage functions for AI-GM system integration
async def integrate_with_aigm_service(streaming_service: FFXIStreamingService):
    """Example integration with AI-GM service"""
    integration = AIGMStreamingIntegration(streaming_service)
    await integration.start_monitoring()
    
    # Example: Simulate GM demonstration
    demo_id = await integration.handle_gm_demonstration_start(
        gm_name="GameMaster1",
        zone_id=230,
        demo_type="Combat Mechanics",
        description="Demonstrating advanced combat techniques for new players"
    )
    
    if demo_id:
        logger.info(f"Demo streaming started with ID: {demo_id}")
        
        # Simulate demo duration
        await asyncio.sleep(10)
        
        # Stop the demo
        await integration.stop_integration(demo_id)
        
    await integration.stop_monitoring()

def main():
    """Test the AI-GM streaming integration"""
    async def test_integration():
        # This would normally use an actual streaming service
        streaming_service = FFXIStreamingService()
        await streaming_service.initialize()
        await streaming_service.start_service()
        
        try:
            await integrate_with_aigm_service(streaming_service)
        finally:
            await streaming_service.stop_service()
            
    asyncio.run(test_integration())
    return 0

if __name__ == "__main__":
    sys.exit(main())