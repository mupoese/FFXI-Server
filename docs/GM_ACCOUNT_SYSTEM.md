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

## Administrative Workflows

### 1. New GM Promotion
```lua
-- Verify promoter has sufficient level
local maxLevel = promoter:getGMLevel() - 1

-- Check target is not equal/higher level
if target:getGMLevel() >= promoter:getGMLevel() then
    -- Denied: Cannot promote equals or superiors
    return false
end

-- Set new level and save
target:setGMLevel(newLevel)
-- Automatically logged to audit_gm table
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

### 1. Audit Logging
All GM commands are automatically logged:
```sql
INSERT INTO audit_gm (date_time, gm_name, command, full_string)
VALUES (NOW(), 'GMName', 'commandName', 'full command with parameters');
```

### 2. Hierarchical Permissions
- GMs cannot promote players to their own level or higher
- Higher-level GMs can demote lower-level GMs
- Level 5 (Super Admin) has unrestricted access

### 3. Command Validation
- Parameter validation for all commands
- Target existence verification
- Permission checking before execution
- Error handling and feedback

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

## Best Practices

### 1. GM Level Assignment
- **Level 1**: New GMs, basic support tasks
- **Level 2**: Experienced GMs, event management
- **Level 3**: Senior staff, content administration
- **Level 4**: Lead staff, server operations
- **Level 5**: Technical administrators only

### 2. Command Usage Guidelines
- Use lowest effective permission level
- Document administrative actions
- Test commands in development environment
- Coordinate major operations with team

### 3. Security Recommendations
- Regular audit log review
- Periodic GM level assessment
- Strong password requirements
- Limited Level 5 access

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