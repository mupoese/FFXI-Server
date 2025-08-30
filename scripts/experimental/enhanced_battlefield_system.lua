-----------------------------------
-- Enhanced Battlefield System
-- Phase 4: Complete battlefield mechanics and reward improvements
-----------------------------------
require('scripts/globals/battlefield')
require('scripts/globals/items')
require('scripts/globals/content_validation')
-----------------------------------
xi = xi or {}
xi.battlefield = xi.battlefield or {}
xi.battlefield.enhanced = xi.battlefield.enhanced or {}

-- Enhanced battlefield status tracking
xi.battlefield.enhanced.status =
{
    PREPARING     = 0,  -- Players entering, setup in progress
    ACTIVE        = 1,  -- Battle in progress
    VICTORY       = 2,  -- Players won
    DEFEAT        = 3,  -- Players lost
    TIMEOUT       = 4,  -- Time limit exceeded
    ABANDONED     = 5,  -- Players left battlefield
}

-- Battlefield difficulty modifiers
xi.battlefield.enhanced.difficulty =
{
    EASY          = 0.8,  -- 80% of normal stats
    NORMAL        = 1.0,  -- 100% normal stats
    HARD          = 1.2,  -- 120% of normal stats
    VERY_HARD     = 1.5,  -- 150% of normal stats
    ULTIMATE      = 2.0,  -- 200% of normal stats
}

-- Reward distribution types
xi.battlefield.enhanced.rewardType =
{
    COMPLETION    = 1,    -- Rewards for completing battle
    VICTORY       = 2,    -- Rewards for winning battle
    PARTICIPATION = 3,    -- Rewards for participation
    BONUS         = 4,    -- Bonus rewards for special conditions
    PENALTY       = 5,    -- Penalty for failure/abandonment
}

-- Enhanced battlefield configuration structure
xi.battlefield.enhanced.config = {
    -- Time management
    timeLimit = 1800,           -- 30 minutes default
    warningTimes = { 600, 300, 60 }, -- Warning at 10min, 5min, 1min remaining
    
    -- Difficulty scaling
    difficultyScaling = true,
    baseLevel = 75,
    levelCap = 99,
    
    -- Reward system
    rewards = {
        experience = {
            base = 1000,
            scalingFactor = 1.2,
            bonusForDifficulty = true,
        },
        gil = {
            base = 5000,
            scalingFactor = 1.1,
            bonusForSpeed = true,
        },
        items = {},
        keyItems = {},
    },
    
    -- Special mechanics
    mechanics = {
        limitTrusts = true,
        preventSubjobs = false,
        allowSaves = false,
        forceLevel = nil,
    },
}

-- Initialize enhanced battlefield
xi.battlefield.enhanced.initialize = function(battlefield, config)
    if not battlefield then
        return false
    end
    
    config = config or xi.battlefield.enhanced.config
    
    -- Set enhanced configuration
    battlefield:setLocalVar("enhancedBF", 1)
    battlefield:setLocalVar("config", utils.serialize(config))
    battlefield:setLocalVar("startTime", os.time())
    battlefield:setLocalVar("status", xi.battlefield.enhanced.status.PREPARING)
    
    -- Initialize reward tracking
    battlefield:setLocalVar("rewardData", utils.serialize({}))
    
    return true
end

-- Enhanced battlefield entry with validation
xi.battlefield.enhanced.onEntry = function(player, battlefield)
    if not battlefield or not player then
        return false
    end
    
    -- Validate player eligibility
    local validation = xi.battlefield.enhanced.validateEntry(player, battlefield)
    if not validation.success then
        player:messageSpecial(zones[player:getZoneID()].text.CANNOT_ENTER_BATTLEFIELD, validation.reason)
        return false
    end
    
    -- Apply battlefield restrictions
    xi.battlefield.enhanced.applyRestrictions(player, battlefield)
    
    -- Initialize player tracking
    xi.battlefield.enhanced.initializePlayerTracking(player, battlefield)
    
    -- Update battlefield status
    xi.battlefield.enhanced.updateStatus(battlefield)
    
    return true
end

-- Validate player entry requirements
xi.battlefield.enhanced.validateEntry = function(player, battlefield)
    local config = utils.deserialize(battlefield:getLocalVar("config")) or xi.battlefield.enhanced.config
    
    -- Check level requirements
    if config.levelCap and player:getMainLvl() > config.levelCap then
        return { success = false, reason = "Level too high for this battlefield" }
    end
    
    -- Check trust limitations
    if config.mechanics.limitTrusts then
        local trustCount = 0
        local zone = player:getZone()
        if zone then
            local trusts = zone:getEntitiesByType(xi.objType.TRUST)
            for _, trust in ipairs(trusts) do
                if trust:getMaster() and trust:getMaster():getID() == player:getID() then
                    trustCount = trustCount + 1
                end
            end
        end
        
        if trustCount > 3 then -- Most battlefields limit to 3 trusts
            return { success = false, reason = "Too many trusts active" }
        end
    end
    
    -- Check subjob restrictions
    if config.mechanics.preventSubjobs and player:getSubJob() ~= xi.job.NONE then
        return { success = false, reason = "Subjobs not allowed in this battlefield" }
    end
    
    return { success = true }
end

-- Apply battlefield restrictions to player
xi.battlefield.enhanced.applyRestrictions = function(player, battlefield)
    local config = utils.deserialize(battlefield:getLocalVar("config")) or xi.battlefield.enhanced.config
    
    -- Force level if specified
    if config.mechanics.forceLevel then
        player:setLocalVar("originalLevel", player:getMainLvl())
        player:setLevel(config.mechanics.forceLevel)
    end
    
    -- Apply battlefield status effect
    player:addStatusEffect(xi.effect.BATTLEFIELD, 1, 0, 0)
    
    -- Disable saves if configured
    if not config.mechanics.allowSaves then
        player:addStatusEffect(xi.effect.SAVE_DISABLED, 1, 0, 0)
    end
end

-- Initialize player tracking for rewards and statistics
xi.battlefield.enhanced.initializePlayerTracking = function(player, battlefield)
    local playerData = {
        entryTime = os.time(),
        damageDealt = 0,
        healingDone = 0,
        deathCount = 0,
        statusEffectsApplied = 0,
        participated = true,
    }
    
    player:setLocalVar("bfPlayerData", utils.serialize(playerData))
    
    -- Start tracking combat events
    xi.battlefield.enhanced.addCombatTracking(player, battlefield)
end

-- Add combat event tracking for enhanced rewards
xi.battlefield.enhanced.addCombatTracking = function(player, battlefield)
    -- Track damage dealt
    player:addListener('DAMAGE_DEALT', 'BF_DAMAGE_TRACKING', function(playerArg, target, damage)
        local data = utils.deserialize(playerArg:getLocalVar("bfPlayerData")) or {}
        data.damageDealt = (data.damageDealt or 0) + damage
        playerArg:setLocalVar("bfPlayerData", utils.serialize(data))
    end)
    
    -- Track healing done
    player:addListener('HEALING_DONE', 'BF_HEALING_TRACKING', function(playerArg, target, healing)
        local data = utils.deserialize(playerArg:getLocalVar("bfPlayerData")) or {}
        data.healingDone = (data.healingDone or 0) + healing
        playerArg:setLocalVar("bfPlayerData", utils.serialize(data))
    end)
    
    -- Track deaths
    player:addListener('PLAYER_DEATH', 'BF_DEATH_TRACKING', function(playerArg)
        local data = utils.deserialize(playerArg:getLocalVar("bfPlayerData")) or {}
        data.deathCount = (data.deathCount or 0) + 1
        playerArg:setLocalVar("bfPlayerData", utils.serialize(data))
    end)
end

-- Enhanced battlefield completion with comprehensive rewards
xi.battlefield.enhanced.onCompletion = function(battlefield, victory)
    if not battlefield then
        return false
    end
    
    local config = utils.deserialize(battlefield:getLocalVar("config")) or xi.battlefield.enhanced.config
    local players = battlefield:getPlayers()
    
    -- Calculate battle statistics
    local battleStats = xi.battlefield.enhanced.calculateBattleStats(battlefield, players)
    
    -- Distribute rewards based on victory and performance
    for _, player in ipairs(players) do
        xi.battlefield.enhanced.distributeRewards(player, battlefield, victory, battleStats)
    end
    
    -- Update battlefield status
    local finalStatus = victory and xi.battlefield.enhanced.status.VICTORY or xi.battlefield.enhanced.status.DEFEAT
    battlefield:setLocalVar("status", finalStatus)
    battlefield:setLocalVar("completionTime", os.time())
    
    -- Clean up tracking
    xi.battlefield.enhanced.cleanupTracking(players)
    
    -- Log completion for validation
    xi.content.validation.addResult(
        xi.content.validation.category.BATTLEFIELD_REWARDS,
        "Battlefield Completion",
        xi.content.validation.resultType.PASS,
        victory and "Battlefield completed successfully" or "Battlefield completed with defeat",
        {
            battlefieldId = battlefield:getID(),
            victory = victory,
            playerCount = #players,
            battleStats = battleStats,
        }
    )
    
    return true
end

-- Calculate comprehensive battle statistics
xi.battlefield.enhanced.calculateBattleStats = function(battlefield, players)
    local startTime = battlefield:getLocalVar("startTime")
    local completionTime = os.time()
    local battleDuration = completionTime - startTime
    
    local stats = {
        duration = battleDuration,
        totalDamage = 0,
        totalHealing = 0,
        totalDeaths = 0,
        participationScore = 0,
        speedBonus = 0,
        difficultyMultiplier = 1.0,
    }
    
    -- Aggregate player statistics
    for _, player in ipairs(players) do
        local playerData = utils.deserialize(player:getLocalVar("bfPlayerData")) or {}
        stats.totalDamage = stats.totalDamage + (playerData.damageDealt or 0)
        stats.totalHealing = stats.totalHealing + (playerData.healingDone or 0)
        stats.totalDeaths = stats.totalDeaths + (playerData.deathCount or 0)
        
        -- Calculate participation score (damage + healing - death penalty)
        local playerScore = (playerData.damageDealt or 0) + (playerData.healingDone or 0) - (playerData.deathCount or 0) * 1000
        stats.participationScore = stats.participationScore + math.max(0, playerScore)
    end
    
    -- Calculate speed bonus (faster completion = higher bonus)
    local timeLimit = battlefield:getTimeRemaining() + battleDuration
    if battleDuration < timeLimit * 0.5 then
        stats.speedBonus = 1.5  -- 50% bonus for very fast completion
    elseif battleDuration < timeLimit * 0.75 then
        stats.speedBonus = 1.25 -- 25% bonus for fast completion
    else
        stats.speedBonus = 1.0  -- No bonus
    end
    
    return stats
end

-- Distribute enhanced rewards based on performance
xi.battlefield.enhanced.distributeRewards = function(player, battlefield, victory, battleStats)
    local config = utils.deserialize(battlefield:getLocalVar("config")) or xi.battlefield.enhanced.config
    local playerData = utils.deserialize(player:getLocalVar("bfPlayerData")) or {}
    
    -- Calculate individual performance multiplier
    local performanceMultiplier = 1.0
    if battleStats.participationScore > 0 then
        local playerScore = (playerData.damageDealt or 0) + (playerData.healingDone or 0) - (playerData.deathCount or 0) * 1000
        performanceMultiplier = math.max(0.5, math.min(2.0, playerScore / (battleStats.participationScore / #battlefield:getPlayers())))
    end
    
    -- Award experience
    if config.rewards.experience and config.rewards.experience.base > 0 then
        local expReward = config.rewards.experience.base
        
        if victory then
            expReward = expReward * (config.rewards.experience.scalingFactor or 1.2)
        else
            expReward = expReward * 0.5 -- Reduced for defeat
        end
        
        expReward = expReward * performanceMultiplier * battleStats.speedBonus
        
        player:addExp(math.floor(expReward))
        player:messageBasic(xi.msg.basic.EXP_OBTAINED, math.floor(expReward))
    end
    
    -- Award gil
    if config.rewards.gil and config.rewards.gil.base > 0 then
        local gilReward = config.rewards.gil.base
        
        if victory then
            gilReward = gilReward * (config.rewards.gil.scalingFactor or 1.1)
        else
            gilReward = gilReward * 0.3 -- Significantly reduced for defeat
        end
        
        if config.rewards.gil.bonusForSpeed then
            gilReward = gilReward * battleStats.speedBonus
        end
        
        gilReward = gilReward * performanceMultiplier
        
        player:addGil(math.floor(gilReward))
        player:messageBasic(xi.msg.basic.GIL_OBTAINED, math.floor(gilReward))
    end
    
    -- Award items (only on victory or high performance)
    if victory or performanceMultiplier > 1.2 then
        xi.battlefield.enhanced.awardItems(player, config.rewards.items, performanceMultiplier)
    end
    
    -- Award key items (special rewards)
    if victory and config.rewards.keyItems then
        for _, keyItem in ipairs(config.rewards.keyItems) do
            if not player:hasKeyItem(keyItem) then
                player:addKeyItem(keyItem)
                player:messageSpecial(zones[player:getZoneID()].text.KEYITEM_OBTAINED, keyItem)
            end
        end
    end
end

-- Award items with smart distribution
xi.battlefield.enhanced.awardItems = function(player, items, multiplier)
    if not items or #items == 0 then
        return
    end
    
    for _, itemData in ipairs(items) do
        local itemId = itemData.id or itemData
        local quantity = itemData.quantity or 1
        local dropRate = itemData.dropRate or 1.0
        
        -- Apply performance multiplier to drop rate
        local adjustedDropRate = math.min(1.0, dropRate * multiplier)
        
        if math.random() <= adjustedDropRate then
            if player:getFreeSlotsCount() >= 1 then
                player:addItem(itemId, quantity)
                player:messageSpecial(zones[player:getZoneID()].text.ITEM_OBTAINED, itemId)
            else
                -- Store item for later pickup if inventory full
                player:setLocalVar("bfRewardItem_" .. itemId, (player:getLocalVar("bfRewardItem_" .. itemId) or 0) + quantity)
                player:messageSpecial(zones[player:getZoneID()].text.ITEM_CANNOT_BE_OBTAINED, itemId)
            end
        end
    end
end

-- Update battlefield status and notify players
xi.battlefield.enhanced.updateStatus = function(battlefield)
    local players = battlefield:getPlayers()
    local timeRemaining = battlefield:getTimeRemaining()
    local config = utils.deserialize(battlefield:getLocalVar("config")) or xi.battlefield.enhanced.config
    
    -- Check for time warnings
    for _, warningTime in ipairs(config.warningTimes) do
        if timeRemaining <= warningTime and timeRemaining > warningTime - 10 then
            for _, player in ipairs(players) do
                player:messageSpecial(zones[player:getZoneID()].text.TIME_REMAINING, timeRemaining)
            end
            break
        end
    end
    
    -- Check for timeout
    if timeRemaining <= 0 then
        battlefield:setLocalVar("status", xi.battlefield.enhanced.status.TIMEOUT)
        xi.battlefield.enhanced.onCompletion(battlefield, false)
    end
end

-- Enhanced battlefield monster spawning with scaling
xi.battlefield.enhanced.spawnMob = function(battlefield, mobId, pos, difficulty)
    local mob = battlefield:spawnMob(mobId, pos)
    
    if not mob then
        return nil
    end
    
    difficulty = difficulty or xi.battlefield.enhanced.difficulty.NORMAL
    
    -- Apply difficulty scaling
    if difficulty ~= xi.battlefield.enhanced.difficulty.NORMAL then
        local hpMultiplier = difficulty
        local damageMultiplier = difficulty
        local defenseMultiplier = math.sqrt(difficulty) -- Less dramatic scaling for defense
        
        mob:setHP(mob:getMaxHP() * hpMultiplier)
        mob:setMaxHP(mob:getMaxHP() * hpMultiplier)
        mob:setMobMod(xi.mobMod.ATT_BOOST, (damageMultiplier - 1.0) * 100)
        mob:setMobMod(xi.mobMod.DEF_BOOST, (defenseMultiplier - 1.0) * 100)
    end
    
    -- Add enhanced mob tracking
    mob:setLocalVar("battlefieldMob", 1)
    mob:setLocalVar("difficulty", difficulty)
    
    return mob
end

-- Clean up tracking after battlefield completion
xi.battlefield.enhanced.cleanupTracking = function(players)
    for _, player in ipairs(players) do
        -- Remove combat listeners
        player:removeListener("BF_DAMAGE_TRACKING")
        player:removeListener("BF_HEALING_TRACKING")
        player:removeListener("BF_DEATH_TRACKING")
        
        -- Restore original level if it was forced
        local originalLevel = player:getLocalVar("originalLevel")
        if originalLevel and originalLevel > 0 then
            player:setLevel(originalLevel)
            player:setLocalVar("originalLevel", 0)
        end
        
        -- Remove battlefield status effects
        player:delStatusEffect(xi.effect.BATTLEFIELD)
        player:delStatusEffect(xi.effect.SAVE_DISABLED)
        
        -- Clear tracking data
        player:setLocalVar("bfPlayerData", "")
    end
end

-- Battlefield diagnostic and validation
xi.battlefield.enhanced.runDiagnostic = function(battlefield)
    if not battlefield then
        return { error = "No battlefield provided" }
    end
    
    local diagnostic = {
        battlefieldId = battlefield:getID(),
        status = battlefield:getLocalVar("status"),
        timeRemaining = battlefield:getTimeRemaining(),
        players = {},
        mobs = {},
        errors = {},
        warnings = {},
    }
    
    -- Check players
    local players = battlefield:getPlayers()
    for _, player in ipairs(players) do
        local playerData = utils.deserialize(player:getLocalVar("bfPlayerData")) or {}
        table.insert(diagnostic.players, {
            id = player:getID(),
            name = player:getName(),
            level = player:getMainLvl(),
            hp = player:getHP(),
            mp = player:getMP(),
            tracking = playerData,
        })
    end
    
    -- Validate battlefield state
    xi.content.validation.validateBattlefieldRewards(battlefield, players)
    
    return diagnostic
end

return xi.battlefield.enhanced