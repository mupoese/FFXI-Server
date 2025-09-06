-----------------------------------
-- Ability: Accession
-- Extends the effect of your next healing or enhancing white magic spell to party members within range.
-- MP cost and casting time are doubled.
-- Obtained: Scholar Level 40
-- Enhanced with complete database integration and subjob support
-----------------------------------
---@type TAbility
local abilityObject = {}

abilityObject.onAbilityCheck = function(player, target, ability)
    return xi.job_utils.scholar.checkStratagem(player, target, ability)
end

abilityObject.onUseAbility = function(player, target, ability)
    xi.job_utils.scholar.useAccession(player, target, ability)
    return xi.effect.ACCESSION
end

return abilityObject
