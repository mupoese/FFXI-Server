-----------------------------------
-- Ability: Alacrity
-- Reduces the casting and the recast time of your next black magic spell by 50%.
-- Obtained: Scholar Level 25
-- Enhanced with complete database integration and subjob support
-----------------------------------
---@type TAbility
local abilityObject = {}

abilityObject.onAbilityCheck = function(player, target, ability)
    return xi.job_utils.scholar.checkStratagem(player, target, ability)
end

abilityObject.onUseAbility = function(player, target, ability)
    xi.job_utils.scholar.useAlacrity(player, target, ability)
    return xi.effect.ALACRITY
end

return abilityObject
