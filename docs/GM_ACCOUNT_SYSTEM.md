# FFXI Server GM Account System Documentation

## Overview

The Final Fantasy XI Server implements a comprehensive Game Master (GM) account system with **ADMIN DASHBOARD EXCLUSIVE** promotion control. GM privileges can only be granted through the web admin dashboard by the server owner, ensuring maximum security and preventing unauthorized privilege escalation.

## Security Model

### ⚠️ CRITICAL SECURITY CHANGE ⚠️
**GM promotions are now EXCLUSIVELY controlled through the web admin dashboard. In-game promotion commands have been disabled for security.**

### Server Owner Authority
- **Only the server owner** can promote or demote GMs through the admin dashboard
- Server owner account is **permanently protected** at Level 5 and cannot be demoted
- All GM privilege changes are logged in the audit system
- Database triggers prevent unauthorized privilege modifications

## GM Level System

### Privilege Levels

| Level | Type | Description | Access |
|-------|------|-------------|---------|
| **0** | Normal Player | Standard player account with no GM privileges | None |
| **1** | Basic GM | Entry-level GM with basic administrative commands | Most commands |
| **2** | Intermediate GM | Enhanced privileges for content management | Advanced commands |
| **3** | Senior GM | Advanced administrative capabilities | Server management |
| **4** | Lead GM | High-level administrative control | System operations |
| **5** | Super Admin | Full server control and dangerous operations | All commands |

### Promotion Security

#### Admin Dashboard Exclusive Control
```javascript
// GM promotion endpoint - requires server owner authentication
POST /api/gm/promote
{
    "login": "target_username",
    "gmlevel": 3
}

// Only server owner can execute this endpoint
// All actions are logged in audit_gm table
```

#### Database Protection
```sql
-- Triggers prevent unauthorized changes
CREATE TRIGGER prevent_unauthorized_gmlevel_update
BEFORE UPDATE ON chars
FOR EACH ROW
BEGIN
    -- Prevent server owner demotion
    IF account_login = server_owner AND NEW.gmlevel < 5 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Server owner cannot be demoted below GM level 5';
    END IF;
END
```

### Database Structure

#### Accounts Table
```sql
CREATE TABLE accounts (
  id int(10) unsigned NOT NULL,
  login varchar(16) NOT NULL,
  password varchar(64) NOT NULL,
  priv tinyint(3) unsigned NOT NULL DEFAULT '1',  -- Account privilege level
  -- ... other fields
);
```

#### Characters Table
```sql
-- GM level stored in chars table
UPDATE chars SET gmlevel = ? WHERE charid = ? LIMIT 1;
```

#### Enhanced Audit Table
```sql
CREATE TABLE audit_gm (
  date_time datetime NOT NULL,
  gm_name varchar(16) NOT NULL,
  command varchar(40) NOT NULL,
  full_string varchar(200) NOT NULL,
  PRIMARY KEY (date_time, gm_name)
);
```

## Admin Dashboard GM Management

### Accessing GM Management
1. Log into the web admin dashboard as server owner
2. Navigate to the "👑 GM Management" tab
3. Only server owner accounts have access to this section

### Promoting a GM
1. Click "➕ Promote New GM" button
2. Enter the target username
3. Select GM level (1-5)
4. Confirm the promotion

### Managing Existing GMs
- **Edit GM Level**: Modify an existing GM's privilege level
- **Revoke Privileges**: Remove GM status from an account
- **View Audit Log**: Review all GM-related actions

### Security Features
- **Server Owner Protection**: Owner account cannot be modified or demoted
- **Audit Logging**: All GM actions are logged with timestamps
- **Database Triggers**: Prevent unauthorized database modifications
- **Session Authentication**: Admin dashboard requires secure authentication

## Disabled In-Game Commands

### Promote Command Disabled
```lua
-- scripts/commands/promote.lua
commandObj.onTrigger = function(player, target, level)
    -- GM promotion is now restricted to admin dashboard only
    player:printToPlayer('GM promotion is now restricted to the web admin dashboard for security.')
    player:printToPlayer('Contact the server owner to request GM privileges through the admin panel.')
    
    -- Log the attempt for security audit
    printf('[SECURITY] %s attempted to use disabled promote command', player:getName())
end
```

### Security Audit
All attempts to use the disabled promote command are logged for security monitoring.

## Core GM Functions

### Level Management
```lua
-- Check GM level
local level = player:getGMLevel()
if level >= 3 then
    -- Authorized for advanced operations
end

-- GM level changes now only through admin dashboard
-- setGMLevel() function restricted to admin API calls
```

### Character Entity Implementation
```cpp
class CCharEntity {
    uint8 m_GMlevel;    // GM privilege level (0-5)
    
    uint8 getGMLevel() const { return m_GMlevel; }
    // setGMLevel() now restricted to admin dashboard calls
};
```

## GM Command Categories

### 1. Player Management (Permission 1-3)
| Command | Permission | Description |
|---------|------------|-------------|
| ~~`promote`~~ | ~~1~~ | **DISABLED - Admin Dashboard Only** |
| `bring` | 1 | Teleport player to GM |
| `goto` | 1 | Teleport GM to player |
| `jail` | 1 | Confine player to GM jail |
| `pardon` | 1 | Release player from jail |
| `raise` | 1 | Resurrect player |
| `setplayerlevel` | 1 | Modify player job level |
| `setgil` | 1 | Modify player currency |

### 2. Content Management (Permission 1-2)
| Command | Permission | Description |
|---------|------------|-------------|
| `additem` | 1 | Give items to players |
| `addquest` | 1 | Grant quest progress |
| `addmission` | 1 | Grant mission progress |

## Implementation Guide

### Setting Up Server Owner Exclusive Control

#### 1. Environment Configuration
```bash
# Set server owner username (default: admin)
export FFXI_SERVER_OWNER="your_server_owner_username"

# Set secure API secret key
export FFXI_API_SECRET_KEY="your_secure_secret_key_here"
```

#### 2. Database Security Installation
```bash
# Install database security triggers
mysql -u root -p xidb < sql/gm_security_triggers.sql

# Verify triggers are installed
mysql -u root -p xidb -e "SHOW TRIGGERS WHERE Trigger like '%gm%';"
```

#### 3. Web Admin Dashboard Setup
```bash
# Start the admin API
cd web/api
python3 app.py

# Access admin dashboard
# http://localhost:5000/admin.html
```

#### 4. Server Owner Initial Setup
1. Access the admin dashboard with server owner credentials
2. Navigate to "👑 GM Management" tab
3. Verify server owner account shows as "Protected"
4. Test GM promotion functionality

### Security Verification

#### Check Disabled Promote Command
```bash
# Test in-game that promote command is disabled
# Character should receive security message
!promote testuser 1
```

#### Verify Database Protection
```sql
-- This should fail with error message
UPDATE accounts SET priv = 5 WHERE login = 'regular_user';

-- This should fail with error message  
UPDATE chars SET gmlevel = 5 WHERE charname = 'regular_character';
```

#### Audit Log Verification
```sql
-- Check audit log for security events
SELECT * FROM audit_gm 
WHERE command LIKE '%SECURITY%' 
ORDER BY date_time DESC 
LIMIT 10;
```

### Emergency Procedures

#### Server Owner Password Reset
```bash
# Reset server owner password if needed
mysql -u root -p xidb -e "
UPDATE accounts 
SET password = SHA1('new_password_here') 
WHERE login = 'admin';"
```

#### Emergency GM Revocation
```bash
# Revoke all GM privileges except server owner
mysql -u root -p xidb -e "
UPDATE chars c 
JOIN accounts a ON c.accid = a.id 
SET c.gmlevel = 0 
WHERE a.login != 'admin';"
```

#### Restore In-Game Promote (Emergency Only)
```lua
-- Only if admin dashboard is compromised
-- Edit scripts/commands/promote.lua to restore original functionality
-- NOT RECOMMENDED - defeats security purpose
```

## API Endpoints

### GM Management API

#### Get GM Accounts
```http
GET /api/gm/accounts
Authorization: Bearer {server_owner_token}

Response:
{
    "gm_accounts": [...],
    "server_owner": "admin",
    "timestamp": "2024-08-31T01:15:23Z"
}
```

#### Promote GM
```http
POST /api/gm/promote
Authorization: Bearer {server_owner_token}
Content-Type: application/json

{
    "login": "target_username",
    "gmlevel": 3
}

Response:
{
    "success": true,
    "message": "Successfully promoted target_username to GM level 3",
    "timestamp": "2024-08-31T01:15:23Z"
}
```

#### Revoke GM
```http
POST /api/gm/revoke
Authorization: Bearer {server_owner_token}
Content-Type: application/json

{
    "login": "target_username"
}

Response:
{
    "success": true,
    "message": "Successfully revoked GM privileges for target_username",
    "timestamp": "2024-08-31T01:15:23Z"
}
```

#### Audit Log
```http
GET /api/gm/audit?limit=50
Authorization: Bearer {server_owner_token}

Response:
{
    "audit_logs": [...],
    "count": 50,
    "timestamp": "2024-08-31T01:15:23Z"
}
```

## Best Practices

### Security Recommendations
1. **Unique Server Owner**: Use a unique username, not 'admin'
2. **Strong Password**: Use a strong password for the server owner account
3. **Secure API Key**: Generate a random, secure API secret key
4. **Regular Audits**: Review audit logs regularly for suspicious activity
5. **Backup Access**: Maintain database access for emergency procedures
6. **HTTPS Only**: Use HTTPS for admin dashboard access in production

### GM Management Workflow
1. **Request Process**: Establish a formal GM application process
2. **Approval Process**: Server owner reviews and approves all GM requests
3. **Trial Period**: Consider trial periods for new GMs
4. **Regular Reviews**: Periodically review GM performance and necessity
5. **Privilege Escalation**: Start GMs at lower levels and promote based on performance

### Monitoring and Maintenance
1. **Daily Audit Review**: Check audit logs daily for unauthorized attempts
2. **Weekly GM Review**: Review active GM accounts weekly
3. **Monthly Security Check**: Verify security triggers and protections monthly
4. **Quarterly Access Review**: Full review of all GM privileges quarterly

## Troubleshooting

### Common Issues

#### "Only the server owner can promote GMs"
- **Cause**: User is not authenticated as server owner
- **Solution**: Verify server owner username and authentication

#### "Server owner cannot be demoted"
- **Cause**: Attempt to demote server owner account
- **Solution**: This is by design for security - server owner is protected

#### "Invalid or expired token"
- **Cause**: Authentication token has expired
- **Solution**: Re-authenticate through admin dashboard

#### Database trigger errors
- **Cause**: Direct database modification blocked by security triggers
- **Solution**: Use admin dashboard for all GM management

### Debug Commands

```bash
# Check server owner configuration
echo $FFXI_SERVER_OWNER

# Test API authentication
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/gm/accounts

# Check database triggers
mysql -u root -p xidb -e "SHOW TRIGGERS WHERE Trigger LIKE '%gm%';"

# View recent audit logs
mysql -u root -p xidb -e "SELECT * FROM audit_gm ORDER BY date_time DESC LIMIT 10;"
```
| `addspell` | 1 | Teach spells to players |
| `addkeyitem` | 1 | Grant key items |
| `completemission` | 1 | Complete missions |
| `completequest` | 1 | Complete quests |

### 3. Server Management (Permission 3-5)
| Command | Permission | Description |
|---------|------------|-------------|
| `reloadglobal` | 5 | Reload global scripts |
| `reloadquest` | 5 | Reload quest scripts |
| `reloadbattlefield` | 5 | Reload battlefield data |
| `updateconquest` | 3 | Update conquest system |
| `setweather` | 1 | Control zone weather |
| `time` | 1 | Modify game time |

### 4. Debug & Development (Permission 4-5)
| Command | Permission | Description |
|---------|------------|-------------|
| `checkinteraction` | 5 | Debug entity interactions |
| `packetmod` | 5 | Modify network packets |
| `crash` | 5 | Force server crash (testing) |
| `gc_full` | 5 | Force garbage collection |
| `reloadnavmesh` | 5 | Reload navigation meshes |

### 5. Special Abilities (Permission 1)
| Command | Description |
|---------|-------------|
| `godmode` | Grant invincibility and massive stat boosts |
| `hide` | Become invisible to players |
| `wallhack` | Phase through walls and obstacles |
| `speed` | Increase movement speed |
| `immortal` | Prevent death |

## Special GM Modes

### God Mode
Provides ultimate power for testing and emergency situations:

```lua
-- God Mode Effects
- MAX_HP_BOOST: +1000 HP
- MAX_MP_BOOST: +1000 MP  
- All job abilities permanently active
- REGAIN: 300/tick TP regeneration
- REFRESH: 99/tick MP regeneration
- REGEN: 99/tick HP regeneration
- Massive stat bonuses: +2500 to all combat stats

-- God Mode Tier 1 (Soft Mode)
- MAX_HP_BOOST: +200 HP
- REGAIN: 50/tick TP
- REFRESH: 999/tick MP
- REGEN: 999/tick HP
- CHAINSPELL and MANAFONT active
```

### Hide Mode
Makes GM invisible to normal players:
```lua
-- Hide Implementation
player:setCharVar('GMHidden', 1)
player:setGMHidden(true)
-- GM becomes invisible to non-GM players
-- Used for observation and investigation
```

### Visual GM Level
Controls GM indicator display on client:
```lua
-- Visual levels 0-7
-- Shows crown/special icons next to GM name
-- Level 0 = No indicator (appears as normal player)
-- Level 7 = Maximum indicator visibility
player:setVisibleGMLevel(math.min(7, gmlevel + 3))
```

## Permission Control System

### Server Owner Authority
The FFXI Server implements **hierarchical permission control** with strict server owner authority:

#### Admin Dashboard Exclusive Control
GM privileges can be controlled through multiple channels, but **server administrators should configure the system for exclusive admin dashboard control**:

1. **Web Admin Panel Authority**: The `tools/web_admin.py` provides comprehensive user management
2. **Database Level Control**: Direct database access for `accounts.priv` and `chars.gmlevel` fields
3. **In-Game Command System**: GM commands like `!promote` (can be disabled for security)

#### Recommended Security Configuration

**Option 1: Admin Dashboard Only (Recommended)**
```lua
-- Disable in-game promotion commands by setting server owner as sole authority
-- Edit scripts/commands/promote.lua to require priv level 5
commandObj.cmdprops = {
    permission = 5,  -- Only server owner (level 5) can promote
    parameters = 'si'
}
```

**Option 2: Database-Only Control**
```lua
-- Remove promote command entirely from scripts/commands/
-- All GM level changes must go through web admin panel or direct database access
```

#### Web Admin Panel Security Features
```python
# Only accounts with priv >= 3 can access admin functions
if priv >= 3:  # Admin level
    session['user_type'] = 'admin'
    return redirect('/admin')
elif priv == 2:  # Moderator level
    session['user_type'] = 'moderator'
    return redirect('/admin')
else:  # Regular user
    session['user_type'] = 'user'
    return redirect('/portal')
```

### Permission Enforcement Mechanism

The server enforces permissions through **dual-layer security**:

#### 1. Code-Level Permission Checking
```cpp
// src/map/command_handler.cpp - Every GM command is validated
int8 permission = commandTable["cmdprops"]["permission"];
if (permission > PChar->m_GMlevel) {
    ShowWarning("Character %s attempting to use higher permission command %s", 
                PChar->name, cmdname);
    return -1; // Command denied
}
```

#### 2. Database-Level Authority
```sql
-- accounts table: Account-level privileges (1-5)
UPDATE accounts SET priv = 5 WHERE id = 1; -- Server owner

-- chars table: Character-level GM status (0-5)  
UPDATE chars SET gmlevel = 5 WHERE charid = 1; -- Server owner character
```

### Server Owner Designation

To establish **exclusive server owner control**:

#### 1. Database Setup
```sql
-- Create server owner account with maximum privileges
INSERT INTO accounts (id, login, password, priv) 
VALUES (1, 'serverowner', 'secure_hash', 5);

-- Ensure server owner character has maximum GM level
UPDATE chars SET gmlevel = 5 WHERE charid = 1;
```

#### 2. Security Hardening
```lua
-- Modify scripts/commands/promote.lua for owner-only promotion
local function error(player, msg)
    player:printToPlayer(msg)
    player:printToPlayer('Only the server owner can use this command.')
end

commandObj.onTrigger = function(player, target, level)
    -- Only allow level 5 (server owner) to promote others
    if player:getGMLevel() < 5 then
        error(player, 'Insufficient authority. Contact server owner.')
        return
    end
    
    -- Prevent anyone from promoting to level 5 except current level 5
    if level >= 5 and player:getGMLevel() < 5 then
        error(player, 'Cannot promote to server owner level.')
        return
    end
    
    -- Original promotion logic continues...
end
```

#### 3. Web Admin Configuration
```python
# In tools/web_admin.py - Add server owner protection
@app.route('/api/users/promote', methods=['POST'])
def api_promote_user():
    if session.get('user_id') != 1:  # Only server owner (account ID 1)
        return jsonify({'error': 'Only server owner can promote users'}), 403
    
    # Promotion logic for server owner only
```

## Administrative Workflows

### 1. Server Owner-Only GM Promotion
```lua
-- Server owner (Level 5) exclusive promotion workflow
local maxLevel = 4  -- Maximum level server owner can assign to others

-- Verify only server owner can promote
if player:getGMLevel() < 5 then
    error(player, 'Only server owner can promote users.')
    return
end

-- Prevent multiple server owners
if level >= 5 then
    error(player, 'Cannot create additional server owners.')
    return
end

-- Set new level and save (automatic audit logging)
target:setGMLevel(newLevel)
```

### 2. GM Demotion/Removal
```lua
-- When setting level to 0, remove all GM privileges
if newLevel == 0 then
    -- Remove god mode
    target:setCharVar('GodMode', 0)
    -- Remove all special effects
    -- Remove hide mode
    target:setCharVar('GMHidden', 0)
    target:setGMHidden(false)
    -- Reset visual indicator
    target:setVisibleGMLevel(0)
    -- Remove costume
    target:setCostume(0)
    -- Remove wallhack
    target:setWallhack(false)
end
```

### 3. Command Authorization
```lua
-- Each command checks permission level
commandObj.cmdprops = {
    permission = 1,  -- Minimum GM level required
    parameters = 'si'  -- Parameter format
}

-- Runtime validation
if player:getGMLevel() < requiredPermission then
    player:printToPlayer("Insufficient privileges")
    return
end
```

## Security Features

### 1. Complete Audit Logging
All GM commands are automatically logged with **comprehensive tracking**:
```sql
-- audit_gm table captures every GM action
INSERT INTO audit_gm (date_time, gm_name, command, full_string)
VALUES (NOW(), 'GMName', 'commandName', 'full command with parameters');

-- Audit configuration in map server
-- settings/default/map.lua: AUDIT_GM_CMD controls logging level
```

### 2. Hierarchical Permission Enforcement
- **Strict Level Control**: GMs cannot promote players to their own level or higher
- **Server Owner Protection**: Only level 5 can promote to levels 3-4
- **Cascade Demotion**: Higher-level GMs can demote lower-level GMs
- **Command Segregation**: Critical commands restricted to level 4-5 only

### 3. Multi-Layer Command Validation
```cpp
// Code-level validation (src/map/command_handler.cpp)
if (permission > PChar->m_GMlevel) {
    ShowWarning("Character %s attempting to use higher permission command %s", 
                PChar->name, cmdname);
    return -1;  // Immediate rejection
}

// Database-level persistence (src/map/utils/charutils.cpp)
void SaveCharGMLevel(CCharEntity* PChar) {
    db::preparedStmt("UPDATE chars SET gmlevel = ? WHERE charid = ? LIMIT 1",
                     PChar->m_GMlevel, PChar->id);
}
```

### 4. Admin Dashboard Integration
The web admin panel provides **centralized permission control**:
```python
# Session-based authentication with privilege checking
if session.get('user_type') not in ['admin']:
    return jsonify({'error': 'Unauthorized'}), 403

# Server owner exclusive functions
if session.get('user_id') != SERVER_OWNER_ID:
    return jsonify({'error': 'Server owner only'}), 403
```

### 5. Database-Level Security
```sql
-- Account privilege levels (accounts.priv)
-- 1 = Normal user, 2 = Moderator, 3-4 = Admin, 5 = Server Owner
ALTER TABLE accounts ADD CONSTRAINT check_priv 
CHECK (priv BETWEEN 1 AND 5);

-- Character GM levels (chars.gmlevel) 
-- 0 = Normal player, 1-5 = GM levels
ALTER TABLE chars ADD CONSTRAINT check_gmlevel 
CHECK (gmlevel BETWEEN 0 AND 5);
```

### 6. Auto-Authorization Prevention
**No Scripts Automatically Grant GM Privileges**:
- All GM promotions require **manual intervention**
- Database changes require **direct admin access**
- In-game promotions require **existing GM authority**
- Web panel promotions require **admin authentication**

**Verification Commands**:
```bash
# Check for any auto-promotion scripts
grep -r "setGMLevel\|priv.*=" scripts/ | grep -v "player:setGMLevel(0)"

# Verify no hardcoded privilege assignments
grep -r "priv.*[3-5]" sql/ scripts/ --exclude="*.md"

# Confirm GM command permission requirements
grep -r "permission.*=" scripts/commands/ | sort
```

## Configuration

### Server Settings
```lua
-- GM command processing in map server
-- Commands processed in scripts/commands/ directory
-- Each command is a separate Lua script with standardized structure
```

### Account Creation
```sql
-- Create GM account
INSERT INTO accounts (id, login, password, priv) 
VALUES (1001, 'gmuser', 'hashedpass', 3);

-- Set character GM level
UPDATE chars SET gmlevel = 3 WHERE charid = ?;
```

## Server Owner Exclusive Control Implementation

### Recommended Setup for Maximum Security

#### 1. Server Owner Account Creation
```sql
-- Create the server owner account (should be ID 1)
INSERT INTO accounts (id, login, password, priv, status) 
VALUES (1, 'serverowner', SHA2('secure_password', 256), 5, 1);

-- Create server owner character
INSERT INTO chars (charid, accid, charname, gmlevel) 
VALUES (1, 1, 'ServerOwner', 5);
```

#### 2. Disable In-Game GM Promotion Commands
```bash
# Option A: Remove promote command entirely
mv scripts/commands/promote.lua scripts/commands/promote.lua.disabled

# Option B: Restrict to server owner only
# Edit scripts/commands/promote.lua:
# commandObj.cmdprops = { permission = 5, parameters = 'si' }
```

#### 3. Web Admin Panel Configuration
```python
# Add to tools/web_admin.py for server owner exclusive control
SERVER_OWNER_ACCOUNT_ID = 1

def require_server_owner():
    if session.get('user_id') != SERVER_OWNER_ACCOUNT_ID:
        return jsonify({'error': 'Server owner access required'}), 403

@app.route('/api/admin/promote', methods=['POST'])
def api_admin_promote():
    require_server_owner()
    # GM promotion logic here
```

#### 4. Database Trigger for GM Level Protection
```sql
-- Prevent unauthorized GM level changes
DELIMITER $$
CREATE TRIGGER prevent_unauthorized_gm_promotion
BEFORE UPDATE ON chars
FOR EACH ROW
BEGIN
    -- Only allow gmlevel changes if made by server owner or through admin panel
    IF NEW.gmlevel > OLD.gmlevel AND NEW.gmlevel > 0 THEN
        -- Log unauthorized attempts
        INSERT INTO security_log (timestamp, event_type, details)
        VALUES (NOW(), 'UNAUTHORIZED_GM_PROMOTION', 
                CONCAT('Attempt to promote character ', NEW.charid, ' to level ', NEW.gmlevel));
        
        -- Block unauthorized promotion
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'GM promotions must be authorized by server owner';
    END IF;
END$$
DELIMITER ;
```

## Best Practices for Server Owner Control

### 1. Exclusive Server Owner Authority
- **Only ONE server owner account**: Account ID 1 with priv level 5
- **No automatic GM grants**: All promotions require manual server owner approval
- **Admin dashboard control**: Use web panel for all user management
- **Regular privilege audits**: Monthly review of all GM accounts

### 2. Hierarchical Control Structure
```
Level 5 (Server Owner) → Can promote to levels 1-4, exclusive server control
Level 4 (Lead Admin)   → Can promote to levels 1-3, server operations
Level 3 (Senior Admin) → Can promote to levels 1-2, content management  
Level 2 (Moderator)    → Can promote to level 1, user management
Level 1 (Basic GM)     → Cannot promote others, basic support only
```

### 3. Security Implementation Checklist
- [ ] Server owner account created with unique credentials
- [ ] In-game promotion commands disabled or restricted to level 5
- [ ] Web admin panel configured for server owner exclusive control
- [ ] Database triggers implemented to prevent unauthorized promotions
- [ ] Audit logging enabled for all GM command usage
- [ ] Regular backups of accounts and chars tables
- [ ] Strong password requirements enforced
- [ ] Two-factor authentication implemented (if available)

### 4. Monitoring and Alerts
```bash
# Daily GM privilege audit script
#!/bin/bash
echo "=== GM Privilege Audit $(date) ==="
mysql -u root -p xidb -e "
SELECT a.login, a.priv, c.charname, c.gmlevel 
FROM accounts a 
LEFT JOIN chars c ON a.id = c.accid 
WHERE a.priv > 1 OR c.gmlevel > 0 
ORDER BY a.priv DESC, c.gmlevel DESC;"

# Check for unauthorized GM level changes
mysql -u root -p xidb -e "
SELECT * FROM audit_gm 
WHERE command = 'promote' 
AND date_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR);"
```

### 5. Emergency Procedures
```sql
-- Emergency GM privilege revocation (server owner only)
UPDATE chars SET gmlevel = 0 WHERE charid = ? AND charid != 1;
UPDATE accounts SET priv = 1 WHERE id = ? AND id != 1;

-- Emergency server owner password reset
UPDATE accounts SET password = SHA2('new_secure_password', 256) WHERE id = 1;
```

## Command Reference Summary

| Permission Level | Commands Available | Total Count |
|------------------|-------------------|-------------|
| **0** | Player commands only | 3 |
| **1** | Basic GM operations | 165 |
| **2** | Enhanced management | 1 |
| **3** | Advanced administration | 9 |
| **4** | System operations | 4 |
| **5** | Full server control | 15 |

## Error Handling

### Common Issues
```lua
-- Invalid target
error(player, 'Player named "name" not found!')

-- Insufficient privileges  
error(player, 'You can not use this command on same or higher tiered GMs.')

-- Invalid parameters
error(player, 'Invalid level. Must be 0 to X.')
```

### Debug Commands
```lua
-- Check current status
!where          -- Show position and zone
!getstats       -- Display character statistics
!geteffects     -- List active status effects
!checkvar       -- Examine server variables
```

## API Integration

### Lua Script Access
```lua
-- Available in all GM command scripts
local player = GetPlayerByName(name)
local gmlevel = player:getGMLevel()
local visible = player:getVisibleGMLevel()

-- Validation helpers
if not player or player:getGMLevel() < requiredLevel then
    return error(executor, "Insufficient access")
end
```

### C++ Backend
```cpp
// Core implementation in lua_baseentity.cpp
uint8 CLuaBaseEntity::getGMLevel();
void CLuaBaseEntity::setGMLevel(uint8 level);

// Database persistence in charutils.cpp
void charutils::SaveCharGMLevel(CCharEntity* PChar);
```

This GM system provides comprehensive administrative control while maintaining security and audit capabilities for effective Final Fantasy XI server management.