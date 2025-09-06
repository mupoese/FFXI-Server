-----------------------------------
-- func: promote
-- desc: Promotes the player to a new GM level.
-----------------------------------
---@type TCommand
local commandObj = {}

commandObj.cmdprops =
{
    permission = 1,
    parameters = 'si'
}

local function error(player, msg)
    player:printToPlayer(msg)
    player:printToPlayer('!promote <player> <level>')
end

commandObj.onTrigger = function(player, target, level)
    -- GM promotion is now restricted to admin dashboard only
    player:printToPlayer('GM promotion is now restricted to the web admin dashboard for security.')
    player:printToPlayer('Contact the server owner to request GM privileges through the admin panel.')
    
    -- Log the attempt for security audit
    printf('[SECURITY] %s attempted to use disabled promote command (target: %s, level: %s)', 
           player:getName(), target or 'nil', level or 'nil')
end

return commandObj
