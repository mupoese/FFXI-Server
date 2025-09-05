# FFXI Server GM Account System Documentation

## Overview

The Final Fantasy XI Server implements a comprehensive Game Master (GM) account system with 6 privilege levels (0-5) providing administrative control over server operations, player management, and content administration. This system includes 197+ GM commands, special abilities, and comprehensive audit tracking.

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

#### Audit Table
```sql
CREATE TABLE audit_gm (
  date_time datetime NOT NULL,
  gm_name varchar(16) NOT NULL,
  command varchar(40) NOT NULL,
  full_string varchar(200) NOT NULL,
  PRIMARY KEY (date_time, gm_name)
);
```

## Core GM Functions

### Level Management
```lua
-- Check GM level
local level = player:getGMLevel()
if level >= 3 then
    -- Authorized for advanced operations
end

-- Set GM level (requires higher privilege)
player:setGMLevel(newLevel)

-- Visual GM indicator management
player:setVisibleGMLevel(visibleLevel)  -- 0-7 for client display
local visible = player:getVisibleGMLevel()
```

### Character Entity Implementation
```cpp
class CCharEntity {
    uint8 m_GMlevel;    // GM privilege level (0-5)
    
    uint8 getGMLevel() const { return m_GMlevel; }
    void setGMLevel(uint8 level) { 
        m_GMlevel = level;
        charutils::SaveCharGMLevel(this);
    }
};
```

## GM Command Categories

### 1. Player Management (Permission 1-3)
| Command | Permission | Description |
|---------|------------|-------------|
| `promote` | 1 | Change player GM level |
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