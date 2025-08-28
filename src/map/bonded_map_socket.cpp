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

#include "bonded_map_socket.h"

#include "common/logging.h"
#include "common/settings.h"

BondedMapSocket::BondedMapSocket(asio::io_context& io_context, const uint16 port, const ReceiveFn& onReceiveFn)
: port_(port)
, io_context_(io_context)
, socket_(io_context)
, isRunning(true)
, bondingEnabled_(false)
, onReceiveFn_(onReceiveFn)
{
    TracyZoneScoped;

    ShowInfoFmt("BondedMapSocket: Starting on port {}", port_);

    // Check if bonding is enabled in configuration
    if (settings::get<bool>("network.BONDING_ENABLED", false))
    {
        initializeBonding();
    }

    // Initialize standard socket as fallback
    if (!bondingEnabled_)
    {
        asio::ip::udp::endpoint listen_endpoint(asio::ip::udp::v4(), port_);
        socket_.open(listen_endpoint.protocol());
        socket_.bind(listen_endpoint);
        startReceive();
    }
}

BondedMapSocket::~BondedMapSocket()
{
    TracyZoneScoped;

    if (bondedSocket_)
    {
        bondedSocket_->stopReceiving();
    }

    if (socket_.is_open())
    {
        socket_.close();
    }
}

void BondedMapSocket::initializeBonding()
{
    TracyZoneScoped;

    try
    {
        // Initialize network bonding system
        network::bonding::initializeNetworkBonding();
        
        auto& bondingManager = network::bonding::getGlobalBondingManager();
        
        // Create multi-path UDP socket
        bondedSocket_ = std::make_unique<network::bonding::MultiPathUDPSocket>(io_context_, bondingManager);
        
        // Configure interfaces from settings
        std::vector<std::pair<std::string, uint16>> interfaces;
        
        const auto interfaceConfig = settings::get<std::string>("network.BONDING_INTERFACES", "");
        if (!interfaceConfig.empty())
        {
            // Parse interface configuration: "eth0:192.168.1.100,eth1:192.168.1.101"
            std::string current = interfaceConfig;
            size_t pos = 0;
            
            while ((pos = current.find(',')) != std::string::npos || !current.empty())
            {
                std::string interfaceEntry = (pos != std::string::npos) ? current.substr(0, pos) : current;
                
                size_t colonPos = interfaceEntry.find(':');
                if (colonPos != std::string::npos)
                {
                    std::string interfaceName = interfaceEntry.substr(0, colonPos);
                    std::string interfaceIP = interfaceEntry.substr(colonPos + 1);
                    
                    // Add interface to bonding manager
                    bondingManager.addInterface(interfaceName, interfaceIP, port_);
                    interfaces.emplace_back(interfaceName, port_);
                    
                    ShowInfoFmt("BondedMapSocket: Added interface {} ({})", interfaceName, interfaceIP);
                }
                
                if (pos == std::string::npos) break;
                current = current.substr(pos + 1);
            }
        }
        
        // Bind to interfaces
        if (!interfaces.empty() && bondedSocket_->bindToInterfaces(interfaces))
        {
            bondingEnabled_ = true;
            bondedSocket_->startReceiving(onReceiveFn_);
            ShowInfo("BondedMapSocket: Network bonding enabled successfully");
        }
        else
        {
            ShowWarning("BondedMapSocket: Failed to enable network bonding, falling back to standard socket");
            bondedSocket_.reset();
        }
    }
    catch (const std::exception& e)
    {
        ShowErrorFmt("BondedMapSocket: Bonding initialization failed: {}", e.what());
        bondedSocket_.reset();
    }
}

bool BondedMapSocket::enableBonding()
{
    TracyZoneScoped;

    if (bondingEnabled_)
    {
        return true;
    }

    initializeBonding();
    return bondingEnabled_;
}

void BondedMapSocket::disableBonding()
{
    TracyZoneScoped;

    if (bondedSocket_)
    {
        bondedSocket_->stopReceiving();
        bondedSocket_.reset();
    }

    bondingEnabled_ = false;

    // Re-initialize standard socket if needed
    if (!socket_.is_open())
    {
        asio::ip::udp::endpoint listen_endpoint(asio::ip::udp::v4(), port_);
        socket_.open(listen_endpoint.protocol());
        socket_.bind(listen_endpoint);
        startReceive();
    }

    ShowInfo("BondedMapSocket: Network bonding disabled");
}

void BondedMapSocket::startReceive()
{
    TracyZoneScoped;

    if (bondingEnabled_)
    {
        return; // Bonded socket handles receiving
    }

    socket_.async_receive_from(
        asio::buffer(buffer_), remote_endpoint_,
        [this](const std::error_code& ec, std::size_t bytes_recvd)
        {
            // NOTE: ASIO returns the address in host byte order, but we store it in network byte order,
            //     : so we convert it back.
            const auto sender_ip   = htonl(remote_endpoint_.address().to_v4().to_uint());
            const auto sender_port = remote_endpoint_.port();
            const auto ipp         = IPP(sender_ip, sender_port);

            const auto buffer = std::span(buffer_.data(), bytes_recvd);

            DebugPacketsFmt("Received {} bytes from {}", buffer.size(), ipp.toString());

            onReceiveFn_(ec, buffer, ipp);

            if (!io_context_.stopped() && socket_.is_open())
            {
                startReceive(); // Queue up more work
            }
        });
}

void BondedMapSocket::recvFor(timer::duration duration)
{
    TracyZoneScoped;

    // Blocks until the duration is up
    io_context_.run_for(duration);

    // Once run_for() or run() return the io_context enters a stopped state,
    // even if there are still pending asynchronous operations. You need to
    // call restart() to clear that state before you can run it again.
    if (isRunning)
    {
        io_context_.restart();
    }
}

void BondedMapSocket::send(const IPP& ipp, std::span<uint8> buffer)
{
    TracyZoneScoped;

    DebugPacketsFmt("Sending {} bytes to {}", buffer.size(), ipp.toString());

    if (bondingEnabled_ && bondedSocket_)
    {
        // Use bonded socket for improved performance
        bondedSocket_->send(ipp, buffer);
    }
    else
    {
        // Use standard socket
        const auto ip       = ntohl(ipp.getIP());
        const auto endpoint = asio::ip::udp::endpoint(asio::ip::address_v4(ip), ipp.getPort());

        socket_.async_send_to(asio::buffer(buffer), endpoint,
        [](const std::error_code& ec, std::size_t /*bytes_sent*/)
        {
            if (ec)
            {
                ShowErrorFmt("Error sending data: {}", ec.message());
            }
        });
    }

    // This will only be called in the middle of a doSocketsFor() call, so we don't
    // need to enqueue more work when we're done here.
}

void BondedMapSocket::requestExit()
{
    isRunning = false;
    io_context_.stop();
}

auto BondedMapSocket::getBondingStats() -> network::bonding::BondingStats
{
    if (bondedSocket_)
    {
        return bondedSocket_->getStats();
    }
    return network::bonding::BondingStats{}; // Return empty stats
}