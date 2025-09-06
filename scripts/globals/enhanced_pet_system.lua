-----------------------------------
-- Enhanced Pet System for ITERATION 9
-- Advanced pet combat, AI improvements, and coordination
-----------------------------------
require('scripts/globals/pets')
require('scripts/globals/trust')

xi = xi or {}
xi.enhanced_pets = xi.enhanced_pets or {}

-- Pet AI behavior types
xi.enhanced_pets.AI_TYPE = {
    AGGRESSIVE = 1,
    DEFENSIVE = 2,
    SUPPORT = 3,
    BALANCED = 4
}

-- Advanced pet AI calculation
xi.enhanced_pets.calculatePetAI = function(pet, master, target)
    local aiType = pet:getLocalVar("aiType") or xi.enhanced_pets.AI_TYPE.BALANCED
    local masterHP = master:getHPP()
    local petHP = pet:getHPP()
    local threat = pet:getEnmityTowardsTarget(target)
    
    local decision = {
        action = "none",
        priority = 0,
        target = nil
    }
    
    -- Emergency healing check
    if masterHP < 25 and pet:hasSpell(xi.magic.spell.CURE) then
        decision.action = "heal"
        decision.priority = 100
        decision.target = master
        return decision
    end
    
    -- Pet self-preservation
    if petHP < 30 and pet:hasSpell(xi.magic.spell.CURE) then
        decision.action = "self_heal" 
        decision.priority = 90
        decision.target = pet
        return decision
    end
    
    -- AI type specific behaviors
    if aiType == xi.enhanced_pets.AI_TYPE.AGGRESSIVE then
        decision.action = "attack"
        decision.priority = 80
        decision.target = target
    elseif aiType == xi.enhanced_pets.AI_TYPE.DEFENSIVE then
        if masterHP < 50 then
            decision.action = "protect"
            decision.priority = 70
            decision.target = master
        end
    elseif aiType == xi.enhanced_pets.AI_TYPE.SUPPORT then
        decision.action = "buff"
        decision.priority = 60
        decision.target = master
    end
    
    return decision
end

-- Pet equipment and stat inheritance
xi.enhanced_pets.petEquipment = function(pet, master)
    local masterGear = master:getEquippedItems()
    local petStatBonus = 0
    
    -- Calculate stat inheritance from master's gear
    for slot, item in pairs(masterGear) do
        if item and item:getMod(xi.mod.PET_ATT_DEF) > 0 then
            petStatBonus = petStatBonus + item:getMod(xi.mod.PET_ATT_DEF)
        end
        
        if item and item:getMod(xi.mod.PET_MAB_MAD) > 0 then
            pet:addMod(xi.mod.MATT, item:getMod(xi.mod.PET_MAB_MAD))
        end
    end
    
    -- Apply pet stat bonuses
    if petStatBonus > 0 then
        pet:addMod(xi.mod.ATT, petStatBonus)
        pet:addMod(xi.mod.DEF, petStatBonus)
    end
end

-- Trust coordination system
xi.enhanced_pets.partyCoordination = function(trust, party)
    local coordination = {
        efficiency = 92, -- Target 92% party efficiency
        role = trust:getLocalVar("trustRole") or "support"
    }
    
    -- Analyze party composition
    local tanks = 0
    local healers = 0
    local dps = 0
    
    for _, member in pairs(party) do
        if member:isTank() then
            tanks = tanks + 1
        elseif member:isHealer() then
            healers = healers + 1
        else
            dps = dps + 1
        end
    end
    
    -- Adjust trust behavior based on party needs
    if tanks == 0 and trust:canTank() then
        trust:setLocalVar("trustRole", "tank")
        coordination.role = "tank"
    elseif healers == 0 and trust:canHeal() then
        trust:setLocalVar("trustRole", "healer")
        coordination.role = "healer"
    else
        trust:setLocalVar("trustRole", "dps")
        coordination.role = "dps"
    end
    
    -- Calculate coordination efficiency
    local roleBalance = math.abs(tanks - 1) + math.abs(healers - 1) + math.abs(dps - 4)
    coordination.efficiency = math.max(70, 95 - (roleBalance * 5))
    
    return coordination
end

-- Summoner avatar coordination
xi.enhanced_pets.avatarCoordination = function(avatar, summoner, situation)
    local coordination = {
        bloodPactReady = false,
        strategicWithdraw = false,
        battlefieldControl = false
    }
    
    -- Check MP for blood pacts
    local summonerMP = summoner:getMP()
    local mpCost = avatar:getBloodPactCost(avatar:getLocalVar("nextBloodPact"))
    
    if summonerMP >= mpCost then
        coordination.bloodPactReady = true
    end
    
    -- Strategic avatar withdrawal
    local avatarHP = avatar:getHPP()
    if avatarHP < 20 and summoner:hasRecast(xi.recast.ABILITY, 101) then -- Retreat recast
        coordination.strategicWithdraw = true
    end
    
    -- Battlefield control assessment
    local enemies = summoner:getNearbyEnemies(15)
    if #enemies >= 3 and avatar:hasBloodPact("aoe") then
        coordination.battlefieldControl = true
    end
    
    return coordination
end

print("Enhanced Pet System loaded for ITERATION 9")
