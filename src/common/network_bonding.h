/*
===========================================================================

  Copyright (c) 2024 LandSandBoat Dev Teams

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

#include "cbasetypes.h"
#include "logging.h"
#include "timer.h"
#include "ipp.h"

#include <memory>
#include <vector>
#include <string>
#include <unordered_map>
#include <atomic>
#include <mutex>
#include <chrono>
#include <functional>

#include <asio/ip/udp.hpp>
#include <asio/ip/tcp.hpp>
#include <asio/ts/buffer.hpp>
#include <asio/ts/internet.hpp>

namespace network
{
    namespace bonding
    {
        // Bonding modes matching Linux kernel bonding modes
        enum class BondingMode : uint8
        {
            BALANCE_RR = 0,      // Round-robin for maximum throughput
            ACTIVE_BACKUP = 1,   // Fault tolerance focus
            BALANCE_XOR = 2,     // XOR hash-based distribution
            BROADCAST = 3,       // Broadcast on all interfaces
            LACP_802_3AD = 4,    // Dynamic link aggregation (recommended)
            BALANCE_TLB = 5,     // Adaptive transmit load balancing
            BALANCE_ALB = 6      // Adaptive load balancing
        };

        // Hash policies for load balancing
        enum class HashPolicy : uint8
        {
            LAYER2 = 0,          // Ethernet MAC based
            LAYER3_4 = 1,        // IP + Port based (better for TCP/UDP)
            LAYER2_3 = 2,        // MAC + IP based
            ENCAP2_3 = 3,        // Encapsulated layer 2+3
            ENCAP3_4 = 4         // Encapsulated layer 3+4
        };

        // Network interface information
        struct NetworkInterface
        {
            std::string name;
            std::string ip_address;
            uint16 port;
            bool is_active;
            bool is_primary;
            uint64 bytes_sent;
            uint64 bytes_received;
            uint64 packets_sent;
            uint64 packets_received;
            uint64 errors;
            uint64 last_activity;
            
            NetworkInterface(const std::string& n, const std::string& ip, uint16 p)
                : name(n), ip_address(ip), port(p), is_active(true), is_primary(false)
                , bytes_sent(0), bytes_received(0), packets_sent(0), packets_received(0)
                , errors(0), last_activity(timer::get_utc_microseconds()) {}
        };

        // Bonding statistics for monitoring
        struct BondingStats
        {
            std::atomic<uint64> total_bytes_sent{0};
            std::atomic<uint64> total_bytes_received{0};
            std::atomic<uint64> total_packets_sent{0};
            std::atomic<uint64> total_packets_received{0};
            std::atomic<uint64> total_errors{0};
            std::atomic<uint64> interface_failures{0};
            std::atomic<uint64> failover_events{0};
            std::atomic<double> average_latency_ms{0.0};
            std::atomic<uint32> active_interfaces{0};
            std::atomic<uint64> last_stats_reset{0};

            void reset()
            {
                total_bytes_sent = 0;
                total_bytes_received = 0;
                total_packets_sent = 0;
                total_packets_received = 0;
                total_errors = 0;
                interface_failures = 0;
                failover_events = 0;
                average_latency_ms = 0.0;
                last_stats_reset = timer::get_utc_microseconds();
            }
        };

        // Network bonding manager
        class NetworkBondingManager
        {
        public:
            NetworkBondingManager();
            ~NetworkBondingManager();

            // Interface management
            bool addInterface(const std::string& name, const std::string& ip, uint16 port);
            bool removeInterface(const std::string& name);
            bool setInterfaceActive(const std::string& name, bool active);
            bool setPrimaryInterface(const std::string& name);

            // Configuration
            void setBondingMode(BondingMode mode);
            void setHashPolicy(HashPolicy policy);
            void setMiiMonInterval(uint32 interval_ms);
            void setFailoverTimeout(uint32 timeout_ms);

            // Bonding operations
            auto selectInterfaceForSend(const IPP& target) -> NetworkInterface*;
            auto selectInterfaceForReceive() -> NetworkInterface*;
            bool validateInterfaceHealth(const std::string& name);

            // Statistics and monitoring
            auto getStats() -> BondingStats;
            auto getInterfaceStats(const std::string& name) -> NetworkInterface*;
            void resetStats();
            void logStats();

            // Health monitoring
            void startHealthMonitoring();
            void stopHealthMonitoring();
            void checkInterfaceHealth();

            // Initialization
            bool initialize();
            void shutdown();

            // Accessors
            auto getActiveInterfaces() -> std::vector<NetworkInterface*>;
            auto getAllInterfaces() -> std::vector<NetworkInterface*>;
            auto getBondingMode() -> BondingMode { return bondingMode_; }
            auto getHashPolicy() -> HashPolicy { return hashPolicy_; }

        private:
            // Configuration
            BondingMode bondingMode_;
            HashPolicy hashPolicy_;
            uint32 miiMonInterval_;
            uint32 failoverTimeout_;

            // Interface management
            std::unordered_map<std::string, std::unique_ptr<NetworkInterface>> interfaces_;
            std::string primaryInterface_;
            std::mutex interfacesMutex_;

            // Statistics
            BondingStats stats_;

            // Health monitoring
            std::atomic<bool> healthMonitoringActive_{false};
            std::thread healthMonitorThread_;

            // Hash calculation for load balancing
            auto calculateHash(const IPP& target) -> uint32;
            auto selectInterfaceByHash(uint32 hash) -> NetworkInterface*;
            auto selectInterfaceRoundRobin() -> NetworkInterface*;
            auto selectPrimaryInterface() -> NetworkInterface*;

            // Interface health checks
            bool pingInterface(const NetworkInterface& interface);
            void handleInterfaceFailure(const std::string& name);
            void handleInterfaceRecovery(const std::string& name);

            // Internal counters
            std::atomic<uint32> roundRobinCounter_{0};
        };

        // Multi-path socket wrapper for UDP
        class MultiPathUDPSocket
        {
        public:
            using ReceiveFn = std::function<void(const std::error_code&, std::span<uint8>, IPP)>;

            MultiPathUDPSocket(asio::io_context& io_context, NetworkBondingManager& bondingManager);
            ~MultiPathUDPSocket();

            bool bindToInterfaces(const std::vector<std::pair<std::string, uint16>>& interfaces);
            void send(const IPP& target, std::span<uint8> buffer);
            void startReceiving(const ReceiveFn& onReceiveFn);
            void stopReceiving();

            auto getStats() -> BondingStats;

        private:
            asio::io_context& io_context_;
            NetworkBondingManager& bondingManager_;
            std::vector<std::unique_ptr<asio::ip::udp::socket>> sockets_;
            std::vector<NetworkBuffer> receiveBuffers_;
            std::atomic<bool> receiving_{false};
            ReceiveFn receiveFn_;
            asio::ip::udp::endpoint remoteEndpoint_;

            void startReceiveOnSocket(size_t socketIndex);
        };

        // Multi-path TCP connection manager
        class MultiPathTCPManager
        {
        public:
            MultiPathTCPManager(asio::io_context& io_context, NetworkBondingManager& bondingManager);
            ~MultiPathTCPManager();

            bool enableMPTCP();
            auto createConnection(const std::string& host, uint16 port) -> std::shared_ptr<asio::ip::tcp::socket>;
            void setConnectionTimeout(uint32 timeout_ms);

            auto getStats() -> BondingStats;

        private:
            asio::io_context& io_context_;
            NetworkBondingManager& bondingManager_;
            uint32 connectionTimeout_;
            std::atomic<bool> mptcpEnabled_{false};
        };

        // Global bonding manager instance
        auto getGlobalBondingManager() -> NetworkBondingManager&;

        // Bonding initialization/shutdown
        void initializeNetworkBonding();
        void shutdownNetworkBonding();

        // Utility functions
        auto bondingModeToString(BondingMode mode) -> std::string;
        auto hashPolicyToString(HashPolicy policy) -> std::string;
        auto stringToBondingMode(const std::string& mode) -> BondingMode;
        auto stringToHashPolicy(const std::string& policy) -> HashPolicy;

    } // namespace bonding
} // namespace network