-----------------------------------
-- Chant du Cygne
-- Sword weapon skill
-- Skill level: EMPYREAN
-- Delivers a three-hit attack. Chance of params.critical varies with TP.
-- Will stack with Sneak Attack.
-- Element: None
-- Modifiers: DEX:60%
-- 100%TP    200%TP    300%TP
--         ALL 2.25
-----------------------------------
---@type TWeaponSkill
local weaponskillObject = {}

weaponskillObject.onUseWeaponSkill = function(player, target, wsID, tp, primary, action, taChar)
    local params = {}
    params.numHits = 3
    params.ftpMod = { 2.25, 2.25, 2.25 }
    params.dex_wsc = 0.6
    params.critVaries = { 0.15, 0.25, 0.4 }

    if xi.settings.main.USE_ADOULIN_WEAPON_SKILL_CHANGES then
        params.ftpMod = { 1.6328125, 1.6328125, 1.6328125 }
        params.dex_wsc = 0.8
        params.multiHitfTP = true -- https://www.bg-wiki.com/ffxi/Chant_du_Cygne
    end
    
    -- ITERATION 8 Enhancement: Enhanced critical hit scaling
    params.enhanced = true
    if player:isPC() then
        local jpLevel = player:getJobPointLevel(xi.jp.CRITICAL_HIT_RATE)
        if jpLevel > 0 then
            for i = 1, #params.critVaries do
                params.critVaries[i] = params.critVaries[i] + (jpLevel * 0.01)
            end
        end
        
        -- Enhanced WSC with job mastery bonuses
        local masteryBonus = player:getJobPointLevel(xi.jp.WEAPONSKILL_DAMAGE) * 0.01
        params.dex_wsc = params.dex_wsc + masteryBonus
    end

    -- Apply aftermath
    xi.aftermath.addStatusEffect(player, tp, xi.slot.MAIN, xi.aftermath.type.EMPYREAN)

    -- Use enhanced weaponskill function if available
    local damage, criticalHit, tpHits, extraHits
    if xi.enhanced_weaponskills and xi.enhanced_weaponskills.doEnhancedPhysicalWeaponskill then
        damage, criticalHit, tpHits, extraHits = xi.enhanced_weaponskills.doEnhancedPhysicalWeaponskill(player, target, wsID, params, tp, action, primary, taChar)
    else
        damage, criticalHit, tpHits, extraHits = xi.weaponskills.doPhysicalWeaponskill(player, target, wsID, params, tp, action, primary, taChar)
    end

    return tpHits, extraHits, criticalHit, damage
end

return weaponskillObject
