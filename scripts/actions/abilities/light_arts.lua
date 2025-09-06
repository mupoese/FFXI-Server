-----------------------------------
-- Ability: Light Arts
-- Optimizes white magic capability while lowering black magic proficiency. 
-- Grants a bonus to divine, enhancing, enfeebling, and healing magic. Also grants access to Stratagems.
-- Enhanced with complete database integration and subjob support
-- Obtained: Scholar Level 10
-- Recast Time: 1:00
-- Duration: 2:00:00
-----------------------------------
---@type TAbility
local abilityObject = {}

abilityObject.onAbilityCheck = function(player, target, ability)
    return xi.job_utils.scholar.checkLightArts(player, target, ability)
end

abilityObject.onUseAbility = function(player, target, ability)
    xi.job_utils.scholar.useLightArts(player, target, ability)
    return xi.effect.LIGHT_ARTS
end

return abilityObject
