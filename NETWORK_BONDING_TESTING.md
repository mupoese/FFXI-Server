# Network Bonding Testing Guide

This guide provides comprehensive instructions for testing network bonding performance with multiple connections for FFXI servers. The testing suite includes detailed logging and explanations of connection bonding behavior.

## Overview

The network bonding testing suite consists of three main components:

1. **Network Bonding Test Suite** (`network_bonding_test_suite.py`) - Basic bonding functionality and mode comparison
2. **FFXI Performance Test** (`network_bonding_performance_test.py`) - FFXI-specific traffic simulation and performance analysis
3. **Test Runner** (`network_bonding_test_runner.py`) - Unified orchestration and comprehensive reporting

## Test Components Explained

### 1. Basic Network Bonding Test Suite

**Purpose**: Tests fundamental network bonding capabilities across different modes and configurations.

**What it tests**:
- Baseline performance without bonding
- Performance with different bonding modes (balance-xor, 802.3ad, active-backup)
- Multi-connection scaling behavior
- Failover scenarios with interface failures
- Protocol-specific performance (TCP vs UDP)
- Load balancing verification

**Key Metrics**:
- Aggregate throughput (Mbps)
- Average latency (ms)
- CPU and memory utilization
- Error rates
- Traffic distribution across interfaces

### 2. FFXI-Specific Performance Test

**Purpose**: Simulates realistic FFXI server traffic patterns to measure bonding effectiveness in real-world scenarios.

**What it simulates**:
- Position updates (20 Hz per player)
- Chat messages (10 per minute per player)
- Zone change bursts (large data transfers)
- Auction house searches (query/response patterns)
- Multiple concurrent player connections

**Test Scenarios**:
- **Light Load**: 25 players (off-peak simulation)
- **Medium Load**: 100 players (normal activity)
- **Heavy Load**: 200 players (busy periods)
- **Peak Load**: 400+ players (maximum capacity testing)

### 3. Unified Test Runner

**Purpose**: Orchestrates all tests and generates comprehensive reports with deployment recommendations.

**Features**:
- Automated test sequencing
- Real-time progress monitoring
- Unified analysis across all test types
- Performance comparison and trend analysis
- Human-readable summary reports
- CSV export for spreadsheet analysis

## Running the Tests

### Prerequisites

```bash
# Install required Python packages
pip install psutil asyncio

# Ensure network bonding tools are available
sudo modprobe bonding

# Verify network interfaces are available
ip link show
```

### Quick Start - Comprehensive Testing

For a complete network bonding evaluation:

```bash
# Run full test suite with default settings
python3 tools/network_bonding_test_runner.py

# Run with custom configuration
python3 tools/network_bonding_test_runner.py \
    --test-duration 120 \
    --max-connections 100 \
    --max-players 300 \
    --bonding-modes balance-xor 802.3ad active-backup \
    --verbose
```

### Individual Test Components

#### 1. Basic Bonding Tests

```bash
# Run basic bonding test suite
python3 tools/network_bonding_test_suite.py \
    --duration 60 \
    --connections 10 \
    --modes balance-xor 802.3ad active-backup \
    --output-file basic_bonding_results.json \
    --verbose
```

#### 2. FFXI Performance Tests

```bash
# Run FFXI-specific performance tests
python3 tools/network_bonding_performance_test.py \
    --output-file ffxi_performance_results.json \
    --verbose
```

## Test Output and Analysis

### Real-Time Monitoring

During test execution, you'll see real-time logging like this:

```
2024-01-15 10:30:45 - INFO - [NetworkBondingTestSuite] === Baseline Performance Test ===
2024-01-15 10:30:45 - INFO - [NetworkBondingTestSuite] EXPLANATION: This test measures network performance using standard single-interface networking without any bonding...
2024-01-15 10:30:47 - INFO - [NetworkBondingTestSuite] Baseline Results - Throughput: 45.20 Mbps, Latency: 2.80 ms

2024-01-15 10:31:15 - INFO - [NetworkBondingTestSuite] === Bonding Mode Test: balance-xor ===
2024-01-15 10:31:15 - INFO - [NetworkBondingTestSuite] EXPLANATION: Balance-XOR mode distributes FFXI connections across interfaces using hash-based load balancing...
2024-01-15 10:31:45 - INFO - [NetworkBondingTestSuite] Performance vs Baseline - Throughput: +58.4%, Latency: -12.5%
```

### Generated Reports

#### 1. Comprehensive JSON Report
```json
{
  "test_metadata": {
    "timestamp": 1705320645,
    "configuration": {...},
    "test_environment": {...}
  },
  "test_results": {
    "basic_bonding": {...},
    "ffxi_performance": {...},
    "load_testing": {...}
  },
  "unified_analysis": {
    "bonding_effectiveness": {
      "best_mode": "802.3ad",
      "throughput_improvement_percent": 67.2,
      "latency_improvement_percent": 15.8
    },
    "scalability_analysis": {...},
    "recommendations": [...]
  }
}
```

#### 2. Human-Readable Summary
```
FFXI Server Network Bonding Performance Test Summary
============================================================

Test Timestamp: Mon Jan 15 10:30:45 2024
Test Environment: Linux 5.15.0
CPU Cores: 8

Performance Summary:
  Total Tests: 15
  Test Duration: 25.3 minutes
  Overall Assessment: Excellent - Network bonding provides significant performance benefits

Network Bonding Effectiveness:
  Best Mode: 802.3ad
  Throughput Improvement: 67.2%
  Latency Improvement: 15.8%

Key Insights:
  • Network bonding provides 67.2% throughput improvement with 802.3ad mode
  • Successfully tested up to 400 concurrent FFXI players with 89.5 Mbps peak throughput
  • Maximum tested: 50 concurrent connections with 95.2 Mbps aggregate throughput

Recommendations:
  1. Deploy with 802.3ad bonding mode for 67.2% performance improvement
  2. Recommended player capacity: 300 concurrent players for optimal performance
  3. Enable RSS/RPS optimization for multi-core CPU utilization
```

#### 3. CSV Data Export
For spreadsheet analysis and graphing:
```csv
Test_Type,Test_Name,Bonding_Mode,Throughput_Mbps,Latency_ms,Connection_Count,Player_Count,Explanation
Basic_Bonding,baseline,none,45.2,2.8,,,Single-interface baseline measurement
Basic_Bonding,bonding_balance-xor,balance-xor,72.3,2.5,,,Performance test with balance-xor bonding mode
Basic_Bonding,bonding_802.3ad,802.3ad,81.4,2.4,,,Performance test with 802.3ad bonding mode
FFXI_Performance,light_load,bonded,62.5,3.1,,25,FFXI light_load simulation with realistic traffic patterns
FFXI_Performance,medium_load,bonded,75.0,3.6,,100,FFXI medium_load simulation with realistic traffic patterns
Load_Testing,connections_1,bonded,45.0,2.5,1,,Load test with 1 concurrent connections
Load_Testing,connections_5,bonded,47.7,2.7,5,,Load test with 5 concurrent connections
```

## Understanding Test Results

### Performance Metrics Explained

#### Throughput Measurements
- **Aggregate Throughput**: Total bandwidth across all connections
- **Per-Connection Throughput**: Average bandwidth per individual connection
- **Peak Throughput**: Maximum observed bandwidth during test

#### Latency Measurements
- **Average Latency**: Mean round-trip time for requests
- **99th Percentile Latency**: Latency experienced by worst 1% of requests
- **Jitter**: Variation in latency measurements

#### Load Distribution
- **Interface Distribution**: Percentage of traffic on each bonded interface
- **Balance Variance**: Statistical measure of load balancing effectiveness
- **Efficiency Score**: Overall bonding efficiency rating (0-100)

### Bonding Mode Comparison

#### balance-xor
- **Best for**: Medium loads with diverse connection patterns
- **Strengths**: Good load distribution, connection affinity
- **Weaknesses**: May have uneven load with limited connection diversity
- **Expected Improvement**: 40-60% throughput increase

#### 802.3ad (LACP)
- **Best for**: High loads with switch cooperation
- **Strengths**: Optimal load balancing, industry standard
- **Weaknesses**: Requires switch configuration
- **Expected Improvement**: 60-80% throughput increase

#### active-backup
- **Best for**: Fault tolerance over performance
- **Strengths**: Simple failover, no packet reordering
- **Weaknesses**: No bandwidth aggregation
- **Expected Improvement**: 0% throughput (fault tolerance only)

### FFXI-Specific Insights

#### Traffic Pattern Analysis
The tests simulate realistic FFXI traffic patterns:

1. **Position Updates**: Continuous small packets (64-128 bytes) at 20 Hz
2. **Chat Messages**: Variable-size packets (50-200 bytes) at irregular intervals
3. **Zone Changes**: Large bursts (1400 bytes) with multiple packet exchanges
4. **Auction House**: Query/response patterns with moderate-size packets (512 bytes)

#### Player Scaling Analysis
Performance scaling by player count:

- **1-50 players**: Linear scaling with minimal latency increase
- **50-150 players**: Good scaling with moderate resource usage
- **150-300 players**: Diminishing returns, CPU becomes limiting factor
- **300+ players**: Performance plateau, requires optimized configuration

## Troubleshooting

### Common Issues

#### 1. "Permission denied" errors
```bash
# Run with sudo for network configuration
sudo python3 tools/network_bonding_test_runner.py
```

#### 2. "Address already in use" errors
```bash
# Check for running processes on test ports
netstat -tulpn | grep :50000

# Kill conflicting processes
sudo fuser -k 50000/tcp
```

#### 3. Low performance results
- Verify network interfaces are properly configured
- Check for CPU/memory constraints
- Ensure bonding module is loaded: `lsmod | grep bonding`
- Verify switch configuration for LACP mode

#### 4. Uneven load distribution
- Check hash policy: `cat /sys/class/net/bond0/bonding/xmit_hash_policy`
- Verify interface link status: `cat /proc/net/bonding/bond0`
- Consider changing to layer3+4 hashing

### Performance Optimization Tips

#### 1. System-Level Optimizations
```bash
# Apply network optimizations
sudo tools/network_optimization.sh optimize-all

# Configure RSS/RPS
sudo tools/network_optimization.sh configure-bonding bond0

# Check interrupt distribution
cat /proc/interrupts | grep eth
```

#### 2. Bonding Configuration
```bash
# Optimal hash policy for FFXI traffic
echo 'layer3+4' > /sys/class/net/bond0/bonding/xmit_hash_policy

# Fast LACP for quicker failover
echo 'fast' > /sys/class/net/bond0/bonding/lacp_rate

# Frequent link monitoring
echo '100' > /sys/class/net/bond0/bonding/miimon
```

## Advanced Testing Scenarios

### Custom Load Patterns

Create custom test configuration:

```json
{
  "test_duration": 180,
  "connection_counts": [1, 10, 25, 50, 100],
  "payload_sizes": [64, 256, 512, 1024, 1400],
  "bonding_modes": ["balance-xor", "802.3ad"],
  "interfaces": ["eth0", "eth1", "eth2"],
  "ffxi_scenarios": {
    "peak_event": {"players": 500, "duration": 300},
    "raid_scenario": {"players": 75, "duration": 600}
  }
}
```

Run with custom configuration:
```bash
python3 tools/network_bonding_test_runner.py --config custom_config.json
```

### Continuous Monitoring

For ongoing performance monitoring:

```bash
# Run periodic tests (every hour)
while true; do
    python3 tools/network_bonding_performance_test.py \
        --output-file "monitoring_$(date +%Y%m%d_%H%M).json"
    sleep 3600
done
```

### Integration with CI/CD

Add to automated testing pipeline:

```yaml
# .github/workflows/network_performance.yml
name: Network Bonding Performance Tests
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  network_tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install psutil
      - name: Run network bonding tests
        run: |
          python3 tools/network_bonding_test_runner.py \
            --test-duration 30 \
            --max-connections 25 \
            --max-players 100
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: network-test-results
          path: network_bonding_test_results/
```

## Interpreting Results for Production

### Performance Baselines

Use these guidelines for production deployment:

#### Throughput Targets
- **Small Server** (< 100 players): 30-50 Mbps
- **Medium Server** (100-300 players): 50-100 Mbps  
- **Large Server** (300+ players): 100+ Mbps

#### Latency Targets
- **Excellent**: < 2ms average latency
- **Good**: 2-5ms average latency
- **Acceptable**: 5-10ms average latency
- **Poor**: > 10ms average latency

#### Resource Utilization
- **CPU Usage**: Keep below 80% for stable performance
- **Memory Usage**: Monitor for memory leaks during long tests
- **Network Utilization**: Aim for < 80% of interface capacity

### Capacity Planning

Based on test results, plan server capacity:

1. **Identify Performance Ceiling**: Maximum players before performance degrades
2. **Plan for Growth**: Target 70% of maximum tested capacity
3. **Account for Peak Load**: Plan for 150% of average concurrent users
4. **Monitor Real-World Performance**: Compare test results with production metrics

## Conclusion

The network bonding testing suite provides comprehensive analysis of bonding effectiveness for FFXI servers. Use the detailed logging and explanations to understand how connection bonding improves performance and implement optimal configurations for your specific deployment scenarios.

Regular testing helps ensure optimal performance as your server load grows and network infrastructure evolves.