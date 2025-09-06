-----------------------------------
-- Blue Mage Job Utilities
-----------------------------------
-- Comprehensive Blue Mage system implementation
-- Features: Azure Lore, spell learning, Clear Mind, set bonuses
-----------------------------------

require("scripts/globals/job_utils/job_utils_base")
require("scripts/globals/magic")
require("scripts/globals/bluemagic")

xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.blue_mage = {}

-----------------------------------
-- Blue Magic Spell Learning System
-----------------------------------

-- Blue Magic spells that can be learned
local learnableSpells = {
    -- Physical type spells
    [xi.magic.spell.FOOT_KICK] = { type = 'physical', setPoints = 1, level = 1 },
    [xi.magic.spell.POWER_ATTACK] = { type = 'physical', setPoints = 2, level = 4 },
    [xi.magic.spell.QUEASYSHROOM] = { type = 'magical', setPoints = 1, level = 8 },
    [xi.magic.spell.BATTLE_DANCE] = { type = 'physical', setPoints = 3, level = 12 },
    [xi.magic.spell.HEAD_BUTT] = { type = 'physical', setPoints = 1, level = 16 },
    [xi.magic.spell.HEAL_BREATH] = { type = 'breath', setPoints = 2, level = 20 },
    [xi.magic.spell.COCOON] = { type = 'magical', setPoints = 1, level = 24 },
    [xi.magic.spell.WILD_OATS] = { type = 'physical', setPoints = 2, level = 28 },
    [xi.magic.spell.POLLEN] = { type = 'magical', setPoints = 1, level = 32 },
    [xi.magic.spell.CURSED_SPHERE] = { type = 'magical', setPoints = 3, level = 36 },
    [xi.magic.spell.SHEEP_SONG] = { type = 'magical', setPoints = 2, level = 40 },
    [xi.magic.spell.DIMENSIONAL_DEATH] = { type = 'magical', setPoints = 4, level = 44 },
    [xi.magic.spell.BLANK_GAZE] = { type = 'magical', setPoints = 1, level = 48 },
    [xi.magic.spell.MAGIC_FRUIT] = { type = 'magical', setPoints = 3, level = 52 },
    [xi.magic.spell.UPPERCUT] = { type = 'physical', setPoints = 1, level = 56 },
    [xi.magic.spell.TERROR_TOUCH] = { type = 'magical', setPoints = 2, level = 60 },
    [xi.magic.spell.MANDIBULAR_BITE] = { type = 'physical', setPoints = 2, level = 64 },
    [xi.magic.spell.METALLIC_BODY] = { type = 'magical', setPoints = 1, level = 68 },
    [xi.magic.spell.MYSTERIOUS_LIGHT] = { type = 'magical', setPoints = 3, level = 72 },
    [xi.magic.spell.CANNONBALL] = { type = 'physical', setPoints = 3, level = 75 },
}

-- Set bonus combinations for spell traits
local setBonuses = {
    [1] = { -- Attack Bonus
        spells = { xi.magic.spell.POWER_ATTACK, xi.magic.spell.UPPERCUT },
        trait = xi.jobTrait.ATTACK_BONUS,
        value = 10
    },
    [2] = { -- Magic Attack Bonus
        spells = { xi.magic.spell.MYSTERIOUS_LIGHT, xi.magic.spell.CURSED_SPHERE },
        trait = xi.jobTrait.MAGIC_ATK_BONUS,
        value = 5
    },
    [3] = { -- Store TP
        spells = { xi.magic.spell.BATTLE_DANCE, xi.magic.spell.WILD_OATS },
        trait = xi.jobTrait.STORE_TP,
        value = 5
    },
    [4] = { -- Resist Sleep
        spells = { xi.magic.spell.SHEEP_SONG, xi.magic.spell.BLANK_GAZE },
        trait = xi.jobTrait.RESIST_SLEEP,
        value = 1
    },
    [5] = { -- Clear Mind
        spells = { xi.magic.spell.MAGIC_FRUIT, xi.magic.spell.HEAL_BREATH, xi.magic.spell.POLLEN },
        trait = xi.jobTrait.CLEAR_MIND,
        value = 1
    },
}

-- Check if player can learn a blue magic spell
function xi.job_utils.blue_mage.canLearnSpell(player, spellId, caster)
    if player:getMainJob() ~= xi.job.BLU and player:getSubJob() ~= xi.job.BLU then
        return false
    end
    
    local spellInfo = learnableSpells[spellId]
    if not spellInfo then
        return false
    end
    
    -- Check level requirement
    local bluLevel = player:getJobLevel(xi.job.BLU)
    if bluLevel < spellInfo.level then
        return false
    end
    
    -- Check if already learned
    if player:hasSpell(spellId) then
        return false
    end
    
    -- Random chance to learn (base 25%, modified by Azure Lore)
    local learnChance = 0.25
    if player:hasStatusEffect(xi.effect.AZURE_LORE) then
        learnChance = 1.0 -- 100% chance during Azure Lore
    end
    
    return math.random() < learnChance
end

-- Learn a blue magic spell
function xi.job_utils.blue_mage.learnSpell(player, spellId)
    if not xi.job_utils.blue_mage.canLearnSpell(player, spellId) then
        return false
    end
    
    player:addSpell(spellId)
    player:messageBasic(xi.msg.basic.LEARNS_SPELL, spellId)
    
    -- Check and apply set bonuses
    xi.job_utils.blue_mage.checkSetBonuses(player)
    
    return true
end

-- Enhanced job change handling
function xi.job_utils.blue_mage.onJobChange(player, previousJob)
    if player:getMainJob() == xi.job.BLU then
        -- Apply base Blue Mage traits
        player:addJobTrait(xi.jobTrait.RESIST_SLEEP, xi.job.BLU)
        
        -- Recalculate set bonuses
        xi.job_utils.blue_mage.checkSetBonuses(player)
    end
end

-- Calculate maximum spell points based on level
function xi.job_utils.blue_mage.getMaxSetPoints(player)
    local level = player:getJobLevel(xi.job.BLU)
    local basePoints = math.floor(level / 2) + 5
    local merits = player:getMerit(xi.merit.BLUE_MAGIC_POINTS) or 0
    local jpBonus = player:getJobPointLevel(xi.jp.BLUE_MAGIC_POINT_BONUS) or 0
    
    return math.min(55, basePoints + merits + jpBonus)
end

-- Enhanced spell setting with validation
function xi.job_utils.blue_mage.canSetBlueSpell(player, spellId, slotToPut)
    if not player:hasSpell(spellId) then
        return false
    end
    
    local spellInfo = learnableSpells[spellId]
    if not spellInfo then
        return false
    end
    
    -- Calculate current point usage
    local currentPoints = 0
    for i = 1, 20 do -- Max 20 settable spells
        local setSpell = player:getBlueSpell(i)
        if setSpell and setSpell ~= 0 and i ~= slotToPut then
            local setSpellInfo = learnableSpells[setSpell]
            if setSpellInfo then
                currentPoints = currentPoints + setSpellInfo.setPoints
            end
        end
    end
    
    -- Check if adding this spell would exceed points limit
    local maxPoints = xi.job_utils.blue_mage.getMaxSetPoints(player)
    return currentPoints + spellInfo.setPoints <= maxPoints
end

-- Set a blue magic spell in specified slot
function xi.job_utils.blue_mage.setBlueSpell(player, spellId, slotToPut)
    if not xi.job_utils.blue_mage.canSetBlueSpell(player, spellId, slotToPut) then
        return false
    end
    
    player:setBlueSpell(slotToPut, spellId)
    xi.job_utils.blue_mage.checkSetBonuses(player)
    
    return true
end

-- Check and apply set bonuses based on equipped spells
function xi.job_utils.blue_mage.checkSetBonuses(player)
    if player:getMainJob() ~= xi.job.BLU then
        return
    end
    
    -- Get currently set spells
    local setSpells = {}
    for i = 1, 20 do
        local spellId = player:getBlueSpell(i)
        if spellId and spellId ~= 0 then
            setSpells[spellId] = true
        end
    end
    
    -- Check each set bonus
    for _, bonus in pairs(setBonuses) do
        local hasAllSpells = true
        for _, requiredSpell in ipairs(bonus.spells) do
            if not setSpells[requiredSpell] then
                hasAllSpells = false
                break
            end
        end
        
        if hasAllSpells then
            player:addJobTrait(bonus.trait, xi.job.BLU, bonus.value)
        else
            player:delJobTrait(bonus.trait, xi.job.BLU)
        end
    end
end

-----------------------------------
-- Azure Lore Ability Functions
-----------------------------------

function xi.job_utils.blue_mage.checkAzureLore(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

function xi.job_utils.blue_mage.useAzureLore(player, target, ability, action)
    local duration = 30 + player:getJobPointLevel(xi.jp.AZURE_LORE_EFFECT)
    player:addStatusEffect(xi.effect.AZURE_LORE, 1, 0, duration)
end

-----------------------------------
-- Clear Mind Enhancement
-----------------------------------

-- Enhanced Clear Mind calculation for Blue Mage
function xi.job_utils.blue_mage.getClearMindBonus(player)
    local clearMindLevel = 0
    
    -- Check set bonuses for Clear Mind
    for _, bonus in pairs(setBonuses) do
        if bonus.trait == xi.jobTrait.CLEAR_MIND then
            local setSpells = {}
            for i = 1, 20 do
                local spellId = player:getBlueSpell(i)
                if spellId and spellId ~= 0 then
                    setSpells[spellId] = true
                end
            end
            
            local hasAllSpells = true
            for _, requiredSpell in ipairs(bonus.spells) do
                if not setSpells[requiredSpell] then
                    hasAllSpells = false
                    break
                end
            end
            
            if hasAllSpells then
                clearMindLevel = clearMindLevel + bonus.value
            end
        end
    end
    
    -- Apply Clear Mind MP regeneration bonus
    if clearMindLevel > 0 then
        local mpBonus = math.floor(player:getMaxMP() * (clearMindLevel * 0.02)) -- 2% per level
        return mpBonus
    end
    
    return 0
end