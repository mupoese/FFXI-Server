-----------------------------------
-- Blue Mage Job Utilities
-----------------------------------
require('scripts/globals/utils')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.blue_mage = xi.job_utils.blue_mage or {}
-----------------------------------

-----------------------------------
-- Ability Check Functions
-----------------------------------

xi.job_utils.blue_mage.checkAzureLore = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))

    return 0, 0
end

xi.job_utils.blue_mage.checkBurstAffinity = function(player, target, ability)
    return 0, 0
end

xi.job_utils.blue_mage.checkChainAffinity = function(player, target, ability)
    return 0, 0
end

xi.job_utils.blue_mage.checkDiffusion = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.DIFFUSION) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end

    return 0, 0
end

xi.job_utils.blue_mage.checkEfflux = function(player, target, ability)
    return 0, 0
end

xi.job_utils.blue_mage.checkUnbridledWisdom = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.blue_mage.checkUnbridledLearning = function(player, target, ability)
    return 0, 0
end

-----------------------------------
-- Ability Use Functions
-----------------------------------

xi.job_utils.blue_mage.useAzureLore = function(player, target, ability, action)
    player:addStatusEffect(xi.effect.AZURE_LORE, 1, 0, 30)
end

xi.job_utils.blue_mage.useBurstAffinity = function(player, target, ability, action)
    player:addStatusEffect(xi.effect.BURST_AFFINITY, 1, 0, 30)
    return xi.effect.BURST_AFFINITY
end

xi.job_utils.blue_mage.useChainAffinity = function(player, target, ability, action)
    player:addStatusEffect(xi.effect.CHAIN_AFFINITY, 1, 0, 30)
    return xi.effect.CHAIN_AFFINITY
end

xi.job_utils.blue_mage.useDiffusion = function(player, target, ability, action)
    player:addStatusEffect(xi.effect.DIFFUSION, 1, 0, 60)
    return xi.effect.DIFFUSION
end

xi.job_utils.blue_mage.useEfflux = function(player, target, ability, action)
    player:addStatusEffect(xi.effect.EFFLUX, 16, 1, 60)
end

xi.job_utils.blue_mage.useUnbridledWisdom = function(player, target, ability, action)
    target:addStatusEffect(xi.effect.UNBRIDLED_WISDOM, 16, 1, 30)
end

xi.job_utils.blue_mage.useUnbridledLearning = function(player, target, ability, action)
    target:addStatusEffect(xi.effect.UNBRIDLED_LEARNING, 16, 1, 60)
end

-----------------------------------
-- Phase 3 Enhancement: Advanced Blue Magic Utilities
-----------------------------------

-- Enhanced Blue Magic set point validation for retail accuracy
xi.job_utils.blue_mage.validateSetPoints = function(player, spellToAdd, slotToPut)
    if not player or not spellToAdd then
        return false
    end
    
    local currentPoints = 0
    local maxPoints = xi.job_utils.blue_mage.getMaxSetPoints(player)
    
    -- Calculate current used points (excluding the slot we're replacing)
    for slot = 0, 19 do
        if player:getSetBlueSpell(slot) ~= 0 and slot ~= slotToPut then
            local spellId = player:getSetBlueSpell(slot) + 0x200
            local spell = GetSpell(spellId)
            if spell then
                currentPoints = currentPoints + spell:getSetPoints()
            end
        end
    end
    
    -- Add the new spell's points
    local newSpellPoints = spellToAdd:getSetPoints()
    local totalPoints = currentPoints + newSpellPoints
    
    return totalPoints <= maxPoints, totalPoints, maxPoints
end

-- Calculate maximum set points based on level and traits
xi.job_utils.blue_mage.getMaxSetPoints = function(player)
    local bluLevel = 0
    
    if player:getMainJob() == xi.job.BLU then
        bluLevel = player:getMainLvl()
    elseif player:getSubJob() == xi.job.BLU then
        bluLevel = player:getSubLvl()
    else
        return 0
    end
    
    -- Base set points progression (retail accurate)
    local basePoints = 0
    if bluLevel >= 99 then
        basePoints = 60 -- Maximum at level 99
    elseif bluLevel >= 75 then
        basePoints = 55 + math.floor((bluLevel - 75) / 5)
    elseif bluLevel >= 50 then
        basePoints = 45 + math.floor((bluLevel - 50) / 2.5)
    elseif bluLevel >= 25 then
        basePoints = 30 + math.floor((bluLevel - 25) / 1.67)
    else
        basePoints = 15 + math.floor(bluLevel / 1.67)
    end
    
    -- Trait bonuses for set points
    local traitBonus = player:getMod(xi.mod.BLUE_POINTS) or 0
    
    -- Job point bonuses
    local jpBonus = 0
    if player:getMainJob() == xi.job.BLU then
        jpBonus = player:getJobPointLevel(xi.jp.BLUE_MAGIC_POINT_BONUS) * 2 -- 2 points per level
    end
    
    return basePoints + traitBonus + jpBonus
end

-- Enhanced spell learning validation
xi.job_utils.blue_mage.canLearnSpell = function(player, spellId, mobFamily)
    if not player or player:getMainJob() ~= xi.job.BLU then
        return false
    end
    
    -- Check if spell is already learned
    if player:hasSpell(spellId) then
        return false
    end
    
    local spell = GetSpell(spellId)
    if not spell then
        return false
    end
    
    -- Level requirement check
    local requiredLevel = spell:getJob(xi.job.BLU)
    local bluLevel = player:getMainLvl()
    
    if bluLevel < requiredLevel then
        return false
    end
    
    -- Mob family learning check (some spells can only be learned from specific families)
    local spellMobFamily = spell:getMobFamily()
    if spellMobFamily and spellMobFamily ~= 0 and mobFamily ~= spellMobFamily then
        return false
    end
    
    -- Learning rate based on level difference (retail accurate)
    local levelDiff = bluLevel - requiredLevel
    local baseLearnRate = 10 -- 10% base rate
    
    if levelDiff >= 20 then
        baseLearnRate = 50 -- Much higher rate when significantly overleveled
    elseif levelDiff >= 10 then
        baseLearnRate = 30 -- Higher rate when overleveled
    elseif levelDiff >= 5 then
        baseLearnRate = 20 -- Moderate rate
    end
    
    -- Trait bonuses for learning rate
    local learningBonus = player:getMod(xi.mod.BLUE_LEARNING_CHANCE) or 0
    local finalLearnRate = baseLearnRate + learningBonus
    
    return math.random(1, 100) <= finalLearnRate
end

-- Enhanced trait application for Blue Magic
xi.job_utils.blue_mage.applyBlueTraits = function(player)
    if not player or player:getMainJob() ~= xi.job.BLU then
        return
    end
    
    -- Reset all blue traits first
    xi.job_utils.blue_mage.clearBlueTraits(player)
    
    local traitMap = {}
    
    -- Calculate traits from set spells
    for slot = 0, 19 do
        local spellId = player:getSetBlueSpell(slot)
        if spellId ~= 0 then
            local spell = GetSpell(spellId + 0x200)
            if spell then
                local traits = spell:getTraits()
                for _, trait in pairs(traits) do
                    traitMap[trait.trait] = (traitMap[trait.trait] or 0) + trait.value
                end
            end
        end
    end
    
    -- Apply accumulated traits
    for traitType, traitValue in pairs(traitMap) do
        player:addTrait(traitType, traitValue)
    end
end

-- Clear all blue magic traits
xi.job_utils.blue_mage.clearBlueTraits = function(player)
    -- List of all blue magic traits that need to be cleared
    local blueTraits = {
        xi.trait.ATTACK_BONUS,
        xi.trait.DEFENSE_BONUS,
        xi.trait.MAGIC_ATK_BONUS,
        xi.trait.MAGIC_DEF_BONUS,
        xi.trait.AUTO_REFRESH,
        xi.trait.AUTO_REGEN,
        xi.trait.RESIST_SLEEP,
        xi.trait.RESIST_SILENCE,
        xi.trait.RESIST_PARALYSIS,
        xi.trait.RESIST_BLIND,
        xi.trait.RESIST_SLOW,
        xi.trait.DUAL_WIELD,
        xi.trait.CONSERVE_MP,
    }
    
    for _, trait in pairs(blueTraits) do
        player:delTrait(trait)
    end
end
