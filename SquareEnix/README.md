# SquareEnix PlayOnlineViewer Analysis

## Directory Overview

This directory contains the original Square Enix PlayOnlineViewer client files and patch management system used for FFXI client updates. The system represents a sophisticated content delivery and version control mechanism that was used to distribute game updates from 2003 to 2011.

## Key Components

### File Manifests
- **`file.txt`** (1,245 entries): Complete file inventory with checksums and file sizes
- **`patch.txt`** (1,226 entries): Patch file manifest for incremental updates
- Both files use format: `hash:size:filepath` for integrity verification

### Version Control System
- **`version.dat`**: Current version identifier (1.18.15e)
- **`patch.cfg`**: Comprehensive patch history from 2003-2011 with direct/indirect patch support
- **`patch.ver`**: Binary version data for patch validation

### Multi-Language Support
- **`EU/DE/`**: German localization files
- **`EU/EN/`**: English localization files  
- **`EU/FR/`**: French localization files
- Each contains: profile data, string tables, documentation, FAQ databases

### Content Categories

#### Database Files (.pfb/.pib)
- `prof_pol.*`: Player profile data
- `prof_001.*`, `prof_002.*`: Profile templates
- `c_chan.*`: Channel configurations
- `kb_faq.*`: FAQ database content
- `zo_count.*`: Zone counting data

#### Localization Assets
- `proface0.txt`, `proface1.txt`: Profile interface text
- `StringTable.bin`: Localized UI strings
- `polerr.bin`: Error message databases
- `sqpolcts.bin`: Policy/contract text

#### Multimedia Content
- **Audio**: `.spw` sound effects, `.bgw` background music
- **Graphics**: `.png` UI elements, wallpapers, icons
- **Interactive**: `.ang` animation files

#### System Files
- **Executables**: `pol.exe`, various `.dll` libraries
- **Configuration**: Help files, documentation (`.chm`)
- **Utilities**: System information tools, configuration utilities

## Patch Management Architecture

### Direct vs Indirect Patches
The system supports two patch types:
- **Direct patches** (`.slc` files): Complete file replacements
- **Indirect patches** (`.olc` files): Delta/differential updates

### Version Timeline
Patch history spans from `20030909_A` (September 2003) to `20110829_E` (August 2011), showing:
- Regular content updates
- Localization patches
- System file updates
- Audio/visual asset updates

### Integrity System
Each file entry includes:
- SHA-like hash for verification
- File size for validation
- Path for proper deployment

## Integration Opportunities for FFXI Server

### 1. Enhanced Update System
**Current Capability**: Basic file serving
**Enhancement**: Implement PlayOnline-style patch delivery
```
- Differential patching to reduce download sizes
- Multi-language content delivery
- Integrity verification system
- Rollback capabilities for failed updates
```

### 2. Content Management System
**Implementation**: Web-based patch management
```
- Admin interface for patch creation/deployment
- Version control for server-side modifications
- Automated integrity checking
- Client version validation
```

### 3. Multi-Language Server Support
**Current Status**: Limited localization
**Enhancement**: Full EU language support
```
- Dynamic language switching
- Localized error messages
- Region-specific content delivery
- Cultural customization options
```

### 4. Advanced File Validation
**Integration Points**:
```python
class FFXIFileValidator:
    def validate_client_files(self, client_manifest):
        # Compare against PlayOnline manifest
        # Verify file integrity
        # Flag modified/corrupted files
        # Suggest required updates
```

## Direct Download Integration

### PlayOnline Update Mechanism
The original system supported direct downloads from FFXI main servers:

#### Configuration Files
- `patch.cfg`: Contains server endpoints and patch metadata
- `url/cert.db`: Certificate database for secure connections
- `url/rdthosts.bin`: Redirect host configurations

#### Implementation Suggestions
1. **Mirror System**: Set up local mirrors of patch servers
2. **Proxy Integration**: Route client updates through server infrastructure  
3. **Content Validation**: Use existing checksums for integrity verification
4. **Bandwidth Management**: Implement differential patching

### Server Enhancement Proposals

#### 1. Automated Asset Extraction
```bash
# Leverage existing streaming/ffxi_asset_extractor.py
python streaming/ffxi_asset_extractor.py --source SquareEnix/PlayOnlineViewer
```

#### 2. Web Interface Integration
Enhance `web/index.html` with:
- Client version checking
- Automatic update notifications
- Patch download interface
- Multi-language support detection

#### 3. Database Integration
```sql
-- Extend existing database schema
CREATE TABLE client_versions (
    version_id VARCHAR(20) PRIMARY KEY,
    release_date DATETIME,
    language_code CHAR(2),
    manifest_hash VARCHAR(64),
    patch_size BIGINT
);

CREATE TABLE file_manifest (
    file_hash VARCHAR(64) PRIMARY KEY,
    file_path VARCHAR(512),
    file_size BIGINT,
    version_id VARCHAR(20),
    FOREIGN KEY (version_id) REFERENCES client_versions(version_id)
);
```

#### 4. API Endpoints
```javascript
// Proposed REST API for client updates
GET /api/client/version/check
POST /api/client/update/request
GET /api/client/patches/{version}
GET /api/client/files/{hash}
```

## Technical Implementation

### File Parsing Utilities
Create tools to process PlayOnline manifests:
```python
def parse_manifest(file_path):
    """Parse file.txt or patch.txt manifest files"""
    entries = []
    with open(file_path, 'r') as f:
        for line in f:
            if ':' in line:
                hash_val, size, path = line.strip().split(':', 2)
                entries.append({
                    'hash': hash_val,
                    'size': int(size),
                    'path': path
                })
    return entries
```

### Integrity Verification
```python
def verify_file_integrity(file_path, expected_hash, expected_size):
    """Verify file matches PlayOnline manifest entry"""
    if not os.path.exists(file_path):
        return False
    
    actual_size = os.path.getsize(file_path)
    if actual_size != expected_size:
        return False
    
    # Implement hash verification based on PlayOnline algorithm
    return calculate_hash(file_path) == expected_hash
```

## Security Considerations

### File Validation
- Implement cryptographic verification for all client files
- Prevent client-side modification detection
- Secure update delivery channels

### Access Control
- Authenticate client update requests
- Rate limiting for patch downloads
- Geographic content restrictions if needed

## Performance Optimizations

### Caching Strategy
- CDN integration for patch delivery
- Local caching of frequently accessed files
- Compression for large asset files

### Bandwidth Management
- Prioritize critical system files
- Schedule large updates during off-peak hours
- Implement resume capabilities for interrupted downloads

## Analysis Results

### Complete Manifest Analysis
**Generated from PlayOnline files using `tools/playonline_analyzer.py`**

- **Total Files**: 2,469 entries across both manifests
- **Total Size**: 536.8 MB of content
- **Version**: 1.18.15e (final PlayOnline release)
- **Content Distribution**:
  - Graphics: 1,548 files (63% - UI elements, icons, wallpapers)
  - Audio: 434 files (18% - BGM and sound effects)  
  - Database: 128 files (5% - Profile and configuration data)
  - Executables: 34 files (1% - Core PlayOnline components)
  - Other: 356 files (13% - Documentation, patches, data)

### Key Technical Findings

#### Largest Content Files
1. **Daikoukai BGM files**: 14.5 MB each (multiple versions)
2. **Foster Family BGM**: 9.2 MB
3. **Audio content dominates** large file sizes

#### Critical System Components
- **pol.exe** (1.6 MB): Main PlayOnline executable
- **app.dll/appEU.dll** (4.1 MB each): Core application libraries
- **polcore.dll** (0.5 MB): Core functionality module
- **Configuration tools**: polcfg.exe, sysinfo.dll, startpol.exe

#### File Format Distribution
- **.png**: 1,399 files (graphics assets)
- **.spw**: 358 files (sound effects)
- **.pml**: 187 files (markup/interface definitions)
- **.ang**: 149 files (animation data)
- **.bgw**: 76 files (background music)
- **.pfb/.pib**: 128 files (profile/database pairs)

### Practical Integration Opportunities

#### 1. Database Schema Implementation
```sql
-- Recommended table structure based on analysis
CREATE TABLE client_manifest (
    file_hash VARCHAR(64) PRIMARY KEY,
    file_path VARCHAR(512) NOT NULL,
    file_size BIGINT NOT NULL,
    category ENUM('graphics','audio','database','executable','data','documentation','other'),
    version_id VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_version (version_id)
);

-- Store 2,469 entries from PlayOnline manifests
-- Enable client file validation and update checking
```

#### 2. Content Delivery Strategy
- **High Priority** (34 files, ~15 MB): Executables and core system files
- **Medium Priority** (562 files, ~180 MB): Database and interface graphics  
- **Low Priority** (1,873 files, ~340 MB): Audio content and documentation
- **Caching Strategy**: Cache executables indefinitely, graphics for 30 days, audio on-demand

#### 3. Update API Implementation
```python
# Endpoint suggestions based on manifest structure
@app.route('/api/client/manifest/<version>')
def get_client_manifest(version):
    """Return file manifest for client validation"""
    
@app.route('/api/client/validate', methods=['POST'])
def validate_client_files():
    """Validate client files against server manifest"""
    
@app.route('/api/client/file/<file_hash>')
def download_file(file_hash):
    """Serve individual files for updates"""
```

### Future Development

### Phase 1: Analysis & Integration ✅
- [x] Analyze existing PlayOnline structure
- [x] Document file formats and systems
- [x] Create parsing utilities (`tools/playonline_analyzer.py`)
- [x] Generate comprehensive manifest analysis

### Phase 2: Server Integration
- [ ] Import 2,469 manifest entries to server database
- [ ] Implement 5 core API endpoints for client updates
- [ ] Create web interface for 536.8 MB content management
- [ ] Add multi-format file serving (.png, .spw, .bgw, .dll, etc.)

### Phase 3: Advanced Features
- [ ] Implement differential patching (based on patch.cfg history)
- [ ] Deploy CDN for 1,548 graphics files
- [ ] Create real-time client validation system
- [ ] Add bandwidth optimization for 434 audio files

## Implementation Guide

### Quick Start
1. **Analyze existing content**:
   ```bash
   python tools/playonline_analyzer.py SquareEnix
   ```

2. **Setup database integration**:
   ```bash
   mysql -u root -p < sql/playonline_integration.sql
   ```

3. **Import manifest data**:
   ```python
   # Use playonline_analyzer.py to export data for bulk import
   # JSON output can be processed for database insertion
   ```

### Server API Endpoints

#### Client Validation
```python
@app.route('/api/client/validate', methods=['POST'])
def validate_client():
    """
    Validate client files against PlayOnline manifest
    POST body: {"files": [{"hash": "abc123", "path": "pol.exe", "size": 1691648}]}
    Returns: {"valid": true, "missing": [], "corrupted": []}
    """
```

#### File Delivery
```python
@app.route('/api/client/file/<file_hash>')
def serve_file(file_hash):
    """
    Serve individual files for client updates
    Supports range requests for large BGM files (14.5 MB each)
    """
```

#### Update Management
```python
@app.route('/api/client/manifest/<version>')
def get_manifest(version):
    """
    Return complete file manifest for version
    Enables differential updates and integrity checking
    """
```

### Content Categories & Priorities

Based on the 2,469 file analysis:

#### Critical Updates (34 files, ~15 MB)
- **pol.exe, app.dll, polcore.dll**: Core functionality
- **Priority**: Immediate download, cache indefinitely
- **Use case**: Security updates, bug fixes

#### Interface Updates (1,548 files, ~180 MB)  
- **PNG graphics, ANG animations**: UI elements
- **Priority**: Download on-demand, cache 30 days
- **Use case**: Client customization, localization

#### Content Updates (434 files, ~340 MB)
- **BGW music, SPW sound effects**: Audio content
- **Priority**: Background download, cache selectively
- **Use case**: New content, seasonal events

### Resources & References

#### Key Files for Further Analysis
- **`tools/playonline_analyzer.py`**: Complete manifest parser and analyzer
- **`sql/playonline_integration.sql`**: Database schema for client management
- **`playonline_analysis.json`**: Detailed breakdown of all 2,469 files
- **`SquareEnix/PlayOnlineViewer/patch.cfg`**: Historical update system (2003-2011)

#### Related Server Components
- **Database**: Schema extension in `sql/playonline_integration.sql`
- **Web Interface**: Enhancement points in `web/index.html` 
- **Asset Processing**: Integration with `streaming/ffxi_asset_extractor.py`
- **Tools**: Analysis utilities in `tools/playonline_analyzer.py`

---

*This analysis provides a foundation for enhancing the FFXI server with PlayOnline's sophisticated update and content delivery capabilities, enabling more robust client management and improved user experience.*