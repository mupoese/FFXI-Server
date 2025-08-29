/*
===========================================================================

  Copyright (c) 2025 LandSandBoat Dev Teams

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

#include "common/cbasetypes.h"
#include "common/network_bonding.h"
#include "common/tracy.h"

#include <memory>
#include <queue>
#include <unordered_map>
#include <vector>
#include <atomic>
#include <mutex>
#include <functional>

class CCharEntity;

namespace networking
{
    // Enhanced packet processing with network bonding integration
    namespace enhanced_packet_processing
    {
        // Packet priority levels for QoS
        enum class PacketPriority : uint8
        {
            CRITICAL = 0,    // Zone transitions, login/logout
            HIGH = 1,        // Combat, movement updates
            MEDIUM = 2,      // Chat, UI updates
            LOW = 3,         // Background updates, keepalives
            BULK = 4         // Large data transfers
        };

        // Packet processing strategies
        enum class ProcessingStrategy : uint8
        {
            IMMEDIATE = 0,   // Process immediately
            BATCH = 1,       // Batch with other packets
            DEFERRED = 2,    // Process in next tick
            BACKGROUND = 3   // Process in background thread
        };

        // Enhanced packet wrapper with metadata
        struct EnhancedPacket
        {
            std::vector<uint8> data;
            PacketPriority     priority;
            ProcessingStrategy strategy;
            uint32             sourceSessionId;
            uint32             packetId;
            std::chrono::steady_clock::time_point timestamp;
            std::chrono::steady_clock::time_point deadline;
            uint32             retryCount;
            bool               requiresAck;
            
            EnhancedPacket(std::vector<uint8>&& packetData, PacketPriority prio = PacketPriority::MEDIUM)
                : data(std::move(packetData)), priority(prio), strategy(ProcessingStrategy::IMMEDIATE)
                , sourceSessionId(0), packetId(0), timestamp(std::chrono::steady_clock::now())
                , deadline(timestamp + std::chrono::milliseconds(1000)), retryCount(0), requiresAck(false)
            {
            }
        };

        // Packet statistics for monitoring
        struct PacketStatistics
        {
            std::atomic<uint64> packetsReceived{0};
            std::atomic<uint64> packetsSent{0};
            std::atomic<uint64> packetsDropped{0};
            std::atomic<uint64> packetsRetransmitted{0};
            std::atomic<uint64> duplicatesDetected{0};
            std::atomic<double> averageProcessingTime{0.0};
            std::atomic<double> averageLatency{0.0};
            
            void reset()
            {
                packetsReceived = 0;
                packetsSent = 0;
                packetsDropped = 0;
                packetsRetransmitted = 0;
                duplicatesDetected = 0;
                averageProcessingTime = 0.0;
                averageLatency = 0.0;
            }
        };

        // Quality of Service configuration
        struct QoSConfig
        {
            uint32 maxBandwidthMbps = 100;
            uint32 criticalQueueSize = 1000;
            uint32 highQueueSize = 2000;
            uint32 mediumQueueSize = 5000;
            uint32 lowQueueSize = 10000;
            uint32 bulkQueueSize = 20000;
            
            // Timing constraints
            uint32 criticalMaxDelayMs = 10;
            uint32 highMaxDelayMs = 50;
            uint32 mediumMaxDelayMs = 200;
            uint32 lowMaxDelayMs = 1000;
            uint32 bulkMaxDelayMs = 5000;
            
            // Retry configuration
            uint32 maxRetries = 3;
            uint32 ackTimeoutMs = 500;
            bool   enableReliableDelivery = true;
        };

        // Enhanced packet queue with priority handling
        class PriorityPacketQueue
        {
        public:
            PriorityPacketQueue();
            ~PriorityPacketQueue();

            // Queue management
            void enqueue(std::unique_ptr<EnhancedPacket> packet);
            auto dequeue() -> std::unique_ptr<EnhancedPacket>;
            auto dequeueBatch(size_t maxPackets) -> std::vector<std::unique_ptr<EnhancedPacket>>;
            
            // Priority-based operations
            auto dequeueByPriority(PacketPriority priority) -> std::unique_ptr<EnhancedPacket>;
            void clearPriority(PacketPriority priority);
            
            // Queue status
            auto size() const -> size_t;
            auto sizeByPriority(PacketPriority priority) const -> size_t;
            auto isEmpty() const -> bool;
            void clear();
            
            // Configuration
            void setMaxSize(PacketPriority priority, size_t maxSize);
            void enableDropOldest(bool enable) { dropOldest_ = enable; }

        private:
            std::array<std::queue<std::unique_ptr<EnhancedPacket>>, 5> queues_;
            std::array<size_t, 5> maxSizes_;
            mutable std::mutex queueMutex_;
            bool dropOldest_;
            
            auto getPriorityIndex(PacketPriority priority) const -> size_t;
        };

        // Duplicate packet detection
        class DuplicateDetector
        {
        public:
            DuplicateDetector(size_t windowSize = 1000);
            
            auto isDuplicate(uint32 sessionId, uint32 packetId) -> bool;
            void recordPacket(uint32 sessionId, uint32 packetId);
            void cleanupOldEntries();
            
        private:
            struct PacketIdentifier
            {
                uint32 sessionId;
                uint32 packetId;
                std::chrono::steady_clock::time_point timestamp;
                
                auto operator==(const PacketIdentifier& other) const -> bool
                {
                    return sessionId == other.sessionId && packetId == other.packetId;
                }
            };
            
            std::vector<PacketIdentifier> recentPackets_;
            size_t windowSize_;
            size_t currentIndex_;
            mutable std::mutex detectorMutex_;
        };

        // Enhanced packet processor with network bonding integration
        class EnhancedPacketProcessor
        {
        public:
            EnhancedPacketProcessor();
            ~EnhancedPacketProcessor();

            // System lifecycle
            void initialize();
            void shutdown();

            // Packet processing
            void processIncomingPacket(std::vector<uint8>&& packetData, uint32 sessionId);
            void sendPacket(CCharEntity* target, std::vector<uint8>&& packetData, PacketPriority priority = PacketPriority::MEDIUM);
            void broadcastPacket(const std::vector<CCharEntity*>& targets, std::vector<uint8>&& packetData, PacketPriority priority = PacketPriority::MEDIUM);

            // Reliable delivery
            void sendReliablePacket(CCharEntity* target, std::vector<uint8>&& packetData, PacketPriority priority = PacketPriority::MEDIUM);
            void handleAcknowledgment(uint32 sessionId, uint32 packetId);

            // Quality of Service
            void setQoSConfig(const QoSConfig& config);
            auto getQoSConfig() const -> const QoSConfig& { return qosConfig_; }
            
            // Bandwidth management
            void setBandwidthLimit(uint32 mbps);
            auto getCurrentBandwidthUsage() -> double;
            void enableTrafficShaping(bool enable);

            // Network bonding integration
            void enableNetworkBonding(bool enable);
            auto selectOptimalInterface(const std::vector<uint8>& packetData) -> network::bonding::NetworkInterface*;
            void updateInterfaceMetrics();

            // Statistics and monitoring
            auto getStatistics() const -> PacketStatistics;
            void resetStatistics();
            auto getQueueStatistics() -> std::unordered_map<PacketPriority, size_t>;

            // Performance optimization
            void enableBatchProcessing(bool enable, size_t batchSize = 50);
            void setProcessingThreadCount(size_t threadCount);
            void enableAdaptiveQoS(bool enable);

            // Error handling and recovery
            void handlePacketError(const EnhancedPacket& packet, const std::string& error);
            void retransmitFailedPackets();
            
            // Callbacks for custom processing
            void setPacketHandler(PacketPriority priority, std::function<void(const EnhancedPacket&)> handler);
            void setErrorHandler(std::function<void(const EnhancedPacket&, const std::string&)> handler);

        private:
            // Core components
            std::unique_ptr<PriorityPacketQueue> incomingQueue_;
            std::unique_ptr<PriorityPacketQueue> outgoingQueue_;
            std::unique_ptr<DuplicateDetector>   duplicateDetector_;
            
            // Network bonding integration
            network::bonding::NetworkBondingManager* bondingManager_;
            bool networkBondingEnabled_;
            
            // Configuration
            QoSConfig qosConfig_;
            bool      initialized_;
            bool      batchProcessingEnabled_;
            size_t    batchSize_;
            bool      trafficShapingEnabled_;
            bool      adaptiveQoSEnabled_;
            
            // Threading and processing
            std::vector<std::thread> processingThreads_;
            std::atomic<bool>        shouldStop_;
            size_t                   threadCount_;
            
            // Statistics
            mutable PacketStatistics statistics_;
            mutable std::mutex       statisticsMutex_;
            
            // Reliable delivery tracking
            struct PendingAck
            {
                std::unique_ptr<EnhancedPacket> packet;
                std::chrono::steady_clock::time_point sentTime;
                uint32 retryCount;
            };
            
            std::unordered_map<uint64, PendingAck> pendingAcks_; // Key: sessionId << 32 | packetId
            mutable std::mutex pendingAcksMutex_;
            
            // Packet handlers
            std::array<std::function<void(const EnhancedPacket&)>, 5> packetHandlers_;
            std::function<void(const EnhancedPacket&, const std::string&)> errorHandler_;
            
            // Bandwidth tracking
            struct BandwidthTracker
            {
                std::chrono::steady_clock::time_point lastUpdate;
                uint64 bytesTransferred;
                double currentUsageMbps;
            } bandwidthTracker_;
            
            mutable std::mutex bandwidthMutex_;
            
            // Internal methods
            void processingLoop(size_t threadId);
            void processPacketBatch(std::vector<std::unique_ptr<EnhancedPacket>>&& batch);
            void processIndividualPacket(std::unique_ptr<EnhancedPacket> packet);
            
            auto generatePacketId() -> uint32;
            auto createPacketKey(uint32 sessionId, uint32 packetId) -> uint64;
            void updateBandwidthUsage(size_t bytes);
            void enforceQoSLimits();
            
            auto shouldDropPacket(const EnhancedPacket& packet) -> bool;
            auto calculateAdaptivePriority(const EnhancedPacket& packet) -> PacketPriority;
            void optimizeQueueSizes();
            
            // Network bonding helpers
            auto selectInterfaceForPacket(const EnhancedPacket& packet) -> network::bonding::NetworkInterface*;
            void balanceLoadAcrossInterfaces();
        };

        // Session-specific packet management
        class SessionPacketManager
        {
        public:
            explicit SessionPacketManager(uint32 sessionId);
            ~SessionPacketManager();

            // Packet flow control
            void setFlowControlWindow(size_t windowSize);
            auto canSendPacket() -> bool;
            void onPacketSent();
            void onAckReceived();

            // Congestion control
            void handleCongestion();
            void handlePacketLoss();
            auto getCongestionWindow() -> size_t;

            // Statistics
            auto getRoundTripTime() -> double;
            auto getPacketLossRate() -> double;
            void updateRTT(double rtt);

        private:
            uint32 sessionId_;
            size_t flowControlWindow_;
            size_t congestionWindow_;
            size_t packetsInFlight_;
            
            // RTT tracking
            double smoothedRTT_;
            double rttVariation_;
            
            // Loss tracking
            uint64 packetsSent_;
            uint64 packetsLost_;
            
            mutable std::mutex sessionMutex_;
        };

        // Global enhanced packet processing system
        auto getEnhancedPacketProcessor() -> EnhancedPacketProcessor&;
        void initializeEnhancedPacketProcessing();
        void shutdownEnhancedPacketProcessing();

        // Utility functions
        auto getPacketPriorityName(PacketPriority priority) -> std::string;
        auto getProcessingStrategyName(ProcessingStrategy strategy) -> std::string;
        auto calculatePacketPriority(const std::vector<uint8>& packetData) -> PacketPriority;
        auto estimatePacketSize(const std::vector<uint8>& packetData) -> size_t;

        // Performance helpers
        void optimizePacketProcessing();
        void analyzePacketPatterns();
        auto suggestQoSImprovements() -> std::vector<std::string>;

    } // namespace enhanced_packet_processing

} // namespace networking