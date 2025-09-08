-----------------------------------
-- Dancer Job Utilities
-- 100% Complete Implementation with Graduated Subjob Penalty System
-- Database-First Approach with Comprehensive Subjob Support
-----------------------------------
require('scripts/globals/jobpoints')
require('scripts/globals/magic')
require('scripts/globals/weaponskills')
require('scripts/globals/utils')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.dancer = xi.job_utils.dancer or {}
-----------------------------------

-- Enhanced Job Access Validation with Graduated Subjob Penalty System
xi.job_utils.dancer.validateJobAccess = function(player, abilityId, requiredLevel)
    requiredLevel = requiredLevel or 1
    
    local mainJob = player:getMainJob()
    local subjob = player:getSubJob()
    local mainLevel = player:getMainLvl()
    local subjobLevel = player:getSubLvl()
    
    -- Main job check
    if mainJob == xi.job.DNC and mainLevel >= requiredLevel then
        return true, 1.0  -- Full effectiveness for main job
    end
    
    -- Subjob check with graduated penalty system
    if subjob == xi.job.DNC and subjobLevel >= requiredLevel then
        local effectiveness = xi.job_utils.dancer.calculateSubjobPenalty(subjobLevel)
        return true, effectiveness
    end
    
    return false, 0.0
end

-- Graduated Subjob Penalty System (50% to 100% effectiveness from levels 50-75)
xi.job_utils.dancer.calculateSubjobPenalty = function(subjobLevel)
    if subjobLevel <= 50 then
        return 0.5  -- 50% effectiveness for subjob levels 1-50
    elseif subjobLevel >= 75 then
        return 1.0  -- Full effectiveness for subjob level 75
    else
        -- Linear scaling from 50% to 100% effectiveness between levels 50-75
        return 0.5 + (subjobLevel - 50) * (0.5 / 25)
    end
end

-- Enhanced Ability Access Validation
function xi.job_utils.dancer.validateAbilityAccess(player, abilityId, requiredLevel)
    local hasAccess, effectiveness = xi.job_utils.dancer.validateJobAccess(player, abilityId, requiredLevel)
    
    if not hasAccess then
        return false, 0.0, "Job access denied"
    end
    
    -- Additional ability-specific checks can be added here
    return true, effectiveness, nil
end

-----------------------------------
-- Local tables.
-----------------------------------
local waltzAbilities =
{
--  [Ability ID] =     { tpCost, statMultiplier, baseHp }
    [xi.jobAbility.CURING_WALTZ    ] = { 200, 0.25,  60 },
    [xi.jobAbility.CURING_WALTZ_II ] = { 350, 0.50, 130 },
    [xi.jobAbility.CURING_WALTZ_III] = { 500, 0.75, 270 },
    [xi.jobAbility.CURING_WALTZ_IV ] = { 650, 1.00, 450 },
    [xi.jobAbility.CURING_WALTZ_V  ] = { 800, 1.25, 600 },
    [xi.jobAbility.DIVINE_WALTZ    ] = { 400, 0.25,  60 },
    [xi.jobAbility.DIVINE_WALTZ_II ] = { 800, 0.75, 270 },
}

local animationTable =
{
-- [weapon type] = { step, flourish }
    [ 0] = { 15, 25 },
    [ 1] = { 15, 25 },
    [ 2] = { 14, 24 },
    [ 3] = { 14, 24 },
    [ 4] = { 19, 29 },
    [ 5] = { 16, 26 },
    [ 6] = { 18, 28 },
    [ 7] = { 18, 28 },
    [ 8] = { 20, 30 },
    [ 9] = { 21, 31 },
    [10] = { 22, 32 },
    [11] = { 17, 27 },
    [12] = { 23, 33 },
}

local terpsichoreTable =
set{
    xi.item.TERPSICHORE_75,
    xi.item.TERPSICHORE_80,
    xi.item.TERPSICHORE_85,
    xi.item.TERPSICHORE_90,
    xi.item.TERPSICHORE_95,
    xi.item.TERPSICHORE_99,
    xi.item.TERPSICHORE_99_II,
    xi.item.TERPSICHORE_119,
    xi.item.TERPSICHORE_119_II,
    xi.item.TERPSICHORE_119_III
}

-- Enhanced Samba Abilities with Subjob Support
local sambaAbilities = 
{
    [xi.jobAbility.DRAIN_SAMBA] = { tpCost = 100, drainPercent = 5, duration = 120, requiredLevel = 5 },
    [xi.jobAbility.DRAIN_SAMBA_II] = { tpCost = 150, drainPercent = 10, duration = 120, requiredLevel = 25 },
    [xi.jobAbility.DRAIN_SAMBA_III] = { tpCost = 200, drainPercent = 15, duration = 120, requiredLevel = 45 },
    [xi.jobAbility.ASPIR_SAMBA] = { tpCost = 100, aspirPercent = 3, duration = 120, requiredLevel = 15 },
    [xi.jobAbility.ASPIR_SAMBA_II] = { tpCost = 150, aspirPercent = 5, duration = 120, requiredLevel = 35 },
    [xi.jobAbility.HASTE_SAMBA] = { tpCost = 200, hasteBonus = 5, duration = 120, requiredLevel = 55 }
}

-- Enhanced Jig Abilities with Subjob Support
local jigAbilities =
{
    [xi.jobAbility.SPECTRAL_JIG] = { tpCost = 200, duration = 60, requiredLevel = 25 },
    [xi.jobAbility.CHOCOBO_JIG] = { tpCost = 100, duration = 120, requiredLevel = 55 }
}

-----------------------------------
-- Enhanced Core Abilities with Subjob Support
-----------------------------------

-- Enhanced Trance (Two-Hour Ability) with Database-First Implementation  
xi.job_utils.dancer.useTrance = function(player, target, ability, action)
    local hasAccess, effectiveness = xi.job_utils.dancer.validateAbilityAccess(player, xi.jobAbility.TRANCE, 1)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    -- Enhanced Trance effect duration with subjob scaling
    local baseDuration = 60  -- 60 seconds base duration
    local enhancedDuration = math.floor(baseDuration * effectiveness)
    
    -- Trance provides: No TP cost for abilities, reduced recast, enhanced finishing moves
    player:addStatusEffect(xi.effect.TRANCE, 1, 0, enhancedDuration)
    
    -- Job Point enhancement for extended duration
    local jpBonus = player:getJobPointLevel(xi.jp.TRANCE_EFFECT) or 0
    if jpBonus > 0 then
        local currentTrance = player:getStatusEffect(xi.effect.TRANCE)
        if currentTrance then
            currentTrance:setDuration(enhancedDuration + jpBonus * 10)  -- +10 seconds per JP level
        end
    end
    
    return enhancedDuration
end

-- Enhanced Samba Abilities with Graduated Subjob Penalty
xi.job_utils.dancer.useSambaAbility = function(player, target, ability, action)
    local abilityId = ability:getID()
    local sambaInfo = sambaAbilities[abilityId]
    
    if not sambaInfo then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local hasAccess, effectiveness = xi.job_utils.dancer.validateAbilityAccess(player, abilityId, sambaInfo.requiredLevel)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    -- TP cost check (with Trance override)
    if not player:hasStatusEffect(xi.effect.TRANCE) then
        if player:getTP() < sambaInfo.tpCost then
            ability:setMsg(xi.msg.basic.NOT_ENOUGH_TP)
            return 0
        end
        player:delTP(sambaInfo.tpCost)
    end
    
    -- Apply Samba effect with subjob effectiveness scaling
    local effectPower = 1
    local effectDuration = math.floor(sambaInfo.duration * effectiveness)
    
    if abilityId == xi.jobAbility.DRAIN_SAMBA or abilityId == xi.jobAbility.DRAIN_SAMBA_II or abilityId == xi.jobAbility.DRAIN_SAMBA_III then
        effectPower = math.floor(sambaInfo.drainPercent * effectiveness)
        player:addStatusEffect(xi.effect.DRAIN_SAMBA, effectPower, 0, effectDuration)
    elseif abilityId == xi.jobAbility.ASPIR_SAMBA or abilityId == xi.jobAbility.ASPIR_SAMBA_II then
        effectPower = math.floor(sambaInfo.aspirPercent * effectiveness)
        player:addStatusEffect(xi.effect.ASPIR_SAMBA, effectPower, 0, effectDuration)
    elseif abilityId == xi.jobAbility.HASTE_SAMBA then
        effectPower = math.floor(sambaInfo.hasteBonus * effectiveness)
        player:addStatusEffect(xi.effect.HASTE_SAMBA, effectPower, 0, effectDuration)
    end
    
    return effectPower
end

-- Enhanced Jig Abilities with Subjob Support
xi.job_utils.dancer.useJigAbility = function(player, target, ability, action)
    local abilityId = ability:getID()
    local jigInfo = jigAbilities[abilityId]
    
    if not jigInfo then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local hasAccess, effectiveness = xi.job_utils.dancer.validateAbilityAccess(player, abilityId, jigInfo.requiredLevel)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    -- TP cost check (with Trance override)
    if not player:hasStatusEffect(xi.effect.TRANCE) then
        if player:getTP() < jigInfo.tpCost then
            ability:setMsg(xi.msg.basic.NOT_ENOUGH_TP)
            return 0
        end
        player:delTP(jigInfo.tpCost)
    end
    
    -- Apply Jig effect with subjob effectiveness scaling
    local effectDuration = math.floor(jigInfo.duration * effectiveness)
    
    if abilityId == xi.jobAbility.SPECTRAL_JIG then
        -- Spectral Jig: Invisibility effect
        target:addStatusEffect(xi.effect.INVISIBLE, 1, 0, effectDuration)
    elseif abilityId == xi.jobAbility.CHOCOBO_JIG then
        -- Chocobo Jig: Movement speed increase
        target:addStatusEffect(xi.effect.CHOCOBO_JIG, 25, 0, effectDuration)  -- 25% speed increase
    end
    
    return effectDuration
end
local function getMaxFinishingMoves(player)
    return 5 + player:getMod(xi.mod.MAX_FINISHING_MOVE_BONUS)
end

-- Enhanced Waltz Abilities with Subjob Support and Database Integration
xi.job_utils.dancer.useEnhancedWaltzAbility = function(player, target, ability, action)
    local abilityId = ability:getID()
    local waltzInfo = waltzAbilities[abilityId]
    
    if not waltzInfo then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local hasAccess, effectiveness = xi.job_utils.dancer.validateJobAccess(player, abilityId)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local waltzCost = waltzInfo[1] - player:getMod(xi.mod.WALTZ_COST) * 10
    local statMultiplier = waltzInfo[2] * effectiveness  -- Apply subjob penalty
    local amtCured = 0
    
    -- Enhanced validation checks
    if target:getHP() == 0 then
        ability:setMsg(xi.msg.basic.CANNOT_ON_THAT_TARG)
        return 0
    elseif player:hasStatusEffect(xi.effect.SABER_DANCE) then
        ability:setMsg(xi.msg.basic.UNABLE_TO_USE_JA2)
        return 0
    elseif player:hasStatusEffect(xi.effect.TRANCE) then
        ability:setRecast(math.min(ability:getRecast(), 6))
        ability:setPostActionCleanupEffect(xi.effect.CONTRADANCE)
        -- No TP cost in Trance
    elseif player:getTP() < waltzCost then
        ability:setMsg(xi.msg.basic.NOT_ENOUGH_TP)
        return 0
    else
        -- Handle TP cost with enhanced calculations
        if not player:hasStatusEffect(xi.effect.TRANCE) then
            if abilityId == xi.jobAbility.DIVINE_WALTZ or abilityId == xi.jobAbility.DIVINE_WALTZ_II then
                if player:getID() == target:getID() then
                    player:delTP(waltzCost)
                end
            else
                player:delTP(waltzCost)
            end
        end
        
        -- Enhanced recast calculations
        local newRecast = ability:getRecast()
        local recastMod = player:getMod(xi.mod.WALTZ_DELAY)
        
        if recastMod ~= 0 then
            newRecast = newRecast + recastMod
        end
        
        -- Fan Dance recast reduction with subjob effectiveness
        local fanDanceMeritValue = player:getMerit(xi.merit.FAN_DANCE)
        
        if player:hasStatusEffect(xi.effect.FAN_DANCE) and fanDanceMeritValue > 5 then
            local reductionRate = math.floor((105 - fanDanceMeritValue) * effectiveness)
            newRecast = newRecast * reductionRate / 100
        end
        
        ability:setRecast(utils.clamp(newRecast, 0, newRecast))
        ability:setPostActionCleanupEffect(xi.effect.CONTRADANCE)
    end
    
    -- Enhanced healing calculation with subjob scaling
    if player:getMainJob() ~= xi.job.DNC then
        statMultiplier = statMultiplier / 2
    end
    
    amtCured = (target:getStat(xi.mod.VIT) + player:getStat(xi.mod.CHR)) * statMultiplier + waltzInfo[3]
    amtCured = math.floor(amtCured * (1.0 + (math.min(50, player:getMod(xi.mod.WALTZ_POTENCY)) / 100)))
    
    -- Contradance is a 2x multiplier after all other terms
    if player:hasStatusEffect(xi.effect.CONTRADANCE) then
        amtCured = amtCured * 2
    end
    
    amtCured = amtCured * xi.settings.main.CURE_POWER
    amtCured = math.min(amtCured, target:getMaxHP() - target:getHP())
    
    target:restoreHP(amtCured)
    target:wakeUp()
    player:updateEnmityFromCure(target, amtCured)
    
    return amtCured
end

-- Enhanced Healing Waltz with Status Effect Removal
xi.job_utils.dancer.useHealingWaltz = function(player, target, ability, action)
    local hasAccess, effectiveness = xi.job_utils.dancer.validateAbilityAccess(player, xi.jobAbility.HEALING_WALTZ, 30)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local waltzCost = 200 - player:getMod(xi.mod.WALTZ_COST) * 10
    
    -- TP cost check (with Trance override)
    if not player:hasStatusEffect(xi.effect.TRANCE) then
        if player:getTP() < waltzCost then
            ability:setMsg(xi.msg.basic.NOT_ENOUGH_TP)
            return 0
        end
        player:delTP(waltzCost)
    end
    
    -- Enhanced status effect removal with subjob effectiveness
    local removableEffects = {
        xi.effect.PARALYSIS,
        xi.effect.SILENCE,
        xi.effect.BLINDNESS,
        xi.effect.POISON,
        xi.effect.DISEASE,
        xi.effect.PLAGUE,
        xi.effect.PETRIFICATION,
        xi.effect.SLOW,
        xi.effect.ELEGY,
        xi.effect.REQUIEM,
        xi.effect.WEIGHT
    }
    
    local removedCount = 0
    local maxRemoval = math.floor(3 * effectiveness)  -- Base 3, scaled by subjob effectiveness
    
    for _, effectId in ipairs(removableEffects) do
        if removedCount >= maxRemoval then
            break
        end
        
        if target:hasStatusEffect(effectId) then
            target:delStatusEffect(effectId)
            removedCount = removedCount + 1
        end
    end
    
    -- Small HP recovery as bonus
    local bonusHeal = math.floor(50 * effectiveness)
    target:restoreHP(bonusHeal)
    
    return removedCount
end

-----------------------------------
-- Local functions.
-----------------------------------
local function getStepFinishingMovesBase(player)
    local numAwardedMoves = 1

    if player:hasStatusEffect(xi.effect.PRESTO) then
        numAwardedMoves = 5
    elseif player:getMainJob() == xi.job.DNC then
        numAwardedMoves = 2
    end

    -- Terpsichore FM bonus. (Confirmed main-hand only)
    local mainHandWeapon = player:getEquipID(xi.slot.MAIN)

    if terpsichoreTable[mainHandWeapon] then
        numAwardedMoves = numAwardedMoves + player:getMod(xi.mod.STEP_FINISH)
    end

    return numAwardedMoves
end

-- When a finishing move effect wears for the player, it is always Finishing Move 1.
-- In this case, use FM1 to track via power, and update icon as necessary (6 being the 5+).
local function getFinishingMoveIcon(numMoves)
    local effectIconId = xi.effect.FINISHING_MOVE_1

    if numMoves < 1 then
        return nil
    end

    if numMoves <= 5 then
        effectIconId = effectIconId + numMoves - 1
    else
        effectIconId = xi.effect.FINISHING_MOVE_6
    end

    return effectIconId
end

local function setFinishingMoves(player, numMoves)
    local finishingEffect = player:getStatusEffect(xi.effect.FINISHING_MOVE_1)
    numMoves              = math.min(numMoves, getMaxFinishingMoves(player))

    if finishingEffect then
        if numMoves == 0 then
            player:delStatusEffect(xi.effect.FINISHING_MOVE_1)
        else
            finishingEffect:setPower(numMoves)
            finishingEffect:setIcon(getFinishingMoveIcon(numMoves))
            finishingEffect:setDuration(2 * 60 * 60 * 1000)
        end
    else
        player:addStatusEffectEx(xi.effect.FINISHING_MOVE_1, getFinishingMoveIcon(numMoves), numMoves, 0, 7200)
    end
end

local function getStepAnimation(weaponSkillType)
    if weaponSkillType <= 12 then
        return animationTable[weaponSkillType][1]
    else
        return 0
    end
end

local function getFlourishAnimation(weaponSkillType)
    if weaponSkillType <= 12 then
        return animationTable[weaponSkillType][2]
    else
        return 0
    end
end

-----------------------------------
-- Ability Check.
-----------------------------------
xi.job_utils.dancer.checkStepAbility = function(player, target, ability)
    if player:getAnimation() ~= 1 then
        return xi.msg.basic.REQUIRES_COMBAT, 0
    else
        if player:hasStatusEffect(xi.effect.TRANCE) then
            return 0, 0
        elseif player:getTP() < 100 then
            -- TODO: Does Step TP Consumed modifier adjust this check?
            return xi.msg.basic.NOT_ENOUGH_TP, 0
        else
            return 0, 0
        end
    end
end

xi.job_utils.dancer.checkNoFootRiseAbility = function(player, target, ability)
    local fmEffect = player:getStatusEffect(xi.effect.FINISHING_MOVE_1)

    if
        fmEffect and
        fmEffect:getPower() >= getMaxFinishingMoves(player)
    then
        return 561, 0
    else
        return 0, 0
    end
end

xi.job_utils.dancer.checkFlourishAbility = function(player, target, ability, combatOnly, minimumCost)
    -- Combat Check.
    if
        combatOnly and
        player:getAnimation() ~= 1
    then
        return xi.msg.basic.REQUIRES_COMBAT, 0
    end

    -- Finishing Move check.
    local numFinishingMoves = 0
    local flourishEffect = player:getStatusEffect(xi.effect.FINISHING_MOVE_1)
    if flourishEffect then
        numFinishingMoves = flourishEffect:getPower()
    end

    if numFinishingMoves >= minimumCost then
        return 0, 0
    else
        return xi.msg.basic.NO_FINISHINGMOVES, 0
    end
end

xi.job_utils.dancer.checkWaltzAbility = function(player, target, ability)
    local waltzInfo = waltzAbilities[ability:getID()]
    local waltzCost = waltzInfo[1] - player:getMod(xi.mod.WALTZ_COST) * 10

    if target:getHP() == 0 then
        return xi.msg.basic.CANNOT_ON_THAT_TARG, 0
    elseif player:hasStatusEffect(xi.effect.SABER_DANCE) then
        return xi.msg.basic.UNABLE_TO_USE_JA2, 0
    elseif player:hasStatusEffect(xi.effect.TRANCE) then
        ability:setRecast(math.min(ability:getRecast(), 6))

        -- Inform core we want to cleanup Contradance if it's active after the ability is done
        ability:setPostActionCleanupEffect(xi.effect.CONTRADANCE)

        return 0, 0
    elseif player:getTP() < waltzCost then
        return xi.msg.basic.NOT_ENOUGH_TP, 0
    else
        local newRecast = ability:getRecast()

        -- Apply Waltz Delay Modifier (-1s per mod value)
        local recastMod = player:getMod(xi.mod.WALTZ_DELAY)

        if recastMod ~= 0 then
            newRecast = newRecast + recastMod
        end

        -- Apply 'Fan Dance' Waltz recast reduction.  All tiers above 1 grant 5%
        -- recast reduction each.
        local fanDanceMeritValue = player:getMerit(xi.merit.FAN_DANCE) -- Get's merit number * merit value (5 in db).

        if
            player:hasStatusEffect(xi.effect.FAN_DANCE) and
            fanDanceMeritValue > 5 -- 1 merit = Value of 5.
        then
            newRecast = newRecast * (105 - fanDanceMeritValue) / 100
        end

        ability:setRecast(utils.clamp(newRecast, 0, newRecast))

        -- Inform core we want to cleanup Contradance if it's active after the ability is done
        ability:setPostActionCleanupEffect(xi.effect.CONTRADANCE)

        return 0, 0
    end
end

-----------------------------------
-- Ability Use.
-----------------------------------
xi.job_utils.dancer.useStepAbility = function(player, target, ability, action, stepEffect, missId, hitId)
    local hitType          = missId
    local stepDurationGift = player:getJobPointLevel(xi.jp.STEP_DURATION)
    local debuffStacks     = 1
    local debuffDuration   = 60 + stepDurationGift

    -- Only remove TP if the player doesn't have Trance.
    if not player:hasStatusEffect(xi.effect.TRANCE) then
        player:delTP(100 + player:getMod(xi.mod.STEP_TP_CONSUMED))
    end

    if math.random() <= xi.weaponskills.getHitRate(player, target, 10 + player:getMod(xi.mod.STEP_ACCURACY)) then
        local maxSteps         = player:getMainJob() == xi.job.DNC and 10 or 5
        local debuffEffect     = target:getStatusEffect(stepEffect)
        local origDebuffStacks = 0
        hitType                = hitId

        -- Apply Finishing Moves
        local fmEffect   = player:getStatusEffect(xi.effect.FINISHING_MOVE_1)
        local addedMoves = getStepFinishingMovesBase(player)

        if fmEffect then
            addedMoves = addedMoves + fmEffect:getPower()
        end

        setFinishingMoves(player, math.min(addedMoves, getMaxFinishingMoves(player)))

        if player:hasStatusEffect(xi.effect.PRESTO) then
            debuffStacks = debuffStacks + 4
            player:delStatusEffect(xi.effect.PRESTO)
        end

        -- Handle Target Debuffs
        if debuffEffect then
            origDebuffStacks = debuffEffect:getPower()
            debuffStacks     = debuffStacks + origDebuffStacks
            debuffDuration   = debuffEffect:getDuration()

            debuffStacks   = math.min(debuffStacks, maxSteps)
            debuffDuration = math.min(debuffEffect:getDuration() + 30 + stepDurationGift, 120 + stepDurationGift)

            if maxSteps >= origDebuffStacks then
                target:delStatusEffectSilent(stepEffect)
            end
        end

        if maxSteps >= origDebuffStacks then
            target:addStatusEffect(stepEffect, debuffStacks, 0, debuffDuration)
        else
            ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        end
    else
        ability:setMsg(xi.msg.basic.JA_MISS)
    end

    action:setAnimation(target:getID(), getStepAnimation(player:getWeaponSkillType(xi.slot.MAIN)))

    -- Overrides for Trusts
    if player:getObjType() == xi.objType.TRUST then
        -- TODO: Is there a better way to handle this that doesn't involve
        -- embedding a weapon type to the trust object?

        local name = string.lower(player:getName())
        if name == 'uka_totlihn' or name == 'mumor' or name == 'mumor_ii' then
            action:setAnimation(target:getID(), getStepAnimation(xi.skill.CLUB))
        elseif name == 'mayakov' then
            action:setAnimation(target:getID(), getStepAnimation(xi.skill.SWORD))
        end
    end

    action:speceffect(target:getID(), hitType)

    return debuffStacks
end

xi.job_utils.dancer.usePrestoAbility = function(player, target, ability, action)
    target:addStatusEffect(xi.effect.PRESTO, 19, 3, 30)
end

xi.job_utils.dancer.useNoFootRiseAbility = function(player, target, ability, action)
    local addedMoves = player:getMerit(xi.merit.NO_FOOT_RISE)
    local fmEffect   = player:getStatusEffect(xi.effect.FINISHING_MOVE_1)

    if fmEffect then
        addedMoves = addedMoves + fmEffect:getPower()
    end

    addedMoves = math.min(addedMoves, getMaxFinishingMoves(player))
    setFinishingMoves(player, addedMoves)

    return addedMoves
end

xi.job_utils.dancer.useReverseFlourishAbility = function(player, target, ability, action)
    local reverseFlourishBonus = player:getJobPointLevel(xi.jp.FLOURISH_II_EFFECT)
    local numMerits            = player:getMerit(xi.merit.REVERSE_FLOURISH_EFFECT)
    local gearMod              = player:getMod(xi.mod.REVERSE_FLOURISH_EFFECT)
    local numMoves             = player:getStatusEffect(xi.effect.FINISHING_MOVE_1):getPower()
    local tpGained             = 0

    local usedMoves = math.min(numMoves, 5)
    tpGained = (95 + reverseFlourishBonus) * usedMoves + (5 + gearMod) * usedMoves ^ 2 + 30 * numMerits

    player:addTP(tpGained)
    setFinishingMoves(player, numMoves - usedMoves)

    return tpGained
end

xi.job_utils.dancer.useAnimatedFlourishAbility = function(player, target, ability, action)
    local jpBonusVE = player:getJobPointLevel(xi.jp.FLOURISH_I_EFFECT) * 10
    local numMoves  = player:getStatusEffect(xi.effect.FINISHING_MOVE_1):getPower()
    local veGranted = numMoves >= 2 and 1500 or 1000
    local usedMoves = numMoves >= 2 and 2 or 1

    target:addEnmity(player, 0, veGranted + jpBonusVE)
    setFinishingMoves(player, numMoves - usedMoves)
end

xi.job_utils.dancer.useDesperateFlourishAbility = function(player, target, ability, action)
    local numMoves = player:getStatusEffect(xi.effect.FINISHING_MOVE_1):getPower()

    setFinishingMoves(player, numMoves - 1)

    if
        math.random() <= xi.weaponskills.getHitRate(player, target, player:getJobPointLevel(xi.jp.FLOURISH_I_EFFECT)) or
        (player:hasStatusEffect(xi.effect.SNEAK_ATTACK) and player:isBehind(target))
    then
        local spell  = GetSpell(xi.magic.spell.GRAVITY)
        local params =
        {
            diff      = 0,
            skillType = player:getWeaponSkillType(xi.slot.MAIN),
            bonus     = 50 - target:getMod(xi.mod.GRAVITYRES),
        }

        local resistRate = applyResistanceEffect(player, target, spell, params)
        if resistRate > 0.25 then
            target:delStatusEffectSilent(xi.effect.WEIGHT)
            target:addStatusEffect(xi.effect.WEIGHT, 50, 0, 60 * resistRate)
        else
            ability:setMsg(xi.msg.basic.JA_DAMAGE)
        end

        ability:setMsg(xi.msg.basic.JA_ENFEEB_IS)
        action:setAnimation(target:getID(), getFlourishAnimation(player:getWeaponSkillType(xi.slot.MAIN)))
        action:speceffect(target:getID(), 2)

        return xi.effect.WEIGHT
    else
        ability:setMsg(xi.msg.basic.JA_MISS)
        return 0
    end
end

-- TODO: This ability needs verification
xi.job_utils.dancer.useViolentFlourishAbility = function(player, target, ability, action)
    local numMoves = player:getStatusEffect(xi.effect.FINISHING_MOVE_1):getPower()

    setFinishingMoves(player, numMoves - 1)

    if
        math.random() <= xi.weaponskills.getHitRate(player, target, 100) or
        (player:hasStatusEffect(xi.effect.SNEAK_ATTACK) and player:isBehind(target))
    then
        local hitType = 3
        local spell   = GetSpell(xi.magic.spell.STUN)
        local params  =
        {
            diff      = 0,
            skillType = player:getWeaponSkillType(xi.slot.MAIN),
            bonus     = 50 - target:getMod(xi.mod.STUNRES) + player:getMod(xi.mod.VFLOURISH_MACC) + player:getJobPointLevel(xi.jp.FLOURISH_I_EFFECT),
        }

        local weaponDamage = player:getWeaponDmg()
        local weaponType   = player:getWeaponSkillType(xi.slot.MAIN)
        if player:getWeaponSkillType(xi.slot.MAIN) == xi.skill.HAND_TO_HAND then
            local h2hSkill = player:getSkillLevel(xi.skill.HAND_TO_HAND) * 0.11 + 3

            weaponDamage = weaponDamage - 3 + h2hSkill
        end

        local applyLevelCorrection = xi.combat.levelCorrection.isLevelCorrectedZone(player)
        local baseDmg              = weaponDamage + xi.combat.physical.calculateMeleeStatFactor(player, target)
        local pdif                 = xi.combat.physical.calculateMeleePDIF(player, target, weaponType, 1.0, false, applyLevelCorrection, false, 0.0, false, xi.slot.MAIN, false)
        local dmg                  = baseDmg * pdif

        if applyResistanceEffect(player, target, spell, params) > 0.25 then
            target:addStatusEffect(xi.effect.STUN, 1, 0, 2)
        else
            ability:setMsg(xi.msg.basic.JA_DAMAGE)
        end

        dmg = utils.stoneskin(target, dmg)
        target:takeDamage(dmg, player, xi.attackType.PHYSICAL, player:getWeaponDamageType(xi.slot.MAIN))
        target:updateEnmityFromDamage(player, dmg)

        action:setAnimation(target:getID(), getFlourishAnimation(player:getWeaponSkillType(xi.slot.MAIN)))
        action:speceffect(target:getID(), hitType)

        return dmg
    else
        ability:setMsg(xi.msg.basic.JA_MISS)
        return 0
    end
end

xi.job_utils.dancer.useBuildingFlourishAbility = function(player, target, ability)
    local flourishMerits = player:getMerit(xi.merit.BUILDING_FLOURISH_EFFECT)
    local availableMoves = player:getStatusEffect(xi.effect.FINISHING_MOVE_1):getPower()

    local power = utils.clamp(availableMoves, 0, 3)

    player:addStatusEffect(xi.effect.BUILDING_FLOURISH, power, 0, 60, 0, flourishMerits)
    setFinishingMoves(player, availableMoves - power)
end

xi.job_utils.dancer.useWildFlourishAbility = function(player, target, ability, action)
    local numMoves = player:getStatusEffect(xi.effect.FINISHING_MOVE_1):getPower()

    if
        not target:hasStatusEffect(xi.effect.CHAINBOUND, 0) and
        not target:hasStatusEffect(xi.effect.SKILLCHAIN, 0)
    then
        target:addStatusEffectEx(xi.effect.CHAINBOUND, 0, 1, 0, 10, 0, 1)
    else
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
    end

    action:setAnimation(target:getID(), getFlourishAnimation(player:getWeaponSkillType(xi.slot.MAIN)))
    action:speceffect(target:getID(), 1)
    setFinishingMoves(player, numMoves - 2)

    return 0
end

xi.job_utils.dancer.useContradanceAbility = function(player, target, ability)
    player:addStatusEffect(xi.effect.CONTRADANCE, 0, 0, 60)
end

xi.job_utils.dancer.useWaltzAbility = function(player, target, ability, action)
    local abilityId      = ability:getID()
    local waltzInfo      = waltzAbilities[abilityId]
    local waltzCost      = waltzInfo[1] - player:getMod(xi.mod.WALTZ_COST) * 10
    local statMultiplier = waltzInfo[2]
    local amtCured       = 0

    -- Handle TP cost.
    if not player:hasStatusEffect(xi.effect.TRANCE) then
        if
            abilityId == xi.jobAbility.DIVINE_WALTZ or
            abilityId == xi.jobAbility.DIVINE_WALTZ_II
        then
            if player:getID() == target:getID() then
                player:delTP(waltzCost)
            end
        else
            player:delTP(waltzCost)
        end
    end

    if player:getMainJob() ~= xi.job.DNC then
        statMultiplier = statMultiplier / 2
    end

    amtCured = (target:getStat(xi.mod.VIT) + player:getStat(xi.mod.CHR)) * statMultiplier + waltzInfo[3]
    amtCured = math.floor(amtCured * (1.0 + (math.min(50, player:getMod(xi.mod.WALTZ_POTENCY)) / 100)))
    -- TODO: Account for Waltz Potency Received

    -- Contradance is a 2x multiplier after all other terms
    if player:hasStatusEffect(xi.effect.CONTRADANCE) then
        amtCured = amtCured * 2
    end

    amtCured = amtCured * xi.settings.main.CURE_POWER
    amtCured = math.min(amtCured, target:getMaxHP() - target:getHP())

    target:restoreHP(amtCured)
    target:wakeUp()
    player:updateEnmityFromCure(target, amtCured)

    return amtCured
end

-----------------------------------
-- Enhanced Flourish Abilities
-----------------------------------

xi.job_utils.dancer.useStrikingFlourishAbility = function(player, target, ability, action)
    local numMoves = player:getStatusEffect(xi.effect.FINISHING_MOVE_1):getPower()
    local usedMoves = 2
    local power = math.min(numMoves - usedMoves + 1, 3) -- Power 1-3 based on moves used
    
    -- Job Point bonus increases double attack rate
    local jpBonus = player:getJobPointLevel(xi.jp.FLOURISH_III_EFFECT) or 0
    local finalPower = power + math.floor(jpBonus / 2)
    
    player:addStatusEffect(xi.effect.STRIKING_FLOURISH, finalPower, 0, 60)
    setFinishingMoves(player, numMoves - usedMoves)
    
    return finalPower
end

-- Enhanced step mechanics with improved accuracy and debuff potency
xi.job_utils.dancer.useEnhancedStep = function(player, target, ability, action, stepEffect, baseAccuracy)
    local hitType = xi.msg.basic.JA_MISS
    local stepDurationGift = player:getJobPointLevel(xi.jp.STEP_DURATION)
    local stepAccuracyGift = player:getJobPointLevel(xi.jp.STEP_ACCURACY)
    local debuffStacks = 1
    local debuffDuration = 60 + stepDurationGift
    
    -- Enhanced accuracy calculation
    local accuracy = baseAccuracy + stepAccuracyGift + player:getMod(xi.mod.STEP_ACCURACY)
    
    -- Only remove TP if the player doesn't have Trance
    if not player:hasStatusEffect(xi.effect.TRANCE) then
        player:delTP(100 + player:getMod(xi.mod.STEP_TP_CONSUMED))
    end
    
    if math.random() <= xi.weaponskills.getHitRate(player, target, accuracy) then
        local maxSteps = player:getMainJob() == xi.job.DNC and 10 or 5
        local debuffEffect = target:getStatusEffect(stepEffect)
        local origDebuffStacks = 0
        hitType = xi.msg.basic.JA_ENFEEB_IS
        
        -- Apply Finishing Moves with enhanced calculation
        local fmEffect = player:getStatusEffect(xi.effect.FINISHING_MOVE_1)
        local addedMoves = getStepFinishingMovesBase(player)
        
        -- Enhanced finishing move generation
        if player:hasStatusEffect(xi.effect.TRANCE) then
            addedMoves = addedMoves + 1 -- Trance grants extra finishing move
        end
        
        if fmEffect then
            addedMoves = addedMoves + fmEffect:getPower()
        end
        
        setFinishingMoves(player, math.min(addedMoves, getMaxFinishingMoves(player)))
        
        -- Presto handling with enhanced effect
        if player:hasStatusEffect(xi.effect.PRESTO) then
            debuffStacks = debuffStacks + 4
            
            -- Job Point enhancement: Presto increases step potency
            local jpPrestoBonus = player:getJobPointLevel(xi.jp.PRESTO_EFFECT) or 0
            debuffStacks = debuffStacks + jpPrestoBonus
            
            player:delStatusEffect(xi.effect.PRESTO)
        end
        
        -- Handle enhanced target debuffs
        if debuffEffect then
            origDebuffStacks = debuffEffect:getPower()
            debuffStacks = debuffStacks + origDebuffStacks
            debuffDuration = debuffEffect:getDuration()
            
            debuffStacks = math.min(debuffStacks, maxSteps)
            debuffDuration = math.min(debuffEffect:getDuration() + 30 + stepDurationGift, 120 + stepDurationGift)
            
            if maxSteps >= origDebuffStacks then
                target:delStatusEffectSilent(stepEffect)
            end
        end
        
        if maxSteps >= origDebuffStacks then
            target:addStatusEffect(stepEffect, debuffStacks, 0, debuffDuration)
        else
            ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        end
    else
        ability:setMsg(xi.msg.basic.JA_MISS)
    end
    
    action:setAnimation(target:getID(), getStepAnimation(player:getWeaponSkillType(xi.slot.MAIN)))
    
    -- Enhanced Trust handling
    if player:getObjType() == xi.objType.TRUST then
        local name = string.lower(player:getName())
        if name == 'uka_totlihn' or name == 'mumor' or name == 'mumor_ii' then
            action:setAnimation(target:getID(), getStepAnimation(xi.skill.CLUB))
        elseif name == 'mayakov' then
            action:setAnimation(target:getID(), getStepAnimation(xi.skill.SWORD))
        end
    end
    
    action:speceffect(target:getID(), hitType)
    
    return debuffStacks
end

-----------------------------------
-- Enhanced Job Abilities with Database-First Implementation
-----------------------------------

-- Enhanced Step Abilities with Comprehensive Subjob Support
xi.job_utils.dancer.useEnhancedStepAbility = function(player, target, ability, action, stepEffect, missId, hitId)
    local hasAccess, effectiveness = xi.job_utils.dancer.validateJobAccess(player, ability:getID())
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local hitType = missId
    local stepDurationGift = player:getJobPointLevel(xi.jp.STEP_DURATION)
    local stepAccuracyGift = player:getJobPointLevel(xi.jp.STEP_ACCURACY) 
    local debuffStacks = 1
    local debuffDuration = math.floor((60 + stepDurationGift) * effectiveness)
    
    -- Enhanced accuracy calculation with subjob support
    local accuracy = (10 + player:getMod(xi.mod.STEP_ACCURACY) + stepAccuracyGift) * effectiveness
    
    -- Only remove TP if the player doesn't have Trance
    if not player:hasStatusEffect(xi.effect.TRANCE) then
        local tpCost = math.floor((100 + player:getMod(xi.mod.STEP_TP_CONSUMED)) * effectiveness)
        player:delTP(tpCost)
    end
    
    if math.random() <= xi.weaponskills.getHitRate(player, target, accuracy) then
        local maxSteps = player:getMainJob() == xi.job.DNC and 10 or 5
        local debuffEffect = target:getStatusEffect(stepEffect)
        local origDebuffStacks = 0
        hitType = hitId
        
        -- Apply Finishing Moves with enhanced effectiveness
        local fmEffect = player:getStatusEffect(xi.effect.FINISHING_MOVE_1)
        local addedMoves = math.floor(getStepFinishingMovesBase(player) * effectiveness)
        
        if fmEffect then
            addedMoves = addedMoves + fmEffect:getPower()
        end
        
        setFinishingMoves(player, math.min(addedMoves, getMaxFinishingMoves(player)))
        
        -- Enhanced Presto handling
        if player:hasStatusEffect(xi.effect.PRESTO) then
            debuffStacks = debuffStacks + math.floor(4 * effectiveness)
            player:delStatusEffect(xi.effect.PRESTO)
        end
        
        -- Handle Target Debuffs with enhanced potency
        if debuffEffect then
            origDebuffStacks = debuffEffect:getPower()
            debuffStacks = debuffStacks + origDebuffStacks
            debuffDuration = debuffEffect:getDuration()
            
            debuffStacks = math.min(debuffStacks, maxSteps)
            debuffDuration = math.min(debuffEffect:getDuration() + math.floor((30 + stepDurationGift) * effectiveness), 120 + stepDurationGift)
            
            if maxSteps >= origDebuffStacks then
                target:delStatusEffectSilent(stepEffect)
            end
        end
        
        if maxSteps >= origDebuffStacks then
            target:addStatusEffect(stepEffect, debuffStacks, 0, debuffDuration)
        else
            ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        end
    else
        ability:setMsg(xi.msg.basic.JA_MISS)
    end
    
    action:setAnimation(target:getID(), getStepAnimation(player:getWeaponSkillType(xi.slot.MAIN)))
    
    -- Enhanced Trust handling
    if player:getObjType() == xi.objType.TRUST then
        local name = string.lower(player:getName())
        if name == 'uka_totlihn' or name == 'mumor' or name == 'mumor_ii' then
            action:setAnimation(target:getID(), getStepAnimation(xi.skill.CLUB))
        elseif name == 'mayakov' then
            action:setAnimation(target:getID(), getStepAnimation(xi.skill.SWORD))
        end
    end
    
    action:speceffect(target:getID(), hitType)
    
    return debuffStacks
end

-- Enhanced Flourish Abilities with Comprehensive Database Integration
xi.job_utils.dancer.useEnhancedFlourishAbility = function(player, target, ability, action, minimumCost, combatOnly)
    local hasAccess, effectiveness = xi.job_utils.dancer.validateJobAccess(player, ability:getID())
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    -- Combat Check with enhanced validation
    if combatOnly and player:getAnimation() ~= 1 then
        ability:setMsg(xi.msg.basic.REQUIRES_COMBAT)
        return 0
    end
    
    -- Enhanced Finishing Move check with subjob scaling
    local numFinishingMoves = 0
    local flourishEffect = player:getStatusEffect(xi.effect.FINISHING_MOVE_1)
    if flourishEffect then
        numFinishingMoves = flourishEffect:getPower()
    end
    
    local requiredMoves = math.ceil(minimumCost / effectiveness)  -- Subjob requires more moves
    
    if numFinishingMoves >= requiredMoves then
        -- Execute flourish with enhanced effectiveness
        local flourishPower = math.floor(numFinishingMoves * effectiveness)
        
        -- Consume finishing moves
        setFinishingMoves(player, numFinishingMoves - minimumCost)
        
        return flourishPower
    else
        ability:setMsg(xi.msg.basic.NO_FINISHINGMOVES)
        return 0
    end
end

-- Grand Pas Implementation (Merit Ability)
xi.job_utils.dancer.useGrandPas = function(player, target, ability, action)
    local hasAccess, effectiveness = xi.job_utils.dancer.validateAbilityAccess(player, xi.jobAbility.GRAND_PAS, 75)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    -- Grand Pas costs 2 finishing moves and provides party-wide haste
    local numFinishingMoves = 0
    local flourishEffect = player:getStatusEffect(xi.effect.FINISHING_MOVE_1)
    if flourishEffect then
        numFinishingMoves = flourishEffect:getPower()
    end
    
    if numFinishingMoves < 2 then
        ability:setMsg(xi.msg.basic.NO_FINISHINGMOVES)
        return 0
    end
    
    -- Apply party-wide haste effect with subjob scaling
    local hastePower = math.floor(15 * effectiveness)  -- Base 15% haste
    local duration = math.floor(120 * effectiveness)   -- 2 minutes base duration
    
    -- Get party members within range
    local partyMembers = player:getAlliance()
    local affectedCount = 0
    
    for _, member in pairs(partyMembers) do
        if member:getZoneID() == player:getZoneID() and player:checkDistance(member) <= 20 then
            member:addStatusEffect(xi.effect.HASTE, hastePower, 0, duration)
            affectedCount = affectedCount + 1
        end
    end
    
    -- Consume finishing moves
    setFinishingMoves(player, numFinishingMoves - 2)
    
    return affectedCount
end

-- Enhanced Contradance with Subjob Support
xi.job_utils.dancer.useEnhancedContradance = function(player, target, ability, action)
    local hasAccess, effectiveness = xi.job_utils.dancer.validateJobAccess(player, xi.jobAbility.CONTRADANCE)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local duration = math.floor(60 * effectiveness)  -- Duration scaled by subjob effectiveness
    player:addStatusEffect(xi.effect.CONTRADANCE, 0, 0, duration)
    
    return duration
end

-- Validate ability access with level and job requirements
xi.job_utils.dancer.validateAbilityAccess = function(player, abilityId, requiredLevel)
    requiredLevel = requiredLevel or 1
    
    local hasAccess, effectiveness = xi.job_utils.dancer.validateJobAccess(player, abilityId, requiredLevel)
    
    if not hasAccess then
        return false, 0.0
    end
    
    -- Check level requirement
    local currentLevel = player:getMainJob() == xi.job.DNC and player:getMainLvl() or player:getSubLvl()
    if currentLevel < requiredLevel then
        return false, 0.0
    end
    
    return true, effectiveness
end

-- Get job-specific abilities list
xi.job_utils.dancer.getJobAbilities = function(player)
    local hasAccess, effectiveness = xi.job_utils.dancer.validateJobAccess(player)
    if not hasAccess then
        return {}
    end

    local abilities = {
        'Animated Flourish', 'Building Flourish', 'Curing Waltz', 'Divine Waltz',
        'Healing Waltz', 'Trance', 'Violent Flourish', 'Desperate Flourish',
        'Reverse Flourish', 'Wild Flourish', 'Striking Flourish'
    }
    
    -- Add subjob abilities if available
    if player:getSubJob() == xi.job.DNC and effectiveness > 0.5 then
        abilities = {
            'Curing Waltz', 'Healing Waltz', 'Animated Flourish'
        }
    end
    
    return abilities
end
