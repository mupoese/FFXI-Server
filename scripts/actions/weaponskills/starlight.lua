-----------------------------------
-- Starlight
-- Enhanced implementation for ITERATION 8
-----------------------------------
---@type TWeaponSkill
local weaponskillObject = {}

weaponskillObject.onUseWeaponSkill = function(player, target, wsID, tp, primary, action, taChar)
    -- Enhanced Starlight with proper fTP scaling for ITERATION 8
    local params = {}
    params.ftpMod = { 1.0, 1.5, 2.25 }
    params.str_wsc = 0.3  -- STR affects damage
    params.dex_wsc = 0.0
    params.vit_wsc = 0.0
    params.agi_wsc = 0.0
    params.int_wsc = 0.0
    params.mnd_wsc = 0.2  -- MND affects potency
    params.chr_wsc = 0.0
    params.skill_multiplier = 0.11
    params.skillType = xi.skill.CLUB

    -- Calculate weaponskill damage using enhanced system
    local ftp = xi.weaponskills.fTP(tp, params.ftpMod)
    local skill = player:getSkillLevel(params.skillType)
    local wsc = player:getStat(xi.mod.STR) * params.str_wsc + player:getStat(xi.mod.MND) * params.mnd_wsc
    
    -- Enhanced damage calculation with fSTR
    local fstr = xi.weaponskills.fSTR(player, target, params.skillType)
    local baseDamage = math.floor((skill * params.skill_multiplier + wsc + fstr) * ftp)
    
    -- Apply weaponskill damage modifiers
    local wsModifier = 1 + (player:getMod(xi.mod.ALL_WSDMG_ALL_HITS) / 100)
    if player:getMod(xi.mod.WEAPONSKILL_DAMAGE_BASE + wsID) > 0 then
        wsModifier = wsModifier + (player:getMod(xi.mod.WEAPONSKILL_DAMAGE_BASE + wsID) / 100)
    end
    
    -- Apply skill and level-based scaling
    local levelCorrection = 1.0
    if player:getMainLvl() > target:getMainLvl() then
        levelCorrection = 1.0 + (player:getMainLvl() - target:getMainLvl()) * 0.005
    end
    
    local finalDamage = math.floor(baseDamage * wsModifier * levelCorrection)
    
    -- Apply target damage reduction
    finalDamage = target:physicalDmgTaken(finalDamage, xi.damageType.BLUNT)
    finalDamage = finalDamage - target:getMod(xi.mod.PHALANX)
    finalDamage = math.max(0, finalDamage)
    
    -- Apply weapon skill damage settings
    finalDamage = finalDamage * xi.settings.main.WEAPON_SKILL_POWER
    
    return 1, finalDamage, false, 0
end

return weaponskillObject
