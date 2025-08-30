#!/bin/bash
set -e

# FFXI Server Docker Entrypoint Script
echo "Starting FFXI Server..."

# Set environment variables with defaults
export FFXI_SQL_HOST="${FFXI_SQL_HOST:-db}"
export FFXI_SQL_PORT="${FFXI_SQL_PORT:-3306}"
export FFXI_SQL_LOGIN="${FFXI_SQL_LOGIN:-root}"
export FFXI_SQL_PASSWORD="${FFXI_SQL_PASSWORD:-xiserver}"
export FFXI_SQL_DATABASE="${FFXI_SQL_DATABASE:-xidb}"

export FFXI_LOGIN_DATA_IP="${FFXI_LOGIN_DATA_IP:-0.0.0.0}"
export FFXI_LOGIN_VIEW_IP="${FFXI_LOGIN_VIEW_IP:-0.0.0.0}"
export FFXI_LOGIN_AUTH_IP="${FFXI_LOGIN_AUTH_IP:-0.0.0.0}"
export FFXI_LOGIN_CONF_IP="${FFXI_LOGIN_CONF_IP:-0.0.0.0}"

export FFXI_ZMQ_IP="${FFXI_ZMQ_IP:-127.0.0.1}"
export FFXI_HTTP_HOST="${FFXI_HTTP_HOST:-0.0.0.0}"

# Cloudflare configuration
export CLOUDFLARE_TUNNEL_TOKEN="${CLOUDFLARE_TUNNEL_TOKEN:-}"
export CLOUDFLARE_TUNNEL_NAME="${CLOUDFLARE_TUNNEL_NAME:-ffxi-server}"

# Wait for database to be ready
echo "Waiting for database connection..."
while ! mysqladmin ping -h"$FFXI_SQL_HOST" -P"$FFXI_SQL_PORT" -u"$FFXI_SQL_LOGIN" -p"$FFXI_SQL_PASSWORD" --silent; do
    echo "Waiting for database..."
    sleep 2
done
echo "Database is ready!"

# Check if database exists, create if not
echo "Checking database setup..."
mysql -h"$FFXI_SQL_HOST" -P"$FFXI_SQL_PORT" -u"$FFXI_SQL_LOGIN" -p"$FFXI_SQL_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $FFXI_SQL_DATABASE;" 2>/dev/null || true

# Initialize database if empty
TABLES_COUNT=$(mysql -h"$FFXI_SQL_HOST" -P"$FFXI_SQL_PORT" -u"$FFXI_SQL_LOGIN" -p"$FFXI_SQL_PASSWORD" -e "USE $FFXI_SQL_DATABASE; SHOW TABLES;" 2>/dev/null | wc -l)
if [ "$TABLES_COUNT" -le 1 ]; then
    echo "Initializing database..."
    # Import database schema (assuming SQL files exist)
    if [ -d "/opt/ffxi/sql" ]; then
        for sql_file in /opt/ffxi/sql/*.sql; do
            if [ -f "$sql_file" ]; then
                echo "Importing $sql_file..."
                mysql -h"$FFXI_SQL_HOST" -P"$FFXI_SQL_PORT" -u"$FFXI_SQL_LOGIN" -p"$FFXI_SQL_PASSWORD" "$FFXI_SQL_DATABASE" < "$sql_file" || true
            fi
        done
    fi
fi

# Update network configuration
echo "Configuring network settings..."
cat > /opt/ffxi/settings/network.lua << EOF
xi = xi or {}
xi.settings = xi.settings or {}

xi.settings.network =
{
    SQL_HOST     = "$FFXI_SQL_HOST",
    SQL_PORT     = $FFXI_SQL_PORT,
    SQL_LOGIN    = "$FFXI_SQL_LOGIN",
    SQL_PASSWORD = "$FFXI_SQL_PASSWORD",
    SQL_DATABASE = "$FFXI_SQL_DATABASE",

    LOGIN_DATA_IP   = "$FFXI_LOGIN_DATA_IP",
    LOGIN_DATA_PORT = 54230,
    LOGIN_VIEW_IP   = "$FFXI_LOGIN_VIEW_IP",
    LOGIN_VIEW_PORT = 54001,
    LOGIN_AUTH_IP   = "$FFXI_LOGIN_AUTH_IP",
    LOGIN_AUTH_PORT = 54231,
    LOGIN_CONF_IP   = "$FFXI_LOGIN_CONF_IP",
    LOGIN_CONF_PORT = 51220,

    MAP_PORT = 54230,
    SEARCH_PORT = 54002,

    SQL_QUERY_RETRY_COUNT = 3,
    SQL_USE_CONNECTION_POOL = true,
    SQL_POOL_MIN_CONNECTIONS = 5,
    SQL_POOL_MAX_CONNECTIONS = 20,
    SQL_POOL_CONNECTION_TIMEOUT_MS = 30000,
    SQL_POOL_IDLE_TIMEOUT_MS = 300000,

    BONDING_ENABLED = false,
    BONDING_MODE = "balance-xor",
    BONDING_HASH_POLICY = "layer3+4",
    BONDING_MII_MON_INTERVAL = 100,
    BONDING_FAILOVER_TIMEOUT = 5000,
    BONDING_INTERFACES = "",
    BONDING_ENABLE_MPTCP = false,
    BONDING_UDP_MULTI_HOMING = false,
    BONDING_ENABLE_RSS = true,
    BONDING_ENABLE_RPS = true,
    BONDING_INTERRUPT_COALESCING = true,

    ENABLE_HTTP = true,
    HTTP_HOST   = "$FFXI_HTTP_HOST",
    HTTP_PORT   = 8088,

    ZMQ_IP   = "$FFXI_ZMQ_IP",
    ZMQ_PORT = 54003,

    UDP_DEBUG = false,
    TCP_DEBUG = false,
    TCP_STALL_TIME = 60,
    TCP_ENABLE_IP_RULES = false,
    TCP_ORDER = "deny,allow",
    TCP_ALLOW = "all",
    TCP_DENY = "",
    TCP_CONNECT_INTERVAL = 3000,
    TCP_CONNECT_COUNT = 10,
    TCP_CONNECT_LOCKOUT = 600000
}
EOF

# Configure Cloudflare tunnel if token provided
if [ -n "$CLOUDFLARE_TUNNEL_TOKEN" ]; then
    echo "Configuring Cloudflare tunnel..."
    cat > /opt/ffxi/cloudflare-tunnel.yml << EOF
tunnel: $CLOUDFLARE_TUNNEL_NAME
credentials-file: /opt/ffxi/.cloudflared/tunnel.json

ingress:
  # FFXI Login View Port (TCP)
  - hostname: login.${CLOUDFLARE_DOMAIN:-example.com}
    service: tcp://localhost:54001
  # FFXI Login Data Port (UDP) - Note: Cloudflare doesn't support UDP directly
  - hostname: data.${CLOUDFLARE_DOMAIN:-example.com}  
    service: tcp://localhost:54230
  # FFXI Login Auth Port (TCP)
  - hostname: auth.${CLOUDFLARE_DOMAIN:-example.com}
    service: tcp://localhost:54231
  # FFXI Login Config Port (TCP)
  - hostname: config.${CLOUDFLARE_DOMAIN:-example.com}
    service: tcp://localhost:51220
  # FFXI Search Port (TCP)
  - hostname: search.${CLOUDFLARE_DOMAIN:-example.com}
    service: tcp://localhost:54002
  # HTTP Management Interface
  - hostname: admin.${CLOUDFLARE_DOMAIN:-example.com}
    service: http://localhost:8088
  # Catch-all rule
  - service: http_status:404
EOF

    # Create cloudflared directory and authenticate
    mkdir -p /opt/ffxi/.cloudflared
    echo "$CLOUDFLARE_TUNNEL_TOKEN" > /opt/ffxi/.cloudflared/tunnel.json
    
    # Start cloudflared in background
    echo "Starting Cloudflare tunnel..."
    cloudflared tunnel --config /opt/ffxi/cloudflare-tunnel.yml run &
fi

echo "FFXI Server configuration complete!"
echo "Database: $FFXI_SQL_HOST:$FFXI_SQL_PORT/$FFXI_SQL_DATABASE"
echo "Login Ports: 54001 (VIEW), 54230 (DATA), 54231 (AUTH), 51220 (CONFIG)"
echo "Game Ports: 54230 (MAP), 54002 (SEARCH), 54003 (ZMQ)"
echo "HTTP Port: 8088"

# Execute the main command
exec "$@"