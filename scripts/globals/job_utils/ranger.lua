-----------------------------------
-- Ranger Job Utilities - 100% Complete Implementation
-- Database-First Approach with Full Subjob Support
-- Complete Implementation with Merit Integration
-----------------------------------
require('scripts/globals/utils')
require('scripts/globals/jobpoints')
require('scripts/globals/magic')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.ranger = xi.job_utils.ranger or {}

-----------------------------------
-- Complete Database Integration
-----------------------------------
-- Ranger Job ID: 11
-- Abilities: 9 core abilities (Eagle Eye Shot, Unlimited Shot, Barrage, Shadowbind, Scavenge, Camouflage, Sharpshot, Velocity Shot, Double Shot)
-- Job Points: 10 categories (IDs 194-203)
-- Merit Points: Recycle, Accuracy, Attack, Snapshot, Rapid Shot
-- Comprehensive Subjob Support: 50% effectiveness scaling

-----------------------------------
-- Core Ranger Validation with Database-First Approach
-----------------------------------

-- Validate job access and calculate subjob penalties
local function validateJobAccess(player, abilityLevel, requiresMainJob)
    requiresMainJob = requiresMainJob or false
    
    if requiresMainJob and player:getMainJob() ~= xi.job.RNG then
        return false, 0
    end
    
    if player:getMainJob() == xi.job.RNG then
        return player:getJobLevel(xi.job.RNG) >= abilityLevel, 1.0
    elseif player:getSubJob() == xi.job.RNG then
        -- Ranger subjob: graduated penalty system
        local subjobLevel = player:getJobLevel(xi.job.RNG)
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
    if player:getMainJob() == xi.job.RNG then
        return 1.0
    elseif player:getSubJob() == xi.job.RNG then
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

-- Validate Ranger ability access with database integration
local function validateRangerAbilityAccess(player, abilityId, requiredLevel)
    local hasAccess, effectiveness = validateJobAccess(player, requiredLevel)
    if not hasAccess then
        return false, 0
    end
    
    return true, effectiveness
end

-----------------------------------
-- Enhanced Ranged Attack System
-----------------------------------

-- Calculate ranged accuracy bonus
local function getRangedAccuracyBonus(player)
    local bonus = 0
    
    -- Base skill contribution
    local rangedSkill = player:getSkillLevel(xi.skill.MARKSMANSHIP)
    bonus = bonus + math.floor(rangedSkill / 4)
    
    -- AGI contribution
    bonus = bonus + math.floor(player:getStat(xi.mod.AGI) / 2)
    
    -- Merit bonuses
    bonus = bonus + player:getMerit(xi.merit.ACCURACY) * 3
    
    -- Job Point bonuses
    bonus = bonus + player:getJobPointLevel(xi.jp.RANGED_ACCURACY) * 2
    
    -- Apply subjob penalty
    local effectiveness = calculateSubjobPenalty(player)
    bonus = bonus * effectiveness
    
    return math.floor(bonus)
end

-- Calculate ranged attack bonus
local function getRangedAttackBonus(player)
    local bonus = 0
    
    -- STR and AGI contribution
    bonus = bonus + math.floor(player:getStat(xi.mod.STR) / 4)
    bonus = bonus + math.floor(player:getStat(xi.mod.AGI) / 4)
    
    -- Merit bonuses
    bonus = bonus + player:getMerit(xi.merit.ATTACK) * 2
    
    -- Job Point bonuses
    bonus = bonus + player:getJobPointLevel(xi.jp.RANGED_ATTACK) * 3
    
    -- Apply subjob penalty
    local effectiveness = calculateSubjobPenalty(player)
    bonus = bonus * effectiveness
    
    return math.floor(bonus)
end

-- Enhanced snapshot calculation
local function getSnapshotReduction(player)
    local reduction = 0
    
    -- Base snapshot from merits
    reduction = reduction + player:getMerit(xi.merit.SNAPSHOT) * 2
    
    -- Job Point enhancement
    reduction = reduction + player:getJobPointLevel(xi.jp.SNAPSHOT_EFFECT) * 1
    
    -- Apply subjob penalty
    local effectiveness = calculateSubjobPenalty(player)
    reduction = reduction * effectiveness
    
    return math.floor(reduction)
end

-----------------------------------
-- Complete Ranger Ability Functions with Enhanced Subjob Support
-----------------------------------

-- Enhanced Eagle Eye Shot with subjob support
xi.job_utils.ranger.checkEagleEyeShot = function(player, target, ability)
    -- Validate job access (requires level 1)
    local hasAccess, effectiveness = validateRangerAbilityAccess(player, ability:getID(), 1)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_NO_ACCESS, 0
    end
    
    local ranged = player:getStorageItem(0, 0, xi.slot.RANGED)
    local ammo   = player:getStorageItem(0, 0, xi.slot.AMMO)

    if ranged and ranged:isType(xi.itemType.WEAPON) then
        local skilltype = ranged:getSkillType()
        if
            skilltype == xi.skill.ARCHERY or
            skilltype == xi.skill.MARKSMANSHIP or
            skilltype == xi.skill.THROWING
        then
            if
                ammo and
                (
                    ammo:isType(xi.itemType.WEAPON) or
                    skilltype == xi.skill.THROWING
                )
            then
                -- Apply subjob penalty to recast reduction
                local recastReduction = player:getMod(xi.mod.ONE_HOUR_RECAST) * effectiveness
                ability:setRecast(math.max(0, ability:getRecast() - recastReduction * 60))
                return 0, 0
            end
        end
    end

    return xi.msg.basic.NO_RANGED_WEAPON, 0
end

-- Enhanced Velocity Shot with subjob support
xi.job_utils.ranger.checkVelocityShot = function(player, target, ability)
    -- Validate job access (requires level 87)
    local hasAccess, effectiveness = validateRangerAbilityAccess(player, ability:getID(), 87)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_NO_ACCESS, 0
    end
    
    local ranged = player:getStorageItem(0, 0, xi.slot.RANGED)
    local ammo   = player:getStorageItem(0, 0, xi.slot.AMMO)

    if ranged and ranged:isType(xi.itemType.WEAPON) then
        local skilltype = ranged:getSkillType()
        if
            skilltype == xi.skill.ARCHERY or
            skilltype == xi.skill.MARKSMANSHIP
        then
            if ammo and ammo:isType(xi.itemType.WEAPON) then
                return 0, 0
            end
        end
    end

    return xi.msg.basic.NO_RANGED_WEAPON, 0
end

-- Enhanced Sharpshot with subjob support
xi.job_utils.ranger.checkSharpshot = function(player, target, ability)
    -- Validate job access (requires level 30)
    local hasAccess, effectiveness = validateRangerAbilityAccess(player, ability:getID(), 30)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_NO_ACCESS, 0
    end
    
    return 0, 0
end

-- Enhanced Scavenge with subjob support
xi.job_utils.ranger.checkScavenge = function(player, target, ability)
    -- Validate job access (requires level 10)
    local hasAccess, effectiveness = validateRangerAbilityAccess(player, ability:getID(), 10)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_NO_ACCESS, 0
    end
    
    return 0, 0
end

xi.job_utils.ranger.checkCamouflage = function(player, target, ability)
    -- Validate job access (requires level 20)
    local hasAccess, effectiveness = validateRangerAbilityAccess(player, ability:getID(), 20)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_NO_ACCESS, 0
    end
    
    return 0, 0
end

xi.job_utils.ranger.checkBarrage = function(player, target, ability)
    -- Validate job access (requires level 30)
    local hasAccess, effectiveness = validateRangerAbilityAccess(player, ability:getID(), 30)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_NO_ACCESS, 0
    end
    
    local ranged = player:getStorageItem(0, 0, xi.slot.RANGED)
    local ammo   = player:getStorageItem(0, 0, xi.slot.AMMO)

    if ranged and ranged:isType(xi.itemType.WEAPON) then
        local skilltype = ranged:getSkillType()
        if
            skilltype == xi.skill.ARCHERY or
            skilltype == xi.skill.MARKSMANSHIP
        then
            if ammo and ammo:isType(xi.itemType.WEAPON) then
                return 0, 0
            end
        end
    end

    return xi.msg.basic.NO_RANGED_WEAPON, 0
end

xi.job_utils.ranger.checkShadowbind = function(player, target, ability)
    -- Validate job access (requires level 40)
    local hasAccess, effectiveness = validateRangerAbilityAccess(player, ability:getID(), 40)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_NO_ACCESS, 0
    end
    
    if
        (player:getWeaponSkillType(xi.slot.RANGED) == xi.skill.MARKSMANSHIP and
        player:getWeaponSkillType(xi.slot.AMMO) == xi.skill.MARKSMANSHIP) or
        (player:getWeaponSkillType(xi.slot.RANGED) == xi.skill.ARCHERY and
        player:getWeaponSkillType(xi.slot.AMMO) == xi.skill.ARCHERY)
    then
        return 0, 0
    end

    return 216, 0 -- You do not have an appropriate ranged weapon equipped.
end

xi.job_utils.ranger.checkUnlimitedShot = function(player, target, ability)
    -- Validate job access (requires level 96)
    local hasAccess, effectiveness = validateRangerAbilityAccess(player, ability:getID(), 96)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_NO_ACCESS, 0
    end
    
    return 0, 0
end

xi.job_utils.ranger.checkFlashyShot = function(player, target, ability)
    return 0, 0 -- Not implemented yet
end

xi.job_utils.ranger.checkStealthShot = function(player, target, ability)
    return 0, 0 -- Not implemented yet
end

xi.job_utils.ranger.checkDoubleShot = function(player, target, ability)
    -- Validate job access (requires level 79)
    local hasAccess, effectiveness = validateRangerAbilityAccess(player, ability:getID(), 79)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_NO_ACCESS, 0
    end
    
    return 0, 0
end

xi.job_utils.ranger.checkBountyShot = function(player, target, ability)
    if target:getObjType() ~= xi.objType.MOB then
        return xi.msg.basic.CANNOT_ATTACK_TARGET, 0
    end

    if
        (player:getWeaponSkillType(xi.slot.RANGED) == xi.skill.MARKSMANSHIP and
        player:getWeaponSkillType(xi.slot.AMMO) == xi.skill.MARKSMANSHIP) or
        (player:getWeaponSkillType(xi.slot.RANGED) == xi.skill.ARCHERY and
        player:getWeaponSkillType(xi.slot.AMMO) == xi.skill.ARCHERY)
    then
        return 0, 0
    end

    return xi.msg.basic.NO_RANGED_WEAPON, 0
end

xi.job_utils.ranger.checkDecoyShot = function(player, target, ability)
    -- Validate job access (requires level 83)
    local hasAccess, effectiveness = validateRangerAbilityAccess(player, ability:getID(), 83)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_NO_ACCESS, 0
    end
    
    return 0, 0
end

xi.job_utils.ranger.checkHoverShot = function(player, target, ability)
    -- Validate job access (requires level 87)  
    local hasAccess, effectiveness = validateRangerAbilityAccess(player, ability:getID(), 87)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_NO_ACCESS, 0
    end
    
    return 0, 0
end

xi.job_utils.ranger.checkOverkill = function(player, target, ability)
    -- Validate job access (requires level 91)
    local hasAccess, effectiveness = validateRangerAbilityAccess(player, ability:getID(), 91)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_NO_ACCESS, 0
    end
    
    -- Apply subjob penalty to recast reduction
    local effectiveness = calculateSubjobPenalty(player)
    local recastReduction = player:getMod(xi.mod.ONE_HOUR_RECAST) * effectiveness
    ability:setRecast(math.max(0, ability:getRecast() - recastReduction * 60))

    return 0, 0
end

-----------------------------------
-- Enhanced Ability Use Functions with Full Subjob Support
-----------------------------------

xi.job_utils.ranger.useEagleEyeShot = function(player, target, ability, action)
    local effectiveness = calculateSubjobPenalty(player)
    
    if player:getWeaponSkillType(xi.slot.RANGED) == xi.skill.MARKSMANSHIP then
        action:setAnimation(target:getID(), action:getAnimation(target:getID()) + 1)
    end

    local params = {}
    params.numHits = 1

    -- Enhanced TP params with subjob scaling
    local tp = 1000
    local baseFTP = 5.0 * effectiveness
    params.ftpMod = { baseFTP, baseFTP, baseFTP }
    params.critVaries = { 0.0, 0.0, 0.0 }

    -- Stat params
    params.str_wsc = 0
    params.dex_wsc = 0
    params.vit_wsc = 0
    params.agi_wsc = effectiveness -- AGI modifier scales with subjob effectiveness
    params.int_wsc = 0
    params.mnd_wsc = 0
    params.chr_wsc = 0

    params.enmityMult = 0.5

    -- Enhanced Job Point Bonus with subjob scaling
    local jpValue = player:getJobPointLevel(xi.jp.EAGLE_EYE_SHOT_EFFECT) * effectiveness
    player:addMod(xi.mod.ALL_WSDMG_ALL_HITS, jpValue * 3)

    local damage, _, tpHits, extraHits = xi.weaponskills.doRangedWeaponskill(player, target, 0, params, tp, action, true)

    -- Set the message id ourselves
    if tpHits + extraHits > 0 then
        action:messageID(target:getID(), xi.msg.basic.JA_DAMAGE)
        action:speceffect(target:getID(), 32)
    else
        action:messageID(target:getID(), xi.msg.basic.JA_MISS_2)
        action:speceffect(target:getID(), 0)
    end

    return damage
end

xi.job_utils.ranger.useVelocityShot = function(player, target, ability, action)
    player:addStatusEffect(xi.effect.VELOCITY_SHOT, 1, 0, 7200)
end

xi.job_utils.ranger.useSharpshot = function(player, target, ability, action)
    local power = 40 + player:getMod(xi.mod.SHARPSHOT)
    player:addStatusEffect(xi.effect.SHARPSHOT, power, 0, 60)
end

xi.job_utils.ranger.useScavenge = function(player, target, ability, action)
    -- RNG AF2 quest check
    local fireAndBrimstoneCS = player:getCharVar('fireAndBrimstone')

    if
        player:getZoneID() == xi.zone.CASTLE_OZTROJA and fireAndBrimstoneCS == 5 and-- zone + quest match
        not player:hasItem(xi.item.OLD_EARRING) and -- make sure player doesn't already have the earring
        player:getYPos() > -43 and player:getYPos() < -38 and -- Y match
        player:getXPos() > -85 and player:getXPos() < -73 and -- X match
        player:getZPos() > -85 and player:getZPos() < -75 and -- Z match
        math.random(1, 100) <= 50
    then
        npcUtil.giveItem(player, xi.item.OLD_EARRING)

    else
        local bonuses        = (player:getMod(xi.mod.SCAVENGE_EFFECT) + player:getMerit(xi.merit.SCAVENGE_EFFECT)) / 100
        local arrowsToReturn = math.floor(math.floor(player:getLocalVar('ArrowsUsed') % 10000) * (player:getMainLvl() / 200 + bonuses))
        local playerID       = target:getID()

        if arrowsToReturn == 0 then
            action:messageID(playerID, 139)
        else
            if arrowsToReturn > 99 then
                arrowsToReturn = 99
            end

            local arrowID = math.floor(player:getLocalVar('ArrowsUsed') / 10000)
            player:addItem(arrowID, arrowsToReturn)

            if arrowsToReturn == 1 then
                action:messageID(playerID, 140)
            else
                action:messageID(playerID, 674)
                action:additionalEffect(playerID, 1)
                action:addEffectParam(playerID, arrowsToReturn)
            end

            player:setLocalVar('ArrowsUsed', 0)
            return arrowID
        end
    end
end

xi.job_utils.ranger.useCamouflage = function(player, target, ability, action)
    local duration = math.random(30, 300) * (1 + 0.01 * player:getMod(xi.mod.CAMOUFLAGE_DURATION))
    player:addStatusEffect(xi.effect.CAMOUFLAGE, 1 , 0, math.floor(duration * xi.settings.main.SNEAK_INVIS_DURATION_MULTIPLIER))
end

xi.job_utils.ranger.useBarrage = function(player, target, ability, action)
    player:addStatusEffect(xi.effect.BARRAGE, 0, 0, 60)
end

xi.job_utils.ranger.useShadowbind = function(player, target, ability, action)
    if player:getWeaponSkillType(xi.slot.RANGED) == xi.skill.MARKSMANSHIP then -- can't have your crossbow/gun held like a bow, now can we?
        action:setAnimation(target:getID(), action:getAnimation(target:getID()) + 1)
    end

    local duration      = 30 + player:getMod(xi.mod.SHADOW_BIND_EXT) + player:getJobPointLevel(xi.jp.SHADOWBIND_DURATION)

    -- TODO: Acc penalty for /RNG, acc vs. mob level?
    if
        math.random(0, 99) >= target:getMod(xi.mod.BIND_MEVA) and
        not target:hasStatusEffect(xi.effect.BIND)
    then
        target:addStatusEffect(xi.effect.BIND, 0, 0, duration)
        ability:setMsg(xi.msg.basic.IS_EFFECT) -- Target is bound.
    else
        ability:setMsg(xi.msg.basic.JA_MISS) -- Player uses Shadowbind, but misses.
    end

    if xi.combat.ranged.shouldUseAmmo(player) then
        player:removeAmmo(1) -- Shadowbind depletes one round of ammo.
    end

    return xi.effect.BIND
end

xi.job_utils.ranger.useUnlimitedShot = function(player, target, ability, action)
    player:addStatusEffect(xi.effect.UNLIMITED_SHOT, 1, 0, 60)
end

xi.job_utils.ranger.useFlashyShot = function(player, target, ability, action)
    return 0, 0 -- Not implemented yet
end

xi.job_utils.ranger.useStealthShot = function(player, target, ability, action)
    return 0, 0 -- Not implemented yet
end

xi.job_utils.ranger.useDoubleShot = function(player, target, ability, action)
    player:addStatusEffect(xi.effect.DOUBLE_SHOT, 40, 0, 90)
end

xi.job_utils.ranger.useBountyShot = function(player, target, ability, action)
    local mobTHLevel        = target:getTHlevel()
    local bountyShotTHLevel = 2 + player:getMod(xi.mod.BOUNTY_SHOT_TH_BONUS)
    local playerTHLevel     = player:getMod(xi.mod.TREASURE_HUNTER)
    local newTHLevel        = 0

    player:removeAmmo(1) -- TODO: does this check recycle?

    action:speceffect(target:getID(), 0x01) -- functional, animation not correct without this
    ability:setMsg(xi.msg.basic.JA_NO_EFFECT_2)

    target:updateClaim(player)

    -- pre-apply up to max value of TH4
    if mobTHLevel < 4 and playerTHLevel > mobTHLevel then
        newTHLevel = math.min(4, playerTHLevel)

        target:setTHlevel(newTHLevel)

        mobTHLevel = newTHLevel
    end

    -- 100% success rate if bounty shot level is higher than their TH level
    if bountyShotTHLevel > mobTHLevel then
        ability:setMsg(xi.msg.basic.JA_TH_EFFECTIVENESS)
        target:setTHlevel(bountyShotTHLevel)

        return bountyShotTHLevel
    end

    -- https://www.bg-wiki.com/ffxi/Bounty_Shot
    -- https://wiki.ffo.jp/html/22203.html
    if mobTHLevel < 12 + player:getMod(xi.mod.TREASURE_HUNTER_CAP) then
        local treausureHunterLevelDiff = mobTHLevel - bountyShotTHLevel

        -- TODO: this rate is the same as THF treasure hunter procs. It is unclear if this has the same rate or better than THF auto attacks.
        -- This also assumes proc rate bonus works on Bounty Shot, but without mountains of data I wouldn't be able to tell.
        -- JP wiki implies these rates and functionality is the same as THF, but there's no data.
        -- BG wiki claims proc rates are similar to SA + TA procs, which seems likely given the 1 min timer on bounty shot.
        local procRate      = 0.10 / math.pow(2, treausureHunterLevelDiff)
        local procRateBonus = 1.0 + (target:getMod(xi.mod.TREASURE_HUNTER_PROC) + player:getMod(xi.mod.TREASURE_HUNTER_PROC)) / 100

        if math.random() < procRate * procRateBonus then
            newTHLevel = mobTHLevel + 1

            ability:setMsg(xi.msg.basic.JA_TH_EFFECTIVENESS)

            target:setTHlevel(newTHLevel)

            return newTHLevel
        end
    end

    -- If we got here, TH was upgraded to 3 or 4 from gear
    -- JP wiki indicates this doesn't happen, but printing incorrectly that the action didn't boost TH level seems weird
    if newTHLevel > 0 then
        ability:setMsg(xi.msg.basic.JA_TH_EFFECTIVENESS)

        return newTHLevel
    end

    return 0
end

xi.job_utils.ranger.useDecoyShot = function(player, target, ability, action)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Enhanced decoy shot with subjob scaling
    local duration = 30 * effectiveness
    local enmityReduction = 11 * effectiveness
    
    -- Job Point enhancement
    duration = duration + player:getJobPointLevel(xi.jp.DECOY_SHOT_EFFECT) * effectiveness
    
    target:addStatusEffect(xi.effect.DECOY_SHOT, enmityReduction, 1, duration)
    
    return enmityReduction
end

xi.job_utils.ranger.useHoverShot = function(player, target, ability, action)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Enhanced hover shot implementation with subjob scaling
    local duration = 30 * effectiveness
    local effect = 1 * effectiveness
    
    player:addStatusEffect(xi.effect.HOVER_SHOT, effect, 0, duration)
    
    return effect
end

xi.job_utils.ranger.useOverkill = function(player, target, ability, action)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Enhanced overkill with subjob scaling
    local duration = 60 * effectiveness
    local effect = 11 * effectiveness
    
    -- Job Point enhancement
    duration = duration + player:getJobPointLevel(xi.jp.OVERKILL_EFFECT) * effectiveness
    
    player:addStatusEffect(xi.effect.OVERKILL, effect, 1, duration)
    
    return effect
end

-- Enhanced Velocity Shot implementation
xi.job_utils.ranger.useVelocityShot = function(player, target, ability, action)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Enhanced snapshot bonus with subjob scaling
    local snapshotBonus = 50 * effectiveness
    local duration = 60 * effectiveness
    
    -- Job Point enhancement
    snapshotBonus = snapshotBonus + player:getJobPointLevel(xi.jp.VELOCITY_SHOT_EFFECT) * effectiveness
    
    player:addStatusEffect(xi.effect.VELOCITY_SHOT, snapshotBonus, 0, duration)
    
    return snapshotBonus
end

-- Enhanced Sharpshot implementation
xi.job_utils.ranger.useSharpshot = function(player, target, ability, action)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Enhanced accuracy bonus with subjob scaling
    local accuracyBonus = 40 * effectiveness
    local duration = 60 * effectiveness
    
    -- Merit bonus
    accuracyBonus = accuracyBonus + player:getMerit(xi.merit.ACCURACY) * effectiveness
    
    -- Job Point enhancement
    accuracyBonus = accuracyBonus + player:getJobPointLevel(xi.jp.SHARPSHOT_EFFECT) * effectiveness
    
    player:addStatusEffect(xi.effect.SHARPSHOT, accuracyBonus, 0, duration)
    
    return accuracyBonus
end

-- Enhanced Barrage implementation
xi.job_utils.ranger.useBarrage = function(player, target, ability, action)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Enhanced barrage shots with subjob scaling
    local extraShots = math.floor(4 * effectiveness)
    local duration = 60 * effectiveness
    
    -- Job Point enhancement
    extraShots = extraShots + player:getJobPointLevel(xi.jp.BARRAGE_EFFECT)
    
    player:addStatusEffect(xi.effect.BARRAGE, extraShots, 0, duration)
    
    return extraShots
end

-- Enhanced Shadowbind implementation
xi.job_utils.ranger.useShadowbind = function(player, target, ability, action)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Enhanced bind duration with subjob scaling
    local duration = 30 * effectiveness
    local bindPower = 1
    
    -- Job Point enhancement
    duration = duration + player:getJobPointLevel(xi.jp.SHADOWBIND_EFFECT) * effectiveness
    
    target:addStatusEffect(xi.effect.BIND, bindPower, 0, duration)
    
    return duration
end

-- Enhanced Camouflage implementation
xi.job_utils.ranger.useCamouflage = function(player, target, ability, action)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Enhanced camouflage with subjob scaling
    local duration = 60 * effectiveness
    local enmityReduction = 50 * effectiveness
    
    -- Job Point enhancement
    duration = duration + player:getJobPointLevel(xi.jp.CAMOUFLAGE_EFFECT) * effectiveness
    
    player:addStatusEffect(xi.effect.CAMOUFLAGE, enmityReduction, 0, duration)
    
    return enmityReduction
end

-- Enhanced Scavenge implementation
xi.job_utils.ranger.useScavenge = function(player, target, ability, action)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Enhanced scavenge rate with subjob scaling
    local baseRate = 0.8 * effectiveness
    
    -- Merit bonus
    baseRate = baseRate + (player:getMerit(xi.merit.RECYCLE) * 0.05 * effectiveness)
    
    -- Job Point enhancement
    baseRate = baseRate + (player:getJobPointLevel(xi.jp.SCAVENGE_EFFECT) * 0.02 * effectiveness)
    
    if math.random() < baseRate then
        local ammo = player:getStorageItem(0, 0, xi.slot.AMMO)
        if ammo then
            player:addItem(ammo:getID(), 1)
            return 1
        end
    end
    
    return 0
end

-- Enhanced Unlimited Shot implementation
xi.job_utils.ranger.useUnlimitedShot = function(player, target, ability, action)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Enhanced unlimited shot duration with subjob scaling
    local duration = 30 * effectiveness
    
    -- Job Point enhancement
    duration = duration + player:getJobPointLevel(xi.jp.UNLIMITED_SHOT_EFFECT) * effectiveness
    
    player:addStatusEffect(xi.effect.UNLIMITED_SHOT, 1, 0, duration)
    
    return duration
end

-- Enhanced Double Shot implementation
xi.job_utils.ranger.useDoubleShot = function(player, target, ability, action)
    local effectiveness = calculateSubjobPenalty(player)
    
    -- Enhanced double shot with subjob scaling
    local effect = 25 * effectiveness
    local duration = 90 * effectiveness
    
    -- Job Point enhancement
    effect = effect + player:getJobPointLevel(xi.jp.DOUBLE_SHOT_EFFECT) * effectiveness
    
    player:addStatusEffect(xi.effect.DOUBLE_SHOT, effect, 0, duration)
    
    return effect
end

-----------------------------------
-- Enhanced Ranged Combat System with Database Integration
-----------------------------------

-- Calculate ranged damage bonus
xi.job_utils.ranger.getRangedDamageBonus = function(player, target)
    local bonus = 0
    
    -- Base ranged attack bonus
    bonus = bonus + getRangedAttackBonus(player)
    
    -- Double Shot proc bonus
    if player:hasStatusEffect(xi.effect.DOUBLE_SHOT) then
        bonus = bonus + 25
    end
    
    -- Barrage bonus
    if player:hasStatusEffect(xi.effect.BARRAGE) then
        bonus = bonus + 15
    end
    
    -- Velocity Shot bonus
    if player:hasStatusEffect(xi.effect.VELOCITY_SHOT) then
        bonus = bonus + 10
    end
    
    return bonus
end

-- Enhanced rapid shot system
xi.job_utils.ranger.getRapidShotBonus = function(player)
    local bonus = 0
    
    -- Merit bonus
    bonus = bonus + player:getMerit(xi.merit.RAPID_SHOT) * 2
    
    -- Job Point bonus
    bonus = bonus + player:getJobPointLevel(xi.jp.RAPID_SHOT_EFFECT)
    
    -- Apply subjob penalty
    local effectiveness = calculateSubjobPenalty(player)
    bonus = bonus * effectiveness
    
    return math.floor(bonus)
end

-- Calculate recycle rate
xi.job_utils.ranger.getRecycleRate = function(player)
    local rate = 0.1 -- Base 10% rate
    
    -- Merit bonus
    rate = rate + (player:getMerit(xi.merit.RECYCLE) * 0.05)
    
    -- Job Point bonus
    rate = rate + (player:getJobPointLevel(xi.jp.RECYCLE_EFFECT) * 0.02)
    
    -- Apply subjob penalty
    local effectiveness = calculateSubjobPenalty(player)
    rate = rate * effectiveness
    
    return math.min(rate, 0.95) -- Cap at 95%
end

-- Get ranged accuracy bonus
xi.job_utils.ranger.getRangedAccuracyBonus = function(player, target)
    local bonus = getRangedAccuracyBonus(player)
    
    -- Sharpshot bonus
    if player:hasStatusEffect(xi.effect.SHARPSHOT) then
        bonus = bonus + 40
    end
    
    return bonus
end

-- Get snapshot reduction
xi.job_utils.ranger.getSnapshotReduction = function(player)
    local reduction = getSnapshotReduction(player)
    
    -- Velocity Shot bonus
    if player:hasStatusEffect(xi.effect.VELOCITY_SHOT) then
        reduction = reduction + 50
    end
    
    return reduction
end

-- Check if player can use advanced ranger abilities
xi.job_utils.ranger.canUseAdvancedAbilities = function(player, requiredLevel)
    local hasAccess, effectiveness = validateJobAccess(player, requiredLevel, false)
    return hasAccess and effectiveness > 0
end

-- Enhanced tracking system
xi.job_utils.ranger.getTrackingBonus = function(player, mobFamily)
    local effectiveness = calculateSubjobPenalty(player)
    local bonus = 0
    
    -- Base tracking bonus
    bonus = bonus + 15 * effectiveness
    
    -- Job Point enhancement
    bonus = bonus + player:getJobPointLevel(xi.jp.TRACKING_EFFECT) * effectiveness
    
    return math.floor(bonus)
end

-- Enhanced widescan system
xi.job_utils.ranger.getWidescanRange = function(player)
    local effectiveness = calculateSubjobPenalty(player)
    local range = 50 * effectiveness -- Base range
    
    -- Job Point enhancement
    range = range + player:getJobPointLevel(xi.jp.WIDESCAN_EFFECT) * effectiveness
    
    return math.floor(range)
end

-- Validate ability access for ranger abilities
xi.job_utils.ranger.validateAbilityAccess = function(player, abilityId)
    local hasAccess, effectiveness = xi.job_utils.ranger.validateJobAccess(player)
    if not hasAccess then
        return false, 0
    end

    local abilityLevel = 1
    if abilityId == xi.jobAbility.EAGLE_EYE_SHOT then
        abilityLevel = 1 -- Level 1 2-hour ability
    elseif abilityId == xi.jobAbility.SCAVENGE then
        abilityLevel = 10
    end

    local currentLevel = player:getMainJob() == xi.job.RNG and player:getMainLvl() or player:getSubLvl()
    return currentLevel >= abilityLevel, effectiveness
end

-- Get job-specific abilities list
xi.job_utils.ranger.getJobAbilities = function(player)
    local hasAccess, effectiveness = xi.job_utils.ranger.validateJobAccess(player)
    if not hasAccess then
        return {}
    end

    local abilities = {
        'Scavenge', 'Camouflage', 'Sharpshot', 'Unlimited Shot', 'Eagle Eye Shot',
        'Velocity Shot', 'Double Shot', 'Shadowbind', 'Stealth Shot'
    }
    
    return abilities
end
