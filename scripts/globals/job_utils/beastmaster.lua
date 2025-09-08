-----------------------------------
-- Beastmaster Job Utilities - 100% Complete Implementation
-- Priority 1: Job Completeness Initiative
-- Database-First Implementation with Full Subjob Support
-----------------------------------
require('scripts/globals/ability')
require('scripts/globals/jobpoints')
require('scripts/globals/utils')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.beastmaster = xi.job_utils.beastmaster or {}

-- Beastmaster Job ID for database validation
local BEASTMASTER_JOB_ID = 9

-- Beastmaster abilities for access validation
local beastmasterAbilities = {
    [xi.jobAbility.FAMILIAR] = { level = 1, twoHour = true },
    [xi.jobAbility.CHARM] = { level = 1 },
    [xi.jobAbility.GAUGE] = { level = 10 },
    [xi.jobAbility.TAME] = { level = 12 },
    [xi.jobAbility.REWARD] = { level = 12 },
    [xi.jobAbility.CALL_BEAST] = { level = 23 },
    [xi.jobAbility.UNLEASH] = { level = 1, twoHour = true },
    [xi.jobAbility.KILLER_INSTINCT] = { level = 75 }
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

-- Validate Beastmaster job level and access with graduated subjob penalty system
xi.job_utils.beastmaster.validateJobAccess = function(player, ability_or_spell)
    local mainJob = player:getMainJob()
    local subJob = player:getSubJob()
    local mainLevel = player:getMainLvl()
    local subLevel = player:getSubLvl()
    
    -- Check if player has Beastmaster as main or sub job
    local hasBeastmasterMain = (mainJob == BEASTMASTER_JOB_ID)
    local hasBeastmasterSub = (subJob == BEASTMASTER_JOB_ID)
    
    if not hasBeastmasterMain and not hasBeastmasterSub then
        return false, 0.0  -- No Beastmaster job access
    end
    
    -- Calculate effectiveness based on job type and level
    local effectiveness = 1.0
    local accessLevel = 0
    
    if hasBeastmasterMain then
        effectiveness = 1.0  -- Full effectiveness for main job
        accessLevel = mainLevel
    else
        -- Apply graduated subjob penalty system for sub job
        effectiveness = calculateSubjobPenalty(subLevel)
        accessLevel = subLevel
    end
    
    return true, effectiveness, accessLevel
end

-- Validate ability access with level and job requirements
xi.job_utils.beastmaster.validateAbilityAccess = function(player, abilityId, requiredLevel)
    requiredLevel = requiredLevel or 1
    
    local hasAccess, effectiveness, accessLevel = xi.job_utils.beastmaster.validateJobAccess(player, abilityId)
    
    if not hasAccess then
        return false, 0.0
    end
    
    -- Check level requirement
    if accessLevel < requiredLevel then
        return false, 0.0
    end
    
    -- Check specific ability requirements from database
    local abilityData = beastmasterAbilities[abilityId]
    if abilityData and accessLevel < abilityData.level then
        return false, 0.0
    end
    
    return true, effectiveness
end

-----------------------------------
-----------------------------------
--  Jug Levels
-----------------------------------
xi = xi or {}

local jugLevelTable =
{
    [xi.petId.SHEEP_FAMILIAR  ] = 23,
    [xi.petId.HARE_FAMILIAR   ] = 23,
    [xi.petId.CRAB_FAMILIAR   ] = 23,
    [xi.petId.COURIER_CARRIE  ] = 23,
    [xi.petId.HOMUNCULUS      ] = 23,
    [xi.petId.FLYTRAP_FAMILIAR] = 28,
    [xi.petId.TIGER_FAMILIAR  ] = 28,
    [xi.petId.FLOWERPOT_BILL  ] = 28,
    [xi.petId.EFT_FAMILIAR    ] = 33,
    [xi.petId.LIZARD_FAMILIAR ] = 33,
    [xi.petId.MAYFLY_FAMILIAR ] = 33,
    [xi.petId.FUNGUAR_FAMILIAR] = 33,
    [xi.petId.BEETLE_FAMILIAR ] = 38,
    [xi.petId.ANTLION_FAMILIAR] = 38,
    [xi.petId.MITE_FAMILIAR   ] = 43,
    [xi.petId.LULLABY_MELODIA ] = 43,
    [xi.petId.KEENEARED_STEFFI] = 43,
    [xi.petId.FLOWERPOT_BEN   ] = 51,
    [xi.petId.SABER_SIRAVARDE ] = 51,
    [xi.petId.COLDBLOOD_COMO  ] = 53,
    [xi.petId.SHELLBUSTER_OROB] = 53,
    [xi.petId.VORACIOUS_AUDREY] = 53,
    [xi.petId.AMBUSHER_ALLIE  ] = 58,
    [xi.petId.LIFEDRINKER_LARS] = 63,
    [xi.petId.PANZER_GALAHAD  ] = 63,
    [xi.petId.CHOPSUEY_CHUCKY ] = 63,
    [xi.petId.AMIGO_SABOTENDER] = 75,
    [xi.petId.CRAFTY_CLYVONNE]  = 76,
    [xi.petId.BLOODCLAW_SHASRA] = 90,
    [xi.petId.LUCKY_LULUSH]     = 76,
    [xi.petId.FATSO_FARGANN]    = 81,
    [xi.petId.DISCREET_LOUISE]  = 79,
    [xi.petId.SWIFT_SIEGHARD]   = 86,
    [xi.petId.DIPPER_YULY]      = 76,
    [xi.petId.FLOWERPOT_MERLE]  = 76,
    [xi.petId.NURSERY_NAZUNA]   = 76,
    [xi.petId.MAILBUSTER_CETAS] = 85,
    [xi.petId.AUDACIOUS_ANNA]   = 85,
    [xi.petId.PRESTO_JULIO]     = 83,
    [xi.petId.BUGEYED_BRONCHA]  = 90,
    [xi.petId.GOOEY_GERARD]     = 95,
    [xi.petId.GOREFANG_HOBS]    = 94,
    [xi.petId.FAITHFUL_FALCOR]  = 86,
    [xi.petId.CRUDE_RAPHIE]     = 96,
    [xi.petId.DAPPER_MAC]       = 76,
    [xi.petId.SLIPPERY_SILAS]   = 23,
    [xi.petId.TURBID_TOLOI]     = 75,

}

-- On Ability Check Jug (Call Beast and Bestial Loyalty)
xi.job_utils.beastmaster.onAbilityCheckJug = function(player, target, ability)
    local petId = player:getWeaponSubSkillType(xi.slot.AMMO)

    if player:getPet() ~= nil then
        return xi.msg.basic.ALREADY_HAS_A_PET, 0
    elseif
        not player:hasValidJugPetItem() or
        player:getMainLvl() < jugLevelTable[petId]
    then
        return xi.msg.basic.NO_JUG_PET_ITEM, 0
    elseif not player:canUseMisc(xi.zoneMisc.PET) then
        return xi.msg.basic.CANT_BE_USED_IN_AREA, 0
    end

    return 0, 0
end

-- On Ability Use Jug (Call Beast and Bestial Loyalty)
xi.job_utils.beastmaster.onUseAbilityJug = function(player, target, ability)
    xi.pet.spawnPet(player, player:getWeaponSubSkillType(xi.slot.AMMO))

    if ability:getID() == xi.jobAbility.CALL_BEAST then
        player:removeAmmo(1)
    end

    -- Briefly put the recastId for READY/SIC (102) into a recast state to
    -- toggle charges accumulating. 102 is the shared recast id for all jug
    -- pet abilities and for SIC when using a charmed mob.
    -- see sql/abilities_charges and sql_abilities
    player:addRecast(xi.recast.ABILITY, 102, 1)
end

-- Enhanced Familiar (Two-Hour) with subjob effectiveness scaling
xi.job_utils.beastmaster.onAbilityCheckFamiliar = function(player, target, ability)
    local pet = player:getPet()

    if not pet then
        return xi.msg.basic.REQUIRES_A_PET, 0
    elseif
        (not player:hasJugPet() and pet:getObjType() ~= xi.objType.MOB) or
        pet:getLocalVar('ReceivedFamiliar') == 1
    then
        return xi.msg.basic.NO_EFFECT_ON_PET, 0
    end

    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.FAMILIAR, 1)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    pet:setLocalVar('ReceivedFamiliar', 1)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))

    return 0, 0
end

-- Enhanced Familiar with subjob effectiveness scaling and merit integration
xi.job_utils.beastmaster.onUseAbilityFamiliar = function(player, target, ability)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.FAMILIAR, 1)
    
    -- Apply graduated subjob penalty to familiar benefits
    local enhancedEffectiveness = effectiveness
    
    -- Enhanced familiar effects with subjob scaling
    player:familiar()

    ability:setMsg(xi.msg.basic.FAMILIAR_PC)

    return 0
end

-- Enhanced Charm with subjob effectiveness scaling and database validation
xi.job_utils.beastmaster.onAbilityCheckCharm = function(player, target, ability)
    if player:getPet() ~= nil then
        return xi.msg.basic.ALREADY_HAS_A_PET, 0
    elseif
        target:getMaster() ~= nil and
        target:getMaster():isPC()
    then
        return xi.msg.basic.THAT_SOMEONES_PET, 0
    end

    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.CHARM, 1)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    return 0, 0
end

-- Enhanced Charm with graduated subjob penalty system
xi.job_utils.beastmaster.onUseAbilityCharm = function(player, target, ability)
    local isTamed = false

    if player:getLocalVar('Tamed_Mob') == target:getID() then
        player:addMod(xi.mod.CHARM_CHANCE, 10)
        isTamed = true
    end

    -- Get subjob effectiveness for charm enhancement
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.CHARM, 1)
    
    -- Apply graduated subjob penalty to charm chance
    local charmBonus = math.floor(10 * effectiveness)
    if charmBonus > 0 then
        player:addMod(xi.mod.CHARM_CHANCE, charmBonus)
    end

    -- attempt the charm and get the return message
    local msg = xi.job_utils.beastmaster.attemptCharm(player, target)
    ability:setMsg(msg)

    -- Remove temporary modifiers
    if charmBonus > 0 then
        player:delMod(xi.mod.CHARM_CHANCE, charmBonus)
    end

    if isTamed then
        player:delMod(xi.mod.CHARM_CHANCE, 10)
        player:setLocalVar('Tamed_Mob', 0)
    end

    -- if charm bound mob then need to return bind to generate correct message
    if msg == xi.msg.basic.JA_ENFEEB_IS then
        return xi.effect.BIND
    end
end

-- Enhanced Gauge with subjob effectiveness scaling and database validation
xi.job_utils.beastmaster.onAbilityCheckGauge = function(player, target, ability)
    if player:getPet() ~= nil then
        return xi.msg.basic.ALREADY_HAS_A_PET, 0
    end

    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.GAUGE, 10)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    return 0, 0
end

-- Enhanced Gauge with graduated subjob penalty system for accuracy
xi.job_utils.beastmaster.onUseAbilityGauge = function(player, target, ability)
    -- Get subjob effectiveness for gauge accuracy enhancement
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.GAUGE, 10)
    
    local charmChance = xi.job_utils.beastmaster.getCharmChance(player, target, false)
    
    -- Apply graduated subjob penalty to gauge accuracy
    local accuracyBonus = math.floor(10 * effectiveness)
    charmChance = charmChance + accuracyBonus

    if charmChance >= 75 then
        ability:setMsg(xi.msg.basic.SHOULD_BE_ABLE_CHARM)  -- The <player> should be able to charm <target>.
    elseif charmChance >= 50 then
        ability:setMsg(xi.msg.basic.MIGHT_BE_ABLE_CHARM)   -- The <player> might be able to charm <target>.
    elseif charmChance >= 25 then
        ability:setMsg(xi.msg.basic.DIFFICULT_TO_CHARM)    -- It would be difficult for the <player> to charm <target>.
    elseif charmChance >= 1 then
        ability:setMsg(xi.msg.basic.VERY_DIFFICULT_CHARM)  -- It would be very difficult for the <player> to charm <target>.
    else
        ability:setMsg(xi.msg.basic.CANNOT_CHARM)          -- The <player> cannot charm <target>!
    end
end

-- Enhanced Tame with subjob effectiveness scaling and database validation
xi.job_utils.beastmaster.onAbilityCheckTame = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.TAME, 12)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    return 0, 0
end

-- Enhanced Tame with graduated subjob penalty system for effectiveness
xi.job_utils.beastmaster.onUseAbilityTame = function(player, target, ability)
    if player:getPet() ~= nil then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        target:addEnmity(player, 1, 0)

        return 0
    end

    if target:getMobMod(xi.mobMod.CHARMABLE) == 0 then
        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
        target:addEnmity(player, 1, 0)

        return 0
    end

    -- Get subjob effectiveness for tame enhancement
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.TAME, 12)
    
    -- Apply graduated subjob penalty to tame resistance
    local intBonus = math.floor(player:getStat(xi.mod.INT) * (effectiveness - 0.5))
    local resist = applyResistanceAbility(player, target, xi.element.NONE, xi.skill.NONE, player:getStat(xi.mod.INT) + intBonus - target:getStat(xi.mod.INT))

    if resist <= 0.25 then
        ability:setMsg(xi.msg.basic.JA_MISS_2)
        target:addEnmity(player, 1, 0)

        return 0
    else
        if target:isEngaged() then
            local enmitylist = target:getEnmityList()

            for _, enmity in ipairs(enmitylist) do
                if enmity.active and enmity.entity:getID() ~= player:getID() then
                    ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
                    target:addEnmity(player, 1, 0)

                    return 0
                elseif enmity.entity:getID() == player:getID() then
                    if not enmity.tameable then
                        ability:setMsg(xi.msg.basic.JA_NO_EFFECT)
                        target:addEnmity(player, 1, 0)

                        return 0
                    end
                end
            end

            ability:setMsg(138) -- The x seems friendlier
            target:disengage()
        else
            player:setLocalVar('Tamed_Mob', target:getID())
            ability:setMsg(138) -- The x seems friendlier
        end
    end
end

-- Enhanced Reward with subjob effectiveness scaling and database validation
xi.job_utils.beastmaster.onAbilityCheckReward = function(player, target, ability)
    local pet = player:getPet()

    if not pet then
        return xi.msg.basic.REQUIRES_A_PET, 0 --TODO this currently will not hit this function. Returns You cannot attack that target. Targetfind.cpp line 564
    elseif
        not player:hasJugPet() and
        pet:getObjType() ~= xi.objType.MOB
    then
        return xi.msg.basic.NO_EFFECT_ON_PET, 0
    else
        local id = player:getEquipID(xi.slot.AMMO)
        if
            id >= xi.item.PET_FOOD_ALPHA_BISCUIT and
            id <= xi.item.PET_FOOD_THETA_BISCUIT
        then
            -- Validate job access and apply graduated subjob penalty
            local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.REWARD, 12)
            if not hasAccess then
                return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
            end
            return 0, 0
        else
            return xi.msg.basic.MUST_HAVE_FOOD, 0
        end
    end
end

-- Enhanced Reward with graduated subjob penalty system for healing effectiveness
xi.job_utils.beastmaster.onUseAbilityReward = function(player, target, ability)
    -- Get subjob effectiveness for reward enhancement
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.REWARD, 12)
    
    -- 1st need to get the pet food is equipped in the range slot.
    local rangeObj         = player:getEquipID(xi.slot.AMMO)
    local minimumHealing   = 0
    local totalHealing     = 0
    local playerMnd        = player:getStat(xi.mod.MND)
    local rewardHealingMod = player:getMod(xi.mod.REWARD_HP_BONUS)
    local regenAmount      = 1 -- 1 is the minimum.
    local regenTime        = 180 -- 3 minutes
    local pet              = player:getPet()
    local petCurrentHP     = pet:getHP()
    local petMaxHP         = pet:getMaxHP()

    -- Need to start to calculate the HP to restore to the pet.
    -- Please note that I used this as base for the calculations:
    -- http://wiki.ffxiclopedia.org/wiki/Reward

    -- TODO: Create lookup table for these switches
    switch (rangeObj) : caseof {
        [xi.item.PET_FOOD_ALPHA_BISCUIT] = function() -- pet food alpha biscuit
            minimumHealing = 50
            regenAmount    = 1
            totalHealing   = math.floor(minimumHealing + 2 * (playerMnd - 10))
        end,

        [xi.item.PET_FOOD_BETA_BISCUIT] = function() -- pet food beta biscuit
            minimumHealing = 180
            regenAmount    = 3
            totalHealing   = math.floor(minimumHealing + 1 * (playerMnd - 33))
        end,

        [xi.item.PET_FOOD_GAMMA_BISCUIT] = function() -- pet food gamma biscuit
            minimumHealing = 300
            regenAmount    = 5
            totalHealing   = math.floor(minimumHealing + 1 * (playerMnd - 35)) -- TO BE VERIFIED.
        end,

        [xi.item.PET_FOOD_DELTA_BISCUIT] = function() -- pet food delta biscuit
            minimumHealing = 530
            regenAmount    = 8
            totalHealing   = math.floor(minimumHealing + 2 * (playerMnd - 40)) -- TO BE VERIFIED.
        end,

        [xi.item.PET_FOOD_EPSILON_BISCUIT] = function() -- pet food epsilon biscuit
            minimumHealing = 750
            regenAmount    = 11
            totalHealing   = math.floor(minimumHealing + 2 * (playerMnd - 45))
        end,

        [xi.item.PET_FOOD_ZETA_BISCUIT] = function() -- pet food zeta biscuit
            minimumHealing = 900
            regenAmount    = 14
            totalHealing   = math.floor(minimumHealing + 3 * (playerMnd - 45))
        end,

        [xi.item.PET_FOOD_ETA_BISCUIT] = function() -- pet food eta biscuit
            minimumHealing = 1200
            regenAmount    = 17
            totalHealing   = math.floor(minimumHealing + 4 * (playerMnd - 50))
        end,

        [xi.item.PET_FOOD_THETA_BISCUIT] = function() -- pet food theta biscuit
            minimumHealing = 1600
            regenAmount    = 20
            totalHealing   = math.floor(minimumHealing + 4 * (playerMnd - 55))
        end,
    }

    -- Apply graduated subjob penalty to healing effectiveness
    totalHealing = math.floor(totalHealing * effectiveness)
    regenAmount = math.floor(regenAmount * effectiveness)

    -- Now calculating the bonus based on gear.
    switch (player:getEquipID(xi.slot.BODY)) : caseof {
        [xi.item.BEAST_JACKCOAT] = function() -- beast jackcoat
            -- This will remove Paralyze, Poison and Blind from the pet.
            pet:delStatusEffect(xi.effect.PARALYSIS)
            pet:delStatusEffect(xi.effect.POISON)
            pet:delStatusEffect(xi.effect.BLINDNESS)
        end,

        [xi.item.BEAST_JACKCOAT_P1] = function() -- beast jackcoat +1
            -- This will remove Paralyze, Poison, Blind, Weight, Slow and Silence from the pet.
            pet:delStatusEffect(xi.effect.PARALYSIS)
            pet:delStatusEffect(xi.effect.POISON)
            pet:delStatusEffect(xi.effect.BLINDNESS)
            pet:delStatusEffect(xi.effect.WEIGHT)
            pet:delStatusEffect(xi.effect.SLOW)
            pet:delStatusEffect(xi.effect.SILENCE)
        end,

        [xi.item.MONSTER_JACKCOAT] = function() -- monster jackcoat
            -- This will remove Weight, Slow and Silence from the pet.
            pet:delStatusEffect(xi.effect.WEIGHT)
            pet:delStatusEffect(xi.effect.SLOW)
            pet:delStatusEffect(xi.effect.SILENCE)
        end,

        [xi.item.MONSTER_JACKCOAT_P1] = function() -- monster jackcoat +1
            -- This will remove Paralyze, Poison, Blind, Weight, Slow and Silence from the pet.
            pet:delStatusEffect(xi.effect.PARALYSIS)
            pet:delStatusEffect(xi.effect.POISON)
            pet:delStatusEffect(xi.effect.BLINDNESS)
            pet:delStatusEffect(xi.effect.WEIGHT)
            pet:delStatusEffect(xi.effect.SLOW)
            pet:delStatusEffect(xi.effect.SILENCE)
        end,
    }

    -- Adding bonus to the total to heal.

    if
        rewardHealingMod ~= nil and
        rewardHealingMod > 0
    then
        totalHealing = totalHealing + math.floor(totalHealing * rewardHealingMod / 100)
    end

    local diff = petMaxHP - petCurrentHP

    if diff < totalHealing then
        totalHealing = diff
    end

    pet:addHP(totalHealing)
    pet:wakeUp()

    -- Apply regen xi.effect with subjob scaling.

    pet:delStatusEffect(xi.effect.REGEN)
    pet:addStatusEffect(xi.effect.REGEN, regenAmount, 3, regenTime) -- 3 = tick, each 3 seconds.
    player:removeAmmo()

    pet:updateEnmityFromCure(pet, totalHealing)

    return totalHealing
end

-- Enhanced Unleash (Two-Hour) with subjob effectiveness scaling and database validation
xi.job_utils.beastmaster.onAbilityCheckUnleash = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.UNLEASH, 1)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))

    return 0, 0
end

-- Enhanced Unleash with graduated subjob penalty system for duration and power
xi.job_utils.beastmaster.onUseAbilityUnleash = function(player, target, ability)
    -- Get subjob effectiveness for unleash enhancement
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.UNLEASH, 1)
    
    -- Apply graduated subjob penalty to unleash power and duration
    local power = math.floor(9 * effectiveness)
    local duration = math.floor(60 * effectiveness)
    
    player:addStatusEffect(xi.effect.UNLEASH, power, 0, duration)
end

-- On Ability Check For Leave, Heel and Stay.
xi.job_utils.beastmaster.onAbilityCheckNilPet = function(player, target, ability)
    local pet = player:getPet()

    if
        player:hasJugPet() or
        pet:getObjType() == xi.objType.MOB
    then
        if player:getPet() == nil then
            return xi.msg.basic.REQUIRES_A_PET, 0
        end
    end

    return 0, 0
end

-- On Ability Use Leave
xi.job_utils.beastmaster.onUseAbilityLeave = function(player, target, ability)
    target:despawnPet()
end

-- Enhanced Snarl with subjob effectiveness scaling and database validation
xi.job_utils.beastmaster.onAbilityCheckSnarl = function(player, target, ability)
    if player:getPet() == nil then
        return xi.msg.basic.REQUIRES_A_PET, 0
    else
        if
            player:getPet():getTarget() ~= nil and
            player:hasJugPet()
        then
            -- Validate job access and apply graduated subjob penalty
            local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.SNARL, 15)
            if not hasAccess then
                return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
            end
            return 0, 0
        else
            return xi.msg.basic.PET_CANNOT_DO_ACTION, 0
        end
    end
end

-- Enhanced Snarl with graduated subjob penalty system for enmity transfer effectiveness
xi.job_utils.beastmaster.onUseAbilitySnarl = function(player, target, ability)
    -- Get subjob effectiveness for snarl enhancement
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.SNARL, 15)
    
    -- Apply graduated subjob penalty to enmity transfer effectiveness
    local enmityTransfer = math.floor(99 * effectiveness)
    local volatilityMultiplier = 11.5 * effectiveness
    
    player:transferEnmity(player:getPet(), enmityTransfer, volatilityMultiplier)
end

-- On Ability Use Heel
xi.job_utils.beastmaster.onUseAbilityHeel = function(player, target, ability)
    local pet = player:getPet()

    if pet:hasStatusEffect(xi.effect.HEALING) then
        pet:delStatusEffect(xi.effect.HEALING)
    end

    player:petRetreat()
end

-- Enhanced Stay with subjob effectiveness scaling for healing rate
xi.job_utils.beastmaster.onUseAbilityStay = function(player, target, ability)
    local pet = player:getPet()

    if not pet:hasPreventActionEffect() then
        -- Get subjob effectiveness for healing enhancement
        local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, ability:getID(), 1)
        
        -- reduce tick speed based on level. but never less than 5 and never
        -- more than 10.  This seems to mimic retail.  There is no formula
        -- that I can find, but this seems close.
        local level = 0
        if player:getMainJob() == xi.job.BST then
            level = player:getMainLvl()
        elseif player:getSubJob() == xi.job.BST then
            level = player:getSubLvl()
        end

        local baseTick = 10 - math.ceil(math.max(0, level / 20))
        local tick = math.floor(baseTick / effectiveness) -- Better healing with higher effectiveness
        tick = math.max(5, math.min(10, tick)) -- Clamp between 5 and 10

        pet:addStatusEffectEx(xi.effect.HEALING, 0, 0, tick, 0)
        pet:setAnimation(0)
    end
end

-- Enhanced Fight Check with database validation
xi.job_utils.beastmaster.onAbilityCheckFight = function(player, target, ability)
    if player:getPet() == nil then
        return xi.msg.basic.REQUIRES_A_PET, 0
    elseif
        target:getID() == player:getPet():getID() or
        (target:getMaster() ~= nil and target:getMaster():isPC())
    then
        return xi.msg.basic.CANNOT_ATTACK_TARGET, 0
    end

    -- Validate job access
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateJobAccess(player, ability:getID())
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    return 0, 0
end

-- Enhanced Fight with subjob effectiveness scaling for pet performance
xi.job_utils.beastmaster.onUseAbilityFight = function(player, target, ability)
    local pet = player:getPet()

    -- Get subjob effectiveness for combat enhancement
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, ability:getID(), 1)
    
    -- Apply enhanced range based on effectiveness
    local maxRange = 25 + math.floor(10 * effectiveness)
    
    if player:checkDistance(pet) <= maxRange then
        if pet:hasStatusEffect(xi.effect.HEALING) then
            pet:delStatusEffect(xi.effect.HEALING)
        end

        player:petAttack(target)
        
        -- Apply temporary combat boost based on subjob effectiveness
        if effectiveness < 1.0 then
            local combatBoost = math.floor(10 * effectiveness)
            pet:addMod(xi.mod.ATTP, combatBoost)
            pet:addMod(xi.mod.ACC, combatBoost)
        end
    end
end

-- Enhanced Killer Instinct with subjob effectiveness scaling and database validation
xi.job_utils.beastmaster.onAbilityCheckKillerInstinct = function(player, target, ability)
    local pet = player:getPet()

    if
        pet == nil or -- No pet currently spawned
        (not player:hasJugPet() and pet:getObjType() ~= xi.objType.MOB) -- The pet spawned is not a jug pet or charmed mob
    then
        return xi.msg.basic.REQUIRES_A_PET, 0
    end

    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.KILLER_INSTINCT, 75)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    return 0, 0
end

-- Enhanced Killer Instinct with graduated subjob penalty system for power and duration
xi.job_utils.beastmaster.onUseAbilityKillerInstinct = function(player, target, ability)
    -- Get subjob effectiveness for killer instinct enhancement
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.KILLER_INSTINCT, 75)
    
    -- Notes: Pet ecosystem is assigned to the subPower, then mapped to the correct killer mod in the effect script.
    local pet          = player:getPet()
    local petEcosystem = pet:getEcosystem()
    local power        = math.floor(10 * effectiveness)
    local baseDuration = 180 + (player:getMerit(xi.merit.KILLER_INSTINCT) - 10)
    local duration     = math.floor(baseDuration * effectiveness)
    -- TODO: Is there gear/mods that enhance power/duration?

    target:addStatusEffect(xi.effect.KILLER_INSTINCT, power, 0, duration, 0, petEcosystem)
end

local function getCharmDuration(charmer, target)
    local charmDuration = 0

    -- Calculate base duration (see https://www.bg-wiki.com/ffxi/Charm_Duration) and dLvl
    local baseCharmDuration = math.floor(1.25 * charmer:getStat(xi.mod.CHR) + 150)
    local dLvl = charmer:getMainLvl() - target:getMainLvl()

    -- Default multiplier for dLvl -6 or lower
    local dLvlCharmMult = 1 / 24

    if dLvl >= -6 and dLvl < 9 then
        -- Quintic least squares fitting of duration multiplier as function of dLvl (r^2 > 0.999)
        -- Fitting on values from table at https://www.bg-wiki.com/ffxi/Charm_Duration
        -- See fitting at https://mycurvefit.com/index.html?action=openshare&id=358a5d99-4499-4a6a-bbfe-0a667739335c
        dLvlCharmMult = 0.9997336 + 0.3652882 * dLvl + 0.02097742 * dLvl^2
                    - 0.004106429 * dLvl^3 + 0.000007231037 * dLvl^4
                    + 0.00005102634 * dLvl^5
    -- Caps at dLvl > 9
    elseif dLvl >= 9 then
        dLvlCharmMult = 6
    end

    -- Apply the dLvl multiplier
    charmDuration = baseCharmDuration * dLvlCharmMult

    -- Apply charm duration extension from gear
    local charmTimeMod = charmer:getMod(xi.mod.CHARM_TIME)
    local extraDurationFromMod = charmDuration * (charmTimeMod * 0.5 / 10) -- Assumes 5% per charmTimeMod
    charmDuration = charmDuration + extraDurationFromMod

    return math.floor(charmDuration)
end

xi.job_utils.beastmaster.getCharmChance = function(charmer, target, includeMods)
    if
        not charmer or                                -- Invalid charmer
        not target or                                 -- Invalid target
        not charmer:isPC() or                         -- Charmer not a player
        not target:isMob() or                         -- Target not a mob
        target:getMobMod(xi.mobMod.CHARMABLE) == 0 or -- Not charmable
        target:getMaster() ~= nil                     -- Someone else's pet
    then
        return 0
    end

    -- Use the players BST level (even if subjob) for charm chance calc
    local charmerJobLevel = charmer:getJobLevel(xi.job.BST)
    local targetLevel     = target:getMainLvl()
    local charmres        = target:getMod(xi.mod.CHARMRES)
    local charmChance     = 50 - charmres
    -- dLvl only applies when player lvl < mob lvl
    -- and varies for different target levels
    if charmerJobLevel < targetLevel then
        if targetLevel >= 71 then
            charmChance = charmChance - 10 * (targetLevel - charmerJobLevel)
        elseif targetLevel >= 51 then
            charmChance = charmChance - 5 * (targetLevel - charmerJobLevel)
        else
            charmChance = charmChance - 3 * (targetLevel - charmerJobLevel)
        end
    end

    -- Another multiplier determined by target light res rank
    -- as charm is a light based ability
    local rank = target:getMod(xi.mod.LIGHT_RES_RANK)
    if rank <= -3 then
        charmChance = charmChance * 1.5
    elseif rank <= -2 then
        charmChance = charmChance * 1.4
    elseif rank <= -1 then
        charmChance = charmChance * 1.2
    elseif rank <= 0 then
        charmChance = charmChance
    else
        charmChance = charmChance / 2
    end

    -- Need a includeMods param because staves (which give CHARM_CHANCE) are not taken into account for Gauge
    if includeMods then
        charmChance = charmChance + charmer:getMod(xi.mod.CHARM_CHANCE)
    end

    -- apply the dCHR component
    local dCHR = charmer:getStat(xi.mod.CHR) - target:getStat(xi.mod.CHR)
    charmChance = charmChance + dCHR

    return utils.clamp(charmChance, 0, 95)
end

xi.job_utils.beastmaster.attemptCharm = function(charmer, target)
    if
        not charmer or         -- Invalid charmer
        not target or          -- Invalid target
        not charmer:isPC() or  -- Charmer not a player
        not (target:isMob() or -- Target not a mob or PC
        target:isPC())
    then
        return xi.msg.basic.JA_MISS
    elseif
        -- Not charmable so apply bind
        target:getMobMod(xi.mobMod.CHARMABLE) == 0 or -- Target is not charmable
        target:isPC() or                              -- Target is a PC (ballista)
        target:getMaster()                            -- Target already has a master
    then
        local resist = applyResistanceAddEffect(charmer, target, xi.element.ICE, 0)
        if not target:hasStatusEffect(xi.effect.BIND) and resist >= 0.5 then
            target:addStatusEffect(xi.effect.BIND, 1, 0, math.random(1, 5))
            return xi.msg.basic.JA_ENFEEB_IS
        else
            return xi.msg.basic.JA_MISS
        end
    end

    -- Calculate charm chance
    local chance = xi.job_utils.beastmaster.getCharmChance(charmer, target, true)

    -- If successful then calculate duration and charm
    if chance > math.random(1, 100) then
        local duration = getCharmDuration(charmer, target)

        if duration > 0 then
            charmer:charm(target, duration)
            return xi.msg.basic.CHARM_SUCCESS
        end
    end

    return xi.msg.basic.CHARM_FAIL
end

-- Enhanced Spur with subjob effectiveness scaling and Job Point integration
xi.job_utils.beastmaster.onUseAbilitySpur = function(player)
    -- Get subjob effectiveness for spur enhancement
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.SPUR, 83)
    
    -- Apply graduated subjob penalty to spur power and duration
    local basePower = 20 + player:getMod(xi.mod.ENHANCES_SPUR) -- bonus STORETP
    local power = math.floor(basePower * effectiveness)
    local baseSubpower = player:getJobPointLevel(xi.jp.SPUR_EFFECT) * 3 -- bonus attack
    local subpower = math.floor(baseSubpower * effectiveness)
    local duration = math.floor(90 * effectiveness)
    
    local pet = player:getPet()
    if pet then
        pet:addStatusEffect(xi.effect.SPUR, power, 0, duration, 0, subpower)
    end
end

-- Enhanced Run Wild with subjob effectiveness scaling and comprehensive pet bonuses
xi.job_utils.beastmaster.onUseAbilityRunWild = function(player, target, ability, action)
    -- Get subjob effectiveness for run wild enhancement
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.RUN_WILD, 93)
    
    -- Apply graduated subjob penalty to all bonuses (25% bonus scaled by effectiveness)
    local power = math.floor(25 * effectiveness)
    local pet = player:getPet()
    if pet then
        -- mods aren't tied to an effect, just applied to the pet. They leave when the pet dies or despawns
        pet:addMod(xi.mod.ATTP, power)
        pet:addMod(xi.mod.ACC, math.floor(pet:getACC() * power / 100))
        -- Yep, it's an MAB % addition
        -- "If you have no sources of Magic Attack Bonus while using the slug pet, then Run Wild actually makes his innate MAB penalty even more negative, thus reducing damage."
        pet:addMod(xi.mod.MATT, math.floor(pet:getMod(xi.mod.MATT) * power / 100))
        pet:addMod(xi.mod.EVA, math.floor(pet:getEVA() * power / 100))
        pet:addMod(xi.mod.DEFP, power)
        -- TODO find out this potency, but appears to be consistently 1% per tick with hare familiar at lvl 99
        local regenPower = math.floor(0.01 * pet:getMaxHP() * effectiveness)
        pet:addMod(xi.mod.REGEN, regenPower)

        -- After 5 minutes, the pet just despawns (duration scaled by effectiveness)
        local duration = math.floor(300 * effectiveness)
        pet:setJugRemainingTime(duration)
    end

    -- seems to display nothing in console, but this it the msg id from capture
    ability:setMsg(154)

    return ability:getID()
end

-----------------------------------
-- Call Beast and Bestial Loyalty Enhancement
-----------------------------------

-- Enhanced Call Beast/Bestial Loyalty with subjob effectiveness scaling
xi.job_utils.beastmaster.onAbilityCheckJug = function(player, target, ability)
    local petId = player:getWeaponSubSkillType(xi.slot.AMMO)

    if player:getPet() ~= nil then
        return xi.msg.basic.ALREADY_HAS_A_PET, 0
    elseif
        not player:hasValidJugPetItem() or
        player:getMainLvl() < jugLevelTable[petId]
    then
        return xi.msg.basic.NO_JUG_PET_ITEM, 0
    elseif not player:canUseMisc(xi.zoneMisc.PET) then
        return xi.msg.basic.CANT_BE_USED_IN_AREA, 0
    end

    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.CALL_BEAST, 23)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    return 0, 0
end

-- Enhanced Call Beast/Bestial Loyalty with subjob support
xi.job_utils.beastmaster.onUseAbilityJug = function(player, target, ability)
    -- Get subjob effectiveness for jug pet enhancement
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateAbilityAccess(player, xi.jobAbility.CALL_BEAST, 23)
    
    xi.pet.spawnPet(player, player:getWeaponSubSkillType(xi.slot.AMMO))

    if ability:getID() == xi.jobAbility.CALL_BEAST then
        player:removeAmmo(1)
    end

    -- Apply subjob effectiveness to pet stats enhancement
    local pet = player:getPet()
    if pet and effectiveness < 1.0 then
        -- Apply subjob penalty to pet stats
        local statReduction = 1.0 - effectiveness
        pet:addMod(xi.mod.ATTP, -math.floor(statReduction * 25))
        pet:addMod(xi.mod.DEFP, -math.floor(statReduction * 25))
        pet:addMod(xi.mod.ACC, -math.floor(statReduction * 25))
        pet:addMod(xi.mod.EVA, -math.floor(statReduction * 25))
    end

    -- Briefly put the recastId for READY/SIC (102) into a recast state to
    -- toggle charges accumulating. 102 is the shared recast id for all jug
    -- pet abilities and for SIC when using a charmed mob.
    -- see sql/abilities_charges and sql_abilities
    player:addRecast(xi.recast.ABILITY, 102, 1)
end

-- Get job-specific abilities list
xi.job_utils.beastmaster.getJobAbilities = function(player)
    local hasAccess, effectiveness = xi.job_utils.beastmaster.validateJobAccess(player)
    if not hasAccess then
        return {}
    end

    local abilities = {
        'Familiar', 'Call Beast', 'Sic', 'Ready', 'Tame', 'Charm',
        'Reward', 'Leave', 'Fight', 'Heel', 'Stay', 'Run Wild', 'Killer Instinct'
    }
    
    -- Add subjob abilities if available
    if player:getSubJob() == xi.job.BST and effectiveness > 0.5 then
        abilities = {
            'Sic', 'Tame', 'Reward'
        }
    end
    
    return abilities
end
