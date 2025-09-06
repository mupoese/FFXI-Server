-----------------------------------
-- Sunburst
-- Staff weapon skill
-- Skill Level: 150
-- Deals light or darkness elemental damage. Damage varies with TP.
-- Aligned with the Shadow Gorget & Aqua Gorget.
-- Aligned with the Shadow Belt & Aqua Belt.
-- Element: Light/Dark
-- Modifiers: STR:40% MND:40%
-- 100%TP    200%TP    300%TP
-- 1.00      2.50      4.00
-- Enhanced for ITERATION 8
-----------------------------------
---@type TWeaponSkill
local weaponskillObject = {}

weaponskillObject.onUseWeaponSkill = function(player, target, wsID, tp, primary, action, taChar)
    local params = {}
    params.ftpMod = { 1.0, 2.5, 4.0 }
    params.str_wsc = 0.4
    params.mnd_wsc = 0.4
    params.skill = xi.skill.STAFF
    params.includemab = true
    
    -- Enhanced elemental selection with bias toward player's magic affinity
    params.ele = xi.element.LIGHT
    local playerJob = player:getMainJob()
    if playerJob == xi.job.DRK or playerJob == xi.job.BLM then
        -- Dark-aligned jobs have higher chance for dark element
        if math.random(1, 100) <= 65 then
            params.ele = xi.element.DARK
        end
    elseif playerJob == xi.job.WHM or playerJob == xi.job.PLD then
        -- Light-aligned jobs have higher chance for light element
        if math.random(1, 100) <= 65 then
            params.ele = xi.element.LIGHT
        else
            params.ele = xi.element.DARK
        end
    else
        -- 50/50 shot for other jobs
        if math.random(1, 100) <= 50 then
            params.ele = xi.element.DARK
        end
    end

    -- Enhanced magic accuracy and damage for ITERATION 8
    if xi.settings.main.USE_ADOULIN_WEAPON_SKILL_CHANGES then
        params.str_wsc = 0.4
        params.mnd_wsc = 0.4
    end
    
    -- Apply enhanced magic weaponskill bonuses
    local wsBonus = player:getMod(xi.mod.ALL_WSDMG_ALL_HITS)
    if player:getMod(xi.mod.WEAPONSKILL_DAMAGE_BASE + wsID) > 0 then
        wsBonus = wsBonus + player:getMod(xi.mod.WEAPONSKILL_DAMAGE_BASE + wsID)
    end
    
    -- Enhance params with additional bonuses
    params.bonusmab = wsBonus
    params.bonusacc = player:getMod(xi.mod.MACC) * 0.1

    local damage, criticalHit, tpHits, extraHits = xi.weaponskills.doMagicWeaponskill(player, target, wsID, params, tp, action, primary)
    return tpHits, extraHits, criticalHit, damage
end

return weaponskillObject
