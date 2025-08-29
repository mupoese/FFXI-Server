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
#include "common/database.h"
#include "common/tracy.h"

#include <chrono>
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace database
{
    // Enhanced error handling for database operations
    namespace error_handling
    {
        // Error severity levels
        enum class ErrorSeverity : uint8
        {
            INFO = 0,      // Informational, no action needed
            WARNING = 1,   // Warning, may need attention
            ERROR = 2,     // Error, requires intervention
            CRITICAL = 3   // Critical, system stability at risk
        };

        // Error categories for better handling
        enum class ErrorCategory : uint8
        {
            CONNECTION = 0,    // Connection-related errors
            TIMEOUT = 1,       // Query timeout errors
            SYNTAX = 2,        // SQL syntax errors
            CONSTRAINT = 3,    // Constraint violation errors
            DEADLOCK = 4,      // Deadlock errors
            RESOURCE = 5,      // Resource exhaustion
            UNKNOWN = 6        // Unknown/unclassified errors
        };

        // Retry strategy configuration
        struct RetryConfig
        {
            uint32 maxRetries = 3;
            uint32 baseDelayMs = 100;
            uint32 maxDelayMs = 5000;
            float  backoffMultiplier = 2.0f;
            bool   enableJitter = true;
        };

        // Database error information
        struct DatabaseError
        {
            ErrorSeverity severity;
            ErrorCategory category;
            std::string   message;
            std::string   sqlState;
            uint32        errorCode;
            std::string   queryText;
            std::chrono::steady_clock::time_point timestamp;
            
            DatabaseError(ErrorSeverity sev, ErrorCategory cat, const std::string& msg,
                         const std::string& state = "", uint32 code = 0, const std::string& query = "")
                : severity(sev), category(cat), message(msg), sqlState(state), 
                  errorCode(code), queryText(query), timestamp(std::chrono::steady_clock::now()) {}
        };

        // Enhanced database operation result
        template<typename T>
        class DatabaseResult
        {
        public:
            DatabaseResult() : success_(false) {}
            explicit DatabaseResult(T&& value) : success_(true), value_(std::move(value)) {}
            explicit DatabaseResult(const DatabaseError& error) : success_(false), error_(error) {}

            auto isSuccess() const -> bool { return success_; }
            auto hasError() const -> bool { return !success_; }
            
            auto getValue() -> T& { return value_; }
            auto getValue() const -> const T& { return value_; }
            auto getError() const -> const DatabaseError& { return error_; }

            // Convenient access operators
            explicit operator bool() const { return success_; }
            auto operator*() -> T& { return value_; }
            auto operator*() const -> const T& { return value_; }
            auto operator->() -> T* { return &value_; }
            auto operator->() const -> const T* { return &value_; }

        private:
            bool          success_;
            T             value_;
            DatabaseError error_;
        };

        // Enhanced database query executor with retry logic
        class EnhancedDatabaseExecutor
        {
        public:
            EnhancedDatabaseExecutor();
            ~EnhancedDatabaseExecutor();

            // Configuration
            void setRetryConfig(const RetryConfig& config);
            void enableCircuitBreaker(bool enable, uint32 failureThreshold = 5, uint32 timeoutMs = 30000);
            void enablePerformanceMonitoring(bool enable);

            // Enhanced query execution with retry logic
            auto executeQuery(const std::string& query) -> DatabaseResult<std::unique_ptr<db::detail::ResultSetWrapper>>;
            auto executeUpdate(const std::string& query) -> DatabaseResult<uint32>;
            auto executeTransaction(const std::vector<std::string>& queries) -> DatabaseResult<bool>;

            // Async query execution for non-blocking operations
            auto executeQueryAsync(const std::string& query, std::function<void(DatabaseResult<std::unique_ptr<db::detail::ResultSetWrapper>>)> callback) -> void;

            // Prepared statement support with enhanced error handling
            auto executePreparedQuery(const std::string& query, const std::vector<std::string>& parameters) -> DatabaseResult<std::unique_ptr<db::detail::ResultSetWrapper>>;

            // Batch operations with optimized error handling
            auto executeBatch(const std::vector<std::string>& queries, bool stopOnError = true) -> std::vector<DatabaseResult<uint32>>;

            // Health monitoring and statistics
            auto getConnectionHealth() const -> bool;
            auto getErrorRate() const -> double;
            auto getAverageQueryTime() const -> double;
            auto getCircuitBreakerStatus() const -> bool;

            // Error analysis and reporting
            auto getRecentErrors(size_t count = 10) const -> std::vector<DatabaseError>;
            auto getErrorStatistics() const -> std::map<ErrorCategory, uint32>;
            void clearErrorHistory();

        private:
            struct ConnectionState
            {
                bool    isHealthy = true;
                uint32  consecutiveFailures = 0;
                std::chrono::steady_clock::time_point lastFailureTime;
                std::chrono::steady_clock::time_point lastSuccessTime;
            };

            struct CircuitBreakerState
            {
                bool    enabled = false;
                bool    isOpen = false;
                uint32  failureThreshold = 5;
                uint32  timeoutMs = 30000;
                uint32  failureCount = 0;
                std::chrono::steady_clock::time_point lastFailureTime;
            };

            struct PerformanceMetrics
            {
                uint64 totalQueries = 0;
                uint64 successfulQueries = 0;
                uint64 failedQueries = 0;
                double totalQueryTime = 0.0;
                double averageQueryTime = 0.0;
                std::chrono::steady_clock::time_point startTime;
            };

            RetryConfig         retryConfig_;
            ConnectionState     connectionState_;
            CircuitBreakerState circuitBreaker_;
            PerformanceMetrics  metrics_;
            bool                performanceMonitoringEnabled_;

            mutable std::mutex                errorHistoryMutex_;
            std::vector<DatabaseError>        errorHistory_;
            static constexpr size_t           MAX_ERROR_HISTORY = 1000;

            // Internal helper methods
            auto classifyError(const std::exception& e) const -> DatabaseError;
            auto shouldRetry(const DatabaseError& error, uint32 attemptCount) const -> bool;
            auto calculateDelay(uint32 attemptCount) const -> uint32;
            auto isConnectionError(const DatabaseError& error) const -> bool;
            auto updateCircuitBreaker(bool success) -> void;
            auto recordError(const DatabaseError& error) -> void;
            auto updatePerformanceMetrics(bool success, double queryTime) -> void;

            template<typename T>
            auto executeWithRetry(const std::function<T()>& operation, const std::string& queryText) -> DatabaseResult<T>;
        };

        // Connection pool health monitor
        class ConnectionPoolMonitor
        {
        public:
            ConnectionPoolMonitor();
            ~ConnectionPoolMonitor();

            void startMonitoring(uint32 intervalMs = 30000);
            void stopMonitoring();

            // Health checks
            auto checkConnectionHealth() -> bool;
            auto getActiveConnections() const -> uint32;
            auto getIdleConnections() const -> uint32;
            auto getConnectionUtilization() const -> double;

            // Pool management
            void warmupConnections(uint32 count);
            void cleanupIdleConnections(uint32 maxIdleTimeMs = 300000);
            void resetConnectionPool();

            // Monitoring callbacks
            void setHealthCallback(std::function<void(bool healthy, const std::string& details)> callback);
            void setUtilizationCallback(std::function<void(double utilization)> callback);

        private:
            struct MonitoringState
            {
                bool    isRunning = false;
                uint32  intervalMs = 30000;
                std::thread monitoringThread;
            };

            MonitoringState monitoringState_;
            std::function<void(bool, const std::string&)> healthCallback_;
            std::function<void(double)> utilizationCallback_;

            void monitoringLoop();
            auto performHealthCheck() -> std::pair<bool, std::string>;
        };

        // Global enhanced database system
        auto getEnhancedExecutor() -> EnhancedDatabaseExecutor&;
        auto getConnectionMonitor() -> ConnectionPoolMonitor&;
        
        void initializeEnhancedDatabase();
        void shutdownEnhancedDatabase();

        // Utility functions for error handling
        auto formatError(const DatabaseError& error) -> std::string;
        auto isRetryableError(const DatabaseError& error) -> bool;
        auto getErrorCategoryName(ErrorCategory category) -> std::string;
        auto getSeverityName(ErrorSeverity severity) -> std::string;

        // Performance optimization helpers
        auto optimizeQuery(const std::string& query) -> std::string;
        auto analyzeQueryPerformance(const std::string& query, double executionTime) -> void;
        auto suggestQueryImprovements(const std::string& query) -> std::vector<std::string>;

    } // namespace error_handling

} // namespace database