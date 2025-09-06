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

#pragma once

#include <chrono>
#include <cstdint>
#include <string>
#include <string_view>

namespace version
{
    // Git information (inline constexpr definitions)
    [[nodiscard]] constexpr std::string_view GetGitSha() noexcept
    {
        return "0dfed0af";
    }
    [[nodiscard]] constexpr std::string_view GetGitBranch() noexcept
    {
        return "copilot/fix-1736cab6-4bd3-40e0-89d7-35e27175e7a2";
    }
    [[nodiscard]] constexpr std::string_view GetGitDate() noexcept
    {
        return "Sat Sep 6 18:50:25 2025";
    }
    [[nodiscard]] constexpr std::string_view GetGitCommitSubject() noexcept
    {
        return "Fix Lua string method usage in ai_gm.lua";
    }

    // Enhanced version information
    [[nodiscard]] std::string GetVersionString();
    [[nodiscard]] std::string GetFullVersionString();
    [[nodiscard]] std::string GetBuildInfo();

    // Version components
    struct VersionInfo
    {
        std::uint16_t    major;
        std::uint16_t    minor;
        std::uint16_t    patch;
        std::string_view git_sha;
        std::string_view git_branch;
        std::string_view build_date;
        std::string_view compiler_version;
        std::string_view cmake_version;
    };

    [[nodiscard]] VersionInfo GetVersionInfo() noexcept;

    // Runtime information
    [[nodiscard]] std::string                           GetRuntimeInfo();
    [[nodiscard]] std::chrono::system_clock::time_point GetBuildTimestamp();

    // Feature flags
    [[nodiscard]] constexpr bool HasFeature(std::string_view feature) noexcept;
    [[nodiscard]] std::string    GetEnabledFeatures();

} // namespace version
