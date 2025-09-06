-----------------------------------
-- Ability: Perpetuance
-- Increases the enhancement effect duration of your next white magic spell.
-- Obtained: Scholar Level 87
-- Recast Time: Stratagem Charge
-- Duration: 00:01:00 or first white Enhancing Magic cast, whichever first
-- Enhanced with complete database integration and subjob support
-----------------------------------
---@type TAbility
local abilityObject = {}

abilityObject.onAbilityCheck = function(player, target, ability)
    -- Use enhanced Scholar job utilities for validation
    return xi.job_utils.scholar.checkStratagem(player, target, ability)
end

abilityObject.onUseAbility = function(player, target, ability)
    -- Use enhanced Scholar job utilities for implementation
    xi.job_utils.scholar.usePerpettuance(player, target, ability)
    return xi.effect.PERPETUANCE
end

return abilityObject
