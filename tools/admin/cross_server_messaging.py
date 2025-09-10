#!/usr/bin/env python3
"""
ITERATION 11: Cross-Server Communication - Inter-Server Messaging Infrastructure
Provides comprehensive cross-server messaging, shared auction house, and load balancing capabilities.
"""

import asyncio
import aiohttp
import json
import sqlite3
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import hashlib
import hmac
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServerNode:
    """Represents a server node in the cluster"""
    server_id: str
    host: str
    port: int
    region: str
    status: str = "online"
    last_heartbeat: Optional[datetime] = None
    load_factor: float = 0.0
    capacity: int = 1000
    
@dataclass
class InterServerMessage:
    """Inter-server message structure"""
    message_id: str
    source_server: str
    target_server: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 1
    retry_count: int = 0

class CrossServerMessaging:
    """Enhanced cross-server messaging infrastructure"""
    
    def __init__(self, server_id: str, config_path: str = "tools/admin/cross_server_config.json"):
        self.server_id = server_id
        self.config_path = config_path
        self.nodes: Dict[str, ServerNode] = {}
        self.message_queue: List[InterServerMessage] = []
        self.shared_secret = os.environ.get('FFXI_CLUSTER_SECRET', 'default_secret_change_in_production')
        
        # Initialize database
        self._init_database()
        self._load_configuration()
        
    def _init_database(self):
        """Initialize SQLite database for cross-server data"""
        self.db = sqlite3.connect('tools/admin/cross_server.db', check_same_thread=False)
        cursor = self.db.cursor()
        
        # Server registry table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servers (
                server_id TEXT PRIMARY KEY,
                host TEXT NOT NULL,
                port INTEGER NOT NULL,
                region TEXT NOT NULL,
                status TEXT DEFAULT 'online',
                last_heartbeat TIMESTAMP,
                load_factor REAL DEFAULT 0.0,
                capacity INTEGER DEFAULT 1000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Inter-server messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                source_server TEXT NOT NULL,
                target_server TEXT NOT NULL,
                message_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                priority INTEGER DEFAULT 1,
                retry_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Shared auction house table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_auction_house (
                item_id INTEGER,
                server_id TEXT,
                seller_name TEXT,
                price INTEGER,
                quantity INTEGER,
                category TEXT,
                subcategory TEXT,
                expiration TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (item_id, server_id, seller_name)
            )
        ''')
        
        # Load balancing metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS load_metrics (
                server_id TEXT,
                timestamp TIMESTAMP,
                cpu_usage REAL,
                memory_usage REAL,
                player_count INTEGER,
                connection_count INTEGER,
                response_time REAL,
                PRIMARY KEY (server_id, timestamp)
            )
        ''')
        
        self.db.commit()
        logger.info("Cross-server database initialized successfully")
        
    def _load_configuration(self):
        """Load server configuration"""
        default_config = {
            "servers": [
                {
                    "server_id": "bahamut-na",
                    "host": "na.ffxi-server.com",
                    "port": 54230,
                    "region": "north_america",
                    "capacity": 2000
                },
                {
                    "server_id": "carbuncle-eu",
                    "host": "eu.ffxi-server.com", 
                    "port": 54230,
                    "region": "europe",
                    "capacity": 1500
                },
                {
                    "server_id": "fenrir-jp",
                    "host": "jp.ffxi-server.com",
                    "port": 54230,
                    "region": "japan",
                    "capacity": 2500
                }
            ],
            "message_types": [
                "player_transfer",
                "auction_house_sync",
                "global_chat",
                "server_status",
                "load_balance_request",
                "data_replication"
            ],
            "heartbeat_interval": 30,
            "message_retry_limit": 3,
            "load_balance_threshold": 0.8
        }
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        else:
            config = default_config
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
        # Load server nodes
        for server_config in config['servers']:
            node = ServerNode(**server_config)
            self.nodes[node.server_id] = node
            
        self.config = config
        logger.info(f"Loaded configuration for {len(self.nodes)} server nodes")
        
    def _sign_message(self, message: str) -> str:
        """Create HMAC signature for message authentication"""
        return hmac.new(
            self.shared_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
    def _verify_signature(self, message: str, signature: str) -> bool:
        """Verify HMAC signature"""
        expected = self._sign_message(message)
        return hmac.compare_digest(expected, signature)
        
    async def send_message(self, target_server: str, message_type: str, payload: Dict[str, Any], priority: int = 1) -> str:
        """Send inter-server message"""
        message_id = hashlib.sha256(
            f"{self.server_id}:{target_server}:{message_type}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        message = InterServerMessage(
            message_id=message_id,
            source_server=self.server_id,
            target_server=target_server,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.now(),
            priority=priority
        )
        
        # Store in database
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO messages (message_id, source_server, target_server, message_type, 
                                payload, timestamp, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'sending')
        ''', (
            message.message_id,
            message.source_server,
            message.target_server,
            message.message_type,
            json.dumps(message.payload),
            message.timestamp,
            message.priority
        ))
        self.db.commit()
        
        # Attempt to deliver message
        if await self._deliver_message(message):
            cursor.execute('UPDATE messages SET status = "delivered" WHERE message_id = ?', 
                         (message_id,))
            self.db.commit()
            logger.info(f"Message {message_id} delivered successfully")
        else:
            logger.warning(f"Failed to deliver message {message_id}")
            
        return message_id
        
    async def _deliver_message(self, message: InterServerMessage) -> bool:
        """Deliver message to target server"""
        if message.target_server not in self.nodes:
            logger.error(f"Unknown target server: {message.target_server}")
            return False
            
        target_node = self.nodes[message.target_server]
        url = f"http://{target_node.host}:{target_node.port}/api/cross-server/message"
        
        # Prepare payload with signature
        payload = {
            'message': asdict(message),
            'signature': self._sign_message(json.dumps(asdict(message), default=str))
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        return True
                    else:
                        logger.error(f"Server returned status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Failed to deliver message: {e}")
            return False
            
    async def heartbeat(self):
        """Send heartbeat to all other servers"""
        load_factor = await self._calculate_load_factor()
        
        for server_id, node in self.nodes.items():
            if server_id != self.server_id:
                await self.send_message(
                    server_id,
                    "heartbeat",
                    {
                        "load_factor": load_factor,
                        "status": "online",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
    async def _calculate_load_factor(self) -> float:
        """Calculate current server load factor"""
        # This would integrate with actual server metrics
        # For now, return a simulated value
        import random
        return random.uniform(0.1, 0.9)
        
    def sync_auction_house_item(self, item_data: Dict[str, Any]):
        """Sync auction house item across all servers"""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO shared_auction_house 
            (item_id, server_id, seller_name, price, quantity, category, subcategory, expiration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item_data['item_id'],
            self.server_id,
            item_data['seller_name'], 
            item_data['price'],
            item_data['quantity'],
            item_data['category'],
            item_data['subcategory'],
            item_data['expiration']
        ))
        self.db.commit()
        
        # Broadcast to all servers
        asyncio.create_task(self._broadcast_auction_update(item_data))
        
    async def _broadcast_auction_update(self, item_data: Dict[str, Any]):
        """Broadcast auction house update to all servers"""
        for server_id in self.nodes:
            if server_id != self.server_id:
                await self.send_message(
                    server_id,
                    "auction_house_sync",
                    item_data
                )
                
    def get_global_auction_house_listings(self, item_id: Optional[int] = None) -> List[Dict]:
        """Get auction house listings from all servers"""
        cursor = self.db.cursor()
        
        if item_id:
            cursor.execute('''
                SELECT * FROM shared_auction_house 
                WHERE item_id = ? AND expiration > CURRENT_TIMESTAMP
                ORDER BY price ASC
            ''', (item_id,))
        else:
            cursor.execute('''
                SELECT * FROM shared_auction_house 
                WHERE expiration > CURRENT_TIMESTAMP
                ORDER BY updated_at DESC
                LIMIT 100
            ''')
            
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    async def request_player_transfer(self, player_name: str, target_server: str, character_data: Dict[str, Any]) -> bool:
        """Request player transfer to another server"""
        if target_server not in self.nodes:
            logger.error(f"Unknown target server: {target_server}")
            return False
            
        # Check target server capacity
        target_node = self.nodes[target_server]
        if target_node.load_factor > self.config['load_balance_threshold']:
            logger.warning(f"Target server {target_server} is at capacity")
            return False
            
        message_id = await self.send_message(
            target_server,
            "player_transfer",
            {
                "player_name": player_name,
                "character_data": character_data,
                "transfer_timestamp": datetime.now().isoformat()
            },
            priority=5  # High priority
        )
        
        logger.info(f"Player transfer request sent: {message_id}")
        return True
        
    def get_server_recommendations(self, region: Optional[str] = None) -> List[Dict]:
        """Get server recommendations based on load and region"""
        cursor = self.db.cursor()
        
        if region:
            # Get servers in specific region
            servers = [node for node in self.nodes.values() if node.region == region]
        else:
            servers = list(self.nodes.values())
            
        # Sort by load factor (ascending - lower load is better)
        servers.sort(key=lambda x: x.load_factor)
        
        recommendations = []
        for server in servers[:5]:  # Top 5 recommendations
            recommendations.append({
                "server_id": server.server_id,
                "region": server.region,
                "load_factor": server.load_factor,
                "capacity": server.capacity,
                "status": server.status,
                "recommendation_score": (1 - server.load_factor) * 100
            })
            
        return recommendations
        
    async def start_services(self):
        """Start background services"""
        logger.info("Starting cross-server communication services...")
        
        # Start heartbeat service
        asyncio.create_task(self._heartbeat_service())
        
        # Start message retry service
        asyncio.create_task(self._message_retry_service())
        
        # Start metrics collection
        asyncio.create_task(self._metrics_collection_service())
        
    async def _heartbeat_service(self):
        """Background heartbeat service"""
        while True:
            try:
                await self.heartbeat()
                await asyncio.sleep(self.config['heartbeat_interval'])
            except Exception as e:
                logger.error(f"Heartbeat service error: {e}")
                await asyncio.sleep(5)
                
    async def _message_retry_service(self):
        """Background message retry service"""
        while True:
            try:
                cursor = self.db.cursor()
                cursor.execute('''
                    SELECT * FROM messages 
                    WHERE status = 'failed' AND retry_count < ?
                    ORDER BY priority DESC, timestamp ASC
                    LIMIT 10
                ''', (self.config['message_retry_limit'],))
                
                messages = cursor.fetchall()
                for row in messages:
                    message = InterServerMessage(
                        message_id=row[0],
                        source_server=row[1],
                        target_server=row[2],
                        message_type=row[3],
                        payload=json.loads(row[4]),
                        timestamp=datetime.fromisoformat(row[5]),
                        priority=row[6],
                        retry_count=row[7]
                    )
                    
                    if await self._deliver_message(message):
                        cursor.execute('UPDATE messages SET status = "delivered" WHERE message_id = ?',
                                     (message.message_id,))
                    else:
                        cursor.execute('''
                            UPDATE messages SET retry_count = retry_count + 1, 
                                              status = CASE WHEN retry_count + 1 >= ? THEN 'expired' ELSE 'failed' END
                            WHERE message_id = ?
                        ''', (self.config['message_retry_limit'], message.message_id))
                    
                self.db.commit()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Message retry service error: {e}")
                await asyncio.sleep(30)
                
    async def _metrics_collection_service(self):
        """Background metrics collection service"""
        while True:
            try:
                # Collect and store load metrics
                load_factor = await self._calculate_load_factor()
                
                cursor = self.db.cursor()
                cursor.execute('''
                    INSERT INTO load_metrics 
                    (server_id, timestamp, cpu_usage, memory_usage, player_count, 
                     connection_count, response_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.server_id,
                    datetime.now(),
                    load_factor * 100,  # CPU usage
                    load_factor * 80,   # Memory usage  
                    int(load_factor * 1000),  # Player count
                    int(load_factor * 500),   # Connection count
                    load_factor * 50    # Response time
                ))
                self.db.commit()
                
                await asyncio.sleep(300)  # Collect every 5 minutes
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)
                
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive cross-server communication report"""
        cursor = self.db.cursor()
        
        # Message statistics
        cursor.execute('''
            SELECT message_type, status, COUNT(*) as count
            FROM messages 
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY message_type, status
        ''')
        message_stats = cursor.fetchall()
        
        # Server load averages
        cursor.execute('''
            SELECT server_id, AVG(cpu_usage) as avg_cpu, AVG(memory_usage) as avg_memory,
                   AVG(player_count) as avg_players
            FROM load_metrics 
            WHERE timestamp > datetime('now', '-1 hour')
            GROUP BY server_id
        ''')
        load_stats = cursor.fetchall()
        
        # Auction house activity
        cursor.execute('''
            SELECT server_id, COUNT(*) as listings, AVG(price) as avg_price
            FROM shared_auction_house 
            WHERE created_at > datetime('now', '-24 hours')
            GROUP BY server_id
        ''')
        auction_stats = cursor.fetchall()
        
        return {
            "generated_at": datetime.now().isoformat(),
            "server_id": self.server_id,
            "active_nodes": len([n for n in self.nodes.values() if n.status == "online"]),
            "message_statistics": {
                "total_24h": sum(row[2] for row in message_stats),
                "by_type_and_status": [
                    {"type": row[0], "status": row[1], "count": row[2]} 
                    for row in message_stats
                ]
            },
            "load_statistics": [
                {
                    "server_id": row[0],
                    "avg_cpu": round(row[1], 2),
                    "avg_memory": round(row[2], 2), 
                    "avg_players": int(row[3])
                }
                for row in load_stats
            ],
            "auction_house_activity": [
                {
                    "server_id": row[0],
                    "listings_24h": row[1],
                    "avg_price": round(row[2], 2) if row[2] else 0
                }
                for row in auction_stats
            ]
        }

def main():
    """Main function for testing cross-server communication"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FFXI Cross-Server Communication")
    parser.add_argument("--server-id", default="bahamut-na", help="Server ID")
    parser.add_argument("--mode", choices=["server", "client", "report"], default="server", 
                       help="Operation mode")
    parser.add_argument("--target", help="Target server for client mode")
    parser.add_argument("--message", help="Message to send in client mode")
    
    args = parser.parse_args()
    
    messaging = CrossServerMessaging(args.server_id)
    
    if args.mode == "report":
        report = messaging.generate_report()
        print(json.dumps(report, indent=2))
    elif args.mode == "server":
        asyncio.run(messaging.start_services())
    elif args.mode == "client" and args.target and args.message:
        async def send_test_message():
            message_id = await messaging.send_message(
                args.target, 
                "test_message",
                {"content": args.message}
            )
            print(f"Sent message: {message_id}")
        asyncio.run(send_test_message())

if __name__ == "__main__":
    main()