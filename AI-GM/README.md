# FFXI Server AI-GM System Documentation

## Overview

The AI-GM (Artificial Intelligence Game Master) system is an experimental automated moderation and player assistance system for the FFXI server. It provides intelligent monitoring, automated problem resolution, and escalation capabilities while working alongside human game masters.

## Key Features

### 🤖 Automated Moderation
- **Behavior Analysis**: Continuous monitoring of player activities and behavior patterns
- **Problem Detection**: Automatic identification of stuck players, suspicious activities, and rule violations
- **Disciplinary Actions**: Automated warnings, temporary jailing, and escalation procedures
- **Smart Resolution**: Context-aware decision making for appropriate responses

### 💬 Player Communication
- **Direct Messaging**: AI-GM can communicate directly with players through in-game messages
- **Warning System**: Automated warning delivery with escalation tracking
- **Status Updates**: Real-time feedback to players about moderation actions
- **Help Assistance**: Automated help for common player issues (stuck, death, etc.)

### 🚨 Escalation Management
- **GM Notification**: Automatic alerts to human GMs for complex situations
- **Severity Assessment**: Intelligent classification of incident severity levels
- **Level-Based Escalation**: Automatic escalation to appropriate GM levels (2nd/3rd tier)
- **Admin Alerts**: Critical incident notifications for server administrators

### 🔒 Enhanced Jail System
- **Smart Jailing**: Automated player jailing with duration management
- **Multiple Cells**: Support for 32 jail cells across two floors in Mordion Gaol
- **Auto-Release**: Scheduled release system for temporary punishments
- **Audit Logging**: Complete tracking of all jail actions and reasons

## System Architecture

### Core Components

#### 1. AI-GM Service (`ai_gm_service.py`)
The main Python service that handles:
- Database monitoring and analysis
- Incident detection and classification
- Automated response execution
- Escalation management
- Scheduled task processing

#### 2. Lua Communication Interface (`scripts/globals/ai_gm.lua`)
Provides in-game functionality for:
- Player messaging and warnings
- Jail management integration
- GM notification system
- Behavior analysis functions

#### 3. Enhanced Jail Utilities (`src/map/utils/jailutils.cpp/h`)
Extended C++ utilities offering:
- Advanced jail management functions
- Duration-based sentencing
- Automated release scheduling
- GM notification integration

#### 4. Admin Command Interface (`scripts/commands/aigm.lua`)
Administrative control system featuring:
- Manual AI-GM action execution
- System configuration management
- Status monitoring and reporting
- Override capabilities for human GMs

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