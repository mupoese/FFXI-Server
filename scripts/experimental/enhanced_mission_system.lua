-----------------------------------
-- Enhanced Mission System
-- Phase 4: Advanced mission progression and validation
-----------------------------------
require('scripts/globals/missions')
require('scripts/globals/npc_util')
require('scripts/globals/content_validation')
-----------------------------------
xi = xi or {}
xi.missions = xi.missions or {}
xi.missions.enhanced = xi.missions.enhanced or {}

-- Mission progression states
xi.missions.enhanced.progressState =
{
    NOT_STARTED     = 0,
    IN_PROGRESS     = 1,
    READY_TO_COMPLETE = 2,
    COMPLETED       = 3,
    FAILED          = 4,
    BLOCKED         = 5,
}

-- Mission validation results
xi.missions.enhanced.validationResult =
{
    VALID           = 0,
    MISSING_PREREQ  = 1,
    LEVEL_TOO_LOW   = 2,
    WRONG_NATION    = 3,
    MISSING_KEYITEM = 4,
    INVALID_STATE   = 5,
}

-- Enhanced mission progression tracker
xi.missions.enhanced.validateProgression = function(player, logId, missionId)
    local currentMission = player:getCurrentMission(logId)
    local status = player:getMissionStatus(logId)
    
    -- Basic validation
    if currentMission ~= missionId then
        return xi.missions.enhanced.validationResult.INVALID_STATE, "Player is not on this mission"
    end
    
    -- Level requirements check
    local levelReq = xi.missions.enhanced.getLevelRequirement(logId, missionId)
    if levelReq and player:getMainLvl() < levelReq then
        return xi.missions.enhanced.validationResult.LEVEL_TOO_LOW, string.format("Requires level %d", levelReq)
    end
    
    -- Nation requirements for nation missions
    if logId <= xi.mission.log_id.WINDURST then
        local requiredNation = logId
        if player:getNation() ~= requiredNation then
            return xi.missions.enhanced.validationResult.WRONG_NATION, "Wrong starting nation"
        end
    end
    
    return xi.missions.enhanced.validationResult.VALID, "Mission progression valid"
end

-- Get level requirement for specific missions
xi.missions.enhanced.getLevelRequirement = function(logId, missionId)
    local requirements = {
        -- CoP missions
        [xi.mission.log_id.COP] = {
            [xi.mission.id.cop.THE_RITES_OF_LIFE] = 30,
            [xi.mission.id.cop.BELOW_THE_ARKS] = 40,
            [xi.mission.id.cop.THE_MOTHERCRYSTALS] = 50,
            [xi.mission.id.cop.AN_INVITATION_WEST] = 50,
            [xi.mission.id.cop.THE_CALL_OF_THE_WYRMKING] = 60,
            [xi.mission.id.cop.DAWN] = 70,
        },
        -- RoV missions  
        [xi.mission.log_id.ROV] = {
            [xi.mission.id.rov.RHAPSODIES_OF_VANADIEL] = 3,
            [xi.mission.id.rov.RESONANCE] = 6,
            [xi.mission.id.rov.SPIRITS_AWOKEN] = 75,
            [xi.mission.id.rov.CRASHING_WAVES] = 75,
        },
        -- ToAU missions
        [xi.mission.log_id.TOAU] = {
            [xi.mission.id.toau.LAND_OF_SACRED_SERPENTS] = 50,
            [xi.mission.id.toau.IMMORTAL_SENTRIES] = 60,
            [xi.mission.id.toau.PRESIDENT_SALAHEEM] = 60,
        },
    }
    
    if requirements[logId] and requirements[logId][missionId] then
        return requirements[logId][missionId]
    end
    
    return nil
end

-- Enhanced mission completion with validation
xi.missions.enhanced.completeMission = function(player, logId, nextMission, options)
    options = options or {}
    
    -- Validate current state
    local validationResult, message = xi.missions.enhanced.validateProgression(player, logId, player:getCurrentMission(logId))
    
    if validationResult ~= xi.missions.enhanced.validationResult.VALID then
        printf("Mission completion validation failed: %s", message)
        return false
    end
    
    -- Award experience if specified
    if options.experience then
        player:addExp(options.experience)
        if options.showExpMessage then
            player:messageBasic(xi.msg.basic.EXP_OBTAINED, options.experience)
        end
    end
    
    -- Award gil if specified
    if options.gil then
        player:addGil(options.gil)
        player:messageBasic(xi.msg.basic.GIL_OBTAINED, options.gil)
    end
    
    -- Award key items if specified
    if options.keyItems then
        for _, keyItem in ipairs(options.keyItems) do
            if not player:hasKeyItem(keyItem) then
                player:addKeyItem(keyItem)
                player:messageSpecial(zones[player:getZoneID()].text.KEYITEM_OBTAINED, keyItem)
            end
        end
    end
    
    -- Award items if specified
    if options.items then
        for _, item in ipairs(options.items) do
            local itemId = item.id or item
            local quantity = item.quantity or 1
            
            if player:getFreeSlotsCount() >= 1 then
                player:addItem(itemId, quantity)
                player:messageSpecial(zones[player:getZoneID()].text.ITEM_OBTAINED, itemId)
            else
                player:messageSpecial(zones[player:getZoneID()].text.ITEM_CANNOT_BE_OBTAINED, itemId)
            end
        end
    end
    
    -- Complete the mission
    player:completeMission(logId)
    
    -- Start next mission if specified
    if nextMission then
        player:addMission(logId, nextMission)
    end
    
    -- Log completion for validation
    xi.content.validation.addResult(
        xi.content.validation.category.MISSION_PROGRESSION,
        "Mission Completion",
        xi.content.validation.resultType.PASS,
        string.format("Mission %d completed successfully", player:getCurrentMission(logId)),
        {
            logId = logId,
            completedMission = player:getCurrentMission(logId),
            nextMission = nextMission,
            awards = options,
        }
    )
    
    return true
end

-- Enhanced cutscene progression with validation
xi.missions.enhanced.progressCutscene = function(mission, player, csid, options)
    options = options or {}
    
    -- Validate player state before progressing
    local validationResult, message = xi.missions.enhanced.validateProgression(
        player, 
        mission.logId, 
        mission.missionId
    )
    
    if validationResult ~= xi.missions.enhanced.validationResult.VALID and not options.skipValidation then
        printf("Cutscene progression validation failed: %s", message)
        return nil
    end
    
    -- Set mission variables if specified
    if options.setVars then
        for varName, value in pairs(options.setVars) do
            mission:setVar(player, varName, value)
        end
    end
    
    -- Track cutscene progression
    if options.trackProgression then
        local currentProgress = mission:getVar(player, 'CutsceneProgress') or 0
        mission:setVar(player, 'CutsceneProgress', currentProgress + 1)
    end
    
    return mission:progressEvent(csid, options.param1 or 0, options.param2 or 0, options.param3 or 0)
end

-- Fix common CoP progression issues
xi.missions.enhanced.fixCoPProgression = function(player)
    local copMission = player:getCurrentMission(xi.mission.log_id.COP)
    local copStatus = player:getMissionStatus(xi.mission.log_id.COP)
    
    -- Fix Promyvion progression blocking
    if copMission == xi.mission.id.cop.BELOW_THE_ARKS then
        local numPromyvionCompleted = 0
        for keyItem = xi.ki.LIGHT_OF_HOLLA, xi.ki.LIGHT_OF_MEA do
            if player:hasKeyItem(keyItem) then
                numPromyvionCompleted = numPromyvionCompleted + 1
            end
        end
        
        -- If player has completed all Promyvions but mission not progressed
        if numPromyvionCompleted >= 3 and copStatus ~= 2 then
            player:setMissionStatus(xi.mission.log_id.COP, 2)
            player:messageSpecial(zones[player:getZoneID()].text.MISSION_PROGRESS_UPDATED)
            return true
        end
    end
    
    -- Fix The Mothercrystals progression
    if copMission == xi.mission.id.cop.THE_MOTHERCRYSTALS then
        local hasAllLights = player:hasKeyItem(xi.ki.LIGHT_OF_HOLLA) and
                            player:hasKeyItem(xi.ki.LIGHT_OF_DEM) and
                            player:hasKeyItem(xi.ki.LIGHT_OF_MEA)
        
        if hasAllLights and copStatus == 0 then
            player:setMissionStatus(xi.mission.log_id.COP, 1)
            return true
        end
    end
    
    return false
end

-- Fix common RoV progression issues
xi.missions.enhanced.fixRoVProgression = function(player)
    local rovMission = player:getCurrentMission(xi.mission.log_id.ROV)
    local rovStatus = player:getMissionStatus(xi.mission.log_id.ROV)
    
    -- Fix common RoV chapter 1 completion issues
    if rovMission >= xi.mission.id.rov.RHAPSODIES_OF_VANADIEL and 
       rovMission <= xi.mission.id.rov.VOLTO_OSCURO then
        
        -- Check if player has completed required nation missions
        local nationMissionComplete = false
        for nationLogId = xi.mission.log_id.SANDORIA, xi.mission.log_id.WINDURST do
            if player:getCurrentMission(nationLogId) >= xi.mission.id.nation.MAGICITE then
                nationMissionComplete = true
                break
            end
        end
        
        if not nationMissionComplete and rovMission > xi.mission.id.rov.THE_BEGINNING then
            -- Reset to appropriate RoV mission based on progress
            player:addMission(xi.mission.log_id.ROV, xi.mission.id.rov.THE_BEGINNING)
            return true
        end
    end
    
    return false
}

-- Fix common ToAU progression issues  
xi.missions.enhanced.fixToAUProgression = function(player)
    local toauMission = player:getCurrentMission(xi.mission.log_id.TOAU)
    local toauStatus = player:getMissionStatus(xi.mission.log_id.TOAU)
    
    -- Fix Imperial Standing requirements
    if toauMission > xi.mission.id.toau.LAND_OF_SACRED_SERPENTS then
        local imperialStanding = player:getCurrency("imperial_standing")
        
        -- Some missions require minimum Imperial Standing
        local requiredStanding = {
            [xi.mission.id.toau.IMMORTAL_SENTRIES] = 1000,
            [xi.mission.id.toau.PRESIDENT_SALAHEEM] = 2000,
            [xi.mission.id.toau.LOST_KINGDOM] = 3000,
        }
        
        if requiredStanding[toauMission] and imperialStanding < requiredStanding[toauMission] then
            player:messageSpecial(zones[player:getZoneID()].text.IMPERIAL_STANDING_INCREASED, requiredStanding[toauMission] - imperialStanding)
            player:addCurrency("imperial_standing", requiredStanding[toauMission] - imperialStanding)
            return true
        end
    end
    
    return false
end

-- Comprehensive mission system diagnostic
xi.missions.enhanced.runDiagnostic = function(player)
    local diagnosticResults = {}
    
    -- Check all mission lines for issues
    for logId = xi.mission.log_id.NATION, xi.mission.log_id.ROV do
        local currentMission = player:getCurrentMission(logId)
        local status = player:getMissionStatus(logId)
        
        if currentMission and currentMission > 0 then
            local validationResult, message = xi.missions.enhanced.validateProgression(player, logId, currentMission)
            
            table.insert(diagnosticResults, {
                logId = logId,
                missionId = currentMission,
                status = status,
                validation = validationResult,
                message = message,
            })
            
            -- Attempt to fix known issues
            local fixed = false
            if logId == xi.mission.log_id.COP then
                fixed = xi.missions.enhanced.fixCoPProgression(player)
            elseif logId == xi.mission.log_id.ROV then
                fixed = xi.missions.enhanced.fixRoVProgression(player)
            elseif logId == xi.mission.log_id.TOAU then
                fixed = xi.missions.enhanced.fixToAUProgression(player)
            end
            
            if fixed then
                diagnosticResults[#diagnosticResults].fixed = true
            end
        end
    end
    
    return diagnosticResults
end

return xi.missions.enhanced