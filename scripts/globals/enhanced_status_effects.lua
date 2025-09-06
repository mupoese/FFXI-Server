-----------------------------------
-- Enhanced Status Effect System for ITERATION 9
-- Retail-accurate durations and interruption mechanics
-----------------------------------

xi = xi or {}
xi.enhanced_status = xi.enhanced_status or {}

-- Status effect duration calculations with retail accuracy
xi.enhanced_status.calculateStatusDuration = function(caster, target, baseEffect, baseDuration)
    local finalDuration = baseDuration
    
    -- Caster level bonus for status effects
    local casterLevel = caster:getMainLvl()
    local targetLevel = target:getMainLvl()
    local levelDiff = casterLevel - targetLevel
    
    -- Level difference modifier (retail formula)
    if levelDiff > 0 then
        finalDuration = finalDuration * (1 + (levelDiff * 0.1))
    else
        finalDuration = finalDuration * (1 + (levelDiff * 0.05))
    end
    
    -- Resistance calculations
    local resistance = target:getMod(baseEffect.resistanceMod or xi.mod.NONE)
    if resistance > 0 then
        finalDuration = finalDuration * (1 - (resistance / 100))
    end
    
    -- Caster enhancing gear
    local enhancingSkill = caster:getSkillLevel(xi.skill.ENHANCING_MAGIC)
    local skillBonus = enhancingSkill * 0.5 -- 0.5 seconds per skill level
    finalDuration = finalDuration + skillBonus
    
    -- Job-specific bonuses
    if caster:getMainJob() == xi.job.RDM then
        local rdmBonus = caster:getJobPointLevel(xi.jp.ENHANCING_DURATION) * 10
        finalDuration = finalDuration + rdmBonus
    end
    
    return math.max(1, math.floor(finalDuration))
end

-- Monster TP move interruption mechanics
xi.enhanced_status.checkInterruption = function(target, interruptType, damage)
    interruptType = interruptType or "damage"
    damage = damage or 0
    
    local interrupted = false
    local interruptChance = 0
    
    -- Damage-based interruption
    if interruptType == "damage" and damage > 0 then
        local targetHP = target:getHP()
        local damageRatio = damage / targetHP
        
        -- Higher damage = higher interrupt chance
        interruptChance = math.min(95, damageRatio * 100)
        
        -- Status effect specific modifiers
        if target:hasStatusEffect(xi.effect.SHOCK) then
            interruptChance = interruptChance + 15
        end
        
        if target:hasStatusEffect(xi.effect.TERROR) then
            interruptChance = interruptChance + 25
        end
    elseif interruptType == "stun" then
        interruptChance = 100 -- Stun always interrupts
    elseif interruptType == "silence" and target:isCasting() then
        local spell = target:getCastingSpell()
        if spell and spell:getSkillType() ~= xi.skill.SINGING then
            interruptChance = 100 -- Silence interrupts non-song casting
        end
    end
    
    -- Apply interruption
    if math.random(1, 100) <= interruptChance then
        interrupted = true
        target:interruptSpell()
        
        -- Additional effects for successful interruption
        if interruptType == "damage" and damage > (target:getHP() * 0.1) then
            target:addStatusEffect(xi.effect.AMNESIA, 0, 0, 5) -- 5 second amnesia
        end
    end
    
    return interrupted, interruptChance
end

-- Dispel priority system (retail accurate)
xi.enhanced_status.dispelPriority = function(target, dispelPower)
    dispelPower = dispelPower or 1
    
    local statusEffects = target:getStatusEffects()
    local dispellableEffects = {}
    
    -- Build priority list
    for _, effect in pairs(statusEffects) do
        if effect:getFlag(xi.effectFlag.DISPELABLE) then
            local priority = 0
            
            -- High priority effects (buffs)
            if effect:getType() == xi.effect.PROTECT or 
               effect:getType() == xi.effect.SHELL or
               effect:getType() == xi.effect.HASTE then
                priority = 100
            end
            
            -- Medium priority effects
            if effect:getType() == xi.effect.STONESKIN or
               effect:getType() == xi.effect.BLINK then
                priority = 75
            end
            
            -- Low priority effects
            if effect:getType() == xi.effect.REFRESH or
               effect:getType() == xi.effect.REGEN then
                priority = 50
            end
            
            -- Duration-based priority (newer effects first)
            priority = priority + (300 - effect:getDuration()) / 10
            
            table.insert(dispellableEffects, {
                effect = effect,
                priority = priority
            })
        end
    end
    
    -- Sort by priority (highest first)
    table.sort(dispellableEffects, function(a, b) return a.priority > b.priority end)
    
    -- Dispel effects based on power
    local dispelCount = 0
    for _, entry in pairs(dispellableEffects) do
        if dispelCount >= dispelPower then
            break
        end
        
        target:delStatusEffect(entry.effect:getType())
        dispelCount = dispelCount + 1
    end
    
    return dispelCount
end

-- Cross-system effect validation
xi.enhanced_status.validateEffectInteractions = function(target, newEffect)
    local conflicts = {}
    local enhancements = {}
    
    local existingEffects = target:getStatusEffects()
    
    for _, existing in pairs(existingEffects) do
        -- Check for conflicting effects
        if newEffect:conflictsWith(existing) then
            table.insert(conflicts, existing)
        end
        
        -- Check for enhancing interactions
        if newEffect:enhancesWith(existing) then
            table.insert(enhancements, existing)
        end
    end
    
    return conflicts, enhancements
end

print("Enhanced Status Effect System loaded for ITERATION 9")
