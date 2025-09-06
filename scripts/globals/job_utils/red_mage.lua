-----------------------------------
-- Red Mage Job Utilities
-----------------------------------
require('scripts/globals/utils')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.red_mage = xi.job_utils.red_mage or {}

-----------------------------------
-- Ability Check Functions
-----------------------------------
xi.job_utils.red_mage.checkChainspell = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.red_mage.checkStymie = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

-----------------------------------
-- Ability Use Functions
-----------------------------------
xi.job_utils.red_mage.useChainspell = function(player, target, ability)
    player:addStatusEffect(xi.effect.CHAINSPELL, 1, 0, 60)
end

xi.job_utils.red_mage.useComposure = function(player, target, ability)
    player:delStatusEffect(xi.effect.COMPOSURE)
    
    -- Enhanced Composure with accuracy bonuses and enspell improvements
    local jpLevel = player:getJobPointLevel(xi.jp.COMPOSURE_EFFECT) or 0
    local merit = player:getMerit(xi.merit.COMPOSURE_EFFECT) or 0
    
    -- Power determines accuracy bonus and enspell enhancement
    local power = 1 + jpLevel + merit
    
    player:addStatusEffect(xi.effect.COMPOSURE, power, 0, 7200)
end

xi.job_utils.red_mage.useConvert = function(player, target, ability)
    local playerMP    = player:getMP()
    local playerHP    = player:getHP()
    local playerMaxHP = player:getMaxHP()

    -- HP bonuses
    local jpExtraHP       = math.floor(playerMaxHP * player:getJobPointLevel(xi.jp.CONVERT_EFFECT) / 100)
    local murgleisExtraHP = 0

    if player:getMod(xi.mod.AUGMENTS_CONVERT) > 0 then
        murgleisExtraHP = math.floor(playerMaxHP * player:getMod(xi.mod.AUGMENTS_CONVERT) / 100)
    end

    if playerMP > 0 then -- Safety check, not really needed.
        player:setHP(playerMP + jpExtraHP + murgleisExtraHP)
        player:setMP(playerHP)
    end
end

xi.job_utils.red_mage.useSaboteur = function(player, target, ability)
    player:addStatusEffect(xi.effect.SABOTEUR, 1, 0, 60)
end

xi.job_utils.red_mage.useSpontaneity = function(player, target, ability)
    target:addStatusEffect(xi.effect.SPONTANEITY, 1, 0, 60)
end

xi.job_utils.red_mage.useStymie = function(player, target, ability)
    target:addStatusEffect(xi.effect.STYMIE, 1, 0, 60)
end

-----------------------------------
-- Enhanced Enspell System
-----------------------------------

-- Enspell damage calculation
xi.job_utils.red_mage.calculateEnspellDamage = function(player, target, element)
    local skill = player:getSkillLevel(xi.skill.ENHANCING_MAGIC)
    local mab = player:getMod(xi.mod.MATT)
    local jpBonus = player:getJobPointLevel(xi.jp.ENSPELL_DAMAGE) or 0
    
    -- Base damage calculation
    local baseDamage = math.floor(skill / 3) + math.floor(mab / 5) + jpBonus
    
    -- Composure enhancement
    if player:hasStatusEffect(xi.effect.COMPOSURE) then
        local composurePower = player:getStatusEffect(xi.effect.COMPOSURE):getPower()
        baseDamage = baseDamage + math.floor(baseDamage * (composurePower * 0.1))
    end
    
    -- Element-specific bonuses
    local elementalMod = player:getMod(element) or 0
    baseDamage = baseDamage + elementalMod
    
    -- Apply level correction
    local levelCorrection = 1.0
    if target:getMainLvl() > player:getMainLvl() then
        levelCorrection = 0.8 + (player:getMainLvl() / target:getMainLvl()) * 0.2
    end
    
    return math.floor(baseDamage * levelCorrection)
end

-- Enhanced enspell proc handling
xi.job_utils.red_mage.handleEnspellProc = function(attacker, target, damage)
    if attacker:getMainJob() ~= xi.job.RDM and attacker:getSubJob() ~= xi.job.RDM then
        return 0
    end
    
    local enspellEffect = nil
    local element = nil
    
    -- Check for active enspells
    if attacker:hasStatusEffect(xi.effect.ENFIRE) then
        enspellEffect = xi.effect.ENFIRE
        element = xi.mod.FIRE_AFFINITY_DMG
    elseif attacker:hasStatusEffect(xi.effect.ENBLIZZARD) then
        enspellEffect = xi.effect.ENBLIZZARD
        element = xi.mod.ICE_AFFINITY_DMG
    elseif attacker:hasStatusEffect(xi.effect.ENAERO) then
        enspellEffect = xi.effect.ENAERO
        element = xi.mod.WIND_AFFINITY_DMG
    elseif attacker:hasStatusEffect(xi.effect.ENSTONE) then
        enspellEffect = xi.effect.ENSTONE
        element = xi.mod.EARTH_AFFINITY_DMG
    elseif attacker:hasStatusEffect(xi.effect.ENTHUNDER) then
        enspellEffect = xi.effect.ENTHUNDER
        element = xi.mod.THUNDER_AFFINITY_DMG
    elseif attacker:hasStatusEffect(xi.effect.ENWATER) then
        enspellEffect = xi.effect.ENWATER
        element = xi.mod.WATER_AFFINITY_DMG
    end
    
    if not enspellEffect or not element then
        return 0
    end
    
    -- Calculate proc chance (base 100% for melee attacks)
    local procChance = 1.0
    
    -- Composure increases proc rate and damage
    if attacker:hasStatusEffect(xi.effect.COMPOSURE) then
        local composurePower = attacker:getStatusEffect(xi.effect.COMPOSURE):getPower()
        procChance = procChance + (composurePower * 0.05) -- 5% increase per composure level
    end
    
    if math.random() < procChance then
        local enspellDamage = xi.job_utils.red_mage.calculateEnspellDamage(attacker, target, element)
        
        -- Apply target's resistance
        local resistance = target:getMod(element + 54) -- Resistance modifier offset
        enspellDamage = math.floor(enspellDamage * (1.0 - resistance / 100))
        
        if enspellDamage > 0 then
            target:takeDamage(enspellDamage, attacker, xi.attackType.MAGICAL, xi.damageType.ELEMENTAL)
            target:updateEnmityFromDamage(attacker, enspellDamage)
            
            return enspellDamage
        end
    end
    
    return 0
end

-- Enhancing magic potency calculation for Red Mage
xi.job_utils.red_mage.getEnhancingPotency = function(player, spellId)
    local skill = player:getSkillLevel(xi.skill.ENHANCING_MAGIC)
    local composureBonus = 0
    
    if player:hasStatusEffect(xi.effect.COMPOSURE) then
        local composurePower = player:getStatusEffect(xi.effect.COMPOSURE):getPower()
        composureBonus = composurePower * 5 -- 5% potency increase per composure level
    end
    
    -- Job Point bonuses
    local jpBonus = player:getJobPointLevel(xi.jp.ENHANCING_MAGIC_EFFECT) or 0
    
    return skill + composureBonus + jpBonus
end
