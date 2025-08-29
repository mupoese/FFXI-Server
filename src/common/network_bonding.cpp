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

#include "network_bonding.h"
#include "settings.h"
#include "tracy.h"

#include <algorithm>
#include <cstring>
#include <random>
#include <system_error>
#include <thread>

#ifdef __linux__
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <ifaddrs.h>
#include <net/if.h>
#endif

namespace network
{
    namespace bonding
    {
        namespace
        {
            std::unique_ptr<NetworkBondingManager> g_bondingManager = nullptr;
        }

        NetworkBondingManager::NetworkBondingManager()
        : bondingMode_(BondingMode::BALANCE_XOR)
        , hashPolicy_(HashPolicy::LAYER3_4)
        , miiMonInterval_(100)
        , failoverTimeout_(5000)
        , primaryInterface_("")
        {
            TracyZoneScoped;
            ShowInfo("NetworkBondingManager: Initializing network bonding system");
        }

        NetworkBondingManager::~NetworkBondingManager()
        {
            TracyZoneScoped;
            shutdown();
        }

        bool NetworkBondingManager::initialize()
        {
            TracyZoneScoped;

            std::lock_guard<std::mutex> lock(interfacesMutex_);

            // Load configuration from settings
            if (settings::exists("network.BONDING_MODE"))
            {
                const auto modeStr = settings::get<std::string>("network.BONDING_MODE");
                bondingMode_ = stringToBondingMode(modeStr);
            }

            if (settings::exists("network.BONDING_HASH_POLICY"))
            {
                const auto policyStr = settings::get<std::string>("network.BONDING_HASH_POLICY");
                hashPolicy_ = stringToHashPolicy(policyStr);
            }

            if (settings::exists("network.BONDING_MII_MON_INTERVAL"))
            {
                miiMonInterval_ = settings::get<uint32>("network.BONDING_MII_MON_INTERVAL");
            }

            if (settings::exists("network.BONDING_FAILOVER_TIMEOUT"))
            {
                failoverTimeout_ = settings::get<uint32>("network.BONDING_FAILOVER_TIMEOUT");
            }

            // Load explicit interfaces from configuration
            if (settings::exists("network.BONDING_INTERFACES"))
            {
                // Configuration format: "eth0:192.168.1.100,eth1:192.168.1.101"
                const auto interfaceList = settings::get<std::string>("network.BONDING_INTERFACES");
                // Parse and add interfaces from configuration
                // This is a placeholder for configuration-based interface setup
                ShowInfoFmt("NetworkBondingManager: Interface configuration: {}", interfaceList);
            }

            ShowInfoFmt("NetworkBondingManager: Initialized with mode: {}, hash policy: {}", 
                       bondingModeToString(bondingMode_), hashPolicyToString(hashPolicy_));

            startHealthMonitoring();
            return true;
        }

        void NetworkBondingManager::shutdown()
        {
            TracyZoneScoped;

            stopHealthMonitoring();

            std::lock_guard<std::mutex> lock(interfacesMutex_);
            interfaces_.clear();
            primaryInterface_.clear();

            ShowInfo("NetworkBondingManager: Shutdown complete");
        }

        bool NetworkBondingManager::addInterface(const std::string& name, const std::string& ip, uint16 port)
        {
            TracyZoneScoped;

            std::lock_guard<std::mutex> lock(interfacesMutex_);

            if (interfaces_.find(name) != interfaces_.end())
            {
                ShowWarningFmt("NetworkBondingManager: Interface {} already exists", name);
                return false;
            }

            auto interface = std::make_unique<NetworkInterface>(name, ip, port);
            
            // Set as primary if it's the first interface
            if (interfaces_.empty())
            {
                interface->is_primary = true;
                primaryInterface_ = name;
            }

            interfaces_[name] = std::move(interface);
            stats_.active_interfaces = getActiveInterfaces().size();

            ShowInfoFmt("NetworkBondingManager: Added interface {} ({}:{})", name, ip, port);
            return true;
        }

        bool NetworkBondingManager::removeInterface(const std::string& name)
        {
            TracyZoneScoped;

            std::lock_guard<std::mutex> lock(interfacesMutex_);

            auto it = interfaces_.find(name);
            if (it == interfaces_.end())
            {
                return false;
            }

            // If removing primary interface, select a new one
            if (primaryInterface_ == name && interfaces_.size() > 1)
            {
                for (const auto& [ifaceName, iface] : interfaces_)
                {
                    if (ifaceName != name && iface->is_active)
                    {
                        setPrimaryInterface(ifaceName);
                        break;
                    }
                }
            }

            interfaces_.erase(it);
            stats_.active_interfaces = getActiveInterfaces().size();

            ShowInfoFmt("NetworkBondingManager: Removed interface {}", name);
            return true;
        }

        bool NetworkBondingManager::setInterfaceActive(const std::string& name, bool active)
        {
            TracyZoneScoped;

            std::lock_guard<std::mutex> lock(interfacesMutex_);

            auto it = interfaces_.find(name);
            if (it == interfaces_.end())
            {
                return false;
            }

            it->second->is_active = active;
            stats_.active_interfaces = getActiveInterfaces().size();

            if (!active)
            {
                handleInterfaceFailure(name);
            }
            else
            {
                handleInterfaceRecovery(name);
            }

            ShowInfoFmt("NetworkBondingManager: Interface {} set to {}", name, active ? "active" : "inactive");
            return true;
        }

        bool NetworkBondingManager::setPrimaryInterface(const std::string& name)
        {
            TracyZoneScoped;

            std::lock_guard<std::mutex> lock(interfacesMutex_);

            auto it = interfaces_.find(name);
            if (it == interfaces_.end() || !it->second->is_active)
            {
                return false;
            }

            // Clear previous primary
            if (!primaryInterface_.empty())
            {
                auto prevIt = interfaces_.find(primaryInterface_);
                if (prevIt != interfaces_.end())
                {
                    prevIt->second->is_primary = false;
                }
            }

            it->second->is_primary = true;
            primaryInterface_ = name;

            ShowInfoFmt("NetworkBondingManager: Set primary interface to {}", name);
            return true;
        }

        void NetworkBondingManager::setBondingMode(BondingMode mode)
        {
            bondingMode_ = mode;
            ShowInfoFmt("NetworkBondingManager: Set bonding mode to {}", bondingModeToString(mode));
        }

        void NetworkBondingManager::setHashPolicy(HashPolicy policy)
        {
            hashPolicy_ = policy;
            ShowInfoFmt("NetworkBondingManager: Set hash policy to {}", hashPolicyToString(policy));
        }

        auto NetworkBondingManager::selectInterfaceForSend(const IPP& target) -> NetworkInterface*
        {
            TracyZoneScoped;

            std::lock_guard<std::mutex> lock(interfacesMutex_);

            auto activeInterfaces = getActiveInterfaces();
            if (activeInterfaces.empty())
            {
                return nullptr;
            }

            switch (bondingMode_)
            {
                case BondingMode::BALANCE_RR:
                    return selectInterfaceRoundRobin();

                case BondingMode::ACTIVE_BACKUP:
                    return selectPrimaryInterface();

                case BondingMode::BALANCE_XOR:
                case BondingMode::LACP_802_3AD:
                {
                    const auto hash = calculateHash(target);
                    return selectInterfaceByHash(hash);
                }

                case BondingMode::BROADCAST:
                    // For broadcast, we would send on all interfaces
                    // Return the primary for single send operations
                    return selectPrimaryInterface();

                default:
                    return selectPrimaryInterface();
            }
        }

        auto NetworkBondingManager::selectInterfaceForReceive() -> NetworkInterface*
        {
            TracyZoneScoped;

            // For receive operations, typically use primary interface
            // unless implementing specific receive load balancing
            return selectPrimaryInterface();
        }

        auto NetworkBondingManager::calculateHash(const IPP& target) -> uint32
        {
            TracyZoneScoped;

            uint32 hash = 0;

            switch (hashPolicy_)
            {
                case HashPolicy::LAYER2:
                    // Use a simple hash of the IP for layer 2 simulation
                    hash = target.getIP();
                    break;

                case HashPolicy::LAYER3_4:
                    // Combine IP and port for layer 3+4 hashing
                    hash = target.getIP() ^ (static_cast<uint32>(target.getPort()) << 16);
                    break;

                case HashPolicy::LAYER2_3:
                    // IP-based hashing for layer 2+3
                    hash = target.getIP() * 31;
                    break;

                default:
                    hash = target.getIP();
                    break;
            }

            return hash;
        }

        auto NetworkBondingManager::selectInterfaceByHash(uint32 hash) -> NetworkInterface*
        {
            TracyZoneScoped;

            auto activeInterfaces = getActiveInterfaces();
            if (activeInterfaces.empty())
            {
                return nullptr;
            }

            const auto index = hash % activeInterfaces.size();
            return activeInterfaces[index];
        }

        auto NetworkBondingManager::selectInterfaceRoundRobin() -> NetworkInterface*
        {
            TracyZoneScoped;

            auto activeInterfaces = getActiveInterfaces();
            if (activeInterfaces.empty())
            {
                return nullptr;
            }

            const auto index = roundRobinCounter_.fetch_add(1) % activeInterfaces.size();
            return activeInterfaces[index];
        }

        auto NetworkBondingManager::selectPrimaryInterface() -> NetworkInterface*
        {
            TracyZoneScoped;

            if (primaryInterface_.empty())
            {
                auto activeInterfaces = getActiveInterfaces();
                return activeInterfaces.empty() ? nullptr : activeInterfaces[0];
            }

            auto it = interfaces_.find(primaryInterface_);
            if (it != interfaces_.end() && it->second->is_active)
            {
                return it->second.get();
            }

            // Primary interface is not active, select first active interface
            auto activeInterfaces = getActiveInterfaces();
            return activeInterfaces.empty() ? nullptr : activeInterfaces[0];
        }

        void NetworkBondingManager::startHealthMonitoring()
        {
            TracyZoneScoped;

            if (healthMonitoringActive_.exchange(true))
            {
                return; // Already running
            }

            healthMonitorThread_ = std::thread([this]()
            {
                TracySetThreadName("NetworkBondingHealthMonitor");
                
                while (healthMonitoringActive_)
                {
                    checkInterfaceHealth();
                    std::this_thread::sleep_for(std::chrono::milliseconds(miiMonInterval_));
                }
            });

            ShowInfo("NetworkBondingManager: Health monitoring started");
        }

        void NetworkBondingManager::stopHealthMonitoring()
        {
            TracyZoneScoped;

            if (!healthMonitoringActive_.exchange(false))
            {
                return; // Already stopped
            }

            if (healthMonitorThread_.joinable())
            {
                healthMonitorThread_.join();
            }

            ShowInfo("NetworkBondingManager: Health monitoring stopped");
        }

        void NetworkBondingManager::checkInterfaceHealth()
        {
            TracyZoneScoped;

            std::lock_guard<std::mutex> lock(interfacesMutex_);

            for (auto& [name, interface] : interfaces_)
            {
                if (!interface->is_active)
                {
                    continue;
                }

                const bool isHealthy = validateInterfaceHealth(name);
                if (!isHealthy)
                {
                    ShowWarningFmt("NetworkBondingManager: Interface {} health check failed", name);
                    handleInterfaceFailure(name);
                }
            }
        }

        bool NetworkBondingManager::validateInterfaceHealth(const std::string& name)
        {
            TracyZoneScoped;

            auto it = interfaces_.find(name);
            if (it == interfaces_.end())
            {
                return false;
            }

            const auto& interface = *it->second;

            // Check if interface has been idle too long
            const auto currentTime = timer::get_utc_microseconds();
            const auto idleTime = currentTime - interface.last_activity;
            const auto maxIdleTime = failoverTimeout_ * 1000; // Convert to microseconds

            if (idleTime > maxIdleTime)
            {
                return false;
            }

            // Additional health checks could be added here
            // e.g., ping tests, link status checks, etc.

            return true;
        }

        void NetworkBondingManager::handleInterfaceFailure(const std::string& name)
        {
            TracyZoneScoped;

            stats_.interface_failures++;

            // If the failed interface is primary, failover to another
            if (primaryInterface_ == name)
            {
                auto activeInterfaces = getActiveInterfaces();
                for (auto* iface : activeInterfaces)
                {
                    if (iface->name != name)
                    {
                        setPrimaryInterface(iface->name);
                        stats_.failover_events++;
                        ShowInfoFmt("NetworkBondingManager: Failover from {} to {}", name, iface->name);
                        break;
                    }
                }
            }
        }

        void NetworkBondingManager::handleInterfaceRecovery(const std::string& name)
        {
            TracyZoneScoped;
            ShowInfoFmt("NetworkBondingManager: Interface {} recovered", name);
        }

        auto NetworkBondingManager::getActiveInterfaces() -> std::vector<NetworkInterface*>
        {
            std::vector<NetworkInterface*> active;
            for (auto& [name, interface] : interfaces_)
            {
                if (interface->is_active)
                {
                    active.push_back(interface.get());
                }
            }
            return active;
        }

        auto NetworkBondingManager::getAllInterfaces() -> std::vector<NetworkInterface*>
        {
            std::vector<NetworkInterface*> all;
            for (auto& [name, interface] : interfaces_)
            {
                all.push_back(interface.get());
            }
            return all;
        }

        auto NetworkBondingManager::getStats() -> BondingStats
        {
            return stats_;
        }

        auto NetworkBondingManager::getInterfaceStats(const std::string& name) -> NetworkInterface*
        {
            std::lock_guard<std::mutex> lock(interfacesMutex_);
            auto it = interfaces_.find(name);
            return (it != interfaces_.end()) ? it->second.get() : nullptr;
        }

        void NetworkBondingManager::resetStats()
        {
            stats_.reset();
        }

        void NetworkBondingManager::logStats()
        {
            const auto stats = getStats();
            ShowInfoFmt("NetworkBonding Stats - Bytes: {}S/{}R, Packets: {}S/{}R, Errors: {}, Interfaces: {}", 
                       stats.total_bytes_sent.load(), stats.total_bytes_received.load(),
                       stats.total_packets_sent.load(), stats.total_packets_received.load(),
                       stats.total_errors.load(), stats.active_interfaces.load());
        }

        // Utility functions
        auto bondingModeToString(BondingMode mode) -> std::string
        {
            switch (mode)
            {
                case BondingMode::BALANCE_RR: return "balance-rr";
                case BondingMode::ACTIVE_BACKUP: return "active-backup";
                case BondingMode::BALANCE_XOR: return "balance-xor";
                case BondingMode::BROADCAST: return "broadcast";
                case BondingMode::LACP_802_3AD: return "802.3ad";
                case BondingMode::BALANCE_TLB: return "balance-tlb";
                case BondingMode::BALANCE_ALB: return "balance-alb";
                default: return "unknown";
            }
        }

        auto hashPolicyToString(HashPolicy policy) -> std::string
        {
            switch (policy)
            {
                case HashPolicy::LAYER2: return "layer2";
                case HashPolicy::LAYER3_4: return "layer3+4";
                case HashPolicy::LAYER2_3: return "layer2+3";
                case HashPolicy::ENCAP2_3: return "encap2+3";
                case HashPolicy::ENCAP3_4: return "encap3+4";
                default: return "unknown";
            }
        }

        auto stringToBondingMode(const std::string& mode) -> BondingMode
        {
            if (mode == "balance-rr") return BondingMode::BALANCE_RR;
            if (mode == "active-backup") return BondingMode::ACTIVE_BACKUP;
            if (mode == "balance-xor") return BondingMode::BALANCE_XOR;
            if (mode == "broadcast") return BondingMode::BROADCAST;
            if (mode == "802.3ad") return BondingMode::LACP_802_3AD;
            if (mode == "balance-tlb") return BondingMode::BALANCE_TLB;
            if (mode == "balance-alb") return BondingMode::BALANCE_ALB;
            return BondingMode::BALANCE_XOR; // Default
        }

        auto stringToHashPolicy(const std::string& policy) -> HashPolicy
        {
            if (policy == "layer2") return HashPolicy::LAYER2;
            if (policy == "layer3+4") return HashPolicy::LAYER3_4;
            if (policy == "layer2+3") return HashPolicy::LAYER2_3;
            if (policy == "encap2+3") return HashPolicy::ENCAP2_3;
            if (policy == "encap3+4") return HashPolicy::ENCAP3_4;
            return HashPolicy::LAYER3_4; // Default
        }

        // Global instance management
        auto getGlobalBondingManager() -> NetworkBondingManager&
        {
            if (!g_bondingManager)
            {
                g_bondingManager = std::make_unique<NetworkBondingManager>();
            }
            return *g_bondingManager;
        }

        void initializeNetworkBonding()
        {
            auto& manager = getGlobalBondingManager();
            manager.initialize();
        }

        void shutdownNetworkBonding()
        {
            if (g_bondingManager)
            {
                g_bondingManager->shutdown();
                g_bondingManager.reset();
            }
        }

        // Multi-path UDP socket implementation
        MultiPathUDPSocket::MultiPathUDPSocket(asio::io_context& io_context, NetworkBondingManager& bondingManager)
        : io_context_(io_context)
        , bondingManager_(bondingManager)
        {
            TracyZoneScoped;
        }

        MultiPathUDPSocket::~MultiPathUDPSocket()
        {
            TracyZoneScoped;
            stopReceiving();
        }

        bool MultiPathUDPSocket::bindToInterfaces(const std::vector<std::pair<std::string, uint16>>& interfaces)
        {
            TracyZoneScoped;

            for (const auto& [interfaceName, port] : interfaces)
            {
                try
                {
                    auto socket = std::make_unique<asio::ip::udp::socket>(io_context_);
                    
                    // Find the interface in bonding manager
                    auto* interface = bondingManager_.getInterfaceStats(interfaceName);
                    if (!interface)
                    {
                        ShowWarningFmt("MultiPathUDPSocket: Interface {} not found in bonding manager", interfaceName);
                        continue;
                    }

                    asio::ip::udp::endpoint endpoint(asio::ip::address::from_string(interface->ip_address), port);
                    socket->open(endpoint.protocol());
                    socket->bind(endpoint);

                    sockets_.push_back(std::move(socket));
                    receiveBuffers_.emplace_back();

                    ShowInfoFmt("MultiPathUDPSocket: Bound to interface {} ({}:{})", interfaceName, interface->ip_address, port);
                }
                catch (const std::exception& e)
                {
                    ShowErrorFmt("MultiPathUDPSocket: Failed to bind to interface {}: {}", interfaceName, e.what());
                    return false;
                }
            }

            return !sockets_.empty();
        }

        void MultiPathUDPSocket::send(const IPP& target, std::span<uint8> buffer)
        {
            TracyZoneScoped;

            auto* interface = bondingManager_.selectInterfaceForSend(target);
            if (!interface)
            {
                ShowError("MultiPathUDPSocket: No active interface available for send");
                return;
            }

            // Find the socket for this interface
            size_t socketIndex = 0;
            auto activeInterfaces = bondingManager_.getActiveInterfaces();
            for (size_t i = 0; i < activeInterfaces.size() && i < sockets_.size(); ++i)
            {
                if (activeInterfaces[i] == interface)
                {
                    socketIndex = i;
                    break;
                }
            }

            if (socketIndex >= sockets_.size())
            {
                ShowError("MultiPathUDPSocket: Socket not found for selected interface");
                return;
            }

            try
            {
                const auto ip = ntohl(target.getIP());
                const auto endpoint = asio::ip::udp::endpoint(asio::ip::address_v4(ip), target.getPort());

                sockets_[socketIndex]->async_send_to(asio::buffer(buffer), endpoint,
                    [interface](const std::error_code& ec, std::size_t bytes_sent)
                    {
                        if (!ec)
                        {
                            interface->bytes_sent += bytes_sent;
                            interface->packets_sent++;
                            interface->last_activity = timer::get_utc_microseconds();
                        }
                        else
                        {
                            interface->errors++;
                            ShowErrorFmt("MultiPathUDPSocket: Send error: {}", ec.message());
                        }
                    });
            }
            catch (const std::exception& e)
            {
                interface->errors++;
                ShowErrorFmt("MultiPathUDPSocket: Send exception: {}", e.what());
            }
        }

        void MultiPathUDPSocket::startReceiving(const ReceiveFn& onReceiveFn)
        {
            TracyZoneScoped;

            receiveFn_ = onReceiveFn;
            receiving_ = true;

            for (size_t i = 0; i < sockets_.size(); ++i)
            {
                startReceiveOnSocket(i);
            }
        }

        void MultiPathUDPSocket::stopReceiving()
        {
            TracyZoneScoped;

            receiving_ = false;
            for (auto& socket : sockets_)
            {
                if (socket->is_open())
                {
                    socket->close();
                }
            }
        }

        void MultiPathUDPSocket::startReceiveOnSocket(size_t socketIndex)
        {
            TracyZoneScoped;

            if (socketIndex >= sockets_.size() || !receiving_)
            {
                return;
            }

            auto& socket = sockets_[socketIndex];
            auto& buffer = receiveBuffers_[socketIndex];

            socket->async_receive_from(
                asio::buffer(buffer), remoteEndpoint_,
                [this, socketIndex](const std::error_code& ec, std::size_t bytes_recvd)
                {
                    if (!ec && receiving_)
                    {
                        const auto sender_ip = htonl(remoteEndpoint_.address().to_v4().to_uint());
                        const auto sender_port = remoteEndpoint_.port();
                        const auto ipp = IPP(sender_ip, sender_port);

                        const auto bufferSpan = std::span(receiveBuffers_[socketIndex].data(), bytes_recvd);

                        // Update interface statistics
                        auto activeInterfaces = bondingManager_.getActiveInterfaces();
                        if (socketIndex < activeInterfaces.size())
                        {
                            auto* interface = activeInterfaces[socketIndex];
                            interface->bytes_received += bytes_recvd;
                            interface->packets_received++;
                            interface->last_activity = timer::get_utc_microseconds();
                        }

                        receiveFn_(ec, bufferSpan, ipp);

                        // Continue receiving
                        startReceiveOnSocket(socketIndex);
                    }
                    else if (ec && receiving_)
                    {
                        ShowErrorFmt("MultiPathUDPSocket: Receive error on socket {}: {}", socketIndex, ec.message());
                        
                        // Update error statistics
                        auto activeInterfaces = bondingManager_.getActiveInterfaces();
                        if (socketIndex < activeInterfaces.size())
                        {
                            activeInterfaces[socketIndex]->errors++;
                        }
                    }
                });
        }

        auto MultiPathUDPSocket::getStats() -> BondingStats
        {
            return bondingManager_.getStats();
        }

        // Multi-path TCP manager implementation
        MultiPathTCPManager::MultiPathTCPManager(asio::io_context& io_context, NetworkBondingManager& bondingManager)
        : io_context_(io_context)
        , bondingManager_(bondingManager)
        , connectionTimeout_(30000)
        {
            TracyZoneScoped;
        }

        MultiPathTCPManager::~MultiPathTCPManager()
        {
            TracyZoneScoped;
        }

        bool MultiPathTCPManager::enableMPTCP()
        {
            TracyZoneScoped;

#ifdef __linux__
            // Check if MPTCP is available in the kernel
            // This would typically involve checking /proc/sys/net/mptcp/enabled
            ShowInfo("MultiPathTCPManager: Attempting to enable MPTCP support");
            mptcpEnabled_ = true;
            return true;
#else
            ShowWarning("MultiPathTCPManager: MPTCP not supported on this platform");
            return false;
#endif
        }

        auto MultiPathTCPManager::createConnection(const std::string& host, uint16 port) -> std::shared_ptr<asio::ip::tcp::socket>
        {
            TracyZoneScoped;

            auto socket = std::make_shared<asio::ip::tcp::socket>(io_context_);

            try
            {
                asio::ip::tcp::resolver resolver(io_context_);
                auto endpoints = resolver.resolve(host, std::to_string(port));

                // For MPTCP, we would set socket options here
                if (mptcpEnabled_)
                {
#ifdef __linux__
                    // Enable MPTCP on this socket
                    // This is a placeholder for actual MPTCP socket configuration
                    ShowInfoFmt("MultiPathTCPManager: Creating MPTCP connection to {}:{}", host, port);
#endif
                }

                asio::connect(*socket, endpoints);
                return socket;
            }
            catch (const std::exception& e)
            {
                ShowErrorFmt("MultiPathTCPManager: Failed to create connection to {}:{}: {}", host, port, e.what());
                return nullptr;
            }
        }

        void MultiPathTCPManager::setConnectionTimeout(uint32 timeout_ms)
        {
            connectionTimeout_ = timeout_ms;
        }

        auto MultiPathTCPManager::getStats() -> BondingStats
        {
            return bondingManager_.getStats();
        }

    } // namespace bonding
} // namespace network