#!/usr/bin/env python3
"""
ITERATION 11: Mobile & Web Platform - Progressive Web App Support
Provides mobile companion application and advanced web administration features.
"""

import asyncio
import aiohttp
from aiohttp import web, WSMsgType
import aiofiles
import json
import sqlite3
import logging
import os
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib
import jwt
import qrcode
import io
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MobileWebPlatform:
    """Enhanced mobile and web platform for FFXI Server"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8090):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.websockets: Dict[str, web.WebSocketResponse] = {}
        self.jwt_secret = os.environ.get('FFXI_JWT_SECRET', 'change_in_production_environment')
        
        # Initialize database and routes
        self._init_database()
        self._setup_routes()
        
    def _init_database(self):
        """Initialize SQLite database for mobile/web platform"""
        self.db = sqlite3.connect('tools/admin/mobile_web_platform.db', check_same_thread=False)
        cursor = self.db.cursor()
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_name TEXT NOT NULL,
                device_type TEXT NOT NULL,
                device_info TEXT,
                ip_address TEXT,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                push_token TEXT
            )
        ''')
        
        # Mobile app installations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mobile_installations (
                installation_id TEXT PRIMARY KEY,
                user_name TEXT,
                device_platform TEXT NOT NULL,
                app_version TEXT NOT NULL,
                device_model TEXT,
                os_version TEXT,
                install_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Push notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS push_notifications (
                notification_id TEXT PRIMARY KEY,
                user_name TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                data TEXT,
                sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivered_time TIMESTAMP,
                read_time TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # PWA data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pwa_data (
                user_name TEXT PRIMARY KEY,
                offline_data TEXT,
                sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cache_version INTEGER DEFAULT 1,
                preferences TEXT
            )
        ''')
        
        # Community features table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS community_posts (
                post_id TEXT PRIMARY KEY,
                user_name TEXT NOT NULL,
                post_type TEXT NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                media_url TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                is_featured BOOLEAN DEFAULT FALSE
            )
        ''')
        
        self.db.commit()
        logger.info("Mobile/Web platform database initialized successfully")
        
    def _setup_routes(self):
        """Setup HTTP routes and WebSocket handlers"""
        # Static files
        self.app.router.add_static('/', path='tools/admin/web_static/', name='static')
        
        # API routes
        self.app.router.add_post('/api/auth/login', self.handle_login)
        self.app.router.add_post('/api/auth/logout', self.handle_logout)
        self.app.router.add_get('/api/auth/qr-code', self.generate_qr_login)
        
        # Server status API
        self.app.router.add_get('/api/server/status', self.get_server_status)
        self.app.router.add_get('/api/server/players', self.get_player_list)
        self.app.router.add_get('/api/server/zones', self.get_zone_status)
        
        # Character management API
        self.app.router.add_get('/api/character/{char_name}', self.get_character_info)
        self.app.router.add_post('/api/character/{char_name}/teleport', self.teleport_character)
        self.app.router.add_post('/api/character/{char_name}/item', self.give_item)
        
        # Community features API
        self.app.router.add_get('/api/community/posts', self.get_community_posts)
        self.app.router.add_post('/api/community/posts', self.create_community_post)
        self.app.router.add_post('/api/community/posts/{post_id}/like', self.like_post)
        
        # PWA support
        self.app.router.add_get('/manifest.json', self.serve_manifest)
        self.app.router.add_get('/sw.js', self.serve_service_worker)
        
        # WebSocket for real-time updates
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Mobile app API
        self.app.router.add_post('/api/mobile/register', self.register_mobile_device)
        self.app.router.add_post('/api/mobile/sync', self.sync_mobile_data)
        self.app.router.add_post('/api/mobile/push-token', self.update_push_token)
        
    async def handle_login(self, request):
        """Handle user login"""
        data = await request.json()
        username = data.get('username')
        password = data.get('password')
        device_type = data.get('device_type', 'web')
        
        # In production, this would validate against the FFXI server's user database
        # For now, simulate authentication
        if username and password:
            # Generate JWT token
            token_payload = {
                'username': username,
                'device_type': device_type,
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            }
            token = jwt.encode(token_payload, self.jwt_secret, algorithm='HS256')
            
            # Create session
            session_id = hashlib.sha256(f"{username}:{datetime.now()}".encode()).hexdigest()[:16]
            
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO user_sessions 
                (session_id, user_name, device_type, device_info, ip_address)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_id,
                username,
                device_type,
                request.headers.get('User-Agent', ''),
                request.remote
            ))
            self.db.commit()
            
            return web.json_response({
                'success': True,
                'token': token,
                'session_id': session_id,
                'user': {
                    'username': username,
                    'device_type': device_type
                }
            })
        else:
            return web.json_response({
                'success': False,
                'error': 'Invalid credentials'
            }, status=401)
            
    async def handle_logout(self, request):
        """Handle user logout"""
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
                username = payload['username']
                
                # Deactivate session
                cursor = self.db.cursor()
                cursor.execute('''
                    UPDATE user_sessions SET is_active = FALSE 
                    WHERE user_name = ? AND is_active = TRUE
                ''', (username,))
                self.db.commit()
                
                return web.json_response({'success': True})
            except jwt.InvalidTokenError:
                pass
                
        return web.json_response({'success': False, 'error': 'Invalid token'}, status=401)
        
    async def generate_qr_login(self, request):
        """Generate QR code for mobile login"""
        # Generate temporary login code
        login_code = hashlib.sha256(f"qr_login:{datetime.now()}".encode()).hexdigest()[:12]
        
        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"ffxi://login?code={login_code}")
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return web.json_response({
            'qr_code': f"data:image/png;base64,{img_str}",
            'login_code': login_code,
            'expires_in': 300  # 5 minutes
        })
        
    async def get_server_status(self, request):
        """Get current server status"""
        # Simulate server status - in production this would query actual server
        status = {
            'server_name': 'FFXI-Server',
            'status': 'online',
            'uptime': '7 days, 14 hours, 23 minutes',
            'player_count': 1247,
            'max_players': 2000,
            'zones_active': 156,
            'cpu_usage': 45.2,
            'memory_usage': 67.8,
            'network_io': {
                'bytes_in': 1024 * 1024 * 150,  # 150 MB
                'bytes_out': 1024 * 1024 * 89   # 89 MB
            },
            'last_update': datetime.now().isoformat()
        }
        
        return web.json_response(status)
        
    async def get_player_list(self, request):
        """Get current player list"""
        # Simulate player data
        players = [
            {
                'name': 'Adventurer01',
                'job': 'WAR/NIN',
                'level': '75/37',
                'zone': 'Bastok Mines',
                'status': 'online',
                'login_time': '2024-01-15T10:30:00Z'
            },
            {
                'name': 'MagicUser99',
                'job': 'BLM/WHM',
                'level': '72/36',
                'zone': 'Windurst Woods',
                'status': 'online',
                'login_time': '2024-01-15T11:15:00Z'
            },
            {
                'name': 'HealerPro',
                'job': 'WHM/SCH',
                'level': '75/40',
                'zone': 'San d\'Oria',
                'status': 'online',
                'login_time': '2024-01-15T09:45:00Z'
            }
        ]
        
        return web.json_response({
            'players': players,
            'total_count': len(players),
            'last_update': datetime.now().isoformat()
        })
        
    async def get_zone_status(self, request):
        """Get zone status information"""
        zones = [
            {'name': 'Bastok Mines', 'players': 23, 'status': 'active'},
            {'name': 'Windurst Woods', 'players': 18, 'status': 'active'},
            {'name': 'San d\'Oria', 'players': 31, 'status': 'active'},
            {'name': 'Valkurm Dunes', 'players': 12, 'status': 'active'},
            {'name': 'Qufim Island', 'players': 8, 'status': 'active'},
            {'name': 'Gusgen Mines', 'players': 4, 'status': 'active'},
            {'name': 'King Ranperre\'s Tomb', 'players': 0, 'status': 'inactive'}
        ]
        
        return web.json_response({
            'zones': zones,
            'total_zones': len(zones),
            'active_zones': len([z for z in zones if z['status'] == 'active']),
            'last_update': datetime.now().isoformat()
        })
        
    async def get_character_info(self, request):
        """Get character information"""
        char_name = request.match_info['char_name']
        
        # Simulate character data
        character = {
            'name': char_name,
            'job': 'WAR/NIN',
            'level': '75/37',
            'race': 'Hume',
            'nation': 'Bastok',
            'zone': 'Bastok Mines',
            'position': {'x': 116.5, 'y': -1.0, 'z': -158.2},
            'hp': {'current': 1247, 'max': 1593},
            'mp': {'current': 89, 'max': 156},
            'tp': 1000,
            'exp': {'current': 45623, 'tnl': 2377},
            'gil': 2534678,
            'playtime': '456 days, 12 hours, 34 minutes',
            'last_login': '2024-01-15T10:30:00Z',
            'status': 'online'
        }
        
        return web.json_response(character)
        
    async def teleport_character(self, request):
        """Teleport character to specified location"""
        char_name = request.match_info['char_name']
        data = await request.json()
        
        zone = data.get('zone')
        x = data.get('x', 0)
        y = data.get('y', 0) 
        z = data.get('z', 0)
        
        # In production, this would send commands to the actual FFXI server
        logger.info(f"Teleporting {char_name} to {zone} ({x}, {y}, {z})")
        
        return web.json_response({
            'success': True,
            'message': f'{char_name} teleported to {zone}',
            'new_position': {'x': x, 'y': y, 'z': z, 'zone': zone}
        })
        
    async def give_item(self, request):
        """Give item to character"""
        char_name = request.match_info['char_name']
        data = await request.json()
        
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)
        item_name = data.get('item_name', f'Item {item_id}')
        
        # In production, this would interface with the FFXI server
        logger.info(f"Giving {quantity}x {item_name} to {char_name}")
        
        return web.json_response({
            'success': True,
            'message': f'Gave {quantity}x {item_name} to {char_name}',
            'item': {
                'id': item_id,
                'name': item_name,
                'quantity': quantity
            }
        })
        
    async def get_community_posts(self, request):
        """Get community posts"""
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT * FROM community_posts 
            ORDER BY created_at DESC 
            LIMIT 20
        ''')
        
        columns = [description[0] for description in cursor.description]
        posts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return web.json_response({
            'posts': posts,
            'total_count': len(posts)
        })
        
    async def create_community_post(self, request):
        """Create new community post"""
        data = await request.json()
        
        post_id = hashlib.sha256(f"{data.get('user_name')}:{datetime.now()}".encode()).hexdigest()[:16]
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO community_posts 
            (post_id, user_name, post_type, title, content, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            post_id,
            data.get('user_name'),
            data.get('post_type', 'general'),
            data.get('title'),
            data.get('content'),
            json.dumps(data.get('tags', []))
        ))
        self.db.commit()
        
        return web.json_response({
            'success': True,
            'post_id': post_id,
            'message': 'Post created successfully'
        })
        
    async def like_post(self, request):
        """Like a community post"""
        post_id = request.match_info['post_id']
        
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE community_posts 
            SET likes = likes + 1 
            WHERE post_id = ?
        ''', (post_id,))
        self.db.commit()
        
        return web.json_response({
            'success': True,
            'message': 'Post liked successfully'
        })
        
    async def serve_manifest(self, request):
        """Serve PWA manifest"""
        manifest = {
            "name": "FFXI Server Companion",
            "short_name": "FFXI Companion",
            "description": "Mobile companion app for FFXI Server administration",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#1a1a1a",
            "theme_color": "#4a90e2",
            "orientation": "portrait",
            "icons": [
                {
                    "src": "/static/icons/icon-72x72.png",
                    "sizes": "72x72",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-96x96.png", 
                    "sizes": "96x96",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-128x128.png",
                    "sizes": "128x128", 
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-144x144.png",
                    "sizes": "144x144",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-152x152.png",
                    "sizes": "152x152",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-384x384.png",
                    "sizes": "384x384",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ],
            "categories": ["games", "utilities"],
            "lang": "en",
            "dir": "ltr"
        }
        
        return web.json_response(manifest)
        
    async def serve_service_worker(self, request):
        """Serve service worker for PWA"""
        sw_content = '''
// FFXI Server Companion - Service Worker
const CACHE_NAME = 'ffxi-companion-v1';
const urlsToCache = [
    '/',
    '/static/css/app.css',
    '/static/js/app.js',
    '/static/icons/icon-192x192.png',
    '/manifest.json'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Cache hit - return response
                if (response) {
                    return response;
                }
                return fetch(event.request);
            }
        )
    );
});

self.addEventListener('push', event => {
    const options = {
        body: event.data ? event.data.text() : 'FFXI Server notification',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: '2'
        },
        actions: [
            {
                action: 'explore',
                title: 'View Details',
                icon: '/static/icons/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/icons/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('FFXI Server', options)
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(clients.openWindow('/'));
    }
});
'''
        
        return web.Response(text=sw_content, content_type='application/javascript')
        
    async def websocket_handler(self, request):
        """Handle WebSocket connections for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Generate connection ID
        conn_id = hashlib.sha256(f"{request.remote}:{datetime.now()}".encode()).hexdigest()[:16]
        self.websockets[conn_id] = ws
        
        logger.info(f"WebSocket connection established: {conn_id}")
        
        # Send welcome message
        await ws.send_str(json.dumps({
            'type': 'connection',
            'message': 'Connected to FFXI Server',
            'connection_id': conn_id
        }))
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_websocket_message(ws, data)
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({
                            'type': 'error',
                            'message': 'Invalid JSON format'
                        }))
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
                    
        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
        finally:
            if conn_id in self.websockets:
                del self.websockets[conn_id]
            logger.info(f"WebSocket connection closed: {conn_id}")
            
        return ws
        
    async def _handle_websocket_message(self, ws, data):
        """Handle incoming WebSocket messages"""
        msg_type = data.get('type')
        
        if msg_type == 'subscribe':
            # Subscribe to real-time updates
            await ws.send_str(json.dumps({
                'type': 'subscription',
                'status': 'subscribed',
                'channels': data.get('channels', [])
            }))
        elif msg_type == 'get_status':
            # Send current server status
            status = await self.get_server_status(None)
            await ws.send_str(json.dumps({
                'type': 'status_update',
                'data': json.loads(status.text)
            }))
        elif msg_type == 'ping':
            # Respond to ping
            await ws.send_str(json.dumps({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            }))
            
    async def register_mobile_device(self, request):
        """Register mobile device installation"""
        data = await request.json()
        
        installation_id = hashlib.sha256(
            f"{data.get('device_id')}:{data.get('app_version')}".encode()
        ).hexdigest()[:16]
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO mobile_installations
            (installation_id, user_name, device_platform, app_version, 
             device_model, os_version)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            installation_id,
            data.get('user_name'),
            data.get('platform'),
            data.get('app_version'),
            data.get('device_model'),
            data.get('os_version')
        ))
        self.db.commit()
        
        return web.json_response({
            'success': True,
            'installation_id': installation_id,
            'message': 'Device registered successfully'
        })
        
    async def sync_mobile_data(self, request):
        """Sync mobile app data"""
        data = await request.json()
        user_name = data.get('user_name')
        
        # Update PWA data
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO pwa_data
            (user_name, offline_data, preferences, cache_version)
            VALUES (?, ?, ?, ?)
        ''', (
            user_name,
            json.dumps(data.get('offline_data', {})),
            json.dumps(data.get('preferences', {})),
            data.get('cache_version', 1)
        ))
        self.db.commit()
        
        # Return server-side data
        cursor.execute('SELECT * FROM pwa_data WHERE user_name = ?', (user_name,))
        row = cursor.fetchone()
        
        if row:
            return web.json_response({
                'success': True,
                'data': {
                    'offline_data': json.loads(row[1]) if row[1] else {},
                    'sync_timestamp': row[2],
                    'cache_version': row[3],
                    'preferences': json.loads(row[4]) if row[4] else {}
                }
            })
        else:
            return web.json_response({
                'success': True,
                'data': {
                    'offline_data': {},
                    'preferences': {},
                    'cache_version': 1
                }
            })
            
    async def update_push_token(self, request):
        """Update push notification token"""
        data = await request.json()
        user_name = data.get('user_name')
        push_token = data.get('push_token')
        
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE user_sessions 
            SET push_token = ?
            WHERE user_name = ? AND is_active = TRUE
        ''', (push_token, user_name))
        self.db.commit()
        
        return web.json_response({
            'success': True,
            'message': 'Push token updated successfully'
        })
        
    async def send_push_notification(self, user_name: str, title: str, message: str, 
                                   notification_type: str = 'general', data: Dict = None):
        """Send push notification to user"""
        notification_id = hashlib.sha256(
            f"{user_name}:{title}:{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO push_notifications
            (notification_id, user_name, title, message, notification_type, data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            notification_id,
            user_name,
            title,
            message,
            notification_type,
            json.dumps(data or {})
        ))
        self.db.commit()
        
        # In production, this would send the notification via FCM/APNS
        logger.info(f"Push notification sent to {user_name}: {title}")
        
        # Send to connected WebSocket clients
        for ws in self.websockets.values():
            try:
                await ws.send_str(json.dumps({
                    'type': 'notification',
                    'title': title,
                    'message': message,
                    'notification_type': notification_type,
                    'data': data or {}
                }))
            except Exception as e:
                logger.error(f"Failed to send WebSocket notification: {e}")
                
        return notification_id
        
    async def broadcast_server_event(self, event_type: str, data: Dict):
        """Broadcast server event to all connected clients"""
        message = {
            'type': 'server_event',
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to all WebSocket connections
        disconnected = []
        for conn_id, ws in self.websockets.items():
            try:
                await ws.send_str(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send to WebSocket {conn_id}: {e}")
                disconnected.append(conn_id)
                
        # Clean up disconnected WebSockets
        for conn_id in disconnected:
            del self.websockets[conn_id]
            
    def generate_analytics_report(self) -> Dict[str, Any]:
        """Generate mobile/web platform analytics report"""
        cursor = self.db.cursor()
        
        # Active sessions
        cursor.execute('''
            SELECT device_type, COUNT(*) as count
            FROM user_sessions 
            WHERE is_active = TRUE
            GROUP BY device_type
        ''')
        active_sessions = dict(cursor.fetchall())
        
        # Mobile installations
        cursor.execute('''
            SELECT device_platform, COUNT(*) as count
            FROM mobile_installations
            WHERE is_active = TRUE
            GROUP BY device_platform
        ''')
        mobile_installs = dict(cursor.fetchall())
        
        # Push notification stats
        cursor.execute('''
            SELECT notification_type, status, COUNT(*) as count
            FROM push_notifications
            WHERE sent_time > datetime('now', '-7 days')
            GROUP BY notification_type, status
        ''')
        notification_stats = cursor.fetchall()
        
        # Community engagement
        cursor.execute('''
            SELECT COUNT(*) as posts, SUM(likes) as total_likes
            FROM community_posts
            WHERE created_at > datetime('now', '-7 days')
        ''')
        community_row = cursor.fetchone()
        
        return {
            'generated_at': datetime.now().isoformat(),
            'active_websocket_connections': len(self.websockets),
            'active_sessions_by_device': active_sessions,
            'mobile_installations_by_platform': mobile_installs,
            'push_notification_stats': [
                {'type': row[0], 'status': row[1], 'count': row[2]}
                for row in notification_stats
            ],
            'community_engagement_7d': {
                'new_posts': community_row[0] if community_row else 0,
                'total_likes': community_row[1] if community_row else 0
            }
        }
        
    async def start_background_services(self):
        """Start background services for mobile/web platform"""
        logger.info("Starting mobile/web platform background services...")
        
        # Start periodic server status broadcasts
        asyncio.create_task(self._periodic_status_broadcast())
        
        # Start notification cleanup service
        asyncio.create_task(self._notification_cleanup_service())
        
    async def _periodic_status_broadcast(self):
        """Periodic server status broadcast to connected clients"""
        while True:
            try:
                # Get current server status
                status = {
                    'player_count': 1247,  # Would be real data in production
                    'server_status': 'online',
                    'timestamp': datetime.now().isoformat()
                }
                
                await self.broadcast_server_event('status_update', status)
                await asyncio.sleep(30)  # Broadcast every 30 seconds
                
            except Exception as e:
                logger.error(f"Status broadcast error: {e}")
                await asyncio.sleep(60)
                
    async def _notification_cleanup_service(self):
        """Clean up old notifications"""
        while True:
            try:
                cursor = self.db.cursor()
                # Delete notifications older than 30 days
                cursor.execute('''
                    DELETE FROM push_notifications 
                    WHERE sent_time < datetime('now', '-30 days')
                ''')
                
                # Delete inactive sessions older than 7 days
                cursor.execute('''
                    DELETE FROM user_sessions 
                    WHERE is_active = FALSE AND last_activity < datetime('now', '-7 days')
                ''')
                
                self.db.commit()
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Notification cleanup error: {e}")
                await asyncio.sleep(1800)
                
    async def run_server(self):
        """Run the mobile/web platform server"""
        await self.start_background_services()
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"Mobile/Web platform server started at http://{self.host}:{self.port}")
        
        # Keep the server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down mobile/web platform server...")
        finally:
            await runner.cleanup()

def main():
    """Main function for mobile/web platform"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FFXI Mobile/Web Platform")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8090, help="Port to bind to")
    parser.add_argument("--mode", choices=["server", "report"], default="server",
                       help="Operation mode")
    
    args = parser.parse_args()
    
    platform = MobileWebPlatform(args.host, args.port)
    
    if args.mode == "report":
        report = platform.generate_analytics_report()
        print(json.dumps(report, indent=2))
    else:
        asyncio.run(platform.run_server())

if __name__ == "__main__":
    main()