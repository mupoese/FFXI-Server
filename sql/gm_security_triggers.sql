-- GM Security Triggers for Admin Dashboard Exclusive Control
-- These triggers prevent unauthorized GM level changes outside the admin dashboard

DELIMITER $$

-- Trigger to prevent unauthorized account privilege changes
CREATE TRIGGER prevent_unauthorized_account_priv_update
BEFORE UPDATE ON accounts
FOR EACH ROW
BEGIN
    -- Get server owner from settings or default to 'admin'
    DECLARE server_owner VARCHAR(16) DEFAULT 'admin';
    
    -- Prevent demoting the server owner below privilege level 5
    IF OLD.login = server_owner AND NEW.priv < 5 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Server owner account cannot be demoted below privilege level 5';
    END IF;
    
    -- Log privilege changes for audit
    IF OLD.priv != NEW.priv THEN
        INSERT INTO audit_gm (date_time, gm_name, command, full_string)
        VALUES (NOW(), 'SYSTEM', 'PRIV_CHANGE', 
                CONCAT('Account ', NEW.login, ' privilege changed from ', OLD.priv, ' to ', NEW.priv));
    END IF;
END$$

-- Trigger to prevent unauthorized GM level changes in chars table
CREATE TRIGGER prevent_unauthorized_gmlevel_update
BEFORE UPDATE ON chars
FOR EACH ROW
BEGIN
    DECLARE account_login VARCHAR(16);
    DECLARE server_owner VARCHAR(16) DEFAULT 'admin';
    
    -- Get account login for this character
    SELECT a.login INTO account_login 
    FROM accounts a 
    WHERE a.id = NEW.accid;
    
    -- Prevent demoting the server owner below GM level 5
    IF account_login = server_owner AND NEW.gmlevel < 5 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Server owner character cannot be demoted below GM level 5';
    END IF;
    
    -- Log GM level changes for audit
    IF OLD.gmlevel != NEW.gmlevel THEN
        INSERT INTO audit_gm (date_time, gm_name, command, full_string)
        VALUES (NOW(), 'SYSTEM', 'GMLEVEL_CHANGE', 
                CONCAT('Character ', NEW.charname, ' (', account_login, ') GM level changed from ', 
                       OLD.gmlevel, ' to ', NEW.gmlevel));
    END IF;
END$$

-- Trigger to prevent unauthorized account privilege insertions
CREATE TRIGGER prevent_unauthorized_account_priv_insert
BEFORE INSERT ON accounts
FOR EACH ROW
BEGIN
    -- Ensure new accounts don't get high privileges by default
    IF NEW.priv > 2 THEN
        SET NEW.priv = 1;
        
        INSERT INTO audit_gm (date_time, gm_name, command, full_string)
        VALUES (NOW(), 'SYSTEM', 'PRIV_RESET', 
                CONCAT('New account ', NEW.login, ' privilege reset to 1 for security'));
    END IF;
END$$

-- Trigger to prevent unauthorized GM level insertions
CREATE TRIGGER prevent_unauthorized_gmlevel_insert
BEFORE INSERT ON chars
FOR EACH ROW
BEGIN
    -- Ensure new characters don't get GM levels by default
    IF NEW.gmlevel > 0 THEN
        SET NEW.gmlevel = 0;
        
        INSERT INTO audit_gm (date_time, gm_name, command, full_string)
        VALUES (NOW(), 'SYSTEM', 'GMLEVEL_RESET', 
                CONCAT('New character ', NEW.charname, ' GM level reset to 0 for security'));
    END IF;
END$$

DELIMITER ;

-- Create audit table if it doesn't exist
CREATE TABLE IF NOT EXISTS audit_gm (
    date_time DATETIME NOT NULL,
    gm_name VARCHAR(16) NOT NULL,
    command VARCHAR(40) NOT NULL,
    full_string VARCHAR(200) NOT NULL,
    PRIMARY KEY (date_time, gm_name),
    INDEX idx_date_time (date_time),
    INDEX idx_gm_name (gm_name),
    INDEX idx_command (command)
);

-- Ensure server owner exists and has proper privileges
INSERT INTO accounts (login, password, priv) 
VALUES ('admin', SHA1('admin_password_change_this'), 5)
ON DUPLICATE KEY UPDATE priv = 5;

-- Create initial server owner character if needed
INSERT IGNORE INTO chars (accid, charname, gmlevel, nation, zone) 
SELECT a.id, 'ServerOwner', 5, 0, 230
FROM accounts a 
WHERE a.login = 'admin';

-- Initial audit log entry
INSERT INTO audit_gm (date_time, gm_name, command, full_string)
VALUES (NOW(), 'SYSTEM', 'SECURITY_INIT', 'GM Security triggers initialized - Admin dashboard exclusive control enabled');