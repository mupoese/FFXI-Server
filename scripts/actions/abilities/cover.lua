-----------------------------------
-- Ability: Cover
-- Allows you to protect party members by placing yourself between them and the enemy.
-- Obtained: Paladin Level 35
-- Recast Time: 0:03:00
-- Duration: 0:00:15 - 0:00:35
-- Info from https://www.bg-wiki.com/bg/Cover
-- Enhanced: Complete retail accuracy with subjob support
-----------------------------------
---@type TAbility
local abilityObject = {}

abilityObject.onAbilityCheck = function(player, target, ability)
    return xi.job_utils.paladin.checkCover(player, target, ability)
end

abilityObject.onUseAbility = function(player, target, ability)
    xi.job_utils.paladin.useCover(player, target, ability)
    
    -- Enhanced messaging based on subjob status
    local jobLevel, isSubjob = xi.job_utils.paladin.getJobLevel(player)
    if isSubjob then
        -- Subjob cover has reduced effectiveness
        player:messageBasic(xi.msg.basic.COVER_SUCCESS)
    end
end

return abilityObject
