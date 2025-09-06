-----------------------------------
-- Myrkr
-----------------------------------
---@type TWeaponSkill
local weaponskillObject = {}

weaponskillObject.onUseWeaponSkill = function(player, target, wsID, tp, primary, action, taChar)
    -- Apply aftermath
    xi.aftermath.addStatusEffect(player, tp, xi.slot.MAIN, xi.aftermath.type.EMPYREAN)

    -- Enhanced fTP calculation for Myrkr (ITERATION 8 enhancement)
    local params = {}
    params.ftpMod = { 0.2, 0.4, 0.6 }
    params.str_wsc = 0.0
    params.dex_wsc = 0.0
    params.vit_wsc = 0.0
    params.agi_wsc = 0.0
    params.int_wsc = 0.0
    params.mnd_wsc = 1.0 -- MND affects MP restoration
    params.chr_wsc = 0.0
    
    local ftpmp = xi.weaponskills.fTP(tp, params.ftpMod)
    local mpRestored = math.floor(ftpmp * player:getMaxMP())
    
    -- Enhanced MP restoration with weaponskill modifiers
    local wsModifier = 1 + (player:getMod(xi.mod.ALL_WSDMG_ALL_HITS) / 100)
    mpRestored = math.floor(mpRestored * wsModifier)
    
    -- Apply MND scaling for enhanced retail accuracy
    local mndBonus = player:getStat(xi.mod.MND) * 0.1
    mpRestored = mpRestored + math.floor(mndBonus)
    
    return 1, 0, false, mpRestored
end

return weaponskillObject
