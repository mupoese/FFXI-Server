-----------------------------------
-- xi.effect.STRIKING_FLOURISH
-----------------------------------
---@type TEffect
local effectObject = {}

effectObject.onEffectGain = function(target, effect)
    local power = effect:getPower()
    
    -- Striking Flourish provides accuracy bonus and double attack rate
    -- Power determines the potency (1-3 based on finishing moves consumed)
    local accBonus = power * 10  -- +10/20/30 accuracy
    local daBonus = power * 5    -- +5%/10%/15% double attack rate
    
    effect:addMod(xi.mod.ACC, accBonus)
    effect:addMod(xi.mod.DOUBLE_ATTACK, daBonus)
end

effectObject.onEffectTick = function(target, effect)
end

effectObject.onEffectLose = function(target, effect)
end

return effectObject
