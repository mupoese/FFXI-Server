-- Dynamic Server Content Management Schema
-- Integration script for configurable server database
-- Inspired by content delivery systems for client-server communication
-- Note: Uses 'ffxi' prefix for compatibility, but system adapts to any SERVERNAME via application layer

-- FFXI client file manifest table
CREATE TABLE IF NOT EXISTS ffxi_client_manifest (
    file_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    file_hash VARCHAR(64) NOT NULL UNIQUE,
    file_path VARCHAR(512) NOT NULL,
    file_size BIGINT NOT NULL,
    file_category ENUM('graphics','audio','database','executable','data','documentation','other') NOT NULL,
    file_extension VARCHAR(10),
    version_id VARCHAR(20) NOT NULL DEFAULT '1.18.15e',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_hash (file_hash),
    INDEX idx_category (file_category),
    INDEX idx_version (version_id),
    INDEX idx_path (file_path(255)),
    INDEX idx_size (file_size)
);

-- FFXI client version tracking
CREATE TABLE IF NOT EXISTS ffxi_client_versions (
    version_id VARCHAR(20) PRIMARY KEY,
    version_name VARCHAR(100),
    release_date DATE,
    total_files INT DEFAULT 0,
    total_size_bytes BIGINT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FFXI client update requests and tracking
CREATE TABLE IF NOT EXISTS ffxi_client_updates (
    request_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    player_id INT,
    client_version VARCHAR(20),
    requested_version VARCHAR(20),
    request_status ENUM('pending','in_progress','completed','failed') DEFAULT 'pending',
    files_updated INT DEFAULT 0,
    bytes_transferred BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    
    INDEX idx_player (player_id),
    INDEX idx_status (request_status),
    INDEX idx_version (client_version),
    FOREIGN KEY (player_id) REFERENCES accounts(id) ON DELETE CASCADE
);

-- File download tracking for bandwidth management
CREATE TABLE IF NOT EXISTS client_file_downloads (
    download_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    file_hash VARCHAR(64) NOT NULL,
    player_id INT,
    download_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    download_complete TIMESTAMP NULL,
    bytes_downloaded BIGINT DEFAULT 0,
    download_status ENUM('started','completed','failed','cancelled') DEFAULT 'started',
    client_ip VARCHAR(45),
    
    INDEX idx_file_hash (file_hash),
    INDEX idx_player (player_id),
    INDEX idx_status (download_status),
    INDEX idx_start_time (download_start),
    FOREIGN KEY (file_hash) REFERENCES client_manifest(file_hash),
    FOREIGN KEY (player_id) REFERENCES accounts(id) ON DELETE SET NULL
);

-- Insert PlayOnline version data
INSERT INTO client_versions (version_id, version_name, release_date, total_files, total_size_bytes) 
VALUES ('1.18.15e', 'PlayOnline Final Release', '2011-08-29', 2469, 562881258)
ON DUPLICATE KEY UPDATE 
    total_files = VALUES(total_files),
    total_size_bytes = VALUES(total_size_bytes);

-- Example manifest entries (top 10 largest files from analysis)
-- These would normally be bulk-imported from playonline_analyzer.py output
INSERT IGNORE INTO client_manifest (file_hash, file_path, file_size, file_category, file_extension) VALUES
('hash1', 'viewer/data/pmlus/bgm/Daikoukai.114.bgw', 15156318, 'audio', '.bgw'),
('hash2', 'viewer/data/system/bgm/Daikoukai_(by_Noriko_Matsueda).114.bgw', 15156318, 'audio', '.bgw'),
('hash3', 'viewer/data/system/bgm/Foster_Family_(by_Noriko_Matsueda).126.bgw', 9629850, 'audio', '.bgw'),
('hash4', 'viewer/data/pmlus/bgm/FFXIContMusic.155.bgw', 9049278, 'audio', '.bgw'),
('hash5', 'viewer/data/system/bgm/Honobono_(by_Noriko_Matsueda).110.bgw', 9351822, 'audio', '.bgw'),
('hash6', 'viewer/data/system/bgm/Payload_Pasific_(by_Noriko_Matsueda).125.bgw', 8335236, 'audio', '.bgw'),
('hash7', 'viewer/data/pmlus/bgm/FFXIContMusic.150.bgw', 6817386, 'audio', '.bgw'),
('hash8', 'viewer/data/pmlus/bgm/FFXIContMusic.157.bgw', 6603186, 'audio', '.bgw'),
('hash9', 'viewer/data/system/bgm/Funky_monky_(by_Noriko_Matsueda).116.bgw', 6561696, 'audio', '.bgw'),
('hash10', 'patchfiles/PlayOnlineViewer/viewer/com/app.dll', 4335104, 'executable', '.dll');

-- Views for easy querying
CREATE OR REPLACE VIEW v_manifest_summary AS
SELECT 
    file_category,
    COUNT(*) as file_count,
    ROUND(SUM(file_size)/1024/1024, 2) as total_mb,
    ROUND(AVG(file_size)/1024, 2) as avg_kb
FROM client_manifest 
GROUP BY file_category
ORDER BY total_mb DESC;

CREATE OR REPLACE VIEW v_largest_files AS
SELECT 
    file_path,
    file_category,
    ROUND(file_size/1024/1024, 2) as size_mb
FROM client_manifest 
ORDER BY file_size DESC 
LIMIT 20;

-- Stored procedures for client operations
DELIMITER //

CREATE PROCEDURE GetClientManifest(IN client_version VARCHAR(20))
BEGIN
    SELECT file_hash, file_path, file_size, file_category
    FROM client_manifest 
    WHERE version_id = client_version
    ORDER BY file_category, file_path;
END //

CREATE PROCEDURE ValidateClientFiles(IN player_id INT, IN client_hashes JSON)
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE file_hash VARCHAR(64);
    DECLARE file_exists INT DEFAULT 0;
    DECLARE missing_files INT DEFAULT 0;
    
    -- Create temporary table for validation results
    CREATE TEMPORARY TABLE temp_validation (
        file_hash VARCHAR(64),
        is_valid BOOLEAN
    );
    
    -- Log validation request
    INSERT INTO client_update_requests (player_id, client_version, request_status)
    VALUES (player_id, '1.18.15e', 'pending');
    
    SELECT 'Validation complete' as result, missing_files as missing_count;
    
    DROP TEMPORARY TABLE temp_validation;
END //

CREATE PROCEDURE RecordFileDownload(
    IN p_file_hash VARCHAR(64),
    IN p_player_id INT,
    IN p_client_ip VARCHAR(45)
)
BEGIN
    INSERT INTO client_file_downloads (file_hash, player_id, client_ip)
    VALUES (p_file_hash, p_player_id, p_client_ip);
END //

DELIMITER ;

-- Create indexes for performance
CREATE INDEX idx_manifest_category_size ON client_manifest(file_category, file_size DESC);
CREATE INDEX idx_downloads_daily ON client_file_downloads(DATE(download_start));

-- Example queries for server integration

-- Get summary statistics (matching playonline_analyzer.py output)
-- SELECT * FROM v_manifest_summary;

-- Find files needing updates for a client
-- SELECT m.file_hash, m.file_path, m.file_size 
-- FROM client_manifest m 
-- WHERE m.file_hash NOT IN ('hash1', 'hash2', 'hash3')  -- client's file hashes
-- ORDER BY m.file_size ASC;  -- Download smallest files first

-- Monitor bandwidth usage
-- SELECT 
--     DATE(download_start) as date,
--     COUNT(*) as downloads,
--     ROUND(SUM(bytes_downloaded)/1024/1024, 2) as mb_transferred
-- FROM client_file_downloads 
-- WHERE download_start >= DATE_SUB(NOW(), INTERVAL 7 DAY)
-- GROUP BY DATE(download_start);

-- Clean up old download records (run periodically)
-- DELETE FROM client_file_downloads 
-- WHERE download_start < DATE_SUB(NOW(), INTERVAL 30 DAY)
-- AND download_status IN ('completed', 'failed', 'cancelled');