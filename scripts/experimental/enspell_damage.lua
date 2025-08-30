-----------------------------------
-- Enspell Damage Utilities
-- Used for calculating enspell additional effect damage (Enfire, Enstone, etc.)
-- Replaces C++ CalculateEnspellDamage function for better maintainability
-----------------------------------
require('scripts/globals/combat/element_tables')
require('scripts/globals/magic')
require('scripts/globals/utils')
-----------------------------------
xi = xi or {}
xi.spells = xi.spells or {}
xi.spells.enspell = xi.spells.enspell or {}
-----------------------------------

-- Enspell tier definitions
local ENSPELL_TIER = 
{
    TIER_1 = 1, -- Basic enspells (Enfire, Enblizzard, etc.)
    TIER_2 = 2, -- Enhanced enspells (Enfire II, Enblizzard II, etc.)
    TIER_3 = 3, -- Enlight/Endark
    TIER_4 = 4, -- Rune Enhancement
}

-- Obi item IDs for elemental bonuses
local ELEMENTAL_OBI = 
{
    [xi.element.FIRE]    = 15435,
    [xi.element.ICE]     = 15436,
    [xi.element.WIND]    = 15437,
    [xi.element.EARTH]   = 15438,
    [xi.element.THUNDER] = 15439,
    [xi.element.WATER]   = 15440,
    [xi.element.LIGHT]   = 15441,
    [xi.element.DARK]    = 15442,
}

-----------------------------------
-- Local Helper Functions
-----------------------------------

-- Calculate equipment bonus for enspell damage, excluding the weapon hit
local function calculateEquipmentBonus(attacker, weaponHit)
    local totalMod = attacker:getMod(xi.mod.ENSPELL_DMG_BONUS)
    local exclude = 0
    
    if attacker:isPC() then
        local slots = { xi.slot.MAIN, xi.slot.SUB }
        for _, slot in ipairs(slots) do
            local equipment = attacker:getEquip(slot)
            if equipment and equipment ~= weaponHit then
                exclude = exclude + equipment:getModifier(xi.mod.ENSPELL_DMG_BONUS)
            end
        end
    end
    
    return totalMod - exclude
end

-- Calculate day and weather bonuses for elemental damage
local function calculateElementalBonus(attacker, element)
    local bonus = 1.0
    local hasObi = false
    
    -- Check for elemental obi equipment
    if attacker:isPC() then
        local waist = attacker:getEquip(xi.slot.WAIST)
        if waist and waist:getID() == ELEMENTAL_OBI[element] then
            hasObi = true
        end
    else
        -- Mobs get random multiplier
        bonus = bonus + math.random(0, 100) / 1000.0
    end
    
    -- Get current day and weather from element tables
    local elementData = xi.combat.element.dataTable[element]
    if not elementData then
        return bonus
    end
    
    local strongDay = elementData[xi.combat.element.column.DAY_ASSOCIATED]
    local weakDay = xi.combat.element.dataTable[elementData[xi.combat.element.column.ELEMENT_OPPOSED]][xi.combat.element.column.DAY_ASSOCIATED]
    local strongWeatherSingle = elementData[xi.combat.element.column.WEATHER_SINGLE]
    local strongWeatherDouble = elementData[xi.combat.element.column.WEATHER_DOUBLE]
    local weakWeatherSingle = xi.combat.element.dataTable[elementData[xi.combat.element.column.ELEMENT_OPPOSED]][xi.combat.element.column.WEATHER_SINGLE]
    local weakWeatherDouble = xi.combat.element.dataTable[elementData[xi.combat.element.column.ELEMENT_OPPOSED]][xi.combat.element.column.WEATHER_DOUBLE]
    
    local currentDay = VanadielDay()
    local currentWeather = attacker:getWeather()
    
    -- Day bonuses (10% bonus/penalty)
    if currentDay == strongDay and (hasObi or math.random(1, 100) <= 33) then
        bonus = bonus + 0.1
    elseif currentDay == weakDay and (hasObi or math.random(1, 100) <= 33) then
        bonus = bonus - 0.1
    end
    
    -- Weather bonuses
    if currentWeather == strongWeatherSingle and (hasObi or math.random(1, 100) <= 33) then
        bonus = bonus + 0.1
    elseif currentWeather == strongWeatherDouble and (hasObi or math.random(1, 100) <= 33) then
        bonus = bonus + 0.25
    elseif currentWeather == weakWeatherSingle and (hasObi or math.random(1, 100) <= 33) then
        bonus = bonus - 0.1
    elseif currentWeather == weakWeatherDouble and (hasObi or math.random(1, 100) <= 33) then
        bonus = bonus - 0.25
    end
    
    return bonus
end

-- Calculate magical resistance for enspell damage
local function calculateMagicalResistance(defender, element)
    local elementData = xi.combat.element.dataTable[element]
    if not elementData then
        return 1.0
    end
    
    local resistMod = elementData[xi.combat.element.column.MOD_ELEMENT_MEVA]
    local resistValue = defender:getMod(resistMod) / 100.0
    
    -- Calculate resistance tiers based on random roll
    local resistRoll = math.random()
    local half = resistValue
    local quarter = half * half
    local eighth = half * half * half
    local sixteenth = half * half * half * half
    
    if resistRoll <= sixteenth then
        return 0.0625 -- 1/16 resistance
    elseif resistRoll <= eighth then
        return 0.125  -- 1/8 resistance
    elseif resistRoll <= quarter then
        return 0.25   -- 1/4 resistance
    elseif resistRoll <= half then
        return 0.5    -- 1/2 resistance
    else
        return 1.0    -- No resistance
    end
end

-----------------------------------
-- Tier-Specific Damage Calculations
-----------------------------------

-- Calculate Tier 1 enspell damage (basic enspells)
local function calculateTier1Damage(attacker, equipBonus)
    local damage = attacker:getMod(xi.mod.ENSPELL_DMG) + equipBonus
    
    -- Add merit bonus for players
    if attacker:isPC() then
        damage = damage + attacker:getMerit(xi.merit.ENSPELL_DAMAGE)
    end
    
    return damage
end

-- Calculate Tier 2 enspell damage (enhanced enspells)
local function calculateTier2Damage(attacker, equipBonus)
    local skill = attacker:getSkillLevel(xi.skill.ENHANCING_MAGIC)
    local cap = 3 + 6 * skill / 100
    
    if skill > 200 then
        cap = 5 + 5 * skill / 100
    end
    cap = cap * 2
    
    local currentDamage = attacker:getMod(xi.mod.ENSPELL_DMG)
    local damage = 0
    
    if currentDamage > cap then
        attacker:setMod(xi.mod.ENSPELL_DMG, cap)
        damage = cap
    elseif currentDamage == cap then
        damage = cap
    else -- currentDamage < cap
        attacker:addMod(xi.mod.ENSPELL_DMG, 1)
        damage = currentDamage
    end
    
    damage = damage + equipBonus
    
    -- Add enhanced merit bonus for players (doubled for Tier 2)
    if attacker:isPC() then
        damage = damage + attacker:getMerit(xi.merit.ENSPELL_DAMAGE) * 2
    end
    
    return damage
end

-- Calculate Tier 3 enspell damage (Enlight/Endark)
local function calculateTier3Damage(attacker, element, equipBonus)
    local damage = attacker:getMod(xi.mod.ENSPELL_DMG)
    
    if damage > 1 then
        attacker:delMod(xi.mod.ENSPELL_DMG, 1)
    else
        -- Remove the enspell effect when charges are depleted
        if element == xi.element.DARK then
            attacker:delStatusEffect(xi.effect.ENDARK)
        else
            attacker:delStatusEffect(xi.effect.ENLIGHT)
        end
    end
    
    return damage + equipBonus
end

-- Calculate Tier 4 enspell damage (Rune Enhancement)
local function calculateTier4Damage(attacker, equipBonus)
    local weapon = attacker:getEquip(xi.slot.MAIN)
    local runeDPS = 0.0
    
    if not weapon then
        -- Hand-to-hand base DPS
        runeDPS = 3.0 / 240.0
    else
        runeDPS = weapon:getDPS()
    end
    
    -- Adjust for dual wield
    if attacker:isDualWielding() then
        runeDPS = runeDPS / 2
    end
    
    -- Cap DPS at known maximum
    runeDPS = math.min(21, runeDPS)
    
    -- Get rune count and calculate damage range
    local highestRuneEffect = attacker:getHighestRuneEffect()
    local runeCount = attacker:getStatusEffectCount(highestRuneEffect)
    
    local minDamage = 0
    local maxDamage = 0
    
    if runeCount == 1 then
        minDamage = math.floor(runeDPS * 0.97)
        maxDamage = math.floor(runeDPS * 1.30)
    elseif runeCount == 2 then
        minDamage = math.floor(runeDPS * 1.40)
        maxDamage = math.floor(runeDPS * 1.70)
    elseif runeCount == 3 then
        minDamage = math.floor(runeDPS * 1.90)
        maxDamage = math.floor(runeDPS * 2.20)
    end
    
    if maxDamage == 0 then
        return 0
    end
    
    -- Random damage within range (inclusive of max)
    return math.random(minDamage, maxDamage)
end

-----------------------------------
-- Main Enspell Damage Function
-----------------------------------

xi.spells.enspell.calculateDamage = function(attacker, defender, tier, element, weaponHit)
    if not attacker or not defender then
        return 0
    end
    
    local damage = 0
    local equipBonus = calculateEquipmentBonus(attacker, weaponHit)
    
    -- Calculate base damage based on tier
    if tier == ENSPELL_TIER.TIER_1 then
        damage = calculateTier1Damage(attacker, equipBonus)
    elseif tier == ENSPELL_TIER.TIER_2 then
        damage = calculateTier2Damage(attacker, equipBonus)
    elseif tier == ENSPELL_TIER.TIER_3 then
        damage = calculateTier3Damage(attacker, element, equipBonus)
    elseif tier == ENSPELL_TIER.TIER_4 then
        damage = calculateTier4Damage(attacker, equipBonus)
    else
        return 0
    end
    
    -- Apply elemental bonuses (day/weather)
    local elementalBonus = calculateElementalBonus(attacker, element)
    damage = math.floor(damage * elementalBonus)
    
    -- Apply magical resistance
    local resistance = calculateMagicalResistance(defender, element)
    damage = math.floor(damage * resistance)
    
    -- Apply magic damage taken calculations
    damage = xi.magic.calculateMagicDamageTaken(defender, damage, element)
    
    -- Apply final damage reductions (Phalanx, Stoneskin, etc.)
    if damage > 0 then
        damage = math.max(damage - defender:getMod(xi.mod.PHALANX), 0)
        damage = xi.magic.handleOneForAll(defender, damage)
        damage = xi.magic.handleStoneskin(defender, damage)
    end
    
    -- Clamp damage to valid range
    damage = utils.clamp(damage, -99999, 99999)
    
    return damage
end

-----------------------------------
-- Convenience Functions for Different Enspell Types
-----------------------------------

xi.spells.enspell.calculateBasicEnspellDamage = function(attacker, defender, element, weaponHit)
    return xi.spells.enspell.calculateDamage(attacker, defender, ENSPELL_TIER.TIER_1, element, weaponHit)
end

xi.spells.enspell.calculateEnhancedEnspellDamage = function(attacker, defender, element, weaponHit)
    return xi.spells.enspell.calculateDamage(attacker, defender, ENSPELL_TIER.TIER_2, element, weaponHit)
end

xi.spells.enspell.calculateEnlightEndarkDamage = function(attacker, defender, element, weaponHit)
    return xi.spells.enspell.calculateDamage(attacker, defender, ENSPELL_TIER.TIER_3, element, weaponHit)
end

xi.spells.enspell.calculateRuneEnhancementDamage = function(attacker, defender, element, weaponHit)
    return xi.spells.enspell.calculateDamage(attacker, defender, ENSPELL_TIER.TIER_4, element, weaponHit)
end

return xi.spells.enspell
