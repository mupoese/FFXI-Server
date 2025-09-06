#!/usr/bin/env python3
"""
Streaming Dashboard API for Admin Interface
FastAPI-based web service for managing streaming platforms and configurations

Features:
- Platform configuration management
- Real-time streaming status
- Stream control (start/stop)
- Analytics and monitoring
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json

# FastAPI and web components
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Import streaming service
from ffxi_streaming_service import FFXIStreamingService, StreamingEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class PlatformConfig(BaseModel):
    name: str
    platform_type: str
    enabled: bool = False
    api_key: str = ""
    secret_key: str = ""
    stream_key: str = ""
    rtmp_url: str = ""
    chat_enabled: bool = True
    quality: str = "1080p"
    bitrate: int = 6000

class StreamRequest(BaseModel):
    platform: str
    title: str
    description: str = ""
    auto_announce: bool = True

class EventStreamRequest(BaseModel):
    event_type: str
    title: str
    description: str = ""
    zone_id: int
    gm_name: str = ""
    platforms: List[str] = []

# FastAPI app
app = FastAPI(
    title="FFXI Streaming Dashboard API",
    description="API for managing FFXI real-time streaming",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global streaming service instance
streaming_service: Optional[FFXIStreamingService] = None
active_websockets: List[WebSocket] = []

@app.on_event("startup")
async def startup_event():
    """Initialize streaming service on startup"""
    global streaming_service
    try:
        streaming_service = FFXIStreamingService()
        if await streaming_service.initialize():
            await streaming_service.start_service()
            logger.info("✅ Streaming service initialized and started")
        else:
            logger.error("❌ Failed to initialize streaming service")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global streaming_service
    if streaming_service:
        await streaming_service.stop_service()
        logger.info("Streaming service stopped")

# API Endpoints

@app.get("/api/streaming/status")
async def get_streaming_status():
    """Get current streaming status"""
    if not streaming_service:
        raise HTTPException(status_code=503, detail="Streaming service not available")
        
    try:
        status = streaming_service.get_streaming_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Error getting streaming status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/streaming/platforms")
async def get_platforms():
    """Get configured streaming platforms"""
    if not streaming_service or not streaming_service.streaming_manager:
        raise HTTPException(status_code=503, detail="Streaming service not available")
        
    try:
        platforms = {}
        for name, platform in streaming_service.streaming_manager.platforms.items():
            platforms[name] = {
                "name": platform.name,
                "platform_type": platform.platform_type,
                "enabled": platform.enabled,
                "quality": platform.quality,
                "bitrate": platform.bitrate,
                "chat_enabled": platform.chat_enabled
            }
        return JSONResponse(content={"platforms": platforms})
    except Exception as e:
        logger.error(f"Error getting platforms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/streaming/platforms/{platform_name}")
async def update_platform_config(platform_name: str, config: PlatformConfig):
    """Update platform configuration"""
    if not streaming_service or not streaming_service.streaming_manager:
        raise HTTPException(status_code=503, detail="Streaming service not available")
        
    try:
        from streaming_manager import StreamPlatform
        
        platform = StreamPlatform(
            name=config.name,
            platform_type=config.platform_type,
            enabled=config.enabled,
            api_key=config.api_key,
            secret_key=config.secret_key,
            stream_key=config.stream_key,
            rtmp_url=config.rtmp_url,
            chat_enabled=config.chat_enabled,
            quality=config.quality,
            bitrate=config.bitrate
        )
        
        streaming_service.streaming_manager.platforms[platform_name] = platform
        streaming_service.streaming_manager.save_config()
        
        return JSONResponse(content={"success": True, "message": f"Platform {platform_name} updated"})
        
    except Exception as e:
        logger.error(f"Error updating platform {platform_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/streaming/start")
async def start_stream(request: StreamRequest, background_tasks: BackgroundTasks):
    """Start streaming to a platform"""
    if not streaming_service or not streaming_service.streaming_manager:
        raise HTTPException(status_code=503, detail="Streaming service not available")
        
    try:
        success = await streaming_service.streaming_manager.start_stream(
            request.platform,
            request.title,
            request.description
        )
        
        if success:
            # Broadcast update to connected websockets
            background_tasks.add_task(broadcast_status_update)
            return JSONResponse(content={"success": True, "message": f"Stream started on {request.platform}"})
        else:
            raise HTTPException(status_code=400, detail=f"Failed to start stream on {request.platform}")
            
    except Exception as e:
        logger.error(f"Error starting stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/streaming/stop/{platform_name}")
async def stop_stream(platform_name: str, background_tasks: BackgroundTasks):
    """Stop streaming to a platform"""
    if not streaming_service or not streaming_service.streaming_manager:
        raise HTTPException(status_code=503, detail="Streaming service not available")
        
    try:
        await streaming_service.streaming_manager.stop_stream(platform_name)
        
        # Broadcast update to connected websockets
        background_tasks.add_task(broadcast_status_update)
        return JSONResponse(content={"success": True, "message": f"Stream stopped on {platform_name}"})
        
    except Exception as e:
        logger.error(f"Error stopping stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/streaming/event")
async def start_event_stream(request: EventStreamRequest, background_tasks: BackgroundTasks):
    """Start streaming for a specific event"""
    if not streaming_service:
        raise HTTPException(status_code=503, detail="Streaming service not available")
        
    try:
        event = StreamingEvent(
            event_type=request.event_type,
            event_id=f"{request.event_type}_{int(datetime.now().timestamp())}",
            title=request.title,
            description=request.description,
            zone_id=request.zone_id,
            gm_name=request.gm_name,
            platforms=request.platforms or ["youtube", "twitch"]
        )
        
        success = await streaming_service.start_event_stream(event)
        
        if success:
            background_tasks.add_task(broadcast_status_update)
            return JSONResponse(content={
                "success": True, 
                "event_id": event.event_id,
                "message": f"Event stream started: {request.title}"
            })
        else:
            raise HTTPException(status_code=400, detail="Failed to start event stream")
            
    except Exception as e:
        logger.error(f"Error starting event stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/streaming/event/{event_id}")
async def stop_event_stream(event_id: str, background_tasks: BackgroundTasks):
    """Stop streaming for a specific event"""
    if not streaming_service:
        raise HTTPException(status_code=503, detail="Streaming service not available")
        
    try:
        await streaming_service.stop_event_stream(event_id)
        
        background_tasks.add_task(broadcast_status_update)
        return JSONResponse(content={"success": True, "message": f"Event stream stopped: {event_id}"})
        
    except Exception as e:
        logger.error(f"Error stopping event stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/streaming/analytics")
async def get_streaming_analytics():
    """Get streaming analytics and statistics"""
    if not streaming_service:
        raise HTTPException(status_code=503, detail="Streaming service not available")
        
    try:
        # Get current status
        status = streaming_service.get_streaming_status()
        
        # Add analytics data
        analytics = {
            "current_status": status,
            "session_stats": {
                "active_sessions": len(streaming_service.current_events) if hasattr(streaming_service, 'current_events') else 0,
                "total_platforms": len(status.get("platforms", {})),
                "enabled_platforms": sum(1 for p in status.get("platforms", {}).values() if p.get("enabled", False))
            },
            "performance": {
                "renderer_fps": status.get("renderer_fps", 0),
                "tracked_objects": status.get("tracked_players", 0) + status.get("tracked_mobs", 0)
            }
        }
        
        return JSONResponse(content=analytics)
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
@app.websocket("/ws/streaming")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time streaming updates"""
    await websocket.accept()
    active_websockets.append(websocket)
    
    try:
        while True:
            # Send periodic status updates
            if streaming_service:
                status = streaming_service.get_streaming_status()
                await websocket.send_json({
                    "type": "status_update",
                    "data": status,
                    "timestamp": datetime.now().isoformat()
                })
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_websockets:
            active_websockets.remove(websocket)

async def broadcast_status_update():
    """Broadcast status update to all connected WebSocket clients"""
    if not streaming_service:
        return
        
    try:
        status = streaming_service.get_streaming_status()
        message = {
            "type": "status_update",
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to all connected clients
        disconnected = []
        for websocket in active_websockets:
            try:
                await websocket.send_json(message)
            except:
                disconnected.append(websocket)
                
        # Remove disconnected clients
        for websocket in disconnected:
            active_websockets.remove(websocket)
            
    except Exception as e:
        logger.error(f"Error broadcasting status update: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = "healthy" if streaming_service and streaming_service.is_active else "unhealthy"
    return JSONResponse(content={"status": status, "timestamp": datetime.now().isoformat()})

# API documentation endpoint
@app.get("/", response_class=HTMLResponse)
async def api_documentation():
    """API documentation page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FFXI Streaming API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
            .header { background: #4a90e2; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
            .endpoint { background: #2d2d2d; padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #27ae60; }
            .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
            .get { background: #27ae60; }
            .post { background: #3498db; }
            .delete { background: #e74c3c; }
            code { background: #444; padding: 2px 6px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎥 FFXI Real-time Streaming API</h1>
            <p>API for managing multi-platform streaming of FFXI server events and GM demonstrations</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/api/streaming/status</strong>
            <p>Get current streaming service status and statistics</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/api/streaming/platforms</strong>
            <p>Get configured streaming platforms (YouTube, Twitch, Facebook, etc.)</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <strong>/api/streaming/platforms/{platform_name}</strong>
            <p>Update platform configuration with API keys and settings</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <strong>/api/streaming/start</strong>
            <p>Start streaming to a specific platform</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <strong>/api/streaming/stop/{platform_name}</strong>
            <p>Stop streaming to a specific platform</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <strong>/api/streaming/event</strong>
            <p>Start streaming for a specific event (GM demo, battle test, etc.)</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/api/streaming/analytics</strong>
            <p>Get streaming analytics and performance metrics</p>
        </div>
        
        <div class="endpoint">
            <span class="method">WS</span>
            <strong>/ws/streaming</strong>
            <p>WebSocket endpoint for real-time streaming status updates</p>
        </div>
        
        <p style="margin-top: 30px; color: #888;">
            📚 Full API documentation: <a href="/docs" style="color: #4a90e2;">/docs</a> | 
            📊 Interactive API: <a href="/redoc" style="color: #4a90e2;">/redoc</a>
        </p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def main():
    """Run the streaming dashboard API"""
    print("🎥 Starting FFXI Streaming Dashboard API...")
    
    uvicorn.run(
        "streaming_dashboard_api:app",
        host="0.0.0.0",
        port=8888,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()