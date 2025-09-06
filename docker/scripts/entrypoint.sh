#!/bin/bash
set -e

# FFXI Server Docker Entrypoint Script
echo "Starting FFXI Server..."

# Set environment variables with defaults from new .env structure
export FFXI_SQL_HOST="${FFXI_SQL_HOST:-db}"
export FFXI_SQL_PORT="${FFXI_SQL_PORT:-3306}"
export FFXI_SQL_LOGIN="${FFXI_SQL_USER:-xiuser}"
export FFXI_SQL_PASSWORD="${FFXI_SQL_PASSWORD:-xiserver_2024}"
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
timeout=60
counter=0
while ! mysqladmin ping -h"$FFXI_SQL_HOST" -P"$FFXI_SQL_PORT" -u"$FFXI_SQL_LOGIN" -p"$FFXI_SQL_PASSWORD" --silent 2>/dev/null; do
    echo "Waiting for database... ($counter/$timeout seconds)"
    sleep 2
    counter=$((counter + 2))
    if [ $counter -ge $timeout ]; then
        echo "Database connection timeout after $timeout seconds!"
        exit 1
    fi
done
echo "Database is ready!"

# Check if database exists, create if not
echo "Checking database setup..."
mysql -h"$FFXI_SQL_HOST" -P"$FFXI_SQL_PORT" -u"$FFXI_SQL_LOGIN" -p"$FFXI_SQL_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $FFXI_SQL_DATABASE;" 2>/dev/null || true

# Initialize database if empty
TABLES_COUNT=$(mysql -h"$FFXI_SQL_HOST" -P"$FFXI_SQL_PORT" -u"$FFXI_SQL_LOGIN" -p"$FFXI_SQL_PASSWORD" -e "USE $FFXI_SQL_DATABASE; SHOW TABLES;" 2>/dev/null | wc -l)
if [ "$TABLES_COUNT" -le 1 ]; then
    echo "Initializing database..."
    # Use the Python database tool if available
    if [ -f "/opt/ffxi/tools/dbtool.py" ]; then
        echo "Using dbtool.py for database initialization..."
        cd /opt/ffxi
        python3 tools/dbtool.py setup --host "$FFXI_SQL_HOST" --port "$FFXI_SQL_PORT" --user "$FFXI_SQL_LOGIN" --password "$FFXI_SQL_PASSWORD" --database "$FFXI_SQL_DATABASE" || true
    elif [ -d "/opt/ffxi/sql" ]; then
        # Fallback to manual SQL import
        echo "Importing SQL files manually..."
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
echo "Launcher Web Server Port: 8089"

# Execute the main command based on argument
case "$1" in
    "connect"|"xi_connect")
        echo "Starting xi_connect server..."
        exec /opt/ffxi/bin/xi_connect "${@:2}"
        ;;
    "map"|"xi_map")
        echo "Starting xi_map server..."
        exec /opt/ffxi/bin/xi_map "${@:2}"
        ;;
    "search"|"xi_search")
        echo "Starting xi_search server..."
        exec /opt/ffxi/bin/xi_search "${@:2}"
        ;;
    "world"|"xi_world")
        echo "Starting xi_world server..."
        exec /opt/ffxi/bin/xi_world "${@:2}"
        ;;
    "launcher"|"build-launcher")
        echo "Building launcher with current .env configuration..."
        cd /opt/ffxi
        if [ -f ".env" ]; then
            echo "Using existing .env file for launcher build..."
            python3 tools/enhanced_build_launcher.py
        else
            echo "No .env file found, using .env.example as template..."
            cp .env.example .env
            python3 tools/enhanced_build_launcher.py
        fi
        echo "Launcher build completed. Files available in web/downloads/"
        ;;
    "launcher-server"|"serve-launcher")
        echo "Starting launcher web server..."
        cd /opt/ffxi/web
        python3 -m http.server 8089 --bind 0.0.0.0 &
        echo "Launcher web server started on port 8089"
        echo "Download URL: http://localhost:8089/downloads/"
        wait
        ;;
    "all-with-launcher"|"full")
        echo "Starting all FFXI server components with launcher web server..."
        
        # Build launcher first if .env exists
        if [ -f "/opt/ffxi/.env" ]; then
            echo "Building launcher with current configuration..."
            cd /opt/ffxi
            python3 tools/enhanced_build_launcher.py
        fi
        
        # Start launcher web server
        cd /opt/ffxi/web
        python3 -m http.server 8089 --bind 0.0.0.0 &
        echo "Launcher web server started on port 8089"
        
        # Start all FFXI servers in background except the last one
        /opt/ffxi/bin/xi_connect --log /opt/ffxi/logs/xi_connect.log &
        /opt/ffxi/bin/xi_search --log /opt/ffxi/logs/xi_search.log &
        /opt/ffxi/bin/xi_world --log /opt/ffxi/logs/xi_world.log &
        
        # Start map server in foreground (will keep container running)
        exec /opt/ffxi/bin/xi_map --log /opt/ffxi/logs/xi_map.log
        ;;
    "all"|"")
        echo "Starting all FFXI server components..."
        # Start all servers in background except the last one
        /opt/ffxi/bin/xi_connect --log /opt/ffxi/logs/xi_connect.log &
        /opt/ffxi/bin/xi_search --log /opt/ffxi/logs/xi_search.log &
        /opt/ffxi/bin/xi_world --log /opt/ffxi/logs/xi_world.log &
        
        # Start map server in foreground (will keep container running)
        exec /opt/ffxi/bin/xi_map --log /opt/ffxi/logs/xi_map.log
        ;;
    "test"|"xi_test")
        echo "Running FFXI tests..."
        exec /opt/ffxi/bin/xi_test "${@:2}"
        ;;
    "bash"|"sh")
        echo "Starting interactive shell..."
        exec /bin/bash
        ;;
    "health")
        echo "Performing health check..."
        # Simple health check - verify processes and database connection
        mysqladmin ping -h"$FFXI_SQL_HOST" -P"$FFXI_SQL_PORT" -u"$FFXI_SQL_LOGIN" -p"$FFXI_SQL_PASSWORD" --silent || exit 1
        curl -f http://localhost:8088/health 2>/dev/null || echo "HTTP health check not available"
        echo "Health check passed"
        exit 0
        ;;
    *)
        echo "Usage: $0 {connect|map|search|world|all|launcher|launcher-server|all-with-launcher|test|bash|health}"
        echo "  connect           - Start only xi_connect server"
        echo "  map               - Start only xi_map server"
        echo "  search            - Start only xi_search server"
        echo "  world             - Start only xi_world server"
        echo "  all               - Start all server components (default)"
        echo "  launcher          - Build launcher with current .env configuration"
        echo "  launcher-server   - Start launcher web server on port 8089"
        echo "  all-with-launcher - Start all servers and launcher web server"
        echo "  test              - Run server tests"
        echo "  bash              - Start interactive shell"
        echo "  health            - Perform health check"
        exec "$@"
        ;;
esac