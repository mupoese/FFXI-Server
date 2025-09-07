-----------------------------------
-- Ability: Sublimation
-- Gradually creates a storage of MP while reducing your HP. The effect ends once an MP limit is reached, 
-- or your HP has gone too low. The stored MP is then transferred to your MP pool by using the ability a second time.
-- Enhanced with complete database integration and subjob support
-- Obtained: Scholar Level 35
-- Recast Time: 30 seconds after the ability is reactivated
-- Duration (Charging): Until MP stored is 25% of Max HP or until HP = 50%
-- Duration (Charged): 2 hours
-----------------------------------
---@type TAbility
local abilityObject = {}

abilityObject.onAbilityCheck = function(player, target, ability)
    return xi.job_utils.scholar.checkSublimation(player, target, ability)
end

abilityObject.onUseAbility = function(player, target, ability)
    return xi.job_utils.scholar.useSublimation(player, target, ability)
end

return abilityObject
