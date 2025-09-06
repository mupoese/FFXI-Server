-----------------------------------
-- Pet Global Functions (Enhanced for ITERATION 9)
-----------------------------------
require('scripts/globals/nyzul/pathos')
require('scripts/globals/enhanced_pet_system')
-----------------------------------
xi = xi or {}
xi.pet = xi.pet or {}

xi.pet.spawnPet = function(player, petID)
    player:spawnPet(petID)

    -- Nyzul Isle has Pathos set randomly on floors and is recorded as bits in a localvar of the instance
    if player:getZoneID() == xi.zone.NYZUL_ISLE then
        xi.nyzul.addPetSpawnPathos(player)
    end
    
    -- Apply ITERATION 9 pet enhancements
    local pet = player:getPet()
    if pet then
        -- Initialize enhanced pet AI
        pet:setLocalVar("aiType", xi.enhanced_pets.AI_TYPE.BALANCED)
        
        -- Apply pet equipment bonuses
        xi.enhanced_pets.petEquipment(pet, player)
        
        -- Set up trust coordination if pet is a trust
        if pet:isTrust() then
            local party = player:getParty()
            local coordination = xi.enhanced_pets.partyCoordination(pet, party)
            pet:setLocalVar("trustRole", coordination.role)
            pet:setLocalVar("partyEfficiency", coordination.efficiency)
        end
    end
end

-- Enhanced pet AI processing (ITERATION 9)
xi.pet.processEnhancedAI = function(pet, master, target)
    if not xi.enhanced_pets then
        return -- Fallback if enhanced system not loaded
    end
    
    local decision = xi.enhanced_pets.calculatePetAI(pet, master, target)
    
    -- Execute AI decision
    if decision.action == "heal" and decision.target then
        pet:castSpell(xi.magic.spell.CURE, decision.target)
    elseif decision.action == "attack" and decision.target then
        pet:updateEnmity(decision.target)
    elseif decision.action == "protect" and decision.target then
        pet:useMobAbility(pet:getRandomProtectiveAbility(), decision.target)
    elseif decision.action == "buff" and decision.target then
        pet:castSpell(pet:getRandomBuffSpell(), decision.target)
    end
    
    return decision
end
