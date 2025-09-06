-----------------------------------
-- Warrior Job Utilities
-----------------------------------
require('scripts/globals/utils')
require('scripts/globals/jobpoints')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.warrior = xi.job_utils.warrior or {}

-----------------------------------
-- Warrior Combat Enhancement
-----------------------------------
function calculateProvokeEnmity(player, target)
    local enmityGain = 1000 -- Base enmity gain
    enmityGain = enmityGain + player:getJobPointLevel(xi.jp.PROVOKE_EFFECT) * 100
    return enmityGain
end

function getWarriorChargeBonus(player)
    local merits = player:getMerit(xi.merit.WARRIORS_CHARGE)
    local jpBonus = player:getJobPointLevel(xi.jp.WARRIORS_CHARGE_EFFECT)
    return merits + jpBonus
end

function handleDoubleAttackBonus(player)
    local bonuses = 0
    
    if player:hasStatusEffect(xi.effect.BERSERK) then
        bonuses = bonuses + 10
    end
    
    if player:hasStatusEffect(xi.effect.AGGRESSOR) then
        bonuses = bonuses + 5
    end
    
    bonuses = bonuses + player:getJobPointLevel(xi.jp.DOUBLE_ATTACK_EFFECT)
    
    return bonuses
end

-----------------------------------
-- Ability Check Functions
-----------------------------------
xi.job_utils.warrior.checkBrazenRush = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.warrior.checkMightyStrikes = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.warrior.checkTomahawk = function(player, target, ability)
    local ammoID = player:getEquipID(xi.slot.AMMO)

    if ammoID == xi.item.THROWING_TOMAHAWK then
        return 0, 0
    else
        return xi.msg.basic.CANNOT_PERFORM, 0
    end
end

xi.job_utils.warrior.checkProvoke = function(player, target, ability)
    if not target:isMob() then
        return xi.msg.basic.CANNOT_PERFORM_TARG, 0
    end
    return 0, 0
end

xi.job_utils.warrior.checkAggressor = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.AGGRESSOR) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.warrior.checkBerserk = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.BERSERK) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.warrior.checkDefender = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.DEFENDER) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

-----------------------------------
-- Core Warrior Abilities
-----------------------------------
xi.job_utils.warrior.useProvoke = function(player, target, ability)
    if target:isMob() then
        local enmityGain = calculateProvokeEnmity(player, target)
        target:addEnmity(player, enmityGain, 0)
        
        -- Job point enhancement - chance to reset recast
        local jpLevel = player:getJobPointLevel(xi.jp.PROVOKE_RECAST)
        if math.random(100) <= jpLevel * 2 then
            ability:setRecast(0)
        end
    end
end

-----------------------------------
-- Ability Use Functions
-----------------------------------
xi.job_utils.warrior.useAggressor = function(player, target, ability)
    local merits = player:getMerit(xi.merit.AGGRESSIVE_AIM)
    local duration = 180 + player:getMod(xi.mod.AGGRESSOR_DURATION) + player:getJobPointLevel(xi.jp.AGGRESSOR_EFFECT) * 10

    player:addStatusEffect(xi.effect.AGGRESSOR, merits, 0, duration)
end

xi.job_utils.warrior.useBerserk = function(player, target, ability)
    local power = 25 + player:getMod(xi.mod.BERSERK_POTENCY) + player:getJobPointLevel(xi.jp.BERSERK_EFFECT)
    local duration = 180 + player:getMod(xi.mod.BERSERK_DURATION) + player:getJobPointLevel(xi.jp.BERSERK_EFFECT) * 10
    
    player:addStatusEffect(xi.effect.BERSERK, power, 0, duration)
end

xi.job_utils.warrior.useBloodRage = function(player, target, ability)
    local power    = 20 + player:getJobPointLevel(xi.jp.BLOOD_RAGE_EFFECT)
    local duration = 30 + player:getMod(xi.mod.ENHANCES_BLOOD_RAGE)

    target:addStatusEffect(xi.effect.BLOOD_RAGE, power, 0, duration)

    if player:getID() ~= target:getID() then
        ability:setMsg(xi.msg.basic.JA_GAIN_EFFECT)
    end

    return xi.effect.BLOOD_RAGE
end

xi.job_utils.warrior.useBrazenRush = function(player, target, ability)
    local power = 100 + player:getJobPointLevel(xi.jp.BRAZEN_RUSH_EFFECT)
    local duration = 30 + player:getJobPointLevel(xi.jp.BRAZEN_RUSH_EFFECT)
    
    player:addStatusEffect(xi.effect.BRAZEN_RUSH, power, 3, duration)
end

xi.job_utils.warrior.useDefender = function(player, target, ability)
    local duration = 180 + player:getMod(xi.mod.DEFENDER_DURATION) + player:getJobPointLevel(xi.jp.DEFENDER_EFFECT) * 10
    player:addStatusEffect(xi.effect.DEFENDER, 1, 0, duration)
end

xi.job_utils.warrior.useMightyStrikes = function(player, target, ability)
    local duration = 45 + player:getJobPointLevel(xi.jp.MIGHTY_STRIKES_EFFECT)
    player:addStatusEffect(xi.effect.MIGHTY_STRIKES, 1, 0, duration)
end

xi.job_utils.warrior.useRestraint = function(player, target, ability)
    local duration = 300 + player:getJobPointLevel(xi.jp.RESTRAINT_EFFECT) * 30
    player:addStatusEffect(xi.effect.RESTRAINT, 0, 0, duration)
end

xi.job_utils.warrior.useRetaliation = function(player, target, ability)
    local duration = 180 + player:getJobPointLevel(xi.jp.RETALIATION_EFFECT) * 10
    player:addStatusEffect(xi.effect.RETALIATION, 1, 0, duration)
end

xi.job_utils.warrior.useTomahawk = function(player, target, ability)
    local merits   = player:getMerit(xi.merit.TOMAHAWK) - 15
    local duration = 30 + merits + player:getJobPointLevel(xi.jp.TOMAHAWK_EFFECT)

    target:addStatusEffectEx(xi.effect.TOMAHAWK, 0, 25, 3, duration, 0, 0, 0)
    player:removeAmmo()
end

xi.job_utils.warrior.useWarcry = function(player, target, ability)
    local merit    = player:getMerit(xi.merit.SAVAGERY)
    local warLevel = utils.getActiveJobLevel(player, xi.job.WAR)
    local power    = (math.floor((warLevel / 4) + 4.75) / 256) * 100
    local duration = 30

    duration = duration + player:getMod(xi.mod.WARCRY_DURATION) + player:getJobPointLevel(xi.jp.WARCRY_EFFECT) * 5
    power = power + player:getJobPointLevel(xi.jp.WARCRY_EFFECT)

    target:addStatusEffect(xi.effect.WARCRY, power, 0, duration, 0, merit)

    if player:getID() ~= target:getID() then
        ability:setMsg(xi.msg.basic.JA_ATK_ENHANCED)
    end

    return xi.effect.WARCRY
end

xi.job_utils.warrior.useWarriorsCharge = function(player, target, ability)
    local merits = player:getMerit(xi.merit.WARRIORS_CHARGE)
    local jpBonus = player:getJobPointLevel(xi.jp.WARRIORS_CHARGE_EFFECT)
    local duration = 60 + jpBonus * 10

    player:addStatusEffect(xi.effect.WARRIORS_CHARGE, merits - 5 + jpBonus, 0, duration)
end

-----------------------------------
-- Warrior Enhancement System
-----------------------------------
xi.job_utils.warrior.enhanceAttack = function(player)
    local enhancement = 0
    
    -- Berserk enhancement
    if player:hasStatusEffect(xi.effect.BERSERK) then
        enhancement = enhancement + player:getStatusEffect(xi.effect.BERSERK):getPower()
    end
    
    -- Warcry enhancement
    if player:hasStatusEffect(xi.effect.WARCRY) then
        enhancement = enhancement + player:getStatusEffect(xi.effect.WARCRY):getPower()
    end
    
    -- Aggressor accuracy bonus
    if player:hasStatusEffect(xi.effect.AGGRESSOR) then
        enhancement = enhancement + 25
    end
    
    return enhancement
end

xi.job_utils.warrior.calculateWarriorDamage = function(player, baseDamage)
    local finalDamage = baseDamage
    
    -- Apply warrior-specific damage bonuses
    if player:hasStatusEffect(xi.effect.MIGHTY_STRIKES) then
        finalDamage = finalDamage * 2  -- Critical hit guarantee
    end
    
    if player:hasStatusEffect(xi.effect.BLOOD_RAGE) then
        finalDamage = finalDamage + player:getStatusEffect(xi.effect.BLOOD_RAGE):getPower()
    end
    
    return finalDamage
end
