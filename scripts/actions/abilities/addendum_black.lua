-----------------------------------
-- Ability: Addendum: Black
-- Allows access to additional Black Magic spells while using Dark Arts.
-- Enhanced with complete database integration and subjob support  
-- Obtained: Scholar Level 30
-- Recast Time: Stratagem Charge
-- Duration: 2 hours
-----------------------------------
---@type TAbility
local abilityObject = {}

abilityObject.onAbilityCheck = function(player, target, ability)
    return xi.job_utils.scholar.checkStratagem(player, target, ability)
end

abilityObject.onUseAbility = function(player, target, ability)
    xi.job_utils.scholar.useAddendumBlack(player, target, ability)
    return xi.effect.ADDENDUM_BLACK
end

return abilityObject
