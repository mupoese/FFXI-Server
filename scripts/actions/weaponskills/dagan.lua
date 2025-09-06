-----------------------------------
-- Dagan
-- Description: Restores HP and MP. Amount restored varies with TP. Gambanteinn: Aftermath.
-- Acquired permanently by completing the appropriate Walk of Echoes Weapon Skill Trials.
-- Can also be used by equipping Gambanteinn (85), Gambanteinn (90), Canne de Combat +1 or Canne de Combat +2.
-- Skillchain Properties: N/A
-- Modifiers: Max HP / Max MP
-- Amount restored in HP/MP by TP
-- Does not deal damage.
-----------------------------------
---@type TWeaponSkill
local weaponskillObject = {}

weaponskillObject.onUseWeaponSkill = function(player, target, wsID, tp, primary, action, taChar)
    -- Apply aftermath
    xi.aftermath.addStatusEffect(player, tp, xi.slot.MAIN, xi.aftermath.type.EMPYREAN)

    -- Enhanced fTP calculation for ITERATION 8
    local params = {}
    params.ftpMod = { 0.22, 0.33, 0.52 }
    params.ftpModMP = { 0.15, 0.22, 0.35 }
    params.str_wsc = 0.0
    params.dex_wsc = 0.0
    params.vit_wsc = 0.0
    params.agi_wsc = 0.0
    params.int_wsc = 0.0
    params.mnd_wsc = 0.5 -- MND affects both HP and MP restoration
    params.chr_wsc = 0.0

    local ftphp = xi.weaponskills.fTP(tp, params.ftpMod)
    local ftpmp = xi.weaponskills.fTP(tp, params.ftpModMP)
    
    -- Enhanced restoration with weaponskill modifiers
    local wsModifier = 1 + (player:getMod(xi.mod.ALL_WSDMG_ALL_HITS) / 100)
    local mndBonus = player:getStat(xi.mod.MND) * params.mnd_wsc
    
    -- Calculate restoration amounts with MND scaling
    local hpRestored = math.floor((ftphp * player:getMaxHP() + mndBonus) * wsModifier)
    local mpRestored = math.floor((ftpmp * player:getMaxMP() + mndBonus * 0.5) * wsModifier)
    
    -- Enhanced restoration with Job Point bonuses
    if player:isPC() then
        local jpBonus = player:getJobPointLevel(xi.jp.CURE_POTENCY) or 0
        if jpBonus > 0 then
            hpRestored = hpRestored + math.floor(hpRestored * (jpBonus * 0.01))
            mpRestored = mpRestored + math.floor(mpRestored * (jpBonus * 0.01))
        end
    end
    
    -- Apply healing modifiers
    local healingBonus = player:getMod(xi.mod.CURE_POTENCY) / 100
    hpRestored = math.floor(hpRestored * (1 + healingBonus))
    mpRestored = math.floor(mpRestored * (1 + healingBonus))
    
    player:addHP(hpRestored)
    return 0, 0, false, mpRestored
end

return weaponskillObject
