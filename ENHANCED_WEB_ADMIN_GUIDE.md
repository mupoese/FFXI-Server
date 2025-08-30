# LandSandBoat Enhanced Web Administration Panel

## Overview

The enhanced web administration panel provides comprehensive user management, character viewing, and administrative capabilities for the LandSandBoat FFXI server emulator.

## New Features Added

### 🔐 User Registration & Authentication System
- **Email/password registration** with secure password hashing
- **Account approval workflow** - new users require moderator/admin approval
- **Character limit enforcement** - maximum 2 characters per user (configurable)
- **Session management** with role-based access control

### 👥 User Management Interface
- **Registration requests dashboard** - approve/reject pending users
- **User account overview** - view all registered users, their status, and character counts
- **Search and filtering** capabilities for user management
- **Status management** - active, pending, banned account states

### 🎮 Player Portal
- **Character viewing** - registered users can view their character information
- **Real-time game data** - Vana'diel time, elemental day, moon phase
- **Character statistics** - level, job, zone, playtime
- **Inventory display** - visual inventory grid showing items
- **Auction house activity** - real-time auction house data

### 📊 Enhanced Game Data Display
- **Real-time Vana'diel calendar** - current date, elemental day, moon phase
- **Auction house metrics** - active listings, daily sales, total gil
- **Zone population tracking** - see where players are active
- **Server uptime and performance metrics**

### 🛡️ Moderator/GM Management
- **Role-based permissions** - admin, moderator, and user levels
- **GM promotion system** - admins can promote moderators to GM status
- **Privilege management** - control access to different admin functions
- **Configuration management** - adjust character limits and approval requirements

## Technical Implementation

### Database Integration
- **Secure authentication** using existing `accounts` table
- **Character data access** from `chars` and related tables
- **Inventory integration** with `char_inventory` table
- **Auction house data** from `auction_house` table
- **GM level management** through character `gmlevel` field

### Security Features
- **Password hashing** using SHA-256 for secure authentication
- **Session management** with Flask sessions
- **Role-based access control** for different admin functions
- **Input validation** and SQL injection prevention
- **CSRF protection** for form submissions

### Real-time Features
- **Auto-refreshing dashboards** - data updates every 10-30 seconds
- **Live system monitoring** - CPU, memory, disk usage
- **Real-time game data** - Vana'diel time calculation
- **Dynamic user interfaces** - responsive tab system

## Configuration

### Database Configuration
```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "database": "xidb",
    "user": "your_username",
    "password": "your_password"
  }
}
```

### User Management Settings
```json
{
  "user_management": {
    "max_characters_per_user": 2,
    "require_approval": true,
    "admin_email": "admin@landsandboat.local"
  }
}
```

## Installation & Usage

### Prerequisites
```bash
pip install flask mysql-connector-python psutil
```

### Starting the Web Panel
```bash
# Start on default port 8080
python3 tools/web_admin.py

# Custom configuration
python3 tools/web_admin.py --host 0.0.0.0 --port 8080 --config config.json

# Debug mode
python3 tools/web_admin.py --debug
```

### Access URLs
- **User Login/Registration**: `http://localhost:8080/`
- **Admin Panel**: `http://localhost:8080/admin` (requires admin/moderator privileges)
- **Player Portal**: `http://localhost:8080/portal` (for registered users)

## User Workflow

### New User Registration
1. User visits registration page at `/register`
2. Fills out email, username, password
3. Account created with "pending" status if approval required
4. Admin/moderator reviews and approves/rejects registration
5. User can login and access player portal

### Character Viewing
1. User logs in and accesses player portal
2. Can view all their characters with stats and information
3. Click on character to see detailed inventory
4. Real-time game information displayed

### Administrative Functions
1. Admin/moderator logs in to admin panel
2. Review pending user registrations
3. Manage existing users and characters
4. Monitor real-time game data and server metrics
5. Configure system settings

## API Endpoints

### Authentication
- `POST /` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Admin API
- `GET /api/users` - Get user list for management
- `POST /api/users/approve` - Approve user registration
- `POST /api/users/reject` - Reject user registration
- `GET /api/characters` - Get character list
- `GET /api/gamedata` - Get real-time game data

### User API
- `GET /api/user/characters` - Get current user's characters
- `GET /api/user/character/{id}/inventory` - Get character inventory

## Database Schema Integration

### Accounts Table Usage
- `id` - Unique account identifier
- `login` - Username for authentication
- `password` - SHA-256 hashed password
- `current_email` - User email address
- `status` - Account status (0=pending, 1=active, 2=banned)
- `priv` - Privilege level (1=user, 2=moderator, 3=admin)
- `content_ids` - Character limit per account

### Characters Table Integration
- `charid` - Character identifier
- `accid` - Links to accounts table
- `charname` - Character name
- `gmlevel` - GM privilege level
- Character stats, position, and game data

## Security Considerations

### Password Security
- SHA-256 hashing for password storage
- No plaintext passwords stored
- Session-based authentication

### Access Control
- Role-based permissions (user/moderator/admin)
- Session validation for all protected routes
- Database query parameterization to prevent SQL injection

### User Data Protection
- Character data only accessible by account owner
- Admin functions restricted to appropriate privilege levels
- Secure session management with Flask sessions

## Customization Options

### Appearance
- Responsive dark theme design
- Mobile-friendly interface
- Customizable CSS styling

### Functionality
- Configurable character limits
- Adjustable approval requirements
- Customizable refresh intervals
- Flexible alert thresholds

## Integration with Existing LandSandBoat Features

### Database Compatibility
- Uses existing database schema
- Compatible with current account/character system
- Integrates with inventory and auction house systems

### Server Integration
- Works alongside existing server processes
- Provides monitoring for xi_map, xi_login, xi_search
- Real-time integration with game data

This enhanced web administration panel provides a comprehensive solution for managing LandSandBoat server users, characters, and administrative functions through a modern web interface.