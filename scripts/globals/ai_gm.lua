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

-- Message types for different situations
aiGM.MessageType = {
    INFO = 0,
    WARNING = 1,
    ERROR = 2,
    SYSTEM = 3
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
-- Player Behavior Analysis
-----------------------------------

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