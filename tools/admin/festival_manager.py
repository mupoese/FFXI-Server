#!/usr/bin/env python3
"""
Festival Management System
Automated festival announcements and management integration
"""

import json
import sqlite3
import time
import datetime
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

class FestivalManager:
    """Automated festival management with Japanese time synchronization"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.db_path = self.config.get('database_path', 'festival_management.db')
        self._init_database()
        
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'database_path': 'festival_management.db',
            'announcement_interval': 300,  # 5 minutes
            'website_update_url': 'http://localhost:8080/api/festivals/update',
            'server_announcement_command': 'tools/admin/announce.py',
            'enabled_festivals': [
                'new_year', 'valentines', 'white_day', 'golden_week', 
                'summer_festival', 'harvest_festival', 'starlight_celebration'
            ],
            'auto_announce': True,
            'auto_website_update': True,
            'timezone': 'Asia/Tokyo'
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
        
        return default_config
    
    def _init_database(self):
        """Initialize festival management database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Festival tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS festival_status (
                    festival_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    currently_active BOOLEAN DEFAULT FALSE,
                    last_start_announcement TIMESTAMP,
                    last_end_announcement TIMESTAMP,
                    announcement_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Festival logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS festival_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    festival_id TEXT NOT NULL,
                    event_type TEXT NOT NULL, -- 'start', 'end', 'announcement'
                    message TEXT,
                    japanese_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Website announcements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS website_announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    festival_id TEXT,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    announcement_type TEXT NOT NULL, -- 'festival_start', 'festival_end', 'reminder'
                    active BOOLEAN DEFAULT TRUE,
                    priority INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Festival management database initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            sys.exit(1)
    
    def get_japanese_time(self) -> datetime.datetime:
        """Get current Japanese Standard Time"""
        import pytz
        jst = pytz.timezone('Asia/Tokyo')
        return datetime.datetime.now(jst)
    
    def get_active_festivals(self) -> List[Dict[str, Any]]:
        """Get currently active festivals based on Japanese time"""
        jst_time = self.get_japanese_time()
        current_month = jst_time.month
        current_day = jst_time.day
        
        festivals = [
            {
                'id': 'new_year',
                'name': "New Year's Celebration", 
                'icon': '🎆',
                'start_month': 1, 'start_day': 1,
                'end_month': 1, 'end_day': 15,
                'start_message': "🎆 New Year's Celebration has begun! Welcome to a new year in Vana'diel!",
                'end_message': "🎆 New Year's Celebration has ended. Thank you for celebrating with us!"
            },
            {
                'id': 'valentines',
                'name': "Valentine's Day",
                'icon': '💝', 
                'start_month': 2, 'start_day': 10,
                'end_month': 2, 'end_day': 20,
                'start_message': "💝 Valentine's Day event has started! Spread love throughout Vana'diel!",
                'end_message': "💝 Valentine's Day event has ended. Until next year, adventurers!"
            },
            {
                'id': 'white_day',
                'name': 'White Day',
                'icon': '🤍',
                'start_month': 3, 'start_day': 10, 
                'end_month': 3, 'end_day': 20,
                'start_message': "🤍 White Day has arrived! Time to return the kindness!",
                'end_message': "🤍 White Day has concluded. See you next year!"
            },
            {
                'id': 'golden_week',
                'name': 'Golden Week',
                'icon': '🏅',
                'start_month': 4, 'start_day': 29,
                'end_month': 5, 'end_day': 5,
                'start_message': "🏅 Golden Week celebration begins! Enjoy the festivities!",
                'end_message': "🏅 Golden Week has ended. Thank you for participating!"
            },
            {
                'id': 'summer_festival',
                'name': 'Summer Festival',
                'icon': '🎆',
                'start_month': 7, 'start_day': 15,
                'end_month': 8, 'end_day': 31,
                'start_message': "🎆 Summer Festival is here! Enjoy fireworks and summer fun!",
                'end_message': "🎆 Summer Festival has ended. Autumn approaches in Vana'diel!"
            },
            {
                'id': 'harvest_festival',
                'name': 'Harvest Festival',
                'icon': '🎃',
                'start_month': 10, 'start_day': 20,
                'end_month': 11, 'end_day': 1,
                'start_message': "🎃 The Harvest Festival begins! Beware of things that go bump in the night!",
                'end_message': "🎃 The Harvest Festival has ended. The spirits return to rest!"
            },
            {
                'id': 'starlight_celebration',
                'name': 'Starlight Celebration',
                'icon': '⭐',
                'start_month': 12, 'start_day': 15,
                'end_month': 12, 'end_day': 31,
                'start_message': "⭐ The Starlight Celebration has begun! May your holidays be bright!",
                'end_message': "⭐ The Starlight Celebration has ended. Happy New Year approaches!"
            }
        ]
        
        active_festivals = []
        for festival in festivals:
            if festival['id'] not in self.config['enabled_festivals']:
                continue
                
            if self._is_festival_active(festival, current_month, current_day):
                active_festivals.append(festival)
        
        return active_festivals
    
    def _is_festival_active(self, festival: Dict[str, Any], month: int, day: int) -> bool:
        """Check if a festival is currently active"""
        start_month = festival['start_month']
        start_day = festival['start_day'] 
        end_month = festival['end_month']
        end_day = festival['end_day']
        
        if start_month == end_month:
            # Same month
            return month == start_month and start_day <= day <= end_day
        elif start_month < end_month:
            # Spans consecutive months in same year
            return ((month == start_month and day >= start_day) or
                    (month == end_month and day <= end_day) or
                    (start_month < month < end_month))
        else:
            # Spans year boundary
            return ((month == start_month and day >= start_day) or
                    (month == end_month and day <= end_day) or
                    (month > start_month) or
                    (month < end_month))
    
    def check_festival_changes(self) -> List[Dict[str, Any]]:
        """Check for festival status changes and handle announcements"""
        current_active = self.get_active_festivals()
        changes = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get previously known status
            cursor.execute('SELECT festival_id, currently_active FROM festival_status')
            previous_status = {row[0]: bool(row[1]) for row in cursor.fetchall()}
            
            # Check for newly started festivals
            for festival in current_active:
                festival_id = festival['id']
                was_active = previous_status.get(festival_id, False)
                
                if not was_active:
                    # Festival just started
                    changes.append({
                        'type': 'start',
                        'festival': festival,
                        'message': festival['start_message']
                    })
                    
                    if self.config['auto_announce']:
                        self._send_server_announcement(festival['start_message'])
                        self._log_festival_event(festival_id, 'start', festival['start_message'])
                    
                    if self.config['auto_website_update']:
                        self._update_website_announcement(festival, 'festival_start')
                
                # Update status
                cursor.execute('''
                    INSERT OR REPLACE INTO festival_status 
                    (festival_id, name, currently_active, updated_at) 
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (festival_id, festival['name'], True))
            
            # Check for ended festivals
            for festival_id, was_active in previous_status.items():
                if was_active:
                    # Check if still active
                    still_active = any(f['id'] == festival_id for f in current_active)
                    if not still_active:
                        # Festival just ended
                        festival_info = self._get_festival_info(festival_id)
                        if festival_info:
                            changes.append({
                                'type': 'end',
                                'festival': festival_info,
                                'message': festival_info['end_message']
                            })
                            
                            if self.config['auto_announce']:
                                self._send_server_announcement(festival_info['end_message'])
                                self._log_festival_event(festival_id, 'end', festival_info['end_message'])
                            
                            if self.config['auto_website_update']:
                                self._update_website_announcement(festival_info, 'festival_end')
                        
                        # Update status
                        cursor.execute('''
                            UPDATE festival_status 
                            SET currently_active = FALSE, updated_at = CURRENT_TIMESTAMP 
                            WHERE festival_id = ?
                        ''', (festival_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error checking festival changes: {e}")
        
        return changes
    
    def _get_festival_info(self, festival_id: str) -> Optional[Dict[str, Any]]:
        """Get festival information by ID"""
        all_festivals = [
            {'id': 'new_year', 'name': "New Year's Celebration", 'icon': '🎆', 'end_message': "🎆 New Year's Celebration has ended. Thank you for celebrating with us!"},
            {'id': 'valentines', 'name': "Valentine's Day", 'icon': '💝', 'end_message': "💝 Valentine's Day event has ended. Until next year, adventurers!"},
            {'id': 'white_day', 'name': 'White Day', 'icon': '🤍', 'end_message': "🤍 White Day has concluded. See you next year!"},
            {'id': 'golden_week', 'name': 'Golden Week', 'icon': '🏅', 'end_message': "🏅 Golden Week has ended. Thank you for participating!"},
            {'id': 'summer_festival', 'name': 'Summer Festival', 'icon': '🎆', 'end_message': "🎆 Summer Festival has ended. Autumn approaches in Vana'diel!"},
            {'id': 'harvest_festival', 'name': 'Harvest Festival', 'icon': '🎃', 'end_message': "🎃 The Harvest Festival has ended. The spirits return to rest!"},
            {'id': 'starlight_celebration', 'name': 'Starlight Celebration', 'icon': '⭐', 'end_message': "⭐ The Starlight Celebration has ended. Happy New Year approaches!"}
        ]
        
        for festival in all_festivals:
            if festival['id'] == festival_id:
                return festival
        return None
    
    def _send_server_announcement(self, message: str):
        """Send announcement to all online players"""
        try:
            announce_script = Path(self.config['server_announcement_command'])
            if announce_script.exists():
                import subprocess
                result = subprocess.run([
                    'python3', str(announce_script), '--message', message
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Server announcement sent: {message}")
                else:
                    print(f"⚠️ Announcement script returned error: {result.stderr}")
            else:
                print(f"⚠️ Announcement script not found: {announce_script}")
        
        except Exception as e:
            print(f"❌ Error sending server announcement: {e}")
    
    def _update_website_announcement(self, festival: Dict[str, Any], announcement_type: str):
        """Update website with festival announcement"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create website announcement
            if announcement_type == 'festival_start':
                title = f"{festival['icon']} {festival['name']} Active!"
                message = f"{festival['name']} is now active! Join the celebration in Vana'diel!"
                expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
            else:
                title = f"{festival['icon']} {festival['name']} Ended"
                message = f"{festival['name']} has concluded. Thank you for participating!"
                expires_at = datetime.datetime.now() + datetime.timedelta(days=7)
            
            cursor.execute('''
                INSERT INTO website_announcements 
                (festival_id, title, message, announcement_type, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (festival['id'], title, message, announcement_type, expires_at))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Website announcement created: {title}")
            
        except Exception as e:
            print(f"❌ Error updating website announcement: {e}")
    
    def _log_festival_event(self, festival_id: str, event_type: str, message: str):
        """Log festival event to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            jst_time = self.get_japanese_time()
            
            cursor.execute('''
                INSERT INTO festival_logs 
                (festival_id, event_type, message, japanese_time)
                VALUES (?, ?, ?, ?)
            ''', (festival_id, event_type, message, jst_time))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error logging festival event: {e}")
    
    def get_festival_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive festival status report"""
        jst_time = self.get_japanese_time()
        active_festivals = self.get_active_festivals()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent logs
            cursor.execute('''
                SELECT festival_id, event_type, message, japanese_time
                FROM festival_logs 
                ORDER BY created_at DESC 
                LIMIT 10
            ''')
            recent_logs = cursor.fetchall()
            
            # Get website announcements
            cursor.execute('''
                SELECT title, message, announcement_type, created_at
                FROM website_announcements 
                WHERE active = TRUE AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                ORDER BY priority DESC, created_at DESC
            ''')
            active_announcements = cursor.fetchall()
            
            conn.close()
            
            report = {
                'japanese_time': jst_time.isoformat(),
                'active_festivals': active_festivals,
                'active_festival_count': len(active_festivals),
                'recent_logs': recent_logs,
                'active_announcements': active_announcements,
                'next_check_in': self.config['announcement_interval']
            }
            
            return report
            
        except Exception as e:
            print(f"❌ Error generating status report: {e}")
            return {
                'japanese_time': jst_time.isoformat(),
                'active_festivals': active_festivals,
                'active_festival_count': len(active_festivals),
                'error': str(e)
            }
    
    def run_monitoring_loop(self):
        """Run continuous monitoring for festival changes"""
        print("🎆 Starting festival monitoring system...")
        print(f"Check interval: {self.config['announcement_interval']} seconds")
        print(f"Auto announcements: {self.config['auto_announce']}")
        print(f"Website updates: {self.config['auto_website_update']}")
        
        while True:
            try:
                print(f"\n⏰ Checking festivals at {self.get_japanese_time()}")
                changes = self.check_festival_changes()
                
                if changes:
                    print(f"✨ Festival changes detected: {len(changes)}")
                    for change in changes:
                        festival_name = change['festival']['name']
                        print(f"  {change['type'].upper()}: {festival_name}")
                else:
                    active_festivals = self.get_active_festivals()
                    print(f"📊 Status: {len(active_festivals)} active festivals")
                
                time.sleep(self.config['announcement_interval'])
                
            except KeyboardInterrupt:
                print("\n🛑 Festival monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FFXI Festival Management System")
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--monitor', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--check', action='store_true', help='Check for changes once')
    
    args = parser.parse_args()
    
    manager = FestivalManager(args.config)
    
    if args.monitor:
        manager.run_monitoring_loop()
    elif args.status:
        report = manager.get_festival_status_report()
        print(json.dumps(report, indent=2, default=str))
    elif args.check:
        changes = manager.check_festival_changes()
        if changes:
            print(f"Festival changes detected: {len(changes)}")
            for change in changes:
                print(f"  {change['type'].upper()}: {change['festival']['name']}")
        else:
            print("No festival changes detected")
    else:
        # Show help
        parser.print_help()

if __name__ == '__main__':
    main()