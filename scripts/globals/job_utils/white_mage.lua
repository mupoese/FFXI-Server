-----------------------------------
-- White Mage Job Utilities
-----------------------------------
require('scripts/globals/utils')
require('scripts/globals/jobpoints')
require('scripts/globals/magic')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.white_mage = xi.job_utils.white_mage or {}

local removables =
{
    xi.effect.FLASH,              xi.effect.BLINDNESS,      xi.effect.MAX_HP_DOWN,    xi.effect.MAX_MP_DOWN,
    xi.effect.PARALYSIS,          xi.effect.POISON,         xi.effect.CURSE_I,        xi.effect.CURSE_II,
    xi.effect.DISEASE,            xi.effect.PLAGUE,         xi.effect.WEIGHT,         xi.effect.BIND,
    xi.effect.BIO,                xi.effect.DIA,            xi.effect.BURN,           xi.effect.FROST,
    xi.effect.CHOKE,              xi.effect.RASP,           xi.effect.SHOCK,          xi.effect.DROWN,
    xi.effect.STR_DOWN,           xi.effect.DEX_DOWN,       xi.effect.VIT_DOWN,       xi.effect.AGI_DOWN,
    xi.effect.INT_DOWN,           xi.effect.MND_DOWN,       xi.effect.CHR_DOWN,       xi.effect.ADDLE,
    xi.effect.SLOW,               xi.effect.HELIX,          xi.effect.ACCURACY_DOWN,  xi.effect.ATTACK_DOWN,
    xi.effect.EVASION_DOWN,       xi.effect.DEFENSE_DOWN,   xi.effect.MAGIC_ACC_DOWN, xi.effect.MAGIC_ATK_DOWN,
    xi.effect.MAGIC_EVASION_DOWN, xi.effect.MAGIC_DEF_DOWN, xi.effect.MAX_TP_DOWN,    xi.effect.SILENCE,
    xi.effect.PETRIFICATION
}

-----------------------------------
-- Divine Magic Enhancement
-----------------------------------
function getDivineSealBonus(player)
    if player:hasStatusEffect(xi.effect.DIVINE_SEAL) then
        return 100 -- 100% magic accuracy bonus for healing
    end
    return 0
end

function calculateCurePotency(player, baseCure)
    local healingSkill = player:getSkillLevel(xi.skill.HEALING_MAGIC)
    local mnd = player:getStat(xi.mod.MND)
    local vit = player:getStat(xi.mod.VIT)
    
    local potency = baseCure + math.floor(healingSkill / 5) + math.floor(mnd / 3) + math.floor(vit / 10)
    
    -- Apply Divine Seal bonus
    if player:hasStatusEffect(xi.effect.DIVINE_SEAL) then
        potency = potency * 1.5
    end
    
    -- Job point bonuses
    potency = potency + player:getJobPointLevel(xi.jp.CURE_POTENCY)
    
    return potency
end

function handleProtectShell(player, target, spellType, tier)
    local duration = 1800 -- 30 minutes base
    duration = duration + player:getJobPointLevel(xi.jp.PROTECT_SHELL_DURATION) * 60
    
    local power = tier * 10 + player:getJobPointLevel(xi.jp.PROTECT_SHELL_EFFECT)
    
    if spellType == "protect" then
        target:addStatusEffect(xi.effect.PROTECT, power, 0, duration)
    elseif spellType == "shell" then
        target:addStatusEffect(xi.effect.SHELL, power, 0, duration)
    end
end

function handleRaise(player, target, tier)
    if not target:isDead() then
        return false
    end
    
    local weaknessLevel = 1
    local hpPercent = 0.25
    
    -- Higher tier raises give better recovery
    if tier >= 2 then
        hpPercent = 0.5
        weaknessLevel = 0
    elseif tier >= 3 then
        hpPercent = 0.75
        weaknessLevel = 0
    end
    
    target:raise(hpPercent)
    if weaknessLevel > 0 then
        target:addStatusEffect(xi.effect.WEAKNESS, weaknessLevel, 0, 300)
    end
    
    return true
end

-----------------------------------
-- Ability Check Functions
-----------------------------------
xi.job_utils.white_mage.checkAsylum = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.white_mage.checkBenediction = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.white_mage.checkDevotion = function(player, target, ability)
    if player:getID() == target:getID() then
        return xi.msg.basic.CANNOT_PERFORM_TARG, 0
    elseif player:getHP() < 4 then -- Fails if HP < 4
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    else
        return 0, 0
    end
end

xi.job_utils.white_mage.checkMartyr = function(player, target, ability)
    if player:getID() == target:getID() then
        return xi.msg.basic.CANNOT_PERFORM_TARG, 0
    elseif player:getHP() < 4 then -- Fails if HP < 4
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    else
        return 0, 0
    end
end

xi.job_utils.white_mage.checkDivineSeal = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.DIVINE_SEAL) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

-----------------------------------
-- Healing and Protection Magic
-----------------------------------
xi.job_utils.white_mage.enhanceCure = function(player, target, baseCure)
    return calculateCurePotency(player, baseCure)
end

xi.job_utils.white_mage.castProtect = function(player, target, tier)
    handleProtectShell(player, target, "protect", tier)
end

xi.job_utils.white_mage.castShell = function(player, target, tier)
    handleProtectShell(player, target, "shell", tier)
end

xi.job_utils.white_mage.castRaise = function(player, target, tier)
    return handleRaise(player, target, tier)
end

-----------------------------------
-- Ability Use Functions
-----------------------------------
xi.job_utils.white_mage.useAfflatusMisery = function(player, target, ability)
    target:delStatusEffect(xi.effect.AFFLATUS_SOLACE)
    target:delStatusEffect(xi.effect.AFFLATUS_MISERY)
    local duration = 7200 + player:getJobPointLevel(xi.jp.AFFLATUS_MISERY_EFFECT) * 60
    target:addStatusEffect(xi.effect.AFFLATUS_MISERY, 8, 0, duration)
end

xi.job_utils.white_mage.useAfflatusSolace = function(player, target, ability)
    target:delStatusEffect(xi.effect.AFFLATUS_SOLACE)
    target:delStatusEffect(xi.effect.AFFLATUS_MISERY)
    local duration = 7200 + player:getJobPointLevel(xi.jp.AFFLATUS_SOLACE_EFFECT) * 60
    target:addStatusEffect(xi.effect.AFFLATUS_SOLACE, 8, 0, duration)
end

xi.job_utils.white_mage.useAsylum = function(player, target, ability)
    local duration = 30 + player:getJobPointLevel(xi.jp.ASYLUM_EFFECT)
    target:addStatusEffect(xi.effect.ASYLUM, 3, 0, duration)
end

xi.job_utils.white_mage.useBenediction = function(player, target, ability)
    -- To Do: Benediction can remove Charm only while in Assault Mission Lamia No.13
    for i, effect in ipairs(removables) do
        if target:hasStatusEffect(effect) then
            target:delStatusEffect(effect)
        end
    end

    local heal = (target:getMaxHP() * player:getMainLvl()) / target:getMainLvl()

    local maxHeal = target:getMaxHP() - target:getHP()

    if heal > maxHeal then
        heal = maxHeal
    end

    local power = 33 + player:getJobPointLevel(xi.jp.BENEDICTION_EFFECT) --chance to remove Doom. Basing off of Holy Water?

    if target:hasStatusEffect(xi.effect.DOOM) and power > math.random(1, 100) then
        target:delStatusEffect(xi.effect.DOOM)
    end

    player:updateEnmityFromCure(target, heal)
    target:addHP(heal)
    target:wakeUp()

    return heal
end

xi.job_utils.white_mage.useDevotion = function(player, target, ability)
    -- Plus 5 percent mp recovers per extra devotion merit
    local meritBonus = player:getMerit(xi.merit.DEVOTION) - 5
    local mpPercent  = (25 + meritBonus) / 100
    local damageHP   = math.floor(player:getHP() * 0.25)

    -- If stoneskin is present, it should absorb damage
    damageHP = utils.stoneskin(player, damageHP)

    local healMP = player:getHP() * mpPercent
    healMP = utils.clamp(healMP, 0, target:getMaxMP() - target:getMP())

    damageHP = utils.stoneskin(player, damageHP)
    player:delHP(damageHP)
    target:addMP(healMP)

    return healMP
end

xi.job_utils.white_mage.useDivineCaress = function(player, target, ability)
    local duration = 60 + player:getJobPointLevel(xi.jp.DIVINE_CARESS_EFFECT)
    player:addStatusEffect(xi.effect.DIVINE_CARESS_I, 3, 0, duration)
end

xi.job_utils.white_mage.useDivineSeal = function(player, target, ability)
    local duration = 60 + player:getJobPointLevel(xi.jp.DIVINE_SEAL_EFFECT)
    player:addStatusEffect(xi.effect.DIVINE_SEAL, 100, 0, duration)
end

xi.job_utils.white_mage.useMartyr = function(player, target, ability)
    -- Plus 5 percent hp recovers per extra martyr merit
    local meritBonus = player:getMerit(xi.merit.MARTYR) - 5

    local hpPercent = (200 + meritBonus) / 100

    local damageHP = math.floor(player:getHP() * 0.25)

    --We need to capture this here because the base damage is the basis for the heal
    local healHP = damageHP * hpPercent
    healHP = utils.clamp(healHP, 0, target:getMaxHP() - target:getHP())

    -- If stoneskin is present, it should absorb damage
    damageHP = utils.stoneskin(player, damageHP)
    player:delHP(damageHP)
    target:addHP(healHP)

    return healHP
end

xi.job_utils.white_mage.useSacrosanctity = function(player, target, ability)
    local duration = 60 + player:getJobPointLevel(xi.jp.SACROSANCTITY_EFFECT)
    target:addStatusEffect(xi.effect.SACROSANCTITY, 3, 0, duration)
end
