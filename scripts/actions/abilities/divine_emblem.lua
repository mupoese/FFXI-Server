-----------------------------------
-- Ability: Divine Emblem
-- Description: Enhances the accuracy of your next divine magic spell and increases enmity.
-- Obtained: PLD Level 78
-- Recast Time: 00:03:00
-- Duration: 00:01:00 or the next spell cast
-- Enhanced: Complete retail accuracy with subjob support
-----------------------------------
---@type TAbility
local abilityObject = {}

abilityObject.onAbilityCheck = function(player, target, ability)
    return xi.job_utils.paladin.checkDivineEmblem(player, target, ability)
end

abilityObject.onUseAbility = function(player, target, ability)
    xi.job_utils.paladin.useDivineEmblem(player, target, ability)
    
    -- Enhanced enmity generation
    local enmityBonus = xi.job_utils.paladin.calculateEnmityBonus(player, 300)
    player:updateEnmity(enmityBonus)
end

return abilityObject
