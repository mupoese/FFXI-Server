-----------------------------------
-- Moonlight
-- Enhanced implementation for ITERATION 8
-----------------------------------
---@type TWeaponSkill
local weaponskillObject = {}

weaponskillObject.onUseWeaponSkill = function(player, target, wsID, tp, primary, action, taChar)
    -- Enhanced Moonlight with proper fTP scaling for ITERATION 8
    local params = {}
    params.ftpMod = { 1.0, 1.25, 1.75 }
    params.str_wsc = 0.0
    params.dex_wsc = 0.0
    params.vit_wsc = 0.0
    params.agi_wsc = 0.0
    params.int_wsc = 0.0
    params.mnd_wsc = 0.3  -- MND affects potency
    params.chr_wsc = 0.0
    params.skill_multiplier = 0.11
    params.skillType = xi.skill.CLUB

    -- Calculate weaponskill damage using enhanced system
    local ftp = xi.weaponskills.fTP(tp, params.ftpMod)
    local skill = player:getSkillLevel(params.skillType)
    local wsc = player:getStat(xi.mod.MND) * params.mnd_wsc
    
    -- Enhanced damage calculation with improved scaling
    local baseDamage = math.floor((skill * params.skill_multiplier + wsc) * ftp)
    
    -- TP-based scaling enhancement
    local tpBonus = (tp - 1000) * 0.001 -- Additional scaling beyond base fTP
    baseDamage = math.floor(baseDamage * (1 + tpBonus))
    
    -- Apply weaponskill damage modifiers
    local wsModifier = 1 + (player:getMod(xi.mod.ALL_WSDMG_ALL_HITS) / 100)
    if player:getMod(xi.mod.WEAPONSKILL_DAMAGE_BASE + wsID) > 0 then
        wsModifier = wsModifier + (player:getMod(xi.mod.WEAPONSKILL_DAMAGE_BASE + wsID) / 100)
    end
    
    local finalDamage = math.floor(baseDamage * wsModifier)
    
    -- Apply weapon skill damage settings
    finalDamage = finalDamage * xi.settings.main.WEAPON_SKILL_POWER
    
    return 1, 0, false, finalDamage
end

return weaponskillObject
