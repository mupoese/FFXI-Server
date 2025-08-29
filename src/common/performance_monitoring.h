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
#include "common/tracy.h"

#include <chrono>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>
#include <atomic>
#include <mutex>
#include <functional>

namespace performance
{
    // Performance monitoring and regression detection system
    namespace monitoring
    {
        // Metric types for performance tracking
        enum class MetricType : uint8
        {
            COUNTER = 0,     // Incrementing counter (e.g., packet count)
            GAUGE = 1,       // Current value (e.g., memory usage)
            TIMER = 2,       // Time-based measurements (e.g., query time)
            HISTOGRAM = 3    // Value distribution tracking
        };

        // Performance categories for organization
        enum class MetricCategory : uint8
        {
            NETWORK = 0,      // Network-related metrics
            DATABASE = 1,     // Database performance metrics  
            GAMEPLAY = 2,     // Game logic performance
            SYSTEM = 3,       // System resource metrics
            SPATIAL = 4,      // Spatial partitioning metrics
            CUSTOM = 5        // User-defined metrics
        };

        // Metric value with timestamp
        struct MetricValue
        {
            double value;
            std::chrono::steady_clock::time_point timestamp;
            
            MetricValue(double val) : value(val), timestamp(std::chrono::steady_clock::now()) {}
        };

        // Statistical summary for metric analysis
        struct MetricStatistics
        {
            double min = std::numeric_limits<double>::max();
            double max = std::numeric_limits<double>::lowest();
            double avg = 0.0;
            double median = 0.0;
            double p95 = 0.0;
            double p99 = 0.0;
            double stddev = 0.0;
            size_t count = 0;
            
            void reset()
            {
                min = std::numeric_limits<double>::max();
                max = std::numeric_limits<double>::lowest();
                avg = median = p95 = p99 = stddev = 0.0;
                count = 0;
            }
        };

        // Performance regression detection
        struct RegressionThreshold
        {
            double warningThreshold = 1.2;    // 20% increase
            double criticalThreshold = 1.5;   // 50% increase
            uint32 samplesRequired = 10;      // Minimum samples for detection
            uint32 comparisonPeriodMs = 300000; // 5 minutes comparison window
        };

        // Alert information for performance issues
        struct PerformanceAlert
        {
            std::string metricName;
            MetricCategory category;
            double currentValue;
            double baselineValue;
            double regressionRatio;
            std::chrono::steady_clock::time_point timestamp;
            std::string description;
            
            PerformanceAlert(const std::string& name, MetricCategory cat, double current, double baseline)
                : metricName(name), category(cat), currentValue(current), baselineValue(baseline)
                , regressionRatio(current / baseline), timestamp(std::chrono::steady_clock::now()) {}
        };

        // Individual metric tracker
        class MetricTracker
        {
        public:
            MetricTracker(const std::string& name, MetricType type, MetricCategory category);
            ~MetricTracker();

            // Value recording
            void recordValue(double value);
            void increment(double delta = 1.0);
            void decrement(double delta = 1.0);
            void setGaugeValue(double value);

            // Timer helpers
            auto startTimer() -> std::chrono::steady_clock::time_point;
            void endTimer(const std::chrono::steady_clock::time_point& start);
            
            // RAII timer helper
            class ScopedTimer
            {
            public:
                explicit ScopedTimer(MetricTracker& tracker) : tracker_(tracker), start_(std::chrono::steady_clock::now()) {}
                ~ScopedTimer() { tracker_.endTimer(start_); }
            private:
                MetricTracker& tracker_;
                std::chrono::steady_clock::time_point start_;
            };

            auto createScopedTimer() -> ScopedTimer { return ScopedTimer(*this); }

            // Statistics and analysis
            auto getStatistics(uint32 periodMs = 60000) const -> MetricStatistics;
            auto getCurrentValue() const -> double;
            auto getValueHistory(uint32 periodMs = 300000) const -> std::vector<MetricValue>;

            // Configuration
            void setRegressionThreshold(const RegressionThreshold& threshold);
            void enableRegression Detection(bool enable);

            // Metadata
            auto getName() const -> const std::string& { return name_; }
            auto getType() const -> MetricType { return type_; }
            auto getCategory() const -> MetricCategory { return category_; }

        private:
            std::string name_;
            MetricType type_;
            MetricCategory category_;
            
            mutable std::mutex valuesMutex_;
            std::vector<MetricValue> values_;
            std::atomic<double> currentValue_;
            
            RegressionThreshold regressionThreshold_;
            bool regressionDetectionEnabled_;
            
            static constexpr size_t MAX_VALUES = 10000;
            
            void cleanup Older Values(uint32 periodMs) const;
            auto detect Regression() const -> bool;
        };

        // Global performance monitoring system
        class PerformanceMonitoringSystem
        {
        public:
            PerformanceMonitoringSystem();
            ~PerformanceMonitoringSystem();

            // System lifecycle
            void initialize();
            void shutdown();

            // Metric management
            auto createMetric(const std::string& name, MetricType type, MetricCategory category) -> std::shared_ptr<MetricTracker>;
            auto getMetric(const std::string& name) -> std::shared_ptr<MetricTracker>;
            auto getMetricsByCategory(MetricCategory category) -> std::vector<std::shared_ptr<MetricTracker>>;
            void removeMetric(const std::string& name);

            // Quick metric recording
            void recordValue(const std::string& name, double value);
            void incrementCounter(const std::string& name, double delta = 1.0);
            void setGaugeValue(const std::string& name, double value);
            void recordTimerMs(const std::string& name, double timeMs);

            // Batch operations for efficiency
            void recordBatch(const std::unordered_map<std::string, double>& values);

            // Regression detection and alerting
            void enableGlobalRegressionDetection(bool enable);
            void setGlobalRegressionThreshold(const RegressionThreshold& threshold);
            auto getPerformanceAlerts(uint32 periodMs = 300000) -> std::vector<PerformanceAlert>;
            void clearAlerts();

            // Alert callbacks
            void setAlertCallback(std::function<void(const PerformanceAlert&)> callback);

            // Reporting and analysis
            auto generateReport(MetricCategory category = MetricCategory::CUSTOM) -> std::string;
            auto getSystemOverview() -> std::unordered_map<std::string, double>;
            auto exportMetrics(const std::string& format = "json") -> std::string;

            // Performance thresholds for CI/CD
            void setPerformanceThreshold(const std::string& metricName, double threshold);
            auto checkPerformanceThresholds() -> std::vector<std::string>;

            // Resource monitoring integration
            void enableSystemResourceMonitoring(bool enable);
            void updateSystemResources();

        private:
            std::unordered_map<std::string, std::shared_ptr<MetricTracker>> metrics_;
            mutable std::mutex metricsMutex_;
            
            std::vector<PerformanceAlert> alerts_;
            mutable std::mutex alertsMutex_;
            
            std::function<void(const PerformanceAlert&)> alertCallback_;
            
            RegressionThreshold globalRegressionThreshold_;
            bool globalRegressionDetectionEnabled_;
            bool systemResourceMonitoringEnabled_;
            
            std::unordered_map<std::string, double> performanceThresholds_;
            
            std::thread monitoringThread_;
            std::atomic<bool> shouldStop_;
            
            // Built-in system metrics
            void initializeBuiltinMetrics();
            void monitoringLoop();
            void processRegressionDetection();
            void updateBuiltinMetrics();
            auto getSystemCpuUsage() -> double;
            auto getSystemMemoryUsage() -> double;
            auto getSystemNetworkUsage() -> double;
        };

        // Scoped performance timer for automatic measurement
        class ScopedPerformanceTimer
        {
        public:
            explicit ScopedPerformanceTimer(const std::string& metricName);
            ~ScopedPerformanceTimer();

        private:
            std::string metricName_;
            std::chrono::steady_clock::time_point startTime_;
        };

        // Predefined metric names for common operations
        namespace metrics
        {
            // Network metrics
            inline constexpr const char* PACKETS_SENT = "network.packets_sent";
            inline constexpr const char* PACKETS_RECEIVED = "network.packets_received";
            inline constexpr const char* PACKET_SEND_TIME = "network.packet_send_time_ms";
            inline constexpr const char* NETWORK_LATENCY = "network.latency_ms";
            inline constexpr const char* BONDING_THROUGHPUT = "network.bonding_throughput_mbps";
            
            // Database metrics
            inline constexpr const char* DB_QUERY_TIME = "database.query_time_ms";
            inline constexpr const char* DB_CONNECTIONS_ACTIVE = "database.connections_active";
            inline constexpr const char* DB_QUERIES_EXECUTED = "database.queries_executed";
            inline constexpr const char* DB_QUERY_FAILURES = "database.query_failures";
            inline constexpr const char* DB_CONNECTION_POOL_UTILIZATION = "database.connection_pool_utilization";
            
            // Spatial system metrics
            inline constexpr const char* SPATIAL_ENTITIES_TRACKED = "spatial.entities_tracked";
            inline constexpr const char* SPATIAL_QUERY_TIME = "spatial.query_time_ms";
            inline constexpr const char* SPATIAL_QUERIES_EXECUTED = "spatial.queries_executed";
            inline constexpr const char* SPATIAL_UPDATES_PROCESSED = "spatial.updates_processed";
            
            // Gameplay metrics
            inline constexpr const char* PLAYERS_ONLINE = "gameplay.players_online";
            inline constexpr const char* ZONES_ACTIVE = "gameplay.zones_active";
            inline constexpr const char* ENTITIES_SPAWNED = "gameplay.entities_spawned";
            inline constexpr const char* TICK_TIME = "gameplay.tick_time_ms";
            
            // System metrics
            inline constexpr const char* CPU_USAGE = "system.cpu_usage_percent";
            inline constexpr const char* MEMORY_USAGE = "system.memory_usage_mb";
            inline constexpr const char* MEMORY_USAGE_PERCENT = "system.memory_usage_percent";
            inline constexpr const char* NETWORK_USAGE = "system.network_usage_mbps";
        }

        // Convenience macros for performance measurement
        #define PERF_TIMER(name) performance::monitoring::ScopedPerformanceTimer _perf_timer(name)
        #define PERF_TIMER_START(tracker) auto _timer_start = tracker->startTimer()
        #define PERF_TIMER_END(tracker) tracker->endTimer(_timer_start)
        #define PERF_SCOPED_TIMER(tracker) auto _scoped_timer = tracker->createScopedTimer()

        // Global system access
        auto getPerformanceSystem() -> PerformanceMonitoringSystem&;
        void initializePerformanceSystem();
        void shutdownPerformanceSystem();

        // Convenience functions for quick metrics
        void recordMetric(const std::string& name, double value, MetricCategory category = MetricCategory::CUSTOM);
        void incrementCounter(const std::string& name, double delta = 1.0);
        void recordTimer(const std::string& name, double timeMs);
        auto createTimer(const std::string& name) -> std::shared_ptr<MetricTracker>;

        // CI/CD integration helpers
        auto generateCIReport() -> std::string;
        auto checkRegressions() -> bool;
        void setRegressionThresholds(const std::unordered_map<std::string, RegressionThreshold>& thresholds);

    } // namespace monitoring

} // namespace performance