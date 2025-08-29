-----------------------------------
-- Enhanced Trust AI System
-- Phase 4: Retail-accurate trust behaviors and advanced AI
-----------------------------------
require('scripts/globals/trust')
require('scripts/globals/magic')
require('scripts/globals/content_validation')
-----------------------------------
xi = xi or {}
xi.trust = xi.trust or {}
xi.trust.enhanced = xi.trust.enhanced or {}

-- Trust AI behavior types
xi.trust.enhanced.behaviorType =
{
    AGGRESSIVE     = 1,  -- Focuses on damage dealing
    DEFENSIVE      = 2,  -- Focuses on protection and healing
    SUPPORT        = 3,  -- Focuses on buffs and debuffs
    BALANCED       = 4,  -- Balanced approach
    SPECIALIST     = 5,  -- Job-specific specialized behavior
}

-- Trust combat roles
xi.trust.enhanced.combatRole =
{
    TANK           = 1,
    DAMAGE_DEALER  = 2,
    HEALER         = 3,
    SUPPORT        = 4,
    HYBRID         = 5,
}

-- Trust decision making priorities
xi.trust.enhanced.priority =
{
    CRITICAL       = 10,  -- Life-threatening situations
    HIGH           = 8,   -- Important tactical decisions
    MEDIUM         = 5,   -- Standard combat actions
    LOW            = 3,   -- Convenience actions
    MINIMAL        = 1,   -- Background maintenance
}

-- Enhanced Trust AI configuration
xi.trust.enhanced.aiConfig = {
    -- Healing thresholds
    healing = {
        emergency = 0.25,    -- 25% HP - Emergency healing
        urgent = 0.50,       -- 50% HP - Urgent healing
        routine = 0.75,      -- 75% HP - Routine healing
    },
    
    -- Buffing preferences
    buffing = {
        selfBuffPriority = 0.8,     -- Prioritize self-buffs
        masterBuffPriority = 0.9,   -- High priority for master buffs
        partyBuffPriority = 0.6,    -- Medium priority for party buffs
    },
    
    -- Combat behavior
    combat = {
        aggroManagement = true,     -- Manage enmity intelligently
        wsCoordination = true,      -- Coordinate weapon skills
        spellInterruption = true,   -- Interrupt enemy spells
        statusEffectCleansing = true, -- Remove harmful effects
    },
    
    -- Positioning
    positioning = {
        maintainDistance = true,    -- Maintain appropriate combat distance
        avoidAoE = true,           -- Move away from AoE attacks
        formationKeeping = true,   -- Maintain party formation
    },
    
    -- Subjob integration
    subjob = {
        useSubjobAbilities = true,  -- Allow use of subjob abilities
        subjobPriority = 0.4,       -- Priority of subjob abilities vs main job
        intelligentSwitching = true, -- Switch between main/sub focus based on situation
        mpConservation = true,      -- Conserve MP for subjob abilities when needed
    },
}

-- Subjob behavior combinations
xi.trust.enhanced.subjobBehaviors = {
    -- Popular and effective subjob combinations
    [xi.job.WAR] = {
        [xi.job.NIN] = { -- WAR/NIN - Evasion tanking
            abilities = { "utsusemi", "tonko" },
            priority = 0.6,
            conditions = { "lowHP", "noShadows" },
        },
        [xi.job.MNK] = { -- WAR/MNK - Counter tanking
            abilities = { "counterstance", "dodge" },
            priority = 0.4,
            conditions = { "melee_combat" },
        },
        [xi.job.WHM] = { -- WAR/WHM - Self-sufficient tanking
            abilities = { "cure", "healing_breeze" },
            priority = 0.5,
            conditions = { "lowHP", "noHealer" },
        },
    },
    
    [xi.job.MNK] = {
        [xi.job.WAR] = { -- MNK/WAR - Aggressive melee
            abilities = { "berserk", "warcry" },
            priority = 0.5,
            conditions = { "combat", "highTP" },
        },
        [xi.job.NIN] = { -- MNK/NIN - Evasive damage dealer
            abilities = { "utsusemi" },
            priority = 0.7,
            conditions = { "noShadows", "takingDamage" },
        },
        [xi.job.WHM] = { -- MNK/WHM - Self-healing
            abilities = { "cure", "poisona" },
            priority = 0.4,
            conditions = { "lowHP", "statusAilment" },
        },
    },
    
    [xi.job.WHM] = {
        [xi.job.BLM] = { -- WHM/BLM - Offensive healing
            abilities = { "stone", "water", "aero", "fire", "blizzard", "thunder" },
            priority = 0.3,
            conditions = { "partyHealthy", "enemyWeak" },
        },
        [xi.job.RDM] = { -- WHM/RDM - Enhanced support
            abilities = { "dispel", "gravity", "bind" },
            priority = 0.4,
            conditions = { "enemyBuffed", "emergencyControl" },
        },
        [xi.job.SMN] = { -- WHM/SMN - Avatar support
            abilities = { "carbuncle" },
            priority = 0.2,
            conditions = { "needExtraHealing" },
        },
    },
    
    [xi.job.BLM] = {
        [xi.job.RDM] = { -- BLM/RDM - MP management
            abilities = { "refresh", "convert" },
            priority = 0.6,
            conditions = { "lowMP", "needSustain" },
        },
        [xi.job.WHM] = { -- BLM/WHM - Emergency healing
            abilities = { "cure", "poisona" },
            priority = 0.4,
            conditions = { "emergencyHP", "noHealer" },
        },
        [xi.job.NIN] = { -- BLM/NIN - Survivability
            abilities = { "utsusemi" },
            priority = 0.7,
            conditions = { "noShadows", "beingTargeted" },
        },
    },
    
    [xi.job.RDM] = {
        [xi.job.BLM] = { -- RDM/BLM - Enhanced nuking
            abilities = { "manafont" },
            priority = 0.5,
            conditions = { "lowMP", "needBurst" },
        },
        [xi.job.WHM] = { -- RDM/WHM - Enhanced healing
            abilities = { "cure" },
            priority = 0.6,
            conditions = { "lowHP", "emergencyHealing" },
        },
        [xi.job.NIN] = { -- RDM/NIN - Melee hybrid
            abilities = { "utsusemi" },
            priority = 0.5,
            conditions = { "noShadows", "meleeMode" },
        },
    },
    
    [xi.job.THF] = {
        [xi.job.NIN] = { -- THF/NIN - Dual wield
            abilities = { "utsusemi", "dual_wield" },
            priority = 0.8,
            conditions = { "noShadows", "melee_combat" },
        },
        [xi.job.RNG] = { -- THF/RNG - Ranged support
            abilities = { "shadowbind", "eagle_eye_shot" },
            priority = 0.4,
            conditions = { "needRanged", "enemyFar" },
        },
        [xi.job.WAR] = { -- THF/WAR - Aggressive thief
            abilities = { "berserk", "provoke" },
            priority = 0.3,
            conditions = { "combat", "needAggro" },
        },
    },
    
    [xi.job.PLD] = {
        [xi.job.WAR] = { -- PLD/WAR - Aggressive tanking
            abilities = { "berserk", "warcry" },
            priority = 0.4,
            conditions = { "needAggro", "combat" },
        },
        [xi.job.WHM] = { -- PLD/WHM - Enhanced healing
            abilities = { "cure", "protect", "shell" },
            priority = 0.7,
            conditions = { "lowHP", "needBuff" },
        },
        [xi.job.RDM] = { -- PLD/RDM - Utility tanking
            abilities = { "refresh", "phalanx" },
            priority = 0.5,
            conditions = { "lowMP", "needDefense" },
        },
    },
    
    [xi.job.DRK] = {
        [xi.job.WAR] = { -- DRK/WAR - Berserker
            abilities = { "berserk", "warcry" },
            priority = 0.6,
            conditions = { "combat", "highDamage" },
        },
        [xi.job.SAM] = { -- DRK/SAM - Weapon skill specialist
            abilities = { "meditate", "third_eye" },
            priority = 0.5,
            conditions = { "lowTP", "needDefense" },
        },
        [xi.job.BLM] = { -- DRK/BLM - Dark magic focus
            abilities = { "elemental_seal", "manafont" },
            priority = 0.4,
            conditions = { "lowMP", "darkMagic" },
        },
    },
    
    [xi.job.BST] = {
        [xi.job.WHM] = { -- BST/WHM - Pet healing
            abilities = { "cure" },
            priority = 0.5,
            conditions = { "petLowHP", "lowHP" },
        },
        [xi.job.NIN] = { -- BST/NIN - Survivability
            abilities = { "utsusemi" },
            priority = 0.6,
            conditions = { "noShadows", "combat" },
        },
        [xi.job.RNG] = { -- BST/RNG - Ranged combat
            abilities = { "shadowbind", "eagle_eye_shot" },
            priority = 0.3,
            conditions = { "petEngaged", "needRanged" },
        },
    },
    
    [xi.job.BRD] = {
        [xi.job.WHM] = { -- BRD/WHM - Healing support
            abilities = { "cure", "poisona" },
            priority = 0.5,
            conditions = { "lowHP", "statusAilment" },
        },
        [xi.job.BLM] = { -- BRD/BLM - Elemental songs
            abilities = { "stone", "water" },
            priority = 0.3,
            conditions = { "needDamage", "partyBuffed" },
        },
        [xi.job.RDM] = { -- BRD/RDM - Enhanced support
            abilities = { "dispel", "gravity" },
            priority = 0.4,
            conditions = { "enemyBuffed", "needControl" },
        },
    },
    
    [xi.job.RNG] = {
        [xi.job.NIN] = { -- RNG/NIN - Evasive archer
            abilities = { "utsusemi" },
            priority = 0.7,
            conditions = { "noShadows", "beingTargeted" },
        },
        [xi.job.WAR] = { -- RNG/WAR - Aggressive archer
            abilities = { "berserk" },
            priority = 0.4,
            conditions = { "combat", "needDamage" },
        },
        [xi.job.SAM] = { -- RNG/SAM - Meditative archer
            abilities = { "meditate", "third_eye" },
            priority = 0.3,
            conditions = { "lowTP", "needTP" },
        },
    },
    
    [xi.job.SAM] = {
        [xi.job.WAR] = { -- SAM/WAR - Berserker samurai
            abilities = { "berserk", "warcry" },
            priority = 0.5,
            conditions = { "combat", "needDamage" },
        },
        [xi.job.RNG] = { -- SAM/RNG - Ranged samurai
            abilities = { "shadowbind", "eagle_eye_shot" },
            priority = 0.3,
            conditions = { "needRanged", "TPBuilding" },
        },
        [xi.job.THF] = { -- SAM/THF - SATA weaponskills
            abilities = { "sneak_attack", "trick_attack" },
            priority = 0.6,
            conditions = { "weaponskillReady", "positioning" },
        },
    },
    
    [xi.job.NIN] = {
        [xi.job.WAR] = { -- NIN/WAR - Aggressive ninja
            abilities = { "berserk", "provoke" },
            priority = 0.4,
            conditions = { "combat", "needAggro" },
        },
        [xi.job.RNG] = { -- NIN/RNG - Ranged ninja
            abilities = { "shadowbind" },
            priority = 0.3,
            conditions = { "needRanged", "enemyFar" },
        },
        [xi.job.THF] = { -- NIN/THF - Stealth ninja
            abilities = { "sneak_attack", "trick_attack" },
            priority = 0.5,
            conditions = { "positioning", "highTP" },
        },
    },
    
    [xi.job.DRG] = {
        [xi.job.WAR] = { -- DRG/WAR - Aggressive dragoon
            abilities = { "berserk", "warcry" },
            priority = 0.5,
            conditions = { "combat", "wyvernAlive" },
        },
        [xi.job.SAM] = { -- DRG/SAM - Weapon skill specialist
            abilities = { "meditate", "third_eye" },
            priority = 0.4,
            conditions = { "lowTP", "needDefense" },
        },
        [xi.job.WHM] = { -- DRG/WHM - Wyvern healing
            abilities = { "cure", "poisona" },
            priority = 0.6,
            conditions = { "wyvernLowHP", "lowHP" },
        },
    },
    
    [xi.job.SMN] = {
        [xi.job.WHM] = { -- SMN/WHM - Enhanced healing
            abilities = { "cure", "protect" },
            priority = 0.5,
            conditions = { "lowHP", "noAvatar" },
        },
        [xi.job.BLM] = { -- SMN/BLM - Elemental focus
            abilities = { "elemental_seal", "manafont" },
            priority = 0.4,
            conditions = { "lowMP", "avatarCombat" },
        },
        [xi.job.RDM] = { -- SMN/RDM - MP management
            abilities = { "refresh", "convert" },
            priority = 0.6,
            conditions = { "lowMP", "avatarActive" },
        },
    },
}

-- Enhanced trust behavior patterns based on job
xi.trust.enhanced.jobBehaviors = {
    [xi.job.WAR] = {
        role = xi.trust.enhanced.combatRole.TANK,
        behavior = xi.trust.enhanced.behaviorType.AGGRESSIVE,
        priorities = {
            { action = "provoke", priority = xi.trust.enhanced.priority.HIGH, condition = "lowEnmity" },
            { action = "cure", priority = xi.trust.enhanced.priority.MEDIUM, condition = "lowHP" },
            { action = "weaponskill", priority = xi.trust.enhanced.priority.MEDIUM, condition = "highTP" },
            { action = "berserk", priority = xi.trust.enhanced.priority.MEDIUM, condition = "combat" },
            { action = "defender", priority = xi.trust.enhanced.priority.LOW, condition = "lowHP" },
        },
    },
    
    [xi.job.MNK] = {
        role = xi.trust.enhanced.combatRole.DAMAGE_DEALER,
        behavior = xi.trust.enhanced.behaviorType.AGGRESSIVE,
        priorities = {
            { action = "boost", priority = xi.trust.enhanced.priority.HIGH, condition = "noBuff" },
            { action = "focus", priority = xi.trust.enhanced.priority.HIGH, condition = "noBuff" },
            { action = "dodge", priority = xi.trust.enhanced.priority.MEDIUM, condition = "lowHP" },
            { action = "weaponskill", priority = xi.trust.enhanced.priority.HIGH, condition = "highTP" },
            { action = "chakra", priority = xi.trust.enhanced.priority.MEDIUM, condition = "lowHP" },
        },
    },
    
    [xi.job.WHM] = {
        role = xi.trust.enhanced.combatRole.HEALER,
        behavior = xi.trust.enhanced.behaviorType.DEFENSIVE,
        priorities = {
            { action = "cure", priority = xi.trust.enhanced.priority.CRITICAL, condition = "emergencyHP" },
            { action = "protect", priority = xi.trust.enhanced.priority.HIGH, condition = "needsBuff" },
            { action = "shell", priority = xi.trust.enhanced.priority.HIGH, condition = "needsBuff" },
            { action = "erase", priority = xi.trust.enhanced.priority.HIGH, condition = "hasDebuff" },
            { action = "regen", priority = xi.trust.enhanced.priority.MEDIUM, condition = "lowHP" },
            { action = "raise", priority = xi.trust.enhanced.priority.CRITICAL, condition = "deadAlly" },
        },
    },
    
    [xi.job.BLM] = {
        role = xi.trust.enhanced.combatRole.DAMAGE_DEALER,
        behavior = xi.trust.enhanced.behaviorType.AGGRESSIVE,
        priorities = {
            { action = "nuke", priority = xi.trust.enhanced.priority.HIGH, condition = "enemyWeakness" },
            { action = "sleep", priority = xi.trust.enhanced.priority.HIGH, condition = "multipleEnemies" },
            { action = "bind", priority = xi.trust.enhanced.priority.MEDIUM, condition = "enemyMoving" },
            { action = "manafont", priority = xi.trust.enhanced.priority.HIGH, condition = "lowMP" },
            { action = "elemental_seal", priority = xi.trust.enhanced.priority.MEDIUM, condition = "combat" },
        },
    },
    
    [xi.job.RDM] = {
        role = xi.trust.enhanced.combatRole.HYBRID,
        behavior = xi.trust.enhanced.behaviorType.SUPPORT,
        priorities = {
            { action = "refresh", priority = xi.trust.enhanced.priority.HIGH, condition = "lowMP" },
            { action = "haste", priority = xi.trust.enhanced.priority.HIGH, condition = "needsBuff" },
            { action = "cure", priority = xi.trust.enhanced.priority.MEDIUM, condition = "lowHP" },
            { action = "dispel", priority = xi.trust.enhanced.priority.MEDIUM, condition = "enemyBuffed" },
            { action = "convert", priority = xi.trust.enhanced.priority.HIGH, condition = "criticalMP" },
            { action = "chainspell", priority = xi.trust.enhanced.priority.MEDIUM, condition = "emergencyMagic" },
        },
    },
    
    [xi.job.THF] = {
        role = xi.trust.enhanced.combatRole.DAMAGE_DEALER,
        behavior = xi.trust.enhanced.behaviorType.SPECIALIST,
        priorities = {
            { action = "sneak_attack", priority = xi.trust.enhanced.priority.HIGH, condition = "behind" },
            { action = "trick_attack", priority = xi.trust.enhanced.priority.HIGH, condition = "coordinated" },
            { action = "steal", priority = xi.trust.enhanced.priority.LOW, condition = "hasStealable" },
            { action = "flee", priority = xi.trust.enhanced.priority.MEDIUM, condition = "needEscape" },
            { action = "hide", priority = xi.trust.enhanced.priority.HIGH, condition = "dangerousHP" },
        },
    },
    
    [xi.job.PLD] = {
        role = xi.trust.enhanced.combatRole.TANK,
        behavior = xi.trust.enhanced.behaviorType.DEFENSIVE,
        priorities = {
            { action = "provoke", priority = xi.trust.enhanced.priority.HIGH, condition = "lowEnmity" },
            { action = "cure", priority = xi.trust.enhanced.priority.HIGH, condition = "lowHP" },
            { action = "sentinel", priority = xi.trust.enhanced.priority.HIGH, condition = "highThreat" },
            { action = "cover", priority = xi.trust.enhanced.priority.HIGH, condition = "allyDanger" },
            { action = "holy_circle", priority = xi.trust.enhanced.priority.MEDIUM, condition = "undeadEnemy" },
            { action = "shield_bash", priority = xi.trust.enhanced.priority.MEDIUM, condition = "enemyCasting" },
        },
    },
    
    [xi.job.DRK] = {
        role = xi.trust.enhanced.combatRole.DAMAGE_DEALER,
        behavior = xi.trust.enhanced.behaviorType.AGGRESSIVE,
        priorities = {
            { action = "absorb", priority = xi.trust.enhanced.priority.HIGH, condition = "needStat" },
            { action = "drain", priority = xi.trust.enhanced.priority.MEDIUM, condition = "lowHP" },
            { action = "aspir", priority = xi.trust.enhanced.priority.MEDIUM, condition = "lowMP" },
            { action = "last_resort", priority = xi.trust.enhanced.priority.HIGH, condition = "criticalBattle" },
            { action = "weapon_bash", priority = xi.trust.enhanced.priority.MEDIUM, condition = "enemyCasting" },
            { action = "arcane_circle", priority = xi.trust.enhanced.priority.LOW, condition = "arcaneMagic" },
        },
    },
    
    [xi.job.BST] = {
        role = xi.trust.enhanced.combatRole.HYBRID,
        behavior = xi.trust.enhanced.behaviorType.SPECIALIST,
        priorities = {
            { action = "charm", priority = xi.trust.enhanced.priority.HIGH, condition = "noPet" },
            { action = "call_beast", priority = xi.trust.enhanced.priority.HIGH, condition = "noPet" },
            { action = "reward", priority = xi.trust.enhanced.priority.MEDIUM, condition = "petLowHP" },
            { action = "tame", priority = xi.trust.enhanced.priority.LOW, condition = "charmable" },
            { action = "familiar", priority = xi.trust.enhanced.priority.MEDIUM, condition = "combat" },
        },
    },
    
    [xi.job.BRD] = {
        role = xi.trust.enhanced.combatRole.SUPPORT,
        behavior = xi.trust.enhanced.behaviorType.SUPPORT,
        priorities = {
            { action = "song_buffs", priority = xi.trust.enhanced.priority.HIGH, condition = "noSongs" },
            { action = "soul_voice", priority = xi.trust.enhanced.priority.HIGH, condition = "criticalBattle" },
            { action = "song_debuffs", priority = xi.trust.enhanced.priority.MEDIUM, condition = "strongEnemy" },
            { action = "lullaby", priority = xi.trust.enhanced.priority.HIGH, condition = "multipleEnemies" },
            { action = "requiem", priority = xi.trust.enhanced.priority.MEDIUM, condition = "undeadEnemy" },
        },
    },
    
    [xi.job.RNG] = {
        role = xi.trust.enhanced.combatRole.DAMAGE_DEALER,
        behavior = xi.trust.enhanced.behaviorType.AGGRESSIVE,
        priorities = {
            { action = "ranged_attack", priority = xi.trust.enhanced.priority.HIGH, condition = "hasAmmo" },
            { action = "barrage", priority = xi.trust.enhanced.priority.HIGH, condition = "multipleShots" },
            { action = "shadowbind", priority = xi.trust.enhanced.priority.MEDIUM, condition = "enemyMoving" },
            { action = "sharpshot", priority = xi.trust.enhanced.priority.MEDIUM, condition = "combat" },
            { action = "eagle_eye_shot", priority = xi.trust.enhanced.priority.HIGH, condition = "highTP" },
        },
    },
    
    [xi.job.SAM] = {
        role = xi.trust.enhanced.combatRole.DAMAGE_DEALER,
        behavior = xi.trust.enhanced.behaviorType.SPECIALIST,
        priorities = {
            { action = "meditate", priority = xi.trust.enhanced.priority.HIGH, condition = "lowTP" },
            { action = "third_eye", priority = xi.trust.enhanced.priority.HIGH, condition = "anticipateAttack" },
            { action = "hasso", priority = xi.trust.enhanced.priority.HIGH, condition = "meleeStance" },
            { action = "seigan", priority = xi.trust.enhanced.priority.MEDIUM, condition = "counterStance" },
            { action = "sekkanoki", priority = xi.trust.enhanced.priority.HIGH, condition = "weaponskillChain" },
            { action = "meikyo_shisui", priority = xi.trust.enhanced.priority.HIGH, condition = "burstDamage" },
        },
    },
    
    [xi.job.NIN] = {
        role = xi.trust.enhanced.combatRole.DAMAGE_DEALER,
        behavior = xi.trust.enhanced.behaviorType.SPECIALIST,
        priorities = {
            { action = "utsusemi", priority = xi.trust.enhanced.priority.CRITICAL, condition = "noShadows" },
            { action = "ninjutsu", priority = xi.trust.enhanced.priority.HIGH, condition = "elementalNeed" },
            { action = "dual_wield", priority = xi.trust.enhanced.priority.HIGH, condition = "weaponskillReady" },
            { action = "mijin_gakure", priority = xi.trust.enhanced.priority.CRITICAL, condition = "desperateSituation" },
        },
    },
    
    [xi.job.DRG] = {
        role = xi.trust.enhanced.combatRole.DAMAGE_DEALER,
        behavior = xi.trust.enhanced.behaviorType.SPECIALIST,
        priorities = {
            { action = "call_wyvern", priority = xi.trust.enhanced.priority.CRITICAL, condition = "noWyvern" },
            { action = "jump", priority = xi.trust.enhanced.priority.HIGH, condition = "enemyAttacking" },
            { action = "high_jump", priority = xi.trust.enhanced.priority.HIGH, condition = "highThreat" },
            { action = "super_jump", priority = xi.trust.enhanced.priority.CRITICAL, condition = "desperateSituation" },
            { action = "ancient_circle", priority = xi.trust.enhanced.priority.MEDIUM, condition = "dragonEnemy" },
        },
    },
    
    [xi.job.SMN] = {
        role = xi.trust.enhanced.combatRole.HYBRID,
        behavior = xi.trust.enhanced.behaviorType.SPECIALIST,
        priorities = {
            { action = "summon_avatar", priority = xi.trust.enhanced.priority.CRITICAL, condition = "noAvatar" },
            { action = "blood_pact_ward", priority = xi.trust.enhanced.priority.HIGH, condition = "needBuff" },
            { action = "blood_pact_rage", priority = xi.trust.enhanced.priority.HIGH, condition = "combat" },
            { action = "astral_flow", priority = xi.trust.enhanced.priority.HIGH, condition = "criticalBattle" },
            { action = "elemental_siphon", priority = xi.trust.enhanced.priority.MEDIUM, condition = "lowMP" },
        },
    },
    
    [xi.job.BLU] = {
        role = xi.trust.enhanced.combatRole.HYBRID,
        behavior = xi.trust.enhanced.behaviorType.SPECIALIST,
        priorities = {
            { action = "blue_magic", priority = xi.trust.enhanced.priority.HIGH, condition = "situationalSpell" },
            { action = "azure_lore", priority = xi.trust.enhanced.priority.HIGH, condition = "criticalBattle" },
            { action = "chain_affinity", priority = xi.trust.enhanced.priority.MEDIUM, condition = "magicBurst" },
            { action = "burst_affinity", priority = xi.trust.enhanced.priority.MEDIUM, condition = "chainBurst" },
            { action = "efflux", priority = xi.trust.enhanced.priority.MEDIUM, condition = "blueChain" },
        },
    },
    
    [xi.job.COR] = {
        role = xi.trust.enhanced.combatRole.SUPPORT,
        behavior = xi.trust.enhanced.behaviorType.SUPPORT,
        priorities = {
            { action = "phantom_roll", priority = xi.trust.enhanced.priority.HIGH, condition = "needRoll" },
            { action = "double_up", priority = xi.trust.enhanced.priority.MEDIUM, condition = "goodRoll" },
            { action = "fold", priority = xi.trust.enhanced.priority.HIGH, condition = "badRoll" },
            { action = "quick_draw", priority = xi.trust.enhanced.priority.MEDIUM, condition = "elementalShot" },
            { action = "wild_card", priority = xi.trust.enhanced.priority.HIGH, condition = "resetAbilities" },
        },
    },
    
    [xi.job.PUP] = {
        role = xi.trust.enhanced.combatRole.HYBRID,
        behavior = xi.trust.enhanced.behaviorType.SPECIALIST,
        priorities = {
            { action = "activate", priority = xi.trust.enhanced.priority.CRITICAL, condition = "noPuppet" },
            { action = "repair", priority = xi.trust.enhanced.priority.HIGH, condition = "puppetDamaged" },
            { action = "maintenance", priority = xi.trust.enhanced.priority.MEDIUM, condition = "puppetNeeds" },
            { action = "tactical_switch", priority = xi.trust.enhanced.priority.MEDIUM, condition = "changeTactics" },
            { action = "overdrive", priority = xi.trust.enhanced.priority.HIGH, condition = "criticalBattle" },
        },
    },
    
    [xi.job.DNC] = {
        role = xi.trust.enhanced.combatRole.HYBRID,
        behavior = xi.trust.enhanced.behaviorType.SUPPORT,
        priorities = {
            { action = "steps", priority = xi.trust.enhanced.priority.HIGH, condition = "debuffEnemy" },
            { action = "flourishes", priority = xi.trust.enhanced.priority.MEDIUM, condition = "finishingMoves" },
            { action = "healing_waltz", priority = xi.trust.enhanced.priority.HIGH, condition = "statusAilment" },
            { action = "curing_waltz", priority = xi.trust.enhanced.priority.HIGH, condition = "lowHP" },
            { action = "saber_dance", priority = xi.trust.enhanced.priority.MEDIUM, condition = "meleeMode" },
        },
    },
    
    [xi.job.SCH] = {
        role = xi.trust.enhanced.combatRole.HYBRID,
        behavior = xi.trust.enhanced.behaviorType.SUPPORT,
        priorities = {
            { action = "stratagems", priority = xi.trust.enhanced.priority.HIGH, condition = "enhanceMagic" },
            { action = "weather_spells", priority = xi.trust.enhanced.priority.MEDIUM, condition = "elementalAdvantage" },
            { action = "grimoire_swap", priority = xi.trust.enhanced.priority.HIGH, condition = "changeFocus" },
            { action = "tabula_rasa", priority = xi.trust.enhanced.priority.HIGH, condition = "criticalBattle" },
            { action = "celerity", priority = xi.trust.enhanced.priority.MEDIUM, condition = "fastCasting" },
        },
    },
    
    [xi.job.GEO] = {
        role = xi.trust.enhanced.combatRole.SUPPORT,
        behavior = xi.trust.enhanced.behaviorType.SUPPORT,
        priorities = {
            { action = "geomancy", priority = xi.trust.enhanced.priority.HIGH, condition = "areaEffect" },
            { action = "indicolure", priority = xi.trust.enhanced.priority.HIGH, condition = "partyBuff" },
            { action = "life_cycle", priority = xi.trust.enhanced.priority.MEDIUM, condition = "luopanDanger" },
            { action = "full_circle", priority = xi.trust.enhanced.priority.HIGH, condition = "resetLuopan" },
            { action = "blaze_of_glory", priority = xi.trust.enhanced.priority.HIGH, condition = "criticalBattle" },
        },
    },
    
    [xi.job.RUN] = {
        role = xi.trust.enhanced.combatRole.TANK,
        behavior = xi.trust.enhanced.behaviorType.DEFENSIVE,
        priorities = {
            { action = "runes", priority = xi.trust.enhanced.priority.HIGH, condition = "elementalDefense" },
            { action = "ward_spells", priority = xi.trust.enhanced.priority.HIGH, condition = "protectiveBuffs" },
            { action = "elemental_sforzo", priority = xi.trust.enhanced.priority.HIGH, condition = "singleHit" },
            { action = "one_for_all", priority = xi.trust.enhanced.priority.HIGH, condition = "partyDanger" },
            { action = "embolden", priority = xi.trust.enhanced.priority.MEDIUM, condition = "enhanceRunes" },
        },
    },
}

-- Enhanced trust spawning with AI configuration
xi.trust.enhanced.spawn = function(caster, spell, aiConfig)
    local trust = xi.trust.spawn(caster, spell)
    
    if not trust then
        return nil
    end
    
    -- Apply enhanced AI configuration
    xi.trust.enhanced.configureTrustAI(trust, aiConfig)
    
    return trust
end

-- Configure trust AI based on job and preferences
xi.trust.enhanced.configureTrustAI = function(trust, customConfig)
    if not trust or not trust:isTrust() then
        return false
    end
    
    local job = trust:getMainJob()
    local subjob = trust:getSubJob()
    local jobBehavior = xi.trust.enhanced.jobBehaviors[job] or xi.trust.enhanced.jobBehaviors[xi.job.WAR]
    local config = customConfig or xi.trust.enhanced.aiConfig
    
    -- Set movement type based on role
    local movementType = xi.trust.movementType.MELEE
    if jobBehavior.role == xi.trust.enhanced.combatRole.HEALER then
        movementType = xi.trust.movementType.LONG_RANGE
    elseif jobBehavior.role == xi.trust.enhanced.combatRole.DAMAGE_DEALER then
        if job == xi.job.BLM or job == xi.job.RDM or job == xi.job.SCH then
            movementType = xi.trust.movementType.MID_RANGE
        elseif job == xi.job.RNG or job == xi.job.COR then
            movementType = xi.trust.movementType.LONG_RANGE
        end
    elseif jobBehavior.role == xi.trust.enhanced.combatRole.SUPPORT then
        if job == xi.job.BRD or job == xi.job.GEO then
            movementType = xi.trust.movementType.MID_RANGE
        end
    end
    
    trust:setMobMod(xi.mobMod.TRUST_DISTANCE, movementType)
    
    -- Add enhanced AI gambits based on job
    xi.trust.enhanced.addJobSpecificGambits(trust, job, jobBehavior)
    
    -- Add subjob gambits if subjob exists and config allows
    if subjob and subjob > 0 and config.subjob.useSubjobAbilities then
        xi.trust.enhanced.addSubjobGambits(trust, job, subjob, config.subjob)
    end
    
    -- Add general AI improvements
    xi.trust.enhanced.addGeneralAIGambits(trust, config)
    
    -- Set trust to use enhanced AI
    trust:setLocalVar("enhancedAI", 1)
    trust:setLocalVar("mainJob", job)
    trust:setLocalVar("subJob", subjob or 0)
    trust:setLocalVar("aiConfig", utils.serialize(config))
    
    return true
end

-- Add job-specific AI gambits
xi.trust.enhanced.addJobSpecificGambits = function(trust, job, behavior)
    -- Clear existing gambits to replace with enhanced ones
    trust:clearGambits()
    
    if job == xi.job.WAR then
        -- Warrior tank behavior
        trust:addGambit(ai.t.MASTER, { ai.c.HPP_LT, 50 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.CURE })
        trust:addGambit(ai.t.SELF, { ai.c.NOT_HAS_TOP_ENMITY, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.PROVOKE })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        trust:addGambit(ai.t.SELF, { ai.c.NOT_STATUS, xi.effect.BERSERK }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.BERSERK })
        trust:addGambit(ai.t.SELF, { ai.c.HPP_LT, 30 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.DEFENDER })
        
    elseif job == xi.job.MNK then
        -- Monk damage dealer behavior
        trust:addGambit(ai.t.SELF, { ai.c.NOT_STATUS, xi.effect.BOOST }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.BOOST })
        trust:addGambit(ai.t.SELF, { ai.c.NOT_STATUS, xi.effect.FOCUS }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.FOCUS })
        trust:addGambit(ai.t.SELF, { ai.c.HPP_LT, 50 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.CHAKRA })
        trust:addGambit(ai.t.SELF, { ai.c.HPP_LT, 25 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.DODGE })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.WHM then
        -- White Mage healer behavior
        trust:addGambit(ai.t.PARTY, { ai.c.HPP_LT, 25 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.CURE })
        trust:addGambit(ai.t.MASTER, { ai.c.HPP_LT, 75 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.CURE })
        trust:addGambit(ai.t.PARTY, { ai.c.STATUS_FLAG, xi.effectFlag.ERASABLE }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.ERASE })
        trust:addGambit(ai.t.PARTY, { ai.c.NOT_STATUS, xi.effect.PROTECT }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.PROTECT })
        trust:addGambit(ai.t.PARTY, { ai.c.NOT_STATUS, xi.effect.SHELL }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.SHELL })
        trust:addGambit(ai.t.PARTY, { ai.c.NOT_STATUS, xi.effect.REGEN }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.REGEN })
        
    elseif job == xi.job.BLM then
        -- Black Mage damage dealer behavior
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.MA, ai.s.MB_ELEMENT, xi.magic.spellFamily.ANCIENT_MAGIC })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.MA, ai.s.BEST_AGAINST_TARGET, xi.magic.spellFamily.ELEMENTAL_MAGIC })
        trust:addGambit(ai.t.TARGET, { ai.c.CASTING_MA, 0 }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.STUN })
        trust:addGambit(ai.t.SELF, { ai.c.MPP_LT, 25 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.MANAFONT })
        
    elseif job == xi.job.RDM then
        -- Red Mage hybrid behavior
        trust:addGambit(ai.t.MASTER, { ai.c.NOT_STATUS, xi.effect.HASTE }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.HASTE })
        trust:addGambit(ai.t.MASTER, { ai.c.NOT_STATUS, xi.effect.REFRESH }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.REFRESH })
        trust:addGambit(ai.t.MASTER, { ai.c.HPP_LT, 50 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.CURE })
        trust:addGambit(ai.t.TARGET, { ai.c.STATUS_FLAG, xi.effectFlag.DISPELABLE }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.DISPEL })
        trust:addGambit(ai.t.SELF, { ai.c.MPP_LT, 10 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.CONVERT })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.MA, ai.s.BEST_AGAINST_TARGET, xi.magic.spellFamily.ELEMENTAL_MAGIC })
        
    elseif job == xi.job.THF then
        -- Thief damage dealer behavior
        trust:addGambit(ai.t.TARGET, { ai.c.BEHIND, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.SNEAK_ATTACK })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.TRICK_ATTACK })
        trust:addGambit(ai.t.SELF, { ai.c.HPP_LT, 15 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.HIDE })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.PLD then
        -- Paladin tank behavior
        trust:addGambit(ai.t.SELF, { ai.c.NOT_HAS_TOP_ENMITY, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.PROVOKE })
        trust:addGambit(ai.t.SELF, { ai.c.HPP_LT, 50 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.CURE })
        trust:addGambit(ai.t.SELF, { ai.c.HPP_LT, 25 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.SENTINEL })
        trust:addGambit(ai.t.PARTY, { ai.c.HPP_LT, 20 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.COVER })
        trust:addGambit(ai.t.TARGET, { ai.c.CASTING_MA, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.SHIELD_BASH })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.DRK then
        -- Dark Knight damage dealer behavior
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.ABSORB })
        trust:addGambit(ai.t.TARGET, { ai.c.HPP_GT, 50 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.DRAIN })
        trust:addGambit(ai.t.TARGET, { ai.c.MPP_GT, 50 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.ASPIR })
        trust:addGambit(ai.t.SELF, { ai.c.HPP_LT, 30 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.LAST_RESORT })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.BST then
        -- Beastmaster hybrid behavior
        trust:addGambit(ai.t.SELF, { ai.c.NOT_HAS_PET, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.CALL_BEAST })
        trust:addGambit(ai.t.PET, { ai.c.HPP_LT, 50 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.REWARD })
        trust:addGambit(ai.t.SELF, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.FAMILIAR })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.BRD then
        -- Bard support behavior
        trust:addGambit(ai.t.PARTY, { ai.c.NOT_STATUS, xi.effect.MINUET }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.MINUET })
        trust:addGambit(ai.t.PARTY, { ai.c.NOT_STATUS, xi.effect.MARCH }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.MARCH })
        trust:addGambit(ai.t.TARGET, { ai.c.MULTIPLE, 3 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.LULLABY })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.REQUIEM })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.RNG then
        -- Ranger damage dealer behavior
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.RA, ai.s.HIGHEST, 0 })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.BARRAGE })
        trust:addGambit(ai.t.TARGET, { ai.c.MOVING, 0 }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.SHADOWBIND })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.SAM then
        -- Samurai damage dealer behavior
        trust:addGambit(ai.t.SELF, { ai.c.NOT_STATUS, xi.effect.HASSO }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.HASSO })
        trust:addGambit(ai.t.SELF, { ai.c.TP_LT, 500 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.MEDITATE })
        trust:addGambit(ai.t.SELF, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.THIRD_EYE })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.NIN then
        -- Ninja damage dealer behavior
        trust:addGambit(ai.t.SELF, { ai.c.NOT_STATUS, xi.effect.COPY_IMAGE }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.UTSUSEMI })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.MA, ai.s.BEST_AGAINST_TARGET, xi.magic.spellFamily.NINJUTSU })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.DRG then
        -- Dragoon damage dealer behavior
        trust:addGambit(ai.t.SELF, { ai.c.NOT_HAS_PET, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.CALL_WYVERN })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.JUMP })
        trust:addGambit(ai.t.TARGET, { ai.c.HAS_TOP_ENMITY, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.HIGH_JUMP })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.SMN then
        -- Summoner hybrid behavior
        trust:addGambit(ai.t.SELF, { ai.c.NOT_HAS_PET, 0 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.AVATAR })
        trust:addGambit(ai.t.PET, { ai.c.ALWAYS, 0 }, { ai.r.PET, ai.s.HIGHEST, xi.magic.spellFamily.BLOOD_PACT_WARD })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.PET, ai.s.HIGHEST, xi.magic.spellFamily.BLOOD_PACT_RAGE })
        trust:addGambit(ai.t.SELF, { ai.c.MPP_LT, 25 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.ELEMENTAL_SIPHON })
        
    elseif job == xi.job.BLU then
        -- Blue Mage hybrid behavior
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.BLUE_MAGIC })
        trust:addGambit(ai.t.SELF, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.CHAIN_AFFINITY })
        trust:addGambit(ai.t.SELF, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.BURST_AFFINITY })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.COR then
        -- Corsair support behavior
        trust:addGambit(ai.t.PARTY, { ai.c.NOT_STATUS, xi.effect.FIGHTERS_ROLL }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.FIGHTERS_ROLL })
        trust:addGambit(ai.t.PARTY, { ai.c.NOT_STATUS, xi.effect.CHAOS_ROLL }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.CHAOS_ROLL })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.RA, ai.s.HIGHEST, 0 })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.HIGHEST, xi.ja.QUICK_DRAW })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.PUP then
        -- Puppetmaster hybrid behavior
        trust:addGambit(ai.t.SELF, { ai.c.NOT_HAS_PET, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.ACTIVATE })
        trust:addGambit(ai.t.PET, { ai.c.HPP_LT, 50 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.REPAIR })
        trust:addGambit(ai.t.SELF, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.MAINTENANCE })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.DNC then
        -- Dancer hybrid behavior
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.HIGHEST, xi.ja.STEPS })
        trust:addGambit(ai.t.PARTY, { ai.c.HPP_LT, 50 }, { ai.r.JA, ai.s.HIGHEST, xi.ja.CURING_WALTZ })
        trust:addGambit(ai.t.PARTY, { ai.c.STATUS_FLAG, xi.effectFlag.WALTZABLE }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.HEALING_WALTZ })
        trust:addGambit(ai.t.SELF, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.SABER_DANCE })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.SCH then
        -- Scholar hybrid behavior
        trust:addGambit(ai.t.SELF, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.HIGHEST, xi.ja.STRATAGEMS })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.MA, ai.s.BEST_AGAINST_TARGET, xi.magic.spellFamily.ELEMENTAL_MAGIC })
        trust:addGambit(ai.t.PARTY, { ai.c.HPP_LT, 50 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.CURE })
        trust:addGambit(ai.t.SELF, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.CELERITY })
        
    elseif job == xi.job.GEO then
        -- Geomancer support behavior
        trust:addGambit(ai.t.PARTY, { ai.c.NOT_STATUS, xi.effect.GEO_ACCURACY_BOOST }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.GEOMANCY })
        trust:addGambit(ai.t.PARTY, { ai.c.NOT_STATUS, xi.effect.INDI_ACCURACY }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.INDICOLURE })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.MA, ai.s.BEST_AGAINST_TARGET, xi.magic.spellFamily.ELEMENTAL_MAGIC })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
        
    elseif job == xi.job.RUN then
        -- Rune Fencer tank behavior
        trust:addGambit(ai.t.SELF, { ai.c.NOT_HAS_TOP_ENMITY, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.PROVOKE })
        trust:addGambit(ai.t.SELF, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.HIGHEST, xi.ja.RUNES })
        trust:addGambit(ai.t.SELF, { ai.c.ALWAYS, 0 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.WARD })
        trust:addGambit(ai.t.SELF, { ai.c.HPP_LT, 25 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.ELEMENTAL_SFORZO })
        trust:addGambit(ai.t.SELF, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
    end
    
    -- Add weapon skill usage for all jobs if not already added
    trust:addGambit(ai.t.TARGET, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
end

-- Add subjob-specific AI gambits
xi.trust.enhanced.addSubjobGambits = function(trust, mainJob, subJob, subjobConfig)
    if not subjobConfig.useSubjobAbilities then
        return
    end
    
    local subjobBehavior = xi.trust.enhanced.subjobBehaviors[mainJob] and xi.trust.enhanced.subjobBehaviors[mainJob][subJob]
    if not subjobBehavior then
        return
    end
    
    -- Add subjob abilities based on priority and conditions
    local priority = subjobBehavior.priority * subjobConfig.subjobPriority
    
    for _, ability in ipairs(subjobBehavior.abilities) do
        if ability == "utsusemi" then
            trust:addGambit(ai.t.SELF, { ai.c.NOT_STATUS, xi.effect.COPY_IMAGE }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.UTSUSEMI })
        elseif ability == "cure" then
            trust:addGambit(ai.t.SELF, { ai.c.HPP_LT, 40 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.CURE })
        elseif ability == "refresh" then
            trust:addGambit(ai.t.SELF, { ai.c.MPP_LT, 50 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.REFRESH })
        elseif ability == "berserk" then
            trust:addGambit(ai.t.SELF, { ai.c.NOT_STATUS, xi.effect.BERSERK }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.BERSERK })
        elseif ability == "provoke" then
            trust:addGambit(ai.t.SELF, { ai.c.NOT_HAS_TOP_ENMITY, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.PROVOKE })
        elseif ability == "sneak_attack" then
            trust:addGambit(ai.t.TARGET, { ai.c.BEHIND, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.SNEAK_ATTACK })
        elseif ability == "trick_attack" then
            trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.TRICK_ATTACK })
        elseif ability == "meditate" then
            trust:addGambit(ai.t.SELF, { ai.c.TP_LT, 800 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.MEDITATE })
        elseif ability == "third_eye" then
            trust:addGambit(ai.t.SELF, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.THIRD_EYE })
        elseif ability == "convert" then
            trust:addGambit(ai.t.SELF, { ai.c.MPP_LT, 15 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.CONVERT })
        elseif ability == "manafont" then
            trust:addGambit(ai.t.SELF, { ai.c.MPP_LT, 20 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.MANAFONT })
        elseif ability == "dispel" then
            trust:addGambit(ai.t.TARGET, { ai.c.STATUS_FLAG, xi.effectFlag.DISPELABLE }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.DISPEL })
        elseif ability == "protect" then
            trust:addGambit(ai.t.PARTY, { ai.c.NOT_STATUS, xi.effect.PROTECT }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.PROTECT })
        elseif ability == "shell" then
            trust:addGambit(ai.t.PARTY, { ai.c.NOT_STATUS, xi.effect.SHELL }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.SHELL })
        elseif ability == "poisona" then
            trust:addGambit(ai.t.PARTY, { ai.c.STATUS, xi.effect.POISON }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.POISONA })
        elseif ability == "shadowbind" then
            trust:addGambit(ai.t.TARGET, { ai.c.MOVING, 0 }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.SHADOWBIND })
        elseif ability == "eagle_eye_shot" then
            trust:addGambit(ai.t.TARGET, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.SPECIFIC, xi.ws.EAGLE_EYE_SHOT })
        end
    end
end

-- Add general AI improvements for all trusts
xi.trust.enhanced.addGeneralAIGambits = function(trust, config)
    -- Emergency self-preservation
    trust:addGambit(ai.t.SELF, { ai.c.HPP_LT, 25 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.CURE })
    
    -- Status effect management
    if config.combat.statusEffectCleansing then
        trust:addGambit(ai.t.SELF, { ai.c.STATUS_FLAG, xi.effectFlag.ERASABLE }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.ERASE })
    end
    
    -- Spell interruption
    if config.combat.spellInterruption then
        trust:addGambit(ai.t.TARGET, { ai.c.CASTING_MA, 0 }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.STUN })
    end
end

-- Enhanced trust message system
xi.trust.enhanced.message = function(trust, messageType, extraData)
    -- Call original message system
    xi.trust.message(trust, messageType)
    
    -- Add enhanced messaging for specific situations
    if messageType == xi.trust.messageOffset.SPAWN then
        local master = trust:getMaster()
        if master then
            -- Announce trust capabilities
            local job = trust:getMainJob()
            local subjob = trust:getSubJob()
            local behavior = xi.trust.enhanced.jobBehaviors[job]
            if behavior then
                local roleText = ""
                if behavior.role == xi.trust.enhanced.combatRole.TANK then
                    roleText = "Ready to protect the party!"
                elseif behavior.role == xi.trust.enhanced.combatRole.HEALER then
                    roleText = "Ready to provide healing support!"
                elseif behavior.role == xi.trust.enhanced.combatRole.DAMAGE_DEALER then
                    roleText = "Ready to deal damage!"
                elseif behavior.role == xi.trust.enhanced.combatRole.SUPPORT then
                    roleText = "Ready to provide magical support!"
                elseif behavior.role == xi.trust.enhanced.combatRole.HYBRID then
                    roleText = "Ready to provide versatile support!"
                end
                
                -- Add subjob information if present
                if subjob and subjob > 0 then
                    local jobNames = {
                        [xi.job.WAR] = "Warrior", [xi.job.MNK] = "Monk", [xi.job.WHM] = "White Mage",
                        [xi.job.BLM] = "Black Mage", [xi.job.RDM] = "Red Mage", [xi.job.THF] = "Thief",
                        [xi.job.PLD] = "Paladin", [xi.job.DRK] = "Dark Knight", [xi.job.BST] = "Beastmaster",
                        [xi.job.BRD] = "Bard", [xi.job.RNG] = "Ranger", [xi.job.SAM] = "Samurai",
                        [xi.job.NIN] = "Ninja", [xi.job.DRG] = "Dragoon", [xi.job.SMN] = "Summoner",
                        [xi.job.BLU] = "Blue Mage", [xi.job.COR] = "Corsair", [xi.job.PUP] = "Puppetmaster",
                        [xi.job.DNC] = "Dancer", [xi.job.SCH] = "Scholar", [xi.job.GEO] = "Geomancer",
                        [xi.job.RUN] = "Rune Fencer"
                    }
                    local mainJobName = jobNames[job] or "Unknown"
                    local subJobName = jobNames[subjob] or "Unknown"
                    roleText = roleText .. " (" .. mainJobName .. "/" .. subJobName .. ")"
                end
                
                if roleText ~= "" then
                    trust:messageText(trust, roleText, false)
                end
            end
        end
    end
end

-- Enhanced subjob decision making system
xi.trust.enhanced.evaluateSubjobPriority = function(trust, situation)
    local mainJob = trust:getMainJob()
    local subJob = trust:getSubJob()
    
    if not subJob or subJob <= 0 then
        return 0 -- No subjob
    end
    
    local subjobBehavior = xi.trust.enhanced.subjobBehaviors[mainJob] and xi.trust.enhanced.subjobBehaviors[mainJob][subJob]
    if not subjobBehavior then
        return 0 -- No defined behavior for this combo
    end
    
    -- Evaluate current situation against subjob conditions
    local priorityModifier = 1.0
    local master = trust:getMaster()
    
    for _, condition in ipairs(subjobBehavior.conditions) do
        if condition == "lowHP" and trust:getHPP() < 30 then
            priorityModifier = priorityModifier + 0.3
        elseif condition == "lowMP" and trust:getMPP() < 25 then
            priorityModifier = priorityModifier + 0.4
        elseif condition == "noShadows" and not trust:hasStatusEffect(xi.effect.COPY_IMAGE) then
            priorityModifier = priorityModifier + 0.5
        elseif condition == "combat" and trust:isEngaged() then
            priorityModifier = priorityModifier + 0.2
        elseif condition == "emergencyHP" and (master and master:getHPP() < 20) then
            priorityModifier = priorityModifier + 0.6
        elseif condition == "noHealer" then
            -- Check if party has a dedicated healer
            local hasHealer = false
            local party = master and master:getPartyWithTrusts() or {}
            for _, member in pairs(party) do
                if member:getObjType() == xi.objType.TRUST then
                    local memberJob = member:getMainJob()
                    if memberJob == xi.job.WHM or memberJob == xi.job.RDM then
                        hasHealer = true
                        break
                    end
                end
            end
            if not hasHealer then
                priorityModifier = priorityModifier + 0.7
            end
        elseif condition == "beingTargeted" and trust:hasEnmity() then
            priorityModifier = priorityModifier + 0.4
        elseif condition == "criticalBattle" then
            -- Determine if this is a critical battle situation
            local target = trust:getTarget()
            if target and target:getHPP() > 80 and trust:getHPP() < 50 then
                priorityModifier = priorityModifier + 0.5
            end
        end
    end
    
    return subjobBehavior.priority * priorityModifier
end

-- Enhanced subjob ability selection
xi.trust.enhanced.selectSubjobAbility = function(trust)
    local mainJob = trust:getMainJob()
    local subJob = trust:getSubJob()
    
    if not subJob or subJob <= 0 then
        return nil
    end
    
    local subjobBehavior = xi.trust.enhanced.subjobBehaviors[mainJob] and xi.trust.enhanced.subjobBehaviors[mainJob][subJob]
    if not subjobBehavior then
        return nil
    end
    
    -- Evaluate each ability based on current situation
    local currentSituation = xi.trust.enhanced.analyzeSituation(trust)
    local bestAbility = nil
    local highestPriority = 0
    
    for _, ability in ipairs(subjobBehavior.abilities) do
        local abilityPriority = xi.trust.enhanced.evaluateAbilityPriority(trust, ability, currentSituation)
        if abilityPriority > highestPriority then
            highestPriority = abilityPriority
            bestAbility = ability
        end
    end
    
    return bestAbility
end

-- Analyze current battle situation
xi.trust.enhanced.analyzeSituation = function(trust)
    local situation = {
        inCombat = trust:isEngaged(),
        hpPercent = trust:getHPP(),
        mpPercent = trust:getMPP(),
        hasEnmity = trust:hasEnmity(),
        targetPresent = trust:getTarget() ~= nil,
        partySize = 1,
        multipleEnemies = false,
        emergencyHealing = false,
    }
    
    local master = trust:getMaster()
    if master then
        local party = master:getPartyWithTrusts()
        situation.partySize = #party
        situation.emergencyHealing = master:getHPP() < 25
        
        -- Check for multiple enemies
        local target = trust:getTarget()
        if target then
            local nearbyEnemies = target:getEntitiesNear(10)
            local enemyCount = 0
            for _, entity in ipairs(nearbyEnemies) do
                if entity:isAlive() and entity:isEnemy(trust) then
                    enemyCount = enemyCount + 1
                end
            end
            situation.multipleEnemies = enemyCount > 1
        end
    end
    
    return situation
end

-- Evaluate priority of specific abilities based on situation
xi.trust.enhanced.evaluateAbilityPriority = function(trust, ability, situation)
    local basePriority = 5 -- Default priority
    
    if ability == "utsusemi" then
        if not trust:hasStatusEffect(xi.effect.COPY_IMAGE) and situation.inCombat then
            basePriority = 9
        else
            basePriority = 0 -- Don't use if already have shadows
        end
    elseif ability == "cure" then
        if situation.hpPercent < 30 then
            basePriority = 10
        elseif situation.hpPercent < 60 then
            basePriority = 7
        elseif situation.emergencyHealing then
            basePriority = 8
        else
            basePriority = 2
        end
    elseif ability == "refresh" then
        if situation.mpPercent < 20 then
            basePriority = 8
        elseif situation.mpPercent < 50 then
            basePriority = 5
        else
            basePriority = 1
        end
    elseif ability == "berserk" then
        if situation.inCombat and not trust:hasStatusEffect(xi.effect.BERSERK) then
            basePriority = 6
        else
            basePriority = 0
        end
    elseif ability == "sneak_attack" or ability == "trick_attack" then
        if situation.inCombat and trust:getTP() >= 1000 then
            basePriority = 7
        else
            basePriority = 2
        end
    elseif ability == "meditate" then
        if trust:getTP() < 500 then
            basePriority = 6
        else
            basePriority = 1
        end
    elseif ability == "convert" then
        if situation.mpPercent < 10 then
            basePriority = 9
        else
            basePriority = 0
        end
    end
    
    return basePriority
end

-- Enhanced trust coordination system
xi.trust.enhanced.coordinateParty = function(trust)
    local master = trust:getMaster()
    if not master then
        return
    end
    
    local zone = master:getZone()
    if not zone then
        return
    end
    
    -- Get all trusts belonging to this master
    local trusts = {}
    local entities = zone:getEntitiesByType(xi.objType.TRUST)
    for _, entity in ipairs(entities) do
        if entity:getMaster() and entity:getMaster():getID() == master:getID() then
            table.insert(trusts, entity)
        end
    end
    
    -- Coordinate trust actions
    xi.trust.enhanced.coordinateCombatActions(trusts, master)
    xi.trust.enhanced.coordinateBuffing(trusts, master)
    xi.trust.enhanced.coordinateFormation(trusts, master)
end

-- Coordinate combat actions between trusts
xi.trust.enhanced.coordinateCombatActions = function(trusts, master)
    local target = master:getTarget()
    if not target or not target:isAlive() then
        return
    end
    
    -- Coordinate weapon skills for skillchains
    local readyForWS = {}
    for _, trust in ipairs(trusts) do
        if trust:getTP() >= 1000 and trust:getTarget() and trust:getTarget():getID() == target:getID() then
            table.insert(readyForWS, trust)
        end
    end
    
    -- If multiple trusts are ready, coordinate skillchain
    if #readyForWS >= 2 then
        -- Implement basic skillchain coordination
        -- First trust uses opening WS, second trust follows up
        for i, trust in ipairs(readyForWS) do
            if i == 1 then
                trust:setLocalVar("useWS", 1)
            elseif i == 2 then
                trust:setLocalVar("followupWS", 10) -- Wait 1 second for skillchain window
            end
        end
    end
end

-- Coordinate buffing to avoid overlaps
xi.trust.enhanced.coordinateBuffing = function(trusts, master)
    local partyMembers = { master }
    for _, trust in ipairs(trusts) do
        table.insert(partyMembers, trust)
    end
    
    -- Track who needs what buffs
    local buffNeeds = {}
    for _, member in ipairs(partyMembers) do
        buffNeeds[member:getID()] = {
            needsHaste = not member:hasStatusEffect(xi.effect.HASTE),
            needsRefresh = not member:hasStatusEffect(xi.effect.REFRESH) and member:getMP() < member:getMaxMP() * 0.8,
            needsProtect = not member:hasStatusEffect(xi.effect.PROTECT),
            needsShell = not member:hasStatusEffect(xi.effect.SHELL),
        }
    end
    
    -- Assign buffing responsibilities to avoid conflicts
    local buffAssignments = {}
    for _, trust in ipairs(trusts) do
        local job = trust:getMainJob()
        if job == xi.job.RDM or job == xi.job.WHM then
            buffAssignments[trust:getID()] = buffNeeds
        end
    end
    
    -- Set local variables for buff targeting
    for trustId, assignments in pairs(buffAssignments) do
        for _, trust in ipairs(trusts) do
            if trust:getID() == trustId then
                trust:setLocalVar("buffAssignments", utils.serialize(assignments))
                break
            end
        end
    end
end

-- Coordinate party formation and positioning
xi.trust.enhanced.coordinateFormation = function(trusts, master)
    local masterPos = master:getPos()
    local target = master:getTarget()
    
    if not target then
        return
    end
    
    local targetPos = target:getPos()
    
    -- Calculate formation positions based on roles
    for i, trust in ipairs(trusts) do
        local job = trust:getMainJob()
        local behavior = xi.trust.enhanced.jobBehaviors[job]
        
        if behavior then
            local formationOffset = { x = 0, z = 0 }
            
            if behavior.role == xi.trust.enhanced.combatRole.TANK then
                -- Tanks should be between target and party
                formationOffset.x = (targetPos.x - masterPos.x) * 0.3
                formationOffset.z = (targetPos.z - masterPos.z) * 0.3
                
            elseif behavior.role == xi.trust.enhanced.combatRole.HEALER then
                -- Healers should stay back
                formationOffset.x = (masterPos.x - targetPos.x) * 0.2
                formationOffset.z = (masterPos.z - targetPos.z) * 0.2
                
            elseif behavior.role == xi.trust.enhanced.combatRole.DAMAGE_DEALER then
                -- Melee DDs flank, ranged DDs stay back
                if job == xi.job.BLM or job == xi.job.RDM then
                    formationOffset.x = (masterPos.x - targetPos.x) * 0.1
                    formationOffset.z = (masterPos.z - targetPos.z) * 0.1
                else
                    -- Flank position
                    formationOffset.x = math.sin(i * math.pi / 3) * 2
                    formationOffset.z = math.cos(i * math.pi / 3) * 2
                end
            end
            
            -- Set formation position
            trust:setLocalVar("formationX", masterPos.x + formationOffset.x)
            trust:setLocalVar("formationZ", masterPos.z + formationOffset.z)
        end
    end
end

-- Trust AI update function (called periodically)
xi.trust.enhanced.updateAI = function(trust)
    if not trust or not trust:isTrust() or trust:getLocalVar("enhancedAI") ~= 1 then
        return
    end
    
    -- Coordinate with party
    xi.trust.enhanced.coordinateParty(trust)
    
    -- Handle weapon skill coordination
    if trust:getLocalVar("useWS") == 1 then
        trust:useMobAbility(trust:getLocalVar("preferredWS") or 0)
        trust:setLocalVar("useWS", 0)
    end
    
    if trust:getLocalVar("followupWS") > 0 then
        local countdown = trust:getLocalVar("followupWS") - 1
        trust:setLocalVar("followupWS", countdown)
        if countdown == 0 then
            trust:useMobAbility(trust:getLocalVar("preferredWS") or 0)
        end
    end
    
    -- Enhanced subjob decision making
    local subjobPriority = xi.trust.enhanced.evaluateSubjobPriority(trust, "current")
    trust:setLocalVar("subjobPriority", subjobPriority)
    
    -- Intelligent ability selection based on situation
    local situation = xi.trust.enhanced.analyzeSituation(trust)
    if situation.inCombat then
        local selectedAbility = xi.trust.enhanced.selectSubjobAbility(trust)
        if selectedAbility then
            trust:setLocalVar("selectedSubjobAbility", selectedAbility)
        end
    end
    
    -- Dynamic role adaptation based on party composition
    xi.trust.enhanced.adaptRole(trust)
    
    -- Validate AI performance
    xi.content.validation.validateTrustAI(trust)
end

-- Dynamic role adaptation based on party composition
xi.trust.enhanced.adaptRole = function(trust)
    local master = trust:getMaster()
    if not master then
        return
    end
    
    local party = master:getPartyWithTrusts()
    local roles = {
        tanks = 0,
        healers = 0,
        damage = 0,
        support = 0
    }
    
    -- Count existing roles in party
    for _, member in pairs(party) do
        if member:getObjType() == xi.objType.TRUST then
            local job = member:getMainJob()
            local behavior = xi.trust.enhanced.jobBehaviors[job]
            if behavior then
                if behavior.role == xi.trust.enhanced.combatRole.TANK then
                    roles.tanks = roles.tanks + 1
                elseif behavior.role == xi.trust.enhanced.combatRole.HEALER then
                    roles.healers = roles.healers + 1
                elseif behavior.role == xi.trust.enhanced.combatRole.DAMAGE_DEALER then
                    roles.damage = roles.damage + 1
                elseif behavior.role == xi.trust.enhanced.combatRole.SUPPORT then
                    roles.support = roles.support + 1
                end
            end
        end
    end
    
    -- Adapt behavior based on party needs
    local currentJob = trust:getMainJob()
    local currentBehavior = xi.trust.enhanced.jobBehaviors[currentJob]
    
    if currentBehavior then
        -- If we're a hybrid job, adapt based on party composition
        if currentBehavior.role == xi.trust.enhanced.combatRole.HYBRID then
            if roles.healers == 0 and (currentJob == xi.job.RDM or currentJob == xi.job.SCH or currentJob == xi.job.BLU) then
                -- Become more healer-focused
                trust:setLocalVar("adaptedRole", xi.trust.enhanced.combatRole.HEALER)
            elseif roles.tanks == 0 and currentJob == xi.job.RUN then
                -- Become more tank-focused
                trust:setLocalVar("adaptedRole", xi.trust.enhanced.combatRole.TANK)
            elseif roles.damage < 2 then
                -- Become more damage-focused
                trust:setLocalVar("adaptedRole", xi.trust.enhanced.combatRole.DAMAGE_DEALER)
            else
                -- Default to support
                trust:setLocalVar("adaptedRole", xi.trust.enhanced.combatRole.SUPPORT)
            end
        end
    end
end

-- Enhanced party coordination for larger variety of jobs
xi.trust.enhanced.coordinateAdvancedParty = function(trust)
    local master = trust:getMaster()
    if not master then
        return
    end
    
    local zone = master:getZone()
    if not zone then
        return
    end
    
    -- Get all trusts belonging to this master
    local trusts = {}
    local entities = zone:getEntitiesByType(xi.objType.TRUST)
    for _, entity in ipairs(entities) do
        if entity:getMaster() and entity:getMaster():getID() == master:getID() then
            table.insert(trusts, entity)
        end
    end
    
    -- Enhanced coordination for different job combinations
    xi.trust.enhanced.coordinateJobSpecificActions(trusts, master)
    xi.trust.enhanced.coordinateSubjobSynergy(trusts, master)
    xi.trust.enhanced.coordinateAdvancedBuffing(trusts, master)
    xi.trust.enhanced.coordinateAdvancedFormation(trusts, master)
end

-- Coordinate job-specific actions between different trust types
xi.trust.enhanced.coordinateJobSpecificActions = function(trusts, master)
    local target = master:getTarget()
    if not target or not target:isAlive() then
        return
    end
    
    -- Coordinate based on specific job combinations
    local jobCounts = {}
    for _, trust in ipairs(trusts) do
        local job = trust:getMainJob()
        jobCounts[job] = (jobCounts[job] or 0) + 1
    end
    
    -- Special coordination for job combinations
    if jobCounts[xi.job.BRD] and jobCounts[xi.job.COR] then
        -- BRD + COR combo: stagger songs and rolls
        xi.trust.enhanced.coordinateBardCorsair(trusts, target)
    end
    
    if jobCounts[xi.job.PLD] and jobCounts[xi.job.RUN] then
        -- Multiple tanks: coordinate enmity management
        xi.trust.enhanced.coordinateMultipleTanks(trusts, target)
    end
    
    if jobCounts[xi.job.SMN] and jobCounts[xi.job.BST] then
        -- Pet job coordination
        xi.trust.enhanced.coordinatePetJobs(trusts, target)
    end
end

-- Coordinate subjob synergy between trusts
xi.trust.enhanced.coordinateSubjobSynergy = function(trusts, master)
    -- Look for beneficial subjob combinations in the party
    for i, trust1 in ipairs(trusts) do
        for j, trust2 in ipairs(trusts) do
            if i ~= j then
                local job1 = trust1:getMainJob()
                local subjob1 = trust1:getSubJob()
                local job2 = trust2:getMainJob()
                local subjob2 = trust2:getSubJob()
                
                -- Coordinate complementary abilities
                if job1 == xi.job.WAR and subjob1 == xi.job.NIN and job2 == xi.job.NIN then
                    -- WAR/NIN + NIN: coordinate shadow timing
                    xi.trust.enhanced.coordinateShadowTiming(trust1, trust2)
                elseif job1 == xi.job.RDM and job2 == xi.job.BLM and subjob2 == xi.job.RDM then
                    -- RDM + BLM/RDM: coordinate refresh and convert usage
                    xi.trust.enhanced.coordinateMPManagement(trust1, trust2)
                end
            end
        end
    end
end

-- Specialized coordination functions
xi.trust.enhanced.coordinateBardCorsair = function(trusts, target)
    local bards = {}
    local corsairs = {}
    
    for _, trust in ipairs(trusts) do
        if trust:getMainJob() == xi.job.BRD then
            table.insert(bards, trust)
        elseif trust:getMainJob() == xi.job.COR then
            table.insert(corsairs, trust)
        end
    end
    
    -- Stagger song and roll timing to avoid conflicts
    for i, bard in ipairs(bards) do
        bard:setLocalVar("songDelay", i * 3) -- 3 second stagger
    end
    
    for i, corsair in ipairs(corsairs) do
        corsair:setLocalVar("rollDelay", i * 5) -- 5 second stagger
    end
end

xi.trust.enhanced.coordinateMultipleTanks = function(trusts, target)
    local tanks = {}
    for _, trust in ipairs(trusts) do
        local job = trust:getMainJob()
        if job == xi.job.PLD or job == xi.job.WAR or job == xi.job.RUN then
            table.insert(tanks, trust)
        end
    end
    
    if #tanks >= 2 then
        -- Designate primary and secondary tanks
        tanks[1]:setLocalVar("tankRole", "primary")
        tanks[2]:setLocalVar("tankRole", "secondary")
        
        -- Primary focuses on main target, secondary handles adds
        tanks[1]:setLocalVar("priorityTarget", target:getID())
        tanks[2]:setLocalVar("handleAdds", 1)
    end
end

xi.trust.enhanced.coordinatePetJobs = function(trusts, target)
    for _, trust in ipairs(trusts) do
        local job = trust:getMainJob()
        if job == xi.job.SMN or job == xi.job.BST or job == xi.job.PUP or job == xi.job.DRG then
            -- Coordinate pet usage to avoid overwhelming the battlefield
            trust:setLocalVar("petCoordination", 1)
        end
    end
end

xi.trust.enhanced.coordinateShadowTiming = function(trust1, trust2)
    -- Coordinate Utsusemi timing between WAR/NIN and NIN
    local delay1 = trust1:getLocalVar("shadowDelay") or 0
    local delay2 = trust2:getLocalVar("shadowDelay") or 0
    
    if delay1 == 0 and delay2 == 0 then
        -- Stagger shadow casting
        trust1:setLocalVar("shadowDelay", 2)
        trust2:setLocalVar("shadowDelay", 5)
    end
end

xi.trust.enhanced.coordinateMPManagement = function(rdm, blm)
    -- RDM prioritizes refresh on BLM, BLM uses convert when RDM MP is low
    rdm:setLocalVar("refreshTarget", blm:getID())
    blm:setLocalVar("refreshSource", rdm:getID())
end

return xi.trust.enhanced