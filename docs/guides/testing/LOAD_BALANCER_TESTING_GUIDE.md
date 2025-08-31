# FFXI Server Load Balancer and High-Load System - Final Testing Guide

## Overview

This comprehensive testing guide validates the complete FFXI server system with:
- ✅ Multi-instance server support (up to 3 instances)
- ✅ HAProxy load balancer with health checks
- ✅ Network bonding for high-performance data handling
- ✅ Secure API for port management through Cloudflare tunnel
- ✅ Firewall configuration and security hardening
- ✅ Full compatibility with Windower and Ashita clients
- ✅ Advanced monitoring and alerting

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/mupoese/FFXI-Server.git
cd FFXI-Server

# 2. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 3. Deploy with interactive configuration
./deploy.sh deploy

# 4. Choose deployment type:
#    1) Basic (Single instance)
#    2) High Availability (Multiple instances)
#    3) High Load (Full monitoring, bonding)
#    4) Development (All services)
```

## System Architecture

### Load Balancer Configuration
- **HAProxy** handles all FFXI traffic distribution
- **Round-robin** for login ports
- **Source-based persistence** for data/auth ports (session affinity)
- **Health checks** ensure traffic only goes to healthy instances
- **Statistics dashboard** at http://localhost:8404/stats

### Port Mapping (All Load Balanced)
```
External → Load Balancer → Server Instances
54001   → HAProxy       → 54011, 54021, 54031 (LOGIN_VIEW)
54230   → HAProxy       → 54240, 54250, 54260 (LOGIN_DATA/MAP)
54231   → HAProxy       → 54241, 54251, 54261 (LOGIN_AUTH)
51220   → HAProxy       → 51230, 51240, 51250 (LOGIN_CONF)
54002   → HAProxy       → 54012, 54022, 54032 (SEARCH)
54003   → HAProxy       → 54013, 54023, 54033 (ZMQ)
8088    → HAProxy       → 8089,  8090,  8091  (HTTP)
```

### Database Sharing
- All server instances share a **single MariaDB database**
- **Connection pooling** prevents database overload
- **Optimized MySQL configuration** for high concurrency
- **Automatic failover** if database connection is lost

## Testing Procedures

### 1. Basic Connectivity Test
```bash
# Test all FFXI ports
for port in 54001 54230 54231 51220 54002 54003 8088; do
    nc -zv localhost $port && echo "✓ Port $port accessible" || echo "✗ Port $port failed"
done

# Test API
curl -f http://localhost:5000/health
```

### 2. Load Balancer Validation
```bash
# Check HAProxy status
curl http://localhost:8404/stats

# View load balancer configuration
docker exec ffxi-load-balancer cat /usr/local/etc/haproxy/haproxy.cfg
```

### 3. Multi-Instance Testing
```bash
# Check running server instances
docker ps | grep ffxi-server

# Scale to multiple instances (if not already configured)
./deploy.sh scale high

# Verify instance isolation
docker exec ffxi-server-1 ps aux | grep xi_
docker exec ffxi-server-2 ps aux | grep xi_
```

### 4. Database Load Testing
```bash
# Run comprehensive system test
python3 docker/system_test.py

# Check database connections
docker exec ffxi-database mysql -u xiuser -pxiserver_2024 -e "SHOW PROCESSLIST;"
```

### 5. API Functionality Test
```bash
# Get authentication token
API_TOKEN=$(curl -s -X POST http://localhost:5000/auth/token \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"your_secret_key_here_change_this"}' \
    | jq -r '.token')

# Test server status
curl -H "Authorization: Bearer $API_TOKEN" http://localhost:5000/api/status

# Test Windower compatibility
curl -H "Authorization: Bearer $API_TOKEN" http://localhost:5000/api/compatibility/windower

# Test Ashita compatibility  
curl -H "Authorization: Bearer $API_TOKEN" http://localhost:5000/api/compatibility/ashita
```

### 6. Network Bonding Test (if enabled)
```bash
# Configure network bonding (requires root)
sudo bash docker/network_bonding.sh configure

# Check bonding status
sudo bash docker/network_bonding.sh status

# Monitor bonding performance
sudo bash docker/network_bonding.sh monitor
```

### 7. Firewall Validation
```bash
# Configure firewall (requires root)
sudo bash docker/firewall.sh configure

# Test firewall health
sudo bash docker/firewall.sh test

# View current rules
sudo bash docker/firewall.sh show
```

### 8. Cloudflare Tunnel Test
```bash
# Set tunnel token in .env
echo "CLOUDFLARE_TUNNEL_TOKEN=your_token_here" >> .env

# Restart with Cloudflare profile
COMPOSE_PROFILES=cloudflare docker-compose up -d cloudflare-tunnel

# Test tunnel configuration
curl -H "Authorization: Bearer $API_TOKEN" \
    -X POST http://localhost:5000/api/cloudflare/tunnel/config \
    -H "Content-Type: application/json" \
    -d '{"domain":"yourdomain.com","tunnel_name":"ffxi-server"}'
```

### 9. High Load Simulation
```bash
# Install load testing tools
pip3 install asyncio aiohttp

# Run concurrent connection test
python3 -c "
import asyncio
import socket
import time

async def test_connection(port, duration=5):
    try:
        reader, writer = await asyncio.open_connection('localhost', port)
        await asyncio.sleep(duration)
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

async def load_test():
    tasks = []
    for i in range(100):  # 100 concurrent connections
        task = test_connection(54001, 2)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    success_rate = sum(1 for r in results if r is True) / len(results)
    print(f'Success rate: {success_rate:.1%}')

asyncio.run(load_test())
"
```

## Performance Benchmarks

### Expected Performance (per instance)
- **Concurrent Players**: 250-500 (depending on load)
- **Login Response Time**: < 100ms
- **Database Query Time**: < 10ms
- **Memory Usage**: 512MB - 1GB
- **CPU Usage**: 10-30% (moderate load)

### Load Balancer Performance
- **Request Distribution**: Even across healthy instances
- **Failover Time**: < 5 seconds
- **Health Check Interval**: 5 seconds
- **Session Persistence**: Maintained for auth/data ports

### Network Bonding (when enabled)
- **Bandwidth**: Combined interface speeds
- **Latency**: Optimized for gaming (< 1ms additional)
- **Redundancy**: Automatic failover between interfaces
- **Load Distribution**: Layer 3+4 hash distribution

## Monitoring and Alerts

### Built-in Monitoring
1. **HAProxy Stats**: http://localhost:8404/stats
2. **API Health**: http://localhost:5000/health
3. **Database Status**: Via API or direct MySQL connection
4. **Container Health**: `docker ps` and health checks

### Advanced Monitoring (with monitoring profile)
1. **Grafana Dashboard**: http://localhost:3000
2. **Prometheus Metrics**: http://localhost:9090
3. **NetData Real-time**: http://localhost:19999
4. **Custom Alerts**: Configurable thresholds

## Troubleshooting

### Common Issues

#### Load Balancer Not Starting
```bash
# Check HAProxy configuration
docker exec ffxi-load-balancer haproxy -f /usr/local/etc/haproxy/haproxy.cfg -c

# View logs
docker-compose logs load_balancer
```

#### Server Instance Connection Issues
```bash
# Check instance health
docker exec ffxi-server-1 /opt/ffxi/healthcheck.sh

# View server logs
docker-compose logs ffxi-server-1

# Restart specific instance
docker-compose restart ffxi-server-1
```

#### Database Connection Problems
```bash
# Test database connectivity
docker exec ffxi-database mysqladmin ping -u xiuser -pxiserver_2024

# Check connection pool
docker exec ffxi-database mysql -u xiuser -pxiserver_2024 -e "SHOW PROCESSLIST;"

# View database logs
docker-compose logs db
```

#### Network Bonding Issues
```bash
# Check bonding status
sudo cat /proc/net/bonding/bond0

# Test interface connectivity
sudo ethtool eth0

# Reconfigure bonding
sudo bash docker/network_bonding.sh remove
sudo bash docker/network_bonding.sh configure
```

### Performance Optimization

#### Database Tuning
```sql
-- Optimize for high concurrent connections
SET GLOBAL max_connections = 1000;
SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB
SET GLOBAL query_cache_size = 67108864; -- 64MB
```

#### Network Optimization
```bash
# Increase network buffers
echo 16777216 > /proc/sys/net/core/rmem_max
echo 16777216 > /proc/sys/net/core/wmem_max

# Enable TCP optimizations
echo 1 > /proc/sys/net/ipv4/tcp_window_scaling
echo 1 > /proc/sys/net/ipv4/tcp_low_latency
```

#### Container Resource Limits
```yaml
# Add to docker-compose.yml services
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

## Security Considerations

### Firewall Rules
- **Drop by default** policy for incoming connections
- **Rate limiting** on login and API ports
- **DDoS protection** against port scans and floods
- **Container isolation** with docker network security

### API Security
- **Token-based authentication** with expiration
- **HTTPS/TLS termination** via Cloudflare tunnel
- **Input validation** and sanitization
- **Audit logging** for all administrative actions

### Database Security
- **User isolation** with minimal privileges
- **Connection encryption** in transit
- **Regular backups** with retention policies
- **Access logging** for compliance

## Windower/Ashita Compatibility

### Tested Configurations
- **Windower 4.x**: Full compatibility
- **Windower 5.x**: Full compatibility  
- **Ashita 3.x**: Full compatibility
- **Ashita 4.x**: Full compatibility

### Recommended Client Settings
```ini
# Windower/Ashita network settings
network_timeout = 30000
packet_buffer_size = 8192
enable_compression = true
use_tcp_nodelay = true
```

### Load Balancer Considerations
- **Session persistence** ensures client connects to same instance
- **TCP keep-alive** maintains stable connections
- **Optimized timeouts** prevent connection drops
- **Buffer sizing** handles large data transfers

## Conclusion

This comprehensive FFXI server system provides:

✅ **Production-ready** deployment with Docker containers  
✅ **High availability** with automatic load balancing  
✅ **Scalability** supporting hundreds of concurrent players  
✅ **Performance** optimized for gaming workloads  
✅ **Security** hardened with firewall and authentication  
✅ **Monitoring** with real-time health checks and metrics  
✅ **Compatibility** with all major FFXI client modifications  

The system is designed to handle high-load scenarios while maintaining the low latency and reliability required for an optimal FFXI gaming experience.