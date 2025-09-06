-----------------------------------
-- Starburst
-- Staff weapon skill
-- Skill Level: 100
-- Deals light or darkness elemental damage. Damage varies with TP.
-- Aligned with the Shadow Gorget & Aqua Gorget.
-- Aligned with the Shadow Belt & Aqua Belt.
-- Element: Light/Dark (Random)
-- Modifiers: STR:40% MND:40%
-- 100%TP    200%TP    300%TP
-- 1.00      2.00      2.50
-- Enhanced for ITERATION 8
-----------------------------------
---@type TWeaponSkill
local weaponskillObject = {}

weaponskillObject.onUseWeaponSkill = function(player, target, wsID, tp, primary, action, taChar)
    local params = {}
    params.ftpMod = { 1.0, 2.0, 2.5 }
    params.skill = xi.skill.STAFF
    params.includemab = true
    
    -- Enhanced elemental selection with affinity considerations
    params.ele = xi.element.LIGHT
    local playerJob = player:getMainJob()
    local weatherBonus = 0
    
    -- Check weather and day effects for enhanced damage
    local weather = player:getWeather()
    local vanaDay = VanadielDayElement()
    
    if weather == xi.weather.SUNSHINE or vanaDay == xi.element.LIGHT then
        -- Light conditions favor light element
        if math.random(1, 100) <= 70 then
            params.ele = xi.element.LIGHT
            weatherBonus = 0.1
        else
            params.ele = xi.element.DARK
        end
    elseif playerJob == xi.job.DRK or playerJob == xi.job.BLM then
        -- Dark jobs prefer dark element
        if math.random(1, 100) <= 60 then
            params.ele = xi.element.DARK
        end
    else
        -- Random 50/50 for others
        if math.random(1, 100) <= 50 then
            params.ele = xi.element.DARK
        end
    end

    -- Enhanced WSC for ITERATION 8
    if xi.settings.main.USE_ADOULIN_WEAPON_SKILL_CHANGES then
        params.str_wsc = 0.4
        params.mnd_wsc = 0.4
    else
        params.str_wsc = 0.3
        params.mnd_wsc = 0.3
    end
    
    -- Apply enhanced magic weaponskill bonuses
    local wsBonus = player:getMod(xi.mod.ALL_WSDMG_ALL_HITS)
    if player:getMod(xi.mod.WEAPONSKILL_DAMAGE_BASE + wsID) > 0 then
        wsBonus = wsBonus + player:getMod(xi.mod.WEAPONSKILL_DAMAGE_BASE + wsID)
    end
    
    -- Weather and day bonuses
    params.bonusmab = wsBonus + (weatherBonus * 100)
    params.bonusacc = player:getMod(xi.mod.MACC) * 0.1

    local damage, criticalHit, tpHits, extraHits = xi.weaponskills.doMagicWeaponskill(player, target, wsID, params, tp, action, primary)
    return tpHits, extraHits, criticalHit, damage
end

return weaponskillObject
