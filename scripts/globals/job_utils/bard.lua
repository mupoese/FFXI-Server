-----------------------------------
-- Bard Job Utilities
-----------------------------------
require('scripts/globals/utils')
require('scripts/globals/jobpoints')
-----------------------------------
xi = xi or {}
xi.job_utils = xi.job_utils or {}
xi.job_utils.bard = xi.job_utils.bard or {}

-----------------------------------
-- Song Enhancement Functions with Merit Integration
-----------------------------------
function getSongDuration(player)
    local duration = 120 -- Base song duration
    duration = duration + player:getMod(xi.mod.SONG_DURATION_BONUS)
    duration = duration + player:getJobPointLevel(xi.jp.SONG_DURATION_BONUS)
    return duration
end

function getSongRange(player)
    local range = 10 -- Base song range
    range = range + player:getMod(xi.mod.SONG_RANGE_BONUS)
    return range
end

function getInstrumentSkill(player)
    return math.max(player:getSkillLevel(xi.skill.WIND), player:getSkillLevel(xi.skill.STRING))
end

function applySongEnhancement(player, target, effect, power, duration)
    -- Apply job point bonuses and equipment modifiers
    local jpBonus = player:getJobPointLevel(xi.jp.SONG_EFFECT_I)
    power = power + jpBonus
    
    target:addStatusEffect(effect, power, 0, duration)
end

-- Merit-enhanced song effects
function getSongMeritBonus(player, songType)
    local meritBonus = 0
    
    -- Song-specific merit bonuses
    if songType == "minne" then
        meritBonus = player:getMerit(xi.merit.MINNE_EFFECT)
    elseif songType == "minuet" then
        meritBonus = player:getMerit(xi.merit.MINUET_EFFECT)
    elseif songType == "madrigal" then
        meritBonus = player:getMerit(xi.merit.MADRIGAL_EFFECT)
    end
    
    return meritBonus
end

-- Merit-enhanced recast reduction
function getSongRecastReduction(player, songType)
    local recastReduction = 0
    
    if songType == "lullaby" then
        recastReduction = player:getMerit(xi.merit.LULLABY_RECAST)
    elseif songType == "finale" then
        recastReduction = player:getMerit(xi.merit.FINALE_RECAST)
    end
    
    return recastReduction
end

-----------------------------------
-- Ability Check Functions
-----------------------------------
xi.job_utils.bard.checkSoulVoice = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.bard.checkClarionCall = function(player, target, ability)
    ability:setRecast(math.max(0, ability:getRecast() - player:getMod(xi.mod.ONE_HOUR_RECAST) * 60))
    return 0, 0
end

xi.job_utils.bard.checkPianissimo = function(player, target, ability)
    if player:hasStatusEffect(xi.effect.PIANISSIMO) then
        return xi.msg.basic.EFFECT_ALREADY_ACTIVE, 0
    end
    return 0, 0
end

-----------------------------------
-- Song System Functions
-----------------------------------
xi.job_utils.bard.applySongEffect = function(player, target, songType, power)
    local duration = getSongDuration(player)
    local enhancedPower = power + player:getMod(xi.mod.ALL_SONGS_EFFECT)
    
    applySongEnhancement(player, target, songType, enhancedPower, duration)
end

xi.job_utils.bard.checkSongOverwrite = function(target, newSong)
    -- Check for song conflicts and handle overwriting
    local activeSongs = target:getActiveBuffs()
    -- Implementation for song overwrite logic
    return true
end

-----------------------------------
-- Ability Use Functions with Merit Integration
-----------------------------------
xi.job_utils.bard.useSoulVoice = function(player, target, ability)
    local duration = 180 + player:getJobPointLevel(xi.jp.SOUL_VOICE_EFFECT)
    player:addStatusEffect(xi.effect.SOUL_VOICE, 2, 0, duration)
end

xi.job_utils.bard.usePianissimo = function(player, target, ability)
    player:addStatusEffect(xi.effect.PIANISSIMO, 1, 0, 60)
end

xi.job_utils.bard.useNightingale = function(player, target, ability)
    local duration = 60 + player:getJobPointLevel(xi.jp.NIGHTINGALE_EFFECT)
    -- Merit enhancement for Nightingale
    local meritBonus = player:getMerit(xi.merit.NIGHTINGALE)
    duration = duration + meritBonus
    
    player:addStatusEffect(xi.effect.NIGHTINGALE, 2, 0, duration)
end

xi.job_utils.bard.useTroubadour = function(player, target, ability)
    local duration = 60 + player:getJobPointLevel(xi.jp.TROUBADOUR_EFFECT)
    player:addStatusEffect(xi.effect.TROUBADOUR, 2, 0, duration)
end

xi.job_utils.bard.useTenuto = function(player, target, ability)
    local duration = 60 + player:getJobPointLevel(xi.jp.TENUTO_EFFECT)
    player:addStatusEffect(xi.effect.TENUTO, 2, 0, duration)
end

xi.job_utils.bard.useMarcato = function(player, target, ability)
    local duration = 60 + player:getJobPointLevel(xi.jp.MARCATO_EFFECT)
    player:addStatusEffect(xi.effect.MARCATO, 50, 0, duration)
end

xi.job_utils.bard.useClarionCall = function(player, target, ability)
    local duration = 180 + player:getJobPointLevel(xi.jp.CLARION_CALL_EFFECT)
    local power = 10 + player:getJobPointLevel(xi.jp.CLARION_CALL_EFFECT)
    player:addStatusEffect(xi.effect.CLARION_CALL, power, 0, duration)
end

-----------------------------------
-- Song Enhancement System with Complete Merit Integration
-----------------------------------
xi.job_utils.bard.enhanceSongPower = function(player, basePower, songType)
    local instrumentSkill = getInstrumentSkill(player)
    local skillBonus = math.floor(instrumentSkill / 20)
    local jobPointBonus = player:getJobPointLevel(xi.jp.SONG_EFFECT_I)
    
    -- Merit bonuses for specific songs
    local meritBonus = getSongMeritBonus(player, songType)
    
    return basePower + skillBonus + jobPointBonus + meritBonus
end

xi.job_utils.bard.calculateSongAccuracy = function(player, target)
    local accuracy = player:getACC() + player:getMod(xi.mod.SONG_ACCURACY)
    local targetEvasion = target:getEVA()
    return math.max(accuracy - targetEvasion, 5) / 100
end

-- Complete merit-enhanced song application
xi.job_utils.bard.applySongWithMerits = function(player, target, songType, basePower, baseDuration)
    -- Apply merit bonuses
    local enhancedPower = xi.job_utils.bard.enhanceSongPower(player, basePower, songType)
    local enhancedDuration = baseDuration + getSongDuration(player)
    
    -- Apply recast reduction
    local recastReduction = getSongRecastReduction(player, songType)
    
    -- Apply the enhanced song effect
    applySongEnhancement(player, target, songType, enhancedPower, enhancedDuration)
    
    return {
        power = enhancedPower,
        duration = enhancedDuration,
        recastReduction = recastReduction
    }
end

-- Merit system integration for instrument skills
xi.job_utils.bard.getInstrumentMeritBonus = function(player, instrumentType)
    local meritBonus = 0
    
    if instrumentType == "wind" then
        meritBonus = player:getMerit(xi.merit.WIND)
    elseif instrumentType == "string" then
        meritBonus = player:getMerit(xi.merit.STRING)
    elseif instrumentType == "singing" then
        meritBonus = player:getMerit(xi.merit.SINGING)
    end
    
    return meritBonus
end
