-----------------------------------
-- NETWORK SETTINGS
-----------------------------------
-- All settings are attached to the `xi.settings` object. This is published globally, and be accessed from C++ and any script.
--
-- This file is concerned mainly with networking between the database, client, and server executables.
-----------------------------------

xi = xi or {}
xi.settings = xi.settings or {}

xi.settings.network =
{
    SQL_HOST     = "127.0.0.1",
    SQL_PORT     = 3306,
    SQL_LOGIN    = "root",
    SQL_PASSWORD = "root",
    SQL_DATABASE = "xidb",

    LOGIN_DATA_IP   = "0.0.0.0",
    LOGIN_DATA_PORT = 54230,
    LOGIN_VIEW_IP   = "0.0.0.0",
    LOGIN_VIEW_PORT = 54001,
    LOGIN_AUTH_IP   = "0.0.0.0",
    LOGIN_AUTH_PORT = 54231,
    LOGIN_CONF_IP   = "0.0.0.0",
    LOGIN_CONF_PORT = 51220,

    MAP_PORT = 54230,

    SEARCH_PORT = 54002,

    -- DB queries will attempt each query once, and reconnect and retry up to `SQL_QUERY_RETRY_COUNT` times.
    SQL_QUERY_RETRY_COUNT = 1,

    -- Connection pool settings for improved database performance
    SQL_USE_CONNECTION_POOL = true,
    SQL_POOL_MIN_CONNECTIONS = 10,  -- Increased from 5 for better high-load performance
    SQL_POOL_MAX_CONNECTIONS = 50,  -- Increased from 20 for high-load scenarios
    SQL_POOL_CONNECTION_TIMEOUT_MS = 10000,  -- Reduced from 30000 for faster timeout
    SQL_POOL_IDLE_TIMEOUT_MS = 600000,  -- Increased from 300000 for better reuse

    -- ===========================
    -- Network Bonding Configuration
    -- ===========================
    
    -- Enable network bonding (link aggregation) for improved TCP/UDP performance
    BONDING_ENABLED = false,
    
    -- Bonding modes:
    --   balance-rr     : Round-robin for maximum throughput
    --   active-backup  : Fault tolerance focus
    --   balance-xor    : XOR hash-based distribution
    --   broadcast      : Broadcast on all interfaces
    --   802.3ad        : Dynamic link aggregation (recommended)
    --   balance-tlb    : Adaptive transmit load balancing
    --   balance-alb    : Adaptive load balancing
    BONDING_MODE = "balance-xor",
    
    -- Hash policies for load balancing:
    --   layer2         : Ethernet MAC based
    --   layer3+4       : IP + Port based (better for TCP/UDP)
    --   layer2+3       : MAC + IP based
    --   encap2+3       : Encapsulated layer 2+3
    --   encap3+4       : Encapsulated layer 3+4
    BONDING_HASH_POLICY = "layer3+4",
    
    -- Interface monitoring interval in milliseconds
    BONDING_MII_MON_INTERVAL = 100,
    
    -- Failover timeout in milliseconds
    BONDING_FAILOVER_TIMEOUT = 5000,
    
    -- Bonded network interfaces (format: "interface:ip_address")
    -- Example: "eth0:192.168.1.100,eth1:192.168.1.101"
    BONDING_INTERFACES = "",
    
    -- Enable Multi-Path TCP (MPTCP) support
    BONDING_ENABLE_MPTCP = false,
    
    -- UDP multi-homing configuration
    BONDING_UDP_MULTI_HOMING = false,
    
    -- Performance tuning options
    BONDING_ENABLE_RSS = true,           -- Receive Side Scaling
    BONDING_ENABLE_RPS = true,           -- Receive Packet Steering
    BONDING_INTERRUPT_COALESCING = true, -- Interrupt coalescing for performance

    ENABLE_HTTP = false,
    HTTP_HOST   = "localhost",
    HTTP_PORT   = 8088,

    -- Central message server settings (ensure these are the same on both all map servers and the central (lobby) server
    ZMQ_IP   = "127.0.0.1",
    ZMQ_PORT = 54003,

    -- ===========================
    -- NOTE: The settings that follow will not necessarily need to be modified
    --       in any way for the server to work out of the box.  This should only
    --       be modified by those who understand networking.  Modifying these
    --       values could potentially make it so that you can not log in to your
    --       server.
    -- ===========================

    -- ===========================
    -- UDP Sockets Configuration
    -- ===========================

    -- Display debug reports (When something goes wrong during the report, the report is saved.)
    UDP_DEBUG = false,

    -- ===========================
    -- TCP Sockets Configuration
    -- ===========================

    -- Display debug reports (When something goes wrong during the report, the report is saved.)
    TCP_DEBUG = false,

    -- How long can a socket stall before closing the connection (in seconds)
    TCP_STALL_TIME = 60,

    -- ===========================
    -- IP Rules Settings
    -- ===========================

    -- If IP's are checked when connecting. This also enables DDoS protection.
    TCP_ENABLE_IP_RULES = true,

    -- Order of the checks
    --   deny,allow     : Checks deny rules, then allow rules. Allows if no rules match.
    --   allow,deny     : Checks allow rules, then deny rules. Allows if no rules match.
    --   mutual-failure : Allows only if an allow rule matches and no deny rules match.
    -- (default is deny,allow)
    TCP_ORDER = "deny,allow",
    --TCP_ORDER = "allow,deny",
    --TCP_ORDER = "mutual-failure",

    -- ===========================
    -- IP rules
    -- ===========================
    --   allow : Accepts connections from the ip range (even if flagged as DDoS)
    --   deny  : Rejects connections from the ip range
    -- The rules are processed in order, the first matching rule of each list
    -- (allow and deny) is used

    TCP_ALLOW = "",
    --TCP_ALLOW = "127.0.0.1,192.168.0.0/16",
    --TCP_ALLOW = "127.0.0.1"
    --TCP_ALLOW = "192.168.0.0/16"
    --TCP_ALLOW = "10.0.0.0/255.0.0.0"
    --TCP_ALLOW = "all"

    TCP_DENY = "",
    --TCP_DENY = "10.0.0.0/8,192.168.0.0/16",
    --TCP_DENY = "127.0.0.1",
    --TCP_DENY = "10.0.0.0/255.0.0.0",

    -- ===========================
    -- Connection Limit Settings
    -- ===========================

    -- If connect_count connection request are made within connect_interval
    -- msec, it blocks it

    -- Consecutive attempts interval (msec)
    -- (default is 3000 msecs, 3 seconds)
    TCP_CONNECT_INTERVAL = 3000,

    -- Consecutive attempts trigger
    -- (default is 10 attempts)
    TCP_CONNECT_COUNT = 10,

    -- The time interval after which the connection lockout is lifted. (msec)
    -- After this amount of time, the connection restrictions are lifted.
    -- (default is 600000 msecs, 10 minutes)
    TCP_CONNECT_LOCKOUT = 600000
}

-- EOF
