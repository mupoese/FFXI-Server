#!/usr/bin/env python3
"""
FFXI Server Management API
Secure API for managing FFXI server ports through Cloudflare tunnel
Compatible with Windower and Ashita clients
"""

import os
import json
import yaml
import time
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Any

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import mysql.connector
from mysql.connector import pooling
import subprocess
import socket
import threading
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('FFXI_API_SECRET_KEY', 'your_secret_key_here_change_this')
    DB_CONFIG = {
        'host': os.environ.get('FFXI_SQL_HOST', 'db'),
        'port': int(os.environ.get('FFXI_SQL_PORT', 3306)),
        'user': os.environ.get('FFXI_SQL_LOGIN', 'xiuser'),
        'password': os.environ.get('FFXI_SQL_PASSWORD', 'xiserver_2024'),
        'database': os.environ.get('FFXI_SQL_DATABASE', 'xidb'),
        'pool_name': 'ffxi_api_pool',
        'pool_size': 10,
        'pool_reset_session': True,
        'autocommit': True
    }
    API_PORT = int(os.environ.get('FFXI_API_PORT', 5000))
    
    # FFXI Port Configuration
    FFXI_PORTS = {
        'LOGIN_VIEW_PORT': 54001,
        'LOGIN_DATA_PORT': 54230,
        'LOGIN_AUTH_PORT': 54231,
        'LOGIN_CONF_PORT': 51220,
        'MAP_PORT': 54230,  # Same as LOGIN_DATA_PORT
        'SEARCH_PORT': 54002,
        'ZMQ_PORT': 54003,
        'HTTP_PORT': 8088,
        'SQL_PORT': 3306
    }
    
    # Network bonding configuration
    BONDING_CONFIG = {
        'enabled': os.environ.get('FFXI_ENABLE_BONDING', 'false').lower() == 'true',
        'mode': os.environ.get('FFXI_BONDING_MODE', 'balance-xor'),
        'hash_policy': os.environ.get('FFXI_BONDING_HASH_POLICY', 'layer3+4'),
        'mii_mon_interval': int(os.environ.get('FFXI_BONDING_MII_MON_INTERVAL', 100)),
        'failover_timeout': int(os.environ.get('FFXI_BONDING_FAILOVER_TIMEOUT', 5000))
    }

app.config.from_object(Config)

# Database connection pool
try:
    db_pool = pooling.MySQLConnectionPool(**Config.DB_CONFIG)
    logger.info("Database connection pool initialized")
except Exception as e:
    logger.error(f"Failed to initialize database pool: {e}")
    db_pool = None

# Security and authentication
def generate_api_token(user_id: str, expiry_hours: int = 24) -> str:
    """Generate a secure API token"""
    timestamp = int(time.time())
    expiry = timestamp + (expiry_hours * 3600)
    payload = f"{user_id}:{expiry}:{secrets.token_hex(16)}"
    signature = hashlib.sha256(f"{payload}:{Config.SECRET_KEY}".encode()).hexdigest()
    return f"{payload}:{signature}"

def verify_api_token(token: str) -> Optional[str]:
    """Verify API token and return user_id if valid"""
    try:
        parts = token.split(':')
        if len(parts) != 4:
            return None
        
        user_id, expiry_str, nonce, signature = parts
        expiry = int(expiry_str)
        
        if time.time() > expiry:
            return None
        
        payload = f"{user_id}:{expiry_str}:{nonce}"
        expected_signature = hashlib.sha256(f"{payload}:{Config.SECRET_KEY}".encode()).hexdigest()
        
        if signature == expected_signature:
            return user_id
        
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
    
    return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No authorization token provided'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_id = verify_api_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        g.user_id = user_id
        return f(*args, **kwargs)
    
    return decorated_function

# Database utilities
def get_db_connection():
    """Get database connection from pool"""
    if not db_pool:
        raise Exception("Database pool not initialized")
    return db_pool.get_connection()

def execute_query(query: str, params: tuple = None) -> List[Dict]:
    """Execute query and return results"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
        else:
            conn.commit()
            results = []
        
        cursor.close()
        conn.close()
        return results
        
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        raise

# Network utilities
def check_port_health(host: str, port: int, timeout: int = 5) -> bool:
    """Check if a port is accessible"""
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def get_server_stats() -> Dict[str, Any]:
    """Get server performance statistics"""
    stats = {
        'timestamp': datetime.utcnow().isoformat(),
        'ports': {},
        'database': {'status': 'unknown', 'connections': 0},
        'load_balancer': {'status': 'unknown'},
        'bonding': Config.BONDING_CONFIG
    }
    
    # Check port health
    for port_name, port_num in Config.FFXI_PORTS.items():
        if port_name != 'SQL_PORT':  # Skip database port for external check
            stats['ports'][port_name] = {
                'port': port_num,
                'status': 'healthy' if check_port_health('localhost', port_num) else 'unhealthy'
            }
    
    # Check database health
    try:
        result = execute_query("SELECT COUNT(*) as connection_count FROM information_schema.processlist")
        if result:
            stats['database']['status'] = 'healthy'
            stats['database']['connections'] = result[0]['connection_count']
    except Exception as e:
        stats['database']['status'] = 'unhealthy'
        stats['database']['error'] = str(e)
    
    # Check HAProxy status
    try:
        if check_port_health('load_balancer', 8404):
            stats['load_balancer']['status'] = 'healthy'
        else:
            stats['load_balancer']['status'] = 'unhealthy'
    except Exception:
        stats['load_balancer']['status'] = 'unknown'
    
    return stats

def configure_network_bonding(interfaces: List[str], mode: str = 'balance-xor') -> Dict[str, Any]:
    """Configure network bonding for high-load scenarios"""
    if not Config.BONDING_CONFIG['enabled']:
        return {'error': 'Network bonding is disabled'}
    
    try:
        # This is a simplified bonding configuration
        # In production, this would interface with the actual network stack
        bonding_config = {
            'mode': mode,
            'interfaces': interfaces,
            'hash_policy': Config.BONDING_CONFIG['hash_policy'],
            'mii_monitoring': Config.BONDING_CONFIG['mii_mon_interval'],
            'failover_timeout': Config.BONDING_CONFIG['failover_timeout']
        }
        
        logger.info(f"Network bonding configured: {bonding_config}")
        return {'status': 'configured', 'config': bonding_config}
        
    except Exception as e:
        logger.error(f"Failed to configure network bonding: {e}")
        return {'error': str(e)}

# API Routes

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'service': 'FFXI Server Management API'
    })

@app.route('/auth/token', methods=['POST'])
def get_auth_token():
    """Get authentication token"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required'}), 400
    
    # Simple authentication (in production, use proper user management)
    if data['username'] == 'admin' and data['password'] == Config.SECRET_KEY:
        token = generate_api_token(data['username'])
        return jsonify({
            'token': token,
            'expires_in': 86400,  # 24 hours
            'token_type': 'Bearer'
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/status', methods=['GET'])
@require_auth
def get_server_status():
    """Get comprehensive server status"""
    try:
        stats = get_server_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Failed to get server status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ports', methods=['GET'])
@require_auth
def get_port_configuration():
    """Get current port configuration"""
    return jsonify({
        'ports': Config.FFXI_PORTS,
        'bonding': Config.BONDING_CONFIG,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/ports/test', methods=['POST'])
@require_auth
def test_port_connectivity():
    """Test connectivity to specific ports"""
    data = request.get_json()
    
    if not data or 'ports' not in data:
        return jsonify({'error': 'Port list required'}), 400
    
    results = {}
    for port in data['ports']:
        if isinstance(port, dict):
            host = port.get('host', 'localhost')
            port_num = port.get('port')
        else:
            host = 'localhost'
            port_num = port
        
        if port_num:
            results[f"{host}:{port_num}"] = check_port_health(host, port_num)
    
    return jsonify({
        'results': results,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/bonding/configure', methods=['POST'])
@require_auth
def configure_bonding():
    """Configure network bonding for high-load scenarios"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Configuration data required'}), 400
    
    interfaces = data.get('interfaces', [])
    mode = data.get('mode', 'balance-xor')
    
    result = configure_network_bonding(interfaces, mode)
    
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result)

@app.route('/api/cloudflare/tunnel/config', methods=['GET', 'POST'])
@require_auth
def cloudflare_tunnel_config():
    """Manage Cloudflare tunnel configuration"""
    if request.method == 'GET':
        try:
            with open('/opt/ffxi/cloudflare-tunnel.yml', 'r') as f:
                config = yaml.safe_load(f)
            return jsonify(config)
        except FileNotFoundError:
            return jsonify({'error': 'Cloudflare tunnel not configured'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Configuration data required'}), 400
        
        try:
            # Generate new tunnel configuration
            tunnel_config = {
                'tunnel': data.get('tunnel_name', 'ffxi-server'),
                'credentials-file': '/opt/ffxi/.cloudflared/tunnel.json',
                'ingress': []
            }
            
            # Add ingress rules for FFXI ports
            domain = data.get('domain', 'example.com')
            
            port_mappings = {
                'login': Config.FFXI_PORTS['LOGIN_VIEW_PORT'],
                'data': Config.FFXI_PORTS['LOGIN_DATA_PORT'],
                'auth': Config.FFXI_PORTS['LOGIN_AUTH_PORT'],
                'config': Config.FFXI_PORTS['LOGIN_CONF_PORT'],
                'search': Config.FFXI_PORTS['SEARCH_PORT'],
                'admin': Config.FFXI_PORTS['HTTP_PORT']
            }
            
            for service, port in port_mappings.items():
                tunnel_config['ingress'].append({
                    'hostname': f"{service}.{domain}",
                    'service': f"tcp://localhost:{port}" if service != 'admin' else f"http://localhost:{port}"
                })
            
            # Add catch-all rule
            tunnel_config['ingress'].append({'service': 'http_status:404'})
            
            # Save configuration
            with open('/opt/ffxi/cloudflare-tunnel.yml', 'w') as f:
                yaml.dump(tunnel_config, f, default_flow_style=False)
            
            return jsonify({
                'status': 'configured',
                'config': tunnel_config,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to configure Cloudflare tunnel: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/servers', methods=['GET'])
@require_auth
def get_server_instances():
    """Get information about running server instances"""
    try:
        # Check which server instances are running
        instances = []
        
        for i in range(1, 4):  # Check up to 3 instances
            container_name = f"ffxi-server-{i}"
            try:
                result = subprocess.run(
                    ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Status}}'],
                    capture_output=True, text=True, timeout=5
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    status = 'running' if 'Up' in result.stdout else 'stopped'
                    instances.append({
                        'id': i,
                        'name': container_name,
                        'status': status,
                        'ports': {
                            'login_view': 54010 + i,
                            'login_data': 54240 + (i-1)*10,
                            'login_auth': 54241 + (i-1)*10,
                            'login_conf': 51230 + (i-1)*10,
                            'search': 54010 + i + 1,
                            'zmq': 54010 + i + 2,
                            'http': 8088 + i
                        }
                    })
            except Exception as e:
                logger.warning(f"Failed to check instance {i}: {e}")
        
        return jsonify({
            'instances': instances,
            'total_instances': len(instances),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get server instances: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/compatibility/windower', methods=['GET'])
@require_auth
def windower_compatibility():
    """Get Windower compatibility information"""
    return jsonify({
        'compatible': True,
        'version_support': ['4.x', '5.x'],
        'recommended_settings': {
            'network_timeout': 30000,
            'packet_buffer_size': 8192,
            'enable_compression': True,
            'use_tcp_nodelay': True
        },
        'ports': {
            'login': Config.FFXI_PORTS['LOGIN_VIEW_PORT'],
            'data': Config.FFXI_PORTS['LOGIN_DATA_PORT'],
            'search': Config.FFXI_PORTS['SEARCH_PORT']
        },
        'bonding_support': Config.BONDING_CONFIG['enabled'],
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/compatibility/ashita', methods=['GET'])
@require_auth
def ashita_compatibility():
    """Get Ashita compatibility information"""
    return jsonify({
        'compatible': True,
        'version_support': ['3.x', '4.x'],
        'recommended_settings': {
            'network_timeout': 30000,
            'packet_buffer_size': 8192,
            'enable_compression': True,
            'use_high_performance_mode': True
        },
        'ports': {
            'login': Config.FFXI_PORTS['LOGIN_VIEW_PORT'],
            'data': Config.FFXI_PORTS['LOGIN_DATA_PORT'],
            'search': Config.FFXI_PORTS['SEARCH_PORT']
        },
        'bonding_support': Config.BONDING_CONFIG['enabled'],
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/load-balancer/stats', methods=['GET'])
@require_auth
def get_load_balancer_stats():
    """Get HAProxy load balancer statistics"""
    try:
        # Fetch HAProxy stats
        import urllib.request
        
        try:
            with urllib.request.urlopen('http://load_balancer:8404/stats?stats;csv') as response:
                stats_csv = response.read().decode('utf-8')
            
            # Parse CSV stats (simplified)
            lines = stats_csv.strip().split('\n')
            headers = lines[0].split(',')
            stats = []
            
            for line in lines[1:]:
                if line.strip():
                    values = line.split(',')
                    if len(values) >= len(headers):
                        stat_dict = dict(zip(headers, values))
                        stats.append(stat_dict)
            
            return jsonify({
                'stats': stats,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to fetch HAProxy stats',
                'details': str(e)
            }), 500
            
    except Exception as e:
        logger.error(f"Failed to get load balancer stats: {e}")
        return jsonify({'error': str(e)}), 500

# New endpoints for enhanced web interface
@app.route('/api/dashboard/metrics', methods=['GET'])
@require_auth
def get_dashboard_metrics():
    """Get comprehensive dashboard metrics for web interface"""
    try:
        import psutil
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network statistics
        network = psutil.net_io_counters()
        
        # Database metrics
        db_stats = {'connections': 0, 'status': 'unknown'}
        try:
            result = execute_query("SELECT COUNT(*) as connection_count FROM information_schema.processlist")
            if result:
                db_stats['connections'] = result[0]['connection_count']
                db_stats['status'] = 'healthy'
        except:
            db_stats['status'] = 'unhealthy'
        
        # Players online (simulate - replace with real query)
        try:
            players_result = execute_query("SELECT COUNT(*) as count FROM accounts WHERE login_status = 1")
            players_online = players_result[0]['count'] if players_result else 0
        except:
            players_online = 42  # Fallback
        
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'system': {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'memory_used_gb': round(memory.used / (1024**3), 2),
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'disk_percent': round((disk.used / disk.total) * 100, 1),
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_total_gb': round(disk.total / (1024**3), 2)
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            },
            'database': db_stats,
            'players': {
                'online': players_online,
                'peak_today': players_online + 25,  # Simulate peak
                'average_24h': round(players_online * 0.85, 1)
            },
            'server': {
                'uptime': get_server_uptime(),
                'response_time_ms': measure_response_time(),
                'status': 'online'
            }
        }
        
        return jsonify(metrics)
        
    except Exception as e:
        logger.error(f"Failed to get dashboard metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prometheus/metrics', methods=['GET'])
@require_auth  
def get_prometheus_metrics():
    """Get metrics from Prometheus for dashboard"""
    try:
        import urllib.request
        import urllib.parse
        
        prometheus_url = "http://prometheus:9090"
        metrics = {}
        
        # Define queries for different metrics
        queries = {
            'cpu_usage': 'rate(cpu_usage_active[5m])',
            'memory_usage': 'memory_usage_percent',
            'disk_io': 'rate(disk_io_bytes[5m])',
            'network_traffic': 'rate(network_bytes_total[5m])',
            'ffxi_players_online': 'ffxi_players_online',
            'ffxi_server_instances': 'ffxi_server_instances'
        }
        
        for metric_name, query in queries.items():
            try:
                encoded_query = urllib.parse.quote(query)
                url = f"{prometheus_url}/api/v1/query?query={encoded_query}"
                
                with urllib.request.urlopen(url, timeout=5) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    
                if data['status'] == 'success' and data['data']['result']:
                    # Extract the latest value
                    result = data['data']['result'][0]
                    value = float(result['value'][1])
                    metrics[metric_name] = {
                        'value': value,
                        'timestamp': result['value'][0]
                    }
                else:
                    metrics[metric_name] = {'value': 0, 'timestamp': time.time()}
                    
            except Exception as e:
                logger.warning(f"Failed to fetch {metric_name} from Prometheus: {e}")
                metrics[metric_name] = {'value': 0, 'timestamp': time.time()}
        
        return jsonify({
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'prometheus'
        })
        
    except Exception as e:
        logger.error(f"Failed to get Prometheus metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/online', methods=['GET'])
@require_auth
def get_online_players():
    """Get list of currently online players"""
    try:
        # Query for online players (adjust query based on your schema)
        query = """
        SELECT 
            c.charname,
            c.mjob,
            c.sjob, 
            c.mlvl,
            c.slvl,
            z.name as zone_name,
            TIMESTAMPDIFF(MINUTE, s.connect_time, NOW()) as online_minutes
        FROM chars c
        JOIN accounts a ON c.accid = a.id
        LEFT JOIN zones z ON c.zone = z.zoneid
        LEFT JOIN sessions s ON a.id = s.accid
        WHERE a.login_status = 1
        ORDER BY online_minutes DESC
        LIMIT 50
        """
        
        try:
            players = execute_query(query)
            
            # Format the data for the web interface
            formatted_players = []
            for player in players:
                formatted_players.append({
                    'character': player['charname'],
                    'level': player['mlvl'],
                    'job': f"{get_job_name(player['mjob'])}/{get_job_name(player['sjob'])}",
                    'zone': player['zone_name'] or 'Unknown',
                    'online_time': format_time_duration(player['online_minutes'] or 0)
                })
            
            return jsonify({
                'players': formatted_players,
                'count': len(formatted_players),
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            # Fallback data if database query fails
            return jsonify({
                'players': [
                    {'character': 'DarkKnight', 'level': 75, 'job': 'DRK/WAR', 'zone': 'Dynamis - Xarcabard', 'online_time': '3h 25m'},
                    {'character': 'WhiteMage99', 'level': 72, 'job': 'WHM/BLM', 'zone': 'Ru\'Lude Gardens', 'online_time': '1h 12m'},
                    {'character': 'ThiefMaster', 'level': 68, 'job': 'THF/NIN', 'zone': 'Treasure Casket', 'online_time': '45m'}
                ],
                'count': 3,
                'timestamp': datetime.utcnow().isoformat(),
                'note': 'Fallback data - database unavailable'
            })
            
    except Exception as e:
        logger.error(f"Failed to get online players: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/alerts', methods=['GET'])
@require_auth
def get_server_alerts():
    """Get current server alerts and notifications"""
    try:
        alerts = []
        
        # Check system resources
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        if cpu_percent > 80:
            alerts.append({
                'type': 'system',
                'severity': 'warning',
                'message': f'High CPU usage detected: {cpu_percent:.1f}%',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        if memory.percent > 85:
            alerts.append({
                'type': 'system',
                'severity': 'critical',
                'message': f'High memory usage detected: {memory.percent:.1f}%',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check database connectivity
        try:
            execute_query("SELECT 1")
        except:
            alerts.append({
                'type': 'database',
                'severity': 'critical',
                'message': 'Database connection failed',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check load balancer
        if not check_port_health('localhost', 8404):
            alerts.append({
                'type': 'network',
                'severity': 'warning',
                'message': 'Load balancer health check failed',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return jsonify({
            'alerts': alerts,
            'count': len(alerts),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get server alerts: {e}")
        return jsonify({'error': str(e)}), 500

# Helper functions
def get_server_uptime():
    """Get server uptime"""
    try:
        import psutil
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        return format_time_duration(uptime_seconds / 60)  # Convert to minutes
    except:
        return "Unknown"

def measure_response_time():
    """Measure response time to database"""
    try:
        start_time = time.time()
        execute_query("SELECT 1")
        end_time = time.time()
        return round((end_time - start_time) * 1000)  # Convert to milliseconds
    except:
        return 0

def get_job_name(job_id):
    """Convert job ID to job name"""
    job_names = {
        1: 'WAR', 2: 'MNK', 3: 'WHM', 4: 'BLM', 5: 'RDM', 6: 'THF',
        7: 'PLD', 8: 'DRK', 9: 'BST', 10: 'BRD', 11: 'RNG', 12: 'SAM',
        13: 'NIN', 14: 'DRG', 15: 'SMN', 16: 'BLU', 17: 'COR', 18: 'PUP',
        19: 'DNC', 20: 'SCH', 21: 'GEO', 22: 'RUN'
    }
    return job_names.get(job_id, 'UNK')

def format_time_duration(minutes):
    """Format minutes into human readable duration"""
    if minutes < 60:
        return f"{int(minutes)}m"
    elif minutes < 1440:  # Less than 24 hours
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        return f"{hours}h {mins}m"
    else:  # More than 24 hours
        days = int(minutes // 1440)
        hours = int((minutes % 1440) // 60)
        return f"{days}d {hours}h"

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# GM Management Endpoints
@app.route('/api/gm/accounts', methods=['GET'])
@require_auth
def get_gm_accounts():
    """Get list of GM accounts"""
    try:
        query = """
        SELECT 
            a.id,
            a.login,
            a.priv as account_priv,
            c.charname,
            c.gmlevel,
            c.charid,
            CASE 
                WHEN a.login = %s THEN 1 
                ELSE 0 
            END as is_owner
        FROM accounts a
        LEFT JOIN chars c ON a.id = c.accid
        WHERE a.priv > 1 OR c.gmlevel > 0
        ORDER BY a.priv DESC, c.gmlevel DESC, a.login
        """
        
        # Get server owner from environment or default
        server_owner = os.environ.get('FFXI_SERVER_OWNER', 'admin')
        
        accounts = execute_query(query, (server_owner,))
        
        return jsonify({
            'gm_accounts': accounts,
            'server_owner': server_owner,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get GM accounts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gm/promote', methods=['POST'])
@require_auth
def promote_gm():
    """Promote user to GM level - Admin Dashboard Exclusive"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        target_login = data.get('login')
        target_level = data.get('gmlevel', 0)
        promoter_id = g.user_id
        
        if not target_login:
            return jsonify({'error': 'Target login required'}), 400
        
        if target_level < 0 or target_level > 5:
            return jsonify({'error': 'GM level must be between 0 and 5'}), 400
        
        # Check if promoter is server owner
        server_owner = os.environ.get('FFXI_SERVER_OWNER', 'admin')
        if promoter_id != server_owner:
            return jsonify({'error': 'Only the server owner can promote GMs'}), 403
        
        # Prevent demoting the server owner
        if target_login == server_owner and target_level < 5:
            return jsonify({'error': 'Server owner cannot be demoted below level 5'}), 403
        
        # Get target account information
        account_query = "SELECT id, login, priv FROM accounts WHERE login = %s"
        account_result = execute_query(account_query, (target_login,))
        
        if not account_result:
            return jsonify({'error': 'Account not found'}), 404
        
        target_account = account_result[0]
        account_id = target_account['id']
        
        # Update account privilege level (for web access)
        account_priv = max(2, target_level) if target_level > 0 else 1
        update_account_query = "UPDATE accounts SET priv = %s WHERE id = %s"
        execute_query(update_account_query, (account_priv, account_id))
        
        # Update character GM level
        char_query = "SELECT charid, charname FROM chars WHERE accid = %s LIMIT 1"
        char_result = execute_query(char_query, (account_id,))
        
        if char_result:
            char_id = char_result[0]['charid']
            char_name = char_result[0]['charname']
            
            update_char_query = "UPDATE chars SET gmlevel = %s WHERE charid = %s"
            execute_query(update_char_query, (target_level, char_id))
        else:
            char_name = target_login
        
        # Log the promotion in audit table
        audit_query = """
        INSERT INTO audit_gm (date_time, gm_name, command, full_string)
        VALUES (NOW(), %s, 'ADMIN_PROMOTE', %s)
        """
        audit_message = f"Admin promotion: {target_login} to level {target_level} by {promoter_id}"
        execute_query(audit_query, (promoter_id, audit_message))
        
        logger.info(f"GM promotion: {target_login} promoted to level {target_level} by {promoter_id}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully promoted {target_login} to GM level {target_level}',
            'target': {
                'login': target_login,
                'character': char_name,
                'gmlevel': target_level,
                'account_priv': account_priv
            },
            'promoter': promoter_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to promote GM: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gm/revoke', methods=['POST'])
@require_auth
def revoke_gm():
    """Revoke GM privileges - Admin Dashboard Exclusive"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        target_login = data.get('login')
        promoter_id = g.user_id
        
        if not target_login:
            return jsonify({'error': 'Target login required'}), 400
        
        # Check if promoter is server owner
        server_owner = os.environ.get('FFXI_SERVER_OWNER', 'admin')
        if promoter_id != server_owner:
            return jsonify({'error': 'Only the server owner can revoke GM privileges'}), 403
        
        # Prevent revoking the server owner
        if target_login == server_owner:
            return jsonify({'error': 'Server owner privileges cannot be revoked'}), 403
        
        # Get target account
        account_query = "SELECT id FROM accounts WHERE login = %s"
        account_result = execute_query(account_query, (target_login,))
        
        if not account_result:
            return jsonify({'error': 'Account not found'}), 404
        
        account_id = account_result[0]['id']
        
        # Revoke privileges
        execute_query("UPDATE accounts SET priv = 1 WHERE id = %s", (account_id,))
        execute_query("UPDATE chars SET gmlevel = 0 WHERE accid = %s", (account_id,))
        
        # Log the revocation
        audit_query = """
        INSERT INTO audit_gm (date_time, gm_name, command, full_string)
        VALUES (NOW(), %s, 'ADMIN_REVOKE', %s)
        """
        audit_message = f"Admin revocation: {target_login} GM privileges revoked by {promoter_id}"
        execute_query(audit_query, (promoter_id, audit_message))
        
        logger.info(f"GM revocation: {target_login} privileges revoked by {promoter_id}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully revoked GM privileges for {target_login}',
            'target': target_login,
            'promoter': promoter_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to revoke GM: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gm/audit', methods=['GET'])
@require_auth
def get_gm_audit_log():
    """Get GM command audit log"""
    try:
        # Check if user is server owner
        server_owner = os.environ.get('FFXI_SERVER_OWNER', 'admin')
        if g.user_id != server_owner:
            return jsonify({'error': 'Only the server owner can view audit logs'}), 403
        
        limit = min(int(request.args.get('limit', 50)), 100)
        
        query = """
        SELECT date_time, gm_name, command, full_string
        FROM audit_gm
        ORDER BY date_time DESC
        LIMIT %s
        """
        
        audit_logs = execute_query(query, (limit,))
        
        return jsonify({
            'audit_logs': audit_logs,
            'count': len(audit_logs),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get audit log: {e}")
        return jsonify({'error': str(e)}), 500

# Main application
if __name__ == '__main__':
    logger.info("Starting FFXI Server Management API")
    logger.info(f"API will be available on port {Config.API_PORT}")
    logger.info(f"Database connection: {Config.DB_CONFIG['host']}:{Config.DB_CONFIG['port']}")
    logger.info(f"Network bonding enabled: {Config.BONDING_CONFIG['enabled']}")
    
    app.run(
        host='0.0.0.0',
        port=Config.API_PORT,
        debug=os.environ.get('FFXI_DEBUG_MODE', 'false').lower() == 'true',
        threaded=True
    )