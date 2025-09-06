-----------------------------------
-- Scholar Job Utilities
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.scholar = xi.job_utils.scholar or {}

-----------------------------------
-- Stratagems and Arts System
-----------------------------------

-- Light Arts Spells
local lightArtsSpells = {
    -- Healing Magic
    [xi.magic.spell.CURE] = true,
    [xi.magic.spell.CURE_II] = true,
    [xi.magic.spell.CURE_III] = true,
    [xi.magic.spell.CURE_IV] = true,
    [xi.magic.spell.CURE_V] = true,
    [xi.magic.spell.CURE_VI] = true,
    [xi.magic.spell.CURAGA] = true,
    [xi.magic.spell.CURAGA_II] = true,
    [xi.magic.spell.CURAGA_III] = true,
    [xi.magic.spell.CURAGA_IV] = true,
    [xi.magic.spell.CURAGA_V] = true,
    [xi.magic.spell.RAISE] = true,
    [xi.magic.spell.RAISE_II] = true,
    [xi.magic.spell.RAISE_III] = true,
    [xi.magic.spell.RERAISE] = true,
    [xi.magic.spell.RERAISE_II] = true,
    [xi.magic.spell.RERAISE_III] = true,
    
    -- Enhancing Magic
    [xi.magic.spell.PROTECT] = true,
    [xi.magic.spell.PROTECT_II] = true,
    [xi.magic.spell.PROTECT_III] = true,
    [xi.magic.spell.PROTECT_IV] = true,
    [xi.magic.spell.PROTECT_V] = true,
    [xi.magic.spell.SHELL] = true,
    [xi.magic.spell.SHELL_II] = true,
    [xi.magic.spell.SHELL_III] = true,
    [xi.magic.spell.SHELL_IV] = true,
    [xi.magic.spell.SHELL_V] = true,
    [xi.magic.spell.REGEN] = true,
    [xi.magic.spell.REGEN_II] = true,
    [xi.magic.spell.REGEN_III] = true,
    [xi.magic.spell.REGEN_IV] = true,
    [xi.magic.spell.STONESKIN] = true,
    [xi.magic.spell.AQUAVEIL] = true,
    [xi.magic.spell.BLINK] = true,
}

-- Dark Arts Spells
local darkArtsSpells = {
    -- Elemental Magic
    [xi.magic.spell.STONE] = true,
    [xi.magic.spell.STONE_II] = true,
    [xi.magic.spell.STONE_III] = true,
    [xi.magic.spell.STONE_IV] = true,
    [xi.magic.spell.STONE_V] = true,
    [xi.magic.spell.WATER] = true,
    [xi.magic.spell.WATER_II] = true,
    [xi.magic.spell.WATER_III] = true,
    [xi.magic.spell.WATER_IV] = true,
    [xi.magic.spell.WATER_V] = true,
    [xi.magic.spell.AERO] = true,
    [xi.magic.spell.AERO_II] = true,
    [xi.magic.spell.AERO_III] = true,
    [xi.magic.spell.AERO_IV] = true,
    [xi.magic.spell.AERO_V] = true,
    [xi.magic.spell.FIRE] = true,
    [xi.magic.spell.FIRE_II] = true,
    [xi.magic.spell.FIRE_III] = true,
    [xi.magic.spell.FIRE_IV] = true,
    [xi.magic.spell.FIRE_V] = true,
    [xi.magic.spell.BLIZZARD] = true,
    [xi.magic.spell.BLIZZARD_II] = true,
    [xi.magic.spell.BLIZZARD_III] = true,
    [xi.magic.spell.BLIZZARD_IV] = true,
    [xi.magic.spell.BLIZZARD_V] = true,
    [xi.magic.spell.THUNDER] = true,
    [xi.magic.spell.THUNDER_II] = true,
    [xi.magic.spell.THUNDER_III] = true,
    [xi.magic.spell.THUNDER_IV] = true,
    [xi.magic.spell.THUNDER_V] = true,
    
    -- Enfeebling Magic
    [xi.magic.spell.DIA] = true,
    [xi.magic.spell.DIA_II] = true,
    [xi.magic.spell.DIA_III] = true,
    [xi.magic.spell.BIO] = true,
    [xi.magic.spell.BIO_II] = true,
    [xi.magic.spell.BIO_III] = true,
    [xi.magic.spell.SLOW] = true,
    [xi.magic.spell.SLOW_II] = true,
    [xi.magic.spell.PARALYZE] = true,
    [xi.magic.spell.PARALYZE_II] = true,
    [xi.magic.spell.SILENCE] = true,
    [xi.magic.spell.BLIND] = true,
    [xi.magic.spell.BLIND_II] = true,
    [xi.magic.spell.SLEEP] = true,
    [xi.magic.spell.SLEEP_II] = true,
    [xi.magic.spell.SLEEPGA] = true,
    [xi.magic.spell.SLEEPGA_II] = true,
}

-----------------------------------
-- Ability Check Functions
-----------------------------------
xi.job_utils.scholar.checkTabulaRasa = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.scholar.checkLightArts = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.DARK_ARTS) then
        player:delStatusEffectSilent(xi.effect.DARK_ARTS)
    end
    
    return 0, 0
end

xi.job_utils.scholar.checkDarkArts = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.LIGHT_ARTS) then
        player:delStatusEffectSilent(xi.effect.LIGHT_ARTS)
    end
    
    return 0, 0
end

xi.job_utils.scholar.checkStratagem = function(player, target, ability)
    local stratagemCount = player:getLocalVar("Stratagem_Count")
    local maxStratagems = math.floor(player:getMainLvl() / 10) + 1
    
    if stratagemCount >= maxStratagems then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    return 0, 0
end

-----------------------------------
-- Ability Use Functions
-----------------------------------
xi.job_utils.scholar.useTabulaRasa = function(player, target, ability)
    player:addStatusEffect(xi.effect.TABULA_RASA, 1, 0, 60)
end

xi.job_utils.scholar.useLightArts = function(player, target, ability)
    local jpValue = player:getJobPointLevel(xi.jp.LIGHT_ARTS_EFFECT)
    local healingBonus = 5 + jpValue
    local duration = 120 + player:getMod(xi.mod.ENHANCES_LIGHT_ARTS)
    
    player:addStatusEffect(xi.effect.LIGHT_ARTS, healingBonus, 0, duration)
    
    -- Reset stratagem count
    player:setLocalVar("Stratagem_Count", 0)
end

xi.job_utils.scholar.useDarkArts = function(player, target, ability)
    local jpValue = player:getJobPointLevel(xi.jp.DARK_ARTS_EFFECT)
    local elementalBonus = 5 + jpValue
    local duration = 120 + player:getMod(xi.mod.ENHANCES_DARK_ARTS)
    
    player:addStatusEffect(xi.effect.DARK_ARTS, elementalBonus, 0, duration)
    
    -- Reset stratagem count
    player:setLocalVar("Stratagem_Count", 0)
end

xi.job_utils.scholar.useAddendum = function(player, target, ability, addendumType)
    local duration = 60 + player:getMod(xi.mod.ADDENDUM_DURATION)
    
    if addendumType == "white" then
        player:addStatusEffect(xi.effect.ADDENDUM_WHITE, 1, 0, duration)
    elseif addendumType == "black" then
        player:addStatusEffect(xi.effect.ADDENDUM_BLACK, 1, 0, duration)
    end
end

-----------------------------------
-- Stratagem Functions
-----------------------------------
xi.job_utils.scholar.useAccession = function(player, target, ability)
    local duration = 60 + player:getMod(xi.mod.STRATAGEM_DURATION)
    player:addStatusEffect(xi.effect.ACCESSION, 1, 0, duration)
    xi.job_utils.scholar.incrementStratagemCount(player)
end

xi.job_utils.scholar.useManifesto = function(player, target, ability)
    local duration = 60 + player:getMod(xi.mod.STRATAGEM_DURATION)
    player:addStatusEffect(xi.effect.MANIFESTATION, 1, 0, duration)
    xi.job_utils.scholar.incrementStratagemCount(player)
end

xi.job_utils.scholar.useAlacrity = function(player, target, ability)
    local duration = 60 + player:getMod(xi.mod.STRATAGEM_DURATION)
    player:addStatusEffect(xi.effect.ALACRITY, 50, 0, duration) -- 50% cast time reduction
    xi.job_utils.scholar.incrementStratagemCount(player)
end

xi.job_utils.scholar.useParsimony = function(player, target, ability)
    local duration = 60 + player:getMod(xi.mod.STRATAGEM_DURATION)
    player:addStatusEffect(xi.effect.PARSIMONY, 50, 0, duration) -- 50% MP cost reduction
    xi.job_utils.scholar.incrementStratagemCount(player)
end

xi.job_utils.scholar.usePenury = function(player, target, ability)
    local duration = 60 + player:getMod(xi.mod.STRATAGEM_DURATION)
    player:addStatusEffect(xi.effect.PENURY, 50, 0, duration) -- 50% MP cost reduction
    xi.job_utils.scholar.incrementStratagemCount(player)
end

xi.job_utils.scholar.useCelerity = function(player, target, ability)
    local duration = 60 + player:getMod(xi.mod.STRATAGEM_DURATION)
    player:addStatusEffect(xi.effect.CELERITY, 50, 0, duration) -- 50% cast time reduction
    xi.job_utils.scholar.incrementStratagemCount(player)
end

xi.job_utils.scholar.useRapture = function(player, target, ability)
    local duration = 60 + player:getMod(xi.mod.STRATAGEM_DURATION)
    player:addStatusEffect(xi.effect.RAPTURE, 1, 0, duration)
    xi.job_utils.scholar.incrementStratagemCount(player)
end

xi.job_utils.scholar.useEbullience = function(player, target, ability)
    local duration = 60 + player:getMod(xi.mod.STRATAGEM_DURATION)
    player:addStatusEffect(xi.effect.EBULLIENCE, 1, 0, duration)
    xi.job_utils.scholar.incrementStratagemCount(player)
end

-----------------------------------
-- Helper Functions
-----------------------------------
xi.job_utils.scholar.incrementStratagemCount = function(player)
    local currentCount = player:getLocalVar("Stratagem_Count")
    player:setLocalVar("Stratagem_Count", currentCount + 1)
end

xi.job_utils.scholar.isLightArtsSpell = function(spellID)
    return lightArtsSpells[spellID] or false
end

xi.job_utils.scholar.isDarkArtsSpell = function(spellID)
    return darkArtsSpells[spellID] or false
end

xi.job_utils.scholar.getArtsBonus = function(player, spellID)
    local bonus = 0
    
    if xi.job_utils.scholar.isLightArtsSpell(spellID) and player:hasStatusEffect(xi.effect.LIGHT_ARTS) then
        local effect = player:getStatusEffect(xi.effect.LIGHT_ARTS)
        bonus = effect:getPower() or 5
    elseif xi.job_utils.scholar.isDarkArtsSpell(spellID) and player:hasStatusEffect(xi.effect.DARK_ARTS) then
        local effect = player:getStatusEffect(xi.effect.DARK_ARTS)
        bonus = effect:getPower() or 5
    end
    
    return bonus
end

-----------------------------------
-- Magic Enhancement Functions
-----------------------------------
xi.job_utils.scholar.onCastSpell = function(player, target, spell)
    local spellID = spell:getID()
    local bonus = xi.job_utils.scholar.getArtsBonus(player, spellID)
    
    -- Apply arts bonus
    if bonus > 0 then
        if xi.job_utils.scholar.isLightArtsSpell(spellID) then
            -- Enhance healing/enhancing magic
            if spell:canTargetEnemy() == false then
                spell:setMsg(xi.msg.basic.MAGIC_RECOVERS_HP)
                return bonus
            end
        elseif xi.job_utils.scholar.isDarkArtsSpell(spellID) then
            -- Enhance damage/enfeebling magic
            if spell:canTargetEnemy() == true then
                return bonus
            end
        end
    end
    
    return 0
end

return xi.job_utils.scholar