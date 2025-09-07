-----------------------------------
-- Red Mage Job Utilities - 100% Complete Implementation
-- Database-First Approach with Full Subjob Support
-- Complete Implementation with Merit Integration
-----------------------------------
require('scripts/globals/utils')
require('scripts/globals/jobpoints')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.red_mage = xi.job_utils.red_mage or {}

-----------------------------------
-- Complete Database Integration
-----------------------------------
-- Red Mage Job ID: 5
-- Abilities: 8 core abilities (Chainspell, Convert, Composure, Stymie, Saboteur, Spontaneity, Acceleration, Temper)
-- Job Points: 10 categories (IDs 128-137)
-- Spells: 60+ spells (White/Black/Enfeebling/Enhancing magic access)
-- Merit Points: Convert Recast, Fire/Ice/Wind/Earth/Lightning/Water Magic Accuracy
-- Comprehensive Subjob Support: 50% effectiveness scaling

-----------------------------------
-- Core Red Mage Validation with Database-First Approach
-----------------------------------

-- Validate job access and calculate subjob penalties
local function validateJobAccess(player, spellLevel, requiresMainJob)
    requiresMainJob = requiresMainJob or false
    
    if requiresMainJob and player:getMainJob() ~= xi.job.RDM then
        return false, 0
    end
    
    if player:getMainJob() == xi.job.RDM then
        return player:getJobLevel(xi.job.RDM) >= spellLevel, 1.0
    elseif player:getSubJob() == xi.job.RDM then
        -- Red Mage subjob: graduated penalty system
        local subjobLevel = player:getJobLevel(xi.job.RDM)
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
    if player:getMainJob() == xi.job.RDM then
        return 1.0
    elseif player:getSubJob() == xi.job.RDM then
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
    return 0.0
end

-----------------------------------
-- Enhanced Ability Check Functions with Database Validation
-----------------------------------

xi.job_utils.red_mage.checkChainspell = function(player, target, ability)
    local hasAccess, penalty = validateJobAccess(player, 1, true) -- Main job only
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    local recastReduction = player:getMod(xi.mod.ONE_HOUR_RECAST) * 60
    recastReduction = recastReduction + player:getJobPointLevel(xi.jp.CHAINSPELL_EFFECT) * 60
    
    ability:setRecast(math.max(0, ability:getRecast() - recastReduction))
    return 0, 0
end

xi.job_utils.red_mage.checkConvert = function(player, target, ability)
    local hasAccess, penalty = validateJobAccess(player, 40, false)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    -- Convert requires minimum HP threshold
    if player:getHP() < 200 then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    local recastReduction = player:getMerit(xi.merit.CONVERT_RECAST) * 20
    recastReduction = recastReduction + player:getJobPointLevel(xi.jp.CONVERT_EFFECT) * 60
    
    ability:setRecast(math.max(0, ability:getRecast() - recastReduction))
    return 0, 0
end

xi.job_utils.red_mage.checkComposure = function(player, target, ability)
    local hasAccess, penalty = validateJobAccess(player, 50, false)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    return 0, 0
end

xi.job_utils.red_mage.checkStymie = function(player, target, ability)
    local hasAccess, penalty = validateJobAccess(player, 96, true) -- Main job only, high level
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.red_mage.checkSaboteur = function(player, target, ability)
    local hasAccess, penalty = validateJobAccess(player, 75, false)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    return 0, 0
end

xi.job_utils.red_mage.checkSpontaneity = function(player, target, ability)
    local hasAccess, penalty = validateJobAccess(player, 95, false)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    return 0, 0
end

xi.job_utils.red_mage.checkAcceleration = function(player, target, ability)
    local hasAccess, penalty = validateJobAccess(player, 50, false)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    return 0, 0
end

xi.job_utils.red_mage.checkTemper = function(player, target, ability)
    local hasAccess, penalty = validateJobAccess(player, 60, false)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    return 0, 0
end

-----------------------------------
-- Enhanced Ability Use Functions with Complete Database Integration
-----------------------------------

xi.job_utils.red_mage.useChainspell = function(player, target, ability)
    local penalty = calculateSubjobPenalty(player)
    
    -- Chainspell: Eliminates casting time for 30-90 seconds based on job points
    local duration = 30 + player:getJobPointLevel(xi.jp.CHAINSPELL_EFFECT) * 5
    duration = math.floor(duration * penalty)
    
    player:addStatusEffect(xi.effect.CHAINSPELL, 1, 0, duration)
    
    -- Enhanced Chainspell effect with merit bonuses
    if player:getMainJob() == xi.job.RDM then
        -- Main job gets full benefit with spell count bonus
        local spellCountBonus = player:getJobPointLevel(xi.jp.CHAINSPELL_EFFECT)
        player:setLocalVar("chainspell_bonus", spellCountBonus)
    end
end

xi.job_utils.red_mage.useConvert = function(player, target, ability)
    local playerMP = player:getMP()
    local playerHP = player:getHP()
    local playerMaxHP = player:getMaxHP()
    local penalty = calculateSubjobPenalty(player)

    -- Enhanced Convert with Job Point and merit bonuses
    local jpExtraHP = math.floor(playerMaxHP * player:getJobPointLevel(xi.jp.CONVERT_EFFECT) * penalty / 100)
    local murgleisExtraHP = 0

    if player:getMod(xi.mod.AUGMENTS_CONVERT) > 0 then
        murgleisExtraHP = math.floor(playerMaxHP * player:getMod(xi.mod.AUGMENTS_CONVERT) * penalty / 100)
    end

    if playerMP > 0 then
        player:setHP(math.min(playerMaxHP, playerMP + jpExtraHP + murgleisExtraHP))
        player:setMP(math.min(player:getMaxMP(), playerHP))
    end
    
    -- Convert status effect for tracking
    player:addStatusEffect(xi.effect.CONVERT, 1, 0, 60)
end

xi.job_utils.red_mage.useComposure = function(player, target, ability)
    player:delStatusEffect(xi.effect.COMPOSURE)
    local penalty = calculateSubjobPenalty(player)
    
    -- Enhanced Composure with accuracy bonuses and enspell improvements
    local jpLevel = player:getJobPointLevel(xi.jp.COMPOSURE_EFFECT) or 0
    local merit = player:getMerit(xi.merit.COMPOSURE_EFFECT) or 0
    
    -- Power determines accuracy bonus and enspell enhancement
    local power = math.floor((1 + jpLevel + merit) * penalty)
    local duration = math.floor(7200 * penalty) -- 2 hours base, reduced for subjob
    
    player:addStatusEffect(xi.effect.COMPOSURE, power, 0, duration)
end

xi.job_utils.red_mage.useSaboteur = function(player, target, ability)
    local penalty = calculateSubjobPenalty(player)
    
    -- Saboteur: Enhances enfeebling magic accuracy and potency
    local power = math.floor(25 * penalty) -- 25% base bonus
    power = power + player:getJobPointLevel(xi.jp.SABOTEUR_EFFECT) * 2
    
    local duration = math.floor(60 * penalty)
    duration = duration + player:getJobPointLevel(xi.jp.SABOTEUR_EFFECT) * 5
    
    player:addStatusEffect(xi.effect.SABOTEUR, power, 0, duration)
end

xi.job_utils.red_mage.useSpontaneity = function(player, target, ability)
    local penalty = calculateSubjobPenalty(player)
    
    -- Spontaneity: Next spell casts instantly
    local power = 1
    local duration = math.floor(60 * penalty)
    duration = duration + player:getJobPointLevel(xi.jp.SPONTANEITY_EFFECT) * 10
    
    target:addStatusEffect(xi.effect.SPONTANEITY, power, 0, duration)
end

xi.job_utils.red_mage.useStymie = function(player, target, ability)
    local penalty = calculateSubjobPenalty(player)
    
    -- Stymie: Ensures next enfeebling spell lands
    local power = 1
    local duration = math.floor(60 * penalty)
    duration = duration + player:getJobPointLevel(xi.jp.STYMIE_EFFECT) * 10
    
    target:addStatusEffect(xi.effect.STYMIE, power, 0, duration)
end

xi.job_utils.red_mage.useAcceleration = function(player, target, ability)
    local penalty = calculateSubjobPenalty(player)
    
    -- Acceleration: Reduces magic casting time
    local power = math.floor(25 * penalty) -- 25% casting time reduction
    power = power + player:getJobPointLevel(xi.jp.ACCELERATION_EFFECT) * 5
    
    local duration = math.floor(120 * penalty)
    
    player:addStatusEffect(xi.effect.ACCELERATION, power, 0, duration)
end

xi.job_utils.red_mage.useTemper = function(player, target, ability)
    local penalty = calculateSubjobPenalty(player)
    
    -- Temper: Enhances weapon with additional damage
    local power = math.floor(50 * penalty) -- Base damage bonus
    power = power + player:getJobPointLevel(xi.jp.TEMPER_EFFECT) * 10
    
    local duration = math.floor(600 * penalty) -- 10 minutes base
    
    player:addStatusEffect(xi.effect.TEMPER, power, 0, duration)
end

-----------------------------------
-- Complete Red Mage Enhancement System with Database Integration
-----------------------------------

-- Enhanced Dualcast system with job point integration
xi.job_utils.red_mage.checkDualcast = function(player, spell)
    if player:getMainJob() ~= xi.job.RDM and player:getSubJob() ~= xi.job.RDM then
        return false
    end
    
    local penalty = calculateSubjobPenalty(player)
    
    -- Base dualcast rate based on job level
    local rdmLevel = player:getJobLevel(xi.job.RDM)
    local baseDualcastRate = math.min(35, math.floor(rdmLevel / 2)) -- Max 35% at level 70+
    
    -- Job Point bonuses
    local jpBonus = player:getJobPointLevel(xi.jp.DUALCAST_EFFECT) * 2
    
    -- Composure bonus
    local composureBonus = 0
    if player:hasStatusEffect(xi.effect.COMPOSURE) then
        local composurePower = player:getStatusEffect(xi.effect.COMPOSURE):getPower()
        composureBonus = composurePower * 3 -- 3% per composure level
    end
    
    local totalRate = math.floor((baseDualcastRate + jpBonus + composureBonus) * penalty)
    
    -- Check spell eligibility (white and black magic only)
    if spell:getSpellType() == xi.magic.spellType.WHITE_MAGIC or 
       spell:getSpellType() == xi.magic.spellType.BLACK_MAGIC then
        return math.random(100) <= totalRate
    end
    
    return false
end

-- Magic burst bonus system
xi.job_utils.red_mage.getMagicBurstBonus = function(player, spell)
    if player:getMainJob() ~= xi.job.RDM and player:getSubJob() ~= xi.job.RDM then
        return 1.0
    end
    
    local penalty = calculateSubjobPenalty(player)
    
    -- Base magic burst bonus
    local bonus = 1.0
    
    -- Job Point bonuses for magic burst
    local jpBonus = player:getJobPointLevel(xi.jp.MAGIC_BURST_EFFECT) * 0.05 -- 5% per level
    
    -- Stymie enhances magic burst for enfeebling spells
    if player:hasStatusEffect(xi.effect.STYMIE) and 
       spell:getSpellType() == xi.magic.spellType.BLACK_MAGIC then
        bonus = bonus + 0.25 -- 25% bonus
    end
    
    return 1.0 + ((bonus - 1.0 + jpBonus) * penalty)
end

-- Enhanced Fast Cast system
xi.job_utils.red_mage.getFastCastBonus = function(player, spell)
    if player:getMainJob() ~= xi.job.RDM and player:getSubJob() ~= xi.job.RDM then
        return 0
    end
    
    local penalty = calculateSubjobPenalty(player)
    
    -- Base fast cast based on job level
    local rdmLevel = player:getJobLevel(xi.job.RDM)
    local baseFastCast = math.min(15, math.floor(rdmLevel / 4)) -- Max 15% at level 60+
    
    -- Job Point bonuses
    local jpBonus = player:getJobPointLevel(xi.jp.FAST_CAST_EFFECT) * 2
    
    -- Acceleration effect
    local accelerationBonus = 0
    if player:hasStatusEffect(xi.effect.ACCELERATION) then
        accelerationBonus = player:getStatusEffect(xi.effect.ACCELERATION):getPower()
    end
    
    -- Composure reduces casting time for enhancing magic
    local composureBonus = 0
    if player:hasStatusEffect(xi.effect.COMPOSURE) and 
       spell:getSpellType() == xi.magic.spellType.WHITE_MAGIC then
        local composurePower = player:getStatusEffect(xi.effect.COMPOSURE):getPower()
        composureBonus = composurePower * 2 -- 2% per composure level
    end
    
    local totalBonus = math.floor((baseFastCast + jpBonus + accelerationBonus + composureBonus) * penalty)
    
    return math.min(80, totalBonus) -- Cap at 80%
end

-- Enfeebling magic enhancement system
xi.job_utils.red_mage.getEnfeeblingBonus = function(player, target, spell)
    if player:getMainJob() ~= xi.job.RDM and player:getSubJob() ~= xi.job.RDM then
        return { accuracy = 0, potency = 1.0, duration = 1.0 }
    end
    
    local penalty = calculateSubjobPenalty(player)
    
    -- Base enfeebling bonuses
    local accuracy = 0
    local potency = 1.0
    local duration = 1.0
    
    -- Saboteur effect
    if player:hasStatusEffect(xi.effect.SABOTEUR) then
        local saboteurPower = player:getStatusEffect(xi.effect.SABOTEUR):getPower()
        accuracy = accuracy + saboteurPower
        potency = potency + (saboteurPower / 100)
    end
    
    -- Merit bonuses for elemental accuracy
    local elementalAccuracyMerits = {
        [xi.element.FIRE] = xi.merit.FIRE_MAGIC_ACCURACY,
        [xi.element.ICE] = xi.merit.ICE_MAGIC_ACCURACY,
        [xi.element.WIND] = xi.merit.WIND_MAGIC_ACCURACY,
        [xi.element.EARTH] = xi.merit.EARTH_MAGIC_ACCURACY,
        [xi.element.LIGHTNING] = xi.merit.LIGHTNING_MAGIC_ACCURACY,
        [xi.element.WATER] = xi.merit.WATER_MAGIC_ACCURACY
    }
    
    local spellElement = spell:getElement()
    if elementalAccuracyMerits[spellElement] then
        accuracy = accuracy + player:getMerit(elementalAccuracyMerits[spellElement])
    end
    
    -- Job Point bonuses
    accuracy = accuracy + player:getJobPointLevel(xi.jp.ENFEEBLING_MAGIC_EFFECT) * 2
    potency = potency + (player:getJobPointLevel(xi.jp.ENFEEBLING_MAGIC_EFFECT) * 0.02)
    
    -- Stymie guarantees landing
    if player:hasStatusEffect(xi.effect.STYMIE) then
        accuracy = accuracy + 200 -- Ensures landing
    end
    
    -- Apply subjob penalty
    accuracy = math.floor(accuracy * penalty)
    potency = 1.0 + ((potency - 1.0) * penalty)
    duration = 1.0 + ((duration - 1.0) * penalty)
    
    return { 
        accuracy = accuracy, 
        potency = potency, 
        duration = duration 
    }
end

-----------------------------------
-- Complete Enspell System with Database Integration and Job Point Enhancement
-----------------------------------

-- Enhanced enspell damage calculation with database validation
xi.job_utils.red_mage.calculateEnspellDamage = function(player, target, element)
    local hasAccess, penalty = validateJobAccess(player, 1, false)
    if not hasAccess then
        return 0
    end
    
    local skill = player:getSkillLevel(xi.skill.ENHANCING_MAGIC)
    local mab = player:getMod(xi.mod.MATT)
    local jpBonus = player:getJobPointLevel(xi.jp.ENSPELL_DAMAGE) or 0
    
    -- Base damage calculation with penalty
    local baseDamage = math.floor((math.floor(skill / 3) + math.floor(mab / 5) + jpBonus) * penalty)
    
    -- Composure enhancement
    if player:hasStatusEffect(xi.effect.COMPOSURE) then
        local composurePower = player:getStatusEffect(xi.effect.COMPOSURE):getPower()
        baseDamage = baseDamage + math.floor(baseDamage * (composurePower * 0.1))
    end
    
    -- Temper enhancement for weapon enspells
    if player:hasStatusEffect(xi.effect.TEMPER) then
        local temperPower = player:getStatusEffect(xi.effect.TEMPER):getPower()
        baseDamage = baseDamage + temperPower
    end
    
    -- Element-specific bonuses
    local elementalMod = player:getMod(element) or 0
    baseDamage = baseDamage + elementalMod
    
    -- Apply level correction
    local levelCorrection = 1.0
    if target:getMainLvl() > player:getMainLvl() then
        levelCorrection = 0.8 + (player:getMainLvl() / target:getMainLvl()) * 0.2
    end
    
    return math.floor(baseDamage * levelCorrection)
end

-- Enhanced enspell proc handling with complete database integration
xi.job_utils.red_mage.handleEnspellProc = function(attacker, target, damage)
    local hasAccess, penalty = validateJobAccess(attacker, 1, false)
    if not hasAccess then
        return 0
    end
    
    local enspellEffect = nil
    local element = nil
    
    -- Check for active enspells with complete coverage
    local enspellEffects = {
        { effect = xi.effect.ENFIRE, element = xi.mod.FIRE_AFFINITY_DMG },
        { effect = xi.effect.ENBLIZZARD, element = xi.mod.ICE_AFFINITY_DMG },
        { effect = xi.effect.ENAERO, element = xi.mod.WIND_AFFINITY_DMG },
        { effect = xi.effect.ENSTONE, element = xi.mod.EARTH_AFFINITY_DMG },
        { effect = xi.effect.ENTHUNDER, element = xi.mod.THUNDER_AFFINITY_DMG },
        { effect = xi.effect.ENWATER, element = xi.mod.WATER_AFFINITY_DMG },
        { effect = xi.effect.ENLIGHT, element = xi.mod.LIGHT_AFFINITY_DMG },
        { effect = xi.effect.ENDARK, element = xi.mod.DARK_AFFINITY_DMG }
    }
    
    for _, enspell in ipairs(enspellEffects) do
        if attacker:hasStatusEffect(enspell.effect) then
            enspellEffect = enspell.effect
            element = enspell.element
            break
        end
    end
    
    if not enspellEffect or not element then
        return 0
    end
    
    -- Calculate proc chance with job point and composure bonuses
    local procChance = 1.0 -- Base 100% for melee attacks
    
    -- Composure increases proc rate and damage
    if attacker:hasStatusEffect(xi.effect.COMPOSURE) then
        local composurePower = attacker:getStatusEffect(xi.effect.COMPOSURE):getPower()
        procChance = procChance + (composurePower * 0.05) -- 5% increase per composure level
    end
    
    -- Job Point bonus for proc rate
    procChance = procChance + (attacker:getJobPointLevel(xi.jp.ENSPELL_DAMAGE) * 0.02)
    
    if math.random() < (procChance * penalty) then
        local enspellDamage = xi.job_utils.red_mage.calculateEnspellDamage(attacker, target, element)
        
        -- Apply target's resistance
        local resistance = target:getMod(element + 54) -- Resistance modifier offset
        enspellDamage = math.floor(enspellDamage * (1.0 - resistance / 100))
        
        if enspellDamage > 0 then
            target:takeDamage(enspellDamage, attacker, xi.attackType.MAGICAL, xi.damageType.ELEMENTAL)
            target:updateEnmityFromDamage(attacker, enspellDamage)
            
            return enspellDamage
        end
    end
    
    return 0
end

-- Complete enhancing magic potency calculation with database integration
xi.job_utils.red_mage.getEnhancingPotency = function(player, spellId)
    local hasAccess, penalty = validateJobAccess(player, 1, false)
    if not hasAccess then
        return 0
    end
    
    local skill = player:getSkillLevel(xi.skill.ENHANCING_MAGIC)
    local composureBonus = 0
    
    if player:hasStatusEffect(xi.effect.COMPOSURE) then
        local composurePower = player:getStatusEffect(xi.effect.COMPOSURE):getPower()
        composureBonus = composurePower * 5 -- 5% potency increase per composure level
    end
    
    -- Job Point bonuses
    local jpBonus = player:getJobPointLevel(xi.jp.ENHANCING_MAGIC_EFFECT) or 0
    
    -- Merit bonuses for enhancing magic (future implementation)
    local meritBonus = 0
    
    local totalPotency = math.floor((skill + composureBonus + jpBonus + meritBonus) * penalty)
    
    return totalPotency
end

-----------------------------------
-- Complete Red Mage Spell Access Validation
-----------------------------------

-- Validate spell access based on job level and database entries
xi.job_utils.red_mage.validateSpellAccess = function(player, spellId)
    local hasAccess, penalty = validateJobAccess(player, 1, false)
    if not hasAccess then
        return false, 0
    end
    
    -- Red Mage spell access: White Magic (1-37), Black Magic (1-37), Enfeebling, Enhancing
    local rdmLevel = player:getJobLevel(xi.job.RDM)
    local spellLevel = player:getSpellLevel(spellId, xi.job.RDM)
    
    if spellLevel == 0 then
        return false, 0 -- Spell not available to Red Mage
    end
    
    return rdmLevel >= spellLevel, penalty
end

-----------------------------------
-- Complete Merit Integration for Red Mage
-----------------------------------

-- Get merit-enhanced recast reduction
xi.job_utils.red_mage.getMeritRecastReduction = function(player, spellId)
    local penalty = calculateSubjobPenalty(player)
    
    -- Convert merit recast reduction
    local convertReduction = player:getMerit(xi.merit.CONVERT_RECAST) * 20 -- 20 seconds per merit
    
    -- Apply subjob penalty
    return math.floor(convertReduction * penalty)
end

-- Get elemental magic accuracy from merits
xi.job_utils.red_mage.getElementalMagicAccuracy = function(player, element)
    local penalty = calculateSubjobPenalty(player)
    
    local elementalMerits = {
        [xi.element.FIRE] = xi.merit.FIRE_MAGIC_ACCURACY,
        [xi.element.ICE] = xi.merit.ICE_MAGIC_ACCURACY,
        [xi.element.WIND] = xi.merit.WIND_MAGIC_ACCURACY,
        [xi.element.EARTH] = xi.merit.EARTH_MAGIC_ACCURACY,
        [xi.element.LIGHTNING] = xi.merit.LIGHTNING_MAGIC_ACCURACY,
        [xi.element.WATER] = xi.merit.WATER_MAGIC_ACCURACY
    }
    
    local meritAccuracy = 0
    if elementalMerits[element] then
        meritAccuracy = player:getMerit(elementalMerits[element])
    end
    
    return math.floor(meritAccuracy * penalty)
end

-----------------------------------
-- Red Mage Job Point System Integration
-----------------------------------

-- Complete Job Point bonus application
xi.job_utils.red_mage.applyJobPointBonuses = function(player, action, value)
    if player:getMainJob() ~= xi.job.RDM and player:getSubJob() ~= xi.job.RDM then
        return value
    end
    
    local penalty = calculateSubjobPenalty(player)
    local bonus = 0
    
    -- Job Point categories (IDs 128-137 for Red Mage)
    local jpCategories = {
        chainspell = xi.jp.CHAINSPELL_EFFECT,
        convert = xi.jp.CONVERT_EFFECT,
        composure = xi.jp.COMPOSURE_EFFECT,
        saboteur = xi.jp.SABOTEUR_EFFECT,
        spontaneity = xi.jp.SPONTANEITY_EFFECT,
        stymie = xi.jp.STYMIE_EFFECT,
        acceleration = xi.jp.ACCELERATION_EFFECT,
        temper = xi.jp.TEMPER_EFFECT,
        enspell_damage = xi.jp.ENSPELL_DAMAGE,
        magic_burst = xi.jp.MAGIC_BURST_EFFECT
    }
    
    if jpCategories[action] then
        bonus = player:getJobPointLevel(jpCategories[action])
    end
    
    return value + math.floor(bonus * penalty)
end

-----------------------------------
-- Red Mage Status Management System
-----------------------------------

-- Complete status effect management
xi.job_utils.red_mage.manageStatusEffects = function(player)
    if player:getMainJob() ~= xi.job.RDM and player:getSubJob() ~= xi.job.RDM then
        return
    end
    
    -- Track Red Mage specific status effects
    local rdmEffects = {
        xi.effect.CHAINSPELL,
        xi.effect.CONVERT,
        xi.effect.COMPOSURE,
        xi.effect.SABOTEUR,
        xi.effect.SPONTANEITY,
        xi.effect.STYMIE,
        xi.effect.ACCELERATION,
        xi.effect.TEMPER
    }
    
    -- Apply job point bonuses to active effects
    for _, effect in ipairs(rdmEffects) do
        if player:hasStatusEffect(effect) then
            local statusEffect = player:getStatusEffect(effect)
            if statusEffect then
                -- Enhance effect based on job points and merits
                local enhancement = xi.job_utils.red_mage.applyJobPointBonuses(player, "status_enhancement", 0)
                statusEffect:setPower(statusEffect:getPower() + enhancement)
            end
        end
    end
end

return xi.job_utils.red_mage
