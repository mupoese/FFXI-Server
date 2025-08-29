-----------------------------------
-- Enhanced Status Effect Management for Phase 3
-- Addresses missing status effect behaviors and retail accuracy
-- Enhances the status effect system for better Blue Magic and spell mechanics
-----------------------------------
require('scripts/globals/utils')
-----------------------------------
xi = xi or {}
xi.spells = xi.spells or {}
xi.spells.statusEffects = xi.spells.statusEffects or {}
-----------------------------------

-- Enhanced status effect duration calculations for retail accuracy
xi.spells.statusEffects.calculateEnhancedDuration = function(caster, target, baseEffect, baseDuration, element)
    local duration = baseDuration
    
    -- Enhancing Magic skill bonus for duration (Phase 3 improvement)
    if caster:isPC() then
        local enhancingSkill = caster:getSkillLevel(xi.skill.ENHANCING_MAGIC)
        if enhancingSkill > 0 then
            local skillBonus = math.floor(enhancingSkill / 100) * 5 -- 5% per 100 skill
            duration = duration + math.floor(baseDuration * skillBonus / 100)
        end
        
        -- Merit bonuses for enhancing magic duration
        if enhancingSkill > 300 then
            local meritBonus = caster:getMerit(xi.merit.ENHANCING_MAGIC_DURATION) or 0
            duration = duration + meritBonus
        end
    end
    
    -- Elemental day/weather bonuses for elemental status effects
    if element and element > 0 then
        local dayBonus = xi.spells.statusEffects.calculateElementalDayBonus(caster, element)
        local weatherBonus = xi.spells.statusEffects.calculateElementalWeatherBonus(caster, element)
        duration = math.floor(duration * (1 + dayBonus + weatherBonus))
    end
    
    -- Target resistance can reduce duration
    local targetResistance = xi.spells.statusEffects.calculateTargetResistance(target, baseEffect, element)
    duration = math.floor(duration * targetResistance)
    
    return math.max(duration, 1) -- Minimum 1 second duration
end

-- Calculate elemental day bonus for status effects
xi.spells.statusEffects.calculateElementalDayBonus = function(caster, element)
    local currentDay = VanadielDay()
    local elementData = xi.combat.element.dataTable[element]
    
    if not elementData then
        return 0
    end
    
    local strongDay = elementData[xi.combat.element.column.DAY_ASSOCIATED]
    local weakDay = xi.combat.element.dataTable[elementData[xi.combat.element.column.ELEMENT_OPPOSED]][xi.combat.element.column.DAY_ASSOCIATED]
    
    -- Check for elemental obi
    local hasObi = false
    if caster:isPC() then
        local waist = caster:getEquip(xi.slot.WAIST)
        local obiID = ({[xi.element.FIRE] = 15435, [xi.element.ICE] = 15436, [xi.element.WIND] = 15437, 
                       [xi.element.EARTH] = 15438, [xi.element.THUNDER] = 15439, [xi.element.WATER] = 15440,
                       [xi.element.LIGHT] = 15441, [xi.element.DARK] = 15442})[element]
        if waist and waist:getID() == obiID then
            hasObi = true
        end
    end
    
    if currentDay == strongDay and (hasObi or math.random(1, 100) <= 33) then
        return 0.1 -- 10% bonus duration
    elseif currentDay == weakDay and (hasObi or math.random(1, 100) <= 33) then
        return -0.1 -- 10% penalty duration
    end
    
    return 0
end

-- Calculate elemental weather bonus for status effects
xi.spells.statusEffects.calculateElementalWeatherBonus = function(caster, element)
    local currentWeather = caster:getWeather()
    local elementData = xi.combat.element.dataTable[element]
    
    if not elementData then
        return 0
    end
    
    local strongWeatherSingle = elementData[xi.combat.element.column.WEATHER_SINGLE]
    local strongWeatherDouble = elementData[xi.combat.element.column.WEATHER_DOUBLE]
    local weakWeatherSingle = xi.combat.element.dataTable[elementData[xi.combat.element.column.ELEMENT_OPPOSED]][xi.combat.element.column.WEATHER_SINGLE]
    local weakWeatherDouble = xi.combat.element.dataTable[elementData[xi.combat.element.column.ELEMENT_OPPOSED]][xi.combat.element.column.WEATHER_DOUBLE]
    
    -- Check for elemental obi
    local hasObi = false
    if caster:isPC() then
        local waist = caster:getEquip(xi.slot.WAIST)
        local obiID = ({[xi.element.FIRE] = 15435, [xi.element.ICE] = 15436, [xi.element.WIND] = 15437, 
                       [xi.element.EARTH] = 15438, [xi.element.THUNDER] = 15439, [xi.element.WATER] = 15440,
                       [xi.element.LIGHT] = 15441, [xi.element.DARK] = 15442})[element]
        if waist and waist:getID() == obiID then
            hasObi = true
        end
    end
    
    if currentWeather == strongWeatherSingle and (hasObi or math.random(1, 100) <= 33) then
        return 0.1 -- 10% bonus duration
    elseif currentWeather == strongWeatherDouble and (hasObi or math.random(1, 100) <= 33) then
        return 0.25 -- 25% bonus duration  
    elseif currentWeather == weakWeatherSingle and (hasObi or math.random(1, 100) <= 33) then
        return -0.1 -- 10% penalty duration
    elseif currentWeather == weakWeatherDouble and (hasObi or math.random(1, 100) <= 33) then
        return -0.25 -- 25% penalty duration
    end
    
    return 0
end

-- Calculate target resistance to status effects
xi.spells.statusEffects.calculateTargetResistance = function(target, effect, element)
    local resistance = 1.0
    
    -- Base resistance based on level difference (retail accurate)
    if target:isNM() then
        resistance = resistance * 0.5 -- NMs are more resistant
    elseif target:isMob() then
        resistance = resistance * 0.75 -- Regular mobs have some resistance
    end
    
    -- Elemental resistance affects elemental status effects
    if element and element > 0 then
        local elementData = xi.combat.element.dataTable[element]
        if elementData then
            local resistMod = elementData[xi.combat.element.column.MOD_ELEMENT_MEVA]
            local elementResist = target:getMod(resistMod)
            resistance = resistance * (1 - elementResist / 1000) -- Convert to decimal
        end
    end
    
    -- Status effect specific resistances
    local statusResistMods = {
        [xi.effect.SLEEP] = xi.mod.SLEEP_RES,
        [xi.effect.SILENCE] = xi.mod.SILENCE_RES,
        [xi.effect.PARALYSIS] = xi.mod.PARALYZE_RES,
        [xi.effect.BIND] = xi.mod.BIND_RES,
        [xi.effect.SLOW] = xi.mod.SLOW_RES,
        [xi.effect.POISON] = xi.mod.POISON_RES,
        [xi.effect.BLINDNESS] = xi.mod.BLIND_RES,
        [xi.effect.STUN] = xi.mod.STUN_RES,
    }
    
    if statusResistMods[effect] then
        local statusResist = target:getMod(statusResistMods[effect])
        resistance = resistance * (1 - statusResist / 1000)
    end
    
    return math.max(resistance, 0.1) -- Minimum 10% effectiveness
end

-- Enhanced status effect stacking for retail accuracy
xi.spells.statusEffects.handleStatusEffectStacking = function(target, effect, power, duration, element)
    local currentEffect = target:getStatusEffect(effect)
    
    if currentEffect then
        -- Some effects can stack (like Poison), others overwrite
        local stackableEffects = {
            [xi.effect.POISON] = true,
            [xi.effect.BIO] = true,
            [xi.effect.DIA] = true,
        }
        
        if stackableEffects[effect] then
            -- For stackable effects, add a new instance with reduced potency
            local stackPower = math.floor(power * 0.5) -- 50% power for stacked effects
            target:addStatusEffect(effect, stackPower, 0, duration)
            return true
        else
            -- For non-stackable effects, only overwrite if new effect is stronger
            if power > currentEffect:getPower() or duration > currentEffect:getDuration() then
                target:delStatusEffect(effect)
                target:addStatusEffect(effect, power, 0, duration)
                return true
            end
            return false -- Effect was not applied
        end
    else
        -- No existing effect, apply normally
        target:addStatusEffect(effect, power, 0, duration)
        return true
    end
end

-- Enhanced Blue Magic trait implementation for retail accuracy
xi.spells.statusEffects.applyBlueMagicTraits = function(caster, target, spell, params)
    if not caster:isPC() or caster:getMainJob() ~= xi.job.BLU then
        return
    end
    
    -- Check for relevant Blue Magic traits
    local traits = {
        -- Auto-Refresh trait from certain blue spells
        AUTO_REFRESH = function()
            if caster:getTraitLevel(xi.trait.AUTO_REFRESH) > 0 then
                local refreshPower = caster:getTraitLevel(xi.trait.AUTO_REFRESH)
                if not caster:hasStatusEffect(xi.effect.REFRESH) then
                    caster:addStatusEffect(xi.effect.REFRESH, refreshPower, 3, 0) -- Permanent refresh
                end
            end
        end,
        
        -- Auto-Regen trait from certain blue spells  
        AUTO_REGEN = function()
            if caster:getTraitLevel(xi.trait.AUTO_REGEN) > 0 then
                local regenPower = caster:getTraitLevel(xi.trait.AUTO_REGEN)
                if not caster:hasStatusEffect(xi.effect.REGEN) then
                    caster:addStatusEffect(xi.effect.REGEN, regenPower, 3, 0) -- Permanent regen
                end
            end
        end,
        
        -- Resist status traits
        RESIST_SLEEP = function()
            if caster:getTraitLevel(xi.trait.RESIST_SLEEP) > 0 then
                caster:addMod(xi.mod.SLEEP_RES, caster:getTraitLevel(xi.trait.RESIST_SLEEP) * 25)
            end
        end,
    }
    
    -- Apply all relevant traits
    for traitName, traitFunc in pairs(traits) do
        traitFunc()
    end
end

return xi.spells.statusEffects