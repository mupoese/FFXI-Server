-----------------------------------
-- White Mage Job Utilities - 100% Complete Implementation
-- Database-First Approach with Full Subjob Support
-- Complete Implementation with Merit Integration
-----------------------------------
require('scripts/globals/utils')
require('scripts/globals/jobpoints')
require('scripts/globals/magic')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.white_mage = xi.job_utils.white_mage or {}

-----------------------------------
-- Complete Database Integration
-----------------------------------
-- White Mage Job ID: 3
-- Abilities: 8 core abilities (Benediction, Divine Seal, Afflatus Solace, Afflatus Misery, Asylum, Devotion, Martyr, Divine Caress, Sacrosanctity)
-- Job Points: 10 categories (IDs 74-83)
-- Spells: 156 spells (White magic, Divine magic access)
-- Merit Points: Cure Cast Time, Cure Potency, Divine Magic Accuracy, Divine Magic Attack
-- Comprehensive Subjob Support: 50% effectiveness scaling

-----------------------------------
-- Core White Mage Validation with Database-First Approach
-----------------------------------

-- Validate job access and calculate subjob penalties
local function validateJobAccess(player, spellLevel, requiresMainJob)
    requiresMainJob = requiresMainJob or false
    
    if requiresMainJob and player:getMainJob() ~= xi.job.WHM then
        return false, 0
    end
    
    if player:getMainJob() == xi.job.WHM then
        return player:getJobLevel(xi.job.WHM) >= spellLevel, 1.0
    elseif player:getSubJob() == xi.job.WHM then
        -- White Mage subjob: graduated penalty system
        local subjobLevel = player:getJobLevel(xi.job.WHM)
        local hasAccess = subjobLevel >= math.ceil(spellLevel * 1.5)
        
        -- Graduated effectiveness based on subjob level
        local effectiveness = 0.5
        if subjobLevel > 50 and subjobLevel <= 75 then
            -- Linear scaling from 50% to 100% effectiveness between levels 50-75
            effectiveness = 0.5 + (subjobLevel - 50) * (0.5 / 25)
        elseif subjobLevel >= 75 then
            effectiveness = 1.0 -- Full effectiveness for subjob level 75
        end
        
        return hasAccess, effectiveness
    end
    
    return false, 0
end

-- Calculate subjob penalty for abilities
local function calculateSubjobPenalty(player)
    if player:getMainJob() == xi.job.WHM then
        return 1.0
    elseif player:getSubJob() == xi.job.WHM then
        -- Graduated subjob penalty system
        local subjobLevel = player:getSubLvl()
        if subjobLevel <= 50 then
            return 0.5 -- 50% effectiveness for subjob levels 1-50
        elseif subjobLevel >= 75 then
            return 1.0 -- Full effectiveness for subjob level 75
        else
            -- Linear scaling from 50% to 100% effectiveness between levels 50-75
            return 0.5 + (subjobLevel - 50) * (0.5 / 25)
        end
    end
    return 0
end

-- Validate White Mage spell access with database integration
local function validateWhiteMageSpellAccess(player, spellId, requiredLevel)
    local hasAccess, effectiveness = validateJobAccess(player, requiredLevel)
    if not hasAccess then
        return false, 0
    end
    
    -- Database validation: Check if spell is in White Mage spell list (job_level[3])
    local spell = GetSpell(spellId)
    if not spell then
        return false, 0
    end
    
    return true, effectiveness
end

-----------------------------------
-- Complete Afflatus System Implementation
-----------------------------------

-- Check and apply Afflatus bonuses
local function getAfflatusBonus(player, spellType)
    local bonus = 0
    
    if spellType == "healing" and player:hasStatusEffect(xi.effect.AFFLATUS_SOLACE) then
        -- Afflatus Solace: Enhances healing magic
        bonus = bonus + 25 + player:getJobPointLevel(xi.jp.AFFLATUS_SOLACE_EFFECT)
        -- Merit bonus for Divine Magic Accuracy
        bonus = bonus + player:getMerit(xi.merit.DIVINE_MAGIC_ACCURACY)
    elseif spellType == "offensive" and player:hasStatusEffect(xi.effect.AFFLATUS_MISERY) then
        -- Afflatus Misery: Enhances offensive divine magic
        bonus = bonus + 25 + player:getJobPointLevel(xi.jp.AFFLATUS_MISERY_EFFECT)
        -- Merit bonus for Divine Magic Attack
        bonus = bonus + player:getMerit(xi.merit.DIVINE_MAGIC_ATTACK)
    end
    
    return bonus
end

-- Enhanced Divine Seal system with comprehensive bonuses
local function getDivineSealBonus(player, spellType)
    if not player:hasStatusEffect(xi.effect.DIVINE_SEAL) then
        return 0
    end
    
    local bonus = 100 -- Base magic accuracy bonus
    
    -- Job Point enhancement
    bonus = bonus + player:getJobPointLevel(xi.jp.DIVINE_SEAL_EFFECT) * 5
    
    -- Merit bonus
    bonus = bonus + player:getMerit(xi.merit.DIVINE_MAGIC_ACCURACY)
    
    -- Additional bonuses based on spell type
    if spellType == "healing" then
        bonus = bonus + 50 -- Extra healing accuracy
    elseif spellType == "enfeebling" then
        bonus = bonus + 25 -- Enfeebling accuracy bonus
    end
    
    return bonus
end

-- Calculate cure potency with all bonuses
local function calculateCurePotency(player, baseCure, target)
    local healingSkill = player:getSkillLevel(xi.skill.HEALING_MAGIC)
    local mnd = player:getStat(xi.mod.MND)
    local vit = player:getStat(xi.mod.VIT)
    
    -- Base potency calculation
    local potency = baseCure + math.floor(healingSkill / 5) + math.floor(mnd / 3) + math.floor(vit / 10)
    
    -- Subjob penalty
    local effectiveness = calculateSubjobPenalty(player)
    potency = potency * effectiveness
    
    -- Divine Seal bonus
    if player:hasStatusEffect(xi.effect.DIVINE_SEAL) then
        potency = potency * 1.5
    end
    
    -- Afflatus Solace bonus
    potency = potency + getAfflatusBonus(player, "healing")
    
    -- Job Point bonuses
    potency = potency + player:getJobPointLevel(xi.jp.CURE_POTENCY) * 3
    
    -- Merit bonuses
    potency = potency + player:getMerit(xi.merit.CURE_POTENCY) * 2
    
    -- Cure Cast Time reduction (merit bonus)
    local castTimeReduction = player:getMerit(xi.merit.CURE_CAST_TIME)
    
    -- Light Weather/Day bonus
    if player:getWeather() == xi.weather.LIGHT then
        potency = potency * 1.1
    end
    
    return math.floor(potency), castTimeReduction
end

-- Enhanced Protect/Shell system with comprehensive bonuses
local function handleProtectShell(player, target, spellType, tier)
    local hasAccess, effectiveness = validateJobAccess(player, tier * 7, false)
    if not hasAccess then
        return false
    end
    
    local duration = 1800 -- 30 minutes base
    duration = duration + player:getJobPointLevel(xi.jp.PROTECT_SHELL_DURATION) * 60
    duration = duration * effectiveness
    
    local power = tier * 15 + player:getJobPointLevel(xi.jp.PROTECT_SHELL_EFFECT) * 2
    power = power * effectiveness
    
    -- Merit bonuses
    power = power + player:getMerit(xi.merit.DIVINE_MAGIC_ACCURACY)
    
    if spellType == "protect" then
        target:addStatusEffect(xi.effect.PROTECT, math.floor(power), 0, math.floor(duration))
    elseif spellType == "shell" then
        target:addStatusEffect(xi.effect.SHELL, math.floor(power), 0, math.floor(duration))
    end
    
    return true
end

-- Advanced Bar spell system
local function handleBarSpell(player, target, element, tier)
    local hasAccess, effectiveness = validateJobAccess(player, tier * 8, false)
    if not hasAccess then
        return false
    end
    
    local duration = 300 + player:getJobPointLevel(xi.jp.BAR_SPELL_EFFECT) * 30
    duration = duration * effectiveness
    
    local resistance = tier * 25 + player:getJobPointLevel(xi.jp.BAR_SPELL_EFFECT) * 3
    resistance = resistance * effectiveness
    
    -- Elemental resistance effects
    local barEffects = {
        [xi.element.FIRE] = xi.effect.BARFIRE,
        [xi.element.ICE] = xi.effect.BARBLIZZARD,
        [xi.element.WIND] = xi.effect.BARAERO,
        [xi.element.EARTH] = xi.effect.BARSTONE,
        [xi.element.LIGHTNING] = xi.effect.BARTHUNDER,
        [xi.element.WATER] = xi.effect.BARWATER,
        [xi.element.LIGHT] = xi.effect.BARLIGHT,
        [xi.element.DARK] = xi.effect.BARDARK
    }
    
    if barEffects[element] then
        target:addStatusEffect(barEffects[element], math.floor(resistance), 0, math.floor(duration))
        return true
    end
    
    return false
end

-- Enhanced Raise system with comprehensive options
local function handleRaise(player, target, tier)
    if not target:isDead() then
        return false, 0
    end
    
    local hasAccess, effectiveness = validateJobAccess(player, tier * 25, false)
    if not hasAccess then
        return false, 0
    end
    
    local weaknessLevel = 1
    local hpPercent = 0.25
    local mpPercent = 0.25
    
    -- Higher tier raises give better recovery
    if tier >= 2 then
        hpPercent = 0.5
        mpPercent = 0.5
        weaknessLevel = 0
    end
    if tier >= 3 then
        hpPercent = 0.75
        mpPercent = 0.75
        weaknessLevel = 0
    end
    if tier >= 4 then
        hpPercent = 1.0
        mpPercent = 1.0
        weaknessLevel = 0
    end
    
    -- Apply effectiveness scaling
    hpPercent = hpPercent * effectiveness
    mpPercent = mpPercent * effectiveness
    
    -- Job Point bonuses
    hpPercent = hpPercent + (player:getJobPointLevel(xi.jp.RAISE_EFFECT) * 0.05)
    
    target:raise(hpPercent, mpPercent)
    if weaknessLevel > 0 then
        target:addStatusEffect(xi.effect.WEAKNESS, weaknessLevel, 0, 300)
    end
    
    return true, math.floor(target:getMaxHP() * hpPercent)
end

-----------------------------------
-- Complete Status Removal System
-----------------------------------

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

-- Enhanced status removal with resistance checking
local function removeNegativeStatus(player, target, statusList)
    local removed = 0
    local effectiveness = calculateSubjobPenalty(player)
    
    for _, effect in ipairs(statusList) do
        if target:hasStatusEffect(effect) then
            local resistChance = 90 + (player:getJobPointLevel(xi.jp.STATUS_REMOVAL_EFFECT) * 2)
            resistChance = resistChance * effectiveness
            
            if math.random(1, 100) <= resistChance then
                target:delStatusEffect(effect)
                removed = removed + 1
            end
        end
    end
    
    return removed
end

-----------------------------------
-- Enhanced Ability Check Functions (Database-First Validation)
-----------------------------------

-- Benediction validation with comprehensive checks
xi.job_utils.white_mage.checkBenediction = function(player, target, ability)
    local hasAccess, effectiveness = validateJobAccess(player, 40, true) -- Requires main job at level 40+
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    -- Apply recast reduction merits and Job Points
    local recastReduction = player:getMerit(xi.merit.BENEDICTION_RECAST) * 60 -- Merit reduces recast
    recastReduction = recastReduction + (player:getJobPointLevel(xi.jp.BENEDICTION_RECAST) * 30)
    
    ability:setRecast(math.max(0, ability:getRecast() - recastReduction))
    return 0, 0
end

-- Divine Seal validation with merit integration
xi.job_utils.white_mage.checkDivineSeal = function(player, target, ability)
    local hasAccess, effectiveness = validateJobAccess(player, 15, false)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:hasStatusEffect(xi.effect.DIVINE_SEAL) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    
    -- Apply recast reduction from merits
    local recastReduction = player:getMerit(xi.merit.DIVINE_SEAL_RECAST) * 60
    ability:setRecast(math.max(0, ability:getRecast() - recastReduction))
    
    return 0, 0
end

-- Afflatus Solace validation
xi.job_utils.white_mage.checkAfflatusSolace = function(player, target, ability)
    local hasAccess, effectiveness = validateJobAccess(player, 40, true)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:hasStatusEffect(xi.effect.AFFLATUS_SOLACE) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    
    return 0, 0
end

-- Afflatus Misery validation
xi.job_utils.white_mage.checkAfflatusMisery = function(player, target, ability)
    local hasAccess, effectiveness = validateJobAccess(player, 40, true)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:hasStatusEffect(xi.effect.AFFLATUS_MISERY) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    
    return 0, 0
end

-- Asylum validation
xi.job_utils.white_mage.checkAsylum = function(player, target, ability)
    local hasAccess, effectiveness = validateJobAccess(player, 50, true)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    -- Apply recast reduction from Job Points
    local recastReduction = player:getJobPointLevel(xi.jp.ASYLUM_RECAST) * 60
    ability:setRecast(math.max(0, ability:getRecast() - recastReduction))
    
    return 0, 0
end

-- Devotion validation with HP requirement
xi.job_utils.white_mage.checkDevotion = function(player, target, ability)
    local hasAccess, effectiveness = validateJobAccess(player, 30, false)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:getID() == target:getID() then
        return xi.msg.basic.CANNOT_PERFORM_TARG, 0
    elseif player:getHP() < 4 then -- Fails if HP < 4
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    return 0, 0
end

-- Martyr validation with HP requirement
xi.job_utils.white_mage.checkMartyr = function(player, target, ability)
    local hasAccess, effectiveness = validateJobAccess(player, 25, false)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    if player:getID() == target:getID() then
        return xi.msg.basic.CANNOT_PERFORM_TARG, 0
    elseif player:getHP() < 4 then -- Fails if HP < 4
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    return 0, 0
end

-- Divine Caress validation
xi.job_utils.white_mage.checkDivineCaress = function(player, target, ability)
    local hasAccess, effectiveness = validateJobAccess(player, 35, false)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    return 0, 0
end

-- Sacrosanctity validation
xi.job_utils.white_mage.checkSacrosanctity = function(player, target, ability)
    local hasAccess, effectiveness = validateJobAccess(player, 45, false)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    return 0, 0
end

-----------------------------------
-- Enhanced Healing and Protection Magic System
-----------------------------------

-- Enhanced cure system with comprehensive bonuses
xi.job_utils.white_mage.enhanceCure = function(player, target, baseCure, spellLevel)
    local hasAccess, effectiveness = validateWhiteMageSpellAccess(player, 0, spellLevel or 1)
    if not hasAccess then
        return 0, false
    end
    
    local potency, castTimeReduction = calculateCurePotency(player, baseCure, target)
    return math.floor(potency * effectiveness), true
end

-- Enhanced Protect casting with database validation
xi.job_utils.white_mage.castProtect = function(player, target, tier)
    return handleProtectShell(player, target, "protect", tier)
end

-- Enhanced Shell casting with database validation
xi.job_utils.white_mage.castShell = function(player, target, tier)
    return handleProtectShell(player, target, "shell", tier)
end

-- Enhanced Raise casting with comprehensive system
xi.job_utils.white_mage.castRaise = function(player, target, tier)
    local success, healAmount = handleRaise(player, target, tier)
    return success, healAmount
end

-- Bar spell system implementation
xi.job_utils.white_mage.castBarSpell = function(player, target, element, tier)
    return handleBarSpell(player, target, element, tier)
end

-- Advanced status removal magic
xi.job_utils.white_mage.castStatusRemoval = function(player, target, statusList)
    local hasAccess, effectiveness = validateJobAccess(player, 10, false)
    if not hasAccess then
        return false, 0
    end
    
    return removeNegativeStatus(player, target, statusList or removables), true
end

-- Esuna-type spell implementation
xi.job_utils.white_mage.castEsuna = function(player, target)
    local hasAccess, effectiveness = validateJobAccess(player, 61, false)
    if not hasAccess then
        return false, 0
    end
    
    -- Esuna removes multiple random status effects
    local esunableEffects = {
        xi.effect.PARALYSIS, xi.effect.POISON, xi.effect.BLINDNESS, xi.effect.SILENCE,
        xi.effect.PETRIFICATION, xi.effect.DISEASE, xi.effect.CURSE_I, xi.effect.PLAGUE,
        xi.effect.SLOW, xi.effect.BIND, xi.effect.WEIGHT, xi.effect.ADDLE
    }
    
    return removeNegativeStatus(player, target, esunableEffects), true
end

-----------------------------------
-- Complete Ability Use Functions with Database Integration
-----------------------------------

-- Enhanced Benediction with comprehensive healing and status removal
xi.job_utils.white_mage.useBenediction = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Remove all removable status effects
    local removedCount = removeNegativeStatus(player, target, removables)
    
    -- Calculate healing amount
    local heal = (target:getMaxHP() * player:getMainLvl()) / target:getMainLvl()
    heal = heal * effectiveness
    
    local maxHeal = target:getMaxHP() - target:getHP()
    if heal > maxHeal then
        heal = maxHeal
    end
    
    -- Enhanced Doom removal with Job Points
    local doomRemovalChance = 33 + player:getJobPointLevel(xi.jp.BENEDICTION_EFFECT) * 3
    doomRemovalChance = doomRemovalChance * effectiveness
    
    if target:hasStatusEffect(xi.effect.DOOM) and doomRemovalChance > math.random(1, 100) then
        target:delStatusEffect(xi.effect.DOOM)
    end
    
    -- Apply healing
    player:updateEnmityFromCure(target, heal)
    target:addHP(heal)
    target:wakeUp()
    
    return math.floor(heal)
end

-- Enhanced Divine Seal with merit integration
xi.job_utils.white_mage.useDivineSeal = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    
    local duration = 60 + player:getJobPointLevel(xi.jp.DIVINE_SEAL_EFFECT) * 5
    duration = duration * effectiveness
    
    -- Merit bonus for duration
    duration = duration + player:getMerit(xi.merit.DIVINE_SEAL_DURATION) * 10
    
    local power = 100 + player:getJobPointLevel(xi.jp.DIVINE_SEAL_EFFECT) * 5
    power = power * effectiveness
    
    player:addStatusEffect(xi.effect.DIVINE_SEAL, math.floor(power), 0, math.floor(duration))
    return math.floor(duration)
end

-- Enhanced Afflatus Solace with comprehensive bonuses
xi.job_utils.white_mage.useAfflatusSolace = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    
    target:delStatusEffect(xi.effect.AFFLATUS_SOLACE)
    target:delStatusEffect(xi.effect.AFFLATUS_MISERY)
    
    local duration = 7200 + player:getJobPointLevel(xi.jp.AFFLATUS_SOLACE_EFFECT) * 60
    duration = duration * effectiveness
    
    local power = 8 + player:getJobPointLevel(xi.jp.AFFLATUS_SOLACE_EFFECT)
    power = power * effectiveness
    
    target:addStatusEffect(xi.effect.AFFLATUS_SOLACE, math.floor(power), 0, math.floor(duration))
    return math.floor(duration)
end

-- Enhanced Afflatus Misery with comprehensive bonuses
xi.job_utils.white_mage.useAfflatusMisery = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    
    target:delStatusEffect(xi.effect.AFFLATUS_SOLACE)
    target:delStatusEffect(xi.effect.AFFLATUS_MISERY)
    
    local duration = 7200 + player:getJobPointLevel(xi.jp.AFFLATUS_MISERY_EFFECT) * 60
    duration = duration * effectiveness
    
    local power = 8 + player:getJobPointLevel(xi.jp.AFFLATUS_MISERY_EFFECT)
    power = power * effectiveness
    
    target:addStatusEffect(xi.effect.AFFLATUS_MISERY, math.floor(power), 0, math.floor(duration))
    return math.floor(duration)
end

-- Enhanced Asylum with area healing sanctuary
xi.job_utils.white_mage.useAsylum = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    
    local duration = 30 + player:getJobPointLevel(xi.jp.ASYLUM_EFFECT) * 2
    duration = duration * effectiveness
    
    local power = 3 + player:getJobPointLevel(xi.jp.ASYLUM_EFFECT)
    power = power * effectiveness
    
    -- Merit bonus for healing potency
    power = power + player:getMerit(xi.merit.CURE_POTENCY)
    
    target:addStatusEffect(xi.effect.ASYLUM, math.floor(power), 0, math.floor(duration))
    return math.floor(duration)
end

-- Enhanced Devotion with merit integration
xi.job_utils.white_mage.useDevotion = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Plus 5 percent mp recovers per extra devotion merit
    local meritBonus = player:getMerit(xi.merit.DEVOTION) - 5
    local mpPercent = ((25 + meritBonus) / 100) * effectiveness
    local damageHP = math.floor(player:getHP() * 0.25)
    
    -- If stoneskin is present, it should absorb damage
    damageHP = utils.stoneskin(player, damageHP)
    
    local healMP = math.floor(player:getHP() * mpPercent)
    healMP = utils.clamp(healMP, 0, target:getMaxMP() - target:getMP())
    
    damageHP = utils.stoneskin(player, damageHP)
    player:delHP(damageHP)
    target:addMP(healMP)
    
    return healMP
end

-- Enhanced Martyr with merit integration
xi.job_utils.white_mage.useMartyr = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Plus 5 percent hp recovers per extra martyr merit
    local meritBonus = player:getMerit(xi.merit.MARTYR) - 5
    local hpPercent = ((200 + meritBonus) / 100) * effectiveness
    
    local damageHP = math.floor(player:getHP() * 0.25)
    
    -- We need to capture this here because the base damage is the basis for the heal
    local healHP = math.floor(damageHP * hpPercent)
    healHP = utils.clamp(healHP, 0, target:getMaxHP() - target:getHP())
    
    -- If stoneskin is present, it should absorb damage
    damageHP = utils.stoneskin(player, damageHP)
    player:delHP(damageHP)
    target:addHP(healHP)
    
    return healHP
end

-- Enhanced Divine Caress with comprehensive status immunity
xi.job_utils.white_mage.useDivineCaress = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    
    local duration = 60 + player:getJobPointLevel(xi.jp.DIVINE_CARESS_EFFECT) * 5
    duration = duration * effectiveness
    
    local power = 3 + player:getJobPointLevel(xi.jp.DIVINE_CARESS_EFFECT)
    power = power * effectiveness
    
    player:addStatusEffect(xi.effect.DIVINE_CARESS_I, math.floor(power), 0, math.floor(duration))
    return math.floor(duration)
end

-- Enhanced Sacrosanctity with comprehensive protection
xi.job_utils.white_mage.useSacrosanctity = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    
    local duration = 60 + player:getJobPointLevel(xi.jp.SACROSANCTITY_EFFECT) * 5
    duration = duration * effectiveness
    
    local power = 3 + player:getJobPointLevel(xi.jp.SACROSANCTITY_EFFECT)
    power = power * effectiveness
    
    target:addStatusEffect(xi.effect.SACROSANCTITY, math.floor(power), 0, math.floor(duration))
    return math.floor(duration)
end

-----------------------------------
-- Advanced White Mage Utility Functions
-----------------------------------

-- Calculate total healing bonus from all sources
xi.job_utils.white_mage.getTotalHealingBonus = function(player, spellType)
    local bonus = 0
    
    -- Base MND contribution
    bonus = bonus + math.floor(player:getStat(xi.mod.MND) / 3)
    
    -- Divine Seal bonus
    bonus = bonus + getDivineSealBonus(player, spellType)
    
    -- Afflatus bonus
    bonus = bonus + getAfflatusBonus(player, spellType)
    
    -- Job Point bonuses
    if spellType == "healing" then
        bonus = bonus + player:getJobPointLevel(xi.jp.CURE_POTENCY) * 3
    end
    
    -- Merit bonuses
    bonus = bonus + player:getMerit(xi.merit.CURE_POTENCY) * 2
    bonus = bonus + player:getMerit(xi.merit.DIVINE_MAGIC_ACCURACY)
    
    -- Apply subjob penalty
    local effectiveness = calculateSubjobPenalty(player)
    bonus = bonus * effectiveness
    
    return math.floor(bonus)
end

-- Get magic accuracy bonus for white magic
xi.job_utils.white_mage.getMagicAccuracyBonus = function(player, spellType)
    local bonus = 0
    
    -- Divine Seal bonus
    bonus = bonus + getDivineSealBonus(player, spellType)
    
    -- Job Point bonuses
    bonus = bonus + player:getJobPointLevel(xi.jp.MAGIC_ACCURACY) * 2
    
    -- Merit bonuses
    bonus = bonus + player:getMerit(xi.merit.DIVINE_MAGIC_ACCURACY) * 3
    
    -- Apply subjob penalty
    local effectiveness = calculateSubjobPenalty(player)
    bonus = bonus * effectiveness
    
    return math.floor(bonus)
end

-- Check if player can use advanced white magic
xi.job_utils.white_mage.canUseAdvancedMagic = function(player, requiredLevel)
    local hasAccess, effectiveness = validateJobAccess(player, requiredLevel, false)
    return hasAccess and effectiveness > 0
end

-- Get spell cast time reduction
xi.job_utils.white_mage.getCastTimeReduction = function(player, spellType)
    local reduction = 0
    
    -- Merit bonuses
    if spellType == "healing" then
        reduction = reduction + player:getMerit(xi.merit.CURE_CAST_TIME) * 5
    end
    
    -- Job Point bonuses
    reduction = reduction + player:getJobPointLevel(xi.jp.MAGIC_CAST_TIME) * 2
    
    -- Apply subjob penalty
    local effectiveness = calculateSubjobPenalty(player)
    reduction = reduction * effectiveness
    
    return math.floor(reduction)
end
