-----------------------------------
-- func: aigm
-- desc: AI-GM management command for administrators
-----------------------------------
require("scripts/globals/ai_gm")
---@type TCommand
local commandObj = {}

commandObj.cmdprops =
{
    permission = 3, -- Requires GM level 3 or higher
    parameters = 'sss'
}

commandObj.onTrigger = function(player, action, target, param)
    if not action then
        player:printToPlayer("AI-GM Management Commands:")
        player:printToPlayer("!aigm status - Show AI-GM system status")
        player:printToPlayer("!aigm check [player] - Run behavior check on player or all players")
        player:printToPlayer("!aigm jail <player> [reason] - Jail a player with AI-GM")
        player:printToPlayer("!aigm pardon <player> - Pardon a player from AI-GM jail")
        player:printToPlayer("!aigm warn <player> [reason] - Send warning to player")
        player:printToPlayer("!aigm escalate <player> [level] - Escalate player issue to GM level")
        player:printToPlayer("!aigm announce <message> - Announce message as AI-GM")
        return
    end
    
    action = string.lower(action)
    
    if action == "status" then
        -- Show AI-GM system status
        player:printToPlayer("=== AI-GM System Status ===")
        player:printToPlayer(string.format("AI-GM Name: %s", aiGM.name))
        player:printToPlayer(string.format("AI-GM Level: %d", aiGM.level))
        player:printToPlayer(string.format("Announcements: %s", aiGM.announceActions and "Enabled" or "Disabled"))
        player:printToPlayer(string.format("System: %s", aiGM.isEnabled() and "Active" or "Inactive"))
        
        -- Show recent activity (this would need to be tracked)
        player:printToPlayer("Recent AI-GM actions logged in console")
        
    elseif action == "check" then
        if target then
            -- Check specific player
            local targetPlayer = aiGM.getPlayer(target)
            if not targetPlayer then
                player:printToPlayer(string.format("Player '%s' not found.", target))
                return
            end
            
            player:printToPlayer(string.format("Running AI-GM behavior check on %s...", target))
            local issues = aiGM.analyzePlayerBehavior(targetPlayer)
            
            if issues and #issues > 0 then
                player:printToPlayer(string.format("Found %d issues:", #issues))
                for i, issue in ipairs(issues) do
                    player:printToPlayer(string.format("  %d. %s (%s): %s", i, issue.type, issue.severity, issue.description))
                end
            else
                player:printToPlayer("No issues detected.")
            end
        else
            -- Check all players
            player:printToPlayer("Running AI-GM automated checks on all players...")
            local results = aiGM.performAutomatedChecks()
            player:printToPlayer(string.format("Check complete: %d players checked, %d issues found", 
                                             results.playersChecked, results.issuesFound))
        end
        
    elseif action == "jail" then
        if not target then
            player:printToPlayer("Usage: !aigm jail <player> [reason]")
            return
        end
        
        local targetPlayer = aiGM.getPlayer(target)
        if not targetPlayer then
            player:printToPlayer(string.format("Player '%s' not found.", target))
            return
        end
        
        local reason = param or "Manual AI-GM jail command"
        
        if aiGM.jailPlayer(targetPlayer, 1, reason, 30) then
            player:printToPlayer(string.format("Player %s has been jailed by AI-GM. Reason: %s", target, reason))
            aiGM.logAction("MANUAL_JAIL", target, reason)
        else
            player:printToPlayer("Failed to jail player.")
        end
        
    elseif action == "pardon" then
        if not target then
            player:printToPlayer("Usage: !aigm pardon <player>")
            return
        end
        
        local targetPlayer = aiGM.getPlayer(target)
        if not targetPlayer then
            player:printToPlayer(string.format("Player '%s' not found.", target))
            return
        end
        
        if aiGM.pardonPlayer(targetPlayer) then
            player:printToPlayer(string.format("Player %s has been pardoned by AI-GM.", target))
            aiGM.logAction("MANUAL_PARDON", target, "Manual pardon command")
        else
            player:printToPlayer("Failed to pardon player (may not be jailed).")
        end
        
    elseif action == "warn" then
        if not target then
            player:printToPlayer("Usage: !aigm warn <player> [reason]")
            return
        end
        
        local targetPlayer = aiGM.getPlayer(target)
        if not targetPlayer then
            player:printToPlayer(string.format("Player '%s' not found.", target))
            return
        end
        
        local reason = param or "Manual warning from AI-GM"
        
        if aiGM.sendWarning(targetPlayer, reason) then
            player:printToPlayer(string.format("Warning sent to %s: %s", target, reason))
            aiGM.logAction("MANUAL_WARN", target, reason)
        else
            player:printToPlayer("Failed to send warning.")
        end
        
    elseif action == "escalate" then
        if not target then
            player:printToPlayer("Usage: !aigm escalate <player> [level]")
            return
        end
        
        local gmLevel = tonumber(param) or 2
        if gmLevel < 1 or gmLevel > 5 then
            player:printToPlayer("GM level must be between 1 and 5.")
            return
        end
        
        local description = string.format("Manual escalation requested by %s", player:getName())
        
        if aiGM.escalateToGM(target, "manual_escalation", description, aiGM.Severity.MODERATE, gmLevel) then
            player:printToPlayer(string.format("Escalated %s to GM level %d.", target, gmLevel))
            aiGM.logAction("MANUAL_ESCALATE", target, string.format("Level %d escalation", gmLevel))
        else
            player:printToPlayer("Failed to escalate (no GMs online at that level).")
        end
        
    elseif action == "announce" then
        if not target then
            player:printToPlayer("Usage: !aigm announce <message>")
            return
        end
        
        local message = target
        if param then
            message = target .. " " .. param
        end
        
        -- Broadcast message as AI-GM
        local players = GetPlayersInZone(0)
        local announcedTo = 0
        
        for _, targetPlayer in pairs(players) do
            if targetPlayer then
                aiGM.sendMessage(targetPlayer, message, aiGM.MessageType.INFO)
                announcedTo = announcedTo + 1
            end
        end
        
        player:printToPlayer(string.format("AI-GM announcement sent to %d players: %s", announcedTo, message))
        aiGM.logAction("MANUAL_ANNOUNCE", string.format("%d players", announcedTo), message)
        
    elseif action == "enable" then
        -- Enable AI-GM system (this would need server variable support)
        SetServerVariable("AIGM_ENABLED", 1)
        player:printToPlayer("AI-GM system enabled.")
        aiGM.logAction("SYSTEM_ENABLE", player:getName(), "AI-GM system enabled")
        
    elseif action == "disable" then
        -- Disable AI-GM system
        SetServerVariable("AIGM_ENABLED", 0)
        player:printToPlayer("AI-GM system disabled.")
        aiGM.logAction("SYSTEM_DISABLE", player:getName(), "AI-GM system disabled")
        
    elseif action == "config" then
        if not target then
            player:printToPlayer("AI-GM Configuration:")
            player:printToPlayer(string.format("  Name: %s", aiGM.name))
            player:printToPlayer(string.format("  Level: %d", aiGM.level))
            player:printToPlayer(string.format("  Announce Actions: %s", aiGM.announceActions and "Yes" or "No"))
            player:printToPlayer("Use: !aigm config <setting> <value>")
            player:printToPlayer("Settings: name, level, announce")
            return
        end
        
        local setting = string.lower(target)
        
        if setting == "name" then
            if param then
                aiGM.name = param
                player:printToPlayer(string.format("AI-GM name changed to: %s", param))
                aiGM.logAction("CONFIG_CHANGE", "name", param)
            else
                player:printToPlayer("Usage: !aigm config name <new_name>")
            end
            
        elseif setting == "level" then
            if param then
                local newLevel = tonumber(param)
                if newLevel and newLevel >= 1 and newLevel <= 5 then
                    aiGM.level = newLevel
                    player:printToPlayer(string.format("AI-GM level changed to: %d", newLevel))
                    aiGM.logAction("CONFIG_CHANGE", "level", tostring(newLevel))
                else
                    player:printToPlayer("Level must be between 1 and 5.")
                end
            else
                player:printToPlayer("Usage: !aigm config level <1-5>")
            end
            
        elseif setting == "announce" then
            if param then
                local value = string.lower(param)
                if value == "true" or value == "yes" or value == "1" or value == "on" then
                    aiGM.announceActions = true
                    player:printToPlayer("AI-GM action announcements enabled.")
                elseif value == "false" or value == "no" or value == "0" or value == "off" then
                    aiGM.announceActions = false
                    player:printToPlayer("AI-GM action announcements disabled.")
                else
                    player:printToPlayer("Value must be true/false, yes/no, 1/0, or on/off.")
                end
                aiGM.logAction("CONFIG_CHANGE", "announce", tostring(aiGM.announceActions))
            else
                player:printToPlayer("Usage: !aigm config announce <true/false>")
            end
            
        else
            player:printToPlayer("Unknown setting. Available: name, level, announce")
        end
        
    else
        player:printToPlayer(string.format("Unknown AI-GM action: %s", action))
        player:printToPlayer("Use !aigm without parameters to see available commands.")
    end
end

return commandObj