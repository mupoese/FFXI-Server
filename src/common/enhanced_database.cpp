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

#include "enhanced_database.h"

#include "common/logging.h"
#include "common/settings.h"
#include "common/timer.h"
#include "common/tracy.h"

#include <algorithm>
#include <random>
#include <regex>
#include <thread>

namespace database
{
    namespace error_handling
    {
        namespace
        {
            std::unique_ptr<EnhancedDatabaseExecutor> g_enhancedExecutor;
            std::unique_ptr<ConnectionPoolMonitor>    g_connectionMonitor;
        }

        // EnhancedDatabaseExecutor implementation
        EnhancedDatabaseExecutor::EnhancedDatabaseExecutor()
        : performanceMonitoringEnabled_(true)
        {
            TracyZoneScoped;
            
            // Initialize default retry configuration
            retryConfig_.maxRetries = settings::get<uint32>("database.MAX_RETRIES", 3);
            retryConfig_.baseDelayMs = settings::get<uint32>("database.BASE_DELAY_MS", 100);
            retryConfig_.maxDelayMs = settings::get<uint32>("database.MAX_DELAY_MS", 5000);
            retryConfig_.backoffMultiplier = settings::get<float>("database.BACKOFF_MULTIPLIER", 2.0f);
            retryConfig_.enableJitter = settings::get<bool>("database.ENABLE_JITTER", true);

            // Initialize metrics
            metrics_.startTime = std::chrono::steady_clock::now();
            connectionState_.lastSuccessTime = std::chrono::steady_clock::now();

            errorHistory_.reserve(MAX_ERROR_HISTORY);

            ShowInfo("EnhancedDatabaseExecutor: Initialized with retry config (max: %u, base delay: %ums)", 
                     retryConfig_.maxRetries, retryConfig_.baseDelayMs);
        }

        EnhancedDatabaseExecutor::~EnhancedDatabaseExecutor()
        {
            TracyZoneScoped;
        }

        void EnhancedDatabaseExecutor::setRetryConfig(const RetryConfig& config)
        {
            TracyZoneScoped;
            retryConfig_ = config;
            ShowInfo("EnhancedDatabaseExecutor: Updated retry config (max: %u, base delay: %ums)", 
                     config.maxRetries, config.baseDelayMs);
        }

        void EnhancedDatabaseExecutor::enableCircuitBreaker(bool enable, uint32 failureThreshold, uint32 timeoutMs)
        {
            TracyZoneScoped;
            circuitBreaker_.enabled = enable;
            circuitBreaker_.failureThreshold = failureThreshold;
            circuitBreaker_.timeoutMs = timeoutMs;
            
            if (enable)
            {
                ShowInfo("EnhancedDatabaseExecutor: Circuit breaker enabled (threshold: %u, timeout: %ums)", 
                         failureThreshold, timeoutMs);
            }
            else
            {
                ShowInfo("EnhancedDatabaseExecutor: Circuit breaker disabled");
            }
        }

        void EnhancedDatabaseExecutor::enablePerformanceMonitoring(bool enable)
        {
            performanceMonitoringEnabled_ = enable;
            if (enable)
            {
                ShowInfo("EnhancedDatabaseExecutor: Performance monitoring enabled");
            }
            else
            {
                ShowInfo("EnhancedDatabaseExecutor: Performance monitoring disabled");
            }
        }

        auto EnhancedDatabaseExecutor::executeQuery(const std::string& query) -> DatabaseResult<std::unique_ptr<db::detail::ResultSetWrapper>>
        {
            TracyZoneScoped;
            
            return executeWithRetry<std::unique_ptr<db::detail::ResultSetWrapper>>(
                [&query]() {
                    return db::queryStr(query);
                }, query);
        }

        auto EnhancedDatabaseExecutor::executeUpdate(const std::string& query) -> DatabaseResult<uint32>
        {
            TracyZoneScoped;
            
            return executeWithRetry<uint32>(
                [&query]() -> uint32 {
                    auto result = db::queryStr(query);
                    if (result)
                    {
                        return result->rowsAffected();
                    }
                    throw std::runtime_error("Update query failed");
                }, query);
        }

        auto EnhancedDatabaseExecutor::executeTransaction(const std::vector<std::string>& queries) -> DatabaseResult<bool>
        {
            TracyZoneScoped;
            
            return executeWithRetry<bool>(
                [&queries]() -> bool {
                    // Begin transaction
                    auto beginResult = db::queryStr("BEGIN");
                    if (!beginResult)
                    {
                        throw std::runtime_error("Failed to begin transaction");
                    }

                    try
                    {
                        // Execute all queries
                        for (const auto& query : queries)
                        {
                            auto result = db::queryStr(query);
                            if (!result)
                            {
                                // Rollback on failure
                                db::queryStr("ROLLBACK");
                                throw std::runtime_error("Transaction query failed: " + query);
                            }
                        }

                        // Commit transaction
                        auto commitResult = db::queryStr("COMMIT");
                        if (!commitResult)
                        {
                            db::queryStr("ROLLBACK");
                            throw std::runtime_error("Failed to commit transaction");
                        }

                        return true;
                    }
                    catch (...)
                    {
                        // Ensure rollback on any exception
                        db::queryStr("ROLLBACK");
                        throw;
                    }
                }, "TRANSACTION");
        }

        auto EnhancedDatabaseExecutor::executePreparedQuery(const std::string& query, const std::vector<std::string>& parameters) -> DatabaseResult<std::unique_ptr<db::detail::ResultSetWrapper>>
        {
            TracyZoneScoped;
            
            return executeWithRetry<std::unique_ptr<db::detail::ResultSetWrapper>>(
                [&query, &parameters]() {
                    // Simple parameter substitution for now
                    // In a full implementation, this would use proper prepared statements
                    std::string finalQuery = query;
                    for (size_t i = 0; i < parameters.size(); ++i)
                    {
                        const std::string placeholder = "?";
                        size_t pos = finalQuery.find(placeholder);
                        if (pos != std::string::npos)
                        {
                            finalQuery.replace(pos, placeholder.length(), db::escapeString(parameters[i]));
                        }
                    }
                    return db::queryStr(finalQuery);
                }, query);
        }

        auto EnhancedDatabaseExecutor::executeBatch(const std::vector<std::string>& queries, bool stopOnError) -> std::vector<DatabaseResult<uint32>>
        {
            TracyZoneScoped;
            
            std::vector<DatabaseResult<uint32>> results;
            results.reserve(queries.size());

            for (const auto& query : queries)
            {
                auto result = executeUpdate(query);
                results.push_back(std::move(result));

                if (stopOnError && !results.back().isSuccess())
                {
                    ShowWarning("EnhancedDatabaseExecutor: Batch execution stopped due to error in query: %s", query.c_str());
                    break;
                }
            }

            return results;
        }

        auto EnhancedDatabaseExecutor::getConnectionHealth() const -> bool
        {
            return connectionState_.isHealthy;
        }

        auto EnhancedDatabaseExecutor::getErrorRate() const -> double
        {
            if (metrics_.totalQueries == 0)
            {
                return 0.0;
            }
            return static_cast<double>(metrics_.failedQueries) / static_cast<double>(metrics_.totalQueries);
        }

        auto EnhancedDatabaseExecutor::getAverageQueryTime() const -> double
        {
            return metrics_.averageQueryTime;
        }

        auto EnhancedDatabaseExecutor::getCircuitBreakerStatus() const -> bool
        {
            return circuitBreaker_.isOpen;
        }

        auto EnhancedDatabaseExecutor::getRecentErrors(size_t count) const -> std::vector<DatabaseError>
        {
            std::lock_guard<std::mutex> lock(errorHistoryMutex_);
            
            const size_t startIndex = errorHistory_.size() > count ? errorHistory_.size() - count : 0;
            return std::vector<DatabaseError>(errorHistory_.begin() + startIndex, errorHistory_.end());
        }

        auto EnhancedDatabaseExecutor::getErrorStatistics() const -> std::map<ErrorCategory, uint32>
        {
            std::lock_guard<std::mutex> lock(errorHistoryMutex_);
            
            std::map<ErrorCategory, uint32> stats;
            for (const auto& error : errorHistory_)
            {
                stats[error.category]++;
            }
            return stats;
        }

        void EnhancedDatabaseExecutor::clearErrorHistory()
        {
            std::lock_guard<std::mutex> lock(errorHistoryMutex_);
            errorHistory_.clear();
        }

        auto EnhancedDatabaseExecutor::classifyError(const std::exception& e) const -> DatabaseError
        {
            const std::string message = e.what();
            
            // Classify based on error message patterns
            if (message.find("Connection") != std::string::npos || 
                message.find("connection") != std::string::npos ||
                message.find("Lost connection") != std::string::npos)
            {
                return DatabaseError(ErrorSeverity::ERROR, ErrorCategory::CONNECTION, message);
            }
            
            if (message.find("timeout") != std::string::npos || 
                message.find("Timeout") != std::string::npos)
            {
                return DatabaseError(ErrorSeverity::WARNING, ErrorCategory::TIMEOUT, message);
            }
            
            if (message.find("syntax") != std::string::npos || 
                message.find("Syntax") != std::string::npos)
            {
                return DatabaseError(ErrorSeverity::ERROR, ErrorCategory::SYNTAX, message);
            }
            
            if (message.find("constraint") != std::string::npos || 
                message.find("Constraint") != std::string::npos ||
                message.find("CONSTRAINT") != std::string::npos)
            {
                return DatabaseError(ErrorSeverity::WARNING, ErrorCategory::CONSTRAINT, message);
            }
            
            if (message.find("deadlock") != std::string::npos || 
                message.find("Deadlock") != std::string::npos)
            {
                return DatabaseError(ErrorSeverity::WARNING, ErrorCategory::DEADLOCK, message);
            }
            
            return DatabaseError(ErrorSeverity::ERROR, ErrorCategory::UNKNOWN, message);
        }

        auto EnhancedDatabaseExecutor::shouldRetry(const DatabaseError& error, uint32 attemptCount) const -> bool
        {
            if (attemptCount >= retryConfig_.maxRetries)
            {
                return false;
            }

            // Don't retry syntax errors
            if (error.category == ErrorCategory::SYNTAX)
            {
                return false;
            }

            // Always retry connection and timeout errors
            if (error.category == ErrorCategory::CONNECTION || 
                error.category == ErrorCategory::TIMEOUT ||
                error.category == ErrorCategory::DEADLOCK)
            {
                return true;
            }

            // Retry other errors based on severity
            return error.severity != ErrorSeverity::CRITICAL;
        }

        auto EnhancedDatabaseExecutor::calculateDelay(uint32 attemptCount) const -> uint32
        {
            uint32 delay = retryConfig_.baseDelayMs * static_cast<uint32>(std::pow(retryConfig_.backoffMultiplier, attemptCount));
            delay = std::min(delay, retryConfig_.maxDelayMs);

            if (retryConfig_.enableJitter)
            {
                static std::random_device rd;
                static std::mt19937 gen(rd());
                std::uniform_real_distribution<> dis(0.5, 1.5);
                delay = static_cast<uint32>(delay * dis(gen));
            }

            return delay;
        }

        auto EnhancedDatabaseExecutor::isConnectionError(const DatabaseError& error) const -> bool
        {
            return error.category == ErrorCategory::CONNECTION;
        }

        auto EnhancedDatabaseExecutor::updateCircuitBreaker(bool success) -> void
        {
            if (!circuitBreaker_.enabled)
            {
                return;
            }

            if (success)
            {
                circuitBreaker_.failureCount = 0;
                if (circuitBreaker_.isOpen)
                {
                    circuitBreaker_.isOpen = false;
                    ShowInfo("EnhancedDatabaseExecutor: Circuit breaker closed (connection restored)");
                }
            }
            else
            {
                circuitBreaker_.failureCount++;
                circuitBreaker_.lastFailureTime = std::chrono::steady_clock::now();
                
                if (!circuitBreaker_.isOpen && circuitBreaker_.failureCount >= circuitBreaker_.failureThreshold)
                {
                    circuitBreaker_.isOpen = true;
                    ShowWarning("EnhancedDatabaseExecutor: Circuit breaker opened (too many failures: %u)", 
                               circuitBreaker_.failureCount);
                }
            }
        }

        auto EnhancedDatabaseExecutor::recordError(const DatabaseError& error) -> void
        {
            std::lock_guard<std::mutex> lock(errorHistoryMutex_);
            
            errorHistory_.push_back(error);
            
            // Limit error history size
            if (errorHistory_.size() > MAX_ERROR_HISTORY)
            {
                errorHistory_.erase(errorHistory_.begin(), errorHistory_.begin() + (errorHistory_.size() - MAX_ERROR_HISTORY));
            }
        }

        auto EnhancedDatabaseExecutor::updatePerformanceMetrics(bool success, double queryTime) -> void
        {
            if (!performanceMonitoringEnabled_)
            {
                return;
            }

            metrics_.totalQueries++;
            if (success)
            {
                metrics_.successfulQueries++;
                connectionState_.lastSuccessTime = std::chrono::steady_clock::now();
            }
            else
            {
                metrics_.failedQueries++;
                connectionState_.consecutiveFailures++;
                connectionState_.lastFailureTime = std::chrono::steady_clock::now();
            }

            metrics_.totalQueryTime += queryTime;
            metrics_.averageQueryTime = metrics_.totalQueryTime / static_cast<double>(metrics_.totalQueries);

            // Update connection health based on recent performance
            const auto now = std::chrono::steady_clock::now();
            const auto timeSinceLastSuccess = std::chrono::duration_cast<std::chrono::milliseconds>(now - connectionState_.lastSuccessTime).count();
            
            connectionState_.isHealthy = (connectionState_.consecutiveFailures < 3) && (timeSinceLastSuccess < 60000);
        }

        template<typename T>
        auto EnhancedDatabaseExecutor::executeWithRetry(const std::function<T()>& operation, const std::string& queryText) -> DatabaseResult<T>
        {
            TracyZoneScoped;
            
            // Check circuit breaker
            if (circuitBreaker_.enabled && circuitBreaker_.isOpen)
            {
                const auto now = std::chrono::steady_clock::now();
                const auto timeSinceFailure = std::chrono::duration_cast<std::chrono::milliseconds>(now - circuitBreaker_.lastFailureTime).count();
                
                if (timeSinceFailure < circuitBreaker_.timeoutMs)
                {
                    return DatabaseResult<T>(DatabaseError(ErrorSeverity::ERROR, ErrorCategory::CONNECTION, 
                                                          "Circuit breaker is open"));
                }
                else
                {
                    // Try to close circuit breaker
                    circuitBreaker_.isOpen = false;
                    ShowInfo("EnhancedDatabaseExecutor: Attempting to close circuit breaker (timeout expired)");
                }
            }

            uint32 attemptCount = 0;
            DatabaseError lastError(ErrorSeverity::ERROR, ErrorCategory::UNKNOWN, "No error");

            while (attemptCount <= retryConfig_.maxRetries)
            {
                const auto startTime = std::chrono::high_resolution_clock::now();
                
                try
                {
                    auto result = operation();
                    
                    const auto endTime = std::chrono::high_resolution_clock::now();
                    const auto queryTime = std::chrono::duration<double, std::milli>(endTime - startTime).count();
                    
                    updatePerformanceMetrics(true, queryTime);
                    updateCircuitBreaker(true);
                    
                    if (attemptCount > 0)
                    {
                        ShowInfo("EnhancedDatabaseExecutor: Query succeeded after %u retries", attemptCount);
                    }
                    
                    return DatabaseResult<T>(std::move(result));
                }
                catch (const std::exception& e)
                {
                    const auto endTime = std::chrono::high_resolution_clock::now();
                    const auto queryTime = std::chrono::duration<double, std::milli>(endTime - startTime).count();
                    
                    lastError = classifyError(e);
                    lastError.queryText = queryText;
                    
                    updatePerformanceMetrics(false, queryTime);
                    updateCircuitBreaker(false);
                    recordError(lastError);
                    
                    if (!shouldRetry(lastError, attemptCount))
                    {
                        ShowError("EnhancedDatabaseExecutor: Query failed (no retry): %s", e.what());
                        break;
                    }
                    
                    if (attemptCount < retryConfig_.maxRetries)
                    {
                        const uint32 delay = calculateDelay(attemptCount);
                        ShowWarning("EnhancedDatabaseExecutor: Query failed (attempt %u/%u), retrying in %ums: %s", 
                                   attemptCount + 1, retryConfig_.maxRetries + 1, delay, e.what());
                        
                        std::this_thread::sleep_for(std::chrono::milliseconds(delay));
                    }
                }
                
                attemptCount++;
            }
            
            ShowError("EnhancedDatabaseExecutor: Query failed after %u attempts: %s", 
                     retryConfig_.maxRetries + 1, lastError.message.c_str());
            
            return DatabaseResult<T>(lastError);
        }

        // ConnectionPoolMonitor implementation
        ConnectionPoolMonitor::ConnectionPoolMonitor()
        {
            TracyZoneScoped;
        }

        ConnectionPoolMonitor::~ConnectionPoolMonitor()
        {
            TracyZoneScoped;
            stopMonitoring();
        }

        void ConnectionPoolMonitor::startMonitoring(uint32 intervalMs)
        {
            TracyZoneScoped;
            
            if (monitoringState_.isRunning)
            {
                stopMonitoring();
            }

            monitoringState_.intervalMs = intervalMs;
            monitoringState_.isRunning = true;
            monitoringState_.monitoringThread = std::thread(&ConnectionPoolMonitor::monitoringLoop, this);

            ShowInfo("ConnectionPoolMonitor: Monitoring started (interval: %ums)", intervalMs);
        }

        void ConnectionPoolMonitor::stopMonitoring()
        {
            TracyZoneScoped;
            
            if (monitoringState_.isRunning)
            {
                monitoringState_.isRunning = false;
                if (monitoringState_.monitoringThread.joinable())
                {
                    monitoringState_.monitoringThread.join();
                }
                ShowInfo("ConnectionPoolMonitor: Monitoring stopped");
            }
        }

        auto ConnectionPoolMonitor::checkConnectionHealth() -> bool
        {
            TracyZoneScoped;
            
            try
            {
                // Simple health check query
                auto result = db::queryStr("SELECT 1");
                return result != nullptr;
            }
            catch (const std::exception& e)
            {
                ShowWarning("ConnectionPoolMonitor: Health check failed: %s", e.what());
                return false;
            }
        }

        void ConnectionPoolMonitor::setHealthCallback(std::function<void(bool healthy, const std::string& details)> callback)
        {
            healthCallback_ = std::move(callback);
        }

        void ConnectionPoolMonitor::setUtilizationCallback(std::function<void(double utilization)> callback)
        {
            utilizationCallback_ = std::move(callback);
        }

        void ConnectionPoolMonitor::monitoringLoop()
        {
            TracyZoneScoped;
            
            while (monitoringState_.isRunning)
            {
                auto [healthy, details] = performHealthCheck();
                
                if (healthCallback_)
                {
                    healthCallback_(healthy, details);
                }

                // Calculate utilization (placeholder implementation)
                double utilization = getConnectionUtilization();
                if (utilizationCallback_)
                {
                    utilizationCallback_(utilization);
                }

                std::this_thread::sleep_for(std::chrono::milliseconds(monitoringState_.intervalMs));
            }
        }

        auto ConnectionPoolMonitor::performHealthCheck() -> std::pair<bool, std::string>
        {
            TracyZoneScoped;
            
            bool healthy = checkConnectionHealth();
            std::string details = healthy ? "Connection pool healthy" : "Connection pool unhealthy";
            
            return {healthy, details};
        }

        auto ConnectionPoolMonitor::getActiveConnections() const -> uint32
        {
            // Placeholder implementation - would need access to actual connection pool
            return 5;
        }

        auto ConnectionPoolMonitor::getIdleConnections() const -> uint32
        {
            // Placeholder implementation
            return 10;
        }

        auto ConnectionPoolMonitor::getConnectionUtilization() const -> double
        {
            // Placeholder implementation
            auto active = getActiveConnections();
            auto total = active + getIdleConnections();
            return total > 0 ? static_cast<double>(active) / static_cast<double>(total) : 0.0;
        }

        // Global system functions
        auto getEnhancedExecutor() -> EnhancedDatabaseExecutor&
        {
            if (!g_enhancedExecutor)
            {
                g_enhancedExecutor = std::make_unique<EnhancedDatabaseExecutor>();
            }
            return *g_enhancedExecutor;
        }

        auto getConnectionMonitor() -> ConnectionPoolMonitor&
        {
            if (!g_connectionMonitor)
            {
                g_connectionMonitor = std::make_unique<ConnectionPoolMonitor>();
            }
            return *g_connectionMonitor;
        }

        void initializeEnhancedDatabase()
        {
            getEnhancedExecutor();
            getConnectionMonitor().startMonitoring();
            ShowInfo("Enhanced database system initialized");
        }

        void shutdownEnhancedDatabase()
        {
            if (g_connectionMonitor)
            {
                g_connectionMonitor->stopMonitoring();
                g_connectionMonitor.reset();
            }
            
            if (g_enhancedExecutor)
            {
                g_enhancedExecutor.reset();
            }
            
            ShowInfo("Enhanced database system shutdown");
        }

        // Utility functions
        auto formatError(const DatabaseError& error) -> std::string
        {
            return fmt::format("[{}] {}: {} (Category: {})", 
                              getSeverityName(error.severity),
                              getErrorCategoryName(error.category),
                              error.message,
                              error.queryText.empty() ? "N/A" : error.queryText);
        }

        auto isRetryableError(const DatabaseError& error) -> bool
        {
            return error.category != ErrorCategory::SYNTAX && error.severity != ErrorSeverity::CRITICAL;
        }

        auto getErrorCategoryName(ErrorCategory category) -> std::string
        {
            switch (category)
            {
                case ErrorCategory::CONNECTION: return "CONNECTION";
                case ErrorCategory::TIMEOUT:    return "TIMEOUT";
                case ErrorCategory::SYNTAX:     return "SYNTAX";
                case ErrorCategory::CONSTRAINT: return "CONSTRAINT";
                case ErrorCategory::DEADLOCK:   return "DEADLOCK";
                case ErrorCategory::RESOURCE:   return "RESOURCE";
                case ErrorCategory::UNKNOWN:    return "UNKNOWN";
                default:                        return "INVALID";
            }
        }

        auto getSeverityName(ErrorSeverity severity) -> std::string
        {
            switch (severity)
            {
                case ErrorSeverity::INFO:     return "INFO";
                case ErrorSeverity::WARNING:  return "WARNING";
                case ErrorSeverity::ERROR:    return "ERROR";
                case ErrorSeverity::CRITICAL: return "CRITICAL";
                default:                      return "INVALID";
            }
        }

        auto optimizeQuery(const std::string& query) -> std::string
        {
            // Simple query optimization - remove extra whitespace
            std::string optimized = query;
            optimized = std::regex_replace(optimized, std::regex("\\s+"), " ");
            
            // Trim leading/trailing whitespace
            optimized.erase(0, optimized.find_first_not_of(" \t\n\r"));
            optimized.erase(optimized.find_last_not_of(" \t\n\r") + 1);
            
            return optimized;
        }

        auto analyzeQueryPerformance(const std::string& query, double executionTime) -> void
        {
            if (executionTime > 1000.0) // More than 1 second
            {
                ShowWarning("Slow query detected (%.2fms): %s", executionTime, query.c_str());
            }
        }

        auto suggestQueryImprovements(const std::string& query) -> std::vector<std::string>
        {
            std::vector<std::string> suggestions;
            
            // Simple suggestions based on query patterns
            if (query.find("SELECT *") != std::string::npos)
            {
                suggestions.push_back("Consider selecting only needed columns instead of using SELECT *");
            }
            
            if (query.find("WHERE") == std::string::npos && query.find("SELECT") != std::string::npos)
            {
                suggestions.push_back("Consider adding WHERE clause to limit results");
            }
            
            return suggestions;
        }

    } // namespace error_handling

} // namespace database