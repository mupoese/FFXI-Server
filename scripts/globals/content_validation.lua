-----------------------------------
-- Content Validation System
-- Phase 4: Comprehensive validation framework for content accuracy
-----------------------------------
require('scripts/globals/items')
require('scripts/globals/missions')
require('scripts/globals/quests')
require('scripts/globals/keyitems')
require('scripts/globals/status')
-----------------------------------
xi = xi or {}
xi.content = xi.content or {}
xi.content.validation = xi.content.validation or {}

-- Validation result structure
xi.content.validation.resultType =
{
    PASS     = 0,
    WARNING  = 1,
    FAILURE  = 2,
    CRITICAL = 3,
}

-- Content validation categories
xi.content.validation.category =
{
    MISSION_PROGRESSION = 1,
    TRUST_AI_BEHAVIOR   = 2,
    BATTLEFIELD_REWARDS = 3,
    STATUS_EFFECTS      = 4,
    ITEM_PROPERTIES     = 5,
    NPC_INTERACTIONS    = 6,
}

-- Validation context for detailed reporting
xi.content.validation.context = {}

-- Initialize validation system
xi.content.validation.initialize = function()
    xi.content.validation.results = {}
    xi.content.validation.warnings = 0
    xi.content.validation.failures = 0
    xi.content.validation.criticals = 0
end

-- Add validation result
xi.content.validation.addResult = function(category, test, result, message, details)
    local entry = {
        category = category,
        test = test,
        result = result,
        message = message,
        details = details or {},
        timestamp = os.time(),
    }
    
    table.insert(xi.content.validation.results, entry)
    
    if result == xi.content.validation.resultType.WARNING then
        xi.content.validation.warnings = xi.content.validation.warnings + 1
    elseif result == xi.content.validation.resultType.FAILURE then
        xi.content.validation.failures = xi.content.validation.failures + 1
    elseif result == xi.content.validation.resultType.CRITICAL then
        xi.content.validation.criticals = xi.content.validation.criticals + 1
    end
end

-- Mission progression validation
xi.content.validation.validateMissionProgression = function(player, missionLogId, missionId)
    local mission = player:getCurrentMission(missionLogId)
    local status = player:getMissionStatus(missionLogId)
    local progress = player:getMissionProgress(missionLogId)
    
    -- Check for common mission blocking issues
    local validationTests = {
        {
            name = "Mission Available",
            test = function() return mission >= 0 end,
            message = "Mission is not available or invalid",
        },
        {
            name = "Status Consistency",
            test = function() return status >= 0 and status <= 5 end,
            message = "Mission status is outside valid range",
        },
        {
            name = "Progress Logic",
            test = function() return progress >= 0 end,
            message = "Mission progress is negative or invalid",
        },
    }
    
    for _, validation in ipairs(validationTests) do
        local success = validation.test()
        local result = success and xi.content.validation.resultType.PASS or xi.content.validation.resultType.FAILURE
        
        xi.content.validation.addResult(
            xi.content.validation.category.MISSION_PROGRESSION,
            validation.name,
            result,
            validation.message,
            {
                missionLogId = missionLogId,
                missionId = missionId,
                currentMission = mission,
                status = status,
                progress = progress,
            }
        )
    end
end

-- Trust AI behavior validation
xi.content.validation.validateTrustAI = function(trustMob)
    if not trustMob or not trustMob:isTrust() then
        xi.content.validation.addResult(
            xi.content.validation.category.TRUST_AI_BEHAVIOR,
            "Trust Entity Check",
            xi.content.validation.resultType.FAILURE,
            "Invalid trust entity provided"
        )
        return
    end
    
    local validationTests = {
        {
            name = "AI Responsiveness",
            test = function() return trustMob:isAlive() and trustMob:getTarget() ~= nil end,
            message = "Trust is not responding to combat situations",
        },
        {
            name = "Movement Behavior",
            test = function() return trustMob:getSpeed() > 0 or trustMob:getAnimation() ~= 0 end,
            message = "Trust movement appears frozen or incorrect",
        },
        {
            name = "Ability Usage",
            test = function() return trustMob:getTP() < 3000 or trustMob:hasPreferredTarget() end,
            message = "Trust is not using abilities appropriately",
        },
    }
    
    for _, validation in ipairs(validationTests) do
        local success = validation.test()
        local result = success and xi.content.validation.resultType.PASS or xi.content.validation.resultType.WARNING
        
        xi.content.validation.addResult(
            xi.content.validation.category.TRUST_AI_BEHAVIOR,
            validation.name,
            result,
            validation.message,
            {
                trustId = trustMob:getID(),
                trustName = trustMob:getName(),
                level = trustMob:getMainLvl(),
                target = trustMob:getTarget() and trustMob:getTarget():getID() or nil,
            }
        )
    end
end

-- Battlefield reward validation
xi.content.validation.validateBattlefieldRewards = function(battlefield, players)
    if not battlefield then
        xi.content.validation.addResult(
            xi.content.validation.category.BATTLEFIELD_REWARDS,
            "Battlefield Existence",
            xi.content.validation.resultType.CRITICAL,
            "Battlefield instance is nil"
        )
        return
    end
    
    local battlefieldId = battlefield:getID()
    local timeRemaining = battlefield:getTimeRemaining()
    local status = battlefield:getStatus()
    
    local validationTests = {
        {
            name = "Reward Distribution",
            test = function()
                -- Check if rewards are properly distributed to players
                for _, player in ipairs(players) do
                    if not player:hasStatusEffect(xi.effect.BATTLEFIELD) then
                        return false
                    end
                end
                return true
            end,
            message = "Players may not be receiving battlefield rewards correctly",
        },
        {
            name = "Time Management",
            test = function() return timeRemaining > 0 or status == xi.battlefield.status.WON end,
            message = "Battlefield time management issue detected",
        },
        {
            name = "Status Consistency",
            test = function() return status >= 0 and status <= 4 end,
            message = "Battlefield status is outside valid range",
        },
    }
    
    for _, validation in ipairs(validationTests) do
        local success = validation.test()
        local result = success and xi.content.validation.resultType.PASS or xi.content.validation.resultType.FAILURE
        
        xi.content.validation.addResult(
            xi.content.validation.category.BATTLEFIELD_REWARDS,
            validation.name,
            result,
            validation.message,
            {
                battlefieldId = battlefieldId,
                timeRemaining = timeRemaining,
                status = status,
                playerCount = #players,
            }
        )
    end
end

-- Status effect validation
xi.content.validation.validateStatusEffects = function(entity, expectedEffects)
    if not entity then
        xi.content.validation.addResult(
            xi.content.validation.category.STATUS_EFFECTS,
            "Entity Check",
            xi.content.validation.resultType.FAILURE,
            "Invalid entity provided for status effect validation"
        )
        return
    end
    
    for effectId, expectedData in pairs(expectedEffects) do
        local hasEffect = entity:hasStatusEffect(effectId)
        local effect = entity:getStatusEffect(effectId)
        
        local validationTests = {
            {
                name = "Effect Presence - " .. effectId,
                test = function() return hasEffect == expectedData.shouldHave end,
                message = expectedData.shouldHave and "Missing expected status effect" or "Has unexpected status effect",
            }
        }
        
        if hasEffect and effect and expectedData.shouldHave then
            table.insert(validationTests, {
                name = "Effect Duration - " .. effectId,
                test = function() return effect:getDuration() > 0 end,
                message = "Status effect has invalid duration",
            })
            
            if expectedData.power then
                table.insert(validationTests, {
                    name = "Effect Power - " .. effectId,
                    test = function() return effect:getPower() == expectedData.power end,
                    message = "Status effect power does not match expected value",
                })
            end
        end
        
        for _, validation in ipairs(validationTests) do
            local success = validation.test()
            local result = success and xi.content.validation.resultType.PASS or xi.content.validation.resultType.WARNING
            
            xi.content.validation.addResult(
                xi.content.validation.category.STATUS_EFFECTS,
                validation.name,
                result,
                validation.message,
                {
                    entityId = entity:getID(),
                    effectId = effectId,
                    hasEffect = hasEffect,
                    expectedData = expectedData,
                    actualPower = effect and effect:getPower() or nil,
                    actualDuration = effect and effect:getDuration() or nil,
                }
            )
        end
    end
end

-- Generate validation report
xi.content.validation.generateReport = function()
    local report = {
        summary = {
            total = #xi.content.validation.results,
            warnings = xi.content.validation.warnings,
            failures = xi.content.validation.failures,
            criticals = xi.content.validation.criticals,
            timestamp = os.time(),
        },
        results = xi.content.validation.results,
    }
    
    -- Calculate success rate
    local passed = report.summary.total - report.summary.warnings - report.summary.failures - report.summary.criticals
    report.summary.successRate = report.summary.total > 0 and (passed / report.summary.total * 100) or 100
    
    return report
end

-- Export validation results for external analysis
xi.content.validation.exportResults = function(filename)
    local report = xi.content.validation.generateReport()
    
    -- This would write to a file in a real implementation
    -- For now, we'll return the formatted data
    local output = string.format(
        "Content Validation Report - %s\n" ..
        "========================================\n" ..
        "Total Tests: %d\n" ..
        "Passed: %d (%.1f%%)\n" ..
        "Warnings: %d\n" ..
        "Failures: %d\n" ..
        "Critical: %d\n\n",
        os.date("%Y-%m-%d %H:%M:%S", report.summary.timestamp),
        report.summary.total,
        report.summary.total - report.summary.warnings - report.summary.failures - report.summary.criticals,
        report.summary.successRate,
        report.summary.warnings,
        report.summary.failures,
        report.summary.criticals
    )
    
    return output
end

-- Quick validation for common scenarios
xi.content.validation.quickValidation = function(player)
    xi.content.validation.initialize()
    
    -- Validate current mission state
    for logId = xi.mission.log_id.NATION, xi.mission.log_id.ROV do
        local currentMission = player:getCurrentMission(logId)
        if currentMission and currentMission > 0 then
            xi.content.validation.validateMissionProgression(player, logId, currentMission)
        end
    end
    
    -- Validate active trusts
    local zone = player:getZone()
    if zone then
        local trusts = zone:getEntitiesByType(xi.objType.TRUST)
        for _, trust in ipairs(trusts) do
            if trust:getMaster() and trust:getMaster():getID() == player:getID() then
                xi.content.validation.validateTrustAI(trust)
            end
        end
    end
    
    return xi.content.validation.generateReport()
end

return xi.content.validation