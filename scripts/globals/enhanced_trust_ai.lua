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
        },
    },
    
    [xi.job.BLM] = {
        role = xi.trust.enhanced.combatRole.DAMAGE_DEALER,
        behavior = xi.trust.enhanced.behaviorType.AGGRESSIVE,
        priorities = {
            { action = "nuke", priority = xi.trust.enhanced.priority.HIGH, condition = "enemyWeakness" },
            { action = "sleep", priority = xi.trust.enhanced.priority.HIGH, condition = "multipleEnemies" },
            { action = "bind", priority = xi.trust.enhanced.priority.MEDIUM, condition = "enemyMoving" },
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
    local jobBehavior = xi.trust.enhanced.jobBehaviors[job] or xi.trust.enhanced.jobBehaviors[xi.job.WAR]
    local config = customConfig or xi.trust.enhanced.aiConfig
    
    -- Set movement type based on role
    local movementType = xi.trust.movementType.MELEE
    if jobBehavior.role == xi.trust.enhanced.combatRole.HEALER then
        movementType = xi.trust.movementType.LONG_RANGE
    elseif jobBehavior.role == xi.trust.enhanced.combatRole.DAMAGE_DEALER then
        if job == xi.job.BLM or job == xi.job.RDM then
            movementType = xi.trust.movementType.MID_RANGE
        end
    end
    
    trust:setMobMod(xi.mobMod.TRUST_DISTANCE, movementType)
    
    -- Add enhanced AI gambits based on job
    xi.trust.enhanced.addJobSpecificGambits(trust, job, jobBehavior)
    
    -- Add general AI improvements
    xi.trust.enhanced.addGeneralAIGambits(trust, config)
    
    -- Set trust to use enhanced AI
    trust:setLocalVar("enhancedAI", 1)
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
        trust:addGambit(ai.t.SELF, { ai.c.ALWAYS, 0 }, { ai.r.JA, ai.s.SPECIFIC, xi.ja.DEFENDER })
        
    elseif job == xi.job.WHM then
        -- White Mage healer behavior
        trust:addGambit(ai.t.PARTY, { ai.c.HPP_LT, 25 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.CURE })
        trust:addGambit(ai.t.MASTER, { ai.c.HPP_LT, 75 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.CURE })
        trust:addGambit(ai.t.PARTY, { ai.c.STATUS_FLAG, xi.effectFlag.ERASABLE }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.ERASE })
        trust:addGambit(ai.t.PARTY, { ai.c.NOT_STATUS, xi.effect.PROTECT }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.PROTECT })
        trust:addGambit(ai.t.PARTY, { ai.c.NOT_STATUS, xi.effect.SHELL }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.SHELL })
        
    elseif job == xi.job.BLM then
        -- Black Mage damage dealer behavior
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.MA, ai.s.MB_ELEMENT, xi.magic.spellFamily.ANCIENT_MAGIC })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.MA, ai.s.BEST_AGAINST_TARGET, xi.magic.spellFamily.ELEMENTAL_MAGIC })
        trust:addGambit(ai.t.TARGET, { ai.c.CASTING_MA, 0 }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.STUN })
        
    elseif job == xi.job.RDM then
        -- Red Mage hybrid behavior
        trust:addGambit(ai.t.MASTER, { ai.c.NOT_STATUS, xi.effect.HASTE }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.HASTE })
        trust:addGambit(ai.t.MASTER, { ai.c.NOT_STATUS, xi.effect.REFRESH }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.REFRESH })
        trust:addGambit(ai.t.MASTER, { ai.c.HPP_LT, 50 }, { ai.r.MA, ai.s.HIGHEST, xi.magic.spellFamily.CURE })
        trust:addGambit(ai.t.TARGET, { ai.c.STATUS_FLAG, xi.effectFlag.DISPELABLE }, { ai.r.MA, ai.s.SPECIFIC, xi.magic.spell.DISPEL })
        trust:addGambit(ai.t.TARGET, { ai.c.ALWAYS, 0 }, { ai.r.MA, ai.s.BEST_AGAINST_TARGET, xi.magic.spellFamily.ELEMENTAL_MAGIC })
    end
    
    -- Add weapon skill usage for all jobs
    trust:addGambit(ai.t.TARGET, { ai.c.TP_GTE, 1000 }, { ai.r.WS, ai.s.HIGHEST, 0 })
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
                end
                
                if roleText ~= "" then
                    trust:messageText(trust, roleText, false)
                end
            end
        end
    end
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
    
    -- Validate AI performance
    xi.content.validation.validateTrustAI(trust)
end

return xi.trust.enhanced