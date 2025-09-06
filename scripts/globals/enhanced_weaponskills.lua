-----------------------------------
-- Enhanced Weaponskill System
-- Improved damage calculations and retail accuracy
-- Part of Iteration 7: Job System Excellence
-----------------------------------
require('scripts/globals/weaponskills')
require('scripts/globals/combat/physical_utilities')
require('scripts/globals/magic')
-----------------------------------
xi = xi or {}
xi.weaponskills = xi.weaponskills or {}
xi.weaponskills.enhanced = {}

-----------------------------------
-- Enhanced Weaponskill Constants
-----------------------------------

-- Weaponskill attribute modifiers (WSC)
local wscModifiers = {
    NONE = 0.0,
    LOW  = 0.2,  -- 20%
    MED  = 0.3,  -- 30%
    HIGH = 0.5,  -- 50%
    VERY_HIGH = 0.85, -- 85%
}

-- TP modifier types
local tpModTypes = {
    NONE = 0,
    CRITICAL = 1,    -- Critical hit rate varies with TP
    ACCURACY = 2,    -- Accuracy varies with TP
    ATTACK = 3,      -- Attack varies with TP
    DAMAGE = 4,      -- Damage varies with TP
    DURATION = 5,    -- Additional effect duration varies with TP
}

-----------------------------------
-- Enhanced Damage Calculation Functions
-----------------------------------

-- Calculate enhanced fSTR with level correction
function xi.weaponskills.enhanced.calculateFSTR(attacker, target, weaponType)
    local attackerSTR = attacker:getStat(xi.mod.STR)
    local targetVIT = target:getStat(xi.mod.VIT)
    local strDiff = attackerSTR - targetVIT
    
    -- Base fSTR calculation
    local fSTR = 0
    if strDiff >= 12 then
        fSTR = (strDiff + 4) / 4
    elseif strDiff >= 6 then
        fSTR = (strDiff + 6) / 4
    elseif strDiff >= 1 then
        fSTR = (strDiff + 7) / 4
    elseif strDiff >= -2 then
        fSTR = (strDiff + 8) / 4
    elseif strDiff >= -7 then
        fSTR = (strDiff + 9) / 4
    elseif strDiff >= -15 then
        fSTR = (strDiff + 10) / 4
    elseif strDiff >= -21 then
        fSTR = (strDiff + 12) / 4
    else
        fSTR = (strDiff + 13) / 4
    end
    
    -- Apply weapon-specific fSTR caps
    local fSTRCap = 22 -- Default cap
    if weaponType == xi.skill.HAND_TO_HAND then
        fSTRCap = 24
    elseif weaponType == xi.skill.GREAT_SWORD or weaponType == xi.skill.GREAT_AXE then
        fSTRCap = 26
    end
    
    return math.max(-21, math.min(fSTR, fSTRCap))
end

-- Enhanced WSC calculation with job-specific bonuses
function xi.weaponskills.enhanced.calculateWSC(attacker, params)
    local totalWSC = 0
    
    -- Calculate base WSC
    if params.str_wsc then
        totalWSC = totalWSC + attacker:getStat(xi.mod.STR) * params.str_wsc
    end
    if params.dex_wsc then
        totalWSC = totalWSC + attacker:getStat(xi.mod.DEX) * params.dex_wsc
    end
    if params.vit_wsc then
        totalWSC = totalWSC + attacker:getStat(xi.mod.VIT) * params.vit_wsc
    end
    if params.agi_wsc then
        totalWSC = totalWSC + attacker:getStat(xi.mod.AGI) * params.agi_wsc
    end
    if params.int_wsc then
        totalWSC = totalWSC + attacker:getStat(xi.mod.INT) * params.int_wsc
    end
    if params.mnd_wsc then
        totalWSC = totalWSC + attacker:getStat(xi.mod.MND) * params.mnd_wsc
    end
    if params.chr_wsc then
        totalWSC = totalWSC + attacker:getStat(xi.mod.CHR) * params.chr_wsc
    end
    
    -- Apply alpha (level-dependent modifier)
    local alpha = xi.weaponskills.enhanced.calculateAlpha(attacker:getMainLvl())
    totalWSC = totalWSC * alpha
    
    -- Job-specific WSC bonuses
    local jobBonus = 0
    if attacker:getMainJob() == xi.job.WAR then
        jobBonus = attacker:getJobPointLevel(xi.jp.WEAPON_SKILL_DAMAGE_BONUS) or 0
    elseif attacker:getMainJob() == xi.job.SAM then
        -- Samurai gets bonus WSC from Meikyo Shisui
        if attacker:hasStatusEffect(xi.effect.MEIKYO_SHISUI) then
            jobBonus = jobBonus + 10
        end
    end
    
    return math.floor(totalWSC + jobBonus)
end

-- Enhanced alpha calculation
function xi.weaponskills.enhanced.calculateAlpha(level)
    if level < 10 then
        return 1.0
    elseif level < 60 then
        return 1.0 - (level - 10) / 200  -- Gradual decrease
    elseif level <= 75 then
        return 0.75 - (level - 60) / 120  -- Further decrease
    else
        return 0.625 + (level - 75) / 400  -- Slight increase at higher levels, cap at ~0.83
    end
end

-- Enhanced TP modifier calculation
function xi.weaponskills.enhanced.calculateTPMultiplier(tp, tpModType, tpMod1, tpMod2, tpMod3)
    local tpMultiplier = 1.0
    local tpLevel = 1
    
    if tp >= 2000 then
        tpLevel = 2
        local tpOverflow = (tp - 2000) / 1000
        tpMultiplier = tpMod2 + (tpMod3 - tpMod2) * tpOverflow
    elseif tp >= 1000 then
        tpLevel = 1
        local tpOverflow = (tp - 1000) / 1000
        tpMultiplier = tpMod1 + (tpMod2 - tpMod1) * tpOverflow
    else
        tpMultiplier = tpMod1 * (tp / 1000)
    end
    
    return tpMultiplier, tpLevel
end

-- Enhanced critical hit calculation
function xi.weaponskills.enhanced.calculateCriticalHit(attacker, target, params, tp)
    local baseCritRate = attacker:getMod(xi.mod.CRITHITRATE) / 100
    local wsSpecificCrit = 0
    
    -- TP-based critical hit rate modification
    if params.tpmod_crit then
        local tpMod, tpLevel = xi.weaponskills.enhanced.calculateTPMultiplier(
            tp, tpModTypes.CRITICAL, 
            params.tpmod_crit[1] or 0, 
            params.tpmod_crit[2] or 0, 
            params.tpmod_crit[3] or 0
        )
        wsSpecificCrit = tpMod
    end
    
    -- Job-specific critical hit bonuses
    local jobCritBonus = 0
    if attacker:getMainJob() == xi.job.THF and attacker:isBehind(target) then
        jobCritBonus = jobCritBonus + 0.05 -- 5% bonus for back attacks
    end
    
    -- Equipment and merit bonuses
    local equipCrit = attacker:getMod(xi.mod.WEAPONSKILL_CRIT_RATE) / 100
    
    local totalCritRate = baseCritRate + wsSpecificCrit + jobCritBonus + equipCrit
    return math.min(totalCritRate, 1.0) -- Cap at 100%
end

-- Enhanced accuracy calculation
function xi.weaponskills.enhanced.calculateAccuracy(attacker, target, params, tp, weaponType)
    local baseAccuracy = attacker:getACC()
    local wsAccuracyMod = 0
    
    -- TP-based accuracy modification
    if params.tpmod_acc then
        local tpMod, tpLevel = xi.weaponskills.enhanced.calculateTPMultiplier(
            tp, tpModTypes.ACCURACY,
            params.tpmod_acc[1] or 0,
            params.tpmod_acc[2] or 0,
            params.tpmod_acc[3] or 0
        )
        wsAccuracyMod = tpMod
    end
    
    -- Weaponskill-specific accuracy bonus
    local wsInherentAcc = params.acc_bonus or 0
    
    -- Job-specific accuracy bonuses
    local jobAccBonus = 0
    if attacker:getMainJob() == xi.job.RNG then
        jobAccBonus = attacker:getJobPointLevel(xi.jp.SNAPSHOT_EFFECT) or 0
    elseif attacker:getMainJob() == xi.job.DNC then
        -- Dancers get accuracy bonus with flourishes active
        if attacker:hasStatusEffect(xi.effect.BUILDING_FLOURISH) then
            jobAccBonus = jobAccBonus + attacker:getStatusEffect(xi.effect.BUILDING_FLOURISH):getPower() * 5
        end
    end
    
    return baseAccuracy + wsAccuracyMod + wsInherentAcc + jobAccBonus
end

-----------------------------------
-- Enhanced Weaponskill Execution
-----------------------------------

function xi.weaponskills.enhanced.doPhysicalWeaponskill(attacker, target, wsid, params, tp, action, primaryMsg)
    -- Get weapon information
    local weaponType = attacker:getWeaponSkillType(xi.slot.MAIN)
    local weaponDamage = attacker:getWeaponDmg()
    
    -- Calculate enhanced components
    local fSTR = xi.weaponskills.enhanced.calculateFSTR(attacker, target, weaponType)
    local wsc = xi.weaponskills.enhanced.calculateWSC(attacker, params)
    local accuracy = xi.weaponskills.enhanced.calculateAccuracy(attacker, target, params, tp, weaponType)
    local critRate = xi.weaponskills.enhanced.calculateCriticalHit(attacker, target, params, tp)
    
    -- Calculate TP multipliers
    local damageTPMod = 1.0
    if params.tpmod_damage then
        damageTPMod = xi.weaponskills.enhanced.calculateTPMultiplier(
            tp, tpModTypes.DAMAGE,
            params.tpmod_damage[1] or 1.0,
            params.tpmod_damage[2] or 1.0,
            params.tpmod_damage[3] or 1.0
        )
    end
    
    -- Calculate base damage
    local baseDamage = weaponDamage + fSTR + wsc
    
    -- Apply damage multiplier
    local finalDamage = math.floor(baseDamage * damageTPMod * (params.damage_multiplier or 1.0))
    
    -- Apply critical hit if it occurs
    local isCritical = math.random() < critRate
    if isCritical then
        finalDamage = math.floor(finalDamage * 1.25) -- 25% critical bonus
    end
    
    -- Apply level correction
    local levelCorrection = xi.combat.levelCorrection.calculateCorrection(attacker:getMainLvl(), target:getMainLvl())
    finalDamage = math.floor(finalDamage * levelCorrection)
    
    -- Handle multiple hits
    local hitCount = params.num_hits or 1
    local totalDamage = 0
    local hitLanded = false
    
    for i = 1, hitCount do
        local hitAccuracy = accuracy
        if i > 1 then
            hitAccuracy = hitAccuracy * 0.9 -- Subsequent hits have reduced accuracy
        end
        
        if math.random() <= xi.weaponskills.getHitRate(attacker, target, hitAccuracy) then
            local hitDamage = finalDamage
            if i > 1 then
                hitDamage = math.floor(hitDamage * 0.85) -- Subsequent hits do less damage
            end
            
            -- Apply target's damage reduction
            hitDamage = utils.stoneskin(target, hitDamage)
            target:takeDamage(hitDamage, attacker, xi.attackType.PHYSICAL, attacker:getWeaponDamageType(xi.slot.MAIN))
            target:updateEnmityFromDamage(attacker, hitDamage)
            
            totalDamage = totalDamage + hitDamage
            hitLanded = true
        end
    end
    
    -- Handle additional effects
    if hitLanded and params.additional_effect then
        params.additional_effect(attacker, target, wsid, params, finalDamage)
    end
    
    -- Set action message
    if hitLanded then
        action:setMsg(primaryMsg or xi.msg.basic.USES_WS_DEALS_DAMAGE)
    else
        action:setMsg(xi.msg.basic.USES_WS_MISSES)
    end
    
    return totalDamage
end

-----------------------------------
-- Weaponskill Enhancement Integration
-----------------------------------

-- Enhanced weaponskill damage for specific jobs
function xi.weaponskills.enhanced.applyJobEnhancements(attacker, target, wsid, baseDamage)
    local enhancedDamage = baseDamage
    local mainJob = attacker:getMainJob()
    
    -- Warrior enhancements
    if mainJob == xi.job.WAR then
        local berserkerLevel = attacker:getJobPointLevel(xi.jp.BERSERK_EFFECT) or 0
        if attacker:hasStatusEffect(xi.effect.BERSERK) then
            enhancedDamage = enhancedDamage + math.floor(baseDamage * (berserkerLevel * 0.01))
        end
    end
    
    -- Dark Knight enhancements
    if mainJob == xi.job.DRK then
        if attacker:hasStatusEffect(xi.effect.LAST_RESORT) then
            local lastResortBonus = attacker:getJobPointLevel(xi.jp.LAST_RESORT_EFFECT) or 0
            enhancedDamage = enhancedDamage + math.floor(baseDamage * (0.1 + lastResortBonus * 0.01))
        end
    end
    
    -- Samurai enhancements  
    if mainJob == xi.job.SAM then
        local hassoEffect = attacker:hasStatusEffect(xi.effect.HASSO)
        if hassoEffect then
            enhancedDamage = enhancedDamage + math.floor(baseDamage * 0.1) -- 10% bonus
        end
    end
    
    return enhancedDamage
end

return xi.weaponskills.enhanced