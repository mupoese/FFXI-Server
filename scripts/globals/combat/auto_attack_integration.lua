-----------------------------------
-- Auto-Attack Integration for ITERATION 8
-- Complete integration of Lua auto-attack system with core combat
-----------------------------------
require('scripts/globals/combat/auto_attack')
require('scripts/globals/combat/enhanced_enmity')

xi = xi or {}
xi.auto_attack_integration = xi.auto_attack_integration or {}

-- Integration configuration
xi.auto_attack_integration.CONFIG = {
    ENABLE_LUA_AUTO_ATTACK = true,
    ENABLE_ENHANCED_MULTI_ATTACK = true,
    ENABLE_H2H_ENHANCEMENTS = true,
    ENABLE_DUAL_WIELD_INTEGRATION = true,
    ENABLE_CRITICAL_HIT_ENHANCEMENTS = true
}

-- Enhanced critical hit calculation for auto-attacks
xi.auto_attack_integration.calculateCriticalChance = function(attacker, target, weaponType)
    local baseCritRate = attacker:getMod(xi.mod.CRITHITRATE) / 100
    
    -- Weapon-specific critical bonuses
    local weaponCritBonus = 0
    if weaponType == xi.skill.DAGGER then
        weaponCritBonus = 0.02 -- Daggers have higher crit rate
    elseif weaponType == xi.skill.HAND_TO_HAND then
        weaponCritBonus = 0.015 -- H2H moderate crit bonus
    end
    
    -- Position-based critical bonuses
    local positionBonus = 0
    if attacker:isBehind(target) then
        positionBonus = 0.05 -- 5% bonus for back attacks
        
        -- Thief sneak attack enhancement
        if attacker:getMainJob() == xi.job.THF and attacker:hasStatusEffect(xi.effect.SNEAK_ATTACK) then
            positionBonus = positionBonus + 0.15 -- Additional 15% for sneak attack
        end
    end
    
    -- Job-specific enhancements
    local jobBonus = 0
    if attacker:getMainJob() == xi.job.WAR then
        local berserkerLevel = attacker:getJobPointLevel(xi.jp.BERSERK_EFFECT) or 0
        if attacker:hasStatusEffect(xi.effect.BERSERK) then
            jobBonus = berserkerLevel * 0.005 -- 0.5% per job point level
        end
    elseif attacker:getMainJob() == xi.job.MNK then
        local focusLevel = attacker:getJobPointLevel(xi.jp.FOCUS_EFFECT) or 0
        if attacker:hasStatusEffect(xi.effect.FOCUS) then
            jobBonus = focusLevel * 0.003 -- 0.3% per job point level
        end
    end
    
    local totalCritRate = baseCritRate + weaponCritBonus + positionBonus + jobBonus
    return math.min(totalCritRate, 0.3) -- Cap at 30% for auto-attacks
end

-- Enhanced hand-to-hand combat system
xi.auto_attack_integration.processH2HCombat = function(attacker, target)
    local weaponType = attacker:getWeaponSkillType(xi.slot.MAIN)
    if weaponType ~= xi.skill.HAND_TO_HAND then
        return xi.auto_attack.processAutoAttack(attacker, target)
    end
    
    local totalDamage = 0
    local hitsLanded = 0
    local hitRate = xi.auto_attack.calculateHitRate(attacker, target, 0)
    local critChance = xi.auto_attack_integration.calculateCriticalChance(attacker, target, weaponType)
    
    -- H2H has natural multi-hit potential
    local baseHits = 1
    local h2hSkill = attacker:getSkillLevel(xi.skill.HAND_TO_HAND)
    
    -- Higher skill levels grant additional hit chances
    if h2hSkill >= 150 then
        baseHits = 2 -- Expert level grants double hits
    end
    if h2hSkill >= 250 then
        baseHits = 3 -- Master level grants triple hits
    end
    
    -- Process base H2H hits
    for i = 1, baseHits do
        local currentHitRate = hitRate
        if i > 1 then
            currentHitRate = hitRate * 0.9 -- Subsequent hits have reduced accuracy
        end
        
        if math.random() <= currentHitRate then
            local isCritical = math.random() <= critChance
            local damage = xi.auto_attack.processSingleHit(attacker, target, false, isCritical)
            
            -- H2H damage scaling for multiple hits
            if i > 1 then
                damage = math.floor(damage * 0.75) -- Subsequent hits do less damage
            end
            
            totalDamage = totalDamage + damage
            hitsLanded = hitsLanded + 1
            
            -- Generate appropriate enmity
            local ce, ve = xi.enhanced_enmity.calculateDamageEnmity(attacker, target, damage, xi.attackType.PHYSICAL)
            target:addEnmity(attacker, ce, ve)
        end
    end
    
    -- Check for additional multi-attacks
    local multiAttacks, multiType = xi.auto_attack.calculateMultiAttack(attacker, true)
    for i = 1, multiAttacks do
        if math.random() <= hitRate then
            local isCritical = math.random() <= critChance
            local multiDamage = xi.auto_attack.processSingleHit(attacker, target, false, isCritical)
            multiDamage = math.floor(multiDamage * 0.8) -- Multi-attack penalty
            
            totalDamage = totalDamage + multiDamage
            hitsLanded = hitsLanded + 1
            
            -- Generate enmity for multi-attacks
            local ce, ve = xi.enhanced_enmity.calculateDamageEnmity(attacker, target, multiDamage, xi.attackType.PHYSICAL)
            target:addEnmity(attacker, ce, ve)
        end
    end
    
    return totalDamage, hitsLanded
end

-- Enhanced dual wield integration
xi.auto_attack_integration.processDualWield = function(attacker, target)
    if not attacker:isDualWielding() then
        return xi.auto_attack.processAutoAttack(attacker, target)
    end
    
    local totalDamage = 0
    local hitsLanded = 0
    local hitRate = xi.auto_attack.calculateHitRate(attacker, target, 0)
    
    -- Enhanced dual wield delay calculation
    local mainDelay = attacker:getWeaponDelay(xi.slot.MAIN)
    local subDelay = attacker:getWeaponDelay(xi.slot.SUB)
    local dwLevel = attacker:getMod(xi.mod.DUAL_WIELD)
    
    -- Calculate attack frequency based on dual wield level
    local dwModifier = 1 + (dwLevel * 0.01) -- 1% faster per DW level
    local attackFrequency = (mainDelay + subDelay) / (2 * dwModifier)
    
    -- Process main hand attack
    if math.random() <= hitRate then
        local critChance = xi.auto_attack_integration.calculateCriticalChance(attacker, target, attacker:getWeaponSkillType(xi.slot.MAIN))
        local isCritical = math.random() <= critChance
        local damage = xi.auto_attack.processSingleHit(attacker, target, false, isCritical)
        
        totalDamage = totalDamage + damage
        hitsLanded = hitsLanded + 1
        
        -- Check for main hand multi-attacks
        local multiAttacks, multiType = xi.auto_attack.calculateMultiAttack(attacker, true)
        for i = 1, multiAttacks do
            if math.random() <= hitRate then
                local multiDamage = xi.auto_attack.processSingleHit(attacker, target, false, false)
                totalDamage = totalDamage + multiDamage
                hitsLanded = hitsLanded + 1
            end
        end
    end
    
    -- Process off-hand attack with dual wield enhancements
    local ohHitRate = hitRate * 0.9 -- Off-hand has reduced accuracy
    if math.random() <= ohHitRate then
        local critChance = xi.auto_attack_integration.calculateCriticalChance(attacker, target, attacker:getWeaponSkillType(xi.slot.SUB))
        local isCritical = math.random() <= critChance
        local damage = xi.auto_attack.processSingleHit(attacker, target, true, isCritical)
        
        totalDamage = totalDamage + damage
        hitsLanded = hitsLanded + 1
        
        -- Check for off-hand multi-attacks
        local multiAttacks, multiType = xi.auto_attack.calculateMultiAttack(attacker, false)
        for i = 1, multiAttacks do
            if math.random() <= ohHitRate then
                local multiDamage = xi.auto_attack.processSingleHit(attacker, target, true, false)
                totalDamage = totalDamage + multiDamage
                hitsLanded = hitsLanded + 1
            end
        end
    end
    
    return totalDamage, hitsLanded
end

-- Main integration function
xi.auto_attack_integration.processIntegratedAutoAttack = function(attacker, target)
    if not xi.auto_attack_integration.CONFIG.ENABLE_LUA_AUTO_ATTACK then
        return 0, 0 -- Fall back to C++ system
    end
    
    local weaponType = attacker:getWeaponSkillType(xi.slot.MAIN)
    
    -- Route to appropriate specialized system
    if weaponType == xi.skill.HAND_TO_HAND and xi.auto_attack_integration.CONFIG.ENABLE_H2H_ENHANCEMENTS then
        return xi.auto_attack_integration.processH2HCombat(attacker, target)
    elseif attacker:isDualWielding() and xi.auto_attack_integration.CONFIG.ENABLE_DUAL_WIELD_INTEGRATION then
        return xi.auto_attack_integration.processDualWield(attacker, target)
    else
        return xi.auto_attack.processAutoAttack(attacker, target)
    end
end

print("Auto-Attack Integration System loaded for ITERATION 8")