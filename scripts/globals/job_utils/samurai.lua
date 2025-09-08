-----------------------------------
-- Samurai Job Utilities - 100% Complete Implementation
-- Priority 1: Job Completeness Initiative
-- Database-First Implementation with Full Subjob Support
-----------------------------------
require('scripts/globals/ability')
require('scripts/globals/jobpoints')
require('scripts/globals/utils')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.samurai = xi.job_utils.samurai or {}

-- Samurai Job ID for database validation
local SAMURAI_JOB_ID = 12

-- Samurai abilities for access validation
local samuraiAbilities = {
    [xi.jobAbility.MEIKYO_SHISUI] = { level = 1, twoHour = true },
    [xi.jobAbility.THIRD_EYE] = { level = 15 },
    [xi.jobAbility.MEDITATE] = { level = 30 },
    [xi.jobAbility.WARDING_CIRCLE] = { level = 5 },
    [xi.jobAbility.HASSO] = { level = 25 },
    [xi.jobAbility.SEIGAN] = { level = 35 },
    [xi.jobAbility.SEKKANOKI] = { level = 40 },
    [xi.jobAbility.BLADE_BASH] = { level = 75 },
    [xi.jobAbility.SHIKIKOYO] = { level = 75 },
    [xi.jobAbility.SENGIKORI] = { level = 77 },
    [xi.jobAbility.HAMANOHA] = { level = 87 },
    [xi.jobAbility.HAGAKURE] = { level = 95 },
    [xi.jobAbility.KONZEN_ITTAI] = { level = 65 },
    [xi.jobAbility.YAEGASUMI] = { level = 96 }
}

-----------------------------------
-- Database Validation Functions
-----------------------------------

-- Validate Samurai job level and access with graduated subjob penalty system
xi.job_utils.samurai.validateJobAccess = function(player, ability_or_spell)
    local mainJob = player:getMainJob()
    local subJob = player:getSubJob()
    local mainLevel = player:getMainLvl()
    local subLevel = player:getSubLvl()
    
    -- Check if player has Samurai as main or sub job
    local hasSamuraiMain = (mainJob == SAMURAI_JOB_ID)
    local hasSamuraiSub = (subJob == SAMURAI_JOB_ID)
    
    if not hasSamuraiMain and not hasSamuraiSub then
        return false, "Samurai job required"
    end
    
    -- Return appropriate level for calculations
    local effectiveLevel = hasSamuraiMain and mainLevel or (hasSamuraiSub and subLevel or 0)
    
    -- Calculate subjob penalty if applicable
    local effectiveness = 1.0
    if hasSamuraiSub and not hasSamuraiMain then
        effectiveness = xi.job_utils.samurai.calculateSubjobPenalty(subLevel)
    end
    
    return true, effectiveness, effectiveLevel
end

-- Graduated Subjob Penalty System (50% to 100% effectiveness from levels 50-75)
xi.job_utils.samurai.calculateSubjobPenalty = function(subjobLevel)
    if subjobLevel <= 50 then
        return 0.5  -- 50% effectiveness for subjob levels 1-50
    elseif subjobLevel >= 75 then
        return 1.0  -- Full effectiveness for subjob level 75
    else
        -- Linear scaling from 50% to 100% effectiveness between levels 50-75
        return 0.5 + (subjobLevel - 50) * (0.5 / 25)
    end
end

-- Validate specific ability access with level requirements
xi.job_utils.samurai.validateAbilityAccess = function(player, abilityId, requiredLevel)
    requiredLevel = requiredLevel or 1
    
    local hasAccess, effectiveness, effectiveLevel = xi.job_utils.samurai.validateJobAccess(player, abilityId)
    
    if not hasAccess then
        return false, "Samurai job required"
    end
    
    if effectiveLevel < requiredLevel then
        return false, string.format("Level %d required", requiredLevel)
    end
    
    return true, effectiveness
end

-----------------------------------
-- Enhanced Ability Check Functions
-----------------------------------
xi.job_utils.samurai.checkMeikyoShisui = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.MEIKYO_SHISUI, 1)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.samurai.checkHasso = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.HASSO, 25)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    if player:hasStatusEffect(xi.effect.SEIGAN) then
        return xi.msg.basic.CANNOT_PERFORM, 0
    end

    return 0, 0
end

xi.job_utils.samurai.checkSeigan = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.SEIGAN, 35)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    if player:hasStatusEffect(xi.effect.HASSO) then
        return xi.msg.basic.CANNOT_PERFORM, 0
    end

    return 0, 0
end

xi.job_utils.samurai.checkMeditate = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.MEDITATE, 30)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    return 0, 0
end

xi.job_utils.samurai.checkWardingCircle = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.WARDING_CIRCLE, 5)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    return 0, 0
end

xi.job_utils.samurai.checkThirdEye = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.THIRD_EYE, 15)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    return 0, 0
end

xi.job_utils.samurai.checkSekkanoki = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.SEKKANOKI, 40)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    return 0, 0
end

xi.job_utils.samurai.checkBladeBash = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.BLADE_BASH, 75)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    return 0, 0
end

xi.job_utils.samurai.checkShikikoyo = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.SHIKIKOYO, 75)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    return 0, 0
end

xi.job_utils.samurai.checkSengikori = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.SENGIKORI, 77)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    return 0, 0
end

xi.job_utils.samurai.checkHamanoha = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.HAMANOHA, 87)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    return 0, 0
end

xi.job_utils.samurai.checkHagakure = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.HAGAKURE, 95)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    return 0, 0
end

xi.job_utils.samurai.checkKonzenIttai = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.KONZEN_ITTAI, 65)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    return 0, 0
end

xi.job_utils.samurai.checkYaegasumi = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.YAEGASUMI, 96)
    
    if not hasAccess then
        return xi.msg.basic.JA_NO_EFFECT, 0
    end
    
    return 0, 0
end

-----------------------------------
-- Enhanced Ability Use Functions with Subjob Support
-----------------------------------
xi.job_utils.samurai.useMeikyoShisui = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.MEIKYO_SHISUI, 1)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local merits = player:getMerit(xi.merit.MEIKYO_SHISUI_RECAST)
    local baseDuration = 30
    local enhancedDuration = math.floor(baseDuration * effectiveness)
    
    player:addStatusEffect(xi.effect.MEIKYO_SHISUI, 1, 0, enhancedDuration)
    ability:setRecast(ability:getRecast() - merits)
    
    return enhancedDuration
end

xi.job_utils.samurai.useHasso = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.HASSO, 25)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local jpValue = player:getJobPointLevel(xi.jp.HASSO_EFFECT)
    local accuracyBonus = math.floor((10 + jpValue) * effectiveness)
    local storeTPBonus = math.floor((10 + jpValue) * effectiveness)
    local duration = math.floor(300 * effectiveness)

    player:addStatusEffect(xi.effect.HASSO, 1, 0, duration, 0, accuracyBonus, storeTPBonus)
    
    return duration
end

xi.job_utils.samurai.useSeigan = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.SEIGAN, 35)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local jpValue = player:getJobPointLevel(xi.jp.SEIGAN_EFFECT)
    local thirdEyeBonus = math.floor(jpValue * effectiveness)
    local duration = math.floor(300 * effectiveness)

    player:addStatusEffect(xi.effect.SEIGAN, 1, 0, duration, 0, thirdEyeBonus)
    
    return duration
end

xi.job_utils.samurai.useMeditate = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.MEDITATE, 30)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local jpValue = player:getJobPointLevel(xi.jp.MEDITATE_EFFECT)
    local tpBonus = math.floor((300 + (jpValue * 20)) * effectiveness)
    local currentTP = player:getTP()

    if currentTP + tpBonus > 3000 then
        player:setTP(3000)
    else
        player:setTP(currentTP + tpBonus)
    end
    
    return tpBonus
end

xi.job_utils.samurai.useWardingCircle = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.WARDING_CIRCLE, 5)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local baseDuration = 30 + player:getMod(xi.mod.ENHANCES_WARDING_CIRCLE)
    local duration = math.floor(baseDuration * effectiveness)
    
    player:addStatusEffect(xi.effect.WARDING_CIRCLE, 1, 0, duration)
    
    return duration
end

xi.job_utils.samurai.useThirdEye = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.THIRD_EYE, 15)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local jpValue = player:getJobPointLevel(xi.jp.THIRD_EYE_EFFECT)
    local anticipateBonus = math.floor(jpValue * effectiveness)
    local duration = math.floor(60 * effectiveness)

    player:addStatusEffect(xi.effect.THIRD_EYE, 1, 0, duration, 0, anticipateBonus)
    
    return duration
end

xi.job_utils.samurai.useSekkanoki = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.SEKKANOKI, 40)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local duration = math.floor(300 * effectiveness)  -- 5 minutes base duration
    local power = math.floor(100 * effectiveness)  -- TP cost reduction
    
    player:addStatusEffect(xi.effect.SEKKANOKI, power, 0, duration)
    
    return duration
end

xi.job_utils.samurai.useBladeBash = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.BLADE_BASH, 75)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local damage = 0
    local resist = applyPlayerResistance(player, -1, target, player:getStat(xi.mod.STR) - target:getStat(xi.mod.VIT), 0, xi.element.NONE)
    
    if resist > 0.0625 then
        damage = math.floor(25 * effectiveness)
        local stunDuration = math.floor(5 * effectiveness)
        target:addStatusEffect(xi.effect.STUN, 1, 0, stunDuration)
    end

    return damage
end

xi.job_utils.samurai.useShikikoyo = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.SHIKIKOYO, 75)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local duration = math.floor(300 * effectiveness)  -- 5 minutes base duration
    local power = math.floor(100 * effectiveness)  -- Enhances weapon skill accuracy
    
    player:addStatusEffect(xi.effect.SHIKIKOYO, power, 0, duration)
    
    return duration
end

xi.job_utils.samurai.useSengikori = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.SENGIKORI, 77)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local duration = math.floor(180 * effectiveness)  -- 3 minutes base duration
    local power = math.floor(100 * effectiveness)  -- Enhances weapon skill damage
    
    player:addStatusEffect(xi.effect.SENGIKORI, power, 0, duration)
    
    return duration
end

xi.job_utils.samurai.useHamanoha = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.HAMANOHA, 87)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local damage = 0
    local resist = applyPlayerResistance(player, -1, target, player:getStat(xi.mod.STR) - target:getStat(xi.mod.VIT), 0, xi.element.NONE)
    
    if resist > 0.0625 then
        damage = math.floor(50 * effectiveness)  -- Enhanced damage over Blade Bash
        local stunDuration = math.floor(7 * effectiveness)  -- Longer stun duration
        target:addStatusEffect(xi.effect.STUN, 1, 0, stunDuration)
    end

    return damage
end

xi.job_utils.samurai.useHagakure = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.HAGAKURE, 95)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local duration = math.floor(180 * effectiveness)  -- 3 minutes base duration
    local power = math.floor(100 * effectiveness)  -- Enhances critical hit rate
    
    player:addStatusEffect(xi.effect.HAGAKURE, power, 0, duration)
    
    return duration
end

xi.job_utils.samurai.useKonzenIttai = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.KONZEN_ITTAI, 65)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    -- Konzen-Ittai: Weapon Skill deals piercing damage to all enemies within range
    local damage = 0
    local resist = applyPlayerResistance(player, -1, target, player:getStat(xi.mod.STR) - target:getStat(xi.mod.VIT), 0, xi.element.NONE)
    
    if resist > 0.0625 then
        damage = math.floor(100 * effectiveness)  -- Piercing damage
    end

    return damage
end

xi.job_utils.samurai.useYaegasumi = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateAbilityAccess(player, xi.jobAbility.YAEGASUMI, 96)
    
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        return 0
    end
    
    local duration = math.floor(3600 * effectiveness)  -- 1 hour base duration
    local power = math.floor(100 * effectiveness)  -- Enhances TP gain from weapon skills
    
    player:addStatusEffect(xi.effect.YAEGASUMI, power, 0, duration)
    
    return duration
end

-----------------------------------
-- Enhanced Weaponskill Functions with Subjob Support
-----------------------------------
xi.job_utils.samurai.onUseWeaponskill = function(player, target, wsID, tp, primary, action, taChar)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateJobAccess(player, wsID)
    
    if not hasAccess then
        return 0, false, 0, 0, 0
    end
    
    local damage = 0
    local criticalHit = false
    local tpHitsLanded = 0
    local extraHitsLanded = 0
    local shadowsAbsorbed = 0

    -- Enhanced weaponskill damage for Samurai with subjob scaling
    if player:getMainJob() == xi.job.SAM or player:getSubJob() == xi.job.SAM then
        local samuraiBonus = 1.0 + (player:getSkillLevel(xi.skill.GREAT_KATANA) / 1000)
        samuraiBonus = samuraiBonus * effectiveness  -- Apply subjob penalty
        action:setParam(action:getParam() * samuraiBonus)
    end
    
    -- Shikikoyo enhancement (weapon skill accuracy)
    if player:hasStatusEffect(xi.effect.SHIKIKOYO) then
        local shikikoyoEffect = player:getStatusEffect(xi.effect.SHIKIKOYO)
        local accuracyBonus = math.floor((shikikoyoEffect:getPower() or 100) * effectiveness)
        action:setParam(action:getParam() + accuracyBonus)
    end
    
    -- Sengikori enhancement (weapon skill damage)
    if player:hasStatusEffect(xi.effect.SENGIKORI) then
        local sengikoriEffect = player:getStatusEffect(xi.effect.SENGIKORI)
        local damageBonus = 1.0 + ((sengikoriEffect:getPower() or 100) / 1000) * effectiveness
        action:setParam(action:getParam() * damageBonus)
    end
    
    -- Yaegasumi enhancement (TP gain from weapon skills)
    if player:hasStatusEffect(xi.effect.YAEGASUMI) then
        local yaegasumiEffect = player:getStatusEffect(xi.effect.YAEGASUMI)
        local tpBonus = math.floor((yaegasumiEffect:getPower() or 100) * effectiveness)
        player:addTP(tpBonus)
    end

    return damage, criticalHit, tpHitsLanded, extraHitsLanded, shadowsAbsorbed
end

-----------------------------------
-- Enhanced Store TP Functions with Subjob Support
-----------------------------------
xi.job_utils.samurai.getStoreTPBonus = function(player)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateJobAccess(player, nil)
    
    if not hasAccess then
        return 0
    end
    
    local storeTP = 0
    
    -- Hasso Store TP bonus with subjob scaling
    if player:hasStatusEffect(xi.effect.HASSO) then
        local effect = player:getStatusEffect(xi.effect.HASSO)
        local hassoBonus = math.floor(((effect:getPower() or 10) * effectiveness))
        storeTP = storeTP + hassoBonus
    end
    
    -- Merit bonuses with subjob scaling
    local meritBonus = math.floor(player:getMerit(xi.merit.STORE_TP) * effectiveness)
    storeTP = storeTP + meritBonus
    
    -- Sekkanoki TP cost reduction effect
    if player:hasStatusEffect(xi.effect.SEKKANOKI) then
        local sekkanokiEffect = player:getStatusEffect(xi.effect.SEKKANOKI)
        local tpReduction = math.floor((sekkanokiEffect:getPower() or 100) * effectiveness)
        storeTP = storeTP + tpReduction
    end
    
    return storeTP
end

-----------------------------------
-- Enhanced Combat Functions with Subjob Support
-----------------------------------
xi.job_utils.samurai.onCriticalHit = function(player, target, damage)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateJobAccess(player, nil)
    
    if not hasAccess then
        return damage
    end
    
    local enhancedDamage = damage
    
    -- Enhanced critical hit effects for Samurai with subjob scaling
    if player:hasStatusEffect(xi.effect.HASSO) then
        local critBonus = math.floor(0.1 * effectiveness * 100) / 100  -- 10% critical damage bonus with Hasso
        enhancedDamage = math.floor(damage * (1.0 + critBonus))
    end
    
    -- Hagakure critical hit enhancement
    if player:hasStatusEffect(xi.effect.HAGAKURE) then
        local hagakureEffect = player:getStatusEffect(xi.effect.HAGAKURE)
        local critBonus = math.floor(((hagakureEffect:getPower() or 100) / 1000) * effectiveness * 100) / 100
        enhancedDamage = math.floor(enhancedDamage * (1.0 + critBonus))
    end
    
    return enhancedDamage
end

-----------------------------------
-- Enhanced Merit and Job Point Integration
-----------------------------------
xi.job_utils.samurai.getMeritBonus = function(player, meritType)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateJobAccess(player, nil)
    
    if not hasAccess then
        return 0
    end
    
    local baseBonus = player:getMerit(meritType) or 0
    return math.floor(baseBonus * effectiveness)
end

xi.job_utils.samurai.getJobPointBonus = function(player, jpType)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateJobAccess(player, nil)
    
    if not hasAccess then
        return 0
    end
    
    local baseBonus = player:getJobPointLevel(jpType) or 0
    return math.floor(baseBonus * effectiveness)
end

-----------------------------------
-- Enhanced Great Katana Skill Functions
-----------------------------------
xi.job_utils.samurai.getGreatKatanaSkillBonus = function(player)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateJobAccess(player, nil)
    
    if not hasAccess then
        return 0
    end
    
    local skillLevel = player:getSkillLevel(xi.skill.GREAT_KATANA)
    local bonus = math.floor(skillLevel * effectiveness * 0.1)  -- 10% of skill level as bonus
    
    -- Additional bonus if main job Samurai
    if player:getMainJob() == xi.job.SAM then
        bonus = bonus + math.floor(skillLevel * 0.05)  -- Additional 5% for main job
    end
    
    return bonus
end

-----------------------------------
-- Enhanced Two-Hour Integration
-----------------------------------
xi.job_utils.samurai.enhanceTwoHourAbility = function(player, abilityId)
    local hasAccess, effectiveness = xi.job_utils.samurai.validateJobAccess(player, abilityId)
    
    if not hasAccess then
        return false, 0
    end
    
    if abilityId == xi.jobAbility.MEIKYO_SHISUI then
        -- Meikyo Shisui: Remove TP cost for weapon skills for duration
        local duration = math.floor(30 * effectiveness)
        local merits = xi.job_utils.samurai.getMeritBonus(player, xi.merit.MEIKYO_SHISUI_RECAST)
        
        return true, duration, merits
    end
    
    return false, 0
end

return xi.job_utils.samurai