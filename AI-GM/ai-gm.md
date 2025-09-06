# FFXI Server AI-GM Enhanced System Documentation

## Overview

The AI-GM (Artificial Intelligence Game Master) system is an experimental automated moderation and player assistance system for the FFXI server. **NEWLY ENHANCED** with advanced machine learning capabilities, cross-platform hardware acceleration, and comprehensive battle testing tools. It provides intelligent monitoring, automated problem resolution, and escalation capabilities while working alongside human game masters.

## Key Features

### 🧠 **NEW: Machine Learning Engine**
- **Cross-Platform GPU/NPU Support**: NVIDIA CUDA, AMD ROCm, Intel OpenVINO, Apple Metal
- **Real-Time Behavior Analysis**: Advanced anomaly detection and behavior classification
- **Continuous Learning**: AI learns from server interactions and GM decisions
- **Hardware Auto-Detection**: Automatically selects best available acceleration
- **Predictive Moderation**: Proactive identification of potential issues

### ⚔️ **NEW: Battle Test System**
- **GM Battle Testing**: Spawn mobs and test combat mechanics in controlled environments
- **Player Assistance**: Automated help system with GM demonstration capabilities  
- **Session Management**: Track battle test sessions with comprehensive analytics
- **Demo Mode**: GMs can show combat mechanics to players in need
- **Multi-Config Support**: Quick, standard, advanced, and endgame test configurations

### 🤖 Enhanced Automated Moderation
- **Behavior Analysis**: ML-powered continuous monitoring of player activities and behavior patterns
- **Problem Detection**: Advanced automatic identification of stuck players, suspicious activities, and rule violations
- **Disciplinary Actions**: Intelligent automated warnings, temporary jailing, and escalation procedures
- **Smart Resolution**: Context-aware decision making with ML-enhanced accuracy

### 💬 Advanced Player Communication
- **Direct Messaging**: AI-GM can communicate directly with players through in-game messages
- **Intelligent Warning System**: ML-enhanced warning delivery with behavioral pattern analysis
- **Status Updates**: Real-time feedback to players about moderation actions
- **Automated Assistance**: Smart help for common player issues with battle demonstrations

### 🚨 Smart Escalation Management
- **ML-Enhanced GM Notification**: Automatic alerts to human GMs for complex situations with risk assessment
- **Intelligent Severity Assessment**: ML-powered classification of incident severity levels
- **Adaptive Escalation**: Dynamic escalation to appropriate GM levels based on behavioral patterns
- **Predictive Admin Alerts**: Proactive critical incident notifications for server administrators

### 🔒 Enhanced Jail System
- **AI-Powered Jailing**: ML-informed automated player jailing with duration management
- **Multiple Cells**: Support for 32 jail cells across two floors in Mordion Gaol
- **Smart Auto-Release**: Intelligent scheduled release system for temporary punishments
- **Comprehensive Audit Logging**: ML-enhanced tracking of all jail actions and behavioral patterns

## System Architecture

### Core Components

#### 1. **NEW: ML Engine (`ml_engine.py`)**
Advanced machine learning system featuring:
- Cross-platform hardware acceleration (NVIDIA, AMD, Intel, Apple)
- Real-time player behavior analysis and anomaly detection
- Continuous learning from GM interactions and server data
- Predictive behavior classification and risk assessment
- Intelligent model selection and optimization

#### 2. **NEW: Battle Test System (`battle_test_system.py`)**
Comprehensive GM battle testing framework providing:
- Automated test session management and analytics
- Player assistance request handling with demo capabilities
- Mob spawning and combat mechanics testing
- Multi-configuration support for different test scenarios
- Real-time battle analytics and performance tracking

#### 3. Enhanced AI-GM Service (`ai_gm_service.py`)
The main Python service now includes:
- ML-enhanced database monitoring and analysis
- Advanced incident detection and classification
- Hardware-accelerated automated response execution
- Intelligent escalation management with risk assessment
- Battle test integration and session coordination

#### 4. Advanced Lua Communication Interface (`scripts/globals/ai_gm.lua`)
Enhanced in-game functionality featuring:
- ML-powered player behavior analysis functions
- Battle test session creation and management
- Player assistance request handling with combat demos
- Hardware status monitoring and ML system integration
- Enhanced GM notification system with risk assessment

#### 5. Enhanced Jail Utilities (`src/map/utils/jailutils.cpp/h`)
Extended C++ utilities offering:
- ML-informed jail management functions
- Advanced duration-based sentencing with behavioral factors
- Intelligent automated release scheduling
- Enhanced GM notification integration with risk data

#### 6. **NEW: Enhanced Admin Command Interface (`scripts/commands/aigm.lua`)**
Expanded administrative control system featuring:
- Battle test session management commands
- ML system monitoring and configuration
- Hardware acceleration status and optimization
- Player assistance request handling
- Advanced system diagnostics and analytics

## **NEW: Hardware Requirements and Cross-Platform Support**

### Supported Platforms
- **Windows**: NVIDIA CUDA, Intel OpenVINO, CPU fallback
- **macOS**: Apple Metal (M1/M2/M3), Intel OpenVINO, CPU fallback  
- **Linux**: NVIDIA CUDA, AMD ROCm, Intel OpenVINO, CPU fallback

### Recommended Hardware
- **NVIDIA GPU**: RTX 20/30/40 series, GTX 1060+ for CUDA acceleration
- **AMD GPU**: RX 5000/6000/7000 series for ROCm acceleration (Linux)
- **Intel Hardware**: 4th gen Core+ with integrated NPU, Arc GPUs
- **Apple Silicon**: M1/M2/M3 chips with Metal acceleration
- **RAM**: 8GB minimum, 16GB+ recommended for ML workloads
- **Storage**: SSD recommended for model loading performance

### Hardware Auto-Detection
The system automatically detects and configures the best available hardware:
- **CUDA Detection**: Automatic NVIDIA GPU detection and optimization
- **ROCm Detection**: AMD GPU support on compatible Linux systems  
- **Metal Detection**: Native Apple Silicon acceleration on macOS
- **OpenVINO Detection**: Intel CPU, GPU, and NPU optimization
- **Graceful Fallback**: CPU-only operation when hardware acceleration unavailable

## Installation and Configuration

### Prerequisites
- FFXI Server with GM system enabled
- Python 3.12+ with required dependencies
- MariaDB/MySQL database access
- Web admin API (optional but recommended)

### Installation Steps

1. **Install Python Dependencies**
   ```bash
   cd AI-GM
   pip install -r requirements.txt
   ```

2. **Configure Database Access**
   ```bash
   export FFXI_SQL_HOST="localhost"
   export FFXI_SQL_PORT="3306"
   export FFXI_SQL_LOGIN="xiuser"
   export FFXI_SQL_PASSWORD="xiserver_2024"
   export FFXI_SQL_DATABASE="xidb"
   ```

3. **Initialize AI-GM Service**
   ```bash
   cd AI-GM
   python ai_gm_service.py
   ```

4. **Build Server with Enhanced Jail Utilities**
   ```bash
   mkdir -p build && cd build
   cmake ..
   make -j4
   ```

### Configuration Options

The AI-GM system can be configured through environment variables or the service configuration:

```python
# Core Settings
AIGM_AUTO_MODERATION = True          # Enable automated actions
AIGM_JAIL_DURATION = 30              # Default jail time (minutes)
AIGM_ESCALATION_THRESHOLD = 3        # Warnings before escalation
AIGM_MONITORING_INTERVAL = 60        # Check interval (seconds)

# Communication Settings  
AIGM_GM_NAME = "AI-GM"               # Display name for AI-GM
AIGM_GM_LEVEL = 2                    # AI-GM effective level
AIGM_ANNOUNCE_ACTIONS = True         # Public action announcements
```

## Usage Guide

### For Server Administrators

#### Managing AI-GM System
```lua
-- Enable/disable AI-GM
!aigm enable
!aigm disable

-- Check system status
!aigm status

-- Configure AI-GM behavior
!aigm config name "Server-AI"
!aigm config level 2
!aigm config announce true
```

#### Manual Actions
```lua
-- Jail a player
!aigm jail PlayerName "Disruptive behavior"

-- Send warning
!aigm warn PlayerName "Please follow server rules"

-- Escalate to human GM
!aigm escalate PlayerName 3

-- Make announcements
!aigm announce "Server maintenance in 30 minutes"
```

#### Monitoring and Analysis
```lua
-- Check specific player
!aigm check PlayerName

-- Check all online players
!aigm check

-- View recent AI-GM activity
!aigm status
```

### For Game Masters

#### Receiving AI-GM Notifications
- **Level 1+ GMs**: Receive basic AI-GM action notifications
- **Level 2+ GMs**: Receive escalation alerts and warnings
- **Level 3+ GMs**: Receive critical incident notifications
- **Level 5 Admins**: Receive all AI-GM communications and admin alerts

#### Overriding AI-GM Actions
Human GMs can always override AI-GM decisions:
```lua
-- Pardon AI-GM jailed player
!pardon PlayerName

-- Override AI-GM warnings
!aigm pardon PlayerName

-- Disable AI-GM for specific situations
!aigm disable
```

### For Players

#### Receiving AI-GM Communications
Players receive AI-GM messages through the standard chat system:
- **Info Messages**: System notifications and assistance
- **Warnings**: Behavior warnings with clear explanations
- **Action Notifications**: Information about disciplinary actions

#### Getting Help from AI-GM
The AI-GM automatically assists with common issues:
- **Stuck Players**: Automatic detection and teleportation
- **Dead Players**: Auto-resurrection after extended death
- **Invalid Positions**: Automatic correction and safe teleportation

## Technical Implementation

### Enhanced Jail System API

```cpp
// Core jail management functions
namespace jailutils {
    // Enhanced functions for AI-GM integration
    void JailPlayer(CCharEntity* PChar, uint8 cellId, const std::string& reason);
    void PardonPlayer(CCharEntity* PChar);
    bool IsPlayerJailed(uint32 playerId);
    void SetJailDuration(CCharEntity* PChar, uint32 minutes);
    uint32 GetJailTimeRemaining(const CCharEntity* PChar);
    void NotifyGMsOfJailing(const std::string& playerName, const std::string& reason);
}
```

### Incident Response Framework

```python
# Python service incident handling
class PlayerIncident:
    player_id: int
    player_name: str
    incident_type: str
    severity: AIGMSeverity
    description: str
    timestamp: datetime
    auto_resolved: bool = False
    action_taken: Optional[AIGMAction] = None

# Automated response system
def determine_action(self, incident: PlayerIncident) -> Optional[AIGMAction]:
    warning_count = self.player_warnings.get(incident.player_id, 0)
    
    if incident.severity == AIGMSeverity.WARNING:
        if warning_count >= self.config.escalation_threshold:
            return AIGMAction.TEMP_JAIL
        else:
            return AIGMAction.WARN
    # ... additional logic
```

## Security and Safety

### Authorization and Access Control
- **GM Level Requirements**: Commands restricted to appropriate GM levels
- **Audit Logging**: Complete tracking of all AI-GM actions
- **Override Capabilities**: Human GMs can always override AI-GM decisions
- **Manual Disable**: Emergency shutdown capabilities

### Fail-Safe Mechanisms
- **Human Override**: All AI-GM actions can be manually reversed
- **Escalation Limits**: Automatic escalation to prevent AI-only decisions
- **Emergency Disable**: Quick shutdown for problematic behavior
- **Conservative Actions**: Prefer warnings over punishments when uncertain

## Getting Started

1. **Basic Setup**: Install dependencies and configure database access
2. **Test Mode**: Start with warnings-only to observe AI-GM behavior
3. **Gradual Deployment**: Enable automated actions incrementally
4. **Monitor and Adjust**: Fine-tune thresholds based on server needs
5. **Train Staff**: Ensure GMs understand AI-GM capabilities and overrides

## Support and Maintenance

- **Logs**: Monitor `logs/ai_gm.log` for service activity
- **Database**: Regular maintenance of `ai_gm_incidents` table
- **Performance**: Watch CPU and memory usage during peak hours
- **Updates**: Keep Python dependencies current and secure

---

**Note**: This AI-GM system is experimental and designed to assist human game masters, not replace them. Always maintain human oversight and intervention capabilities for complex moderation decisions.