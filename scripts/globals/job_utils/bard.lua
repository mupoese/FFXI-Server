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
-- Song Enhancement Functions
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
-- Ability Use Functions
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
-- Song Enhancement System
-----------------------------------
xi.job_utils.bard.enhanceSongPower = function(player, basePower)
    local instrumentSkill = getInstrumentSkill(player)
    local skillBonus = math.floor(instrumentSkill / 20)
    local jobPointBonus = player:getJobPointLevel(xi.jp.SONG_EFFECT_I)
    
    return basePower + skillBonus + jobPointBonus
end

xi.job_utils.bard.calculateSongAccuracy = function(player, target)
    local accuracy = player:getACC() + player:getMod(xi.mod.SONG_ACCURACY)
    local targetEvasion = target:getEVA()
    return math.max(accuracy - targetEvasion, 5) / 100
end
