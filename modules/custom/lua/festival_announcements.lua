-----------------------------------
-- Festival Announcement Module
-- Integrates festival calendar with server announcements
-----------------------------------
require('scripts/globals/festival_calendar')
require('modules/module_utils')
-----------------------------------
local m = Module:new('festival_announcements')

-- Festival announcement state tracking
local festivalState = {}
local lastCheckTime = 0
local CHECK_INTERVAL = 300 -- 5 minutes

-- Override player login to show festival announcements
m:addOverride('xi.player.onGameIn', function(player, firstLogin, zoning)
    super(player, firstLogin, zoning)

    if not zoning then
        -- Check for active festivals and announce to logging in player
        local activeFestivals = xi.festival.calendar.getActiveFestivals()
        
        if #activeFestivals > 0 then
            -- Delay the announcement slightly to ensure player is fully loaded
            player:timer(3000, function(playerArg)
                for _, festival in pairs(activeFestivals) do
                    local message = string.format('%s %s is currently active! %s', 
                        festival.icon, festival.name, festival.description)
                    playerArg:printToPlayer(message, xi.msg.channel.SYSTEM_3)
                end
            end)
        end
    end
end)

-- Function to check for festival state changes
local function checkFestivalChanges()
    local currentTime = GetServerTime()
    
    -- Only check every CHECK_INTERVAL seconds
    if currentTime - lastCheckTime < CHECK_INTERVAL then
        return
    end
    
    lastCheckTime = currentTime
    
    -- Get current active festivals
    local activeFestivals = xi.festival.calendar.getActiveFestivals()
    local currentActive = {}
    
    for _, festival in pairs(activeFestivals) do
        currentActive[festival.id] = festival
    end
    
    -- Check for newly started festivals
    for festivalId, festival in pairs(currentActive) do
        if not festivalState[festivalId] then
            -- Festival just started
            festivalState[festivalId] = true
            
            -- Send server-wide announcement
            if festival.announcements and festival.announcements.start then
                -- Send to all zones
                for _, zoneId in pairs(festival.zones or {}) do
                    local zone = GetZone(zoneId)
                    if zone then
                        zone:messageBasic(xi.msg.basic.SERVER_MESSAGE, 0, 0, festival.announcements.start)
                    end
                end
                
                -- Also send to all online players globally
                SendServerMessage(festival.announcements.start)
            end
            
            printf('Festival started: %s', festival.name)
        end
    end
    
    -- Check for ended festivals
    for festivalId, wasActive in pairs(festivalState) do
        if wasActive and not currentActive[festivalId] then
            -- Festival just ended
            festivalState[festivalId] = false
            
            -- Get festival info for end message
            local festival = xi.festival.calendar.getFestivalById(festivalId)
            if festival and festival.announcements and festival.announcements.end then
                -- Send to all zones
                for _, zoneId in pairs(festival.zones or {}) do
                    local zone = GetZone(zoneId)
                    if zone then
                        zone:messageBasic(xi.msg.basic.SERVER_MESSAGE, 0, 0, festival.announcements.end)
                    end
                end
                
                -- Also send to all online players globally
                SendServerMessage(festival.announcements.end)
            end
            
            printf('Festival ended: %s', festival.name or festivalId)
        end
    end
end

-- Function to send server message to all players
function SendServerMessage(message)
    local players = GetPlayersInAllZones()
    for _, player in pairs(players) do
        if player then
            player:printToPlayer(message, xi.msg.channel.SYSTEM_3)
        end
    end
end

-- Function to get all players across zones
function GetPlayersInAllZones()
    local allPlayers = {}
    local zoneList = {
        xi.zone.SOUTHERN_SAN_DORIA, xi.zone.NORTHERN_SAN_DORIA, xi.zone.PORT_SAN_DORIA,
        xi.zone.BASTOK_MINES, xi.zone.BASTOK_MARKETS, xi.zone.PORT_BASTOK,
        xi.zone.WINDURST_WATERS, xi.zone.WINDURST_WALLS, xi.zone.WINDURST_WOODS,
        xi.zone.UPPER_JEUNO, xi.zone.LOWER_JEUNO, xi.zone.PORT_JEUNO,
        xi.zone.RULUDE_GARDENS, xi.zone.KAZHAM, xi.zone.RABAO, xi.zone.NOG
    }
    
    for _, zoneId in pairs(zoneList) do
        local zone = GetZone(zoneId)
        if zone then
            local players = zone:getPlayers()
            for _, player in pairs(players) do
                table.insert(allPlayers, player)
            end
        end
    end
    
    return allPlayers
end

-- Hook into server tick to check for festival changes
m:addOverride('xi.server.onServerTick', function()
    super()
    checkFestivalChanges()
end)

-- GM command to manually trigger festival announcements
m:addOverride('xi.command.festival', function(player, args)
    if player:getGMLevel() < 1 then
        player:printToPlayer('You do not have permission to use this command.', xi.msg.channel.SYSTEM_3)
        return
    end
    
    local subcommand = args[1]
    
    if subcommand == 'check' then
        checkFestivalChanges()
        player:printToPlayer('Festival check triggered.', xi.msg.channel.SYSTEM_3)
        
    elseif subcommand == 'status' then
        local activeFestivals = xi.festival.calendar.getActiveFestivals()
        if #activeFestivals > 0 then
            player:printToPlayer('Active festivals:', xi.msg.channel.SYSTEM_3)
            for _, festival in pairs(activeFestivals) do
                player:printToPlayer(string.format('- %s %s', festival.icon, festival.name), xi.msg.channel.SYSTEM_3)
            end
        else
            player:printToPlayer('No festivals currently active.', xi.msg.channel.SYSTEM_3)
        end
        
    elseif subcommand == 'announce' then
        local festivalId = args[2]
        if not festivalId then
            player:printToPlayer('Usage: !festival announce <festival_id>', xi.msg.channel.SYSTEM_3)
            return
        end
        
        local festival = xi.festival.calendar.getFestivalById(festivalId)
        if not festival then
            player:printToPlayer('Festival not found: ' .. festivalId, xi.msg.channel.SYSTEM_3)
            return
        end
        
        local message = festival.announcements and festival.announcements.start or 
                       string.format('%s %s is active!', festival.icon, festival.name)
        
        SendServerMessage(message)
        player:printToPlayer('Festival announcement sent.', xi.msg.channel.SYSTEM_3)
        
    elseif subcommand == 'list' then
        local allFestivals = xi.festival.calendar.festivals
        player:printToPlayer('All festivals:', xi.msg.channel.SYSTEM_3)
        for _, festival in pairs(allFestivals) do
            local status = xi.festival.calendar.isFestivalActive(festival) and 'ACTIVE' or 'inactive'
            player:printToPlayer(string.format('- %s %s (%s)', festival.icon, festival.name, status), xi.msg.channel.SYSTEM_3)
        end
        
    else
        player:printToPlayer('Festival commands:', xi.msg.channel.SYSTEM_3)
        player:printToPlayer('  !festival check - Check for festival changes', xi.msg.channel.SYSTEM_3)
        player:printToPlayer('  !festival status - Show active festivals', xi.msg.channel.SYSTEM_3)
        player:printToPlayer('  !festival list - Show all festivals', xi.msg.channel.SYSTEM_3)
        player:printToPlayer('  !festival announce <id> - Announce festival', xi.msg.channel.SYSTEM_3)
    end
end)

-- Export functions for external use
xi.festival = xi.festival or {}
xi.festival.announcements = {
    checkChanges = checkFestivalChanges,
    sendServerMessage = SendServerMessage,
    getActiveFestivals = function()
        return xi.festival.calendar.getActiveFestivals()
    end
}

return m