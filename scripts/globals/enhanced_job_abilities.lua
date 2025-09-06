-----------------------------------
-- Enhanced Job Abilities System for ITERATION 9
-- AoE enmity generation and cross-job interactions
-----------------------------------

xi = xi or {}
xi.enhanced_abilities = xi.enhanced_abilities or {}

-- AoE enmity generation system
xi.enhanced_abilities.generateAoEEnmity = function(caster, targets, abilityId, enmityPower)
    enmityPower = enmityPower or 1
    
    local baseEnmity = 100 * enmityPower
    local targetCount = #targets
    
    -- Reduce enmity per target for AoE abilities (retail behavior)
    local enmityPerTarget = baseEnmity
    if targetCount > 1 then
        enmityPerTarget = baseEnmity * (0.8 / targetCount) -- Diminishing returns
    end
    
    for _, target in pairs(targets) do
        if target:isValidTarget(caster, xi.targetFlag.ENEMY) then
            local ce = enmityPerTarget * 0.6
            local ve = enmityPerTarget * 0.4
            
            -- Job-specific AoE enmity bonuses
            if caster:getMainJob() == xi.job.PLD then
                ce = ce * 1.2 -- Paladins generate 20% more CE from AoE abilities
            elseif caster:getMainJob() == xi.job.WAR then
                ve = ve * 1.3 -- Warriors generate 30% more VE from AoE abilities
            end
            
            target:addEnmity(caster, ce, ve)
        end
    end
    
    return targetCount
end

-- Cross-job ability interactions
xi.enhanced_abilities.checkAbilityInteractions = function(caster, abilityId, target)
    local interactions = {}
    
    -- Check for combo abilities
    local lastAbility = caster:getLocalVar("lastAbilityUsed")
    local timeSinceLastAbility = os.time() - caster:getLocalVar("lastAbilityTime")
    
    -- Combo window is 10 seconds
    if timeSinceLastAbility <= 10 then
        -- Warrior + Paladin combo (Provoke -> Cover)
        if lastAbility == xi.jobAbility.PROVOKE and abilityId == xi.jobAbility.COVER then
            interactions.combo = "TANK_COORDINATION"
            interactions.bonus = 1.5 -- 50% effectiveness bonus
        end
        
        -- Ninja combo abilities (Innin -> Trick Attack)
        if lastAbility == xi.jobAbility.INNIN and abilityId == xi.jobAbility.TRICK_ATTACK then
            interactions.combo = "STEALTH_COORDINATION"
            interactions.bonus = 2.0 -- Double damage
        end
        
        -- Dragoon jump combination
        if lastAbility == xi.jobAbility.JUMP and abilityId == xi.jobAbility.HIGH_JUMP then
            interactions.combo = "AERIAL_ASSAULT"
            interactions.bonus = 1.3 -- 30% damage bonus
        end
    end
    
    -- Job Point ability enhancements
    if caster:isPC() then
        local jpLevel = caster:getJobPointLevel(abilityId)
        if jpLevel > 0 then
            interactions.jpBonus = 1 + (jpLevel * 0.05) -- 5% per JP level
        end
    end
    
    return interactions
end

-- Enhanced cooldown display system
xi.enhanced_abilities.displayCooldown = function(player, abilityId)
    local recastInfo = {
        abilityId = abilityId,
        timeRemaining = 0,
        totalRecast = 0,
        percentComplete = 0
    }
    
    -- Get recast information
    local recastTime = player:getRecast(xi.recast.ABILITY, abilityId)
    local maxRecast = player:getAbilityRecast(abilityId)
    
    recastInfo.timeRemaining = recastTime / 1000 -- Convert to seconds
    recastInfo.totalRecast = maxRecast / 1000
    recastInfo.percentComplete = math.max(0, (maxRecast - recastTime) / maxRecast * 100)
    
    -- Send enhanced recast display to client
    if recastInfo.timeRemaining > 0 then
        local minutes = math.floor(recastInfo.timeRemaining / 60)
        local seconds = math.floor(recastInfo.timeRemaining % 60)
        
        local message = string.format("Ability recast: %02d:%02d (%.1f%% complete)", 
                                    minutes, seconds, recastInfo.percentComplete)
        player:printToPlayer(message, xi.msg.channel.SYSTEM_3)
    end
    
    return recastInfo
end

-- Ability power scaling system
xi.enhanced_abilities.calculateAbilityPower = function(caster, abilityId, basePower)
    local finalPower = basePower
    
    -- Level scaling
    local casterLevel = caster:getMainLvl()
    local levelBonus = math.max(0, (casterLevel - 30) * 0.02) -- 2% per level above 30
    finalPower = finalPower * (1 + levelBonus)
    
    -- Stat-based scaling for abilities
    local mainStat = caster:getStat(caster:getMainStat())
    local statBonus = (mainStat - 50) * 0.01 -- 1% per stat point above 50
    finalPower = finalPower * (1 + statBonus)
    
    -- Gear modifications
    local gearBonus = caster:getMod(xi.mod.ABILITY_POWER) / 100
    finalPower = finalPower * (1 + gearBonus)
    
    -- Job mastery bonus
    local jobLevel = caster:getJobLevel(caster:getMainJob())
    if jobLevel >= 75 then
        local masteryBonus = (jobLevel - 74) * 0.01 -- 1% per level above 75
        finalPower = finalPower * (1 + masteryBonus)
    end
    
    return finalPower
end

-- Enhanced status effect application
xi.enhanced_abilities.applyAbilityStatusEffect = function(caster, target, effect, power, duration)
    -- Calculate final duration with enhancements
    local finalDuration = duration
    
    -- Caster enhancements
    local enhancingSkill = caster:getSkillLevel(xi.skill.ENHANCING_MAGIC)
    if enhancingSkill > 0 then
        finalDuration = finalDuration + (enhancingSkill * 0.1) -- 0.1 seconds per skill level
    end
    
    -- Target resistance
    local resistance = target:getMod(effect.resistanceMod or xi.mod.NONE)
    if resistance > 0 then
        finalDuration = finalDuration * (1 - resistance / 100)
        power = power * (1 - resistance / 100)
    end
    
    -- Apply the status effect
    if finalDuration > 0 and power > 0 then
        target:addStatusEffect(effect.id, power, 0, finalDuration)
        return true
    end
    
    return false
end

-- Party coordination system for abilities
xi.enhanced_abilities.coordinatePartyAbilities = function(party, leaderId, abilityId)
    local coordination = {
        synchronized = false,
        participants = {},
        effectiveness = 1.0
    }
    
    local leader = GetPlayerByID(leaderId)
    if not leader then
        return coordination
    end
    
    -- Find party members who can use complementary abilities
    for _, member in pairs(party) do
        if member:getID() ~= leaderId and member:getDistance(leader) <= 15 then
            local complementaryAbility = xi.enhanced_abilities.findComplementaryAbility(abilityId, member)
            if complementaryAbility then
                table.insert(coordination.participants, {
                    player = member,
                    ability = complementaryAbility
                })
            end
        end
    end
    
    -- Calculate coordination effectiveness
    if #coordination.participants > 0 then
        coordination.synchronized = true
        coordination.effectiveness = 1.0 + (#coordination.participants * 0.15) -- 15% per participant
    end
    
    return coordination
end

-- Find complementary abilities for coordination
xi.enhanced_abilities.findComplementaryAbility = function(primaryAbility, player)
    local complementaryMap = {
        [xi.jobAbility.PROVOKE] = {xi.jobAbility.COVER, xi.jobAbility.SENTINEL},
        [xi.jobAbility.WEAPON_BASH] = {xi.jobAbility.SHIELD_BASH, xi.jobAbility.STUN},
        [xi.jobAbility.SNEAK_ATTACK] = {xi.jobAbility.TRICK_ATTACK, xi.jobAbility.MUG},
        [xi.jobAbility.BERSERK] = {xi.jobAbility.AGGRESSOR, xi.jobAbility.DEFENDER},
        [xi.jobAbility.BOOST] = {xi.jobAbility.FOCUS, xi.jobAbility.CHAKRA}
    }
    
    local complementaries = complementaryMap[primaryAbility]
    if not complementaries then
        return nil
    end
    
    -- Check if player has any complementary abilities available
    for _, ability in pairs(complementaries) do
        if player:hasJobAbility(ability) and player:getRecast(xi.recast.ABILITY, ability) == 0 then
            return ability
        end
    end
    
    return nil
end

print("Enhanced Job Abilities System loaded for ITERATION 9")