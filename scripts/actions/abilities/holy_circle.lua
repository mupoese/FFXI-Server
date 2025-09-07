-----------------------------------
-- Ability: Holy Circle
-- Grants resistance, defense, and attack against Undead to party members within the area of effect.
-- Obtained: Paladin Level 5
-- Recast Time: 5:00 minutes
-- Duration: 3:00 minutes
-- Enhanced: Complete retail accuracy with subjob support
-----------------------------------
---@type TAbility
local abilityObject = {}

abilityObject.onAbilityCheck = function(player, target, ability)
    return xi.job_utils.paladin.checkHolyCircle(player, target, ability)
end

abilityObject.onUseAbility = function(player, target, ability)
    xi.job_utils.paladin.useHolyCircle(player, target, ability)
    
    -- Enhanced area of effect for party members
    local jobLevel, isSubjob = xi.job_utils.paladin.getJobLevel(player)
    local party = player:getParty()
    
    if party then
        for _, member in pairs(party) do
            if member and member:isWithinRange(player, 10) then
                xi.job_utils.paladin.useHolyCircle(player, member, ability)
            end
        end
    end
end

return abilityObject
