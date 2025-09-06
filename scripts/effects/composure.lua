-----------------------------------
-- xi.effect.COMPOSURE
-- Increases accuracy and lengthens recast time. Enhancement effects gained through white
-- and black magic you cast on yourself last longer.
-----------------------------------
---@type TEffect
local effectObject = {}

effectObject.onEffectGain = function(target, effect)
    local power = math.floor((24 * target:getMainLvl() + 74) / 49) + target:getJobPointLevel(xi.jp.COMPOSURE_EFFECT)

    effect:addMod(xi.mod.ACC, power)
    
    -- Enhanced enspell damage when Composure is active
    -- Composure enhances enspell damage by approximately 25% base + Job Point bonuses
    local enspellBonus = 25 + (target:getJobPointLevel(xi.jp.COMPOSURE_EFFECT) * 5)
    effect:addMod(xi.mod.ENSPELL_DMG_BONUS, enspellBonus)
end

effectObject.onEffectTick = function(target, effect)
end

effectObject.onEffectLose = function(target, effect)
end

return effectObject
