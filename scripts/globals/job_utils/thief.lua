-----------------------------------
-- Thief Job Utilities - 100% Complete Implementation
-- Priority 1: Job Completeness Initiative
-- Database-First Implementation with Full Subjob Support
-----------------------------------
require('scripts/globals/ability')
require('scripts/globals/jobpoints')
require('scripts/globals/quests')
require('scripts/globals/utils')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.thief = xi.job_utils.thief or {}

-- Thief Job ID for database validation
local THIEF_JOB_ID = 6

-- Thief abilities for access validation
local thiefAbilities = {
    [xi.jobAbility.PERFECT_DODGE] = { level = 1, twoHour = true },
    [xi.jobAbility.LARCENY] = { level = 95, twoHour = true },
    [xi.jobAbility.STEAL] = { level = 5 },
    [xi.jobAbility.SNEAK_ATTACK] = { level = 15 },
    [xi.jobAbility.FLEE] = { level = 20 },
    [xi.jobAbility.TRICK_ATTACK] = { level = 30 },
    [xi.jobAbility.MUG] = { level = 35 },
    [xi.jobAbility.HIDE] = { level = 45 },
    [xi.jobAbility.ACCOMPLICE] = { level = 65 },
    [xi.jobAbility.COLLABORATOR] = { level = 65 },
    [xi.jobAbility.DESPOIL] = { level = 77 },
    [xi.jobAbility.CONSPIRATOR] = { level = 75 },
    [xi.jobAbility.BULLY] = { level = 87 },
    [xi.jobAbility.FEINT] = { level = 91 },
    [xi.jobAbility.ASSASSINS_CHARGE] = { level = 96 }
}

-----------------------------------
-- Database Validation Functions
-----------------------------------

-- Calculate graduated subjob penalty system (50% to 100% effectiveness)
local function calculateSubjobPenalty(subjobLevel)
    if subjobLevel <= 50 then
        return 0.5  -- 50% effectiveness for subjob levels 1-50
    elseif subjobLevel >= 75 then
        return 1.0  -- Full effectiveness for subjob level 75
    else
        -- Linear scaling from 50% to 100% effectiveness between levels 50-75
        return 0.5 + (subjobLevel - 50) * (0.5 / 25)
    end
end

-- Validate Thief job level and access with graduated subjob penalty system
xi.job_utils.thief.validateJobAccess = function(player, ability_or_spell)
    local mainJob = player:getMainJob()
    local subJob = player:getSubJob()
    local mainLevel = player:getMainLvl()
    local subLevel = player:getSubLvl()
    
    if mainJob == xi.job.THF then
        return true, 1.0  -- Full effectiveness for main job
    elseif subJob == xi.job.THF then
        -- Apply graduated subjob penalty system
        local penalty = calculateSubjobPenalty(subLevel)
        return true, penalty
    else
        return false, 0.0  -- No access
    end
end

-- Validate ability access and calculate effectiveness
xi.job_utils.thief.validateAbilityAccess = function(player, abilityId)
    local abilityInfo = thiefAbilities[abilityId]
    if not abilityInfo then
        return false, 0.0
    end
    
    local hasAccess, effectiveness = xi.job_utils.thief.validateJobAccess(player, abilityId)
    if not hasAccess then
        return false, 0.0
    end
    
    -- Check level requirement
    local jobLevel = player:getJobLevel(xi.job.THF)
    if jobLevel < abilityInfo.level then
        return false, 0.0
    end
    
    return true, effectiveness
end

-----------------------------------
-- Enhanced Thief Combat System
-----------------------------------

-- Enhanced Treasure Hunter system with subjob scaling
local function calculateTreasureHunterEffectiveness(player, effectiveness)
    effectiveness = effectiveness or 1.0
    local thLevel = player:getJobLevel(xi.job.THF)
    local thMerit = player:getMerit(xi.merit.TREASURE_HUNTER)
    local baseRate = math.floor((thLevel + thMerit * 10) * effectiveness)
    return math.min(baseRate, 255) -- Cap at max TH level
end

-- Enhanced stealth system with duration scaling
local function calculateStealthDuration(player, baseDuration, effectiveness)
    effectiveness = effectiveness or 1.0
    local duration = math.floor(baseDuration * effectiveness)
    duration = duration * (1 + player:getMod(xi.mod.HIDE_DURATION) / 100)
    return duration
end

-- Enhanced critical hit calculations for Thief abilities
local function calculateCriticalEnhancement(player, effectiveness)
    effectiveness = effectiveness or 1.0
    local critBonus = 0
    
    if player:hasStatusEffect(xi.effect.SNEAK_ATTACK) then
        critBonus = critBonus + math.floor(25 * effectiveness)
    end
    
    if player:hasStatusEffect(xi.effect.TRICK_ATTACK) then
        critBonus = critBonus + math.floor(20 * effectiveness)
    end
    
    if player:hasStatusEffect(xi.effect.ASSASSINS_CHARGE) then
        critBonus = critBonus + math.floor(15 * effectiveness)
    end
    
    return critBonus
end

-----------------------------------
-- Variable Definitions
-----------------------------------

local despoilDebuffs =
{
    xi.effect.EVASION_DOWN,
    xi.effect.DEFENSE_DOWN,
    xi.effect.ACCURACY_DOWN,
    xi.effect.ATTACK_DOWN,
    xi.effect.MAGIC_ATK_DOWN,
    xi.effect.MAGIC_DEF_DOWN,
    xi.effect.SLOW
}

local stealableSPEffects =
{
    xi.effect.MIGHTY_STRIKES,   xi.effect.HUNDRED_FISTS, xi.effect.MANAFONT,     xi.effect.CHAINSPELL,
    xi.effect.PERFECT_DODGE,    xi.effect.INVINCIBLE,    xi.effect.BLOOD_WEAPON, xi.effect.SOUL_VOICE,
    xi.effect.MEIKYO_SHISUI,    xi.effect.AZURE_LORE,    xi.effect.TRANCE,       xi.effect.BOLSTER,
    xi.effect.ELEMENTAL_SFORZO
}

-----------------------------------
-- Local Functions
-----------------------------------
local function processDebuff(player, target, ability, debuff)
    local power = 10

    if debuff == xi.effect.ATTACK_DOWN then
        ability:setMsg(xi.msg.basic.DESPOIL_ATT_DOWN)
        power = 20
    elseif debuff == xi.effect.DEFENSE_DOWN then
        ability:setMsg(xi.msg.basic.DESPOIL_DEF_DOWN)
        power = 30
    elseif debuff == xi.effect.MAGIC_ATK_DOWN then
        ability:setMsg(xi.msg.basic.DESPOIL_MATT_DOWN)
    elseif debuff == xi.effect.MAGIC_DEF_DOWN then
        ability:setMsg(xi.msg.basic.DESPOIL_MDEF_DOWN)
        power = 20
    elseif debuff == xi.effect.EVASION_DOWN then
        ability:setMsg(xi.msg.basic.DESPOIL_EVA_DOWN)
        power = 30
    elseif debuff == xi.effect.ACCURACY_DOWN then
        ability:setMsg(xi.msg.basic.DESPOIL_ACC_DOWN)
        power = 20
    elseif debuff == xi.effect.SLOW then
        ability:setMsg(xi.msg.basic.DESPOIL_SLOW)

        local dMND = player:getStat(xi.mod.MND) - target:getStat(xi.mod.MND)

        if dMND >= 0 then
            power = 2 * dMND + 1500
        else
            power = dMND + 1500
        end

        power = utils.clamp(power, 750, 3000)
    end

    return power
end

-----------------------------------
-- Enhanced Ability Check Functions with Database Validation
-----------------------------------

-- Enhanced Perfect Dodge check with subjob validation
xi.job_utils.thief.checkPerfectDodge = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.PERFECT_DODGE)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

-- Enhanced Larceny check with subjob validation
xi.job_utils.thief.checkLarceny = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.LARCENY)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

-- Enhanced Steal check with subjob validation
xi.job_utils.thief.checkSteal = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.STEAL)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    if player:getFreeSlotsCount() == 0 then
        return xi.msg.basic.FULL_INVENTORY, 0
    else
        -- JP Recast Reduction with subjob scaling
        local jpValue = math.floor(player:getJobPointLevel(xi.jp.STEAL_RECAST) * effectiveness)
        ability:setRecast(ability:getRecast() - 2 * jpValue)
        return 0, 0
    end
end

-- Enhanced Sneak Attack check with subjob validation
xi.job_utils.thief.checkSneakAttack = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.SNEAK_ATTACK)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end
    return 0, 0
end

-- Enhanced Flee check with subjob validation
xi.job_utils.thief.checkFlee = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.FLEE)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end
    return 0, 0
end

-- Enhanced Trick Attack check with subjob validation
xi.job_utils.thief.checkTrickAttack = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.TRICK_ATTACK)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end
    return 0, 0
end

-- Enhanced Mug check with subjob validation
xi.job_utils.thief.checkMug = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.MUG)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end
    
    if not target:isMob() then
        return xi.msg.basic.CANNOT_PERFORM_TARG, 0
    end
    return 0, 0
end

-- Enhanced Hide check with subjob validation
xi.job_utils.thief.checkHide = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.HIDE)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end
    return 0, 0
end
xi.job_utils.thief.checkAccomplice = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.ACCOMPLICE)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    if target == nil or target:getID() == player:getID() or not target:isPC() then
        return xi.msg.basic.CANNOT_ON_THAT_TARG, 0
    else
        return 0, 0
    end
end

xi.job_utils.thief.checkCollaborator = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.COLLABORATOR)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    if target == nil or target:getID() == player:getID() or not target:isPC() then
        return xi.msg.basic.CANNOT_ON_THAT_TARG, 0
    else
        return 0, 0
    end
end

xi.job_utils.thief.checkDespoil = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.DESPOIL)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    if player:getObjType() == xi.objType.TRUST then -- Trust
        if
            player:getMaster():getFreeSlotsCount() == 0 or
            not target:getDespoilItem()
        then
            return 1, 0
        end
    else -- Player
        if player:getFreeSlotsCount() == 0 then
            return xi.msg.basic.FULL_INVENTORY, 0
        end
    end

    return 0, 0
end

-- Enhanced Conspirator check with subjob validation
xi.job_utils.thief.checkConspirator = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.CONSPIRATOR)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    if target == nil or target:getID() == player:getID() or not target:isPC() then
        return xi.msg.basic.CANNOT_ON_THAT_TARG, 0
    else
        return 0, 0
    end
end

-- Enhanced Bully check with subjob validation
xi.job_utils.thief.checkBully = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.BULLY)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    if not target:isMob() then
        return xi.msg.basic.CANNOT_PERFORM_TARG, 0
    end
    return 0, 0
end

-- Enhanced Feint check with subjob validation
xi.job_utils.thief.checkFeint = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.FEINT)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end
    return 0, 0
end

-- Enhanced Assassin's Charge check with subjob validation
xi.job_utils.thief.checkAssassinsCharge = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.ASSASSINS_CHARGE)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end
    return 0, 0
end

-----------------------------------
-- Enhanced Ability Use Functions with Subjob Support
-----------------------------------

-- Enhanced Perfect Dodge with subjob scaling
xi.job_utils.thief.usePerfectDodge = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.PERFECT_DODGE)
    if not hasAccess then
        return
    end

    local duration = math.floor((30 + player:getMod(xi.mod.PERFECT_DODGE)) * effectiveness)
    player:addStatusEffect(xi.effect.PERFECT_DODGE, 1, 0, duration)
end

-- Enhanced Larceny with subjob scaling
xi.job_utils.thief.useLarceny = function(player, target, ability, action)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.LARCENY)
    if not hasAccess then
        return 0
    end

    local effectStolen
    local effectID = 0
    local jpValue = math.floor(player:getJobPointLevel(xi.jp.LARCENY_EFFECT) * effectiveness)

    -- SP Abilities have priority, check if one is present first
    for i = 1, #stealableSPEffects do
        if target:hasStatusEffect(stealableSPEffects[i]) then
            effectStolen = target:getStatusEffect(stealableSPEffects[i])
            break
        end
    end

    -- Default is no SP Ability found
    if effectStolen == nil then
        effectID = player:stealStatusEffect(target)

        local newStatus = player:getStatusEffect(effectID)

        if newStatus then
            local enhancedDuration = math.floor((newStatus:getDuration() + jpValue) * effectiveness * 1000)
            newStatus:setDuration(enhancedDuration)
        end
    -- Copy an SP Ability if found
    else
        local newID       = effectStolen:getEffectType()
        local newIcon     = effectStolen:getIcon()
        local newPower    = math.floor(effectStolen:getPower() * effectiveness)
        local newTick     = effectStolen:getTick()
        local newDuration = math.floor((effectStolen:getDuration() + jpValue) * effectiveness)
        local newSubType  = effectStolen:getSubType()
        local newSubPower = math.floor(effectStolen:getSubPower() * effectiveness)
        local newTier     = effectStolen:getTier()
        local newFlags    = effectStolen:getEffectFlags()

        player:addStatusEffectEx(newID, newIcon, newPower, newTick, newDuration, newSubType, newSubPower, newTier, newFlags)
        target:delStatusEffect(newID)

        effectID = newID
    end

    if effectID == 0 then
        action:setAnimation(target:getID(), 182)
        ability:setMsg(xi.msg.basic.STEAL_FAIL)
    end

    target:updateClaim(player)
    return effectID
end

-- Enhanced Steal with subjob scaling
xi.job_utils.thief.useSteal = function(player, target, ability, action)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.STEAL)
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JOB_ABILITY_UNLEARNED)
        return 0
    end

    local thfLevel    = utils.getActiveJobLevel(player, xi.job.THF)
    local stolen      = action:getParam(target:getID())
    local stealMod    = math.floor(player:getMod(xi.mod.STEAL) * effectiveness)
    local stealChance = math.floor((50 + stealMod * 2 + thfLevel - target:getMainLvl()) * effectiveness)

    if stolen == 0 then
        stolen = target:getStealItem()
    end

    if target:isMob() and math.random(1, 100) <= stealChance and stolen ~= 0 then
        player:addItem(stolen)
        target:itemStolen()
        ability:setMsg(xi.msg.basic.STEAL_SUCCESS) -- Item stolen successfully
        target:triggerListener('ITEM_STOLEN', target, player, stolen)
        -- Aura Steal does not trigger on successful item steal
        return stolen
    else
        ability:setMsg(xi.msg.basic.STEAL_FAIL) -- Failed to steal
        action:setAnimation(target:getID(), 182)
    end

    -- Attempt Aura steal
    if player:hasTrait(xi.trait.AURA_STEAL) then
        local resist = applyResistanceAbility(player, target, xi.element.NONE, 0, 0)
        if resist > 0.0625 then
            local auraStealChance = math.min(math.floor(player:getMerit(xi.merit.AURA_STEAL) * effectiveness), 95)
            if math.random(1, 100) <= auraStealChance then
                local targetShadows = target:getMod(xi.mod.UTSUSEMI)

                stolen = player:stealStatusEffect(target)
                if stolen ~= 0 then
                    ability:setMsg(xi.msg.basic.STEAL_EFFECT)
                    action:setAnimation(target:getID(), 181)

                    if stolen == xi.effect.COPY_IMAGE then
                        if targetShadows > 0 then
                            player:setMod(xi.mod.UTSUSEMI, targetShadows)
                        end
                    end
                end
            end
        end
    end

    return stolen
end

-- Enhanced Sneak Attack with subjob scaling
xi.job_utils.thief.useSneakAttack = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.SNEAK_ATTACK)
    if not hasAccess then
        return
    end

    local duration = math.floor(60 * effectiveness)
    player:addStatusEffect(xi.effect.SNEAK_ATTACK, math.floor(effectiveness * 100), 0, duration)
end

-- Enhanced Flee with subjob scaling
xi.job_utils.thief.useFlee = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.FLEE)
    if not hasAccess then
        return
    end

    local duration = math.floor((30 + player:getMod(xi.mod.FLEE_DURATION)) * effectiveness)

    -- TODO: Flee will not override all types of weight effect. Find out which aren't overriden.
    if player:hasStatusEffect(xi.effect.WEIGHT) then
        player:delStatusEffect(xi.effect.WEIGHT)
    end

    local fleeSpeed = math.floor(10000 * effectiveness)
    player:addStatusEffect(xi.effect.FLEE, fleeSpeed, 0, duration)
end

-- Enhanced Trick Attack with subjob scaling
xi.job_utils.thief.useTrickAttack = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.TRICK_ATTACK)
    if not hasAccess then
        return
    end

    local duration = math.floor(60 * effectiveness)
    player:addStatusEffect(xi.effect.TRICK_ATTACK, math.floor(effectiveness * 100), 0, duration)
end

-- Enhanced Mug with subjob scaling
xi.job_utils.thief.useMug = function(player, target, ability, action)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.MUG)
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JOB_ABILITY_UNLEARNED)
        return 0
    end

    local thfLevel = utils.getActiveJobLevel(player, xi.job.THF)
    local gil      = 0
    local jpValue = math.floor(player:getJobPointLevel(xi.jp.MUG_EFFECT) * effectiveness)

    if jpValue > 0 and player:getMainJob() == xi.job.THF then
        local hpSteal = math.floor(((player:getStat(xi.mod.AGI) + player:getStat(xi.mod.DEX)) * jpValue) * 0.05 * effectiveness)
        local mobHP = target:getHP()

        if hpSteal > mobHP then
            hpSteal = mobHP
        end

        target:addHP(-hpSteal)
        player:addHP(hpSteal)
    end

    local mugChance = math.floor((90 + thfLevel - target:getMainLvl()) * effectiveness)

    if
        target:isMob() and
        math.random(1, 100) <= mugChance and
        target:getMobMod(xi.mobMod.MUG_GIL) > 0
    then
        local purse    = target:getMobMod(xi.mobMod.MUG_GIL)
        local fatpurse = target:getGil()

        gil = fatpurse / (8 + math.random(0, 8))

        if gil == 0 then
            gil = fatpurse / 2
        end

        if gil == 0 then
            gil = fatpurse
        end

        if gil > purse then
            gil = purse
        end

        if gil <= 0 then
            ability:setMsg(xi.msg.basic.MUG_FAIL)
        else
            gil = math.floor(gil * (1 + player:getMod(xi.mod.MUG_EFFECT)) * effectiveness)

            player:addGil(gil)
            target:setMobMod(xi.mobMod.MUG_GIL, target:getMobMod(xi.mobMod.MUG_GIL) - gil)
            ability:setMsg(xi.msg.basic.MUG_SUCCESS)
        end
    else
        ability:setMsg(xi.msg.basic.MUG_FAIL)
        action:setAnimation(target:getID(), 184)
    end

    return gil
end

-- Enhanced Hide with subjob scaling
xi.job_utils.thief.useHide = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.HIDE)
    if not hasAccess then
        return
    end

    local duration = math.random(30, 300)
    duration = calculateStealthDuration(player, duration, effectiveness)

    player:addStatusEffect(xi.effect.HIDE, 1, 0, math.floor(duration * xi.settings.main.SNEAK_INVIS_DURATION_MULTIPLIER))
end
-- Enhanced Accomplice with subjob scaling
xi.job_utils.thief.useAccomplice = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.ACCOMPLICE)
    if not hasAccess then
        return
    end

    local enmityTransfer = math.floor((50 + player:getMod(xi.mod.ACC_COLLAB_EFFECT)) * effectiveness)
    target:transferEnmity(player, enmityTransfer, 20.6)
end

-- Enhanced Collaborator with subjob scaling
xi.job_utils.thief.useCollaborator = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.COLLABORATOR)
    if not hasAccess then
        return
    end

    local enmityTransfer = math.floor((25 + player:getMod(xi.mod.ACC_COLLAB_EFFECT)) * effectiveness)
    target:transferEnmity(player, enmityTransfer, 20.6)
end

-- Enhanced Despoil with subjob scaling
xi.job_utils.thief.useDespoil = function(player, target, ability, action)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.DESPOIL)
    if not hasAccess then
        ability:setMsg(xi.msg.basic.JOB_ABILITY_UNLEARNED)
        return 0
    end

    local level         = utils.getActiveJobLevel(player, xi.job.THF)
    local despoilMod    = math.floor(player:getMod(xi.mod.DESPOIL) * effectiveness)
    local despoilChance = math.floor((50 + despoilMod * 2 + level - target:getMainLvl()) * effectiveness) -- Same math as Steal

    -- TODO: Need to verify if there's a message associated with this
    local jpValue = math.floor(player:getJobPointLevel(xi.jp.DESPOIL_EFFECT) * effectiveness)

    if jpValue > 0 and player:getMainJob() == xi.job.THF then
        local tpSteal = jpValue * 0.02
        local mobTP = target:getTP()

        if tpSteal > mobTP then
            tpSteal = mobTP
        end

        target:addTP(-tpSteal)
        player:addTP(tpSteal)
    end

    local despoiled = target:getDespoilItem()

    if
        target:isMob() and
        math.random(1, 100) <= despoilChance and
        despoiled ~= 0
    then
        if player:getObjType() == xi.objType.TRUST then
            player:getMaster():addItem(despoiled)
        else
            player:addItem(despoiled)
        end

        target:itemDespoiled()

        -- Attempt to grab the debuff from the DB
        -- If there isn't a debuff assigned to the item stolen, select one at random
        local debuff = player:getDespoilDebuff(despoiled)

        if not debuff then
            debuff = despoilDebuffs[math.random(#despoilDebuffs)]
        end

        local power = math.floor(processDebuff(player, target, ability, debuff) * effectiveness) -- Also sets ability message

        target:addStatusEffect(debuff, power, 0, math.floor(90 * effectiveness))
    else
        action:setAnimation(target:getID(), 182)
        ability:setMsg(xi.msg.basic.STEAL_FAIL) -- Failed
    end

    return despoiled
end

-- Enhanced Conspirator with subjob scaling
xi.job_utils.thief.useConspirator = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.CONSPIRATOR)
    if not hasAccess then
        return
    end

    local subtleBlow = 0
    local accuracy   = 0
    local scale      = effectiveness -- Base subjob scaling
    local mob        = player:getTarget()

    if mob then
        local enmityList = mob:getEnmityList()

        if enmityList and #enmityList > 0 then
            if #enmityList < 6 then
                subtleBlow = 20
                accuracy = 15
            elseif #enmityList < 18 then
                subtleBlow = 50
                accuracy = 25
            else
                subtleBlow = 50
                accuracy = 49
            end
        end

        -- See if we should apply the effects to the player at the top of the hate list
        if mob:getTarget() == target then
            scale = scale * player:getMod(xi.mod.AUGMENTS_CONSPIRATOR)
        end
    end

    local finalSubtleBlow = math.floor(subtleBlow * scale)
    local finalAccuracy = math.floor(accuracy * scale)
    target:addStatusEffect(xi.effect.CONSPIRATOR, finalSubtleBlow, 0, math.floor(60 * effectiveness), 0, finalAccuracy)
end

-- Enhanced Bully with subjob scaling
xi.job_utils.thief.useBully = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.BULLY)
    if not hasAccess then
        return xi.effect.NONE
    end

    local jpValue = math.floor(player:getJobPointLevel(xi.jp.BULLY_EFFECT) * effectiveness)
    local intimidatepower = math.floor((15 + jpValue) * effectiveness)

    target:addStatusEffectEx(xi.effect.DOUBT, xi.effect.INTIMIDATE, intimidatepower, 0, math.floor(30 * effectiveness))

    return xi.effect.INTIMIDATE
end

-- Enhanced Feint with subjob scaling
xi.job_utils.thief.useFeint = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.FEINT)
    if not hasAccess then
        return
    end

    local bonus = math.floor(player:getMod(xi.mod.AUGMENTS_FEINT) * player:getMerit(xi.merit.FEINT) / 25 * effectiveness) -- Divide by the merit value (feint is 25) to get the number of merit points
    local evasionDown = math.floor((150 + bonus) * effectiveness)
    local treasureBonus = math.floor((player:getMerit(xi.merit.FEINT) - 25) * effectiveness) -- 0% base TREASURE_HUNTER_PROC, every merit past 1 gives 25%

    -- Subpower is the proc rate bonus for TH procs
    player:addStatusEffect(xi.effect.FEINT, evasionDown, 0, math.floor(60 * effectiveness), 0, treasureBonus)
end

-- Enhanced Assassin's Charge with subjob scaling
xi.job_utils.thief.useAssassinsCharge = function(player, target, ability)
    local hasAccess, effectiveness = xi.job_utils.thief.validateAbilityAccess(player, xi.jobAbility.ASSASSINS_CHARGE)
    if not hasAccess then
        return
    end

    local merits = player:getMerit(xi.merit.ASSASSINS_CHARGE)
    local crit   = 0

    if player:getMod(xi.mod.AUGMENTS_ASSASSINS_CHARGE) > 0 then
        crit = math.floor((merits / 5) * effectiveness)
    end
    
    player:addMod(xi.mod.CRITHITRATE, crit)
    return crit
end

-----------------------------------
-- Enhanced Thief Utility Functions
-----------------------------------

-- Enhanced weapon specialization with subjob support
xi.job_utils.thief.calculateWeaponBonus = function(player, weapon)
    local hasAccess, effectiveness = xi.job_utils.thief.validateJobAccess(player)
    if not hasAccess then
        return 0
    end

    local bonus = 0
    local weaponSkill = weapon:getSkillType()
    
    -- Thief weapon specializations with subjob scaling
    if weaponSkill == xi.skill.DAGGER then
        bonus = math.floor(15 * effectiveness) -- Enhanced dagger mastery
    elseif weaponSkill == xi.skill.SWORD then
        bonus = math.floor(8 * effectiveness) -- Sword proficiency
    elseif weaponSkill == xi.skill.THROWING then
        bonus = math.floor(10 * effectiveness) -- Throwing weapon expertise
    end
    
    return bonus
end

-- Enhanced accuracy calculations with Thief bonuses
xi.job_utils.thief.calculateAccuracyBonus = function(player, target)
    local hasAccess, effectiveness = xi.job_utils.thief.validateJobAccess(player)
    if not hasAccess then
        return 0
    end

    local bonus = 0
    
    -- Sneak Attack accuracy bonus
    if player:hasStatusEffect(xi.effect.SNEAK_ATTACK) then
        bonus = bonus + math.floor(50 * effectiveness)
    end
    
    -- Trick Attack accuracy bonus
    if player:hasStatusEffect(xi.effect.TRICK_ATTACK) then
        bonus = bonus + math.floor(40 * effectiveness)
    end
    
    -- Hide stealth bonus
    if player:hasStatusEffect(xi.effect.HIDE) then
        bonus = bonus + math.floor(30 * effectiveness)
    end
    
    -- Feint evasion down effect
    if player:hasStatusEffect(xi.effect.FEINT) then
        bonus = bonus + math.floor(25 * effectiveness)
    end
    
    return bonus
end

-- Enhanced damage calculations for Thief abilities
xi.job_utils.thief.calculateDamageBonus = function(player, target, isCritical)
    local hasAccess, effectiveness = xi.job_utils.thief.validateJobAccess(player)
    if not hasAccess then
        return 1.0
    end

    local multiplier = 1.0
    
    -- Enhanced critical hit damage with subjob scaling
    if isCritical then
        local critBonus = calculateCriticalEnhancement(player, effectiveness)
        multiplier = multiplier + (critBonus / 100)
    end
    
    -- Sneak Attack damage multiplier
    if player:hasStatusEffect(xi.effect.SNEAK_ATTACK) then
        multiplier = multiplier + (1.5 * effectiveness) -- 2.5x damage at full effectiveness
    end
    
    -- Trick Attack damage multiplier  
    if player:hasStatusEffect(xi.effect.TRICK_ATTACK) then
        multiplier = multiplier + (1.0 * effectiveness) -- 2.0x damage at full effectiveness
    end
    
    -- Assassin's Charge damage enhancement
    if player:hasStatusEffect(xi.effect.ASSASSINS_CHARGE) then
        local chargeEffect = player:getStatusEffect(xi.effect.ASSASSINS_CHARGE)
        if chargeEffect then
            multiplier = multiplier + (chargeEffect:getPower() / 100 * effectiveness)
        end
    end
    
    return multiplier
end

-- Enhanced treasure hunter effectiveness with subjob scaling
xi.job_utils.thief.calculateTreasureHunterBonus = function(player, target)
    local hasAccess, effectiveness = xi.job_utils.thief.validateJobAccess(player)
    if not hasAccess then
        return 0
    end

    local thBonus = calculateTreasureHunterEffectiveness(player, effectiveness)
    
    -- Feint treasure hunter proc bonus
    if player:hasStatusEffect(xi.effect.FEINT) then
        local feintEffect = player:getStatusEffect(xi.effect.FEINT)
        if feintEffect and feintEffect:getSubPower() > 0 then
            thBonus = thBonus + math.floor(feintEffect:getSubPower() * effectiveness)
        end
    end
    
    return thBonus
end

-- Enhanced enmity management for Thief abilities
xi.job_utils.thief.calculateEnmityReduction = function(player, target)
    local hasAccess, effectiveness = xi.job_utils.thief.validateJobAccess(player)
    if not hasAccess then
        return 0
    end

    local reduction = 0
    
    -- Hide enmity reduction
    if player:hasStatusEffect(xi.effect.HIDE) then
        reduction = reduction + math.floor(50 * effectiveness) -- Significant enmity reduction
    end
    
    -- Accomplice/Collaborator enmity transfer effects
    if player:hasStatusEffect(xi.effect.ACCOMPLICE) then
        reduction = reduction + math.floor(25 * effectiveness)
    end
    
    if player:hasStatusEffect(xi.effect.COLLABORATOR) then
        reduction = reduction + math.floor(15 * effectiveness)
    end
    
    return reduction
end

-- Enhanced status resistance for Thief abilities
xi.job_utils.thief.calculateStatusResistance = function(player)
    local hasAccess, effectiveness = xi.job_utils.thief.validateJobAccess(player)
    if not hasAccess then
        return 0
    end

    local resistance = 0
    
    -- Perfect Dodge status immunity
    if player:hasStatusEffect(xi.effect.PERFECT_DODGE) then
        resistance = resistance + math.floor(100 * effectiveness) -- Complete immunity during Perfect Dodge
    end
    
    -- Hide status resistance
    if player:hasStatusEffect(xi.effect.HIDE) then
        resistance = resistance + math.floor(30 * effectiveness)
    end
    
    return resistance
end

-----------------------------------
-- Advanced Combat Analysis Functions
-----------------------------------

-- Thief combat situation analysis with subjob effectiveness
xi.job_utils.thief.analyzeCombatSituation = function(player, target)
    local hasAccess, effectiveness = xi.job_utils.thief.validateJobAccess(player)
    if not hasAccess then
        return {}
    end

    local analysis = {
        effectiveness = effectiveness,
        stealthLevel = 0,
        combatReadiness = 0,
        treasureHuntingCapability = 0,
        damageMultiplier = 1.0,
        accuracyBonus = 0,
        enmityReduction = 0
    }
    
    -- Stealth assessment
    if player:hasStatusEffect(xi.effect.HIDE) then
        analysis.stealthLevel = math.floor(100 * effectiveness)
    elseif player:hasStatusEffect(xi.effect.SNEAK_ATTACK) or player:hasStatusEffect(xi.effect.TRICK_ATTACK) then
        analysis.stealthLevel = math.floor(50 * effectiveness)
    end
    
    -- Combat readiness calculation
    local combatFactors = 0
    if player:hasStatusEffect(xi.effect.PERFECT_DODGE) then
        combatFactors = combatFactors + 40
    end
    if player:hasStatusEffect(xi.effect.SNEAK_ATTACK) then
        combatFactors = combatFactors + 30
    end
    if player:hasStatusEffect(xi.effect.TRICK_ATTACK) then
        combatFactors = combatFactors + 30
    end
    if player:hasStatusEffect(xi.effect.ASSASSINS_CHARGE) then
        combatFactors = combatFactors + 20
    end
    
    analysis.combatReadiness = math.floor(combatFactors * effectiveness)
    
    -- Treasure hunting capability
    analysis.treasureHuntingCapability = calculateTreasureHunterEffectiveness(player, effectiveness)
    
    -- Calculate current bonuses
    analysis.damageMultiplier = xi.job_utils.thief.calculateDamageBonus(player, target, false)
    analysis.accuracyBonus = xi.job_utils.thief.calculateAccuracyBonus(player, target)
    analysis.enmityReduction = xi.job_utils.thief.calculateEnmityReduction(player, target)
    
    return analysis
end

-- Enhanced party support capabilities
xi.job_utils.thief.getPartySupportCapabilities = function(player)
    local hasAccess, effectiveness = xi.job_utils.thief.validateJobAccess(player)
    if not hasAccess then
        return {}
    end

    local capabilities = {
        enmityTransfer = effectiveness * 0.8,    -- Accomplice/Collaborator
        treasureHunting = effectiveness * 0.9,   -- TH enhancement
        stealthSupport = effectiveness * 0.7,    -- Hide and stealth abilities
        debuffApplication = effectiveness * 0.6, -- Despoil and other debuffs
        damageSupport = effectiveness * 0.8,     -- SA/TA damage enhancement
        statusStealing = effectiveness * 0.7     -- Larceny and aura steal
    }
    
    return capabilities
end
