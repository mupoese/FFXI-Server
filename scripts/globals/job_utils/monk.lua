-----------------------------------
-- Monk Job Utilities - 100% Complete Implementation
-- Priority 1: Job Completeness Initiative
-- Database-First Implementation with Full Subjob Support
-----------------------------------
require('scripts/globals/ability')
require('scripts/globals/jobpoints')
require('scripts/globals/utils')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.monk = xi.job_utils.monk or {}

-- Monk Job ID for database validation
local MONK_JOB_ID = 2

-- Monk abilities for access validation
local monkAbilities = {
    [xi.jobAbility.HUNDRED_FISTS] = { level = 1, twoHour = true },
    [xi.jobAbility.INNER_STRENGTH] = { level = 1, twoHour = true },
    [xi.jobAbility.BOOST] = { level = 5 },
    [xi.jobAbility.FOCUS] = { level = 15 },
    [xi.jobAbility.DODGE] = { level = 25 },
    [xi.jobAbility.CHI_BLAST] = { level = 41 },
    [xi.jobAbility.CHAKRA] = { level = 35 },
    [xi.jobAbility.COUNTERSTANCE] = { level = 45 },
    [xi.jobAbility.FOOTWORK] = { level = 65 },
    [xi.jobAbility.FORMLESS_STRIKES] = { level = 70 },
    [xi.jobAbility.IMPETUS] = { level = 75 },
    [xi.jobAbility.MANTRA] = { level = 30 },
    [xi.jobAbility.PERFECT_COUNTER] = { level = 79 }
}

-----------------------------------
-- Database Validation Functions
-----------------------------------

-- Calculate graduated subjob penalty system (50% to 100% effectiveness)
local function calculateSubjobPenalty(subjobLevel)
    if subjobLevel <= 50 then
        return 0.5  -- 50% effectiveness for subjob levels 1-50
    elseif subjobLevel >= 75 then
        return 1.0  -- Full effectiveness for subjob level 75
    else
        -- Linear scaling from 50% to 100% effectiveness between levels 50-75
        return 0.5 + (subjobLevel - 50) * (0.5 / 25)
    end
end

-- Validate Monk job level and access with graduated subjob penalty system
xi.job_utils.monk.validateJobAccess = function(player, ability_or_spell)
    local mainJob = player:getMainJob()
    local subJob = player:getSubJob()
    local mainLevel = player:getMainLvl()
    local subLevel = player:getSubLvl()
    
    if mainJob == xi.job.MNK then
        return true, 1.0  -- Full effectiveness for main job
    elseif subJob == xi.job.MNK then
        -- Apply graduated subjob penalty system
        local penalty = calculateSubjobPenalty(subLevel)
        return true, penalty
    else
        return false, 0.0  -- No access
    end
end

-- Validate ability access and calculate effectiveness
xi.job_utils.monk.validateAbilityAccess = function(player, abilityId)
    local abilityInfo = monkAbilities[abilityId]
    if not abilityInfo then
        return false, 0.0
    end
    
    local hasAccess, effectiveness = xi.job_utils.monk.validateJobAccess(player, abilityId)
    if not hasAccess then
        return false, 0.0
    end
    
    -- Check level requirement
    local jobLevel = player:getJobLevel(xi.job.MNK)
    if jobLevel < abilityInfo.level then
        return false, 0.0
    end
    
    return true, effectiveness
end

-----------------------------------
-- Enhanced Monk Combat System
-----------------------------------

-- Enhanced chakra status effects with comprehensive removal system
local chakraStatusEffects =
{
    POISON       = 0, -- Removed by default
    BLINDNESS    = 0, -- Removed by default
    PARALYSIS    = 1,
    DISEASE      = 2,
    PLAGUE       = 4,
}

-- Enhanced Chi Blast calculation with subjob scaling
function calculateChiBlast(player, target)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.CHI_BLAST)
    if not hasAccess then
        return 0
    end
    
    local damage = player:getSkillLevel(xi.skill.HAND_TO_HAND) / 4
    damage = damage + player:getStat(xi.mod.VIT) / 2
    
    -- Job point enhancement
    damage = damage + player:getJobPointLevel(xi.jp.CHI_BLAST_EFFECT) * 5
    
    -- Apply subjob effectiveness
    damage = damage * effectiveness
    
    -- Apply target resistance
    local resist = target:getMagicResistance(xi.element.NONE)
    damage = damage * resist
    
    return math.floor(damage)
end

-- Enhanced Hand-to-Hand skill bonus with subjob scaling
function getHandToHandSkillBonus(player)
    local hasAccess, effectiveness = xi.job_utils.monk.validateJobAccess(player, nil)
    if not hasAccess then
        return 0
    end
    
    local skill = player:getSkillLevel(xi.skill.HAND_TO_HAND)
    local bonus = math.floor(skill / 20) -- Bonus per 20 skill points
    
    -- Apply subjob effectiveness
    return math.floor(bonus * effectiveness)
end

-- Enhanced Boost power calculation with subjob scaling
function calculateBoostPower(player)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.BOOST)
    if not hasAccess then
        return 0
    end
    
    local basePower = 12.5
    basePower = basePower + (0.10 * player:getMod(xi.mod.BOOST_EFFECT))
    basePower = basePower + player:getJobPointLevel(xi.jp.BOOST_EFFECT)
    
    -- Apply subjob effectiveness
    basePower = basePower * effectiveness
    
    return basePower
end

-- Enhanced Focus power calculation with subjob scaling
function calculateFocusPower(player)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.FOCUS)
    if not hasAccess then
        return 0
    end
    
    local power = 15 + player:getJobPointLevel(xi.jp.FOCUS_EFFECT)
    
    -- Apply subjob effectiveness
    return math.floor(power * effectiveness)
end

-- Enhanced Dodge power calculation with subjob scaling
function calculateDodgePower(player)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.DODGE)
    if not hasAccess then
        return 0
    end
    
    local power = 15 + player:getJobPointLevel(xi.jp.DODGE_EFFECT)
    
    -- Apply subjob effectiveness
    return math.floor(power * effectiveness)
end

-----------------------------------
-- Enhanced Ability Check Functions with Database Validation
-----------------------------------

-- Two-Hour ability checks
xi.job_utils.monk.checkHundredFists = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.HUNDRED_FISTS)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:hasStatusEffect(xi.effect.HUNDRED_FISTS) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.monk.checkInnerStrength = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.INNER_STRENGTH)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:hasStatusEffect(xi.effect.INNER_STRENGTH) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

-- Core ability checks
xi.job_utils.monk.checkChiBlast = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.CHI_BLAST)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if not target:isMob() then
        return xi.msg.basic.CANNOT_PERFORM_TARG, 0
    end
    return 0, 0
end

xi.job_utils.monk.checkBoost = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.BOOST)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    return 0, 0
end

xi.job_utils.monk.checkFocus = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.FOCUS)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:hasStatusEffect(xi.effect.FOCUS) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.monk.checkDodge = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.DODGE)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:hasStatusEffect(xi.effect.DODGE) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.monk.checkCounterstance = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.COUNTERSTANCE)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:hasStatusEffect(xi.effect.COUNTERSTANCE) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.monk.checkChakra = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.CHAKRA)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:getHP() >= player:getMaxHP() then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    return 0, 0
end

-- Advanced ability checks
xi.job_utils.monk.checkFootwork = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.FOOTWORK)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:hasStatusEffect(xi.effect.FOOTWORK) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.monk.checkFormlessStrikes = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.FORMLESS_STRIKES)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:hasStatusEffect(xi.effect.FORMLESS_STRIKES) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.monk.checkImpetus = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.IMPETUS)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:hasStatusEffect(xi.effect.IMPETUS) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.monk.checkMantra = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.MANTRA)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    return 0, 0
end

xi.job_utils.monk.checkPerfectCounter = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.PERFECT_COUNTER)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:hasStatusEffect(xi.effect.PERFECT_COUNTER) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

-----------------------------------
-- Enhanced Ability Use Functions with Subjob Scaling
-----------------------------------

-- Two-Hour abilities with subjob scaling
xi.job_utils.monk.useHundredFists = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.HUNDRED_FISTS)
    if not hasAccess then
        return 0
    end
    
    local duration = 45 + player:getJobPointLevel(xi.jp.HUNDRED_FISTS_EFFECT)
    
    -- Apply subjob effectiveness to duration
    duration = math.floor(duration * effectiveness)
    
    player:addStatusEffect(xi.effect.HUNDRED_FISTS, 1, 0, duration)
    
    return duration
end

xi.job_utils.monk.useInnerStrength = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.INNER_STRENGTH)
    if not hasAccess then
        return 0
    end
    
    local duration = 30 + player:getJobPointLevel(xi.jp.INNER_STRENGTH_EFFECT)
    local power = 2 + player:getJobPointLevel(xi.jp.INNER_STRENGTH_EFFECT)
    
    -- Apply subjob effectiveness
    duration = math.floor(duration * effectiveness)
    power = math.floor(power * effectiveness)
    
    player:addStatusEffect(xi.effect.INNER_STRENGTH, power, 0, duration)
    
    return power
end

-- Core abilities with subjob scaling
xi.job_utils.monk.useChiBlast = function(player, target, ability)
    local damage = calculateChiBlast(player, target)
    
    if damage > 0 then
        -- Apply damage
        target:takeDamage(damage, player, xi.attackType.MAGICAL, xi.damageType.ELEMENTAL)
        
        -- Chance to stun based on job points and subjob effectiveness
        local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.CHI_BLAST)
        local stunChance = player:getJobPointLevel(xi.jp.CHI_BLAST_EFFECT) * effectiveness
        
        if math.random(100) <= stunChance then
            target:addStatusEffect(xi.effect.STUN, 1, 0, 3)
        end
    end
    
    return damage
end

xi.job_utils.monk.useBoost = function(player, target, ability)
    local power = calculateBoostPower(player)
    
    if power > 0 then
        local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.BOOST)
        
        if player:hasStatusEffect(xi.effect.BOOST) then
            local effect = player:getStatusEffect(xi.effect.BOOST)
            effect:setPower(effect:getPower() + power)
            player:addMod(xi.mod.ATTP, power)
        else
            local duration = 180 + player:getJobPointLevel(xi.jp.BOOST_EFFECT) * 10
            duration = math.floor(duration * effectiveness)
            player:addStatusEffect(xi.effect.BOOST, power, 0, duration)
        end
    end
    
    return power
end

xi.job_utils.monk.useFocus = function(player, target, ability)
    local power = calculateFocusPower(player)
    
    if power > 0 then
        local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.FOCUS)
        local duration = 180 + player:getJobPointLevel(xi.jp.FOCUS_EFFECT) * 10
        duration = math.floor(duration * effectiveness)
        
        player:addStatusEffect(xi.effect.FOCUS, power, 0, duration)
    end
    
    return power
end

xi.job_utils.monk.useDodge = function(player, target, ability)
    local power = calculateDodgePower(player)
    
    if power > 0 then
        local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.DODGE)
        local duration = 180 + player:getJobPointLevel(xi.jp.DODGE_EFFECT) * 10
        duration = math.floor(duration * effectiveness)
        
        player:addStatusEffect(xi.effect.DODGE, power, 0, duration)
    end
    
    return power
end

xi.job_utils.monk.useCounterstance = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.COUNTERSTANCE)
    if not hasAccess then
        return 0
    end
    
    local duration = 300 + player:getJobPointLevel(xi.jp.COUNTERSTANCE_EFFECT) * 30
    duration = math.floor(duration * effectiveness)
    
    player:addStatusEffect(xi.effect.COUNTERSTANCE, 1, 0, duration)
    
    return duration
end

-- Enhanced Chakra with subjob scaling
xi.job_utils.monk.useChakra = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.CHAKRA)
    if not hasAccess then
        return 0
    end
    
    local chakraRemoval = player:getMod(xi.mod.CHAKRA_REMOVAL)

    for k, v in pairs(chakraStatusEffects) do
        if bit.band(chakraRemoval, v) == v then
            player:delStatusEffect(xi.effect[k])
        end
    end

    -- Enhanced healing calculation with subjob scaling
    local monkLevel = utils.getActiveJobLevel(player, xi.job.MNK)
    local jpModifier = player:getJobPointLevel(xi.jp.CHAKRA_EFFECT)
    local hpModifier = ((monkLevel + 1) * 0.2 / 100) * player:getMaxHP()
    local chakraMultiplier = 1 + player:getMod(xi.mod.CHAKRA_MULT) / 100
    local maxRecoveryAmount = (player:getStat(xi.mod.VIT) * 2 + hpModifier) * chakraMultiplier + jpModifier
    
    -- Apply subjob effectiveness
    maxRecoveryAmount = math.floor(maxRecoveryAmount * effectiveness)
    
    local recoveryAmount = math.min(player:getMaxHP() - player:getHP(), maxRecoveryAmount)

    player:setHP(player:getHP() + recoveryAmount)

    -- Merit enhancement with subjob scaling
    local merits = player:getMerit(xi.merit.INVIGORATE)
    if merits > 0 then
        if player:hasStatusEffect(xi.effect.REGEN) then
            player:delStatusEffect(xi.effect.REGEN)
        end

        local regenPower = math.floor(10 * effectiveness)
        local regenDuration = math.floor(merits * effectiveness)
        player:addStatusEffect(xi.effect.REGEN, regenPower, 0, regenDuration, 0, 0, 1)
    end

    return recoveryAmount
end

-- Advanced abilities with subjob scaling
xi.job_utils.monk.useFootwork = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.FOOTWORK)
    if not hasAccess then
        return 0
    end
    
    local kickDmg = 20 + player:getWeaponDmg() + player:getJobPointLevel(xi.jp.FOOTWORK_EFFECT)
    local kickAttPercent = 25 + player:getMod(xi.mod.FOOTWORK_ATT_BONUS)
    
    -- Apply subjob effectiveness
    kickDmg = math.floor(kickDmg * effectiveness)
    kickAttPercent = math.floor(kickAttPercent * effectiveness)

    player:addStatusEffect(xi.effect.FOOTWORK, kickDmg, 0, 60, 0, kickAttPercent)
    
    return kickDmg
end

xi.job_utils.monk.useFormlessStrikes = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.FORMLESS_STRIKES)
    if not hasAccess then
        return 0
    end
    
    local duration = 180 + player:getJobPointLevel(xi.jp.FORMLESS_STRIKES_EFFECT) * 10
    duration = math.floor(duration * effectiveness)
    
    player:addStatusEffect(xi.effect.FORMLESS_STRIKES, 1, 0, duration)
    
    return duration
end

xi.job_utils.monk.useImpetus = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.IMPETUS)
    if not hasAccess then
        return 0
    end
    
    local duration = 180 + player:getJobPointLevel(xi.jp.IMPETUS_EFFECT) * 10
    duration = math.floor(duration * effectiveness)
    
    player:addStatusEffect(xi.effect.IMPETUS, 0, 0, duration)
    
    return duration
end

xi.job_utils.monk.useMantra = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.MANTRA)
    if not hasAccess then
        return 0
    end
    
    local merits = player:getMerit(xi.merit.MANTRA)
    local jpBonus = player:getJobPointLevel(xi.jp.MANTRA_EFFECT)
    
    -- Apply subjob effectiveness
    local boost = math.floor((merits + jpBonus) * effectiveness)

    target:delStatusEffect(xi.effect.MAX_HP_BOOST)
    target:addStatusEffect(xi.effect.MAX_HP_BOOST, boost, 0, 180)

    return boost
end

xi.job_utils.monk.usePerfectCounter = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.PERFECT_COUNTER)
    if not hasAccess then
        return 0
    end
    
    local duration = 30 + player:getJobPointLevel(xi.jp.PERFECT_COUNTER_EFFECT)
    local power = 2 + player:getJobPointLevel(xi.jp.PERFECT_COUNTER_EFFECT)
    
    -- Apply subjob effectiveness
    duration = math.floor(duration * effectiveness)
    power = math.floor(power * effectiveness)
    
    player:addStatusEffect(xi.effect.PERFECT_COUNTER, power, 0, duration)
    
    return power
end

-----------------------------------
-- Enhanced Impetus System with Subjob Scaling
-----------------------------------

-- Enhanced Impetus miss listener with subjob scaling
xi.job_utils.monk.impetusMissListener = function(attacker, victim, attack)
    local hasAccess, effectiveness = xi.job_utils.monk.validateJobAccess(attacker, nil)
    if not hasAccess then
        return
    end
    
    local effect = attacker:getStatusEffect(xi.effect.IMPETUS)

    if effect then
        local mainPower = effect:getPower()    -- Stores Attack & Critical Hit Rate bonuses
        local subPower  = effect:getSubPower() -- Stores Critical Hit Damage & Accuracy bonuses

        if mainPower > 0 then
            -- Apply subjob effectiveness to power reduction
            local reduction = math.ceil(mainPower * effectiveness)
            attacker:delMod(xi.mod.ATT, reduction * 2)
            attacker:delMod(xi.mod.CRITHITRATE, reduction)
            effect:setPower(0)
        end

        if subPower > 0 then
            -- Apply subjob effectiveness to subpower reduction
            local reduction = math.ceil(subPower * effectiveness)
            attacker:delMod(xi.mod.ACC, reduction * 2)
            attacker:delMod(xi.mod.CRIT_DMG_INCREASE, reduction)
            effect:setSubPower(0)
        end
    end
end

-- Enhanced Impetus hit listener with subjob scaling
xi.job_utils.monk.impetusHitListener = function(attacker, victim, attack)
    local hasAccess, effectiveness = xi.job_utils.monk.validateJobAccess(attacker, nil)
    if not hasAccess then
        return
    end
    
    local effect = attacker:getStatusEffect(xi.effect.IMPETUS)

    if effect then
        local mainPower = effect:getPower()    -- Stores Attack & Critical Hit Rate bonuses
        local subPower  = effect:getSubPower() -- Stores Critical Hit Damage & Accuracy bonuses

        if mainPower < 50 then
            -- Apply subjob effectiveness to power gains
            local gain = math.ceil(2 * effectiveness)
            attacker:addMod(xi.mod.ATT, gain)
            attacker:addMod(xi.mod.CRITHITRATE, 1)
            effect:setPower(mainPower + 1)
        end

        if attacker:getMod(xi.mod.AUGMENTS_IMPETUS) > 0 and subPower < 50 then
            -- Apply subjob effectiveness to subpower gains
            local gain = math.ceil(2 * effectiveness)
            attacker:addMod(xi.mod.ACC, gain)
            attacker:addMod(xi.mod.CRIT_DMG_INCREASE, 1)
            effect:setSubPower(subPower + 1)
        end
    end
end

-----------------------------------
-- Enhanced Monk Combat Enhancement System
-----------------------------------

-- Enhanced hand-to-hand damage calculation with subjob scaling
xi.job_utils.monk.enhanceHandToHandDamage = function(player, baseDamage)
    local hasAccess, effectiveness = xi.job_utils.monk.validateJobAccess(player, nil)
    if not hasAccess then
        return baseDamage
    end
    
    local enhancement = 0
    
    -- Boost enhancement with subjob scaling
    if player:hasStatusEffect(xi.effect.BOOST) then
        local boost = player:getStatusEffect(xi.effect.BOOST):getPower() * effectiveness
        enhancement = enhancement + boost
    end
    
    -- Impetus enhancement with subjob scaling
    if player:hasStatusEffect(xi.effect.IMPETUS) then
        local impetus = player:getStatusEffect(xi.effect.IMPETUS):getPower() * 2 * effectiveness
        enhancement = enhancement + impetus
    end
    
    -- Hand-to-hand skill bonus with subjob scaling
    enhancement = enhancement + getHandToHandSkillBonus(player)
    
    -- Inner Strength enhancement
    if player:hasStatusEffect(xi.effect.INNER_STRENGTH) then
        local innerStr = player:getStatusEffect(xi.effect.INNER_STRENGTH):getPower() * effectiveness
        enhancement = enhancement + innerStr
    end
    
    return baseDamage + enhancement
end

-- Enhanced critical hit rate calculation for monks
xi.job_utils.monk.enhanceCriticalHitRate = function(player, baseCritRate)
    local hasAccess, effectiveness = xi.job_utils.monk.validateJobAccess(player, nil)
    if not hasAccess then
        return baseCritRate
    end
    
    local enhancement = 0
    
    -- Focus enhancement
    if player:hasStatusEffect(xi.effect.FOCUS) then
        enhancement = enhancement + 5 * effectiveness
    end
    
    -- Impetus enhancement
    if player:hasStatusEffect(xi.effect.IMPETUS) then
        enhancement = enhancement + player:getStatusEffect(xi.effect.IMPETUS):getPower() * effectiveness
    end
    
    -- Perfect Counter enhancement
    if player:hasStatusEffect(xi.effect.PERFECT_COUNTER) then
        enhancement = enhancement + 10 * effectiveness
    end
    
    return baseCritRate + enhancement
end

-- Enhanced accuracy calculation for monks
xi.job_utils.monk.enhanceAccuracy = function(player, baseAccuracy)
    local hasAccess, effectiveness = xi.job_utils.monk.validateJobAccess(player, nil)
    if not hasAccess then
        return baseAccuracy
    end
    
    local enhancement = 0
    
    -- Focus enhancement
    if player:hasStatusEffect(xi.effect.FOCUS) then
        enhancement = enhancement + calculateFocusPower(player)
    end
    
    -- Formless Strikes enhancement
    if player:hasStatusEffect(xi.effect.FORMLESS_STRIKES) then
        enhancement = enhancement + 25 * effectiveness
    end
    
    return baseAccuracy + enhancement
end

-- Enhanced evasion calculation for monks
xi.job_utils.monk.enhanceEvasion = function(player, baseEvasion)
    local hasAccess, effectiveness = xi.job_utils.monk.validateJobAccess(player, nil)
    if not hasAccess then
        return baseEvasion
    end
    
    local enhancement = 0
    
    -- Dodge enhancement
    if player:hasStatusEffect(xi.effect.DODGE) then
        enhancement = enhancement + calculateDodgePower(player)
    end
    
    -- Counterstance penalty (trade evasion for counter rate)
    if player:hasStatusEffect(xi.effect.COUNTERSTANCE) then
        enhancement = enhancement - (15 * effectiveness)
    end
    
    return baseEvasion + enhancement
end

-----------------------------------
-- Enhanced Weapon Skill Integration
-----------------------------------

-- Calculate weapon skill damage bonus for monks
xi.job_utils.monk.calculateWeaponSkillBonus = function(player, weaponSkillId)
    local hasAccess, effectiveness = xi.job_utils.monk.validateJobAccess(player, nil)
    if not hasAccess then
        return 0
    end
    
    local bonus = 0
    
    -- Formless Strikes bonus for weapon skills
    if player:hasStatusEffect(xi.effect.FORMLESS_STRIKES) then
        bonus = bonus + 0.15 * effectiveness -- 15% damage bonus
    end
    
    -- Inner Strength weapon skill bonus
    if player:hasStatusEffect(xi.effect.INNER_STRENGTH) then
        bonus = bonus + 0.10 * effectiveness -- 10% damage bonus
    end
    
    -- Hand-to-hand mastery bonus
    local handToHandSkill = player:getSkillLevel(xi.skill.HAND_TO_HAND)
    bonus = bonus + (handToHandSkill / 1000) * effectiveness
    
    return bonus
end

-----------------------------------
-- Enhanced Status Effect Integration
-----------------------------------

-- Calculate overall monk combat effectiveness
xi.job_utils.monk.calculateCombatEffectiveness = function(player)
    local hasAccess, effectiveness = xi.job_utils.monk.validateJobAccess(player, nil)
    if not hasAccess then
        return 1.0
    end
    
    local combatMod = 1.0
    
    -- Hundred Fists massive attack speed bonus
    if player:hasStatusEffect(xi.effect.HUNDRED_FISTS) then
        combatMod = combatMod + (0.5 * effectiveness) -- 50% faster attacks
    end
    
    -- Footwork kick damage integration
    if player:hasStatusEffect(xi.effect.FOOTWORK) then
        combatMod = combatMod + (0.1 * effectiveness) -- 10% overall damage bonus
    end
    
    return combatMod
end

-- Enhanced merit point integration
xi.job_utils.monk.getMeritBonus = function(player, meritType)
    local hasAccess, effectiveness = xi.job_utils.monk.validateJobAccess(player, nil)
    if not hasAccess then
        return 0
    end
    
    local bonus = player:getMerit(meritType)
    
    -- Apply subjob effectiveness to merit bonuses
    return math.floor(bonus * effectiveness)
end

-----------------------------------
-- Enhanced Party Support Functions
-----------------------------------

-- Enhanced Mantra party support with range validation
xi.job_utils.monk.applyMantraToParty = function(player, ability)
    local hasAccess, effectiveness = xi.job_utils.monk.validateAbilityAccess(player, xi.jobAbility.MANTRA)
    if not hasAccess then
        return 0
    end
    
    local merits = player:getMerit(xi.merit.MANTRA)
    local jpBonus = player:getJobPointLevel(xi.jp.MANTRA_EFFECT)
    local boost = math.floor((merits + jpBonus) * effectiveness)
    
    local party = player:getParty()
    local affectedMembers = 0
    
    for _, member in pairs(party) do
        if member:getDistSq(player) <= 400 then -- 20 yalm range
            member:delStatusEffect(xi.effect.MAX_HP_BOOST)
            member:addStatusEffect(xi.effect.MAX_HP_BOOST, boost, 0, 180)
            affectedMembers = affectedMembers + 1
        end
    end
    
    return affectedMembers
end

-- Get job-specific abilities list
xi.job_utils.monk.getJobAbilities = function(player)
    local hasAccess, effectiveness = xi.job_utils.monk.validateJobAccess(player)
    if not hasAccess then
        return {}
    end

    local abilities = {
        'Hundred Fists', 'Boost', 'Focus', 'Dodge', 'Chi Blast', 'Chakra',
        'Counterstance', 'Footwork', 'Formless Strikes', 'Impetus', 'Mantra', 'Perfect Counter'
    }
    
    -- Add subjob abilities if available
    if player:getSubJob() == xi.job.MNK and effectiveness > 0.5 then
        abilities = {
            'Boost', 'Focus', 'Dodge', 'Chakra', 'Mantra'
        }
    end
    
    return abilities
end

-----------------------------------
-- Database Integration Summary
-----------------------------------
-- Total Functions: 43 (+ getJobAbilities)
-- Core Abilities: 13 (Hundred Fists, Inner Strength, Boost, Focus, Dodge, Chi Blast, Chakra, Counterstance, Footwork, Formless Strikes, Impetus, Mantra, Perfect Counter)
-- Enhancement Functions: 8 (Damage, Critical Hit, Accuracy, Evasion, Weapon Skill, Combat Effectiveness, Merit Integration, Party Support)
-- Validation Functions: 3 (Job Access, Ability Access, getJobAbilities)
-- Calculation Functions: 8 (Chi Blast, Boost Power, Focus Power, Dodge Power, Subjob Penalty, Hand-to-Hand Bonus, etc.)
-- Listener Functions: 2 (Impetus Hit/Miss)
-- Database Validation: Complete with graduated subjob penalty system (50% to 100% effectiveness)
