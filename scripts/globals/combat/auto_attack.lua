-----------------------------------
-- Auto-Attack System Migration Framework for ITERATION 8
-- Migrating auto-attack logic from C++ to Lua for enhanced control
-----------------------------------
require('scripts/globals/combat/physical_utilities')

xi = xi or {}
xi.auto_attack = xi.auto_attack or {}

-- Multi-attack type enumeration
xi.auto_attack.MULTI_ATTACK_TYPE = {
    NORMAL = 0,
    DOUBLE = 1,
    TRIPLE = 2,
    QUAD = 3,
    MYTHIC_TWICE = 4,
    MYTHIC_THRICE = 5
}

-- Calculate multi-attack opportunities
xi.auto_attack.calculateMultiAttack = function(attacker, isFirstHit)
    local multiAttacks = 0
    local multiType = xi.auto_attack.MULTI_ATTACK_TYPE.NORMAL
    
    -- Get multi-attack rates
    local doubleRate = attacker:getMod(xi.mod.DOUBLE_ATTACK) + attacker:getMerit(xi.merit.DOUBLE_ATTACK_RATE)
    local tripleRate = attacker:getMod(xi.mod.TRIPLE_ATTACK) + attacker:getMerit(xi.merit.TRIPLE_ATTACK_RATE)
    local quadRate = attacker:getMod(xi.mod.QUAD_ATTACK)
    local oaThriceRate = attacker:getMod(xi.mod.MYTHIC_OCC_ATT_THRICE)
    local oaTwiceRate = attacker:getMod(xi.mod.MYTHIC_OCC_ATT_TWICE)
    
    -- Process multi-attack in order of priority
    if math.random(1, 100) <= quadRate then
        multiAttacks = 3
        multiType = xi.auto_attack.MULTI_ATTACK_TYPE.QUAD
    elseif math.random(1, 100) <= tripleRate then
        multiAttacks = 2
        multiType = xi.auto_attack.MULTI_ATTACK_TYPE.TRIPLE
    elseif math.random(1, 100) <= doubleRate then
        multiAttacks = 1
        multiType = xi.auto_attack.MULTI_ATTACK_TYPE.DOUBLE
    elseif isFirstHit and math.random(1, 100) <= oaThriceRate then
        multiAttacks = 2
        multiType = xi.auto_attack.MULTI_ATTACK_TYPE.MYTHIC_THRICE
    elseif isFirstHit and math.random(1, 100) <= oaTwiceRate then
        multiAttacks = 1
        multiType = xi.auto_attack.MULTI_ATTACK_TYPE.MYTHIC_TWICE
    end
    
    return multiAttacks, multiType
end

-- Enhanced auto-attack hit rate calculation
xi.auto_attack.calculateHitRate = function(attacker, target, bonusAcc)
    bonusAcc = bonusAcc or 0
    
    local acc = attacker:getACC() + bonusAcc
    local eva = target:getEVA()
    
    -- Level-based accuracy modifiers
    if attacker:getMainLvl() > target:getMainLvl() then
        acc = acc + (attacker:getMainLvl() - target:getMainLvl()) * 4
    elseif attacker:getMainLvl() < target:getMainLvl() then
        acc = acc - (target:getMainLvl() - attacker:getMainLvl()) * 4
    end
    
    -- Position-based modifiers
    if attacker:hasStatusEffect(xi.effect.INNIN) and attacker:isBehind(target, 23) then
        acc = acc + attacker:getStatusEffect(xi.effect.INNIN):getPower()
    end
    
    if target:hasStatusEffect(xi.effect.YONIN) and attacker:isFacing(target, 23) then
        acc = acc - target:getStatusEffect(xi.effect.YONIN):getPower()
    end
    
    -- Calculate hit rate
    local hitdiff = (acc - eva) / 2
    local hitrate = (75 + hitdiff) / 100
    
    -- Apply caps
    return math.max(0.2, math.min(0.95, hitrate))
end

-- Process a single auto-attack hit
xi.auto_attack.processSingleHit = function(attacker, target, isOffhand, isCritical)
    isOffhand = isOffhand or false
    isCritical = isCritical or false
    
    local slot = isOffhand and xi.slot.SUB or xi.slot.MAIN
    local weaponDamage = isOffhand and attacker:getOffhandDmg() or attacker:getWeaponDmg()
    local weaponType = attacker:getWeaponSkillType(slot)
    
    -- Calculate base damage
    local fSTR = xi.combat.physical.calculateMeleeStatFactor(attacker, target)
    local baseDamage = weaponDamage + fSTR
    
    -- Hand-to-hand bonus damage
    if weaponType == xi.skill.HAND_TO_HAND then
        local h2hSkill = attacker:getSkillLevel(xi.skill.HAND_TO_HAND) * 0.11 + 3
        baseDamage = baseDamage + h2hSkill
    end
    
    -- Calculate pDIF
    local pdif = xi.combat.physical.calculateMeleePDIF(
        attacker, target, weaponType, 1.0, isCritical, true, false, 1.0, true, slot, false
    )
    
    local finalDamage = baseDamage * pdif
    
    -- Apply damage type resistance
    finalDamage = target:physicalDmgTaken(finalDamage, attacker:getWeaponDamageType(slot))
    
    -- Apply damage reductions
    if finalDamage > 0 then
        finalDamage = finalDamage - target:getMod(xi.mod.PHALANX)
        finalDamage = math.max(0, finalDamage)
    end
    
    return math.floor(finalDamage)
end

-- Main auto-attack processing function
xi.auto_attack.processAutoAttack = function(attacker, target)
    local totalDamage = 0
    local hitsLanded = 0
    local hitRate = xi.auto_attack.calculateHitRate(attacker, target, 0)
    
    -- Process main hand attack
    if math.random() <= hitRate then
        local damage = xi.auto_attack.processSingleHit(attacker, target, false, false)
        totalDamage = totalDamage + damage
        hitsLanded = hitsLanded + 1
        
        -- Check for multi-attacks on main hand
        local multiAttacks, multiType = xi.auto_attack.calculateMultiAttack(attacker, true)
        for i = 1, multiAttacks do
            if math.random() <= hitRate then
                local multiDamage = xi.auto_attack.processSingleHit(attacker, target, false, false)
                totalDamage = totalDamage + multiDamage
                hitsLanded = hitsLanded + 1
            end
        end
    end
    
    -- Process off-hand attack if dual wielding
    if attacker:isDualWielding() then
        if math.random() <= hitRate then
            local damage = xi.auto_attack.processSingleHit(attacker, target, true, false)
            totalDamage = totalDamage + damage
            hitsLanded = hitsLanded + 1
            
            -- Check for multi-attacks on off hand
            local multiAttacks, multiType = xi.auto_attack.calculateMultiAttack(attacker, false)
            for i = 1, multiAttacks do
                if math.random() <= hitRate then
                    local multiDamage = xi.auto_attack.processSingleHit(attacker, target, true, false)
                    totalDamage = totalDamage + multiDamage
                    hitsLanded = hitsLanded + 1
                end
            end
        end
    end
    
    return totalDamage, hitsLanded
end

print("Auto-Attack Lua Framework loaded for ITERATION 8")
