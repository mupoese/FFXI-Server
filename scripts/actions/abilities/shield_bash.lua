-----------------------------------
-- Ability: Shield Bash
-- Delivers an attack that can stun the target. Shield required.
-- Obtained: Paladin Level 15, Valoredge automaton frame Level 1
-- Recast Time: 1:00 minute (3:00 for Valoredge version)
-- Duration: Instant
-- Enhanced: Complete retail accuracy with subjob support
-----------------------------------
---@type TAbility
local abilityObject = {}

abilityObject.onAbilityCheck = function(player, target, ability)
    return xi.job_utils.paladin.checkShieldBash(player, target, ability)
end

abilityObject.onUseAbility = function(player, target, ability)
    local damage = xi.job_utils.paladin.useShieldBash(player, target, ability)
    
    -- Enhanced enmity generation for tanking
    local enmityBonus = xi.job_utils.paladin.calculateEnmityBonus(player, damage)
    target:updateEnmityFromDamage(player, enmityBonus)
    
    return damage
end

return abilityObject
