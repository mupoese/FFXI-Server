-----------------------------------
-- Samurai Job Utilities
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.samurai = xi.job_utils.samurai or {}

-----------------------------------
-- Ability Check Functions
-----------------------------------
xi.job_utils.samurai.checkMeikyoShisui = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.samurai.checkHasso = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.SEIGAN) then
        return xi.msg.basic.CANNOT_PERFORM, 0
    end

    return 0, 0
end

xi.job_utils.samurai.checkSeigan = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.HASSO) then
        return xi.msg.basic.CANNOT_PERFORM, 0
    end

    return 0, 0
end

xi.job_utils.samurai.checkMeditate = function(player, target, ability)
    return 0, 0
end

xi.job_utils.samurai.checkWardingCircle = function(player, target, ability)
    return 0, 0
end

xi.job_utils.samurai.checkThirdEye = function(player, target, ability)
    return 0, 0
end

-----------------------------------
-- Ability Use Functions
-----------------------------------
xi.job_utils.samurai.useMeikyoShisui = function(player, target, ability)
    local merits = player:getMerit(xi.merit.MEIKYO_SHISUI_RECAST)
    
    player:addStatusEffect(xi.effect.MEIKYO_SHISUI, 1, 0, 30)
    ability:setRecast(ability:getRecast() - merits)
end

xi.job_utils.samurai.useHasso = function(player, target, ability)
    local jpValue = player:getJobPointLevel(xi.jp.HASSO_EFFECT)
    local accuracyBonus = 10 + jpValue
    local storeTPBonus = 10 + jpValue

    player:addStatusEffect(xi.effect.HASSO, 1, 0, 300, 0, accuracyBonus, storeTPBonus)
end

xi.job_utils.samurai.useSeigan = function(player, target, ability)
    local jpValue = player:getJobPointLevel(xi.jp.SEIGAN_EFFECT)
    local thirdEyeBonus = jpValue

    player:addStatusEffect(xi.effect.SEIGAN, 1, 0, 300, 0, thirdEyeBonus)
end

xi.job_utils.samurai.useMeditate = function(player, target, ability)
    local jpValue = player:getJobPointLevel(xi.jp.MEDITATE_EFFECT)
    local tpBonus = 300 + (jpValue * 20)
    local currentTP = player:getTP()

    if currentTP + tpBonus > 3000 then
        player:setTP(3000)
    else
        player:setTP(currentTP + tpBonus)
    end
end

xi.job_utils.samurai.useWardingCircle = function(player, target, ability)
    local duration = 30 + player:getMod(xi.mod.ENHANCES_WARDING_CIRCLE)
    
    player:addStatusEffect(xi.effect.WARDING_CIRCLE, 1, 0, duration)
end

xi.job_utils.samurai.useThirdEye = function(player, target, ability)
    local jpValue = player:getJobPointLevel(xi.jp.THIRD_EYE_EFFECT)
    local anticipateBonus = jpValue

    player:addStatusEffect(xi.effect.THIRD_EYE, 1, 0, 60, 0, anticipateBonus)
end

xi.job_utils.samurai.useBladeBash = function(player, target, ability)
    local damage = 0
    local resist = applyPlayerResistance(player, -1, target, player:getStat(xi.mod.STR) - target:getStat(xi.mod.VIT), 0, xi.element.NONE)
    
    if resist > 0.0625 then
        damage = 25
        target:addStatusEffect(xi.effect.STUN, 1, 0, 5)
    end

    return damage
end

-----------------------------------
-- Weaponskill Functions
-----------------------------------
xi.job_utils.samurai.onUseWeaponskill = function(player, target, wsID, tp, primary, action, taChar)
    local damage = 0
    local criticalHit = false
    local tpHitsLanded = 0
    local extraHitsLanded = 0
    local shadowsAbsorbed = 0

    -- Enhanced weaponskill damage for Samurai
    if player:getMainJob() == xi.job.SAM then
        local samuraiBonus = 1.0 + (player:getSkillLevel(xi.skill.GREAT_KATANA) / 1000)
        action:setParam(action:getParam() * samuraiBonus)
    end

    return damage, criticalHit, tpHitsLanded, extraHitsLanded, shadowsAbsorbed
end

-----------------------------------
-- Store TP Functions
-----------------------------------
xi.job_utils.samurai.getStoreTPBonus = function(player)
    local storeTP = 0
    
    -- Hasso Store TP bonus
    if player:hasStatusEffect(xi.effect.HASSO) then
        local effect = player:getStatusEffect(xi.effect.HASSO)
        storeTP = storeTP + (effect:getPower() or 10)
    end
    
    -- Merit bonuses
    storeTP = storeTP + player:getMerit(xi.merit.STORE_TP)
    
    return storeTP
end

-----------------------------------
-- Combat Enhancements
-----------------------------------
xi.job_utils.samurai.onCriticalHit = function(player, target, damage)
    -- Enhanced critical hit effects for Samurai
    if player:hasStatusEffect(xi.effect.HASSO) then
        return math.floor(damage * 1.1) -- 10% critical damage bonus with Hasso
    end
    
    return damage
end

return xi.job_utils.samurai