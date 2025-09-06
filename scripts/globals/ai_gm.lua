-----------------------------------
-- AI-GM Communication Interface
-- Provides functions for AI-GM to communicate with players
-- and execute moderation actions
-----------------------------------

local aiGM = {}

-- AI-GM Configuration
aiGM.name = "AI-GM"
aiGM.level = 2
aiGM.announceActions = true
aiGM.mlEnabled = true
aiGM.battleTestEnabled = true

-- Message types for different situations
aiGM.MessageType = {
    INFO = 0,
    WARNING = 1,
    ERROR = 2,
    SYSTEM = 3,
    ML_ALERT = 4,
    BATTLE_TEST = 5
}

-- Severity levels for incidents
aiGM.Severity = {
    INFO = "info",
    WARNING = "warning", 
    MODERATE = "moderate",
    SEVERE = "severe",
    CRITICAL = "critical"
}

-- Available AI-GM actions
aiGM.Action = {
    WARN = "warn",
    TEMP_JAIL = "temp_jail",
    JAIL = "jail",
    KICK = "kick",
    TEMP_BAN = "temp_ban",
    ESCALATE_GM2 = "escalate_gm2",
    ESCALATE_GM3 = "escalate_gm3",
    NOTIFY_ADMIN = "notify_admin"
}

-----------------------------------
-- Communication Functions
-----------------------------------

-- Send a message to a specific player
function aiGM.sendMessage(player, message, messageType)
    if not player then
        return false
    end
    
    messageType = messageType or aiGM.MessageType.INFO
    local formattedMessage = string.format("[%s] %s", aiGM.name, message)
    
    -- Use appropriate message type
    if messageType == aiGM.MessageType.WARNING then
        player:printToPlayer(formattedMessage, CHAT_MESSAGE_TYPE_SYSTEM_2)
    elseif messageType == aiGM.MessageType.ERROR then
        player:printToPlayer(formattedMessage, CHAT_MESSAGE_TYPE_SYSTEM_3)
    else
        player:printToPlayer(formattedMessage, CHAT_MESSAGE_TYPE_SYSTEM_1)
    end
    
    return true
end

-- Send a warning to a player
function aiGM.sendWarning(player, reason)
    if not player then
        return false
    end
    
    local message = string.format("Warning: %s. Please adjust your behavior to avoid further action.", reason)
    aiGM.sendMessage(player, message, aiGM.MessageType.WARNING)
    
    -- Log the warning
    printf("[AI-GM] Warning sent to %s: %s", player:getName(), reason)
    
    return true
end

-- Broadcast a message to all online GMs
function aiGM.notifyGMs(message, minLevel)
    minLevel = minLevel or 1
    
    local formattedMessage = string.format("[%s] %s", aiGM.name, message)
    local notifiedCount = 0
    
    -- Get all online players
    local players = GetPlayersInZone(0) -- 0 gets all players across all zones
    
    for _, player in pairs(players) do
        if player and player:getGMLevel() >= minLevel then
            player:printToPlayer(formattedMessage, CHAT_MESSAGE_TYPE_SYSTEM_1)
            notifiedCount = notifiedCount + 1
        end
    end
    
    printf("[AI-GM] Notified %d GMs: %s", notifiedCount, message)
    return notifiedCount
end

-- Announce an action to all players if configured to do so
function aiGM.announceAction(action, playerName, reason)
    if not aiGM.announceActions then
        return
    end
    
    local message = ""
    
    if action == aiGM.Action.WARN then
        -- Don't announce warnings publicly
        return
    elseif action == aiGM.Action.TEMP_JAIL then
        message = string.format("Player %s has been temporarily jailed by %s.", playerName, aiGM.name)
    elseif action == aiGM.Action.JAIL then
        message = string.format("Player %s has been jailed by %s.", playerName, aiGM.name)
    elseif action == aiGM.Action.KICK then
        message = string.format("Player %s has been kicked by %s.", playerName, aiGM.name)
    else
        return -- Don't announce other actions
    end
    
    -- Broadcast to all players
    local players = GetPlayersInZone(0)
    for _, player in pairs(players) do
        if player then
            player:printToPlayer(message, CHAT_MESSAGE_TYPE_SYSTEM_1)
        end
    end
    
    printf("[AI-GM] Announced action: %s", message)
end

-----------------------------------
-- Moderation Functions
-----------------------------------

-- Jail a player using enhanced jail utilities
function aiGM.jailPlayer(player, cellId, reason, duration)
    if not player then
        return false
    end
    
    cellId = cellId or 1
    reason = reason or "Automated moderation"
    duration = duration or 30 -- Default 30 minutes
    
    -- Use the enhanced jail utilities
    jailutils.JailPlayer(player, cellId, reason)
    
    if duration > 0 then
        jailutils.SetJailDuration(player, duration)
    end
    
    -- Notify the player
    local durationText = duration > 0 and string.format("for %d minutes", duration) or "indefinitely"
    local message = string.format("You have been jailed %s. Reason: %s", durationText, reason)
    aiGM.sendMessage(player, message, aiGM.MessageType.ERROR)
    
    -- Notify GMs
    local gmMessage = string.format("Player %s has been jailed in cell %d %s. Reason: %s", 
                                   player:getName(), cellId, durationText, reason)
    aiGM.notifyGMs(gmMessage, 1)
    
    -- Announce if configured
    local actionType = duration > 0 and aiGM.Action.TEMP_JAIL or aiGM.Action.JAIL
    aiGM.announceAction(actionType, player:getName(), reason)
    
    return true
end

-- Pardon a player from jail
function aiGM.pardonPlayer(player)
    if not player then
        return false
    end
    
    if player:getCharVar("inJail") == 0 then
        return false -- Player not jailed
    end
    
    -- Use enhanced jail utilities
    jailutils.PardonPlayer(player)
    
    -- Notify the player
    aiGM.sendMessage(player, "You have been pardoned and released from jail.", aiGM.MessageType.INFO)
    
    -- Notify GMs
    local gmMessage = string.format("Player %s has been pardoned and released from jail.", player:getName())
    aiGM.notifyGMs(gmMessage, 1)
    
    printf("[AI-GM] Pardoned player %s", player:getName())
    
    return true
end

-- Kick a player from the server
function aiGM.kickPlayer(player, reason)
    if not player then
        return false
    end
    
    reason = reason or "Automated moderation"
    
    -- Send message before kicking
    local message = string.format("You are being disconnected. Reason: %s", reason)
    aiGM.sendMessage(player, message, aiGM.MessageType.ERROR)
    
    -- Notify GMs
    local gmMessage = string.format("Player %s has been kicked. Reason: %s", player:getName(), reason)
    aiGM.notifyGMs(gmMessage, 1)
    
    -- Announce the action
    aiGM.announceAction(aiGM.Action.KICK, player:getName(), reason)
    
    -- Kick the player (this would need to be implemented in the core)
    -- For now, just log it
    printf("[AI-GM] Kicked player %s: %s", player:getName(), reason)
    
    return true
end

-----------------------------------
-- Escalation Functions
-----------------------------------

-- Escalate an incident to human GMs
function aiGM.escalateToGM(playerName, incidentType, description, severity, gmLevel)
    gmLevel = gmLevel or 2
    
    local urgencyText = ""
    if severity == aiGM.Severity.SEVERE then
        urgencyText = "[URGENT] "
    elseif severity == aiGM.Severity.CRITICAL then
        urgencyText = "[CRITICAL] "
    end
    
    local escalationMessage = string.format("%sAI-GM Escalation - Player: %s, Type: %s, Details: %s", 
                                          urgencyText, playerName, incidentType, description)
    
    -- Notify appropriate level GMs
    local notifiedCount = aiGM.notifyGMs(escalationMessage, gmLevel)
    
    -- Log escalation
    printf("[AI-GM] Escalated to GM level %d: %s", gmLevel, escalationMessage)
    
    return notifiedCount > 0
end

-- Spawn a temporary GM character for handling escalations
function aiGM.spawnTemporaryGM(level, zoneName, reason)
    level = level or 2
    zoneName = zoneName or "Port_San_dOria"
    reason = reason or "AI-GM escalation response"
    
    -- This would need core implementation to actually spawn a GM character
    -- For now, we'll just notify existing GMs about the need
    
    local message = string.format("Temporary GM level %d needed in %s. Reason: %s", level, zoneName, reason)
    local notifiedCount = aiGM.notifyGMs(message, level)
    
    printf("[AI-GM] Requested temporary GM level %d in %s: %s", level, zoneName, reason)
    
    return notifiedCount > 0
end

-----------------------------------
-- Battle Test Functions
-----------------------------------

-- Create a GM battle test session
function aiGM.createBattleSession(gm, zoneName, configType, announcement, isPublic)
    if not gm then
        return nil
    end
    
    configType = configType or "standard_test"
    announcement = announcement or ""
    isPublic = isPublic == nil and true or isPublic  -- Default to public
    local zoneId = gm:getZoneID()
    local pos = gm:getPos()
    
    -- This would interface with the Python AI-GM service
    local sessionId = string.format("bt_%d_%d", gm:getID(), os.time())
    
    -- Send server-wide announcement if public demonstration
    if isPublic then
        aiGM.sendBattleTestAnnouncement(gm, zoneName, configType, pos, announcement)
    end
    
    aiGM.sendMessage(gm, string.format("Battle test session created: %s", sessionId), aiGM.MessageType.BATTLE_TEST)
    aiGM.sendMessage(gm, string.format("Zone: %s | Type: %s | Public: %s", zoneName, configType, isPublic and "Yes" or "No"), aiGM.MessageType.INFO)
    if announcement and announcement ~= "" then
        aiGM.sendMessage(gm, string.format("Announcement: %s", announcement), aiGM.MessageType.INFO)
    end
    aiGM.sendMessage(gm, "Use !aigm battle spawn to spawn test mobs", aiGM.MessageType.INFO)
    
    printf("[AI-GM] Battle test session %s created for GM %s in zone %d (%s)", sessionId, gm:getName(), zoneId, zoneName)
    
    return sessionId
end

-- Send server-wide battle test announcement
function aiGM.sendBattleTestAnnouncement(gm, zoneName, configType, position, customMessage)
    if not gm or not aiGM.announceActions then
        return
    end
    
    -- Determine safety level based on config type
    local safetyWarnings = {
        quick_test = "⚠️  Low-level players welcome to observe",
        standard_test = "⚠️  Mid-level players (25+) recommended",
        advanced_test = "⚠️  High-level players only (50+) - Combat may be dangerous",
        endgame_test = "⚠️  EXTREME DANGER - Endgame content testing - Keep safe distance!"
    }
    
    local safetyMsg = safetyWarnings[configType] or "⚠️  Use caution when observing"
    local locStr = string.format("(%.1f, %.1f, %.1f)", position.x, position.y, position.z)
    
    -- Build announcement message
    local announcement = {
        "🛡️ GM BATTLE DEMONSTRATION STARTING 🛡️",
        string.format("GM: %s", gm:getName()),
        string.format("Location: %s %s", zoneName, locStr),
        string.format("Test Type: %s", configType:gsub("_", " "):gsub("(%a)([%w_']*)", function(first, rest) return first:upper() .. rest end)),
        safetyMsg
    }
    
    -- Add custom message if provided
    if customMessage and customMessage ~= "" then
        table.insert(announcement, string.format("Comment: %s", customMessage))
    end
    
    table.insert(announcement, "Players may observe from a safe distance")
    
    -- Send announcement to all players in the zone
    local zone = gm:getZone()
    if zone then
        for _, player in pairs(zone:getPlayers()) do
            if player then
                for _, line in ipairs(announcement) do
                    player:printToPlayer(line, 0x0E)  -- Yellow text
                end
            end
        end
    end
    
    -- Log the announcement
    printf("[AI-GM] Battle test announcement sent by %s in %s", gm:getName(), zoneName)
end

-- Update session announcement
function aiGM.updateSessionAnnouncement(sessionIdPrefix, newAnnouncement)
    if not sessionIdPrefix or not newAnnouncement then
        return false
    end
    
    -- This would interface with the Python battle test system
    -- For now, just log the update
    printf("[AI-GM] Session announcement updated: %s", newAnnouncement)
    return true
end

-- Spawn a mob for battle testing
function aiGM.spawnBattleTestMob(gm, sessionId, mobRequest)
    if not gm or not sessionId then
        return false
    end
    
    local pos = gm:getPos()
    local zoneId = gm:getZoneID()
    local zoneName = gm:getZone():getName()
    
    -- Calculate spawn position near GM
    local spawnX = pos.x + math.random(-30, 30)
    local spawnZ = pos.z + math.random(-30, 30)
    local spawnY = pos.y
    
    -- Example mob spawning (this would need integration with actual mob spawn system)
    local mobId = mobRequest and mobRequest.mobId or 17461280  -- Default Goblin Thug
    
    -- Get mob information for announcement
    local mobInfo = aiGM.getMobInfo(mobId)
    local mobName = mobInfo.name or "Test Mob"
    local mobLevel = mobInfo.level or 15
    
    -- Send mob spawn announcement to zone
    if aiGM.announceActions then
        aiGM.sendMobSpawnAnnouncement(gm, mobName, mobLevel, zoneName, pos, mobInfo.family)
    end
    
    aiGM.sendMessage(gm, string.format("Spawning %s (Level %d) at position (%.1f, %.1f, %.1f)", mobName, mobLevel, spawnX, spawnY, spawnZ), aiGM.MessageType.BATTLE_TEST)
    
    -- Log the spawn for analytics
    printf("[AI-GM] Battle test mob %d (%s) spawned for session %s", mobId, mobName, sessionId)
    
    return {
        mobId = mobId,
        mobName = mobName,
        level = mobLevel,
        position = { x = spawnX, y = spawnY, z = spawnZ },
        sessionId = sessionId
    }
end

-- Send mob spawn announcement to players in zone
function aiGM.sendMobSpawnAnnouncement(gm, mobName, mobLevel, zoneName, position, mobFamily)
    if not gm or not aiGM.announceActions then
        return
    end
    
    local locStr = string.format("(%.1f, %.1f, %.1f)", position.x, position.y, position.z)
    
    -- Build mob spawn announcement
    local announcement = {
        string.format("🗡️ GM %s spawning test mob:", gm:getName()),
        string.format("Mob: %s (Level %d)", mobName, mobLevel),
        string.format("Location: %s %s", zoneName, locStr)
    }
    
    if mobFamily then
        table.insert(announcement, string.format("Family: %s", mobFamily))
    end
    
    -- Add safety warnings based on mob level
    if mobLevel >= 60 then
        table.insert(announcement, "⚠️ HIGH LEVEL MOB - Keep safe distance!")
    elseif mobLevel >= 40 then
        table.insert(announcement, "⚠️ Moderate level mob - Lower level players stay back")
    end
    
    -- Send to all players in zone
    local zone = gm:getZone()
    if zone then
        for _, player in pairs(zone:getPlayers()) do
            if player then
                for _, line in ipairs(announcement) do
                    player:printToPlayer(line, 0x0C)  -- Orange text for mob spawns
                end
            end
        end
    end
    
    printf("[AI-GM] Mob spawn announcement sent for %s in %s", mobName, zoneName)
end

-- Get mob information for announcements
function aiGM.getMobInfo(mobId)
    -- This would query the actual mob database
    -- For now, return example data based on common mob IDs
    local mobDatabase = {
        [17461280] = { name = "Goblin Thug", level = 15, family = "Goblin" },
        [17534976] = { name = "Orc Fighter", level = 25, family = "Orc" },
        [17289216] = { name = "Greater Pugil", level = 45, family = "Pugil" },
        [17355776] = { name = "Ancient Dragon", level = 75, family = "Dragon" }
    }
    
    return mobDatabase[mobId] or { name = "Unknown Mob", level = 1, family = "Unknown" }
end

-- Handle player assistance request
function aiGM.requestPlayerAssist(player, issueType, description, urgency)
    if not player then
        return nil
    end
    
    urgency = urgency or "normal"
    local pos = player:getPos()
    local zoneId = player:getZoneID()
    
    local requestId = string.format("assist_%d_%d", player:getID(), os.time())
    
    -- Notify player
    aiGM.sendMessage(player, "Your assistance request has been received. A GM will respond shortly.", aiGM.MessageType.INFO)
    
    -- Notify GMs based on urgency
    local minGMLevel = 1
    if urgency == "high" then
        minGMLevel = 2
    elseif urgency == "emergency" then
        minGMLevel = 3
    end
    
    local assistMessage = string.format("Player Assistance Request [%s]: %s in zone %d - %s", 
                                      urgency:upper(), player:getName(), zoneId, description)
    aiGM.notifyGMs(assistMessage, minGMLevel)
    
    -- For combat-related issues, prepare for potential battle demo
    if issueType == "stuck_in_combat" or issueType == "mob_assistance" or issueType == "combat_help" then
        aiGM.sendMessage(player, "A GM may spawn a demonstration mob to show combat mechanics.", aiGM.MessageType.INFO)
    end
    
    printf("[AI-GM] Assistance request %s created for player %s: %s", requestId, player:getName(), description)
    
    return requestId
end

-- Respond to assistance request with battle demo
function aiGM.respondWithBattleDemo(gm, requestId, playerName, issueType)
    if not gm or not requestId then
        return false
    end
    
    local player = aiGM.getPlayer(playerName)
    if not player then
        aiGM.sendMessage(gm, string.format("Player %s not found for assistance", playerName), aiGM.MessageType.ERROR)
        return false
    end
    
    -- Create a demonstration battle session
    local sessionId = aiGM.createBattleSession(gm, player:getZone():getName(), "quick_test")
    
    if sessionId then
        -- Teleport GM to player's location
        local playerPos = player:getPos()
        gm:setPos(playerPos.x + 10, playerPos.y, playerPos.z + 10, playerPos.rot)
        
        -- Notify both GM and player
        aiGM.sendMessage(gm, string.format("Responding to assist request %s with battle demonstration", requestId), aiGM.MessageType.BATTLE_TEST)
        aiGM.sendMessage(player, string.format("GM %s is responding to your request with a combat demonstration", gm:getName()), aiGM.MessageType.INFO)
        
        -- Spawn appropriate demonstration mob
        local mobRequest = {
            level = player:getMainLvl(),
            appropriate_for_demo = true
        }
        
        aiGM.spawnBattleTestMob(gm, sessionId, mobRequest)
        
        return true
    end
    
    return false
end

-----------------------------------
-- ML Integration Functions
-----------------------------------

-- Analyze player behavior using ML
function aiGM.analyzePlayerWithML(player)
    if not player or not aiGM.mlEnabled then
        return nil
    end
    
    -- Gather player data for ML analysis
    local pos = player:getPos()
    local playerData = {
        playerId = player:getID(),
        playerName = player:getName(),
        zoneId = player:getZoneID(),
        position = { x = pos.x, y = pos.y, z = pos.z },
        hpPercentage = player:getHP() / player:getMaxHP(),
        mpPercentage = player:getMP() / player:getMaxMP(),
        mainJob = player:getMainJob(),
        mainLevel = player:getMainLvl(),
        deathCount = player:getCharVar("deathCount") or 0,
        jailHistory = player:getCharVar("jailHistory") or 0
    }
    
    -- This would interface with the Python ML engine
    -- For now, return mock analysis results
    local analysis = {
        riskScore = math.random() * 0.3,  -- Low risk for demo
        behaviorClass = "normal",
        isAnomaly = false,
        confidence = 0.85
    }
    
    -- Log ML analysis
    if analysis.riskScore > 0.7 then
        printf("[AI-GM ML] High risk behavior detected for player %s (score: %.3f)", 
               player:getName(), analysis.riskScore)
    end
    
    return analysis
end

-- Learn from GM interaction
function aiGM.learnFromGMInteraction(player, gmAction, outcome)
    if not player or not aiGM.mlEnabled then
        return
    end
    
    local interactionData = {
        playerId = player:getID(),
        playerName = player:getName(),
        gmAction = gmAction,
        outcome = outcome,
        timestamp = os.time()
    }
    
    -- This would send data to the ML engine for learning
    printf("[AI-GM ML] Learning from GM interaction: %s -> %s for player %s", 
           gmAction, outcome, player:getName())
end

-- Get ML system status
function aiGM.getMLStatus()
    if not aiGM.mlEnabled then
        return {
            enabled = false,
            reason = "ML system disabled"
        }
    end
    
    -- This would query the actual ML engine status
    return {
        enabled = true,
        modelsLoaded = 3,
        hardwareAcceleration = "CUDA",
        lastTraining = "2024-01-01 12:00:00",
        predictionsToday = 1247
    }
end

-- Check if a player's behavior is suspicious
function aiGM.analyzePlayerBehavior(player)
    if not player then
        return nil
    end
    
    local issues = {}
    
    -- Check if player is in jail
    if player:getCharVar("inJail") > 0 then
        table.insert(issues, {
            type = "currently_jailed",
            severity = aiGM.Severity.INFO,
            description = "Player is currently in jail"
        })
    end
    
    -- Check for suspicious position (stuck at 0,0,0)
    local pos = player:getPos()
    if pos.x == 0 and pos.y == 0 and pos.z == 0 then
        table.insert(issues, {
            type = "invalid_position",
            severity = aiGM.Severity.WARNING,
            description = "Player appears to be stuck at invalid coordinates"
        })
    end
    
    -- Check for very low HP (might be stuck/dead)
    if player:getHP() == 0 and player:getCharVar("DeathTime") > 0 then
        local deathTime = player:getCharVar("DeathTime")
        local currentTime = os.time()
        if (currentTime - deathTime) > 1800 then -- Dead for more than 30 minutes
            table.insert(issues, {
                type = "long_death_time",
                severity = aiGM.Severity.WARNING,
                description = "Player has been dead for an extended period"
            })
        end
    end
    
    return issues
end

-- Perform automated checks on all online players
function aiGM.performAutomatedChecks()
    local playersChecked = 0
    local issuesFound = 0
    
    local players = GetPlayersInZone(0) -- Get all players
    
    for _, player in pairs(players) do
        if player then
            playersChecked = playersChecked + 1
            local issues = aiGM.analyzePlayerBehavior(player)
            
            if issues and #issues > 0 then
                for _, issue in ipairs(issues) do
                    issuesFound = issuesFound + 1
                    
                    -- Handle the issue based on severity
                    if issue.severity == aiGM.Severity.WARNING then
                        if issue.type == "invalid_position" then
                            -- Try to help the stuck player
                            player:warp()
                            aiGM.sendMessage(player, "You appeared to be stuck and have been moved to a safe location.", aiGM.MessageType.INFO)
                        elseif issue.type == "long_death_time" then
                            -- Raise the dead player
                            player:sendRaise(3)
                            aiGM.sendMessage(player, "You have been raised by the AI-GM.", aiGM.MessageType.INFO)
                        end
                    end
                    
                    -- Log the issue
                    printf("[AI-GM] Issue detected for %s: %s (%s)", player:getName(), issue.description, issue.severity)
                end
            end
        end
    end
    
    printf("[AI-GM] Automated check complete: %d players checked, %d issues found", playersChecked, issuesFound)
    return { playersChecked = playersChecked, issuesFound = issuesFound }
end

-----------------------------------
-- Utility Functions
-----------------------------------

-- Get player by name safely
function aiGM.getPlayer(playerName)
    if not playerName or playerName == "" then
        return nil
    end
    
    return GetPlayerByName(playerName)
end

-- Check if AI-GM actions are enabled
function aiGM.isEnabled()
    -- This could check a server configuration variable
    return GetServerVariable("AIGM_ENABLED") == 1
end

-- Log an AI-GM action to the audit system
function aiGM.logAction(action, target, details)
    local logEntry = string.format("[AI-GM] %s on %s: %s", action, target or "N/A", details or "")
    printf(logEntry)
    
    -- This could also write to the audit_gm table if needed
end

return aiGM