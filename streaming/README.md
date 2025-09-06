# FFXI Real-time Streaming System

## Overview
Comprehensive real-time streaming system for FFXI server that provides live video streaming of GM demonstrations, server events, and player interactions to multiple platforms including YouTube, Twitch, Facebook Gaming, and custom RTMP endpoints.

## Architecture

### Core Components

1. **FFXI Asset Extractor** (`ffxi_asset_extractor.py`)
   - Extracts textures, models, and zone data from FFXI DAT files
   - Supports compressed DAT file formats (LZ4, zstandard)
   - Provides demo assets for testing when FFXI files unavailable

2. **3D Renderer** (`ffxi_renderer.py`)
   - OpenGL-based real-time 3D rendering engine
   - Renders FFXI zones, characters, and mobs in real-time
   - Supports dynamic camera positioning and scene updates
   - Provides frame buffers for streaming encoding

3. **Streaming Manager** (`streaming_manager.py`)
   - Multi-platform streaming support (YouTube, Twitch, Facebook, custom RTMP)
   - FFmpeg integration for video encoding and transmission
   - Platform-specific API integrations for authentication and metadata
   - Real-time stream monitoring and analytics

4. **Main Streaming Service** (`ffxi_streaming_service.py`)
   - Orchestrates all streaming components
   - Database integration for real-time player/mob tracking
   - Event-driven streaming activation
   - Performance monitoring and optimization

5. **Dashboard API** (`streaming_dashboard_api.py`)
   - FastAPI-based web service for streaming management
   - RESTful API for platform configuration and control
   - WebSocket support for real-time status updates
   - Integration with admin dashboard

6. **AI-GM Integration** (`aigm_streaming_integration.py`)
   - Automatic streaming triggers for GM demonstrations
   - Integration with battle test system
   - Smart camera positioning and scene composition
   - Event detection and streaming coordination

## Features

### Real-time 3D Rendering
- **Asset Extraction**: Automatic extraction of FFXI game assets for rendering
- **3D Visualization**: Real-time OpenGL rendering of zones, characters, and combat
- **Dynamic Camera**: Intelligent camera positioning based on events and activities
- **Performance Optimization**: Efficient rendering pipeline with 30+ FPS capability

### Multi-Platform Streaming
- **YouTube Live**: Full integration with YouTube Live API for broadcasts
- **Twitch**: Native Twitch API integration with chat and analytics
- **Facebook Gaming**: Direct streaming to Facebook Gaming platform
- **Custom RTMP**: Support for any RTMP-compatible streaming service
- **Simultaneous Streaming**: Stream to multiple platforms simultaneously

### Automatic Event Detection
- **GM Demonstrations**: Automatic detection and streaming of GM battle tests
- **Player Assistance**: Educational streams when GMs help players
- **Server Events**: Automatic streaming of special server events
- **Combat Analysis**: Real-time combat visualization and analysis

### Admin Dashboard Integration
- **Platform Management**: Configure streaming platforms and credentials
- **Real-time Monitoring**: Live status of all streaming activities
- **Analytics Dashboard**: Viewer statistics and performance metrics
- **Event Control**: Manual control of streaming events and demonstrations

## Installation

### Prerequisites
```bash
# System dependencies
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-pip python3.12-dev
sudo apt-get install -y ffmpeg libmariadb-dev-compat libmariadb-dev
sudo apt-get install -y libgl1-mesa-dev libglu1-mesa-dev
```

### Python Dependencies
```bash
cd streaming/
pip install -r requirements.txt
```

### FFXI Assets (Optional)
```bash
# Extract FFXI assets for enhanced rendering
python ffxi_asset_extractor.py --ffxi-path /path/to/ffxi --output-path extracted_assets --quick

# Or generate demo assets for testing
python ffxi_asset_extractor.py --output-path extracted_assets --demo
```

## Configuration

### Database Configuration
Set environment variables for database connection:
```bash
export FFXI_SQL_HOST="localhost"
export FFXI_SQL_DATABASE="xidb"
export FFXI_SQL_USER="ffxi"
export FFXI_SQL_PASSWORD="password"
export FFXI_SQL_PORT="3306"
```

### Streaming Platform Setup

#### YouTube Live
1. Create OAuth 2.0 credentials in Google Cloud Console
2. Download `youtube_credentials.json`
3. Configure in admin dashboard with API keys

#### Twitch
1. Register application on Twitch Developer Console
2. Obtain Client ID and Client Secret
3. Configure stream key in admin dashboard

#### Facebook Gaming
1. Create Facebook app with Gaming permissions
2. Generate stream key from Facebook Creator Studio
3. Configure RTMP endpoint and stream key

### Configuration Files
The system automatically generates configuration files:
- `streaming_config.json` - Platform configurations
- `streaming_service_config.json` - Service settings
- `ffxi_demo_assets.json` - Demo asset data

## Usage

### Starting the Streaming Service
```bash
# Start the main streaming service
python ffxi_streaming_service.py

# Start the dashboard API (separate terminal)
python streaming_dashboard_api.py
```

### Admin Dashboard Integration
Access streaming controls through the admin dashboard:
1. Navigate to admin dashboard (`http://localhost/admin.html`)
2. Click on "🎥 Streaming" tab
3. Configure platforms and start streams

### API Endpoints
- `GET /api/streaming/status` - Get streaming status
- `GET /api/streaming/platforms` - List configured platforms
- `POST /api/streaming/start` - Start streaming to platform
- `POST /api/streaming/event` - Start event-based streaming
- `GET /api/streaming/analytics` - Get streaming analytics
- `WebSocket /ws/streaming` - Real-time status updates

### Manual Streaming Control
```bash
# Start stream to YouTube with custom title
curl -X POST "http://localhost:8888/api/streaming/start" \
  -H "Content-Type: application/json" \
  -d '{"platform": "youtube", "title": "FFXI Server Live", "description": "Live gameplay"}'

# Start event stream for GM demonstration
curl -X POST "http://localhost:8888/api/streaming/event" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "gm_demonstration",
    "title": "Combat Mechanics Demo",
    "description": "GM demonstrating advanced combat",
    "zone_id": 230,
    "gm_name": "GameMaster1",
    "platforms": ["youtube", "twitch"]
  }'
```

## AI-GM Integration

### Automatic Streaming Triggers
The system automatically starts streaming when:
- GM begins battle demonstration
- GM provides educational player assistance
- Special server events are announced
- Combat mechanics are being demonstrated

### Integration Setup
```python
from aigm_streaming_integration import AIGMStreamingIntegration

# Initialize integration
integration = AIGMStreamingIntegration(streaming_service)
await integration.start_monitoring()

# Trigger streams programmatically
demo_id = await integration.handle_gm_demonstration_start(
    gm_name="GameMaster1",
    zone_id=230,
    demo_type="Combat Mechanics",
    description="Advanced combat demonstration"
)
```

## Performance Optimization

### System Requirements
- **CPU**: Multi-core processor (4+ cores recommended)
- **GPU**: OpenGL 3.3+ compatible graphics card
- **RAM**: 8GB+ recommended for 1080p streaming
- **Network**: Stable upload bandwidth (10+ Mbps for 1080p)

### Optimization Settings
```json
{
  "renderer": {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "quality": "balanced"
  },
  "streaming": {
    "bitrate": 6000,
    "preset": "ultrafast",
    "crf": 23
  }
}
```

## Monitoring and Analytics

### Real-time Metrics
- Active stream count and viewer statistics
- Renderer performance (FPS, frame time)
- Network usage and stream health
- Platform-specific analytics

### Performance Monitoring
```bash
# Get current streaming status
curl http://localhost:8888/api/streaming/status

# Get detailed analytics
curl http://localhost:8888/api/streaming/analytics
```

## Security Considerations

### API Security
- All API endpoints require authentication tokens
- Streaming credentials stored securely
- Database access controlled through connection pooling

### Stream Security
- RTMP streams use secure connections (RTMPS) when available
- Platform OAuth tokens refreshed automatically
- Stream keys protected and not logged

## Troubleshooting

### Common Issues

#### OpenGL Initialization Fails
```bash
# Install OpenGL development packages
sudo apt-get install -y mesa-utils libgl1-mesa-dev
export DISPLAY=:0.0  # If running headless
```

#### FFmpeg Encoding Errors
```bash
# Verify FFmpeg installation
ffmpeg -version
# Ensure codec support
ffmpeg -codecs | grep h264
```

#### Database Connection Issues
```bash
# Test database connectivity
mysql -h localhost -u ffxi -p xidb -e "SELECT 1"
```

#### Streaming Platform Authentication
- Verify API credentials are correct and not expired
- Check platform-specific rate limits and quotas
- Ensure OAuth tokens have required permissions

### Debug Mode
Enable debug logging for troubleshooting:
```bash
export STREAMING_LOG_LEVEL=DEBUG
python ffxi_streaming_service.py
```

## Development

### Adding New Platforms
1. Extend `StreamPlatform` class with platform-specific settings
2. Implement authentication in `streaming_manager.py`
3. Add platform-specific API integration
4. Update admin dashboard with new platform controls

### Custom Rendering Features
1. Extend `FFXIRenderer` class with new rendering capabilities
2. Add asset processing in `ffxi_asset_extractor.py`
3. Implement scene composition in streaming service
4. Update camera control in AI-GM integration

### API Extensions
1. Add new endpoints in `streaming_dashboard_api.py`
2. Implement corresponding frontend controls
3. Update WebSocket messaging for real-time updates
4. Add appropriate authentication and validation

## License
This streaming system is part of the FFXI Server project and follows the same licensing terms.

## Contributing
Contributions are welcome! Please:
1. Follow existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure compatibility with existing AI-GM system