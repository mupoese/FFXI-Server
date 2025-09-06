-----------------------------------
-- Enhanced Enmity System for ITERATION 8
-- Improved enmity calculations and retail accuracy
-----------------------------------

xi = xi or {}
xi.enhanced_enmity = xi.enhanced_enmity or {}

-- Enmity calculation constants
xi.enhanced_enmity.ENMITY_CONSTANTS = {
    DAMAGE_CE_MULTIPLIER = 1.0,
    DAMAGE_VE_MULTIPLIER = 1.0,
    CURE_CE_BASE = 40,
    CURE_VE_BASE = 40,
    MAGIC_DAMAGE_CE_MULTIPLIER = 1.0,
    MAGIC_DAMAGE_VE_MULTIPLIER = 0.5
}

-- Calculate enmity from damage dealt
xi.enhanced_enmity.calculateDamageEnmity = function(attacker, target, damage, attackType)
    attackType = attackType or xi.attackType.PHYSICAL
    
    local baseCE = 0
    local baseVE = 0
    
    if attackType == xi.attackType.PHYSICAL then
        -- Physical damage enmity
        baseCE = damage * xi.enhanced_enmity.ENMITY_CONSTANTS.DAMAGE_CE_MULTIPLIER
        baseVE = damage * xi.enhanced_enmity.ENMITY_CONSTANTS.DAMAGE_VE_MULTIPLIER
    elseif attackType == xi.attackType.MAGICAL then
        -- Magic damage enmity (lower VE generation)
        baseCE = damage * xi.enhanced_enmity.ENMITY_CONSTANTS.MAGIC_DAMAGE_CE_MULTIPLIER
        baseVE = damage * xi.enhanced_enmity.ENMITY_CONSTANTS.MAGIC_DAMAGE_VE_MULTIPLIER
    end
    
    -- Apply enmity modifiers
    local enmityMod = attacker:getMod(xi.mod.ENMITY)
    local enmityMultiplier = 1 + (enmityMod / 100)
    
    baseCE = baseCE * enmityMultiplier
    baseVE = baseVE * enmityMultiplier
    
    -- Job-specific enmity bonuses
    if attacker:getMainJob() == xi.job.PLD then
        local pallyBonus = 1 + (attacker:getJobPointLevel(xi.jp.SHIELD_MASTERY_ENMITY) * 0.01)
        baseCE = baseCE * pallyBonus
        baseVE = baseVE * pallyBonus
    end
    
    return math.floor(baseCE), math.floor(baseVE)
end

-- Calculate enmity from healing
xi.enhanced_enmity.calculateHealingEnmity = function(caster, target, healAmount)
    local baseCE = xi.enhanced_enmity.ENMITY_CONSTANTS.CURE_CE_BASE + (healAmount / 2)
    local baseVE = xi.enhanced_enmity.ENMITY_CONSTANTS.CURE_VE_BASE + (healAmount / 2)
    
    -- Apply enmity modifiers
    local enmityMod = caster:getMod(xi.mod.ENMITY)
    local enmityMultiplier = 1 + (enmityMod / 100)
    
    baseCE = baseCE * enmityMultiplier
    baseVE = baseVE * enmityMultiplier
    
    -- Healing-specific enmity reduction gear
    local healingEnmityReduction = caster:getMod(xi.mod.CURE_ENMITY_REDUCTION)
    if healingEnmityReduction > 0 then
        local reductionMultiplier = 1 - (healingEnmityReduction / 100)
        baseCE = baseCE * reductionMultiplier
        baseVE = baseVE * reductionMultiplier
    end
    
    return math.floor(baseCE), math.floor(baseVE)
end

-- Enhanced enmity distribution for multi-target abilities
xi.enhanced_enmity.distributeMultiTargetEnmity = function(caster, targets, baseEnmity, isAoE)
    isAoE = isAoE or false
    
    for _, target in pairs(targets) do
        if target:isValidTarget(caster, xi.targetFlag.ENEMY) then
            local finalEnmity = baseEnmity
            
            -- AoE abilities generate less enmity per target
            if isAoE and #targets > 1 then
                finalEnmity = finalEnmity * 0.7 -- 30% reduction for AoE
            end
            
            local ce, ve = xi.enhanced_enmity.calculateDamageEnmity(caster, target, finalEnmity, xi.attackType.MAGICAL)
            target:addEnmity(caster, ce, ve)
        end
    end
end

-- Process enmity transfer effects (e.g., Ninja tools)
xi.enhanced_enmity.processEnmityTransfer = function(source, target, transferAmount, transferType)
    transferType = transferType or "full" -- "full", "partial", "redirect"
    
    if transferType == "full" then
        -- Full enmity transfer (like Utsusemi)
        local sourceEnmity = source:getEnmityTowardsTarget(target)
        source:lowerEnmity(target, sourceEnmity.ce, sourceEnmity.ve)
        target:addEnmity(source, sourceEnmity.ce, sourceEnmity.ve)
    elseif transferType == "partial" then
        -- Partial enmity transfer
        local sourceEnmity = source:getEnmityTowardsTarget(target)
        local transferCE = math.floor(sourceEnmity.ce * transferAmount)
        local transferVE = math.floor(sourceEnmity.ve * transferAmount)
        
        source:lowerEnmity(target, transferCE, transferVE)
        target:addEnmity(source, transferCE, transferVE)
    elseif transferType == "redirect" then
        -- Redirect enmity to different target
        local sourceEnmity = source:getEnmityTowardsTarget(target)
        source:lowerEnmity(target, sourceEnmity.ce, sourceEnmity.ve)
        -- transferAmount in this case should be the new target
        if transferAmount and transferAmount:isValidTarget(source, xi.targetFlag.ENEMY) then
            transferAmount:addEnmity(source, sourceEnmity.ce, sourceEnmity.ve)
        end
    end
end

print("Enhanced Enmity System loaded for ITERATION 8")
