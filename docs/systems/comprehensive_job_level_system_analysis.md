# Comprehensive FFXI Server Job Level System Analysis

## Overview

This document provides a complete analysis of the Final Fantasy XI Server job and level system implementation, covering main job levels, sub job levels, advanced progression systems, and database integration.

## Table of Contents

1. [Job System Architecture](#job-system-architecture)
2. [Level System Implementation](#level-system-implementation)
3. [Advanced Progression Systems](#advanced-progression-systems)
4. [Database Structure](#database-structure)
5. [Level Restrictions and Caps](#level-restrictions-and-caps)
6. [Experience and Progression Mechanics](#experience-and-progression-mechanics)
7. [Job Points System](#job-points-system)
8. [Merit Points System](#merit-points-system)
9. [Configuration and Settings](#configuration-and-settings)
10. [Administrative Commands](#administrative-commands)

---

## Job System Architecture

### Available Jobs

The server supports all 22 standard FFXI jobs plus special job types:

```cpp
enum JOBTYPE : uint8
{
    JOB_NON = 0,  // No Job
    JOB_WAR = 1,  // Warrior
    JOB_MNK = 2,  // Monk
    JOB_WHM = 3,  // White Mage
    JOB_BLM = 4,  // Black Mage
    JOB_RDM = 5,  // Red Mage
    JOB_THF = 6,  // Thief
    JOB_PLD = 7,  // Paladin
    JOB_DRK = 8,  // Dark Knight
    JOB_BST = 9,  // Beastmaster
    JOB_BRD = 10, // Bard
    JOB_RNG = 11, // Ranger
    JOB_SAM = 12, // Samurai
    JOB_NIN = 13, // Ninja
    JOB_DRG = 14, // Dragoon
    JOB_SMN = 15, // Summoner
    JOB_BLU = 16, // Blue Mage
    JOB_COR = 17, // Corsair
    JOB_PUP = 18, // Puppetmaster
    JOB_DNC = 19, // Dancer
    JOB_SCH = 20, // Scholar
    JOB_GEO = 21, // Geomancer
    JOB_RUN = 22, // Rune Fencer
    JOB_MON = 23, // Monstrosity (Special)
};
#define MAX_JOBTYPE 24
```

### Job Structure

Each character has a `jobs_t` structure containing:

```cpp
struct jobs_t
{
    uint32 unlocked;         // Bitmask of unlocked jobs
    uint8  job[MAX_JOBTYPE]; // Current levels of each job (0-99)
    uint16 exp[MAX_JOBTYPE]; // Experience points for each job
    uint8  genkai;           // Maximum level cap achieved
};
```

---

## Level System Implementation

### Level Ranges

1. **Standard Levels**: 1-99 for both main job and sub job
2. **Sub Job Level Cap**: Sub job is capped at (Main Job Level - 1) / 2
3. **Genkai System**: Level cap progression from 50 → 55 → 60 → 65 → 70 → 75 → 80 → 85 → 90 → 95 → 99

### Level Calculation Logic

```cpp
// Main job level is stored directly
uint8 mainJobLevel = PChar->jobs.job[PChar->GetMJob()];

// Sub job level calculation
uint8 subJobLevel = PChar->jobs.job[PChar->GetSJob()];
uint8 effectiveSubLevel = std::min(subJobLevel, (mainJobLevel - 1) / 2);
```

### Level Restrictions

Players can have level restrictions applied for:
- Level sync parties
- Battlefield restrictions  
- Event limitations
- Administrative restrictions

```cpp
void SetLevelRestriction(CCharEntity* PChar, uint8 lvl);
```

---

## Advanced Progression Systems

### 1. Merit Points System (Level 75+)

Available when main job reaches level 75 and has maximum experience.

**Merit Categories:**
- **HP/MP**: Health and Magic Point bonuses
- **Attributes**: STR, DEX, VIT, AGI, INT, MND, CHR
- **Combat Skills**: Weapon and defensive skills
- **Magic Skills**: All magic skill categories
- **Others**: Special combat bonuses
- **Job-Specific**: Two categories per job (Group 1 & Group 2)
- **Weapon Skills**: Merit-only weapon skills

**Merit Point Limits:**
```cpp
#define MERITS_COUNT 305 // 5 full packages of 61 elements
```

### 2. Job Points System (Level 99)

Available when main job reaches level 99.

**Job Point Categories:**
```cpp
enum JOBPOINT_CATEGORY : uint16
{
    JPCATEGORY_WAR = 0x020, // Each job has dedicated category
    JPCATEGORY_MNK = 0x040,
    // ... (continues for all jobs)
    JPCATEGORY_RUN = 0x2C0,
};
```

**Job Point Features:**
- **Capacity Points**: Earned from experience at level 99
- **Job Point Upgrades**: 10 types per job, up to 20 levels each
- **Job Point Gifts**: Automatic bonuses at certain JP totals
- **Maximum JP**: 500 Job Points per category
- **Maximum Capacity**: 30,000 Capacity Points per job

### 3. Monstrosity System

Special progression system allowing players to play as monsters:
- Separate leveling mechanics
- Species-specific progression
- Independent from standard job system

---

## Database Structure

### Character Jobs Table (`char_jobs`)

```sql
CREATE TABLE char_jobs (
  charid int(10) unsigned NOT NULL,
  unlocked int(10) unsigned NOT NULL DEFAULT '126', -- Bitmask of unlocked jobs
  genkai tinyint(2) unsigned NOT NULL DEFAULT '50', -- Level cap
  war tinyint(2) unsigned NOT NULL DEFAULT '1',     -- Individual job levels
  mnk tinyint(2) unsigned NOT NULL DEFAULT '1',
  whm tinyint(2) unsigned NOT NULL DEFAULT '1',
  blm tinyint(2) unsigned NOT NULL DEFAULT '1',
  rdm tinyint(2) unsigned NOT NULL DEFAULT '1',
  thf tinyint(2) unsigned NOT NULL DEFAULT '1',
  pld tinyint(2) unsigned NOT NULL DEFAULT '0',     -- Advanced jobs start at 0
  -- ... (continues for all jobs)
  PRIMARY KEY (charid)
);
```

### Character Experience Table (`char_exp`)

```sql
CREATE TABLE char_exp (
  charid int(10) unsigned NOT NULL,
  mode tinyint(1) unsigned NOT NULL DEFAULT '0',    -- Merit mode flag
  war smallint(5) unsigned NOT NULL DEFAULT '0',    -- Experience per job
  mnk smallint(5) unsigned NOT NULL DEFAULT '0',
  -- ... (continues for all jobs)
  merits tinyint(2) unsigned NOT NULL DEFAULT '0',  -- Merit points
  limits smallint(5) unsigned NOT NULL DEFAULT '0', -- Limit points
  PRIMARY KEY (charid)
);
```

### Experience Table (`exp_table`)

```sql
CREATE TABLE exp_table (
  level tinyint(2) NOT NULL,
  r1 smallint(4) unsigned NOT NULL DEFAULT '0',  -- Levels 1-5
  r2 smallint(4) unsigned NOT NULL DEFAULT '0',  -- Levels 6-10
  -- ... (continues through r20 for levels 96-99)
  PRIMARY KEY (level)
);
```

---

## Level Restrictions and Caps

### Genkai (Level Cap) System

The genkai system controls maximum achievable levels:

```cpp
// Level cap enforcement
if (PChar->jobs.job[PChar->GetMJob()] >= PChar->jobs.genkai)
{
    // Player is at level cap - award limit points instead of exp
    PChar->jobs.exp[PChar->GetMJob()] = GetExpNEXTLevel(PChar->jobs.job[PChar->GetMJob()]) - 1;
}
```

**Genkai Progression:**
1. **Level 50**: Default starting cap
2. **Level 55**: Genkai 1 quest completion
3. **Level 60**: Genkai 2 quest completion  
4. **Level 65**: Genkai 3 quest completion
5. **Level 70**: Genkai 4 quest completion
6. **Level 75**: Genkai 5 quest completion
7. **Level 80**: Abyssea expansion access
8. **Level 85**: Additional Abyssea progress
9. **Level 90**: Advanced Abyssea completion
10. **Level 95**: Seekers of Adoulin access
11. **Level 99**: Final level cap

### Sub Job Restrictions

Sub job level is automatically calculated and capped:

```cpp
uint8 GetSLevel() const 
{ 
    return std::min(jobs.job[GetSJob()], (uint8)((jobs.job[GetMJob()] - 1) / 2));
}
```

**Sub Job Level Examples:**
- Main Job 20 → Sub Job cap 9
- Main Job 50 → Sub Job cap 24  
- Main Job 75 → Sub Job cap 37
- Main Job 99 → Sub Job cap 49

---

## Experience and Progression Mechanics

### Experience Calculation

Experience is calculated based on:
1. **Character Level**: Current main job level
2. **Monster Level**: Target's level
3. **Level Difference**: Bonus/penalty based on gap
4. **Party Size**: Experience sharing
5. **Chain Bonus**: Consecutive kills
6. **Capacity Chain**: Consecutive capacity point kills

```cpp
uint32 GetBaseExp(uint8 charlvl, uint8 moblvl);
uint32 GetExpNEXTLevel(uint8 charlvl);
```

### Experience Distribution

```cpp
void DistributeExperiencePoints(CCharEntity* PChar, CMobEntity* PMob);
void AddExperiencePoints(bool expFromRaise, CCharEntity* PChar, CBaseEntity* PMob, 
                        uint32 exp, EMobDifficulty mobCheck, bool isexpchain);
```

### Level Up Process

When sufficient experience is gained:

1. **Level Check**: Verify if enough experience for next level
2. **Cap Check**: Ensure level doesn't exceed genkai
3. **Level Increase**: Increment job level
4. **Stat Recalculation**: Update all character statistics
5. **Skill Updates**: Refresh available abilities and spells
6. **Trait Updates**: Apply new job traits
7. **Equipment Check**: Validate equipment requirements

---

## Job Points System

### Capacity Point Earning

At level 99, experience is converted to Capacity Points:

```cpp
bool AddCapacityPoints(uint16 amount);
uint32 GetCapacityPoints();
void SetCapacityPoints(uint16 amount);
```

### Job Point Categories

Each job has 10 Job Point types:

```cpp
// Example for Warrior
JP_MIGHTY_STRIKES_EFFECT = JPCATEGORY_WAR + 0x00,
JP_BRAZEN_RUSH_EFFECT    = JPCATEGORY_WAR + 0x02,
JP_BERSERK_EFFECT        = JPCATEGORY_WAR + 0x01,
// ... (continues for 10 types per job)
```

### Job Point Gifts

Automatic bonuses awarded at specific JP totals:

```cpp
struct JobPointGifts_t
{
    uint16 jpRequired; // JP required for gift
    uint16 modId;      // Modifier type
    int16  value;      // Bonus value
};
```

**Gift Thresholds:** 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1200 JP

---

## Merit Points System

### Merit Point Earning

Available at level 75+ when at maximum experience:

```cpp
if (PChar->MeritMode && PChar->jobs.job[PChar->GetMJob()] > 74)
{
    // Award merit/limit points instead of experience
}
```

### Merit Categories

1. **Group I Merits** (Base Attributes & Skills)
   - HP/MP increases
   - Attribute bonuses (STR, DEX, etc.)
   - Combat skills
   - Magic skills
   - Misc bonuses

2. **Group II Merits** (Job-Specific)
   - Category 1: Job ability enhancements
   - Category 2: Job-specific abilities and spells

### Merit Point Limits

```cpp
#define MERITS_COUNT 305
```

**Point Distribution:**
- **Maximum Merit Points**: Varies by category
- **Point Cost**: Increases per upgrade level
- **Reset Options**: Full reset available with items

---

## Configuration and Settings

### Server Settings

Job and level settings can be configured in `settings/main.lua`:

```lua
-- Experience rate modifiers
xi.settings.map.EXP_RATE = 1.0

-- Level cap settings  
xi.settings.map.MAX_LEVEL = 99

-- Job point settings
xi.settings.map.JP_MODE = 1

-- Merit point settings
xi.settings.map.MERIT_MODE = 1
```

### Database Configuration

Experience tables can be modified to adjust progression curves:

```sql
-- Custom experience requirements
UPDATE exp_table SET r20 = 2000 WHERE level = 15; -- Modify level 96-99 experience for level differential +15
```

---

## Administrative Commands

### Job Management Commands

```lua
-- Change player job
!changejob <player> <job_id>

-- Change player subjob  
!changesjob <player> <job_id>

-- Set job points
!setjobpoints <player> <amount>

-- Set capacity points
!setcapacitypoints <player> <amount>

-- Master job (set to max level)
!masterjob <player> <job_id>
```

### Level Management Commands

```lua
-- Set player level
!level <player> <level>

-- Set all jobs to max
!maxlevel <player>

-- Add experience
!addexp <player> <amount>

-- Set genkai level
!genkai <player> <level_cap>
```

### Merit System Commands

```lua
-- Add merit points
!addmerit <player> <amount>

-- Set limit points  
!setlimit <player> <amount>

-- Reset merits
!resetmerits <player>
```

---

## Technical Implementation Details

### Character Loading Process

1. **Load Job Data**: Read from `char_jobs` table
2. **Load Experience**: Read from `char_exp` table  
3. **Calculate Effective Levels**: Apply restrictions and caps
4. **Load Job Points**: Read job point progression
5. **Load Merits**: Read merit point allocation
6. **Apply Modifiers**: Calculate final statistics

### Level Progression Validation

```cpp
// Ensure level doesn't exceed cap
if (PChar->jobs.job[PChar->GetMJob()] >= PChar->jobs.genkai)
{
    PChar->jobs.exp[PChar->GetMJob()] = GetExpNEXTLevel(PChar->jobs.job[PChar->GetMJob()]) - 1;
}

// Apply level restrictions
if (PChar->m_LevelRestriction > 0 && PChar->m_LevelRestriction < PChar->GetMLevel())
{
    PChar->SetMLevel(PChar->m_LevelRestriction);
}
```

### Database Synchronization

Character progression is automatically saved to database:
- Experience changes saved immediately
- Job point changes saved on allocation
- Merit changes saved on spending
- Level changes trigger full character save

---

## System Integration

### Interaction with Other Systems

1. **Spell System**: Level requirements for spell learning
2. **Ability System**: Job and level requirements for abilities
3. **Equipment System**: Level and job restrictions on gear
4. **Mission System**: Level requirements for progression
5. **Battlefield System**: Level restrictions and level caps
6. **Party System**: Level sync functionality
7. **PvP System**: Level brackets and restrictions

### Performance Considerations

- Job point calculations cached for performance
- Merit modifiers applied once and cached
- Experience calculations optimized for party scenarios
- Database updates batched to reduce I/O

---

## Conclusion

The FFXI Server implements a comprehensive job and level system that faithfully recreates the retail experience while providing administrative flexibility. The system supports:

- **24 job types** with individual progression
- **Level 1-99 progression** with genkai cap system
- **Merit Points** for level 75+ enhancement
- **Job Points** for level 99 specialization
- **Flexible database structure** for customization
- **Administrative tools** for server management

This implementation provides the foundation for authentic FFXI gameplay while maintaining the flexibility needed for private server administration and customization.