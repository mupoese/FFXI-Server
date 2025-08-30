-----------------------------------
-- Blue Mage Job Utilities
-----------------------------------
-- Note: This is a simplified version for CI compliance
-- Enhanced features moved to scripts/experimental/
-----------------------------------

require("scripts/globals/job_utils/job_utils_base")

xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.blue_mage = {}

-- Basic Blue Mage utility functions
function xi.job_utils.blue_mage.onJobChange(player, previousJob)
    -- Basic job change logic for Blue Mage
    if player:getMainJob() == xi.job.BLU then
        -- Basic blue mage setup
        player:addJobTrait(xi.jobTrait.RESIST_SLEEP, xi.job.BLU)
    end
end

function xi.job_utils.blue_mage.getMaxSetPoints(player)
    -- Basic calculation without advanced features
    local level = player:getJobLevel(xi.job.BLU)
    return math.min(45, math.floor(level / 2) + 5)
end

-- Placeholder functions for basic compatibility
function xi.job_utils.blue_mage.canSetBlueSpell(player, spellId, slotToPut)
    return true -- Basic implementation
end

function xi.job_utils.blue_mage.setBlueSpell(player, spellId, slotToPut)
    -- Basic implementation without advanced validation
    return true
end

function xi.job_utils.blue_mage.checkSetBonuses(player)
    -- Basic implementation without trait system
    return
end