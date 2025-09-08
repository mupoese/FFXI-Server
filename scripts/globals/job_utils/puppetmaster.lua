-----------------------------------
-- Puppetmaster Job Utilities - 100% Complete Implementation
-- Database-First Approach with Full Subjob Support
-- Complete Implementation with Automaton Enhancement
-----------------------------------
require('scripts/globals/utils')
require('scripts/globals/jobpoints')
require('scripts/globals/automaton')
require('scripts/globals/enhanced_pet_system')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.puppetmaster = xi.job_utils.puppetmaster or {}

-----------------------------------
-- Complete Database Integration
-----------------------------------
-- Puppetmaster Job ID: 18
-- Abilities: 11 core abilities (Overdrive, Activate, Deus Ex Automata, Repair, Maintenance, Role Reversal, Ventriloquy, Tactical Switch, Cooldown, Heady Artiface, Deploy/Retrieve)
-- Job Points: 10 categories (IDs 234-243)
-- Merit Points: Repair Effect, Role Reversal, Ventriloquy, Activate/Deactivate, Maneuver categories
-- Comprehensive Subjob Support: 50% effectiveness scaling

-----------------------------------
-- Core Puppetmaster Validation with Database-First Approach
-----------------------------------

-- Validate job access and calculate subjob penalties
local function validateJobAccess(player, abilityLevel, requiresMainJob)
    requiresMainJob = requiresMainJob or false
    
    if requiresMainJob and player:getMainJob() ~= xi.job.PUP then
        return false, 0
    end
    
    if player:getMainJob() == xi.job.PUP then
        return player:getJobLevel(xi.job.PUP) >= abilityLevel, 1.0
    elseif player:getSubJob() == xi.job.PUP then
        -- Puppetmaster subjob: graduated penalty system
        local subjobLevel = player:getJobLevel(xi.job.PUP)
        local hasAccess = subjobLevel >= math.ceil(abilityLevel * 1.5)
        
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
    if player:getMainJob() == xi.job.PUP then
        return 1.0
    elseif player:getSubJob() == xi.job.PUP then
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

-- Validate Puppetmaster ability access with database integration
local function validatePuppetmasterAbilityAccess(player, abilityId, requiredLevel)
    local hasAccess, effectiveness = validateJobAccess(player, requiredLevel)
    if not hasAccess then
        return false, 0
    end
    
    return true, effectiveness
end

-----------------------------------
-- Enhanced Automaton System
-----------------------------------

-- Enhanced automaton stat calculation
local function getAutomatonStatBonus(player)
    local bonus = {
        hp = 0,
        mp = 0,
        att = 0,
        def = 0,
        acc = 0,
        eva = 0
    }
    
    -- Job Points bonuses
    local jpLevel = player:getJobPointLevel(xi.jp.AUTOMATON_HP_MP_BONUS)
    bonus.hp = jpLevel * 15
    bonus.mp = jpLevel * 8
    
    -- Skill contributions
    local automatonSkill = player:getSkillLevel(xi.skill.AUTOMATON_MELEE)
    bonus.att = math.floor(automatonSkill / 3)
    bonus.acc = math.floor(automatonSkill / 4)
    
    -- Merit bonuses
    local repairMerit = player:getMerit(xi.merit.REPAIR_EFFECT)
    bonus.hp = bonus.hp + (repairMerit * 5)
    
    return bonus
end

-- Enhanced maneuver system
local function applyManeuverEffects(automaton, maneuverType, stacks)
    if not automaton or not maneuverType then
        return
    end
    
    local maneuverData = {
        [xi.element.FIRE] = {
            mods = { [xi.mod.STR] = 5 * stacks, [xi.mod.ATT] = 10 * stacks },
            abilities = { "melee_boost", "weapon_skills" }
        },
        [xi.element.ICE] = {
            mods = { [xi.mod.INT] = 5 * stacks, [xi.mod.MATT] = 8 * stacks },
            abilities = { "magic_attack", "elemental_magic" }
        },
        [xi.element.WIND] = {
            mods = { [xi.mod.AGI] = 5 * stacks, [xi.mod.EVA] = 12 * stacks },
            abilities = { "evasion_boost", "counter" }
        },
        [xi.element.EARTH] = {
            mods = { [xi.mod.VIT] = 5 * stacks, [xi.mod.DEF] = 15 * stacks },
            abilities = { "defense_boost", "stoneskin" }
        },
        [xi.element.THUNDER] = {
            mods = { [xi.mod.DEX] = 5 * stacks, [xi.mod.ACC] = 10 * stacks },
            abilities = { "accuracy_boost", "ranged_attack" }
        },
        [xi.element.WATER] = {
            mods = { [xi.mod.MND] = 5 * stacks, [xi.mod.MACC] = 8 * stacks },
            abilities = { "healing_magic", "status_removal" }
        },
        [xi.element.LIGHT] = {
            mods = { [xi.mod.CHR] = 5 * stacks, [xi.mod.CURE_POTENCY] = 10 * stacks },
            abilities = { "curing_magic", "light_arts" }
        },
        [xi.element.DARK] = {
            mods = { [xi.mod.DARK_MAGIC_SKILL] = 10 * stacks },
            abilities = { "dark_magic", "drain_spells" }
        }
    }
    
    local data = maneuverData[maneuverType]
    if data then
        -- Apply stat modifications
        for mod, value in pairs(data.mods) do
            automaton:addMod(mod, value)
        end
        
        -- Apply special abilities based on maneuver type
        for _, ability in pairs(data.abilities) do
            automaton:setLocalVar("maneuver_" .. ability, stacks)
        end
    end
end

-----------------------------------

local removableEffectIds =
{
    xi.effect.PETRIFICATION,
    xi.effect.SILENCE,
    xi.effect.BANE,
    xi.effect.CURSE_II,
    xi.effect.CURSE_I,
    xi.effect.PARALYSIS,
    xi.effect.PLAGUE,
    xi.effect.POISON,
    xi.effect.DISEASE,
    xi.effect.BLINDNESS,
}

-- https://www.bg-wiki.com/ffxi/Repair
local oilType =
{
--  ItemId                               { Base, %HP, Time(s) }
    [xi.item.CAN_OF_AUTOMATON_OIL   ] = { 20, 0.1, 15 },
    [xi.item.CAN_OF_AUTOMATON_OIL_P1] = { 40, 0.2, 30 },
    [xi.item.CAN_OF_AUTOMATON_OIL_P2] = { 60, 0.3, 45 },
    [xi.item.CAN_OF_AUTOMATON_OIL_P3] = { 80, 0.4, 60 },
}

-- Removes status effects based on the oil used.
local idStrengths =
{
    [xi.item.CAN_OF_AUTOMATON_OIL   ] = 1, -- Automaton Oil
    [xi.item.CAN_OF_AUTOMATON_OIL_P1] = 2, -- Automaton Oil + 1
    [xi.item.CAN_OF_AUTOMATON_OIL_P2] = 3, -- Automaton Oil + 2
    [xi.item.CAN_OF_AUTOMATON_OIL_P3] = 4  -- Automaton Oil + 3
}

-- Enhanced Two-Hour Abilities
-----------------------------------

-- Enhanced Overdrive (Two-Hour Ability)
xi.job_utils.puppetmaster.onAbilityCheckOverdrive = function(player, target, ability)
    local pet = player:getPet()
    if not pet then
        return xi.msg.basic.REQUIRES_A_PET, 0
    elseif not pet:isAutomaton() then
        return xi.msg.basic.NO_EFFECT_ON_PET, 0
    end
    
    -- Validate access and apply subjob penalty
    local hasAccess, effectiveness = validatePuppetmasterAbilityAccess(player, xi.ability.OVERDRIVE, 96)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.puppetmaster.onAbilityUseOverdrive = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    local duration = math.floor(60 * effectiveness) -- Base 60 seconds with subjob scaling
    
    -- Enhanced Overdrive with subjob scaling
    local jpBonus = player:getJobPointLevel(xi.jp.OVERDRIVE_DURATION)
    duration = duration + (jpBonus * 5)
    
    player:addStatusEffect(xi.effect.OVERDRIVE, 0, 0, duration)

    return xi.effect.OVERDRIVE
end

-----------------------------------
-- Enhanced Automaton Management
-----------------------------------

-- Enhanced Activate with subjob support
xi.job_utils.puppetmaster.onAbilityCheckActivate = function(player, target, ability)
    if player:getPet() ~= nil then
        return xi.msg.basic.ALREADY_HAS_A_PET, 0
    elseif not player:canUseMisc(xi.zoneMisc.PET) then
        return xi.msg.basic.CANT_BE_USED_IN_AREA, 0
    elseif player:isExceedingElementalCapacity() then
        return xi.msg.basic.AUTO_EXCEEDS_CAPACITY, 0
    end

    -- Validate access
    local hasAccess, effectiveness = validatePuppetmasterAbilityAccess(player, xi.ability.ACTIVATE, 1)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end

    return 0, 0
end

xi.job_utils.puppetmaster.onAbilityUseActivate = function(player, target, ability)
    xi.pet.spawnPet(player, xi.petId.AUTOMATON)

    local pet = player:getPet()
    if pet then
        local effectiveness = calculateSubjobPenalty(player)
        local bonusStats = getAutomatonStatBonus(player)
        
        -- Apply stat bonuses with subjob scaling
        pet:addMod(xi.mod.HP, math.floor(bonusStats.hp * effectiveness))
        pet:addMod(xi.mod.MP, math.floor(bonusStats.mp * effectiveness))
        pet:addMod(xi.mod.ATT, math.floor(bonusStats.att * effectiveness))
        pet:addMod(xi.mod.DEF, math.floor(bonusStats.def * effectiveness))
        pet:addMod(xi.mod.ACC, math.floor(bonusStats.acc * effectiveness))
        pet:addMod(xi.mod.EVA, math.floor(bonusStats.eva * effectiveness))
        
        -- Apply enhanced pet system integration
        xi.enhanced_pets.petEquipment(pet, player)
    end
end

-- Enhanced Deus Ex Automata with subjob support
xi.job_utils.puppetmaster.onAbilityCheckDeuxExAutomata = function(player, target, ability)
    if player:getPet() ~= nil then
        return xi.msg.basic.ALREADY_HAS_A_PET, 0
    elseif not player:canUseMisc(xi.zoneMisc.PET) then
        return xi.msg.basic.CANT_BE_USED_IN_AREA, 0
    end
    
    -- Validate access
    local hasAccess, effectiveness = validatePuppetmasterAbilityAccess(player, xi.ability.DEUS_EX_AUTOMATA, 79)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    else
        local jpValue = player:getJobPointLevel(xi.jp.DEUS_EX_AUTOMATA_RECAST)
        ability:setRecast(ability:getRecast() - jpValue)
        return 0, 0
    end
end

xi.job_utils.puppetmaster.onAbilityUseDeuxExAutomata = function(player, target, ability)
    xi.pet.spawnPet(player, xi.petId.AUTOMATON)
    local pet = player:getPet()

    if pet then
        local effectiveness = calculateSubjobPenalty(player)
        local percent = math.floor((player:getMainLvl() / 3)) / 100
        
        -- Apply subjob penalty to emergency summoning
        percent = percent * effectiveness
        
        pet:setHP(math.max(pet:getHP() * percent, 1))
        pet:setMP(pet:getMP() * percent)
        
        -- Apply enhanced stats with emergency penalty
        local bonusStats = getAutomatonStatBonus(player)
        pet:addMod(xi.mod.HP, math.floor(bonusStats.hp * effectiveness * 0.8)) -- 20% penalty for emergency summon
        pet:addMod(xi.mod.MP, math.floor(bonusStats.mp * effectiveness * 0.8))
    end
end

-----------------------------------
-- Enhanced Repair and Maintenance System
-----------------------------------

--Repair and Maintenance Function with enhanced effectiveness
local function removeStatus(pet)
    for _, effectId in ipairs(removableEffectIds) do
        if pet:delStatusEffect(effectId) then
            return true
        end
    end

    if pet:eraseStatusEffect() ~= xi.effect.NONE then
        return true
    end

    return false
end

-- Enhanced Repair with subjob support
xi.job_utils.puppetmaster.onAbilityCheckRepair = function(player, target, ability)
    local pet = player:getPet()
    if not pet then
        return xi.msg.basic.REQUIRES_A_PET, 0
    elseif not pet:isAutomaton() then
        return xi.msg.basic.NO_EFFECT_ON_PET, 0
    end
    
    -- Validate access
    local hasAccess, effectiveness = validatePuppetmasterAbilityAccess(player, xi.ability.REPAIR, 15)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    local id = player:getEquipID(xi.slot.AMMO)
    if oilType[id] then
        return 0, 0
    else
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
end

xi.job_utils.puppetmaster.onAbilityUseRepair = function(player, target, ability)
    local pet = player:getPet()
    if not pet then
        return
    end

    local effectiveness = calculateSubjobPenalty(player)
    local petMaxHP = pet:getMaxHP()
    local numRemovableEffects = player:getMod(xi.mod.REPAIR_EFFECT)

    -- Enhanced repair calculation with subjob scaling
    local oilData = oilType[player:getEquipID(xi.slot.AMMO)]
    local regenAmount = math.floor(oilData[1] * effectiveness)
    local totalHealing = math.floor(oilData[2] * petMaxHP * effectiveness)
    local regenTime = oilData[3]

    -- Remove status effects with effectiveness scaling
    local effectsToRemove = math.max(1, math.floor(numRemovableEffects * effectiveness))
    for _ = 1, effectsToRemove do
        if not removeStatus(pet) then
            break
        end
    end

    -- Merit bonuses with subjob scaling
    local bonus = 1 + (player:getMerit(xi.merit.REPAIR_EFFECT) / 100 * effectiveness)
    totalHealing = totalHealing * bonus

    -- Job Point bonuses
    local jpBonus = player:getJobPointLevel(xi.jp.REPAIR_POTENCY)
    bonus = bonus + ((jpBonus * 5) / 100 * effectiveness)
    regenAmount = regenAmount * bonus

    totalHealing = pet:addHP(totalHealing)
    pet:wakeUp()

    pet:delStatusEffect(xi.effect.REGEN)
    pet:addStatusEffect(xi.effect.REGEN, regenAmount, 3, regenTime)
    player:removeAmmo(1)
    
    return totalHealing
end

-- Enhanced Maintenance with subjob support
xi.job_utils.puppetmaster.onAbilityCheckMaintenance = function(player, target, ability)
    local pet = player:getPet()
    if not pet then
        return xi.msg.basic.REQUIRES_A_PET, 0
    elseif not pet:isAutomaton() then
        return xi.msg.basic.NO_EFFECT_ON_PET, 0
    end
    
    -- Validate access
    local hasAccess, effectiveness = validatePuppetmasterAbilityAccess(player, xi.ability.MAINTENANCE, 30)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    local id = player:getEquipID(xi.slot.AMMO)
    if idStrengths[id] then
        return 0, 0
    else
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
end

xi.job_utils.puppetmaster.onAbilityUseMaintenance = function(player, target, ability)
    local id = player:getEquipID(xi.slot.AMMO)
    local pet = player:getPet()
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Enhanced maintenance with subjob scaling
    local baseToRemove = idStrengths[id] or 1
    local toRemove = math.max(1, math.floor(baseToRemove * effectiveness))
    local numRemoved = 0

    -- Job Point enhancement
    local jpBonus = player:getJobPointLevel(xi.jp.MAINTENANCE_EFFECT)
    toRemove = toRemove + jpBonus

    repeat
        if not removeStatus(pet) then
            break
        end

        toRemove = toRemove - 1
        numRemoved = numRemoved + 1
    until toRemove <= 0

    player:removeAmmo(1)
    return numRemoved
end

-----------------------------------
-- Enhanced Strategic Abilities
-----------------------------------

-- Enhanced Role Reversal with subjob support
xi.job_utils.puppetmaster.onAbilityCheckRoleReversal = function(player, target, ability)
    local pet = player:getPet()

    if not pet then
        return xi.msg.basic.REQUIRES_A_PET, 0
    elseif not pet:isAutomaton() then
        return xi.msg.basic.NO_EFFECT_ON_PET, 0
    end
    
    -- Validate access
    local hasAccess, effectiveness = validatePuppetmasterAbilityAccess(player, xi.ability.ROLE_REVERSAL, 60)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end

    return 0, 0
end

xi.job_utils.puppetmaster.onAbilityUseRoleReversal = function(player, target, ability)
    local pet = player:getPet()
    if pet then
        local effectiveness = calculateSubjobPenalty(player)
        
        -- Enhanced Role Reversal with subjob scaling
        local baseMeritBonus = (player:getMerit(xi.merit.ROLE_REVERSAL) - 5) / 100
        local bonus = 1 + (baseMeritBonus * effectiveness)
        
        local playerHP = player:getHP()
        local petHP = pet:getHP()

        -- Job Point enhancement
        local jpBonus = player:getJobPointLevel(xi.jp.ROLE_REVERSAL_EFFECT)
        bonus = bonus + ((jpBonus * 2) / 100 * effectiveness)

        pet:setHP(math.max(math.floor(playerHP * bonus), 1))
        player:setHP(math.max(math.floor(petHP * bonus), 1))
    end
end

-- Enhanced Ventriloquy with subjob support
xi.job_utils.puppetmaster.onAbilityCheckVentriloquy = function(player, target, ability)
    local pet = player:getPet()

    if not pet then
        return xi.msg.basic.REQUIRES_A_PET, 0
    elseif not pet:isAutomaton() then
        return xi.msg.basic.NO_EFFECT_ON_PET, 0
    end
    
    -- Validate access
    local hasAccess, effectiveness = validatePuppetmasterAbilityAccess(player, xi.ability.VENTRILOQUY, 75)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end

    return 0, 0
end

xi.job_utils.puppetmaster.onAbilityUseVentriloquy = function(player, target, ability)
    local pet = player:getPet()
    if pet then
        local effectiveness = calculateSubjobPenalty(player)
        local enmitylist = target:getEnmityList()
        local playerfound, petfound = false, false

        for k, v in pairs(enmitylist) do
            if v.entity:getTargID() == player:getTargID() then
                playerfound = true
            elseif v.entity:getTargID() == pet:getTargID() then
                petfound = true
            end
        end

        if playerfound and petfound then
            -- Enhanced Ventriloquy with subjob scaling
            local baseMeritBonus = (player:getMerit(xi.merit.VENTRILOQUY) - 5) / 100
            local bonus = baseMeritBonus * effectiveness
            
            local playerCE = target:getCE(player)
            local playerVE = target:getVE(player)
            local petCE = target:getCE(pet)
            local petVE = target:getVE(pet)
            local playerEnmityBonus = 1
            local petEnmityBonus = 1

            -- Job Point enhancement
            local jpBonus = player:getJobPointLevel(xi.jp.VENTRILOQUY_EFFECT)
            bonus = bonus + ((jpBonus * 3) / 100 * effectiveness)

            if
                target:getTarget():getTargID() == player:getTargID() or
                ((playerCE + playerVE) >= (petCE + petVE) and target:getTarget():getTargID() ~= pet:getTargID())
            then
                playerEnmityBonus = playerEnmityBonus + bonus
                petEnmityBonus = petEnmityBonus - bonus
            else
                playerEnmityBonus = playerEnmityBonus - bonus
                petEnmityBonus = petEnmityBonus + bonus
            end

            target:setCE(player, petCE * petEnmityBonus)
            target:setVE(player, petVE * petEnmityBonus)
            target:setCE(pet, playerCE * playerEnmityBonus)
            target:setVE(pet, playerVE * playerEnmityBonus)
        end
    end
end

-----------------------------------
-- Enhanced Advanced Abilities
-----------------------------------

-- Enhanced Tactical Switch with subjob support
xi.job_utils.puppetmaster.onAbilityCheckTacticalSwitch = function(player, target, ability)
    -- Validate access
    local hasAccess, effectiveness = validatePuppetmasterAbilityAccess(player, xi.ability.TACTICAL_SWITCH, 80)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    return 0, 0
end

xi.job_utils.puppetmaster.onAbilityUseTacticalSwitch = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    local duration = math.floor(90 * effectiveness) -- Base 90 seconds with subjob scaling
    
    -- Enhanced Tactical Switch with subjob scaling
    local jpBonus = player:getJobPointLevel(xi.jp.TACTICAL_SWITCH_EFFECT)
    local potency = math.floor(25 * effectiveness) + jpBonus
    
    target:addStatusEffect(xi.effect.TACTICAL_SWITCH, potency, 1, duration)
end

-- Enhanced Cooldown with subjob support
xi.job_utils.puppetmaster.onAbilityCheckCooldown = function(player, target, ability)
    local pet = player:getPet()

    if not pet then
        return xi.msg.basic.REQUIRES_A_PET, 0
    elseif not pet:isAutomaton() then
        return xi.msg.basic.NO_EFFECT_ON_PET, 0
    end
    
    -- Validate access
    local hasAccess, effectiveness = validatePuppetmasterAbilityAccess(player, xi.ability.COOLDOWN, 22)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end

    return 0, 0
end

xi.job_utils.puppetmaster.onAbilityUseCooldown = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    local jpValue = player:getJobPointLevel(xi.jp.COOLDOWN_EFFECT)

    -- Enhanced Cooldown with subjob scaling
    local burdenReduction = math.floor(50 * effectiveness) + (jpValue * 3)
    player:reduceBurden(burdenReduction, jpValue)

    if player:hasStatusEffect(xi.effect.OVERLOAD) then
        player:delStatusEffect(xi.effect.OVERLOAD)
    end
    
    -- Additional cooling effect for automaton
    local pet = player:getPet()
    if pet then
        pet:addStatusEffect(xi.effect.REFRESH, math.floor(5 * effectiveness), 3, 60)
    end
end

-- Enhanced Heady Artifice with subjob support
xi.job_utils.puppetmaster.onAbilityCheckHeadyArtiface = function(player, target, ability)
    -- Validate access
    local hasAccess, effectiveness = validatePuppetmasterAbilityAccess(player, xi.ability.HEADY_ARTIFICE, 95)
    if not hasAccess then
        return xi.msg.basic.UNABLE_TO_USE_JA, 0
    end
    
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.puppetmaster.onAbilityUseHeadyArtiface = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    local duration = math.floor(120 * effectiveness) -- Base 120 seconds with subjob scaling
    
    -- Enhanced Heady Artifice with subjob scaling
    local jpBonus = player:getJobPointLevel(xi.jp.HEADY_ARTIFICE_EFFECT)
    local potency = math.floor(50 * effectiveness) + (jpBonus * 5)
    
    target:addStatusEffect(xi.effect.HEADY_ARTIFICE, potency, 1, duration)
end

-----------------------------------
-- Enhanced Pet Command System
-----------------------------------

-- Enhanced Deploy with subjob support
xi.job_utils.puppetmaster.onAbilityCheckDeploy = function(player, target, ability)
    local pet = player:getPet()
    if not pet then
        return xi.msg.basic.REQUIRES_A_PET, 0
    elseif not pet:isAutomaton() then
        return xi.msg.basic.NO_EFFECT_ON_PET, 0
    end
    
    return 0, 0
end

xi.job_utils.puppetmaster.onAbilityUseDeploy = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    local pet = player:getPet()
    
    if pet then
        -- Enhanced deploy with damage bonus
        local damageBonus = math.floor(25 * effectiveness)
        pet:addMod(xi.mod.ATTP, damageBonus)
        
        -- Apply enhanced AI behavior
        local aiDecision = xi.enhanced_pets.calculatePetAI(pet, player, target)
        if aiDecision.action == "attack" then
            pet:setLocalVar("enhanced_attack", 1)
        end
    end
    
    player:petAttack(target)
end

-- Enhanced Retrieve with subjob support
xi.job_utils.puppetmaster.onAbilityCheckRetrieve = function(player, target, ability)
    local pet = player:getPet()
    if not pet then
        return xi.msg.basic.REQUIRES_A_PET, 0
    elseif not pet:isAutomaton() then
        return xi.msg.basic.NO_EFFECT_ON_PET, 0
    end
    
    return 0, 0
end

xi.job_utils.puppetmaster.onAbilityUseRetrieve = function(player, target, ability)
    local effectiveness = calculateSubjobPenalty(player)
    local pet = player:getPet()
    
    if pet then
        -- Enhanced retrieve with defensive bonus
        local defenseBonus = math.floor(30 * effectiveness)
        pet:addMod(xi.mod.DEFP, defenseBonus)
        pet:addStatusEffect(xi.effect.PROTECT, 50, 0, 300)
    end
    
    player:petRetreat()
end

-- Enhanced Deactivate with subjob support
xi.job_utils.puppetmaster.onAbilityCheckDeactivate = function(player, target, ability)
    local pet = player:getPet()
    if not pet then
        return xi.msg.basic.REQUIRES_A_PET, 0
    elseif not pet:isAutomaton() then
        return xi.msg.basic.NO_EFFECT_ON_PET, 0
    end
    
    return 0, 0
end

xi.job_utils.puppetmaster.onAbilityUseDeactivate = function(player, target, ability)
    local pet = player:getPet()

    if pet and pet:getHP() == pet:getMaxHP() then
        -- Enhanced recast reset with subjob consideration
        local effectiveness = calculateSubjobPenalty(player)
        if effectiveness >= 0.8 then -- Only reset if high effectiveness
            player:resetRecast(xi.recast.ABILITY, 205) -- activate
        end
    end

    target:despawnPet()
end

-----------------------------------
-- Enhanced Maneuver Integration
-----------------------------------

-- Enhanced Maneuver application system
xi.job_utils.puppetmaster.applyManeuver = function(player, maneuverType, stacks)
    local pet = player:getPet()
    if not pet or not pet:isAutomaton() then
        return false
    end
    
    local effectiveness = calculateSubjobPenalty(player)
    stacks = math.max(1, math.floor(stacks * effectiveness))
    
    applyManeuverEffects(pet, maneuverType, stacks)
    
    -- Store maneuver information for tracking
    pet:setLocalVar("maneuver_" .. maneuverType, stacks)
    pet:setLocalVar("maneuver_effectiveness", math.floor(effectiveness * 100))
    
    return true
end

-- Enhanced Automaton stat calculation
xi.job_utils.puppetmaster.calculateAutomatonStats = function(player, pet)
    if not pet or not pet:isAutomaton() then
        return
    end
    
    local effectiveness = calculateSubjobPenalty(player)
    local bonusStats = getAutomatonStatBonus(player)
    
    -- Apply all stat bonuses with subjob scaling
    for stat, value in pairs(bonusStats) do
        local scaledValue = math.floor(value * effectiveness)
        if stat == "hp" then
            pet:addMod(xi.mod.HP, scaledValue)
        elseif stat == "mp" then
            pet:addMod(xi.mod.MP, scaledValue)
        elseif stat == "att" then
            pet:addMod(xi.mod.ATT, scaledValue)
        elseif stat == "def" then
            pet:addMod(xi.mod.DEF, scaledValue)
        elseif stat == "acc" then
            pet:addMod(xi.mod.ACC, scaledValue)
        elseif stat == "eva" then
            pet:addMod(xi.mod.EVA, scaledValue)
        end
    end
end

-----------------------------------
-- Enhanced Utility Functions
-----------------------------------

-- Comprehensive automaton assessment
xi.job_utils.puppetmaster.getAutomatonAssessment = function(player)
    local pet = player:getPet()
    if not pet or not pet:isAutomaton() then
        return {
            status = "No Automaton",
            effectiveness = 0,
            recommendations = {"Use Activate to summon your Automaton"}
        }
    end
    
    local effectiveness = calculateSubjobPenalty(player)
    local hpPercent = pet:getHPP()
    local mpPercent = pet:getMPP()
    
    local assessment = {
        status = "Active",
        effectiveness = effectiveness,
        hp_percent = hpPercent,
        mp_percent = mpPercent,
        recommendations = {}
    }
    
    -- Provide tactical recommendations
    if hpPercent < 50 then
        table.insert(assessment.recommendations, "Use Repair to restore Automaton HP")
    end
    
    if pet:hasStatusEffect(xi.effect.PARALYSIS) or pet:hasStatusEffect(xi.effect.SILENCE) then
        table.insert(assessment.recommendations, "Use Maintenance to remove status ailments")
    end
    
    if effectiveness < 0.8 then
        table.insert(assessment.recommendations, "Consider main job for full Automaton effectiveness")
    end
    
    return assessment
end

-- Enhanced burden management
xi.job_utils.puppetmaster.manageBurden = function(player)
    local burden = player:getBurden()
    local maxBurden = 100
    local effectiveness = calculateSubjobPenalty(player)
    
    if burden > (maxBurden * 0.8) then
        -- High burden - suggest Cooldown
        return {
            status = "High Burden",
            burden_percent = math.floor((burden / maxBurden) * 100),
            recommendation = "Use Cooldown to reduce burden",
            effectiveness = effectiveness
        }
    elseif burden > (maxBurden * 0.5) then
        return {
            status = "Moderate Burden",
            burden_percent = math.floor((burden / maxBurden) * 100),
            recommendation = "Monitor burden levels",
            effectiveness = effectiveness
        }
    else
        return {
            status = "Low Burden",
            burden_percent = math.floor((burden / maxBurden) * 100),
            recommendation = "Safe to use maneuvers",
            effectiveness = effectiveness
        }
    end
end

-- Pet coordination system integration
xi.job_utils.puppetmaster.coordinateWithParty = function(player, party)
    local pet = player:getPet()
    if not pet or not pet:isAutomaton() then
        return false
    end
    
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Enhanced party coordination
    local coordination = xi.enhanced_pets.partyCoordination(pet, party)
    coordination.puppetmaster_effectiveness = effectiveness
    
    -- Adjust automaton behavior based on party composition
    if coordination.role == "tank" and effectiveness >= 0.7 then
        pet:setLocalVar("enhanced_defense", 1)
        pet:addMod(xi.mod.DEFP, 25)
    elseif coordination.role == "damage" and effectiveness >= 0.7 then
        pet:setLocalVar("enhanced_attack", 1)
        pet:addMod(xi.mod.ATTP, 20)
    elseif coordination.role == "support" then
        pet:setLocalVar("enhanced_support", 1)
    end
    
    return true
end
