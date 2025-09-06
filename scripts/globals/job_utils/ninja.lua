-----------------------------------
-- Ninja Job Utilities
-----------------------------------
require('scripts/globals/utils')
require('scripts/globals/jobpoints')
require('scripts/globals/ninjutsu')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.ninja = xi.job_utils.ninja or {}

-----------------------------------
-- Ninjutsu System Functions
-----------------------------------
function calculateNinjutsuDamage(player, baseDamage, element)
    local skill = player:getSkillLevel(xi.skill.NINJUTSU)
    local int = player:getStat(xi.mod.INT)
    
    local damage = baseDamage + math.floor(skill / 5) + math.floor(int / 3)
    
    -- Apply Futae bonus if active
    if player:hasStatusEffect(xi.effect.FUTAE) then
        damage = damage * 2
        player:delStatusEffect(xi.effect.FUTAE)
    end
    
    -- Job point bonuses
    damage = damage + player:getJobPointLevel(xi.jp.NINJUTSU_EFFECT)
    
    return damage
end

function handleUtsusemi(player, tier)
    local shadowCount = tier == 1 and 3 or 4
    shadowCount = shadowCount + player:getJobPointLevel(xi.jp.UTSUSEMI_EFFECT)
    
    -- Remove existing shadows first
    player:delStatusEffect(xi.effect.COPY_IMAGE)
    player:delStatusEffect(xi.effect.COPY_IMAGE_2)
    player:delStatusEffect(xi.effect.COPY_IMAGE_3)
    player:delStatusEffect(xi.effect.COPY_IMAGE_4)
    
    -- Add new shadows
    if tier == 1 then
        player:addStatusEffect(xi.effect.COPY_IMAGE, shadowCount, 0, 900)
    else
        player:addStatusEffect(xi.effect.COPY_IMAGE_4, shadowCount, 0, 900)
    end
    
    return shadowCount
end

function calculateElementalNinjutsu(player, spell, target)
    local baseDamage = spell:getBaseDamage()
    local element = spell:getElement()
    
    return calculateNinjutsuDamage(player, baseDamage, element)
end

-----------------------------------
-- Ability Check Functions
-----------------------------------
xi.job_utils.ninja.checkMijinGakure = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.ninja.checkYonin = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.YONIN) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.ninja.checkInnin = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.INNIN) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.ninja.checkSange = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.SANGE) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.ninja.checkFutae = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.FUTAE) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.ninja.checkIssekigan = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.ISSEKIGAN) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.ninja.checkMikage = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

-----------------------------------
-- Ninjutsu Spells
-----------------------------------
xi.job_utils.ninja.castUtsusemi = function(player, tier)
    return handleUtsusemi(player, tier)
end

xi.job_utils.ninja.castElementalNinjutsu = function(player, target, spell)
    local damage = calculateElementalNinjutsu(player, spell, target)
    
    -- Apply resistances and final calculations
    local resist = target:getMagicResistance(spell:getElement())
    damage = damage * resist
    
    target:takeDamage(damage, player, xi.attackType.MAGICAL, spell:getElement())
    return damage
end

xi.job_utils.ninja.castEnfeeblingNinjutsu = function(player, target, spell)
    local duration = 60
    local potency = player:getSkillLevel(xi.skill.NINJUTSU) / 10
    
    -- Apply job point bonuses
    duration = duration + player:getJobPointLevel(xi.jp.NINJUTSU_DURATION)
    potency = potency + player:getJobPointLevel(xi.jp.NINJUTSU_EFFECT)
    
    local effectType = spell:getEffect()
    target:addStatusEffect(effectType, potency, 0, duration)
    
    return potency
end

-----------------------------------
-- Ability Use Functions
-----------------------------------
xi.job_utils.ninja.useMijinGakure = function(player, target, ability, action)
    local dmg    = player:getHP() * 0.8 + player:getMainLvl() / 0.5
    local resist = xi.mobskills.applyPlayerResistance(player, nil, target, player:getStat(xi.mod.INT)-target:getStat(xi.mod.INT), 0, xi.element.NONE)

    -- Job Point Bonus (3% per Level)
    dmg = dmg * (1 + (player:getJobPointLevel(xi.jp.MIJIN_GAKURE_EFFECT) * 0.03))
    dmg = dmg * resist
    dmg = utils.stoneskin(target, dmg)

    target:takeDamage(dmg, player, xi.attackType.SPECIAL, xi.damageType.ELEMENTAL)
    player:setLocalVar('MijinGakure', 1)
    player:setHP(0)

    return dmg
end

xi.job_utils.ninja.useYonin = function(player, target, ability, action)
    target:delStatusEffect(xi.effect.INNIN)
    target:delStatusEffect(xi.effect.YONIN)
    
    local duration = 300 + player:getJobPointLevel(xi.jp.YONIN_EFFECT) * 30
    local enmityBonus = 30 + player:getJobPointLevel(xi.jp.YONIN_EFFECT)
    
    target:addStatusEffect(xi.effect.YONIN, enmityBonus, 15, duration, 0, 0)
end

xi.job_utils.ninja.useInnin = function(player, target, ability, action)
    target:delStatusEffect(xi.effect.INNIN)
    target:delStatusEffect(xi.effect.YONIN)
    
    local duration = 300 + player:getJobPointLevel(xi.jp.INNIN_EFFECT) * 30
    local enmityReduction = 30 + player:getJobPointLevel(xi.jp.INNIN_EFFECT)
    
    target:addStatusEffect(xi.effect.INNIN, enmityReduction, 15, duration, 0, 20)
end

xi.job_utils.ninja.useSange = function(player, target, ability, action)
    local potency = player:getMerit(xi.merit.SANGE)-1
    local duration = 60 + player:getJobPointLevel(xi.jp.SANGE_EFFECT)
    
    player:addStatusEffect(xi.effect.SANGE, potency * 25, 0, duration)
end

xi.job_utils.ninja.useFutae = function(player, target, ability, action)
    local duration = 60 + player:getJobPointLevel(xi.jp.FUTAE_EFFECT)
    target:addStatusEffect(xi.effect.FUTAE, 1, 0, duration)
end

xi.job_utils.ninja.useIssekigan = function(player, target, ability, action)
    local duration = 60 + player:getJobPointLevel(xi.jp.ISSEKIGAN_EFFECT)
    local critRate = 25 + player:getJobPointLevel(xi.jp.ISSEKIGAN_EFFECT)
    
    target:addStatusEffect(xi.effect.ISSEKIGAN, critRate, 0, duration)
end

xi.job_utils.ninja.useMikage = function(player, target, ability, action)
    local duration = 45 + player:getJobPointLevel(xi.jp.MIKAGE_EFFECT)
    target:addStatusEffect(xi.effect.MIKAGE, 1, 0, duration)
end

-----------------------------------
-- Advanced Ninja Techniques
-----------------------------------
xi.job_utils.ninja.enhanceNinjutsu = function(player, spell)
    local enhancement = 0
    
    -- Sange enhancement for weapon skills
    if player:hasStatusEffect(xi.effect.SANGE) then
        enhancement = enhancement + player:getStatusEffect(xi.effect.SANGE):getPower()
    end
    
    -- Issekigan enhancement for critical hits
    if player:hasStatusEffect(xi.effect.ISSEKIGAN) then
        enhancement = enhancement + 25
    end
    
    return enhancement
end
