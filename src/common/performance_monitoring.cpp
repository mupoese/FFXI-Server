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

#include "performance_monitoring.h"

#include "common/logging.h"
#include "common/settings.h"
#include "common/tracy.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <sstream>
#include <thread>

#ifdef __linux__
#include <sys/sysinfo.h>
#include <unistd.h>
#endif

namespace performance
{
    namespace monitoring
    {
        namespace
        {
            std::unique_ptr<PerformanceMonitoringSystem> g_performanceSystem;
        }

        // MetricTracker implementation
        MetricTracker::MetricTracker(const std::string& name, MetricType type, MetricCategory category)
        : name_(name), type_(type), category_(category), currentValue_(0.0), regressionDetectionEnabled_(false)
        {
            TracyZoneScoped;
            values_.reserve(MAX_VALUES);
        }

        MetricTracker::~MetricTracker()
        {
            TracyZoneScoped;
        }

        void MetricTracker::recordValue(double value)
        {
            TracyZoneScoped;
            
            currentValue_.store(value);
            
            std::lock_guard<std::mutex> lock(valuesMutex_);
            values_.emplace_back(value);
            
            // Cleanup old values to prevent memory growth
            if (values_.size() > MAX_VALUES)
            {
                values_.erase(values_.begin(), values_.begin() + (values_.size() - MAX_VALUES));
            }
            
            // Check for regression if enabled
            if (regressionDetectionEnabled_)
            {
                detectRegression();
            }
        }

        void MetricTracker::increment(double delta)
        {
            double newValue = currentValue_.load() + delta;
            recordValue(newValue);
        }

        void MetricTracker::decrement(double delta)
        {
            double newValue = currentValue_.load() - delta;
            recordValue(newValue);
        }

        void MetricTracker::setGaugeValue(double value)
        {
            recordValue(value);
        }

        auto MetricTracker::startTimer() -> std::chrono::steady_clock::time_point
        {
            return std::chrono::steady_clock::now();
        }

        void MetricTracker::endTimer(const std::chrono::steady_clock::time_point& start)
        {
            TracyZoneScoped;
            
            const auto end = std::chrono::steady_clock::now();
            const auto duration = std::chrono::duration<double, std::milli>(end - start).count();
            recordValue(duration);
        }

        auto MetricTracker::getStatistics(uint32 periodMs) const -> MetricStatistics
        {
            TracyZoneScoped;
            
            std::lock_guard<std::mutex> lock(valuesMutex_);
            
            MetricStatistics stats;
            
            if (values_.empty())
            {
                return stats;
            }
            
            // Filter values within the specified period
            const auto cutoffTime = std::chrono::steady_clock::now() - std::chrono::milliseconds(periodMs);
            std::vector<double> recentValues;
            
            for (const auto& metric : values_)
            {
                if (metric.timestamp >= cutoffTime)
                {
                    recentValues.push_back(metric.value);
                }
            }
            
            if (recentValues.empty())
            {
                return stats;
            }
            
            // Calculate basic statistics
            stats.count = recentValues.size();
            stats.min = *std::min_element(recentValues.begin(), recentValues.end());
            stats.max = *std::max_element(recentValues.begin(), recentValues.end());
            
            // Calculate average
            double sum = 0.0;
            for (double value : recentValues)
            {
                sum += value;
            }
            stats.avg = sum / static_cast<double>(recentValues.size());
            
            // Calculate median and percentiles
            std::sort(recentValues.begin(), recentValues.end());
            const size_t medianIndex = recentValues.size() / 2;
            stats.median = recentValues.size() % 2 == 0 ? 
                (recentValues[medianIndex - 1] + recentValues[medianIndex]) / 2.0 : 
                recentValues[medianIndex];
            
            const size_t p95Index = static_cast<size_t>(recentValues.size() * 0.95);
            const size_t p99Index = static_cast<size_t>(recentValues.size() * 0.99);
            stats.p95 = recentValues[std::min(p95Index, recentValues.size() - 1)];
            stats.p99 = recentValues[std::min(p99Index, recentValues.size() - 1)];
            
            // Calculate standard deviation
            double variance = 0.0;
            for (double value : recentValues)
            {
                variance += (value - stats.avg) * (value - stats.avg);
            }
            variance /= static_cast<double>(recentValues.size());
            stats.stddev = std::sqrt(variance);
            
            return stats;
        }

        auto MetricTracker::getCurrentValue() const -> double
        {
            return currentValue_.load();
        }

        auto MetricTracker::getValueHistory(uint32 periodMs) const -> std::vector<MetricValue>
        {
            TracyZoneScoped;
            
            std::lock_guard<std::mutex> lock(valuesMutex_);
            
            const auto cutoffTime = std::chrono::steady_clock::now() - std::chrono::milliseconds(periodMs);
            std::vector<MetricValue> recentValues;
            
            for (const auto& metric : values_)
            {
                if (metric.timestamp >= cutoffTime)
                {
                    recentValues.push_back(metric);
                }
            }
            
            return recentValues;
        }

        void MetricTracker::setRegressionThreshold(const RegressionThreshold& threshold)
        {
            regressionThreshold_ = threshold;
        }

        void MetricTracker::enableRegressionDetection(bool enable)
        {
            regressionDetectionEnabled_ = enable;
        }

        auto MetricTracker::detectRegression() const -> bool
        {
            TracyZoneScoped;
            
            if (values_.size() < regressionThreshold_.samplesRequired * 2)
            {
                return false; // Not enough samples for comparison
            }
            
            // Get recent values and baseline values
            const auto now = std::chrono::steady_clock::now();
            const auto recentCutoff = now - std::chrono::milliseconds(regressionThreshold_.comparisonPeriodMs / 2);
            const auto baselineCutoff = now - std::chrono::milliseconds(regressionThreshold_.comparisonPeriodMs);
            
            std::vector<double> recentValues, baselineValues;
            
            for (const auto& metric : values_)
            {
                if (metric.timestamp >= recentCutoff)
                {
                    recentValues.push_back(metric.value);
                }
                else if (metric.timestamp >= baselineCutoff)
                {
                    baselineValues.push_back(metric.value);
                }
            }
            
            if (recentValues.size() < regressionThreshold_.samplesRequired || 
                baselineValues.size() < regressionThreshold_.samplesRequired)
            {
                return false;
            }
            
            // Calculate averages
            const double recentAvg = std::accumulate(recentValues.begin(), recentValues.end(), 0.0) / recentValues.size();
            const double baselineAvg = std::accumulate(baselineValues.begin(), baselineValues.end(), 0.0) / baselineValues.size();
            
            if (baselineAvg <= 0.0)
            {
                return false; // Avoid division by zero
            }
            
            const double ratio = recentAvg / baselineAvg;
            return ratio >= regressionThreshold_.warningThreshold;
        }

        // PerformanceMonitoringSystem implementation
        PerformanceMonitoringSystem::PerformanceMonitoringSystem()
        : globalRegressionDetectionEnabled_(false), systemResourceMonitoringEnabled_(true), shouldStop_(false)
        {
            TracyZoneScoped;
        }

        PerformanceMonitoringSystem::~PerformanceMonitoringSystem()
        {
            TracyZoneScoped;
            shutdown();
        }

        void PerformanceMonitoringSystem::initialize()
        {
            TracyZoneScoped;
            
            ShowInfo("PerformanceMonitoringSystem: Initializing...");
            
            initializeBuiltinMetrics();
            
            // Start monitoring thread
            shouldStop_.store(false);
            monitoringThread_ = std::thread(&PerformanceMonitoringSystem::monitoringLoop, this);
            
            ShowInfo("PerformanceMonitoringSystem: Initialized successfully");
        }

        void PerformanceMonitoringSystem::shutdown()
        {
            TracyZoneScoped;
            
            if (shouldStop_.load())
            {
                return; // Already shutdown
            }
            
            ShowInfo("PerformanceMonitoringSystem: Shutting down...");
            
            shouldStop_.store(true);
            if (monitoringThread_.joinable())
            {
                monitoringThread_.join();
            }
            
            std::lock_guard<std::mutex> lock(metricsMutex_);
            metrics_.clear();
            
            ShowInfo("PerformanceMonitoringSystem: Shutdown completed");
        }

        auto PerformanceMonitoringSystem::createMetric(const std::string& name, MetricType type, MetricCategory category) -> std::shared_ptr<MetricTracker>
        {
            TracyZoneScoped;
            
            std::lock_guard<std::mutex> lock(metricsMutex_);
            
            auto metric = std::make_shared<MetricTracker>(name, type, category);
            
            if (globalRegressionDetectionEnabled_)
            {
                metric->setRegressionThreshold(globalRegressionThreshold_);
                metric->enableRegressionDetection(true);
            }
            
            metrics_[name] = metric;
            return metric;
        }

        auto PerformanceMonitoringSystem::getMetric(const std::string& name) -> std::shared_ptr<MetricTracker>
        {
            std::lock_guard<std::mutex> lock(metricsMutex_);
            
            auto it = metrics_.find(name);
            return it != metrics_.end() ? it->second : nullptr;
        }

        auto PerformanceMonitoringSystem::getMetricsByCategory(MetricCategory category) -> std::vector<std::shared_ptr<MetricTracker>>
        {
            std::lock_guard<std::mutex> lock(metricsMutex_);
            
            std::vector<std::shared_ptr<MetricTracker>> result;
            for (const auto& [name, metric] : metrics_)
            {
                if (metric->getCategory() == category)
                {
                    result.push_back(metric);
                }
            }
            return result;
        }

        void PerformanceMonitoringSystem::removeMetric(const std::string& name)
        {
            std::lock_guard<std::mutex> lock(metricsMutex_);
            metrics_.erase(name);
        }

        void PerformanceMonitoringSystem::recordValue(const std::string& name, double value)
        {
            auto metric = getMetric(name);
            if (!metric)
            {
                metric = createMetric(name, MetricType::GAUGE, MetricCategory::CUSTOM);
            }
            metric->recordValue(value);
        }

        void PerformanceMonitoringSystem::incrementCounter(const std::string& name, double delta)
        {
            auto metric = getMetric(name);
            if (!metric)
            {
                metric = createMetric(name, MetricType::COUNTER, MetricCategory::CUSTOM);
            }
            metric->increment(delta);
        }

        void PerformanceMonitoringSystem::setGaugeValue(const std::string& name, double value)
        {
            auto metric = getMetric(name);
            if (!metric)
            {
                metric = createMetric(name, MetricType::GAUGE, MetricCategory::CUSTOM);
            }
            metric->setGaugeValue(value);
        }

        void PerformanceMonitoringSystem::recordTimerMs(const std::string& name, double timeMs)
        {
            auto metric = getMetric(name);
            if (!metric)
            {
                metric = createMetric(name, MetricType::TIMER, MetricCategory::CUSTOM);
            }
            metric->recordValue(timeMs);
        }

        void PerformanceMonitoringSystem::recordBatch(const std::unordered_map<std::string, double>& values)
        {
            TracyZoneScoped;
            
            for (const auto& [name, value] : values)
            {
                recordValue(name, value);
            }
        }

        void PerformanceMonitoringSystem::enableGlobalRegressionDetection(bool enable)
        {
            globalRegressionDetectionEnabled_ = enable;
            
            std::lock_guard<std::mutex> lock(metricsMutex_);
            for (const auto& [name, metric] : metrics_)
            {
                metric->enableRegressionDetection(enable);
            }
        }

        void PerformanceMonitoringSystem::setGlobalRegressionThreshold(const RegressionThreshold& threshold)
        {
            globalRegressionThreshold_ = threshold;
            
            std::lock_guard<std::mutex> lock(metricsMutex_);
            for (const auto& [name, metric] : metrics_)
            {
                metric->setRegressionThreshold(threshold);
            }
        }

        auto PerformanceMonitoringSystem::getPerformanceAlerts(uint32 periodMs) -> std::vector<PerformanceAlert>
        {
            std::lock_guard<std::mutex> lock(alertsMutex_);
            
            const auto cutoffTime = std::chrono::steady_clock::now() - std::chrono::milliseconds(periodMs);
            std::vector<PerformanceAlert> recentAlerts;
            
            for (const auto& alert : alerts_)
            {
                if (alert.timestamp >= cutoffTime)
                {
                    recentAlerts.push_back(alert);
                }
            }
            
            return recentAlerts;
        }

        void PerformanceMonitoringSystem::clearAlerts()
        {
            std::lock_guard<std::mutex> lock(alertsMutex_);
            alerts_.clear();
        }

        void PerformanceMonitoringSystem::setAlertCallback(std::function<void(const PerformanceAlert&)> callback)
        {
            alertCallback_ = std::move(callback);
        }

        auto PerformanceMonitoringSystem::generateReport(MetricCategory category) -> std::string
        {
            TracyZoneScoped;
            
            std::ostringstream report;
            report << "=== Performance Monitoring Report ===\n";
            report << "Generated: " << std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::system_clock::now().time_since_epoch()).count() << "\n\n";
            
            std::lock_guard<std::mutex> lock(metricsMutex_);
            
            for (const auto& [name, metric] : metrics_)
            {
                if (category != MetricCategory::CUSTOM && metric->getCategory() != category)
                {
                    continue;
                }
                
                const auto stats = metric->getStatistics();
                report << "Metric: " << name << "\n";
                report << "  Current: " << metric->getCurrentValue() << "\n";
                report << "  Avg: " << stats.avg << " | Min: " << stats.min << " | Max: " << stats.max << "\n";
                report << "  P95: " << stats.p95 << " | P99: " << stats.p99 << "\n";
                report << "  Samples: " << stats.count << "\n\n";
            }
            
            return report.str();
        }

        auto PerformanceMonitoringSystem::getSystemOverview() -> std::unordered_map<std::string, double>
        {
            std::unordered_map<std::string, double> overview;
            
            std::lock_guard<std::mutex> lock(metricsMutex_);
            for (const auto& [name, metric] : metrics_)
            {
                overview[name] = metric->getCurrentValue();
            }
            
            return overview;
        }

        void PerformanceMonitoringSystem::enableSystemResourceMonitoring(bool enable)
        {
            systemResourceMonitoringEnabled_ = enable;
        }

        void PerformanceMonitoringSystem::initializeBuiltinMetrics()
        {
            TracyZoneScoped;
            
            // Network metrics
            createMetric(metrics::PACKETS_SENT, MetricType::COUNTER, MetricCategory::NETWORK);
            createMetric(metrics::PACKETS_RECEIVED, MetricType::COUNTER, MetricCategory::NETWORK);
            createMetric(metrics::PACKET_SEND_TIME, MetricType::TIMER, MetricCategory::NETWORK);
            createMetric(metrics::NETWORK_LATENCY, MetricType::GAUGE, MetricCategory::NETWORK);
            createMetric(metrics::BONDING_THROUGHPUT, MetricType::GAUGE, MetricCategory::NETWORK);
            
            // Database metrics
            createMetric(metrics::DB_QUERY_TIME, MetricType::TIMER, MetricCategory::DATABASE);
            createMetric(metrics::DB_CONNECTIONS_ACTIVE, MetricType::GAUGE, MetricCategory::DATABASE);
            createMetric(metrics::DB_QUERIES_EXECUTED, MetricType::COUNTER, MetricCategory::DATABASE);
            createMetric(metrics::DB_QUERY_FAILURES, MetricType::COUNTER, MetricCategory::DATABASE);
            createMetric(metrics::DB_CONNECTION_POOL_UTILIZATION, MetricType::GAUGE, MetricCategory::DATABASE);
            
            // Spatial metrics
            createMetric(metrics::SPATIAL_ENTITIES_TRACKED, MetricType::GAUGE, MetricCategory::SPATIAL);
            createMetric(metrics::SPATIAL_QUERY_TIME, MetricType::TIMER, MetricCategory::SPATIAL);
            createMetric(metrics::SPATIAL_QUERIES_EXECUTED, MetricType::COUNTER, MetricCategory::SPATIAL);
            
            // System metrics
            if (systemResourceMonitoringEnabled_)
            {
                createMetric(metrics::CPU_USAGE, MetricType::GAUGE, MetricCategory::SYSTEM);
                createMetric(metrics::MEMORY_USAGE, MetricType::GAUGE, MetricCategory::SYSTEM);
                createMetric(metrics::MEMORY_USAGE_PERCENT, MetricType::GAUGE, MetricCategory::SYSTEM);
            }
        }

        void PerformanceMonitoringSystem::monitoringLoop()
        {
            TracyZoneScoped;
            
            while (!shouldStop_.load())
            {
                updateBuiltinMetrics();
                processRegressionDetection();
                
                std::this_thread::sleep_for(std::chrono::seconds(30)); // Update every 30 seconds
            }
        }

        void PerformanceMonitoringSystem::processRegressionDetection()
        {
            TracyZoneScoped;
            
            if (!globalRegressionDetectionEnabled_)
            {
                return;
            }
            
            std::lock_guard<std::mutex> lock(metricsMutex_);
            
            for (const auto& [name, metric] : metrics_)
            {
                // Simple regression detection based on recent vs baseline comparison
                const auto recentStats = metric->getStatistics(60000);  // Last minute
                const auto baselineStats = metric->getStatistics(300000); // Last 5 minutes
                
                if (recentStats.count >= 5 && baselineStats.count >= 10)
                {
                    const double ratio = recentStats.avg / baselineStats.avg;
                    
                    if (ratio >= globalRegressionThreshold_.warningThreshold)
                    {
                        PerformanceAlert alert(name, metric->getCategory(), recentStats.avg, baselineStats.avg);
                        alert.description = "Performance regression detected";
                        
                        {
                            std::lock_guard<std::mutex> alertLock(alertsMutex_);
                            alerts_.push_back(alert);
                        }
                        
                        if (alertCallback_)
                        {
                            alertCallback_(alert);
                        }
                        
                        ShowWarning("Performance regression detected for %s: %.2f%% increase (%.2f -> %.2f)",
                                   name.c_str(), (ratio - 1.0) * 100.0, baselineStats.avg, recentStats.avg);
                    }
                }
            }
        }

        void PerformanceMonitoringSystem::updateBuiltinMetrics()
        {
            TracyZoneScoped;
            
            if (!systemResourceMonitoringEnabled_)
            {
                return;
            }
            
            // Update system resource metrics
            setGaugeValue(metrics::CPU_USAGE, getSystemCpuUsage());
            setGaugeValue(metrics::MEMORY_USAGE, getSystemMemoryUsage());
        }

        auto PerformanceMonitoringSystem::getSystemCpuUsage() -> double
        {
            #ifdef __linux__
            static auto lastCpuTimes = std::vector<long>{0, 0, 0, 0};
            
            std::ifstream procStat("/proc/stat");
            std::string line;
            std::getline(procStat, line);
            
            std::istringstream iss(line);
            std::string cpuLabel;
            std::vector<long> times(4);
            iss >> cpuLabel >> times[0] >> times[1] >> times[2] >> times[3];
            
            const long idleTime = times[3];
            const long totalTime = times[0] + times[1] + times[2] + times[3];
            
            const long idleDelta = idleTime - lastCpuTimes[3];
            const long totalDelta = totalTime - (lastCpuTimes[0] + lastCpuTimes[1] + lastCpuTimes[2] + lastCpuTimes[3]);
            
            lastCpuTimes = times;
            
            if (totalDelta == 0)
            {
                return 0.0;
            }
            
            return (1.0 - static_cast<double>(idleDelta) / static_cast<double>(totalDelta)) * 100.0;
            #else
            return 0.0; // Not implemented for non-Linux platforms
            #endif
        }

        auto PerformanceMonitoringSystem::getSystemMemoryUsage() -> double
        {
            #ifdef __linux__
            struct sysinfo info;
            if (sysinfo(&info) == 0)
            {
                const double totalMemMB = static_cast<double>(info.totalram * info.mem_unit) / (1024.0 * 1024.0);
                const double freeMemMB = static_cast<double>(info.freeram * info.mem_unit) / (1024.0 * 1024.0);
                return totalMemMB - freeMemMB;
            }
            #endif
            return 0.0;
        }

        // ScopedPerformanceTimer implementation
        ScopedPerformanceTimer::ScopedPerformanceTimer(const std::string& metricName)
        : metricName_(metricName), startTime_(std::chrono::steady_clock::now())
        {
            TracyZoneScoped;
        }

        ScopedPerformanceTimer::~ScopedPerformanceTimer()
        {
            TracyZoneScoped;
            
            const auto endTime = std::chrono::steady_clock::now();
            const auto duration = std::chrono::duration<double, std::milli>(endTime - startTime_).count();
            
            getPerformanceSystem().recordTimerMs(metricName_, duration);
        }

        // Global system functions
        auto getPerformanceSystem() -> PerformanceMonitoringSystem&
        {
            if (!g_performanceSystem)
            {
                g_performanceSystem = std::make_unique<PerformanceMonitoringSystem>();
            }
            return *g_performanceSystem;
        }

        void initializePerformanceSystem()
        {
            getPerformanceSystem().initialize();
        }

        void shutdownPerformanceSystem()
        {
            if (g_performanceSystem)
            {
                g_performanceSystem->shutdown();
                g_performanceSystem.reset();
            }
        }

        // Convenience functions
        void recordMetric(const std::string& name, double value, MetricCategory category)
        {
            getPerformanceSystem().recordValue(name, value);
        }

        void incrementCounter(const std::string& name, double delta)
        {
            getPerformanceSystem().incrementCounter(name, delta);
        }

        void recordTimer(const std::string& name, double timeMs)
        {
            getPerformanceSystem().recordTimerMs(name, timeMs);
        }

        auto createTimer(const std::string& name) -> std::shared_ptr<MetricTracker>
        {
            return getPerformanceSystem().createMetric(name, MetricType::TIMER, MetricCategory::CUSTOM);
        }

        auto generateCIReport() -> std::string
        {
            return getPerformanceSystem().generateReport();
        }

        auto checkRegressions() -> bool
        {
            const auto alerts = getPerformanceSystem().getPerformanceAlerts();
            return !alerts.empty();
        }

    } // namespace monitoring

} // namespace performance