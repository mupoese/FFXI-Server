-----------------------------------
-- Enhanced Weaponskill System for ITERATION 8
-- Improved damage calculations and retail accuracy
-----------------------------------
require('scripts/globals/weaponskills')
require('scripts/globals/combat/physical_utilities')

xi = xi or {}
xi.enhanced_weaponskills = xi.enhanced_weaponskills or {}

-- Enhanced fTP calculation with improved accuracy
xi.enhanced_weaponskills.calculateEnhancedFTP = function(tp, ftpTable, weaponSkill)
    if not ftpTable or tp < 1000 then
        return 1
    end

    -- Enhanced fTP with weapon-specific modifiers
    local baseFTP = xi.weaponskills.fTP(tp, ftpTable)
    
    -- Add weapon skill specific enhancements
    local wsModifier = 1.0
    if weaponSkill and weaponSkill.enhanced then
        wsModifier = 1 + (weaponSkill.enhanced / 100)
    end
    
    return baseFTP * wsModifier
end

-- Enhanced WSC calculation with modern scaling
xi.enhanced_weaponskills.calculateEnhancedWSC = function(attacker, str_wsc, dex_wsc, vit_wsc, agi_wsc, int_wsc, mnd_wsc, chr_wsc)
    local baseWSC = xi.combat.physical.calculateWSC(attacker, str_wsc, dex_wsc, vit_wsc, agi_wsc, int_wsc, mnd_wsc, chr_wsc)
    
    -- Enhanced WSC with job point bonuses
    local jpBonus = 0
    if attacker:isPC() then
        local mainJob = attacker:getMainJob()
        jpBonus = attacker:getJobPointLevel(xi.jp.WEAPONSKILL_DAMAGE) * 0.01
    end
    
    return baseWSC * (1 + jpBonus)
end

-- Enhanced weaponskill damage calculation
xi.enhanced_weaponskills.doEnhancedPhysicalWeaponskill = function(attacker, target, wsID, wsParams, tp, action, primaryMsg, taChar)
    -- Use enhanced calculations
    local originalFTP = wsParams.ftpMod
    local originalWSC = wsParams.str_wsc or 0
    
    -- Apply enhancements
    if not wsParams.enhanced then
        wsParams.enhanced = true
        wsParams.ftpMod = xi.enhanced_weaponskills.calculateEnhancedFTP(tp, originalFTP, wsParams)
    end
    
    -- Call original function with enhanced parameters
    return xi.weaponskills.doPhysicalWeaponskill(attacker, target, wsID, wsParams, tp, action, primaryMsg, taChar)
end

-- Auto-attack enhancement integration
xi.enhanced_weaponskills.processAutoAttack = function(attacker, target)
    local damage = 0
    local hitLanded = false
    
    -- Enhanced auto-attack calculation
    local weaponDamage = attacker:getWeaponDmg()
    local fSTR = xi.combat.physical.calculateMeleeStatFactor(attacker, target)
    local hitRate = xi.weaponskills.getHitRate(attacker, target, 0)
    
    if math.random() <= hitRate then
        hitLanded = true
        local pdif = xi.combat.physical.calculateMeleePDIF(attacker, target, attacker:getWeaponSkillType(xi.slot.MAIN), 1.0, false, true, false, 1.0, true, xi.slot.MAIN, false)
        damage = (weaponDamage + fSTR) * pdif
        
        -- Apply damage reductions
        damage = target:physicalDmgTaken(damage, attacker:getWeaponDamageType(xi.slot.MAIN))
        damage = math.max(0, damage - target:getMod(xi.mod.PHALANX))
    end
    
    return damage, hitLanded
end

print("Enhanced Weaponskill System loaded for ITERATION 8")
