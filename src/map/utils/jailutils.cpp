/*
===========================================================================

  Copyright (c) 2010-2015 Darkstar Dev Teams

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see http://www.gnu.org/licenses/

===========================================================================
*/

#include "jailutils.h"

#include "conquest_system.h"
#include "entities/charentity.h"
#include "map.h"
#include "map_utils.h"
#include "utils/showmsg.h"

#include "ai/ai_container.h"
#include "ai/controllers/player_controller.h"

#include <vector>
#include <array>
#include <ctime>
#include <fmt/format.h>

namespace jailutils
{
    auto InPrison(const CCharEntity* PChar) -> bool
    {
        TracyZoneScoped;
        return PChar->m_GMlevel == 0 && PChar->getZone() == ZONE_MORDION_GAOL;
    }

    void Add(CCharEntity* PChar)
    {
        TracyZoneScoped;
        PChar->PAI->SetController(nullptr);
        
        // Set jail status in character variables
        PChar->setCharVar("inJail", 1);
        PChar->setCharVar("jailTime", static_cast<uint32>(time(nullptr)));
        
        // Move to Mordion Gaol if not already there
        if (PChar->getZone() != ZONE_MORDION_GAOL)
        {
            PChar->setPos(-620, 11, 660, 0, ZONE_MORDION_GAOL);
        }
    }

    void Del(CCharEntity* PChar)
    {
        TracyZoneScoped;
        PChar->PAI->SetController(std::make_unique<CPlayerController>(PChar));
        
        // Clear jail status
        PChar->setCharVar("inJail", 0);
        PChar->setCharVar("jailTime", 0);
        PChar->setCharVar("jailDuration", 0);
        
        // Warp player out of jail
        PChar->warp();
    }
    
    // AI-GM Enhanced Functions Implementation
    void JailPlayer(CCharEntity* PChar, uint8 cellId, const std::string& reason)
    {
        TracyZoneScoped;
        
        if (!PChar) return;
        
        // Jail cell positions (matching the existing jail command)
        const std::vector<std::array<int16, 3>> jailCells = {
            // Floor 1 (Bottom)
            {{-620, 11,  660}}, {{-180, 11,  660}}, {{ 260, 11,  660}}, {{ 700, 11,  660}},
            {{-620, 11,  220}}, {{-180, 11,  220}}, {{ 260, 11,  220}}, {{ 700, 11,  220}},
            {{-620, 11, -220}}, {{-180, 11, -220}}, {{ 260, 11, -220}}, {{ 700, 11, -220}},
            {{-620, 11, -620}}, {{-180, 11, -620}}, {{ 260, 11, -620}}, {{ 700, 11, -620}},
            
            // Floor 2 (Top)
            {{-620, -400,  660}}, {{-180, -400,  660}}, {{ 260, -400,  660}}, {{ 700, -400,  660}},
            {{-620, -400,  220}}, {{-180, -400,  220}}, {{ 260, -400,  220}}, {{ 700, -400,  220}},
            {{-620, -400, -220}}, {{-180, -400, -220}}, {{ 260, -400, -220}}, {{ 700, -400, -220}},
            {{-620, -400, -620}}, {{-180, -400, -620}}, {{ 260, -400, -620}}, {{ 700, -400, -620}}
        };
        
        // Validate cell ID
        if (cellId < 1 || cellId > jailCells.size()) {
            cellId = 1;
        }
        
        auto cell = jailCells[cellId - 1];
        
        // Set jail variables
        PChar->setCharVar("inJail", cellId);
        PChar->setCharVar("jailTime", static_cast<uint32>(time(nullptr)));
        PChar->setCharVar("jailReason", reason.c_str());
        
        // Disable player controller
        PChar->PAI->SetController(nullptr);
        
        // Move to jail cell
        PChar->setPos(cell[0], cell[1], cell[2], 0, ZONE_MORDION_GAOL);
        
        // Notify player
        PChar->PrintToPlayer(fmt::format("You have been jailed by the AI-GM. Reason: {}", reason), CHAT_MESSAGE_TYPE_SYSTEM_3);
        
        // Log the action
        ShowInfo("AI-GM: Jailed player %s (ID: %u) in cell %u. Reason: %s", 
                 PChar->getName().c_str(), PChar->id, cellId, reason.c_str());
    }

    void PardonPlayer(CCharEntity* PChar)
    {
        TracyZoneScoped;
        
        if (!PChar) return;
        
        if (PChar->getCharVar("inJail") > 0)
        {
            Del(PChar);
            
            // Notify player
            PChar->PrintToPlayer("You have been pardoned by the AI-GM and released from jail.", CHAT_MESSAGE_TYPE_SYSTEM_3);
            
            // Log the action
            ShowInfo("AI-GM: Pardoned player %s (ID: %u)", PChar->getName().c_str(), PChar->id);
        }
    }
    
    bool IsPlayerJailed(uint32 playerId)
    {
        TracyZoneScoped;
        
        // This would need database query for offline players
        // For now, check online players only
        auto* PChar = GetCharByID(playerId);
        if (PChar)
        {
            return PChar->getCharVar("inJail") > 0;
        }
        
        return false;
    }
    
    void SetJailDuration(CCharEntity* PChar, uint32 minutes)
    {
        TracyZoneScoped;
        
        if (PChar && PChar->getCharVar("inJail") > 0)
        {
            PChar->setCharVar("jailDuration", minutes);
            PChar->setCharVar("jailTime", static_cast<uint32>(time(nullptr)));
        }
    }
    
    uint32 GetJailTimeRemaining(const CCharEntity* PChar)
    {
        TracyZoneScoped;
        
        if (!PChar || PChar->getCharVar("inJail") == 0) return 0;
        
        uint32 jailDuration = PChar->getCharVar("jailDuration");
        if (jailDuration == 0) return 0xFFFFFFFF; // Indefinite
        
        uint32 jailTime = PChar->getCharVar("jailTime");
        uint32 currentTime = static_cast<uint32>(time(nullptr));
        uint32 elapsed = currentTime - jailTime;
        uint32 durationSeconds = jailDuration * 60;
        
        if (elapsed >= durationSeconds) return 0;
        
        return (durationSeconds - elapsed) / 60; // Return minutes remaining
    }
    
    void NotifyGMsOfJailing(const std::string& playerName, const std::string& reason)
    {
        TracyZoneScoped;
        
        // Notify all online GMs about the jailing action
        map_session_list_t& sessionsMap = map_session_list;
        
        for (auto& [id, session] : sessionsMap)
        {
            if (session && session->PChar && session->PChar->m_GMlevel >= 1)
            {
                session->PChar->PrintToPlayer(
                    fmt::format("[AI-GM] Player {} has been jailed. Reason: {}", playerName, reason),
                    CHAT_MESSAGE_TYPE_SYSTEM_1
                );
            }
        }
    }
}; // namespace jailutils
