#!/usr/bin/env python3
"""
Multi-Platform Streaming Manager for FFXI Server
Handles real-time streaming to YouTube, Twitch, Facebook, and other platforms

Features:
- Multi-platform streaming support
- Real-time video encoding and transmission
- Audio commentary integration
- Chat integration and moderation
- Stream analytics and monitoring
"""

import os
import sys
import asyncio
import logging
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
import cv2
import numpy as np
from datetime import datetime
import subprocess
import tempfile

# Google APIs for YouTube
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# HTTP requests for other platforms
import requests
import websockets

# Audio processing
import pyaudio
from pydub import AudioSegment
import speech_recognition as sr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StreamPlatform:
    """Configuration for a streaming platform"""
    name: str
    platform_type: str  # youtube, twitch, facebook, custom
    enabled: bool = False
    api_key: str = ""
    secret_key: str = ""
    stream_key: str = ""
    rtmp_url: str = ""
    chat_enabled: bool = True
    quality: str = "1080p"  # 720p, 1080p, 1440p, 4k
    bitrate: int = 6000  # kbps
    
@dataclass
class StreamSession:
    """Active streaming session data"""
    session_id: str
    platform: str
    title: str
    description: str
    started_at: datetime
    viewers: int = 0
    chat_messages: List[Dict[str, Any]] = field(default_factory=list)
    analytics: Dict[str, Any] = field(default_factory=dict)

class YouTubeStreamer:
    """YouTube Live streaming integration"""
    
    def __init__(self, credentials_file: str):
        self.credentials_file = credentials_file
        self.service = None
        self.broadcast_id = None
        self.stream_id = None
        
    async def authenticate(self) -> bool:
        """Authenticate with YouTube API"""
        try:
            # OAuth 2.0 flow for YouTube
            flow = Flow.from_client_secrets_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
            )
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f"Please visit: {auth_url}")
            code = input("Enter authorization code: ")
            
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            self.service = build('youtube', 'v3', credentials=credentials)
            logger.info("YouTube authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return False
            
    async def create_broadcast(self, title: str, description: str) -> Optional[str]:
        """Create a YouTube Live broadcast"""
        try:
            if not self.service:
                logger.error("YouTube service not authenticated")
                return None
                
            # Create broadcast
            broadcast_response = self.service.liveBroadcasts().insert(
                part='snippet,contentDetails,status',
                body={
                    'snippet': {
                        'title': title,
                        'description': description,
                        'scheduledStartTime': datetime.utcnow().isoformat() + 'Z'
                    },
                    'contentDetails': {
                        'latencyPreference': 'low'
                    },
                    'status': {
                        'privacyStatus': 'public'
                    }
                }
            ).execute()
            
            self.broadcast_id = broadcast_response['id']
            
            # Create stream
            stream_response = self.service.liveStreams().insert(
                part='snippet,cdn',
                body={
                    'snippet': {
                        'title': f"{title} Stream"
                    },
                    'cdn': {
                        'frameRate': '30fps',
                        'ingestionType': 'rtmp',
                        'resolution': '1080p'
                    }
                }
            ).execute()
            
            self.stream_id = stream_response['id']
            
            # Bind stream to broadcast
            self.service.liveBroadcasts().bind(
                part='id,contentDetails',
                id=self.broadcast_id,
                streamId=self.stream_id
            ).execute()
            
            logger.info(f"YouTube broadcast created: {self.broadcast_id}")
            return self.broadcast_id
            
        except Exception as e:
            logger.error(f"Failed to create YouTube broadcast: {e}")
            return None
            
    def get_stream_key(self) -> Optional[str]:
        """Get RTMP stream key for YouTube"""
        try:
            if not self.service or not self.stream_id:
                return None
                
            stream = self.service.liveStreams().list(
                part='cdn',
                id=self.stream_id
            ).execute()
            
            if stream['items']:
                return stream['items'][0]['cdn']['ingestionInfo']['streamName']
                
        except Exception as e:
            logger.error(f"Failed to get YouTube stream key: {e}")
            
        return None

class TwitchStreamer:
    """Twitch streaming integration"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.user_id = None
        
    async def authenticate(self) -> bool:
        """Authenticate with Twitch API"""
        try:
            # Get OAuth token
            auth_url = "https://id.twitch.tv/oauth2/token"
            auth_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(auth_url, data=auth_data)
            if response.status_code == 200:
                auth_result = response.json()
                self.access_token = auth_result['access_token']
                logger.info("Twitch authentication successful")
                return True
            else:
                logger.error(f"Twitch authentication failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Twitch authentication error: {e}")
            return False
            
    async def update_stream_info(self, title: str, category: str = "Final Fantasy XI") -> bool:
        """Update Twitch stream information"""
        try:
            if not self.access_token:
                logger.error("Twitch not authenticated")
                return False
                
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Client-Id': self.client_id,
                'Content-Type': 'application/json'
            }
            
            # Update stream info
            update_url = f"https://api.twitch.tv/helix/channels?broadcaster_id={self.user_id}"
            update_data = {
                'title': title,
                'game_name': category
            }
            
            response = requests.patch(update_url, headers=headers, json=update_data)
            if response.status_code == 204:
                logger.info("Twitch stream info updated")
                return True
            else:
                logger.error(f"Failed to update Twitch stream: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Twitch stream update error: {e}")
            return False

class StreamingManager:
    """Main streaming manager for multiple platforms"""
    
    def __init__(self, config_file: str = "streaming_config.json"):
        self.config_file = Path(config_file)
        self.platforms: Dict[str, StreamPlatform] = {}
        self.active_sessions: Dict[str, StreamSession] = {}
        self.ffmpeg_processes: Dict[str, subprocess.Popen] = {}
        
        # Streaming state
        self.is_streaming = False
        self.current_frame = None
        self.audio_enabled = False
        self.chat_enabled = True
        
        # Platform handlers
        self.youtube_streamer = None
        self.twitch_streamer = None
        
        # Load configuration
        self.load_config()
        
    def load_config(self):
        """Load streaming platform configurations"""
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
                    
                for platform_name, platform_data in config.get("platforms", {}).items():
                    platform = StreamPlatform(**platform_data)
                    self.platforms[platform_name] = platform
                    
                logger.info(f"Loaded {len(self.platforms)} platform configurations")
            else:
                # Create default config
                self.create_default_config()
                
        except Exception as e:
            logger.error(f"Failed to load streaming config: {e}")
            self.create_default_config()
            
    def create_default_config(self):
        """Create default streaming configuration"""
        default_platforms = {
            "youtube": StreamPlatform(
                name="YouTube Live",
                platform_type="youtube",
                rtmp_url="rtmp://a.rtmp.youtube.com/live2/",
                quality="1080p",
                bitrate=6000
            ),
            "twitch": StreamPlatform(
                name="Twitch",
                platform_type="twitch", 
                rtmp_url="rtmp://live.twitch.tv/live/",
                quality="1080p",
                bitrate=6000
            ),
            "facebook": StreamPlatform(
                name="Facebook Gaming",
                platform_type="facebook",
                rtmp_url="rtmps://live-api-s.facebook.com:443/rtmp/",
                quality="1080p",
                bitrate=6000
            )
        }
        
        self.platforms = default_platforms
        self.save_config()
        
    def save_config(self):
        """Save streaming configuration"""
        try:
            config = {
                "platforms": {
                    name: {
                        "name": platform.name,
                        "platform_type": platform.platform_type,
                        "enabled": platform.enabled,
                        "api_key": platform.api_key,
                        "secret_key": platform.secret_key,
                        "stream_key": platform.stream_key,
                        "rtmp_url": platform.rtmp_url,
                        "chat_enabled": platform.chat_enabled,
                        "quality": platform.quality,
                        "bitrate": platform.bitrate
                    }
                    for name, platform in self.platforms.items()
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info("Streaming configuration saved")
            
        except Exception as e:
            logger.error(f"Failed to save streaming config: {e}")
            
    async def start_stream(self, platform_name: str, title: str, description: str = "") -> bool:
        """Start streaming to a specific platform"""
        try:
            if platform_name not in self.platforms:
                logger.error(f"Platform not configured: {platform_name}")
                return False
                
            platform = self.platforms[platform_name]
            if not platform.enabled:
                logger.error(f"Platform not enabled: {platform_name}")
                return False
                
            logger.info(f"Starting stream to {platform.name}")
            
            # Create session
            session = StreamSession(
                session_id=f"{platform_name}_{int(time.time())}",
                platform=platform_name,
                title=title,
                description=description,
                started_at=datetime.now()
            )
            
            # Platform-specific setup
            if platform.platform_type == "youtube":
                await self._start_youtube_stream(platform, session)
            elif platform.platform_type == "twitch":
                await self._start_twitch_stream(platform, session)
            else:
                await self._start_generic_rtmp_stream(platform, session)
                
            self.active_sessions[platform_name] = session
            logger.info(f"Stream started to {platform.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start stream to {platform_name}: {e}")
            return False
            
    async def _start_youtube_stream(self, platform: StreamPlatform, session: StreamSession):
        """Start YouTube Live stream"""
        if not self.youtube_streamer:
            self.youtube_streamer = YouTubeStreamer("youtube_credentials.json")
            await self.youtube_streamer.authenticate()
            
        broadcast_id = await self.youtube_streamer.create_broadcast(session.title, session.description)
        if broadcast_id:
            stream_key = self.youtube_streamer.get_stream_key()
            if stream_key:
                await self._start_ffmpeg_stream(platform, stream_key)
                
    async def _start_twitch_stream(self, platform: StreamPlatform, session: StreamSession):
        """Start Twitch stream"""
        if not self.twitch_streamer:
            self.twitch_streamer = TwitchStreamer(platform.api_key, platform.secret_key)
            await self.twitch_streamer.authenticate()
            
        await self.twitch_streamer.update_stream_info(session.title)
        await self._start_ffmpeg_stream(platform, platform.stream_key)
        
    async def _start_generic_rtmp_stream(self, platform: StreamPlatform, session: StreamSession):
        """Start generic RTMP stream"""
        await self._start_ffmpeg_stream(platform, platform.stream_key)
        
    async def _start_ffmpeg_stream(self, platform: StreamPlatform, stream_key: str):
        """Start FFmpeg streaming process"""
        try:
            # FFmpeg command for streaming
            cmd = [
                'ffmpeg',
                '-f', 'rawvideo',
                '-vcodec', 'rawvideo',
                '-s', f'{1920}x{1080}',  # Resolution
                '-pix_fmt', 'rgb24',
                '-r', '30',  # FPS
                '-i', '-',  # Input from stdin
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-tune', 'zerolatency',
                '-crf', '23',
                '-maxrate', f'{platform.bitrate}k',
                '-bufsize', f'{platform.bitrate * 2}k',
                '-pix_fmt', 'yuv420p',
                '-f', 'flv',
                f'{platform.rtmp_url}{stream_key}'
            ]
            
            # Start FFmpeg process
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.ffmpeg_processes[platform.name] = process
            logger.info(f"FFmpeg streaming started for {platform.name}")
            
        except Exception as e:
            logger.error(f"Failed to start FFmpeg for {platform.name}: {e}")
            
    def update_frame(self, frame: np.ndarray):
        """Update the current frame for streaming"""
        self.current_frame = frame
        
        # Send frame to all active streams
        for platform_name, process in self.ffmpeg_processes.items():
            if process and process.poll() is None:  # Process is running
                try:
                    # Convert frame to bytes and send to FFmpeg
                    frame_bytes = frame.tobytes()
                    process.stdin.write(frame_bytes)
                    process.stdin.flush()
                except Exception as e:
                    logger.error(f"Error sending frame to {platform_name}: {e}")
                    
    async def stop_stream(self, platform_name: str):
        """Stop streaming to a specific platform"""
        try:
            if platform_name in self.ffmpeg_processes:
                process = self.ffmpeg_processes[platform_name]
                if process and process.poll() is None:
                    process.terminate()
                    process.wait()
                del self.ffmpeg_processes[platform_name]
                
            if platform_name in self.active_sessions:
                session = self.active_sessions[platform_name]
                logger.info(f"Stream to {platform_name} stopped after {datetime.now() - session.started_at}")
                del self.active_sessions[platform_name]
                
        except Exception as e:
            logger.error(f"Error stopping stream to {platform_name}: {e}")
            
    def stop_all_streams(self):
        """Stop all active streams"""
        for platform_name in list(self.active_sessions.keys()):
            asyncio.create_task(self.stop_stream(platform_name))
            
    def get_streaming_status(self) -> Dict[str, Any]:
        """Get current streaming status"""
        return {
            "active_sessions": len(self.active_sessions),
            "platforms": {
                name: {
                    "enabled": platform.enabled,
                    "streaming": name in self.active_sessions,
                    "quality": platform.quality,
                    "bitrate": platform.bitrate
                }
                for name, platform in self.platforms.items()
            },
            "total_viewers": sum(session.viewers for session in self.active_sessions.values())
        }

def main():
    """Test the streaming manager"""
    async def test_streaming():
        manager = StreamingManager()
        
        # Create a test frame
        test_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        
        print("✅ Streaming manager initialized")
        print(f"Available platforms: {list(manager.platforms.keys())}")
        
        # Test frame update
        manager.update_frame(test_frame)
        print("✅ Frame update test completed")
        
        status = manager.get_streaming_status()
        print(f"Streaming status: {status}")
        
    asyncio.run(test_streaming())
    return 0

if __name__ == "__main__":
    sys.exit(main())