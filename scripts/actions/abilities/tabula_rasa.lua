-----------------------------------
-- Ability: Tabula Rasa
-- Optimizes both white and black magic capabilities while allowing charge-free stratagem use.
-- Enhanced with complete database integration and subjob support
-- Obtained: Scholar Level 1
-- Recast Time: 1:00:00
-- Duration: 0:03:00
-----------------------------------
---@type TAbility
local abilityObject = {}

abilityObject.onAbilityCheck = function(player, target, ability)
    return xi.job_utils.scholar.checkTabulaRasa(player, target, ability)
end

abilityObject.onUseAbility = function(player, target, ability)
    xi.job_utils.scholar.useTabulaRasa(player, target, ability)
    return xi.effect.TABULA_RASA
end

return abilityObject
