# PlayOnline Server Integration Guide

## Overview

This guide details the comprehensive PlayOnline integration features that have been added to the FFXI server, providing enhanced client file management, automatic updates, and multi-language support based on the original Square Enix PlayOnline architecture.

## New Features

### 1. Enhanced Web Interface

The main web interface (`web/index.html`) has been enhanced with:

- **PlayOnline Integration Status**: Real-time monitoring of client update system
- **Client Update Management**: Direct access to client file validation and updates
- **Multi-Language Support Display**: Shows supported languages (EN, DE, FR, US)
- **File Statistics**: Displays 2,469 tracked files from original PlayOnline manifests

### 2. Extended API Endpoints

New API endpoints in `web/api/app.py`:

#### Client Manifest Management
- `GET /api/playonline/manifest/<version>` - Get client file manifest
- `POST /api/playonline/validate` - Validate client files against server manifest
- `GET /api/playonline/file/<file_hash>` - Serve individual files for updates

#### Update Management
- `GET /api/playonline/updates/available` - Check for available client updates
- `GET /api/playonline/downloads/stats` - Get download statistics
- `GET /api/playonline/languages` - Get supported languages and localization

### 3. Client Update Manager

New tool `tools/client_update_manager.py` provides:

- **Manifest Import**: Import PlayOnline manifests to server database
- **Client Validation**: Comprehensive client file integrity checking
- **Update Package Generation**: Create optimized update packages
- **Statistics Reporting**: Detailed download and usage analytics
- **Cleanup Operations**: Automated maintenance of download records

### 4. Content Delivery System

New module `tools/playonline_content_delivery.py` offers:

- **Enhanced File Validation**: Deep integrity checking with security analysis
- **Optimized Downloads**: Prioritized download sequences (critical → important → standard → optional)
- **Compression Support**: Bandwidth optimization with compression
- **Caching System**: Intelligent content caching for performance
- **Multi-Language Filtering**: Language-specific content delivery

## Database Integration

The PlayOnline integration uses the existing database schema from `sql/playonline_integration.sql`:

### Core Tables

```sql
-- Client file manifest (2,469 files from PlayOnline)
client_manifest (
    file_id, file_hash, file_path, file_size, 
    file_category, file_extension, version_id
)

-- Version tracking  
client_versions (
    version_id, version_name, total_files, 
    total_size_bytes, release_date, is_active
)

-- Download tracking for bandwidth management
client_file_downloads (
    download_id, file_hash, player_id, 
    download_start, bytes_downloaded, client_ip
)

-- Update request management
client_update_requests (
    request_id, player_id, client_version,
    request_status, files_updated, bytes_transferred
)
```

## Usage Examples

### 1. Import PlayOnline Manifests

```bash
# Import original PlayOnline manifest data to server database
python tools/client_update_manager.py --import-manifest --version 1.18.15e

# Output: Successfully imported 2,469 manifest entries for version 1.18.15e
```

### 2. Validate Client Installation

```bash
# Create client file list (example format)
echo '[
    {"hash": "abc123", "path": "pol.exe", "size": 1691648},
    {"hash": "def456", "path": "app.dll", "size": 4335104}
]' > client_files.json

# Validate against server manifest
python tools/client_update_manager.py --validate-client client_files.json

# Output:
# Validation Status: needs_update
# Valid Files: 1,245
# Missing Files: 1,224  
# Corrupted Files: 0
# Update Priority: critical
```

### 3. Generate Update Package

```bash
# Generate optimized update package for missing files
python tools/client_update_manager.py --generate-update missing_files.json --language EN

# Output:
# Update Package Generated:
# Language: EN
# Total Files: 1,224
# Total Size: 485.3 MB
# Estimated Download Time: 8m 15s
```

### 4. API Usage Examples

#### Check Client Updates
```bash
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:5000/api/playonline/updates/available?version=1.18.15e&language=EN"
```

#### Validate Client Files
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"files": [{"hash": "abc123", "path": "pol.exe", "size": 1691648}], "version": "1.18.15e"}' \
     "http://localhost:5000/api/playonline/validate"
```

#### Get Download Statistics
```bash
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:5000/api/playonline/downloads/stats"
```

## Configuration

### Environment Variables

```bash
# PlayOnline content delivery settings
export FFXI_PLAYONLINE_CONTENT_PATH="/opt/ffxi/client_content"
export FFXI_PLAYONLINE_ENABLE_COMPRESSION="true"
export FFXI_PLAYONLINE_MAX_BANDWIDTH_MBPS="100"
export FFXI_PLAYONLINE_CONCURRENT_DOWNLOADS="10"
export FFXI_PLAYONLINE_CACHE_DURATION_HOURS="24"
```

### Content Directory Structure

```
/opt/ffxi/client_content/
├── graphics/           # 1,548 graphics files (PNG, ANG)
├── audio/             # 434 audio files (SPW, BGW)  
├── database/          # 128 database files (PFB, PIB)
├── executable/        # 34 system files (EXE, DLL)
├── data/             # Configuration and data files
├── documentation/     # Help files and documentation
├── patches/          # Patch files and updates
├── languages/
│   ├── EN/           # English localization
│   ├── DE/           # German localization
│   ├── FR/           # French localization
│   └── US/           # US English localization
├── temp/             # Temporary download files
└── cache/            # Cached content for performance
```

## Performance Optimization

### 1. Download Prioritization

Files are downloaded in optimized sequence:

1. **Critical** (Priority 1): Executables and essential system files
2. **Important** (Priority 2): Core game data and configuration
3. **Standard** (Priority 3): Graphics and user interface elements
4. **Optional** (Priority 4): Audio content and documentation

### 2. Bandwidth Management

- **Compression**: Reduces download size by ~30% (enabled by default)
- **Concurrent Downloads**: Configurable (default: 10 simultaneous)
- **Rate Limiting**: Bandwidth cap to prevent server overload
- **Resume Support**: Interrupted downloads can be resumed

### 3. Caching Strategy

- **Executables**: Cached indefinitely (critical files)
- **Graphics**: Cached for 24 hours (frequently accessed)
- **Audio**: Cached on-demand (large files)
- **Documentation**: Cached for 7 days (rarely changed)

## Multi-Language Support

### Supported Languages

- **EN**: English (default)
- **DE**: German (Deutsch)
- **FR**: French (Français)  
- **US**: US English

### Language-Specific Content

The system automatically filters content based on client language:

```python
# Example: Get German language manifest
manifest = content_delivery.get_client_manifest("1.18.15e", "DE")

# Returns only files matching:
# - /EU/DE/* (German-specific files)
# - Non-language-specific files (shared content)
```

## Security Features

### File Integrity Validation

- **Hash Verification**: All files validated against original PlayOnline hashes
- **Size Checking**: File size verification prevents corruption
- **Security Scanning**: Detects unknown executables and potential threats

### Access Control

- **API Authentication**: All endpoints require valid bearer tokens
- **Player Tracking**: Download requests logged with player ID and IP
- **Rate Limiting**: Prevents abuse and DDoS attacks

## Monitoring and Analytics

### Real-Time Statistics

- **Download Activity**: Live monitoring of file downloads
- **Player Metrics**: Track unique players and update requests
- **Performance Data**: Bandwidth usage and download speeds
- **Error Tracking**: Failed downloads and corruption detection

### Administrative Tools

- **Web Dashboard**: Real-time status display in main interface
- **CLI Tools**: Command-line management and statistics
- **Database Queries**: Direct access to download analytics
- **Automated Cleanup**: Scheduled maintenance of old records

## Integration with Existing Systems

### Database Schema

The PlayOnline integration extends the existing FFXI database schema without breaking changes:

- Uses existing `accounts` table for player authentication
- Extends with new tables for manifest and download tracking
- Maintains compatibility with existing server components

### Web Interface

Enhanced features integrate seamlessly with existing admin panel:

- Added PlayOnline status indicators to main dashboard
- New client management links in server status section
- Maintains existing monitoring and administration features

### API Compatibility

New PlayOnline endpoints coexist with existing API:

- All new endpoints use `/api/playonline/` prefix
- Existing endpoints remain unchanged
- Shared authentication and security model

## Troubleshooting

### Common Issues

1. **Manifest Import Fails**
   ```bash
   # Check SquareEnix directory exists and contains PlayOnlineViewer
   ls -la SquareEnix/PlayOnlineViewer/
   
   # Verify file.txt and patch.txt are present
   wc -l SquareEnix/PlayOnlineViewer/file.txt
   wc -l SquareEnix/PlayOnlineViewer/patch.txt
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connectivity
   mysql -h $FFXI_SQL_HOST -u $FFXI_SQL_LOGIN -p$FFXI_SQL_PASSWORD $FFXI_SQL_DATABASE -e "SELECT 1"
   
   # Check if PlayOnline tables exist
   mysql -h $FFXI_SQL_HOST -u $FFXI_SQL_LOGIN -p$FFXI_SQL_PASSWORD $FFXI_SQL_DATABASE -e "SHOW TABLES LIKE 'client_%'"
   ```

3. **API Authentication Errors**
   ```bash
   # Generate new API token
   curl -X POST -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "your_secret_key"}' \
        "http://localhost:5000/auth/token"
   ```

### Log Analysis

Monitor logs for PlayOnline integration issues:

```bash
# Check API logs
tail -f logs/ffxi_api.log | grep -i playonline

# Check client update manager logs  
tail -f logs/client_update.log

# Check database connection logs
tail -f logs/database.log | grep -i client_manifest
```

## Future Enhancements

### Planned Features

1. **Real-Time Updates**: WebSocket-based live update notifications
2. **CDN Integration**: Content delivery network for global distribution
3. **Delta Patching**: Incremental updates using binary diffs
4. **Mobile Support**: Client update management from mobile devices
5. **Automated Testing**: Continuous validation of client installations

### Development Roadmap

- **Phase 1** ✅: Basic integration and API endpoints (Complete)
- **Phase 2**: Enhanced web interface and monitoring (In Progress)
- **Phase 3**: Advanced caching and CDN integration (Planned)
- **Phase 4**: Mobile apps and real-time notifications (Future)

## Contributing

To contribute to PlayOnline integration development:

1. **Code Style**: Follow existing Python and JavaScript conventions
2. **Testing**: Add tests for new features in `tests/playonline/`
3. **Documentation**: Update this guide for new functionality
4. **Database**: Include migration scripts for schema changes

### Development Setup

```bash
# Install dependencies
pip install -r tools/requirements.txt

# Setup test database
python tools/client_update_manager.py --import-manifest

# Run tests
python -m pytest tests/playonline/

# Start development server
python web/api/app.py
```

---

*This PlayOnline integration provides a modern, scalable foundation for FFXI client management while preserving the proven architecture that Square Enix used successfully for over 8 years of content delivery.*