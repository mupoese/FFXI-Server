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
#include "tracy.h"
#include "timer.h"

#include <chrono>
#include <condition_variable>
#include <memory>
#include <queue>
#include <thread>
#include <atomic>
#include <mutex>
#include <string>

#include <conncpp.hpp>
#include <memory>
#include <mutex>
#include <queue>
#include <thread>
#include <atomic>
#include <unordered_map>

// Connection pool implementation for improved database performance
namespace db
{
    namespace pool
    {
        // Forward declaration
        class Connection;

        // Connection pool statistics for monitoring
        struct PoolStats
        {
            std::atomic<uint32> totalConnections{0};
            std::atomic<uint32> activeConnections{0};
            std::atomic<uint32> idleConnections{0};
            std::atomic<uint32> waitingRequests{0};
            std::atomic<uint64> totalRequestsServed{0};
            std::atomic<uint64> totalConnectionsCreated{0};
            std::atomic<uint64> totalConnectionsDestroyed{0};
            std::atomic<double> averageWaitTimeMs{0.0};
            std::atomic<uint64> lastConnectionTime{0};
            std::atomic<uint64> lastStatsReset{0};

            // Custom copy constructor
            PoolStats(const PoolStats& other)
                : totalConnections(other.totalConnections.load())
                , activeConnections(other.activeConnections.load())
                , idleConnections(other.idleConnections.load())
                , waitingRequests(other.waitingRequests.load())
                , totalRequestsServed(other.totalRequestsServed.load())
                , totalConnectionsCreated(other.totalConnectionsCreated.load())
                , totalConnectionsDestroyed(other.totalConnectionsDestroyed.load())
                , averageWaitTimeMs(other.averageWaitTimeMs.load())
                , lastConnectionTime(other.lastConnectionTime.load())
                , lastStatsReset(other.lastStatsReset.load())
            {
            }

            // Custom assignment operator
            PoolStats& operator=(const PoolStats& other)
            {
                if (this != &other)
                {
                    totalConnections = other.totalConnections.load();
                    activeConnections = other.activeConnections.load();
                    idleConnections = other.idleConnections.load();
                    waitingRequests = other.waitingRequests.load();
                    totalRequestsServed = other.totalRequestsServed.load();
                    totalConnectionsCreated = other.totalConnectionsCreated.load();
                    totalConnectionsDestroyed = other.totalConnectionsDestroyed.load();
                    averageWaitTimeMs = other.averageWaitTimeMs.load();
                    lastConnectionTime = other.lastConnectionTime.load();
                    lastStatsReset = other.lastStatsReset.load();
                }
                return *this;
            }

            // Default constructor
            PoolStats() = default;

            void reset()
            {
                totalRequestsServed = 0;
                totalConnectionsCreated = 0;
                totalConnectionsDestroyed = 0;
                averageWaitTimeMs = 0.0;
                lastStatsReset = timer::get_utc_microseconds();
            }
        };

        // Connection wrapper with lifetime tracking
        class PooledConnection
        {
        public:
            PooledConnection(std::unique_ptr<sql::Connection> conn, uint32 poolId);
            ~PooledConnection();

            auto getConnection() -> sql::Connection*;
            auto isValid() const -> bool;
            auto getLastUsed() const -> uint64;
            auto getCreatedTime() const -> uint64;
            auto getPoolId() const -> uint32;

            void markUsed();
            void resetConnection();

        private:
            std::unique_ptr<sql::Connection> connection_;
            uint32 poolId_;
            uint64 createdTime_;
            uint64 lastUsedTime_;
            std::atomic<bool> isValid_;
        };

        // Database connection pool
        class ConnectionPool
        {
        public:
            explicit ConnectionPool(uint32 minConnections = 10, uint32 maxConnections = 50, 
                                    uint32 connectionTimeoutMs = 10000, uint32 idleTimeoutMs = 600000);
            ~ConnectionPool();

            // Get a connection from the pool
            auto getConnection() -> std::unique_ptr<PooledConnection>;

            // Return a connection to the pool
            void returnConnection(std::unique_ptr<PooledConnection> conn);

            // Pool management
            void initialize();
            void shutdown();
            void cleanupIdleConnections();

            // Statistics and monitoring
            auto getStats() const -> PoolStats;
            void resetStats();
            void logStats();

            // Configuration
            void setMinConnections(uint32 min);
            void setMaxConnections(uint32 max);
            void setConnectionTimeout(uint32 timeoutMs);
            void setIdleTimeout(uint32 idleTimeoutMs);

        private:
            // Pool configuration
            uint32 minConnections_;
            uint32 maxConnections_;
            uint32 connectionTimeoutMs_;
            uint32 idleTimeoutMs_;

            // Pool state
            std::queue<std::unique_ptr<PooledConnection>> availableConnections_;
            std::unordered_map<uint32, std::unique_ptr<PooledConnection>> activeConnections_;
            std::mutex poolMutex_;
            std::condition_variable connectionAvailable_;
            std::atomic<bool> isInitialized_{false};
            std::atomic<bool> isShuttingDown_{false};
            std::atomic<uint32> nextConnectionId_{1};

            // Statistics
            PoolStats stats_;

            // Background cleanup thread
            std::thread cleanupThread_;
            std::atomic<bool> cleanupShouldRun_{false};

            // Internal methods
            auto createNewConnection() -> std::unique_ptr<PooledConnection>;
            void cleanupWorker();
            void ensureMinConnections();
            bool isConnectionStale(const PooledConnection* conn);
        };

        // Global pool instance
        auto getGlobalPool() -> ConnectionPool&;

        // Pool initialization/shutdown
        void initializeGlobalPool();
        void shutdownGlobalPool();

    } // namespace pool
} // namespace db