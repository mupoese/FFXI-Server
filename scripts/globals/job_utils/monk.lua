-----------------------------------
-- Monk Job Utilities
-----------------------------------
require('scripts/globals/utils')
require('scripts/globals/jobpoints')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.monk = xi.job_utils.monk or {}

local chakraStatusEffects =
{
    POISON       = 0, -- Removed by default
    BLINDNESS    = 0, -- Removed by default
    PARALYSIS    = 1,
    DISEASE      = 2,
    PLAGUE       = 4,
}

-----------------------------------
-- Monk Combat Enhancement
-----------------------------------
function calculateChiBlast(player, target)
    local damage = player:getSkillLevel(xi.skill.HAND_TO_HAND) / 4
    damage = damage + player:getStat(xi.mod.VIT) / 2
    
    -- Job point enhancement
    damage = damage + player:getJobPointLevel(xi.jp.CHI_BLAST_EFFECT) * 5
    
    -- Apply target resistance
    local resist = target:getMagicResistance(xi.element.NONE)
    damage = damage * resist
    
    return math.floor(damage)
end

function getHandToHandSkillBonus(player)
    local skill = player:getSkillLevel(xi.skill.HAND_TO_HAND)
    return math.floor(skill / 20) -- Bonus per 20 skill points
end

function calculateBoostPower(player)
    local basePower = 12.5
    basePower = basePower + (0.10 * player:getMod(xi.mod.BOOST_EFFECT))
    basePower = basePower + player:getJobPointLevel(xi.jp.BOOST_EFFECT)
    return basePower
end

-----------------------------------
-- Ability Check Functions
-----------------------------------
xi.job_utils.monk.checkHundredFists = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.monk.checkInnerStrength = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.monk.checkChiBlast = function(player, target, ability)
    if not target:isMob() then
        return xi.msg.basic.CANNOT_PERFORM_TARG, 0
    end
    return 0, 0
end

xi.job_utils.monk.checkBoost = function(player, target, ability)
    return 0, 0
end

xi.job_utils.monk.checkFocus = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.FOCUS) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.monk.checkDodge = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.DODGE) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.monk.checkCounterstance = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.COUNTERSTANCE) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

-----------------------------------
-- Ability Use Functions
-----------------------------------
xi.job_utils.monk.useChiBlast = function(player, target, ability)
    local damage = calculateChiBlast(player, target)
    
    -- Apply damage
    target:takeDamage(damage, player, xi.attackType.MAGICAL, xi.damageType.ELEMENTAL)
    
    -- Chance to stun based on job points
    local stunChance = player:getJobPointLevel(xi.jp.CHI_BLAST_EFFECT)
    if math.random(100) <= stunChance then
        target:addStatusEffect(xi.effect.STUN, 1, 0, 3)
    end
    
    return damage
end
xi.job_utils.monk.useBoost = function(player, target, ability)
    local power = calculateBoostPower(player)

    if player:hasStatusEffect(xi.effect.BOOST) then
        local effect = player:getStatusEffect(xi.effect.BOOST)
        effect:setPower(effect:getPower() + power)
        player:addMod(xi.mod.ATTP, power)
    else
        local duration = 180 + player:getJobPointLevel(xi.jp.BOOST_EFFECT) * 10
        player:addStatusEffect(xi.effect.BOOST, power, 0, duration)
    end
end

xi.job_utils.monk.useFocus = function(player, target, ability)
    local power = 15 + player:getJobPointLevel(xi.jp.FOCUS_EFFECT)
    local duration = 180 + player:getJobPointLevel(xi.jp.FOCUS_EFFECT) * 10
    
    player:addStatusEffect(xi.effect.FOCUS, power, 0, duration)
end

xi.job_utils.monk.useDodge = function(player, target, ability)
    local power = 15 + player:getJobPointLevel(xi.jp.DODGE_EFFECT)
    local duration = 180 + player:getJobPointLevel(xi.jp.DODGE_EFFECT) * 10
    
    player:addStatusEffect(xi.effect.DODGE, power, 0, duration)
end

xi.job_utils.monk.useCounterstance = function(player, target, ability)
    local duration = 300 + player:getJobPointLevel(xi.jp.COUNTERSTANCE_EFFECT) * 30
    player:addStatusEffect(xi.effect.COUNTERSTANCE, 1, 0, duration)
end

-- TODO: add Melee Gloves +2 aug
xi.job_utils.monk.useChakra = function(player, target, ability)
    local chakraRemoval = player:getMod(xi.mod.CHAKRA_REMOVAL)

    for k, v in pairs(chakraStatusEffects) do
        if bit.band(chakraRemoval, v) == v then
            player:delStatusEffect(xi.effect[k])
        end
    end

    -- see https://www.bg-wiki.com/ffxi/Chakra
    local monkLevel         = utils.getActiveJobLevel(player, xi.job.MNK)
    local jpModifier        = target:getJobPointLevel(xi.jp.CHAKRA_EFFECT) -- NOTE: Level is the modified value, so 10 per point spent
    local hpModifier        = ((monkLevel + 1) * 0.2 / 100) * player:getMaxHP()
    local chakraMultiplier  = 1 + player:getMod(xi.mod.CHAKRA_MULT) / 100
    local maxRecoveryAmount = (player:getStat(xi.mod.VIT) * 2 + hpModifier) * chakraMultiplier + jpModifier
    local recoveryAmount    = math.min(player:getMaxHP() - player:getHP(), maxRecoveryAmount)

    player:setHP(player:getHP() + recoveryAmount)

    local merits = player:getMerit(xi.merit.INVIGORATE)
    if merits > 0 then
        if player:hasStatusEffect(xi.effect.REGEN) then
            player:delStatusEffect(xi.effect.REGEN)
        end

        player:addStatusEffect(xi.effect.REGEN, 10, 0, merits, 0, 0, 1)
    end

    return recoveryAmount
end

-----------------------------------
-- Enhanced Monk Abilities
-----------------------------------
xi.job_utils.monk.useFootwork = function(player, target, ability)
    local kickDmg = 20 + player:getWeaponDmg() + player:getJobPointLevel(xi.jp.FOOTWORK_EFFECT)
    local kickAttPercent = 25 + player:getMod(xi.mod.FOOTWORK_ATT_BONUS)

    player:addStatusEffect(xi.effect.FOOTWORK, kickDmg, 0, 60, 0, kickAttPercent)
end

xi.job_utils.monk.useFormlessStrikes = function(player, target, ability)
    local duration = 180 + player:getJobPointLevel(xi.jp.FORMLESS_STRIKES_EFFECT) * 10
    player:addStatusEffect(xi.effect.FORMLESS_STRIKES, 1, 0, duration)
end

xi.job_utils.monk.useHundredFists = function(player, target, ability)
    local duration = 45 + player:getJobPointLevel(xi.jp.HUNDRED_FISTS_EFFECT)
    player:addStatusEffect(xi.effect.HUNDRED_FISTS, 1, 0, duration)
end

-- TODO: Support Tantra Cyclas + 1 (does not give critical hit damage)
-- Probably will be exceptionally jank, very low priority
xi.job_utils.monk.impetusMissListener = function(attacker, victim, attack)
    local effect = attacker:getStatusEffect(xi.effect.IMPETUS)

    if effect then
        local mainPower = effect:getPower()    -- Stores Attack & Critical Hit Rate bonuses
        local subPower  = effect:getSubPower() -- Stores Critical Hit Damage & Accuracy bonuses

        if mainPower > 0 then
            attacker:delMod(xi.mod.ATT, mainPower * 2)
            attacker:delMod(xi.mod.CRITHITRATE, mainPower)

            effect:setPower(0)
        end

        if subPower > 0 then
            attacker:delMod(xi.mod.ACC, subPower * 2)
            attacker:delMod(xi.mod.CRIT_DMG_INCREASE, subPower)

            effect:setSubPower(0)
        end
    end
end

-- TODO: Support Tantra Cyclas + 1 (does not give critical hit damage)
-- Probably will be exceptionally jank, very low priority
xi.job_utils.monk.impetusHitListener = function(attacker, victim, attack)
    local effect = attacker:getStatusEffect(xi.effect.IMPETUS)

    if effect then
        local mainPower = effect:getPower()    -- Stores Attack & Critical Hit Rate bonuses
        local subPower  = effect:getSubPower() -- Stores Critical Hit Damage & Accuracy bonuses

        if mainPower < 50 then
            attacker:addMod(xi.mod.ATT, 2)
            attacker:addMod(xi.mod.CRITHITRATE, 1)

            effect:setPower(mainPower + 1)
        end

        if attacker:getMod(xi.mod.AUGMENTS_IMPETUS) > 0 and subPower < 50 then
            attacker:addMod(xi.mod.ACC, 2)
            attacker:addMod(xi.mod.CRIT_DMG_INCREASE, 1)

            effect:setSubPower(subPower + 1)
        end
    end
end

xi.job_utils.monk.useImpetus = function(player, target, ability)
    local duration = 180 + player:getJobPointLevel(xi.jp.IMPETUS_EFFECT) * 10
    player:addStatusEffect(xi.effect.IMPETUS, 0, 0, duration)
end

xi.job_utils.monk.useInnerStrength = function(player, target, ability)
    local duration = 30 + player:getJobPointLevel(xi.jp.INNER_STRENGTH_EFFECT)
    local power = 2 + player:getJobPointLevel(xi.jp.INNER_STRENGTH_EFFECT)
    player:addStatusEffect(xi.effect.INNER_STRENGTH, power, 0, duration)
end

xi.job_utils.monk.useMantra = function(player, target, ability)
    local merits = player:getMerit(xi.merit.MANTRA)
    local jpBonus = player:getJobPointLevel(xi.jp.MANTRA_EFFECT)

    target:delStatusEffect(xi.effect.MAX_HP_BOOST) -- TODO: confirm which versions of HP boost mantra can overwrite
    target:addStatusEffect(xi.effect.MAX_HP_BOOST, merits + jpBonus, 0, 180)

    return 0 -- xi.effect.MANTRA -- TODO: implement xi.effect.MANTRA
end

xi.job_utils.monk.usePerfectCounter = function(player, target, ability)
    local duration = 30 + player:getJobPointLevel(xi.jp.PERFECT_COUNTER_EFFECT)
    local power = 2 + player:getJobPointLevel(xi.jp.PERFECT_COUNTER_EFFECT)
    player:addStatusEffect(xi.effect.PERFECT_COUNTER, power, 0, duration)
end

-----------------------------------
-- Monk Enhancement System
-----------------------------------
xi.job_utils.monk.enhanceHandToHandDamage = function(player, baseDamage)
    local enhancement = 0
    
    -- Boost enhancement
    if player:hasStatusEffect(xi.effect.BOOST) then
        enhancement = enhancement + player:getStatusEffect(xi.effect.BOOST):getPower()
    end
    
    -- Impetus enhancement
    if player:hasStatusEffect(xi.effect.IMPETUS) then
        enhancement = enhancement + player:getStatusEffect(xi.effect.IMPETUS):getPower() * 2
    end
    
    -- Hand-to-hand skill bonus
    enhancement = enhancement + getHandToHandSkillBonus(player)
    
    return baseDamage + enhancement
end
