-----------------------------------
-- Ability: Invincible
-- Grants immunity to all physical attacks.
-- Obtained: Paladin Level 1
-- Recast Time: 1:00:00
-- Duration: 0:00:30
-- Enhanced: Complete retail accuracy with subjob support
-----------------------------------
---@type TAbility
local abilityObject = {}

abilityObject.onAbilityCheck = function(player, target, ability)
    return xi.job_utils.paladin.checkInvincible(player, target, ability)
end

abilityObject.onUseAbility = function(player, target, ability)
    xi.job_utils.paladin.useInvincible(player, target, ability)
    
    -- Enhanced messaging for job completeness
    local jobLevel, isSubjob = xi.job_utils.paladin.getJobLevel(player)
    if isSubjob then
        ability:setMsg(xi.msg.basic.JA_GAINS_EFFECT_SUBJ)
    else
        ability:setMsg(xi.msg.basic.JA_GAINS_EFFECT)
    end
end

return abilityObject
