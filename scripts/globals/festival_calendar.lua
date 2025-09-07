-----------------------------------
-- Festival Calendar System
-- Centralized Japanese time-based festival management
-----------------------------------
require('scripts/globals/utils')
-----------------------------------
xi = xi or {}
xi.festival = xi.festival or {}
xi.festival.calendar = xi.festival.calendar or {}

-- Festival Calendar Database
-- All dates are based on Japanese Standard Time (JST)
xi.festival.calendar.festivals = {
    -- New Year's Celebration
    {
        id = "new_year",
        name = "New Year's Celebration",
        description = "Welcome the new year with special events and rewards!",
        startMonth = 1,
        startDay = 1,
        endMonth = 1,
        endDay = 15,
        icon = "🎆",
        color = "#FFD700",
        announcements = {
            start = "🎆 New Year's Celebration has begun! Welcome to a new year in Vana'diel!",
            end = "🎆 New Year's Celebration has ended. Thank you for celebrating with us!"
        },
        zones = { xi.zone.UPPER_JEUNO, xi.zone.LOWER_JEUNO, xi.zone.PORT_JEUNO },
        rewards = { "Festive items and special rewards await!" }
    },
    
    -- Valentine's Day
    {
        id = "valentines",
        name = "Valentine's Day", 
        description = "Share the love with special valentine items and events!",
        startMonth = 2,
        startDay = 10,
        endMonth = 2,
        endDay = 20,
        icon = "💝",
        color = "#FF69B4",
        announcements = {
            start = "💝 Valentine's Day event has started! Spread love throughout Vana'diel!",
            end = "💝 Valentine's Day event has ended. Until next year, adventurers!"
        },
        zones = { xi.zone.PORT_SAN_DORIA, xi.zone.PORT_BASTOK, xi.zone.WINDURST_WALLS },
        rewards = { "Valentine chocolates", "Love letters", "Special accessories" }
    },
    
    -- White Day
    {
        id = "white_day",
        name = "White Day",
        description = "Return the favor with white gifts and special events!",
        startMonth = 3,
        startDay = 10,
        endMonth = 3,
        endDay = 20,
        icon = "🤍",
        color = "#FFFFFF",
        announcements = {
            start = "🤍 White Day has arrived! Time to return the kindness!",
            end = "🤍 White Day has concluded. See you next year!"
        },
        zones = { xi.zone.PORT_SAN_DORIA, xi.zone.PORT_BASTOK, xi.zone.WINDURST_WALLS },
        rewards = { "White chocolates", "Return gifts", "Friendship tokens" }
    },
    
    -- Golden Week
    {
        id = "golden_week",
        name = "Golden Week",
        description = "Celebrate Japan's Golden Week with special events!",
        startMonth = 4,
        startDay = 29,
        endMonth = 5,
        endDay = 5,
        icon = "🏅",
        color = "#FFD700",
        announcements = {
            start = "🏅 Golden Week celebration begins! Enjoy the festivities!",
            end = "🏅 Golden Week has ended. Thank you for participating!"
        },
        zones = { xi.zone.UPPER_JEUNO, xi.zone.LOWER_JEUNO, xi.zone.PORT_JEUNO },
        rewards = { "Golden rewards", "Experience bonuses", "Special titles" }
    },
    
    -- Summer Festival
    {
        id = "summer_festival",
        name = "Summer Festival",
        description = "Beat the heat with cool summer events and fireworks!",
        startMonth = 7,
        startDay = 15,
        endMonth = 8,
        endDay = 31,
        icon = "🎆",
        color = "#87CEEB",
        announcements = {
            start = "🎆 Summer Festival is here! Enjoy fireworks and summer fun!",
            end = "🎆 Summer Festival has ended. Autumn approaches in Vana'diel!"
        },
        zones = { xi.zone.UPPER_JEUNO, xi.zone.LOWER_JEUNO, xi.zone.PORT_JEUNO },
        rewards = { "Fireworks", "Summer clothing", "Yukata", "Festival foods" }
    },
    
    -- Harvest Festival (Halloween)
    {
        id = "harvest_festival",
        name = "Harvest Festival",
        description = "Spooky fun awaits in this haunting celebration!",
        startMonth = 10,
        startDay = 20,
        endMonth = 11,
        endDay = 1,
        icon = "🎃",
        color = "#FF8C00",
        announcements = {
            start = "🎃 The Harvest Festival begins! Beware of things that go bump in the night!",
            end = "🎃 The Harvest Festival has ended. The spirits return to rest!"
        },
        zones = { xi.zone.PORT_SAN_DORIA, xi.zone.PORT_BASTOK, xi.zone.WINDURST_WALLS },
        rewards = { "Pumpkin Head", "Horror Head", "Trick Staff", "Treat Staff", "Halloween sweets" }
    },
    
    -- Starlight Celebration (Christmas)
    {
        id = "starlight_celebration",
        name = "Starlight Celebration",
        description = "Celebrate the season of giving with festive cheer!",
        startMonth = 12,
        startDay = 15,
        endMonth = 12,
        endDay = 31,
        icon = "⭐",
        color = "#00FF00",
        announcements = {
            start = "⭐ The Starlight Celebration has begun! May your holidays be bright!",
            end = "⭐ The Starlight Celebration has ended. Happy New Year approaches!"
        },
        zones = { xi.zone.UPPER_JEUNO, xi.zone.LOWER_JEUNO, xi.zone.PORT_JEUNO },
        rewards = { "Starlight decorations", "Holiday treats", "Festive clothing", "Gift boxes" }
    }
}

-- Get current active festivals
xi.festival.calendar.getActiveFestivals = function()
    local activeFestivals = {}
    local currentMonth = JstMonth()
    local currentDay = JstDayOfTheMonth()
    
    for _, festival in pairs(xi.festival.calendar.festivals) do
        if xi.festival.calendar.isFestivalActive(festival, currentMonth, currentDay) then
            table.insert(activeFestivals, festival)
        end
    end
    
    return activeFestivals
end

-- Check if a specific festival is active
xi.festival.calendar.isFestivalActive = function(festival, month, day)
    month = month or JstMonth()
    day = day or JstDayOfTheMonth()
    
    -- Handle festivals that span across months
    if festival.startMonth == festival.endMonth then
        -- Same month
        return month == festival.startMonth and day >= festival.startDay and day <= festival.endDay
    elseif festival.startMonth < festival.endMonth then
        -- Spans consecutive months in same year
        return (month == festival.startMonth and day >= festival.startDay) or
               (month == festival.endMonth and day <= festival.endDay) or
               (month > festival.startMonth and month < festival.endMonth)
    else
        -- Spans year boundary (e.g., December to January)
        return (month == festival.startMonth and day >= festival.startDay) or
               (month == festival.endMonth and day <= festival.endDay) or
               (month > festival.startMonth) or
               (month < festival.endMonth)
    end
end

-- Get upcoming festivals (next 30 days)
xi.festival.calendar.getUpcomingFestivals = function()
    local upcomingFestivals = {}
    local currentMonth = JstMonth()
    local currentDay = JstDayOfTheMonth()
    
    for _, festival in pairs(xi.festival.calendar.festivals) do
        local daysUntilStart = xi.festival.calendar.getDaysUntilFestival(festival, currentMonth, currentDay)
        if daysUntilStart >= 0 and daysUntilStart <= 30 then
            festival.daysUntilStart = daysUntilStart
            table.insert(upcomingFestivals, festival)
        end
    end
    
    -- Sort by days until start
    table.sort(upcomingFestivals, function(a, b) return a.daysUntilStart < b.daysUntilStart end)
    return upcomingFestivals
end

-- Calculate days until festival starts
xi.festival.calendar.getDaysUntilFestival = function(festival, currentMonth, currentDay)
    currentMonth = currentMonth or JstMonth()
    currentDay = currentDay or JstDayOfTheMonth()
    
    -- Simple calculation for same year festivals
    local daysInMonth = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 }
    
    if festival.startMonth == currentMonth then
        if festival.startDay >= currentDay then
            return festival.startDay - currentDay
        else
            -- Festival already passed this year, check next year
            return 365 - xi.festival.calendar.dayOfYear(currentMonth, currentDay) + xi.festival.calendar.dayOfYear(festival.startMonth, festival.startDay)
        end
    elseif festival.startMonth > currentMonth then
        -- Festival later this year
        local days = 0
        for month = currentMonth, festival.startMonth - 1 do
            if month == currentMonth then
                days = days + (daysInMonth[month] - currentDay)
            else
                days = days + daysInMonth[month]
            end
        end
        return days + festival.startDay
    else
        -- Festival next year
        local days = 0
        for month = currentMonth, 12 do
            if month == currentMonth then
                days = days + (daysInMonth[month] - currentDay)
            else
                days = days + daysInMonth[month]
            end
        end
        for month = 1, festival.startMonth - 1 do
            days = days + daysInMonth[month]
        end
        return days + festival.startDay
    end
end

-- Calculate day of year
xi.festival.calendar.dayOfYear = function(month, day)
    local daysInMonth = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 }
    local dayOfYear = day
    
    for i = 1, month - 1 do
        dayOfYear = dayOfYear + daysInMonth[i]
    end
    
    return dayOfYear
end

-- Get festival by ID
xi.festival.calendar.getFestivalById = function(festivalId)
    for _, festival in pairs(xi.festival.calendar.festivals) do
        if festival.id == festivalId then
            return festival
        end
    end
    return nil
end

-- Generate web calendar data
xi.festival.calendar.generateWebCalendarData = function()
    local calendarData = {
        currentMonth = JstMonth(),
        currentDay = JstDayOfTheMonth(),
        activeFestivals = xi.festival.calendar.getActiveFestivals(),
        upcomingFestivals = xi.festival.calendar.getUpcomingFestivals(),
        allFestivals = xi.festival.calendar.festivals
    }
    
    return calendarData
end

-- Send festival announcements
xi.festival.calendar.sendFestivalAnnouncement = function(festivalId, announcementType)
    local festival = xi.festival.calendar.getFestivalById(festivalId)
    if not festival or not festival.announcements or not festival.announcements[announcementType] then
        return false
    end
    
    local message = festival.announcements[announcementType]
    
    -- Send to all online players
    local players = GetPlayersInZone(0) -- 0 = all zones
    for _, player in pairs(players) do
        if player then
            player:printToPlayer(message, xi.msg.channel.SYSTEM_3)
        end
    end
    
    return true
end

-- Check for festival state changes (to be called periodically)
xi.festival.calendar.checkFestivalStateChanges = function()
    local currentMonth = JstMonth()
    local currentDay = JstDayOfTheMonth()
    local stateChanges = {}
    
    for _, festival in pairs(xi.festival.calendar.festivals) do
        local isCurrentlyActive = xi.festival.calendar.isFestivalActive(festival, currentMonth, currentDay)
        
        -- Check if festival just started
        if isCurrentlyActive and currentDay == festival.startDay and currentMonth == festival.startMonth then
            table.insert(stateChanges, { type = "start", festival = festival })
            xi.festival.calendar.sendFestivalAnnouncement(festival.id, "start")
        end
        
        -- Check if festival just ended
        if not isCurrentlyActive and currentDay == festival.endDay + 1 and currentMonth == festival.endMonth then
            table.insert(stateChanges, { type = "end", festival = festival })
            xi.festival.calendar.sendFestivalAnnouncement(festival.id, "end")
        end
    end
    
    return stateChanges
end

return xi.festival.calendar