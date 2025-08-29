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

#include "connection_pool.h"
#include "database.h"
#include "settings.h"
#include "timer.h"
#include "utils.h"

#include <chrono>
#include <thread>

using namespace std::chrono_literals;

namespace db
{
    namespace pool
    {
        // PooledConnection implementation
        PooledConnection::PooledConnection(std::unique_ptr<sql::Connection> conn, uint32 poolId)
        : connection_(std::move(conn))
        , poolId_(poolId)
        , createdTime_(timer::get_utc_microseconds())
        , lastUsedTime_(timer::get_utc_microseconds())
        , isValid_(true)
        {
        }

        PooledConnection::~PooledConnection() = default;

        auto PooledConnection::getConnection() -> sql::Connection*
        {
            markUsed();
            return connection_.get();
        }

        auto PooledConnection::isValid() -> bool
        {
            if (!isValid_.load())
            {
                return false;
            }

            try
            {
                // Check if connection is still alive
                if (connection_ && !connection_->isClosed())
                {
                    return true;
                }
            }
            catch (const std::exception& e)
            {
                ShowWarning("Connection validation failed: %s", e.what());
                isValid_ = false;
            }

            return false;
        }

        auto PooledConnection::getLastUsed() -> uint64
        {
            return lastUsedTime_;
        }

        auto PooledConnection::getCreatedTime() -> uint64
        {
            return createdTime_;
        }

        auto PooledConnection::getPoolId() -> uint32
        {
            return poolId_;
        }

        void PooledConnection::markUsed()
        {
            lastUsedTime_ = timer::get_utc_microseconds();
        }

        void PooledConnection::resetConnection()
        {
            try
            {
                if (connection_ && !connection_->isClosed())
                {
                    // Reset any connection state if needed
                    connection_->rollback(); // Rollback any uncommitted transactions
                }
            }
            catch (const std::exception& e)
            {
                ShowWarning("Failed to reset connection: %s", e.what());
                isValid_ = false;
            }
        }

        // ConnectionPool implementation
        ConnectionPool::ConnectionPool(uint32 minConnections, uint32 maxConnections, 
                                       uint32 connectionTimeoutMs, uint32 idleTimeoutMs)
        : minConnections_(minConnections)
        , maxConnections_(maxConnections)
        , connectionTimeoutMs_(connectionTimeoutMs)
        , idleTimeoutMs_(idleTimeoutMs)
        {
            stats_.lastStatsReset = timer::get_utc_microseconds();
        }

        ConnectionPool::~ConnectionPool()
        {
            shutdown();
        }

        void ConnectionPool::initialize()
        {
            TracyZoneScoped;

            std::lock_guard<std::mutex> lock(poolMutex_);
            
            if (isInitialized_.load())
            {
                return;
            }

            ShowInfo("Initializing database connection pool (min: %u, max: %u)", minConnections_, maxConnections_);

            // Create minimum connections
            for (uint32 i = 0; i < minConnections_; ++i)
            {
                auto conn = createNewConnection();
                if (conn)
                {
                    availableConnections_.push(std::move(conn));
                }
            }

            stats_.totalConnections = static_cast<uint32>(availableConnections_.size());
            stats_.idleConnections = stats_.totalConnections.load();

            // Start cleanup thread
            cleanupShouldRun_ = true;
            cleanupThread_ = std::thread(&ConnectionPool::cleanupWorker, this);

            isInitialized_ = true;
            
            ShowInfo("Database connection pool initialized with %u connections", stats_.totalConnections.load());
        }

        void ConnectionPool::shutdown()
        {
            TracyZoneScoped;

            if (!isInitialized_.load())
            {
                return;
            }

            ShowInfo("Shutting down database connection pool");

            isShuttingDown_ = true;

            // Stop cleanup thread
            cleanupShouldRun_ = false;
            if (cleanupThread_.joinable())
            {
                cleanupThread_.join();
            }

            std::lock_guard<std::mutex> lock(poolMutex_);

            // Clear available connections
            while (!availableConnections_.empty())
            {
                availableConnections_.pop();
                stats_.totalConnectionsDestroyed++;
            }

            // Clear active connections (they should be returned by now)
            activeConnections_.clear();

            stats_.totalConnections = 0;
            stats_.activeConnections = 0;
            stats_.idleConnections = 0;

            isInitialized_ = false;

            ShowInfo("Database connection pool shutdown complete");
        }

        auto ConnectionPool::getConnection() -> std::unique_ptr<PooledConnection>
        {
            TracyZoneScoped;

            if (isShuttingDown_.load())
            {
                return nullptr;
            }

            const auto startTime = timer::get_utc_microseconds();
            std::unique_lock<std::mutex> lock(poolMutex_);

            stats_.waitingRequests++;

            // Wait for available connection or timeout
            auto timeout = std::chrono::milliseconds(connectionTimeoutMs_);
            bool gotConnection = connectionAvailable_.wait_for(lock, timeout, [this]()
            {
                return !availableConnections_.empty() || isShuttingDown_.load();
            });

            stats_.waitingRequests--;

            if (isShuttingDown_.load())
            {
                return nullptr;
            }

            std::unique_ptr<PooledConnection> conn;

            if (gotConnection && !availableConnections_.empty())
            {
                // Get connection from pool
                conn = std::move(availableConnections_.front());
                availableConnections_.pop();
                
                // Validate connection
                if (!conn->isValid())
                {
                    ShowWarning("Retrieved invalid connection from pool, creating new one");
                    conn = createNewConnection();
                }
            }
            else if (stats_.totalConnections.load() < maxConnections_)
            {
                // Create new connection if under max limit
                conn = createNewConnection();
            }

            if (conn)
            {
                auto connId = conn->getPoolId();
                activeConnections_[connId] = std::move(conn);
                
                stats_.activeConnections++;
                stats_.idleConnections--;
                stats_.totalRequestsServed++;
                
                const auto waitTime = (timer::get_utc_microseconds() - startTime) / 1000.0; // Convert to ms
                const auto currentAvg = stats_.averageWaitTimeMs.load();
                const auto newAvg = (currentAvg * 0.9) + (waitTime * 0.1); // Exponential moving average
                stats_.averageWaitTimeMs = newAvg;

                return std::unique_ptr<PooledConnection>(activeConnections_[connId].release());
            }

            ShowError("Failed to get database connection from pool (timeout: %ums)", connectionTimeoutMs_);
            return nullptr;
        }

        void ConnectionPool::returnConnection(std::unique_ptr<PooledConnection> conn)
        {
            TracyZoneScoped;

            if (!conn || isShuttingDown_.load())
            {
                return;
            }

            std::lock_guard<std::mutex> lock(poolMutex_);

            auto connId = conn->getPoolId();
            
            // Remove from active connections
            activeConnections_.erase(connId);
            
            // Reset connection state
            conn->resetConnection();

            if (conn->isValid())
            {
                // Return to available pool
                availableConnections_.push(std::move(conn));
                stats_.idleConnections++;
            }
            else
            {
                // Connection is invalid, destroy it
                stats_.totalConnectionsDestroyed++;
                stats_.totalConnections--;
            }

            stats_.activeConnections--;
            connectionAvailable_.notify_one();
        }

        auto ConnectionPool::getStats() -> PoolStats
        {
            return stats_;
        }

        void ConnectionPool::resetStats()
        {
            stats_.reset();
        }

        void ConnectionPool::logStats()
        {
            const auto stats = getStats();
            ShowInfo("DB Pool Stats - Total: %u, Active: %u, Idle: %u, Served: %llu, Avg Wait: %.2fms",
                     stats.totalConnections.load(),
                     stats.activeConnections.load(), 
                     stats.idleConnections.load(),
                     stats.totalRequestsServed.load(),
                     stats.averageWaitTimeMs.load());
        }

        void ConnectionPool::cleanupIdleConnections()
        {
            TracyZoneScoped;

            std::lock_guard<std::mutex> lock(poolMutex_);
            
            const auto currentTime = timer::get_utc_microseconds();
            const auto timeoutMicros = idleTimeoutMs_ * 1000ULL;

            // Check idle connections for cleanup
            std::queue<std::unique_ptr<PooledConnection>> newQueue;
            while (!availableConnections_.empty())
            {
                auto conn = std::move(availableConnections_.front());
                availableConnections_.pop();

                if (isConnectionStale(conn.get()) || 
                    (currentTime - conn->getLastUsed()) > timeoutMicros)
                {
                    // Connection is stale or idle too long
                    stats_.totalConnectionsDestroyed++;
                    stats_.totalConnections--;
                    stats_.idleConnections--;
                }
                else
                {
                    newQueue.push(std::move(conn));
                }
            }

            availableConnections_ = std::move(newQueue);
            
            // Ensure minimum connections
            ensureMinConnections();
        }

        auto ConnectionPool::createNewConnection() -> std::unique_ptr<PooledConnection>
        {
            TracyZoneScoped;

            try
            {
                auto conn = db::getConnection();
                if (conn)
                {
                    auto pooledConn = std::make_unique<PooledConnection>(std::move(conn), nextConnectionId_++);
                    stats_.totalConnectionsCreated++;
                    stats_.totalConnections++;
                    stats_.lastConnectionTime = timer::get_utc_microseconds();
                    return pooledConn;
                }
            }
            catch (const std::exception& e)
            {
                ShowError("Failed to create new database connection: %s", e.what());
            }

            return nullptr;
        }

        void ConnectionPool::cleanupWorker()
        {
            while (cleanupShouldRun_.load())
            {
                std::this_thread::sleep_for(30s); // Cleanup every 30 seconds
                
                if (!cleanupShouldRun_.load())
                {
                    break;
                }

                cleanupIdleConnections();
            }
        }

        void ConnectionPool::ensureMinConnections()
        {
            while (availableConnections_.size() < minConnections_)
            {
                auto conn = createNewConnection();
                if (conn)
                {
                    availableConnections_.push(std::move(conn));
                    stats_.idleConnections++;
                }
                else
                {
                    break; // Failed to create connection, stop trying
                }
            }
        }

        bool ConnectionPool::isConnectionStale(const PooledConnection* conn)
        {
            const auto currentTime = timer::get_utc_microseconds();
            const auto connectionAge = currentTime - conn->getCreatedTime();
            const auto maxAgeMicros = 3600000000ULL; // 1 hour in microseconds

            return connectionAge > maxAgeMicros || !conn->isValid();
        }

        void ConnectionPool::setMinConnections(uint32 min)
        {
            std::lock_guard<std::mutex> lock(poolMutex_);
            minConnections_ = min;
            ensureMinConnections();
        }

        void ConnectionPool::setMaxConnections(uint32 max)
        {
            std::lock_guard<std::mutex> lock(poolMutex_);
            maxConnections_ = max;
        }

        void ConnectionPool::setConnectionTimeout(uint32 timeoutMs)
        {
            connectionTimeoutMs_ = timeoutMs;
        }

        void ConnectionPool::setIdleTimeout(uint32 idleTimeoutMs)
        {
            idleTimeoutMs_ = idleTimeoutMs;
        }

        // Global pool instance
        static std::unique_ptr<ConnectionPool> globalPool;
        static std::mutex globalPoolMutex;

        auto getGlobalPool() -> ConnectionPool&
        {
            std::lock_guard<std::mutex> lock(globalPoolMutex);
            if (!globalPool)
            {
                const auto minConn = settings::get<uint32>("network.SQL_POOL_MIN_CONNECTIONS");
                const auto maxConn = settings::get<uint32>("network.SQL_POOL_MAX_CONNECTIONS");
                const auto connTimeout = settings::get<uint32>("network.SQL_POOL_CONNECTION_TIMEOUT_MS");
                const auto idleTimeout = settings::get<uint32>("network.SQL_POOL_IDLE_TIMEOUT_MS");
                
                globalPool = std::make_unique<ConnectionPool>(minConn, maxConn, connTimeout, idleTimeout);
                globalPool->initialize();
            }
            return *globalPool;
        }

        void initializeGlobalPool()
        {
            getGlobalPool(); // This will create and initialize the pool
        }

        void shutdownGlobalPool()
        {
            std::lock_guard<std::mutex> lock(globalPoolMutex);
            if (globalPool)
            {
                globalPool->shutdown();
                globalPool.reset();
            }
        }

    } // namespace pool
} // namespace db