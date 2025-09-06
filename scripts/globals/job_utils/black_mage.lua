-----------------------------------
-- Black Mage Job Utilities
-----------------------------------
require('scripts/globals/utils')
require('scripts/globals/jobpoints')
require('scripts/globals/magic')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.black_mage = xi.job_utils.black_mage or {}

-----------------------------------
-- Magic Enhancement Functions
-----------------------------------
function getElementalSealBonus(player, element)
    if player:hasStatusEffect(xi.effect.ELEMENTAL_SEAL) then
        return 100 -- 100% magic accuracy bonus
    end
    return 0
end

function getAncientMagicBonus(player, spellId)
    -- Ancient magic spells get enhanced damage based on merits and job points
    local meritBonus = player:getMerit(xi.merit.ANCIENT_MAGIC)
    local jpBonus = player:getJobPointLevel(xi.jp.ANCIENT_MAGIC_EFFECT)
    return meritBonus + jpBonus
end

function calculateManaFont(player)
    local duration = 60 + player:getJobPointLevel(xi.jp.MANAFONT_EFFECT)
    return duration
end

function handleElementalMagic(player, target, spell)
    local damage = spell:getBaseDamage()
    
    -- Apply Elemental Seal bonus
    if player:hasStatusEffect(xi.effect.ELEMENTAL_SEAL) then
        damage = damage * 1.5
    end
    
    -- Apply job point bonuses
    damage = damage + player:getJobPointLevel(xi.jp.ELEMENTAL_MAGIC_EFFECT)
    
    return damage
end

-----------------------------------
-- Ability Check Functions
-----------------------------------
xi.job_utils.black_mage.checkManafont = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.black_mage.checkSubtleSorcery = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.black_mage.checkElementalSeal = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.ELEMENTAL_SEAL) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

xi.job_utils.black_mage.checkManaWall = function(player, target, ability)
    if player:getMP() < player:getMaxMP() * 0.2 then
        return xi.msg.basic.NOT_ENOUGH_MP, 0
    end
    return 0, 0
end

-----------------------------------
-- Ancient Magic System
-----------------------------------
xi.job_utils.black_mage.handleAncientMagic = function(player, target, spell)
    local spellId = spell:getID()
    local baseDamage = spell:getBaseDamage()
    
    -- Check for Ancient Magic merits and job points
    local ancientBonus = getAncientMagicBonus(player, spellId)
    baseDamage = baseDamage + ancientBonus
    
    -- Apply damage multipliers for specific ancient spells
    if spellId == xi.magic.spell.FLARE then
        baseDamage = baseDamage * 1.2
    elseif spellId == xi.magic.spell.FREEZE then
        baseDamage = baseDamage * 1.2
    elseif spellId == xi.magic.spell.TORNADO then
        baseDamage = baseDamage * 1.2
    elseif spellId == xi.magic.spell.QUAKE then
        baseDamage = baseDamage * 1.2
    elseif spellId == xi.magic.spell.BURST then
        baseDamage = baseDamage * 1.2
    elseif spellId == xi.magic.spell.FLOOD then
        baseDamage = baseDamage * 1.2
    end
    
    return baseDamage
end

-----------------------------------
-- Ability Use Functions
-----------------------------------
xi.job_utils.black_mage.useCascade = function(player, target, ability)
    local duration = 60 + player:getJobPointLevel(xi.jp.CASCADE_EFFECT)
    player:addStatusEffect(xi.effect.CASCADE, 2, 0, duration)
end

xi.job_utils.black_mage.useElementalSeal = function(player, target, ability)
    local duration = 60 + player:getJobPointLevel(xi.jp.ELEMENTAL_SEAL_EFFECT)
    player:addStatusEffect(xi.effect.ELEMENTAL_SEAL, 100, 0, duration)
end

xi.job_utils.black_mage.useEnmityDouse = function(player, target, ability)
    if target:isMob() then
        target:setCE(player, 1)
        target:setVE(player, 0)
    end
    
    -- Job point enhancement
    local jpBonus = player:getJobPointLevel(xi.jp.ENMITY_DOUSE_EFFECT)
    if jpBonus > 0 and target:isMob() then
        target:addStatusEffect(xi.effect.AMNESIA, 1, 0, 30 + jpBonus * 5)
    end
end

xi.job_utils.black_mage.useManafont = function(player, target, ability)
    local duration = calculateManaFont(player)
    player:addStatusEffect(xi.effect.MANAFONT, 1, 0, duration)
end

xi.job_utils.black_mage.useManaWall = function(player, target, ability)
    local mpCost = math.floor(player:getMaxMP() * 0.2)
    player:delMP(mpCost)
    
    local duration = 300 + player:getJobPointLevel(xi.jp.MANA_WALL_EFFECT) * 30
    player:addStatusEffect(xi.effect.MANA_WALL, 3, 0, duration)
end

xi.job_utils.black_mage.useManawell = function(player, target, ability)
    local duration = 60 + player:getJobPointLevel(xi.jp.MANAWELL_EFFECT)
    target:addStatusEffect(xi.effect.MANAWELL, 2, 0, duration)
end

xi.job_utils.black_mage.useSubtleSorcery = function(player, target, ability)
    local duration = 60 + player:getJobPointLevel(xi.jp.SUBTLE_SORCERY_EFFECT)
    player:addStatusEffect(xi.effect.SUBTLE_SORCERY, 2, 0, duration)
end

-----------------------------------
-- Elemental Magic Enhancement
-----------------------------------
xi.job_utils.black_mage.enhanceElementalMagic = function(player, spell, damage)
    -- Apply various Black Mage enhancements
    local finalDamage = damage
    
    -- Elemental Seal enhancement
    finalDamage = finalDamage + getElementalSealBonus(player, spell:getElement())
    
    -- Job point bonuses
    finalDamage = finalDamage + player:getJobPointLevel(xi.jp.ELEMENTAL_MAGIC_EFFECT)
    
    -- Occult Acumen trait for melee enhancement
    if player:hasStatusEffect(xi.effect.MANAFONT) then
        finalDamage = finalDamage * 1.5
    end
    
    return finalDamage
end
