#!/usr/bin/env python3
"""
Ecosystem Integration & API Platform
ITERATION 12: Advanced Ecosystem & Global Scale

Comprehensive API platform for third-party integrations, streaming platforms,
social media integration, and external service webhook framework.
"""

import asyncio
import logging
import json
import time
import hmac
import hashlib
import base64
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import aiohttp
import sqlite3
from pathlib import Path
import jwt
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIVersion(Enum):
    """API version enumeration"""
    V1 = "v1"
    V2 = "v2"
    BETA = "beta"

class IntegrationType(Enum):
    """Integration type enumeration"""
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"
    STREAMING = "streaming"
    SOCIAL_MEDIA = "social_media"
    THIRD_PARTY = "third_party"

class AuthMethod(Enum):
    """Authentication method enumeration"""
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    OAUTH2 = "oauth2"
    WEBHOOK_SIGNATURE = "webhook_signature"

@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    path: str
    method: str
    version: APIVersion
    auth_required: bool = True
    rate_limit: int = 100  # requests per minute
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    response_schema: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WebhookConfiguration:
    """Webhook configuration"""
    webhook_id: str
    url: str
    events: List[str]
    secret: str
    active: bool = True
    retry_attempts: int = 3
    timeout: int = 30
    headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class Integration:
    """Third-party integration configuration"""
    integration_id: str
    name: str
    type: IntegrationType
    auth_method: AuthMethod
    configuration: Dict[str, Any] = field(default_factory=dict)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None

class EcosystemAPIGateway:
    """
    Ecosystem Integration & API Platform
    
    Provides comprehensive API gateway with authentication, rate limiting,
    webhook management, and third-party integrations.
    """
    
    def __init__(self, database_path: str = "ecosystem_api.sqlite"):
        self.database_path = database_path
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.integrations: Dict[str, Integration] = {}
        self.webhooks: Dict[str, WebhookConfiguration] = {}
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # API configuration
        self.jwt_secret = "ffxi_ecosystem_jwt_secret_key"
        self.api_key_length = 32
        self.session_timeout = 3600  # 1 hour
        
        # Initialize database and endpoints
        self.init_database()
        self.register_default_endpoints()
        self.load_integrations()
        
        logger.info("Ecosystem API Gateway initialized")
    
    def init_database(self):
        """Initialize API gateway database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # API keys table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id TEXT UNIQUE NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                permissions TEXT,
                active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME,
                usage_count INTEGER DEFAULT 0
            )
        """)
        
        # Integrations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS integrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                integration_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                auth_method TEXT NOT NULL,
                configuration TEXT,
                active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME
            )
        """)
        
        # Webhooks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                webhook_id TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                events TEXT NOT NULL,
                secret TEXT NOT NULL,
                active BOOLEAN DEFAULT 1,
                retry_attempts INTEGER DEFAULT 3,
                timeout INTEGER DEFAULT 30,
                headers TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # API logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                endpoint TEXT,
                method TEXT,
                client_id TEXT,
                status_code INTEGER,
                response_time REAL,
                request_size INTEGER,
                response_size INTEGER,
                user_agent TEXT,
                ip_address TEXT
            )
        """)
        
        # Webhook deliveries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS webhook_deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                webhook_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT,
                delivery_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                response_code INTEGER,
                response_body TEXT,
                success BOOLEAN,
                retry_count INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("API gateway database initialized")
    
    def register_default_endpoints(self):
        """Register default API endpoints"""
        # Core server endpoints
        self.register_endpoint(APIEndpoint(
            path="/api/v1/server/status",
            method="GET",
            version=APIVersion.V1,
            auth_required=False,
            rate_limit=30,
            description="Get server status information",
            response_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "players_online": {"type": "integer"},
                    "uptime": {"type": "string"},
                    "version": {"type": "string"}
                }
            }
        ))
        
        # Player data endpoints
        self.register_endpoint(APIEndpoint(
            path="/api/v1/players/{player_id}",
            method="GET",
            version=APIVersion.V1,
            auth_required=True,
            rate_limit=60,
            description="Get player information",
            parameters={
                "player_id": {"type": "string", "required": True}
            },
            response_schema={
                "type": "object",
                "properties": {
                    "player_id": {"type": "string"},
                    "name": {"type": "string"},
                    "level": {"type": "integer"},
                    "job": {"type": "string"},
                    "zone": {"type": "string"}
                }
            }
        ))
        
        # Game events endpoint
        self.register_endpoint(APIEndpoint(
            path="/api/v1/events",
            method="GET",
            version=APIVersion.V1,
            auth_required=True,
            rate_limit=100,
            description="Get recent game events",
            response_schema={
                "type": "object",
                "properties": {
                    "events": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "event_id": {"type": "string"},
                                "type": {"type": "string"},
                                "timestamp": {"type": "string"},
                                "data": {"type": "object"}
                            }
                        }
                    }
                }
            }
        ))
        
        # Economy endpoints
        self.register_endpoint(APIEndpoint(
            path="/api/v1/economy/auction_house",
            method="GET",
            version=APIVersion.V1,
            auth_required=True,
            rate_limit=50,
            description="Get auction house data",
            parameters={
                "item_id": {"type": "integer", "required": False},
                "server": {"type": "string", "required": False}
            }
        ))
        
        # Guild/Linkshell endpoints
        self.register_endpoint(APIEndpoint(
            path="/api/v1/guilds/{guild_id}/members",
            method="GET",
            version=APIVersion.V1,
            auth_required=True,
            rate_limit=40,
            description="Get guild member list"
        ))
        
        # WebSocket endpoint for real-time data
        self.register_endpoint(APIEndpoint(
            path="/ws/v1/realtime",
            method="WEBSOCKET",
            version=APIVersion.V1,
            auth_required=True,
            rate_limit=0,  # No rate limit for WebSocket
            description="Real-time game events via WebSocket"
        ))
        
        # GraphQL endpoint
        self.register_endpoint(APIEndpoint(
            path="/api/v1/graphql",
            method="POST",
            version=APIVersion.V1,
            auth_required=True,
            rate_limit=200,
            description="GraphQL query endpoint"
        ))
        
        logger.info(f"Registered {len(self.endpoints)} default API endpoints")
    
    def register_endpoint(self, endpoint: APIEndpoint):
        """Register an API endpoint"""
        endpoint_key = f"{endpoint.method}:{endpoint.path}"
        self.endpoints[endpoint_key] = endpoint
        logger.debug(f"Registered endpoint: {endpoint_key}")
    
    def generate_api_key(self, name: str, permissions: List[str] = None) -> str:
        """Generate a new API key"""
        key_id = str(uuid.uuid4())
        api_key = base64.urlsafe_b64encode(
            hashlib.sha256(f"{key_id}_{time.time()}".encode()).digest()
        ).decode()[:self.api_key_length]
        
        # Store in database
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO api_keys (key_id, api_key, name, permissions, active)
            VALUES (?, ?, ?, ?, ?)
        """, (
            key_id,
            api_key,
            name,
            json.dumps(permissions or []),
            True
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Generated API key for: {name}")
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return key information"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT key_id, name, permissions, active, usage_count
            FROM api_keys 
            WHERE api_key = ? AND active = 1
        """, (api_key,))
        
        result = cursor.fetchone()
        
        if result:
            # Update usage statistics
            cursor.execute("""
                UPDATE api_keys 
                SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE api_key = ?
            """, (api_key,))
            conn.commit()
            
            key_info = {
                'key_id': result[0],
                'name': result[1],
                'permissions': json.loads(result[2] or '[]'),
                'active': bool(result[3]),
                'usage_count': result[4] + 1
            }
        else:
            key_info = None
        
        conn.close()
        return key_info
    
    def generate_jwt_token(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """Generate JWT token"""
        payload['exp'] = time.time() + expires_in
        payload['iat'] = time.time()
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    def check_rate_limit(self, client_id: str, endpoint: str, limit: int) -> bool:
        """Check if client is within rate limits"""
        if limit <= 0:  # No rate limit
            return True
        
        current_time = time.time()
        window_start = current_time - 60  # 1-minute window
        
        # Initialize rate limit tracking for client
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = {}
        
        if endpoint not in self.rate_limits[client_id]:
            self.rate_limits[client_id][endpoint] = []
        
        # Remove old requests outside the window
        self.rate_limits[client_id][endpoint] = [
            req_time for req_time in self.rate_limits[client_id][endpoint]
            if req_time > window_start
        ]
        
        # Check if within limit
        if len(self.rate_limits[client_id][endpoint]) >= limit:
            return False
        
        # Add current request
        self.rate_limits[client_id][endpoint].append(current_time)
        return True
    
    async def process_api_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming API request"""
        start_time = time.time()
        
        try:
            method = request_data.get('method', 'GET')
            path = request_data.get('path', '/')
            headers = request_data.get('headers', {})
            client_ip = request_data.get('client_ip', 'unknown')
            
            # Find matching endpoint
            endpoint_key = f"{method}:{path}"
            endpoint = self.endpoints.get(endpoint_key)
            
            if not endpoint:
                return {
                    'status_code': 404,
                    'error': 'Endpoint not found',
                    'message': f'No endpoint registered for {method} {path}'
                }
            
            # Authenticate request
            client_id = 'anonymous'
            if endpoint.auth_required:
                auth_result = self.authenticate_request(headers)
                if not auth_result['success']:
                    return {
                        'status_code': 401,
                        'error': 'Authentication failed',
                        'message': auth_result['message']
                    }
                client_id = auth_result['client_id']
            
            # Check rate limits
            if not self.check_rate_limit(client_id, endpoint_key, endpoint.rate_limit):
                return {
                    'status_code': 429,
                    'error': 'Rate limit exceeded',
                    'message': f'Rate limit of {endpoint.rate_limit} requests per minute exceeded'
                }
            
            # Process request based on endpoint type
            if method == 'WEBSOCKET':
                response = await self.handle_websocket_request(request_data, endpoint)
            elif path.endswith('/graphql'):
                response = await self.handle_graphql_request(request_data, endpoint)
            else:
                response = await self.handle_rest_request(request_data, endpoint)
            
            # Log request
            response_time = time.time() - start_time
            self.log_api_request(
                endpoint=path,
                method=method,
                client_id=client_id,
                status_code=response.get('status_code', 200),
                response_time=response_time,
                request_size=len(str(request_data)),
                response_size=len(str(response)),
                user_agent=headers.get('User-Agent', ''),
                ip_address=client_ip
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing API request: {e}")
            return {
                'status_code': 500,
                'error': 'Internal server error',
                'message': str(e)
            }
    
    def authenticate_request(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Authenticate API request"""
        # Check for API key in headers
        api_key = headers.get('X-API-Key') or headers.get('Authorization', '').replace('Bearer ', '')
        
        if api_key:
            # Try API key authentication
            key_info = self.validate_api_key(api_key)
            if key_info:
                return {
                    'success': True,
                    'client_id': key_info['key_id'],
                    'auth_method': 'api_key',
                    'permissions': key_info['permissions']
                }
            
            # Try JWT token authentication
            token_payload = self.validate_jwt_token(api_key)
            if token_payload:
                return {
                    'success': True,
                    'client_id': token_payload.get('sub', 'jwt_user'),
                    'auth_method': 'jwt_token',
                    'permissions': token_payload.get('permissions', [])
                }
        
        return {
            'success': False,
            'message': 'No valid authentication provided'
        }
    
    async def handle_rest_request(self, request_data: Dict[str, Any], endpoint: APIEndpoint) -> Dict[str, Any]:
        """Handle REST API request"""
        path = request_data.get('path', '')
        method = request_data.get('method', 'GET')
        query_params = request_data.get('query_params', {})
        body = request_data.get('body', {})
        
        # Mock REST API responses based on endpoint
        if '/server/status' in path:
            return {
                'status_code': 200,
                'data': {
                    'status': 'online',
                    'players_online': 247,
                    'uptime': '5 days, 14 hours',
                    'version': '1.0.0',
                    'timestamp': datetime.now().isoformat()
                }
            }
        
        elif '/players/' in path:
            # Extract player ID from path
            parts = path.split('/')
            player_id = parts[-1] if parts else 'unknown'
            
            return {
                'status_code': 200,
                'data': {
                    'player_id': player_id,
                    'name': f'Player{player_id}',
                    'level': 75,
                    'job': 'Warrior',
                    'subjob': 'Monk',
                    'zone': 'Jeuno',
                    'online': True,
                    'last_login': datetime.now().isoformat()
                }
            }
        
        elif '/events' in path:
            return {
                'status_code': 200,
                'data': {
                    'events': [
                        {
                            'event_id': f'event_{i}',
                            'type': 'player_login',
                            'timestamp': (datetime.now() - timedelta(minutes=i*5)).isoformat(),
                            'data': {'player_name': f'Player{i}'}
                        }
                        for i in range(10)
                    ],
                    'total': 10,
                    'page': 1
                }
            }
        
        elif '/economy/auction_house' in path:
            return {
                'status_code': 200,
                'data': {
                    'listings': [
                        {
                            'item_id': 12345,
                            'item_name': 'Dragon Sword',
                            'price': 150000,
                            'seller': 'PlayerSeller',
                            'quantity': 1,
                            'server': 'Bahamut'
                        }
                    ],
                    'total_listings': 1,
                    'average_price': 150000
                }
            }
        
        elif '/guilds/' in path and '/members' in path:
            return {
                'status_code': 200,
                'data': {
                    'guild_id': 'guild_123',
                    'guild_name': 'Elite Warriors',
                    'members': [
                        {
                            'player_id': f'player_{i}',
                            'name': f'Member{i}',
                            'rank': 'Member' if i > 0 else 'Leader',
                            'join_date': (datetime.now() - timedelta(days=i*30)).isoformat()
                        }
                        for i in range(5)
                    ],
                    'member_count': 5
                }
            }
        
        else:
            return {
                'status_code': 404,
                'error': 'Endpoint not implemented',
                'message': f'Handler for {path} not implemented'
            }
    
    async def handle_graphql_request(self, request_data: Dict[str, Any], endpoint: APIEndpoint) -> Dict[str, Any]:
        """Handle GraphQL request"""
        body = request_data.get('body', {})
        query = body.get('query', '')
        variables = body.get('variables', {})
        
        # Simple GraphQL query parsing and response
        if 'serverStatus' in query:
            return {
                'status_code': 200,
                'data': {
                    'data': {
                        'serverStatus': {
                            'online': True,
                            'playersOnline': 247,
                            'uptime': '5 days, 14 hours'
                        }
                    }
                }
            }
        
        elif 'player' in query:
            player_id = variables.get('id', 'unknown')
            return {
                'status_code': 200,
                'data': {
                    'data': {
                        'player': {
                            'id': player_id,
                            'name': f'Player{player_id}',
                            'level': 75,
                            'job': {
                                'name': 'Warrior',
                                'level': 75
                            },
                            'location': {
                                'zone': 'Jeuno',
                                'coordinates': {'x': 100, 'y': 50, 'z': 200}
                            }
                        }
                    }
                }
            }
        
        else:
            return {
                'status_code': 400,
                'error': 'Invalid GraphQL query',
                'message': 'Unable to parse or process GraphQL query'
            }
    
    async def handle_websocket_request(self, request_data: Dict[str, Any], endpoint: APIEndpoint) -> Dict[str, Any]:
        """Handle WebSocket connection request"""
        # Mock WebSocket connection establishment
        session_id = str(uuid.uuid4())
        
        # Store session information
        self.active_sessions[session_id] = {
            'type': 'websocket',
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'subscriptions': []
        }
        
        return {
            'status_code': 101,  # Switching Protocols
            'message': 'WebSocket connection established',
            'session_id': session_id,
            'data': {
                'protocols': ['ffxi-realtime-v1'],
                'extensions': ['permessage-deflate']
            }
        }
    
    def log_api_request(self, endpoint: str, method: str, client_id: str, 
                       status_code: int, response_time: float, request_size: int,
                       response_size: int, user_agent: str, ip_address: str):
        """Log API request to database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO api_logs (
                    endpoint, method, client_id, status_code, response_time,
                    request_size, response_size, user_agent, ip_address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                endpoint, method, client_id, status_code, response_time,
                request_size, response_size, user_agent, ip_address
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.warning(f"Error logging API request: {e}")
    
    def register_webhook(self, webhook_config: WebhookConfiguration):
        """Register a webhook"""
        self.webhooks[webhook_config.webhook_id] = webhook_config
        
        # Store in database
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO webhooks (
                webhook_id, url, events, secret, active, retry_attempts, timeout, headers
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            webhook_config.webhook_id,
            webhook_config.url,
            json.dumps(webhook_config.events),
            webhook_config.secret,
            webhook_config.active,
            webhook_config.retry_attempts,
            webhook_config.timeout,
            json.dumps(webhook_config.headers)
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Registered webhook: {webhook_config.webhook_id}")
    
    async def trigger_webhook(self, event_type: str, payload: Dict[str, Any]):
        """Trigger webhooks for a specific event"""
        # Find webhooks subscribed to this event type
        relevant_webhooks = [
            webhook for webhook in self.webhooks.values()
            if event_type in webhook.events and webhook.active
        ]
        
        # Send webhook notifications
        tasks = []
        for webhook in relevant_webhooks:
            task = asyncio.create_task(
                self.send_webhook_notification(webhook, event_type, payload)
            )
            tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful = sum(1 for result in results if isinstance(result, bool) and result)
            logger.info(f"Webhook notifications sent: {successful}/{len(tasks)} successful")
    
    async def send_webhook_notification(self, webhook: WebhookConfiguration, 
                                      event_type: str, payload: Dict[str, Any]) -> bool:
        """Send webhook notification"""
        try:
            # Prepare webhook payload
            webhook_payload = {
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'data': payload
            }
            
            # Generate signature
            signature = self.generate_webhook_signature(
                json.dumps(webhook_payload), 
                webhook.secret
            )
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'X-FFXI-Signature': signature,
                'X-FFXI-Event': event_type,
                'User-Agent': 'FFXI-Webhook/1.0'
            }
            headers.update(webhook.headers)
            
            # Send webhook
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=webhook.timeout)) as session:
                async with session.post(
                    webhook.url,
                    json=webhook_payload,
                    headers=headers
                ) as response:
                    success = 200 <= response.status < 300
                    response_body = await response.text()
                    
                    # Log webhook delivery
                    self.log_webhook_delivery(
                        webhook.webhook_id,
                        event_type,
                        webhook_payload,
                        response.status,
                        response_body,
                        success
                    )
                    
                    return success
        
        except Exception as e:
            logger.error(f"Error sending webhook to {webhook.url}: {e}")
            
            # Log failed delivery
            self.log_webhook_delivery(
                webhook.webhook_id,
                event_type,
                payload,
                0,
                str(e),
                False
            )
            
            return False
    
    def generate_webhook_signature(self, payload: str, secret: str) -> str:
        """Generate webhook signature"""
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def log_webhook_delivery(self, webhook_id: str, event_type: str, payload: Dict[str, Any],
                           response_code: int, response_body: str, success: bool):
        """Log webhook delivery"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO webhook_deliveries (
                    webhook_id, event_type, payload, response_code, 
                    response_body, success, retry_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                webhook_id,
                event_type,
                json.dumps(payload),
                response_code,
                response_body,
                success,
                0
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.warning(f"Error logging webhook delivery: {e}")
    
    def register_integration(self, integration: Integration):
        """Register a third-party integration"""
        self.integrations[integration.integration_id] = integration
        
        # Store in database
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO integrations (
                integration_id, name, type, auth_method, configuration, active
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            integration.integration_id,
            integration.name,
            integration.type.value,
            integration.auth_method.value,
            json.dumps(integration.configuration),
            integration.active
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Registered integration: {integration.name}")
    
    def load_integrations(self):
        """Load integrations from database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM integrations WHERE active = 1")
            rows = cursor.fetchall()
            
            for row in rows:
                integration = Integration(
                    integration_id=row[1],
                    name=row[2],
                    type=IntegrationType(row[3]),
                    auth_method=AuthMethod(row[4]),
                    configuration=json.loads(row[5] or '{}'),
                    active=bool(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    last_used=datetime.fromisoformat(row[8]) if row[8] else None
                )
                self.integrations[integration.integration_id] = integration
            
            conn.close()
            logger.info(f"Loaded {len(self.integrations)} integrations")
            
        except Exception as e:
            logger.warning(f"Error loading integrations: {e}")
    
    def get_api_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get request statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_requests,
                    AVG(response_time) as avg_response_time,
                    COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count,
                    COUNT(DISTINCT client_id) as unique_clients
                FROM api_logs 
                WHERE timestamp > datetime('now', '-24 hours')
            """)
            stats_row = cursor.fetchone()
            
            # Get top endpoints
            cursor.execute("""
                SELECT endpoint, COUNT(*) as request_count
                FROM api_logs 
                WHERE timestamp > datetime('now', '-24 hours')
                GROUP BY endpoint
                ORDER BY request_count DESC
                LIMIT 10
            """)
            top_endpoints = cursor.fetchall()
            
            # Get webhook statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_deliveries,
                    COUNT(CASE WHEN success = 1 THEN 1 END) as successful_deliveries
                FROM webhook_deliveries
                WHERE delivery_timestamp > datetime('now', '-24 hours')
            """)
            webhook_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'api_requests': {
                    'total': stats_row[0] or 0,
                    'avg_response_time_ms': (stats_row[1] or 0) * 1000,
                    'error_count': stats_row[2] or 0,
                    'unique_clients': stats_row[3] or 0,
                    'error_rate': (stats_row[2] or 0) / max(stats_row[0] or 1, 1)
                },
                'top_endpoints': [
                    {'endpoint': row[0], 'requests': row[1]}
                    for row in top_endpoints
                ],
                'webhooks': {
                    'total_deliveries': webhook_stats[0] or 0,
                    'successful_deliveries': webhook_stats[1] or 0,
                    'success_rate': (webhook_stats[1] or 0) / max(webhook_stats[0] or 1, 1)
                },
                'integrations': {
                    'total': len(self.integrations),
                    'active': sum(1 for i in self.integrations.values() if i.active)
                },
                'active_sessions': len(self.active_sessions)
            }
            
        except Exception as e:
            logger.error(f"Error getting API statistics: {e}")
            return {}

# Example usage and testing
async def main():
    """Main function for testing ecosystem API"""
    api_gateway = EcosystemAPIGateway()
    
    print("\n🌐 FFXI Ecosystem Integration & API Platform")
    print("=" * 60)
    
    # Generate API key
    api_key = api_gateway.generate_api_key(
        name="Test Application",
        permissions=["read:players", "read:events", "write:webhooks"]
    )
    print(f"🔑 Generated API Key: {api_key[:16]}...")
    
    # Test API requests
    print("\n📡 Testing API Endpoints...")
    
    test_requests = [
        {
            'method': 'GET',
            'path': '/api/v1/server/status',
            'headers': {},
            'client_ip': '127.0.0.1'
        },
        {
            'method': 'GET',
            'path': '/api/v1/players/12345',
            'headers': {'X-API-Key': api_key},
            'client_ip': '127.0.0.1'
        },
        {
            'method': 'GET',
            'path': '/api/v1/events',
            'headers': {'X-API-Key': api_key},
            'client_ip': '127.0.0.1'
        },
        {
            'method': 'POST',
            'path': '/api/v1/graphql',
            'headers': {'X-API-Key': api_key, 'Content-Type': 'application/json'},
            'body': {
                'query': '{ serverStatus { online playersOnline uptime } }'
            },
            'client_ip': '127.0.0.1'
        }
    ]
    
    for i, request in enumerate(test_requests, 1):
        response = await api_gateway.process_api_request(request)
        print(f"Request {i}: {request['method']} {request['path']} "
              f"-> {response.get('status_code', 'unknown')}")
    
    # Test webhook registration
    print("\n🔗 Testing Webhook Integration...")
    webhook = WebhookConfiguration(
        webhook_id="test_webhook_1",
        url="https://example.com/webhook",
        events=["player.login", "player.logout", "server.status"],
        secret="webhook_secret_key"
    )
    api_gateway.register_webhook(webhook)
    
    # Trigger test webhook
    await api_gateway.trigger_webhook("player.login", {
        "player_id": "12345",
        "player_name": "TestPlayer",
        "login_time": datetime.now().isoformat()
    })
    
    # Test integration registration
    print("\n🔌 Testing Third-Party Integrations...")
    
    # Discord integration
    discord_integration = Integration(
        integration_id="discord_bot_1",
        name="Discord Bot Integration",
        type=IntegrationType.WEBHOOK,
        auth_method=AuthMethod.WEBHOOK_SIGNATURE,
        configuration={
            "discord_webhook_url": "https://discord.com/api/webhooks/...",
            "channels": ["general", "events"],
            "event_types": ["player.achievement", "server.announcement"]
        }
    )
    api_gateway.register_integration(discord_integration)
    
    # Streaming platform integration
    twitch_integration = Integration(
        integration_id="twitch_stream_1",
        name="Twitch Stream Integration",
        type=IntegrationType.REST_API,
        auth_method=AuthMethod.OAUTH2,
        configuration={
            "twitch_client_id": "your_twitch_client_id",
            "stream_events": ["boss.defeated", "rare.drop"],
            "overlay_enabled": True
        }
    )
    api_gateway.register_integration(twitch_integration)
    
    # Test rate limiting
    print("\n⏱️ Testing Rate Limiting...")
    rate_limit_requests = []
    for i in range(5):
        request = {
            'method': 'GET',
            'path': '/api/v1/server/status',
            'headers': {},
            'client_ip': '127.0.0.1'
        }
        response = await api_gateway.process_api_request(request)
        rate_limit_requests.append(response['status_code'])
    
    print(f"Rate limit test results: {rate_limit_requests}")
    
    # Get API statistics
    print("\n📊 API Statistics:")
    stats = api_gateway.get_api_statistics()
    if stats:
        print(f"Total Requests: {stats['api_requests']['total']}")
        print(f"Average Response Time: {stats['api_requests']['avg_response_time_ms']:.2f}ms")
        print(f"Error Rate: {stats['api_requests']['error_rate']:.2%}")
        print(f"Active Integrations: {stats['integrations']['active']}")
        print(f"Webhook Success Rate: {stats['webhooks']['success_rate']:.2%}")
    
    print("\n✅ Ecosystem API platform testing completed!")

if __name__ == "__main__":
    asyncio.run(main())