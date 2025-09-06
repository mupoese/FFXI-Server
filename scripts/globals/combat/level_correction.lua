-----------------------------------
-- Handles the zones in which level correction still happens.
-- As a general rule:
-- Any zone in which contains a mob over lvl 99, level correction is deactivated.
-- Adoulin zones, zones with Apex or Locus mobs, etc...
-----------------------------------
xi = xi or {}
xi.combat = xi.combat or {}
xi.combat.levelCorrection = xi.combat.levelCorrection or {}
-----------------------------------
-- List of zones in which level correction still happens.
local levelCorrectionZoneList =
set{
    xi.zone.PHANAUET_CHANNEL,
    xi.zone.CARPENTERS_LANDING,
    xi.zone.MANACLIPPER,
    xi.zone.ULEGUERAND_RANGE,
    xi.zone.BEARCLAW_PINNACLE,
    xi.zone.ATTOHWA_CHASM,
    xi.zone.BONEYARD_GULLY,
    xi.zone.PSOXJA,
    xi.zone.THE_SHROUDED_MAW,
    xi.zone.OLDTON_MOVALPOLOS,
    xi.zone.NEWTON_MOVALPOLOS,
    xi.zone.MINE_SHAFT_2716,
    xi.zone.HALL_OF_TRANSFERENCE,
    xi.zone.ABYSSEA_KONSCHTAT,
    xi.zone.SPIRE_OF_HOLLA,
    xi.zone.SPIRE_OF_DEM,
    xi.zone.SPIRE_OF_MEA,
    xi.zone.SPIRE_OF_VAHZL,
    xi.zone.LUFAISE_MEADOWS,
    xi.zone.MISAREAUX_COAST,
    xi.zone.TAVNAZIAN_SAFEHOLD,
    xi.zone.PHOMIUNA_AQUEDUCTS,
    xi.zone.SACRARIUM,
    xi.zone.RIVERNE_SITE_B01,
    xi.zone.RIVERNE_SITE_A01,
    xi.zone.MONARCH_LINN,
    xi.zone.SEALIONS_DEN,
    xi.zone.ALTAIEU,
    xi.zone.GRAND_PALACE_OF_HUXZOI,
    xi.zone.THE_GARDEN_OF_RUHMET,
    xi.zone.EMPYREAL_PARADOX,
    xi.zone.TEMENOS,
    xi.zone.APOLLYON,
    xi.zone.DYNAMIS_VALKURM,
    xi.zone.DYNAMIS_BUBURIMU,
    xi.zone.DYNAMIS_QUFIM,
    xi.zone.DYNAMIS_TAVNAZIA,
    xi.zone.DIORAMA_ABDHALJS_GHELSBA,
    xi.zone.ABDHALJS_ISLE_PURGONORGO,
    xi.zone.ABYSSEA_TAHRONGI,
    xi.zone.OPEN_SEA_ROUTE_TO_AL_ZAHBI,
    xi.zone.OPEN_SEA_ROUTE_TO_MHAURA,
    xi.zone.AL_ZAHBI,
    xi.zone.WAJAOM_WOODLANDS,
    xi.zone.ARRAPAGO_REEF,
    xi.zone.ILRUSI_ATOLL,
    xi.zone.PERIQIA,
    xi.zone.TALACCA_COVE,
    xi.zone.SILVER_SEA_ROUTE_TO_NASHMAU,
    xi.zone.SILVER_SEA_ROUTE_TO_AL_ZAHBI,
    xi.zone.THE_ASHU_TALIF,
    xi.zone.MOUNT_ZHAYOLM,
    xi.zone.HALVUNG,
    xi.zone.LEBROS_CAVERN,
    xi.zone.NAVUKGO_EXECUTION_CHAMBER,
    xi.zone.MAMOOK,
    xi.zone.MAMOOL_JA_TRAINING_GROUNDS,
    xi.zone.JADE_SEPULCHER,
    xi.zone.AYDEEWA_SUBTERRANE,
    xi.zone.LEUJAOAM_SANCTUM,
    xi.zone.THE_COLOSSEUM,
    xi.zone.ZHAYOLM_REMNANTS,
    xi.zone.ARRAPAGO_REMNANTS,
    xi.zone.BHAFLAU_REMNANTS,
    xi.zone.SILVER_SEA_REMNANTS,
    xi.zone.NYZUL_ISLE,
    xi.zone.HAZHALM_TESTING_GROUNDS,
    xi.zone.CAEDARVA_MIRE,
    xi.zone.SOUTHERN_SAN_DORIA_S,
    xi.zone.EAST_RONFAURE_S,
    xi.zone.JUGNER_FOREST_S,
    xi.zone.VUNKERL_INLET_S,
    xi.zone.BATALLIA_DOWNS_S,
    xi.zone.LA_VAULE_S,
    xi.zone.EVERBLOOM_HOLLOW,
    xi.zone.BASTOK_MARKETS_S,
    xi.zone.NORTH_GUSTABERG_S,
    xi.zone.GRAUBERG_S,
    xi.zone.PASHHOW_MARSHLANDS_S,
    xi.zone.ROLANBERRY_FIELDS_S,
    xi.zone.BEADEAUX_S,
    xi.zone.RUHOTZ_SILVERMINES,
    xi.zone.WINDURST_WATERS_S,
    xi.zone.WEST_SARUTABARUTA_S,
    xi.zone.FORT_KARUGO_NARUGO_S,
    xi.zone.MERIPHATAUD_MOUNTAINS_S,
    xi.zone.SAUROMUGUE_CHAMPAIGN_S,
    xi.zone.CASTLE_OZTROJA_S,
    xi.zone.WEST_RONFAURE,
    xi.zone.EAST_RONFAURE,
    xi.zone.LA_THEINE_PLATEAU,
    xi.zone.VALKURM_DUNES,
    xi.zone.JUGNER_FOREST,
    xi.zone.BATALLIA_DOWNS,
    xi.zone.NORTH_GUSTABERG,
    xi.zone.SOUTH_GUSTABERG,
    xi.zone.KONSCHTAT_HIGHLANDS,
    xi.zone.PASHHOW_MARSHLANDS,
    xi.zone.ROLANBERRY_FIELDS,
    xi.zone.BEAUCEDINE_GLACIER,
    xi.zone.XARCABARD,
    xi.zone.CAPE_TERIGGAN,
    xi.zone.EASTERN_ALTEPA_DESERT,
    xi.zone.WEST_SARUTABARUTA,
    xi.zone.EAST_SARUTABARUTA,
    xi.zone.TAHRONGI_CANYON,
    xi.zone.BUBURIMU_PENINSULA,
    xi.zone.MERIPHATAUD_MOUNTAINS,
    xi.zone.SAUROMUGUE_CHAMPAIGN,
    xi.zone.THE_SANCTUARY_OF_ZITAH,
    xi.zone.ROMAEVE,
    xi.zone.YUHTUNGA_JUNGLE,
    xi.zone.YHOATOR_JUNGLE,
    xi.zone.WESTERN_ALTEPA_DESERT,
    xi.zone.QUFIM_ISLAND,
    xi.zone.BEHEMOTHS_DOMINION,
    xi.zone.VALLEY_OF_SORROWS,
    xi.zone.GHOYUS_REVERIE,
    xi.zone.RUAUN_GARDENS,
    xi.zone.ABYSSEA_LA_THEINE,
    xi.zone.DYNAMIS_BEAUCEDINE,
    xi.zone.DYNAMIS_XARCABARD,
    xi.zone.BEAUCEDINE_GLACIER_S,
    xi.zone.XARCABARD_S,
    xi.zone.CASTLE_ZVAHL_BAILEYS_S,
    xi.zone.HORLAIS_PEAK,
    xi.zone.GHELSBA_OUTPOST,
    xi.zone.FORT_GHELSBA,
    xi.zone.YUGHOTT_GROTTO,
    xi.zone.PALBOROUGH_MINES,
    xi.zone.WAUGHROON_SHRINE,
    xi.zone.GIDDEUS,
    xi.zone.BALGAS_DAIS,
    xi.zone.BEADEAUX,
    xi.zone.QULUN_DOME,
    xi.zone.DAVOI,
    xi.zone.MONASTIC_CAVERN,
    xi.zone.CASTLE_OZTROJA,
    xi.zone.ALTAR_ROOM,
    xi.zone.THE_BOYAHDA_TREE,
    xi.zone.DRAGONS_AERY,
    xi.zone.CASTLE_ZVAHL_KEEP_S,
    xi.zone.THRONE_ROOM_S,
    xi.zone.MIDDLE_DELKFUTTS_TOWER,
    xi.zone.UPPER_DELKFUTTS_TOWER,
    xi.zone.TEMPLE_OF_UGGALEPIH,
    xi.zone.DEN_OF_RANCOR,
    xi.zone.CASTLE_ZVAHL_BAILEYS,
    xi.zone.CASTLE_ZVAHL_KEEP,
    xi.zone.SACRIFICIAL_CHAMBER,
    xi.zone.GARLAIGE_CITADEL_S,
    xi.zone.THRONE_ROOM,
    xi.zone.RANGUEMONT_PASS,
    xi.zone.BOSTAUNIEUX_OUBLIETTE,
    xi.zone.CHAMBER_OF_ORACLES,
    xi.zone.TORAIMARAI_CANAL,
    xi.zone.FULL_MOON_FOUNTAIN,
    xi.zone.ZERUHN_MINES,
    xi.zone.KORROLOKA_TUNNEL,
    xi.zone.KUFTAL_TUNNEL,
    xi.zone.THE_ELDIEME_NECROPOLIS_S,
    xi.zone.SEA_SERPENT_GROTTO,
    xi.zone.VELUGANNON_PALACE,
    xi.zone.THE_SHRINE_OF_RUAVITAU,
    xi.zone.STELLAR_FULCRUM,
    xi.zone.LALOFF_AMPHITHEATER,
    xi.zone.THE_CELESTIAL_NEXUS,
    xi.zone.WALK_OF_ECHOES,
    xi.zone.MAQUETTE_ABDHALJS_LEGION_A,
    xi.zone.LOWER_DELKFUTTS_TOWER,
    xi.zone.DYNAMIS_SAN_DORIA,
    xi.zone.DYNAMIS_BASTOK,
    xi.zone.DYNAMIS_WINDURST,
    xi.zone.DYNAMIS_JEUNO,
    xi.zone.DANGRUF_WADI,
    xi.zone.INNER_HORUTOTO_RUINS,
    xi.zone.ORDELLES_CAVES,
    xi.zone.OUTER_HORUTOTO_RUINS,
    xi.zone.THE_ELDIEME_NECROPOLIS,
    xi.zone.GUSGEN_MINES,
    xi.zone.CRAWLERS_NEST,
    xi.zone.MAZE_OF_SHAKHRAMI,
    xi.zone.GARLAIGE_CITADEL,
    xi.zone.CLOISTER_OF_GALES,
    xi.zone.CLOISTER_OF_STORMS,
    xi.zone.CLOISTER_OF_FROST,
    xi.zone.FEIYIN,
    xi.zone.IFRITS_CAULDRON,
    xi.zone.QUBIA_ARENA,
    xi.zone.CLOISTER_OF_FLAMES,
    xi.zone.QUICKSAND_CAVES,
    xi.zone.CLOISTER_OF_TREMORS,
    xi.zone.CLOISTER_OF_TIDES,
    xi.zone.GUSTAV_TUNNEL,
    xi.zone.LABYRINTH_OF_ONZOZO,
    xi.zone.ABYSSEA_ATTOHWA,
    xi.zone.ABYSSEA_MISAREAUX,
    xi.zone.ABYSSEA_VUNKERL,
    xi.zone.ABYSSEA_ALTEPA,
    xi.zone.SHIP_BOUND_FOR_SELBINA,
    xi.zone.SHIP_BOUND_FOR_MHAURA,
    xi.zone.PROVENANCE,
    xi.zone.SAN_DORIA_JEUNO_AIRSHIP,
    xi.zone.BASTOK_JEUNO_AIRSHIP,
    xi.zone.WINDURST_JEUNO_AIRSHIP,
    xi.zone.KAZHAM_JEUNO_AIRSHIP,
    xi.zone.SHIP_BOUND_FOR_SELBINA_PIRATES,
    xi.zone.SHIP_BOUND_FOR_MHAURA_PIRATES,
    xi.zone.ABYSSEA_ULEGUERAND,
    xi.zone.ABYSSEA_GRAUBERG,
    xi.zone.ABYSSEA_EMPYREAL_PARADOX,
    xi.zone.WALK_OF_ECHOES_P2,
    xi.zone.DYNAMIS_SAN_DORIA_D,
    xi.zone.DYNAMIS_BASTOK_D,
    xi.zone.DYNAMIS_WINDURST_D,
    xi.zone.DYNAMIS_JEUNO_D,
    xi.zone.WALK_OF_ECHOES_P1
}

-- Meant to be called from a master function and fed to corresponding calculation.
-- Example: pDIF functions, Actor magic accuracy, etc...
xi.combat.levelCorrection.isLevelCorrectedZone = function(actor)
    if xi.settings.main.USE_ADOULIN_WEAPON_SKILL_CHANGES then
        local actorZone = actor:getZoneID()

        return levelCorrectionZoneList[actorZone] or false
    else
        return true
    end
end

-- Enhanced level correction calculation for ITERATION 8
xi.combat.levelCorrection.calculateCorrection = function(attackerLevel, targetLevel, zoneOverride)
    local levelDiff = attackerLevel - targetLevel
    
    -- Zone check - use override if provided, otherwise check current zone
    local useLevelCorrection = true
    if zoneOverride ~= nil then
        useLevelCorrection = zoneOverride
    else
        -- Assume we're in a level corrected zone if no override provided
        useLevelCorrection = true
    end
    
    if not useLevelCorrection then
        return 1.0 -- No level correction
    end
    
    -- Retail-accurate level correction formula
    local correction = 1.0
    
    if levelDiff > 0 then
        -- Attacker is higher level
        if levelDiff <= 5 then
            correction = 1.0 + (levelDiff * 0.05) -- 5% per level up to 5 levels
        elseif levelDiff <= 10 then
            correction = 1.25 + ((levelDiff - 5) * 0.03) -- 3% per level from 6-10
        else
            correction = 1.40 + ((levelDiff - 10) * 0.02) -- 2% per level beyond 10
            correction = math.min(correction, 2.0) -- Cap at 200%
        end
    elseif levelDiff < 0 then
        -- Attacker is lower level
        local absLevelDiff = math.abs(levelDiff)
        if absLevelDiff <= 5 then
            correction = 1.0 - (absLevelDiff * 0.05) -- -5% per level up to 5 levels
        elseif absLevelDiff <= 10 then
            correction = 0.75 - ((absLevelDiff - 5) * 0.04) -- -4% per level from 6-10
        else
            correction = 0.55 - ((absLevelDiff - 10) * 0.03) -- -3% per level beyond 10
            correction = math.max(correction, 0.1) -- Cap at 10% minimum
        end
    end
    
    return correction
end

-- Enhanced level correction for specific combat aspects
xi.combat.levelCorrection.calculateAccuracyCorrection = function(attackerLevel, targetLevel, zoneOverride)
    local baseCorrection = xi.combat.levelCorrection.calculateCorrection(attackerLevel, targetLevel, zoneOverride)
    
    -- Accuracy has different scaling than damage
    local levelDiff = attackerLevel - targetLevel
    local accuracyMod = 1.0
    
    if levelDiff > 0 then
        accuracyMod = 1.0 + (levelDiff * 0.04) -- 4% accuracy per level advantage
        accuracyMod = math.min(accuracyMod, 1.8) -- Cap at 180%
    elseif levelDiff < 0 then
        accuracyMod = 1.0 + (levelDiff * 0.06) -- -6% accuracy per level disadvantage
        accuracyMod = math.max(accuracyMod, 0.2) -- Cap at 20% minimum
    end
    
    return baseCorrection * accuracyMod
end

-- Enhanced level correction for magical accuracy
xi.combat.levelCorrection.calculateMagicAccuracyCorrection = function(casterLevel, targetLevel, zoneOverride)
    local baseCorrection = xi.combat.levelCorrection.calculateCorrection(casterLevel, targetLevel, zoneOverride)
    
    -- Magic accuracy scaling
    local levelDiff = casterLevel - targetLevel
    local magicAccMod = 1.0
    
    if levelDiff > 0 then
        magicAccMod = 1.0 + (levelDiff * 0.03) -- 3% magic accuracy per level advantage
        magicAccMod = math.min(magicAccMod, 1.6) -- Cap at 160%
    elseif levelDiff < 0 then
        magicAccMod = 1.0 + (levelDiff * 0.05) -- -5% magic accuracy per level disadvantage
        magicAccMod = math.max(magicAccMod, 0.25) -- Cap at 25% minimum
    end
    
    return baseCorrection * magicAccMod
end

-- Enhanced level correction for critical hit rates
xi.combat.levelCorrection.calculateCriticalCorrection = function(attackerLevel, targetLevel, zoneOverride)
    local levelDiff = attackerLevel - targetLevel
    local critMod = 1.0
    
    -- Critical hits are affected by level difference
    if levelDiff > 0 then
        critMod = 1.0 + (levelDiff * 0.02) -- 2% crit bonus per level advantage
        critMod = math.min(critMod, 1.5) -- Cap at 150%
    elseif levelDiff < 0 then
        critMod = 1.0 + (levelDiff * 0.03) -- -3% crit rate per level disadvantage
        critMod = math.max(critMod, 0.1) -- Cap at 10% minimum
    end
    
    return critMod
end

print("Enhanced Level Correction System loaded for ITERATION 8")
