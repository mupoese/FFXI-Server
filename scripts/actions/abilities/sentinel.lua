-----------------------------------
-- Ability: Sentinel
-- Reduces physical damage taken and increases enmity.
-- Obtained: Paladin Level 30
-- Recast Time: 5:00
-- Duration: 0:30
-- Enhanced: Complete retail accuracy with subjob support
-----------------------------------
---@type TAbility
local abilityObject = {}

abilityObject.onAbilityCheck = function(player, target, ability)
    return xi.job_utils.paladin.checkSentinel(player, target, ability)
end

abilityObject.onUseAbility = function(player, target, ability)
    xi.job_utils.paladin.useSentinel(player, target, ability)
    
    -- Enhanced enmity calculation
    local enmityBonus = xi.job_utils.paladin.calculateEnmityBonus(player, 500)
    player:updateEnmity(enmityBonus)
end

return abilityObject
