-----------------------------------
-- Energy Drain
-----------------------------------
---@type TWeaponSkill
local weaponskillObject = {}

-- https://www.bg-wiki.com/ffxi/Energy_Drain
weaponskillObject.onUseWeaponSkill = function(player, target, wsID, tp, primary, action, taChar)
    -- Enhanced Energy Drain with ITERATION 8 improvements
    local params = {}
    params.ftpMod = { 1.25, 2.5, 4.125 }
    params.str_wsc = 0.0
    params.dex_wsc = 0.0
    params.vit_wsc = 0.0
    params.agi_wsc = 0.0
    params.int_wsc = 0.0
    params.mnd_wsc = 1.0
    params.chr_wsc = 0.0
    
    local fTPAnchors = params.ftpMod
    local startingAnchor = math.floor(tp / 1000)
    local multiplier = 0

    if tp >= 3000 then
        multiplier = fTPAnchors[3]
    else
        local basefTP   = fTPAnchors[startingAnchor]
        local nextfTP   = fTPAnchors[startingAnchor + 1]
        local multPerTP = (nextfTP - basefTP) / 1000 * (tp - 1000 * startingAnchor)
        multiplier = basefTP + multPerTP
    end

    local skill = player:getSkillLevel(xi.skill.DAGGER)
    local wsc   = player:getStat(xi.mod.MND) * params.mnd_wsc

    local mpRestored = math.floor((math.floor(skill * 0.11) + wsc) * multiplier)
    
    -- Enhanced drain calculation with weaponskill damage bonuses
    local wsBonus = player:getMod(xi.mod.ALL_WSDMG_ALL_HITS)
    if player:getMod(xi.mod.WEAPONSKILL_DAMAGE_BASE + wsID) > 0 then
        wsBonus = wsBonus + player:getMod(xi.mod.WEAPONSKILL_DAMAGE_BASE + wsID)
    end
    mpRestored = math.floor(mpRestored * (100 + wsBonus) / 100)

    if target:isUndead() then
        mpRestored = 0
    else
        -- Enhanced MP absorption with target resistance
        local targetResistance = target:getMod(xi.mod.MP_DRAIN_RESIST) or 0
        local drainAmount = math.floor(mpRestored * (100 - targetResistance) / 100)
        
        -- Absorb MP from target
        mpRestored = target:delMP(drainAmount)

        -- Add stolen MP to player
        mpRestored = player:addMP(mpRestored)
    end

    -- Display MP actually given to player
    action:messageID(target:getID(), xi.msg.basic.SKILL_DRAIN_MP)
    action:param(target:getID(), mpRestored)

    return 1, 0, false, mpRestored
end

return weaponskillObject
