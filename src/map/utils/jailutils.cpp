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

#include <array>
#include <cstdint>
#include <ctime>
#include <fmt/format.h>
#include <vector>

#include "ai/ai_container.h"
#include "ai/controllers/player_controller.h"
#include "common/logging.h"
#include "conquest_system.h"
#include "entities/charentity.h"
#include "map_session_container.h"
#include "packets/chat_message.h"
#include "utils/charutils.h"
#include "utils/zoneutils.h"
#include "zone.h"

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
        PChar->setCharVar("jailTime", static_cast<std::uint32_t>(time(nullptr)));

        // Move to Mordion Gaol if not already there
        if (PChar->getZone() != ZONE_MORDION_GAOL)
        {
            charutils::SendToZone(PChar, ZONE_MORDION_GAOL);
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
        charutils::HomePoint(PChar, true);
    }

    // AI-GM Enhanced Functions Implementation
    void JailPlayer(CCharEntity* PChar, std::uint8_t cellId, const std::string& reason)
    {
        TracyZoneScoped;

        if (!PChar)
            return;

        // Jail cell positions (matching the existing jail command)
        const std::vector<std::array<int16, 3>> jailCells = {
            // Floor 1 (Bottom)
            { { -620, 11, 660 } },
            { { -180, 11, 660 } },
            { { 260, 11, 660 } },
            { { 700, 11, 660 } },
            { { -620, 11, 220 } },
            { { -180, 11, 220 } },
            { { 260, 11, 220 } },
            { { 700, 11, 220 } },
            { { -620, 11, -220 } },
            { { -180, 11, -220 } },
            { { 260, 11, -220 } },
            { { 700, 11, -220 } },
            { { -620, 11, -620 } },
            { { -180, 11, -620 } },
            { { 260, 11, -620 } },
            { { 700, 11, -620 } },

            // Floor 2 (Top)
            { { -620, -400, 660 } },
            { { -180, -400, 660 } },
            { { 260, -400, 660 } },
            { { 700, -400, 660 } },
            { { -620, -400, 220 } },
            { { -180, -400, 220 } },
            { { 260, -400, 220 } },
            { { 700, -400, 220 } },
            { { -620, -400, -220 } },
            { { -180, -400, -220 } },
            { { 260, -400, -220 } },
            { { 700, -400, -220 } },
            { { -620, -400, -620 } },
            { { -180, -400, -620 } },
            { { 260, -400, -620 } },
            { { 700, -400, -620 } }
        };

        // Validate cell ID
        if (cellId < 1 || cellId > jailCells.size())
        {
            cellId = 1;
        }

        auto cell = jailCells[cellId - 1];

        // Set jail variables
        PChar->setCharVar("inJail", cellId);
        PChar->setCharVar("jailTime", static_cast<std::uint32_t>(time(nullptr)));
        PChar->setCharVar("jailReason", reason.c_str());

        // Disable player controller
        PChar->PAI->SetController(nullptr);

        // Move to jail cell - first send to zone, then set position
        if (PChar->getZone() != ZONE_MORDION_GAOL)
        {
            charutils::SendToZone(PChar, ZONE_MORDION_GAOL);
        }
        // Note: Position will be set when zone loads - this is handled by zone logic

        // Notify player
        PChar->pushPacket<CChatMessagePacket>(PChar, CHAT_MESSAGE_TYPE::MESSAGE_SYSTEM_3, fmt::format("You have been jailed by the AI-GM. Reason: {}", reason));

        // Log the action
        ShowInfo("AI-GM: Jailed player %s (ID: %u) in cell %u. Reason: %s",
                 PChar->getName().c_str(), PChar->id, cellId, reason.c_str());
    }

    void PardonPlayer(CCharEntity* PChar)
    {
        TracyZoneScoped;

        if (!PChar)
            return;

        if (PChar->getCharVar("inJail") > 0)
        {
            Del(PChar);

            // Notify player
            PChar->pushPacket<CChatMessagePacket>(PChar, CHAT_MESSAGE_TYPE::MESSAGE_SYSTEM_3, "You have been pardoned by the AI-GM and released from jail.");

            // Log the action
            ShowInfo("AI-GM: Pardoned player %s (ID: %u)", PChar->getName().c_str(), PChar->id);
        }
    }

    bool IsPlayerJailed(std::uint32_t playerId)
    {
        TracyZoneScoped;

        // TODO: This would need database query for offline players or proper session lookup
        // For now, return false to allow compilation
        // This function should be implemented once the proper character lookup mechanism is determined
        return false;
    }

    void SetJailDuration(CCharEntity* PChar, std::uint32_t minutes)
    {
        TracyZoneScoped;

        if (PChar && PChar->getCharVar("inJail") > 0)
        {
            PChar->setCharVar("jailDuration", minutes);
            PChar->setCharVar("jailTime", static_cast<std::uint32_t>(time(nullptr)));
        }
    }

    std::uint32_t GetJailTimeRemaining(const CCharEntity* PChar)
    {
        TracyZoneScoped;

        if (!PChar || PChar->getCharVar("inJail") == 0)
            return 0;

        std::uint32_t jailDuration = PChar->getCharVar("jailDuration");
        if (jailDuration == 0)
            return 0xFFFFFFFF; // Indefinite

        std::uint32_t jailTime        = PChar->getCharVar("jailTime");
        std::uint32_t currentTime     = static_cast<std::uint32_t>(time(nullptr));
        std::uint32_t elapsed         = currentTime - jailTime;
        std::uint32_t durationSeconds = jailDuration * 60;

        if (elapsed >= durationSeconds)
            return 0;

        return (durationSeconds - elapsed) / 60; // Return minutes remaining
    }

    void NotifyGMsOfJailing(const std::string& playerName, const std::string& reason)
    {
        TracyZoneScoped;

        // TODO: Notify all online GMs about the jailing action
        // This needs proper session container access - simplified for now
        ShowInfo("[AI-GM] Player %s has been jailed. Reason: %s", playerName.c_str(), reason.c_str());
    }
}; // namespace jailutils
