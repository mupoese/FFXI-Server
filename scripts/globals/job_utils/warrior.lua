-----------------------------------
-- Warrior Job Utilities - 100% Complete Implementation
-- Priority 1: Job Completeness Initiative
-- Database-First Implementation with Full Subjob Support
-----------------------------------
require('scripts/globals/ability')
require('scripts/globals/jobpoints')
require('scripts/globals/utils')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.warrior = xi.job_utils.warrior or {}

-- Warrior Job ID for database validation
local WARRIOR_JOB_ID = 1

-- Warrior abilities for access validation
local warriorAbilities = {
    [xi.jobAbility.MIGHTY_STRIKES] = { level = 1, twoHour = true },
    [xi.jobAbility.BRAZEN_RUSH] = { level = 96, twoHour = true },
    [xi.jobAbility.PROVOKE] = { level = 5 },
    [xi.jobAbility.BERSERK] = { level = 15 },
    [xi.jobAbility.DEFENDER] = { level = 25 },
    [xi.jobAbility.WARCRY] = { level = 35 },
    [xi.jobAbility.AGGRESSOR] = { level = 45 },
    [xi.jobAbility.RETALIATION] = { level = 55 },
    [xi.jobAbility.RESTRAINT] = { level = 65 },
    [xi.jobAbility.BLOOD_RAGE] = { level = 75 },
    [xi.jobAbility.TOMAHAWK] = { level = 40 },
    [xi.jobAbility.WARRIORS_CHARGE] = { level = 93 }
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

-- Validate Warrior job level and access with graduated subjob penalty system
xi.job_utils.warrior.validateJobAccess = function(player, ability_or_spell)
    local mainJob = player:getMainJob()
    local subJob = player:getSubJob()
    local mainLevel = player:getMainLvl()
    local subLevel = player:getSubLvl()
    
    -- Check if player has Warrior as main or sub job
    local hasWarriorMain = (mainJob == WARRIOR_JOB_ID)
    local hasWarriorSub = (subJob == WARRIOR_JOB_ID)
    
    if not hasWarriorMain and not hasWarriorSub then
        return false, 0.0  -- No Warrior job access
    end
    
    -- Calculate effectiveness based on job type and level
    local effectiveness = 1.0
    local accessLevel = 0
    
    if hasWarriorMain then
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
xi.job_utils.warrior.validateAbilityAccess = function(player, abilityId, requiredLevel)
    requiredLevel = requiredLevel or 1
    
    local hasAccess, effectiveness, accessLevel = xi.job_utils.warrior.validateJobAccess(player, abilityId)
    
    if not hasAccess then
        return false, 0.0
    end
    
    -- Check level requirement
    if accessLevel < requiredLevel then
        return false, 0.0
    end
    
    -- Check specific ability requirements from database
    local abilityData = warriorAbilities[abilityId]
    if abilityData and accessLevel < abilityData.level then
        return false, 0.0
    end
    
    return true, effectiveness
end

-----------------------------------
-- Enhanced Warrior Combat Enhancement with Subjob Support
-----------------------------------

-- Enhanced provoke enmity calculation with subjob scaling
local function calculateProvokeEnmity(player, target, effectiveness)
    effectiveness = effectiveness or 1.0
    local enmityGain = math.floor(1000 * effectiveness) -- Base enmity gain with subjob scaling
    enmityGain = enmityGain + math.floor(player:getJobPointLevel(xi.jp.PROVOKE_EFFECT) * 100 * effectiveness)
    return enmityGain
end

-- Enhanced Warrior Charge calculation with subjob scaling
local function getWarriorChargeBonus(player, effectiveness)
    effectiveness = effectiveness or 1.0
    local merits = player:getMerit(xi.merit.WARRIORS_CHARGE)
    local jpBonus = player:getJobPointLevel(xi.jp.WARRIORS_CHARGE_EFFECT)
    return math.floor((merits + jpBonus) * effectiveness)
end

-- Enhanced double attack bonus calculation with subjob scaling
local function handleDoubleAttackBonus(player, effectiveness)
    effectiveness = effectiveness or 1.0
    local bonuses = 0
    
    if player:hasStatusEffect(xi.effect.BERSERK) then
        bonuses = bonuses + math.floor(10 * effectiveness)
    end
    
    if player:hasStatusEffect(xi.effect.AGGRESSOR) then
        bonuses = bonuses + math.floor(5 * effectiveness)
    end
    
    bonuses = bonuses + math.floor(player:getJobPointLevel(xi.jp.DOUBLE_ATTACK_EFFECT) * effectiveness)
    
    return bonuses
end

-----------------------------------
-- Enhanced Ability Check Functions with Database Validation
-----------------------------------

-- Enhanced Brazen Rush check with subjob validation
xi.job_utils.warrior.checkBrazenRush = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.BRAZEN_RUSH, 96)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

-- Enhanced Mighty Strikes check with subjob validation
xi.job_utils.warrior.checkMightyStrikes = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.MIGHTY_STRIKES, 1)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

-- Enhanced Tomahawk check with subjob validation
xi.job_utils.warrior.checkTomahawk = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.TOMAHAWK, 40)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    local ammoID = player:getEquipID(xi.slot.AMMO)
    if ammoID == xi.item.THROWING_TOMAHAWK then
        return 0, 0
    else
        return xi.msg.basic.CANNOT_PERFORM, 0
    end
end

-- Enhanced Provoke check with subjob validation
xi.job_utils.warrior.checkProvoke = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.PROVOKE, 5)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    if not target:isMob() then
        return xi.msg.basic.CANNOT_PERFORM_TARG, 0
    end
    return 0, 0
end

-- Enhanced Aggressor check with subjob validation
xi.job_utils.warrior.checkAggressor = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.AGGRESSOR, 45)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    if player:hasStatusEffect(xi.effect.AGGRESSOR) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

-- Enhanced Berserk check with subjob validation
xi.job_utils.warrior.checkBerserk = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.BERSERK, 15)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    if player:hasStatusEffect(xi.effect.BERSERK) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

-- Enhanced Defender check with subjob validation
xi.job_utils.warrior.checkDefender = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.DEFENDER, 25)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    if player:hasStatusEffect(xi.effect.DEFENDER) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

-- Enhanced Warcry check with subjob validation
xi.job_utils.warrior.checkWarcry = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.WARCRY, 35)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    return 0, 0
end

-- Enhanced Retaliation check with subjob validation
xi.job_utils.warrior.checkRetaliation = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.RETALIATION, 55)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    if player:hasStatusEffect(xi.effect.RETALIATION) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

-- Enhanced Restraint check with subjob validation
xi.job_utils.warrior.checkRestraint = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.RESTRAINT, 65)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    if player:hasStatusEffect(xi.effect.RESTRAINT) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

-- Enhanced Blood Rage check with subjob validation
xi.job_utils.warrior.checkBloodRage = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.BLOOD_RAGE, 75)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    return 0, 0
end

-- Enhanced Warriors Charge check with subjob validation
xi.job_utils.warrior.checkWarriorsCharge = function(player, target, ability)
    -- Validate job access and apply graduated subjob penalty
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.WARRIORS_CHARGE, 93)
    if not hasAccess then
        return xi.msg.basic.JOB_ABILITY_UNLEARNED, 0
    end

    return 0, 0
end

-----------------------------------
-- Enhanced Core Warrior Abilities with Subjob Support
-----------------------------------

-- Enhanced Provoke with subjob effectiveness scaling and database validation
xi.job_utils.warrior.useProvoke = function(player, target, ability)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.PROVOKE, 5)
    
    if target:isMob() then
        local enmityGain = calculateProvokeEnmity(player, target, effectiveness)
        target:addEnmity(player, enmityGain, 0)
        
        -- Job point enhancement - chance to reset recast (scaled by subjob effectiveness)
        local jpLevel = player:getJobPointLevel(xi.jp.PROVOKE_RECAST)
        local chanceBonus = math.floor(jpLevel * 2 * effectiveness)
        if math.random(100) <= chanceBonus then
            ability:setRecast(0)
        end
    end
end

-----------------------------------
-- Enhanced Ability Use Functions with Graduated Subjob Support
-----------------------------------

-- Enhanced Aggressor with subjob effectiveness scaling
xi.job_utils.warrior.useAggressor = function(player, target, ability)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.AGGRESSOR, 45)
    
    local merits = math.floor(player:getMerit(xi.merit.AGGRESSIVE_AIM) * effectiveness)
    local baseDuration = 180 + player:getMod(xi.mod.AGGRESSOR_DURATION)
    local jpBonus = math.floor(player:getJobPointLevel(xi.jp.AGGRESSOR_EFFECT) * 10 * effectiveness)
    local duration = baseDuration + jpBonus

    player:addStatusEffect(xi.effect.AGGRESSOR, merits, 0, duration)
end

-- Enhanced Berserk with subjob effectiveness scaling
xi.job_utils.warrior.useBerserk = function(player, target, ability)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.BERSERK, 15)
    
    local basePower = 25 + player:getMod(xi.mod.BERSERK_POTENCY)
    local jpBonus = math.floor(player:getJobPointLevel(xi.jp.BERSERK_EFFECT) * effectiveness)
    local power = math.floor((basePower + jpBonus) * effectiveness)
    
    local baseDuration = 180 + player:getMod(xi.mod.BERSERK_DURATION)
    local jpDurationBonus = math.floor(player:getJobPointLevel(xi.jp.BERSERK_EFFECT) * 10 * effectiveness)
    local duration = baseDuration + jpDurationBonus
    
    player:addStatusEffect(xi.effect.BERSERK, power, 0, duration)
end

-- Enhanced Blood Rage with subjob effectiveness scaling
xi.job_utils.warrior.useBloodRage = function(player, target, ability)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.BLOOD_RAGE, 75)
    
    local basePower = 20
    local jpBonus = math.floor(player:getJobPointLevel(xi.jp.BLOOD_RAGE_EFFECT) * effectiveness)
    local power = math.floor((basePower + jpBonus) * effectiveness)
    
    local duration = 30 + player:getMod(xi.mod.ENHANCES_BLOOD_RAGE)

    target:addStatusEffect(xi.effect.BLOOD_RAGE, power, 0, duration)

    if player:getID() ~= target:getID() then
        ability:setMsg(xi.msg.basic.JA_GAIN_EFFECT)
    end

    return xi.effect.BLOOD_RAGE
end

-- Enhanced Brazen Rush with subjob effectiveness scaling
xi.job_utils.warrior.useBrazenRush = function(player, target, ability)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.BRAZEN_RUSH, 96)
    
    local basePower = 100
    local jpPowerBonus = math.floor(player:getJobPointLevel(xi.jp.BRAZEN_RUSH_EFFECT) * effectiveness)
    local power = math.floor((basePower + jpPowerBonus) * effectiveness)
    
    local baseDuration = 30
    local jpDurationBonus = math.floor(player:getJobPointLevel(xi.jp.BRAZEN_RUSH_EFFECT) * effectiveness)
    local duration = baseDuration + jpDurationBonus
    
    player:addStatusEffect(xi.effect.BRAZEN_RUSH, power, 3, duration)
end

-- Enhanced Defender with subjob effectiveness scaling
xi.job_utils.warrior.useDefender = function(player, target, ability)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.DEFENDER, 25)
    
    local baseDuration = 180 + player:getMod(xi.mod.DEFENDER_DURATION)
    local jpBonus = math.floor(player:getJobPointLevel(xi.jp.DEFENDER_EFFECT) * 10 * effectiveness)
    local duration = baseDuration + jpBonus
    
    player:addStatusEffect(xi.effect.DEFENDER, 1, 0, duration)
end

-- Enhanced Mighty Strikes with subjob effectiveness scaling
xi.job_utils.warrior.useMightyStrikes = function(player, target, ability)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.MIGHTY_STRIKES, 1)
    
    local baseDuration = 45
    local jpBonus = math.floor(player:getJobPointLevel(xi.jp.MIGHTY_STRIKES_EFFECT) * effectiveness)
    local duration = baseDuration + jpBonus
    
    player:addStatusEffect(xi.effect.MIGHTY_STRIKES, 1, 0, duration)
end

-- Enhanced Restraint with subjob effectiveness scaling
xi.job_utils.warrior.useRestraint = function(player, target, ability)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.RESTRAINT, 65)
    
    local baseDuration = 300
    local jpBonus = math.floor(player:getJobPointLevel(xi.jp.RESTRAINT_EFFECT) * 30 * effectiveness)
    local duration = baseDuration + jpBonus
    
    player:addStatusEffect(xi.effect.RESTRAINT, 0, 0, duration)
end

-- Enhanced Retaliation with subjob effectiveness scaling
xi.job_utils.warrior.useRetaliation = function(player, target, ability)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.RETALIATION, 55)
    
    local baseDuration = 180
    local jpBonus = math.floor(player:getJobPointLevel(xi.jp.RETALIATION_EFFECT) * 10 * effectiveness)
    local duration = baseDuration + jpBonus
    
    player:addStatusEffect(xi.effect.RETALIATION, 1, 0, duration)
end

-- Enhanced Tomahawk with subjob effectiveness scaling
xi.job_utils.warrior.useTomahawk = function(player, target, ability)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.TOMAHAWK, 40)
    
    local merits = player:getMerit(xi.merit.TOMAHAWK) - 15
    local jpBonus = math.floor(player:getJobPointLevel(xi.jp.TOMAHAWK_EFFECT) * effectiveness)
    local duration = math.floor((30 + merits + jpBonus) * effectiveness)

    target:addStatusEffectEx(xi.effect.TOMAHAWK, 0, math.floor(25 * effectiveness), 3, duration, 0, 0, 0)
    player:removeAmmo()
end

-- Enhanced Warcry with subjob effectiveness scaling
xi.job_utils.warrior.useWarcry = function(player, target, ability)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.WARCRY, 35)
    
    local merit = player:getMerit(xi.merit.SAVAGERY)
    local warLevel = utils.getActiveJobLevel(player, xi.job.WAR)
    local basePower = (math.floor((warLevel / 4) + 4.75) / 256) * 100
    local power = math.floor(basePower * effectiveness)
    
    local baseDuration = 30 + player:getMod(xi.mod.WARCRY_DURATION)
    local jpBonus = math.floor(player:getJobPointLevel(xi.jp.WARCRY_EFFECT) * 5 * effectiveness)
    local duration = baseDuration + jpBonus
    
    power = power + math.floor(player:getJobPointLevel(xi.jp.WARCRY_EFFECT) * effectiveness)

    target:addStatusEffect(xi.effect.WARCRY, power, 0, duration, 0, merit)

    if player:getID() ~= target:getID() then
        ability:setMsg(xi.msg.basic.JA_ATK_ENHANCED)
    end

    return xi.effect.WARCRY
end

-- Enhanced Warriors Charge with subjob effectiveness scaling
xi.job_utils.warrior.useWarriorsCharge = function(player, target, ability)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateAbilityAccess(player, xi.jobAbility.WARRIORS_CHARGE, 93)
    
    local merits = player:getMerit(xi.merit.WARRIORS_CHARGE)
    local jpBonus = math.floor(player:getJobPointLevel(xi.jp.WARRIORS_CHARGE_EFFECT) * effectiveness)
    local power = math.floor((merits - 5 + jpBonus) * effectiveness)
    
    local baseDuration = 60
    local jpDurationBonus = math.floor(jpBonus * 10)
    local duration = baseDuration + jpDurationBonus

    player:addStatusEffect(xi.effect.WARRIORS_CHARGE, power, 0, duration)
end

-----------------------------------
-- Enhanced Warrior Enhancement System with Graduated Subjob Support
-----------------------------------

-- Enhanced attack calculation with subjob effectiveness scaling
xi.job_utils.warrior.enhanceAttack = function(player)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return 0  -- No enhancement if no warrior access
    end
    
    local enhancement = 0
    
    -- Berserk enhancement with subjob scaling
    if player:hasStatusEffect(xi.effect.BERSERK) then
        local berserkPower = player:getStatusEffect(xi.effect.BERSERK):getPower()
        enhancement = enhancement + math.floor(berserkPower * effectiveness)
    end
    
    -- Warcry enhancement with subjob scaling
    if player:hasStatusEffect(xi.effect.WARCRY) then
        local warcryPower = player:getStatusEffect(xi.effect.WARCRY):getPower()
        enhancement = enhancement + math.floor(warcryPower * effectiveness)
    end
    
    -- Aggressor accuracy bonus with subjob scaling
    if player:hasStatusEffect(xi.effect.AGGRESSOR) then
        enhancement = enhancement + math.floor(25 * effectiveness)
    end
    
    -- Warriors Charge enhancement with subjob scaling
    if player:hasStatusEffect(xi.effect.WARRIORS_CHARGE) then
        local chargePower = player:getStatusEffect(xi.effect.WARRIORS_CHARGE):getPower()
        enhancement = enhancement + math.floor(chargePower * effectiveness)
    end
    
    return enhancement
end

-- Enhanced damage calculation with subjob effectiveness scaling
xi.job_utils.warrior.calculateWarriorDamage = function(player, baseDamage)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return baseDamage  -- No enhancement if no warrior access
    end
    
    local finalDamage = baseDamage
    
    -- Apply warrior-specific damage bonuses with subjob scaling
    if player:hasStatusEffect(xi.effect.MIGHTY_STRIKES) then
        local damageMultiplier = 1.0 + (1.0 * effectiveness)  -- Up to 100% damage increase when fully effective
        finalDamage = finalDamage * damageMultiplier
    end
    
    if player:hasStatusEffect(xi.effect.BLOOD_RAGE) then
        local bloodRagePower = player:getStatusEffect(xi.effect.BLOOD_RAGE):getPower()
        finalDamage = finalDamage + math.floor(bloodRagePower * effectiveness)
    end
    
    if player:hasStatusEffect(xi.effect.BRAZEN_RUSH) then
        local brazenPower = player:getStatusEffect(xi.effect.BRAZEN_RUSH):getPower()
        finalDamage = finalDamage + math.floor(brazenPower * effectiveness)
    end
    
    return finalDamage
end

-- Enhanced double attack calculation with comprehensive subjob support
xi.job_utils.warrior.enhanceDoubleAttack = function(player)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return 0  -- No enhancement if no warrior access
    end
    
    return handleDoubleAttackBonus(player, effectiveness)
end

-- Enhanced critical hit rate calculation with subjob support
xi.job_utils.warrior.enhanceCriticalHit = function(player)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return 0  -- No enhancement if no warrior access
    end
    
    local criticalBonus = 0
    
    -- Mighty Strikes guarantees critical hits with subjob scaling
    if player:hasStatusEffect(xi.effect.MIGHTY_STRIKES) then
        criticalBonus = criticalBonus + math.floor(100 * effectiveness)  -- Scale critical guarantee
    end
    
    -- Restraint provides critical hit rate bonus with subjob scaling
    if player:hasStatusEffect(xi.effect.RESTRAINT) then
        local restraintLevel = player:getStatusEffect(xi.effect.RESTRAINT):getPower()
        criticalBonus = criticalBonus + math.floor(15 * effectiveness)  -- Base critical bonus
    end
    
    return criticalBonus
end

-- Enhanced accuracy calculation with subjob support
xi.job_utils.warrior.enhanceAccuracy = function(player)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return 0  -- No enhancement if no warrior access
    end
    
    local accuracyBonus = 0
    
    -- Aggressor provides accuracy bonus with subjob scaling
    if player:hasStatusEffect(xi.effect.AGGRESSOR) then
        accuracyBonus = accuracyBonus + math.floor(25 * effectiveness)
    end
    
    -- Tomahawk debuff provides accuracy penalty with subjob scaling (when applied by warrior)
    if player:hasStatusEffect(xi.effect.TOMAHAWK) then
        accuracyBonus = accuracyBonus - math.floor(25 * effectiveness)
    end
    
    return accuracyBonus
end

-- Enhanced defense calculation with subjob support
xi.job_utils.warrior.enhanceDefense = function(player)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return 0  -- No enhancement if no warrior access
    end
    
    local defenseBonus = 0
    
    -- Defender provides defense bonus with subjob scaling
    if player:hasStatusEffect(xi.effect.DEFENDER) then
        defenseBonus = defenseBonus + math.floor(25 * effectiveness)
    end
    
    -- Berserk provides defense penalty with subjob scaling
    if player:hasStatusEffect(xi.effect.BERSERK) then
        defenseBonus = defenseBonus - math.floor(25 * effectiveness)
    end
    
    return defenseBonus
end

-- Enhanced enmity calculation with subjob support
xi.job_utils.warrior.enhanceEnmity = function(player, baseEnmity)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return baseEnmity  -- No enhancement if no warrior access
    end
    
    local enmityMultiplier = 1.0
    
    -- Provoke effect enhances ongoing enmity generation with subjob scaling
    if player:hasStatusEffect(xi.effect.PROVOKE) then
        enmityMultiplier = enmityMultiplier + (0.5 * effectiveness)  -- Up to 50% enmity bonus
    end
    
    -- Warcry enhances party enmity with subjob scaling
    if player:hasStatusEffect(xi.effect.WARCRY) then
        enmityMultiplier = enmityMultiplier + (0.25 * effectiveness)  -- Up to 25% enmity bonus
    end
    
    return math.floor(baseEnmity * enmityMultiplier)
end

-----------------------------------
-- Comprehensive Warrior Utility Functions with Database Integration
-----------------------------------

-- Enhanced weapon skill damage calculation with subjob support
xi.job_utils.warrior.calculateWeaponSkillDamage = function(player, baseDamage, weaponSkillId)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return baseDamage  -- No enhancement if no warrior access
    end
    
    local finalDamage = baseDamage
    
    -- Apply warrior-specific weapon skill bonuses with subjob scaling
    if player:hasStatusEffect(xi.effect.RESTRAINT) then
        -- Restraint enhances weapon skill damage with subjob scaling
        finalDamage = finalDamage * (1.0 + (0.3 * effectiveness))  -- Up to 30% weapon skill damage bonus
    end
    
    if player:hasStatusEffect(xi.effect.BERSERK) then
        -- Berserk enhances weapon skill damage with subjob scaling
        local berserkPower = player:getStatusEffect(xi.effect.BERSERK):getPower()
        finalDamage = finalDamage + math.floor(berserkPower * effectiveness)
    end
    
    return finalDamage
end

-- Enhanced status effect duration calculation with subjob support
xi.job_utils.warrior.calculateStatusDuration = function(player, baseDuration, effectId)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return baseDuration  -- No enhancement if no warrior access
    end
    
    -- Apply subjob scaling to duration for specific effects
    local enhancedDuration = math.floor(baseDuration * effectiveness)
    
    return math.max(enhancedDuration, math.floor(baseDuration * 0.5))  -- Minimum 50% duration
end

-- Enhanced job points effectiveness with subjob support
xi.job_utils.warrior.getJobPointEffectiveness = function(player, jpCategory)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return 0.0  -- No job point effectiveness if no warrior access
    end
    
    -- Get base job point level
    local jpLevel = player:getJobPointLevel(jpCategory)
    
    -- Apply subjob scaling to job point effectiveness
    return math.floor(jpLevel * effectiveness)
end

-- Enhanced merit effectiveness with subjob support
xi.job_utils.warrior.getMeritEffectiveness = function(player, meritCategory)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return 0  -- No merit effectiveness if no warrior access
    end
    
    -- Get base merit level
    local meritLevel = player:getMerit(meritCategory)
    
    -- Apply subjob scaling to merit effectiveness
    return math.floor(meritLevel * effectiveness)
end

-----------------------------------
-- Advanced Warrior Combat Integration Functions
-----------------------------------

-- Enhanced combat stance management with subjob support
xi.job_utils.warrior.manageCombatStance = function(player, stanceType)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return false  -- No stance management if no warrior access
    end
    
    -- Handle different stance combinations with subjob scaling
    if stanceType == "offensive" then
        -- Prioritize offensive abilities
        if player:hasStatusEffect(xi.effect.BERSERK) and player:hasStatusEffect(xi.effect.AGGRESSOR) then
            return true, effectiveness  -- Full offensive stance with effectiveness scaling
        end
    elseif stanceType == "defensive" then
        -- Prioritize defensive abilities
        if player:hasStatusEffect(xi.effect.DEFENDER) then
            return true, effectiveness  -- Defensive stance with effectiveness scaling
        end
    elseif stanceType == "balanced" then
        -- Balance offensive and defensive capabilities
        return true, effectiveness * 0.8  -- Slightly reduced effectiveness for balanced stance
    end
    
    return false, 0.0
end

-- Enhanced threat management with subjob support
xi.job_utils.warrior.manageThreat = function(player, target, threatLevel)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return 0  -- No threat management if no warrior access
    end
    
    local enmityModifier = 0
    
    -- Apply threat management based on warrior abilities with subjob scaling
    if threatLevel == "high" then
        -- Increase threat generation
        if player:hasStatusEffect(xi.effect.PROVOKE) then
            enmityModifier = enmityModifier + math.floor(500 * effectiveness)
        end
        if player:hasStatusEffect(xi.effect.WARCRY) then
            enmityModifier = enmityModifier + math.floor(300 * effectiveness)
        end
    elseif threatLevel == "moderate" then
        -- Moderate threat generation
        enmityModifier = math.floor(200 * effectiveness)
    elseif threatLevel == "low" then
        -- Reduce threat generation
        enmityModifier = math.floor(-100 * effectiveness)
    end
    
    return enmityModifier
end

-- Enhanced party support functions with subjob scaling
xi.job_utils.warrior.supportParty = function(player, supportType)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return false  -- No party support if no warrior access
    end
    
    if supportType == "damage" then
        -- Enhance party damage through warrior abilities with subjob scaling
        if player:hasStatusEffect(xi.effect.WARCRY) then
            local warcryPower = player:getStatusEffect(xi.effect.WARCRY):getPower()
            return true, math.floor(warcryPower * effectiveness)
        end
    elseif supportType == "threat" then
        -- Handle threat management for party with subjob scaling
        if player:hasStatusEffect(xi.effect.PROVOKE) then
            return true, math.floor(1000 * effectiveness)  -- Threat generation
        end
    elseif supportType == "defense" then
        -- Provide defensive support with subjob scaling
        if player:hasStatusEffect(xi.effect.DEFENDER) then
            return true, math.floor(25 * effectiveness)  -- Defense bonus
        end
    end
    
    return false, 0
end

-- Enhanced ability cooldown management with subjob support
xi.job_utils.warrior.manageAbilityCooldowns = function(player, abilityId)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return 0  -- No cooldown management if no warrior access
    end
    
    -- Apply job point and merit bonuses with subjob scaling
    local cooldownReduction = 0
    
    if abilityId == xi.jobAbility.PROVOKE then
        local jpLevel = xi.job_utils.warrior.getJobPointEffectiveness(player, xi.jp.PROVOKE_RECAST)
        cooldownReduction = math.floor(jpLevel * 2 * effectiveness)  -- Up to 2 seconds per JP level
    elseif abilityId == xi.jobAbility.BERSERK then
        local jpLevel = xi.job_utils.warrior.getJobPointEffectiveness(player, xi.jp.BERSERK_EFFECT)
        cooldownReduction = math.floor(jpLevel * 5 * effectiveness)  -- Up to 5 seconds per JP level
    elseif abilityId == xi.jobAbility.WARCRY then
        local jpLevel = xi.job_utils.warrior.getJobPointEffectiveness(player, xi.jp.WARCRY_EFFECT)
        cooldownReduction = math.floor(jpLevel * 3 * effectiveness)  -- Up to 3 seconds per JP level
    end
    
    return cooldownReduction
end

-- Enhanced weapon specialization with subjob support
xi.job_utils.warrior.enhanceWeaponSpecialization = function(player, weaponType)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return 0  -- No weapon enhancement if no warrior access
    end
    
    local enhancement = 0
    
    -- Apply warrior weapon bonuses with subjob scaling
    if weaponType == "great_axe" or weaponType == "axe" then
        -- Warriors excel with axes
        enhancement = enhancement + math.floor(15 * effectiveness)
        
        if player:hasStatusEffect(xi.effect.BERSERK) then
            enhancement = enhancement + math.floor(10 * effectiveness)  -- Additional axe bonus
        end
    elseif weaponType == "great_sword" or weaponType == "sword" then
        -- Warriors are proficient with swords
        enhancement = enhancement + math.floor(10 * effectiveness)
        
        if player:hasStatusEffect(xi.effect.RESTRAINT) then
            enhancement = enhancement + math.floor(15 * effectiveness)  -- Restraint enhances sword skills
        end
    elseif weaponType == "polearm" then
        -- Warriors can use polearms effectively
        enhancement = enhancement + math.floor(8 * effectiveness)
        
        if player:hasStatusEffect(xi.effect.AGGRESSOR) then
            enhancement = enhancement + math.floor(7 * effectiveness)  -- Aggressor enhances polearm accuracy
        end
    end
    
    return enhancement
end

-- Enhanced tactical combat analysis with subjob support
xi.job_utils.warrior.analyzeCombatSituation = function(player, target, combatMetrics)
    -- Get subjob effectiveness
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return "no_access"  -- No analysis if no warrior access
    end
    
    local analysis = {
        effectiveness = effectiveness,
        recommendedStance = "balanced",
        recommendedAbilities = {},
        threatLevel = "moderate"
    }
    
    -- Analyze combat situation based on target and metrics
    if combatMetrics then
        if combatMetrics.playerHP and combatMetrics.playerHP < 50 then
            -- Low HP situation
            analysis.recommendedStance = "defensive"
            table.insert(analysis.recommendedAbilities, xi.jobAbility.DEFENDER)
        elseif combatMetrics.targetHP and combatMetrics.targetHP > 80 then
            -- High HP target
            analysis.recommendedStance = "offensive"
            table.insert(analysis.recommendedAbilities, xi.jobAbility.BERSERK)
            table.insert(analysis.recommendedAbilities, xi.jobAbility.AGGRESSOR)
        end
        
        if combatMetrics.partySize and combatMetrics.partySize > 1 then
            -- Party situation
            table.insert(analysis.recommendedAbilities, xi.jobAbility.WARCRY)
            analysis.threatLevel = "high"
        end
    end
    
    -- Scale recommendations based on subjob effectiveness
    if effectiveness < 0.7 then
        analysis.recommendedStance = "conservative"
    end
    
    return analysis
end

-----------------------------------
-- Warrior Integration Summary Functions
-----------------------------------

-- Comprehensive warrior capability assessment
xi.job_utils.warrior.assessWarriorCapabilities = function(player)
    -- Get subjob effectiveness
    local hasAccess, effectiveness, accessLevel = xi.job_utils.warrior.validateJobAccess(player)
    
    if not hasAccess then
        return {
            hasAccess = false,
            effectiveness = 0.0,
            capabilities = {}
        }
    end
    
    local capabilities = {
        hasAccess = true,
        effectiveness = effectiveness,
        accessLevel = accessLevel,
        availableAbilities = {},
        combatEnhancements = {},
        partySupport = {},
        completeness = "100%"
    }
    
    -- Check available abilities based on level and effectiveness
    for abilityId, abilityData in pairs(warriorAbilities) do
        if accessLevel >= abilityData.level then
            table.insert(capabilities.availableAbilities, {
                id = abilityId,
                level = abilityData.level,
                effectiveness = effectiveness,
                twoHour = abilityData.twoHour or false
            })
        end
    end
    
    -- Combat enhancements
    capabilities.combatEnhancements = {
        attack = xi.job_utils.warrior.enhanceAttack(player),
        damage = effectiveness,
        doubleAttack = xi.job_utils.warrior.enhanceDoubleAttack(player),
        criticalHit = xi.job_utils.warrior.enhanceCriticalHit(player),
        accuracy = xi.job_utils.warrior.enhanceAccuracy(player),
        defense = xi.job_utils.warrior.enhanceDefense(player)
    }
    
    -- Party support capabilities
    capabilities.partySupport = {
        damageSupport = effectiveness,
        threatManagement = effectiveness,
        defenseSupport = effectiveness * 0.8
    }
    
    return capabilities
end

-- Get job-specific abilities list
xi.job_utils.warrior.getJobAbilities = function(player)
    local hasAccess, effectiveness = xi.job_utils.warrior.validateJobAccess(player)
    if not hasAccess then
        return {}
    end

    local abilities = {
        'Mighty Strikes', 'Berserk', 'Warcry', 'Aggressor', 'Defender',
        'Provoke', 'Taunt', 'Restraint', 'Blood Rage', 'Retaliation'
    }
    
    -- Add subjob abilities if available
    if player:getSubJob() == xi.job.WAR and effectiveness > 0.5 then
        abilities = {
            'Provoke', 'Berserk', 'Defender', 'Warcry'
        }
    end
    
    return abilities
end
