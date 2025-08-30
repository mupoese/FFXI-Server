#!/usr/bin/env python3
"""
LandSandBoat Web Administration Panel
Comprehensive web interface for server administration and user management
"""

import json
import os
import sqlite3
import datetime
import hashlib
import secrets
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

try:
    from flask import Flask, render_template_string, jsonify, request, Response, session, redirect, url_for, flash
    import mysql.connector
    import psutil
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Missing required dependency: {e}")
    if __name__ == "__main__":
        print("Install with: pip install flask mysql-connector-python psutil")
        exit(1)
    DEPENDENCIES_AVAILABLE = False

if DEPENDENCIES_AVAILABLE:
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)  # Generate secure secret key
else:
    app = None

class WebAdminPanel:
    """Enhanced Web-based administration panel for LandSandBoat"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.setup_routes()
        
    def load_config(self) -> dict:
        """Load configuration for web admin panel"""
        default_config = {
            "database": {
                "host": "localhost",
                "port": 3306,
                "database": "xidb", 
                "user": "root",
                "password": ""
            },
            "monitoring": {
                "refresh_interval": 2,
                "alert_thresholds": {
                    "cpu_percent": 80,
                    "memory_percent": 85,
                    "disk_percent": 90
                }
            },
            "user_management": {
                "max_characters_per_user": 2,
                "require_approval": True,
                "admin_email": "admin@landsandboat.local"
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            else:
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            
        return default_config
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @app.route('/')
        def login_page():
            """User login page"""
            if 'user_id' in session:
                user_type = session.get('user_type', 'user')
                if user_type in ['admin', 'moderator']:
                    return redirect('/admin')
                else:
                    return redirect('/portal')
            
            return render_template_string(LOGIN_TEMPLATE, 
                                        page_type='login', 
                                        page_title='Player Login')
        
        @app.route('/register')
        def register_page():
            """User registration page"""
            return render_template_string(LOGIN_TEMPLATE, 
                                        page_type='register', 
                                        page_title='Create Account')
        
        @app.route('/register', methods=['POST'])
        def handle_registration():
            """Handle user registration"""
            try:
                email = request.form['email']
                username = request.form['username']
                password = request.form['password']
                confirm_password = request.form['confirm_password']
                
                if password != confirm_password:
                    return render_template_string(LOGIN_TEMPLATE, 
                                                page_type='register',
                                                page_title='Create Account',
                                                error='Passwords do not match')
                
                # Hash password
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # Check if user exists
                conn = self.get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute("SELECT id FROM accounts WHERE login = %s OR current_email = %s", 
                             (username, email))
                if cursor.fetchone():
                    return render_template_string(LOGIN_TEMPLATE, 
                                                page_type='register',
                                                page_title='Create Account',
                                                error='Username or email already exists')
                
                # Create account with pending status
                status = 0 if self.config['user_management']['require_approval'] else 1
                
                # Get next account ID
                cursor.execute("SELECT MAX(id) FROM accounts")
                max_id = cursor.fetchone()[0] or 0
                new_id = max_id + 1
                
                cursor.execute("""
                    INSERT INTO accounts (id, login, password, current_email, registration_email, 
                                        timecreate, status, priv, content_ids)
                    VALUES (%s, %s, %s, %s, %s, NOW(), %s, 1, %s)
                """, (new_id, username, password_hash, email, email, status, 
                     self.config['user_management']['max_characters_per_user']))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                if status == 0:
                    return render_template_string(LOGIN_TEMPLATE, 
                                                page_type='register',
                                                page_title='Create Account',
                                                success='Registration successful! Please wait for admin approval.')
                else:
                    return render_template_string(LOGIN_TEMPLATE, 
                                                page_type='login',
                                                page_title='Player Login',
                                                success='Registration successful! You can now login.')
                    
            except Exception as e:
                return render_template_string(LOGIN_TEMPLATE, 
                                            page_type='register',
                                            page_title='Create Account',
                                            error=f'Registration error: {str(e)}')
        
        @app.route('/', methods=['POST'])
        def handle_login():
            """Handle user login"""
            try:
                username = request.form['username']
                password = request.form['password']
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                conn = self.get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, login, status, priv 
                    FROM accounts 
                    WHERE login = %s AND password = %s
                """, (username, password_hash))
                
                user = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if not user:
                    return render_template_string(LOGIN_TEMPLATE, 
                                                page_type='login',
                                                page_title='Player Login',
                                                error='Invalid username or password')
                
                user_id, login, status, priv = user
                
                if status == 0:
                    return render_template_string(LOGIN_TEMPLATE, 
                                                page_type='login',
                                                page_title='Player Login',
                                                error='Account pending approval')
                
                # Set session
                session['user_id'] = user_id
                session['username'] = login
                
                if priv >= 3:  # Admin level
                    session['user_type'] = 'admin'
                    return redirect('/admin')
                elif priv == 2:  # Moderator level
                    session['user_type'] = 'moderator'
                    return redirect('/admin')
                else:  # Regular user
                    session['user_type'] = 'user'
                    return redirect('/portal')
                    
            except Exception as e:
                return render_template_string(LOGIN_TEMPLATE, 
                                            page_type='login',
                                            page_title='Player Login',
                                            error=f'Login error: {str(e)}')
        
        @app.route('/admin')
        def admin_panel():
            """Admin panel - requires admin or moderator privileges"""
            if 'user_id' not in session or session.get('user_type') not in ['admin', 'moderator']:
                return redirect('/')
            return render_template_string(ADMIN_TEMPLATE, session=session)
        
        @app.route('/portal')
        def user_portal():
            """User portal for registered players"""
            if 'user_id' not in session:
                return redirect('/')
            return render_template_string(USER_PORTAL_TEMPLATE, session=session)
        
        @app.route('/logout')
        def logout():
            """Logout user"""
            session.clear()
            return redirect('/')
        
        # API Routes
        @app.route('/api/status')
        def api_status():
            """Get current system status as JSON"""
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # Database info
                db_info = self.get_database_info()
                
                # Server process info
                servers = self.get_server_info()
                
                return jsonify({
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent,
                    'network': {
                        'bytes_recv': self.format_bytes(network.bytes_recv),
                        'bytes_sent': self.format_bytes(network.bytes_sent)
                    },
                    'database': db_info,
                    'servers': servers,
                    'timestamp': datetime.datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/users')
        def api_users():
            """Get users for management"""
            if session.get('user_type') not in ['admin', 'moderator']:
                return jsonify({'error': 'Unauthorized'}), 403
                
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT a.id, a.login, a.current_email, a.timecreate, a.status,
                           COUNT(c.charid) as character_count
                    FROM accounts a
                    LEFT JOIN chars c ON a.id = c.accid
                    GROUP BY a.id
                    ORDER BY a.timecreate DESC
                """)
                
                users = []
                for row in cursor.fetchall():
                    status_map = {0: 'pending', 1: 'active', 2: 'banned'}
                    users.append({
                        'id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'registration_date': row[3].isoformat() if row[3] else None,
                        'status': status_map.get(row[4], 'unknown'),
                        'character_count': row[5] or 0
                    })
                
                cursor.close()
                conn.close()
                
                return jsonify({'users': users})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/characters')
        def api_characters():
            """Get characters for management"""
            if session.get('user_type') not in ['admin', 'moderator']:
                return jsonify({'error': 'Unauthorized'}), 403
                
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT c.charid, c.charname, a.login, c.pos_zone, c.last_logout, c.gmlevel,
                           j.job_level, j.job
                    FROM chars c
                    JOIN accounts a ON c.accid = a.id
                    LEFT JOIN char_jobs j ON c.charid = j.charid AND j.job = (
                        SELECT job FROM char_jobs WHERE charid = c.charid ORDER BY job_level DESC LIMIT 1
                    )
                    ORDER BY c.last_logout DESC
                """)
                
                characters = []
                for row in cursor.fetchall():
                    characters.append({
                        'id': row[0],
                        'name': row[1],
                        'account': row[2],
                        'zone': row[3] or 'Unknown',
                        'last_login': row[4].isoformat() if row[4] else None,
                        'gm_level': row[5] or 0,
                        'level': row[6] or 1,
                        'job': row[7] or 'WAR'
                    })
                
                cursor.close()
                conn.close()
                
                return jsonify({'characters': characters})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/gamedata')
        def api_gamedata():
            """Get real-time game data"""
            try:
                # Calculate Vana'diel time
                vanadiel_date = self.get_vanadiel_date()
                elemental_day = self.get_elemental_day()
                moon_phase = self.get_moon_phase()
                
                # Get auction house data
                conn = self.get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM auction_house WHERE sale = 0")
                active_listings = cursor.fetchone()[0] or 0
                
                cursor.execute("""
                    SELECT COUNT(*) FROM auction_house 
                    WHERE sale = 1 AND sell_date >= CURDATE()
                """)
                sales_today = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT SUM(price) FROM auction_house WHERE sale = 0")
                total_gil = cursor.fetchone()[0] or 0
                
                # Get zone population
                cursor.execute("""
                    SELECT pos_zone, COUNT(*) as population
                    FROM chars 
                    WHERE last_logout > DATE_SUB(NOW(), INTERVAL 1 HOUR)
                    GROUP BY pos_zone
                    ORDER BY population DESC
                    LIMIT 10
                """)
                zone_population = [{'name': f'Zone {row[0]}', 'population': row[1]} for row in cursor.fetchall()]
                
                # Get players online count
                cursor.execute("""
                    SELECT COUNT(*) FROM chars 
                    WHERE last_logout > DATE_SUB(NOW(), INTERVAL 30 MINUTE)
                """)
                players_online = cursor.fetchone()[0] or 0
                
                cursor.close()
                conn.close()
                
                return jsonify({
                    'vanadiel_date': vanadiel_date,
                    'elemental_day': elemental_day,
                    'moon_phase': moon_phase,
                    'uptime': self.get_server_uptime(),
                    'players_online': players_online,
                    'auction_house': {
                        'active_listings': active_listings,
                        'sales_today': sales_today,
                        'total_gil': self.format_gil(total_gil)
                    },
                    'zone_population': zone_population
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/users/approve', methods=['POST'])
        def api_approve_user():
            """Approve a user registration"""
            if session.get('user_type') not in ['admin', 'moderator']:
                return jsonify({'error': 'Unauthorized'}), 403
                
            try:
                user_id = request.json.get('user_id')
                
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE accounts SET status = 1 WHERE id = %s", (user_id,))
                conn.commit()
                cursor.close()
                conn.close()
                
                return jsonify({'success': True, 'message': 'User approved successfully'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @app.route('/api/users/reject', methods=['POST'])
        def api_reject_user():
            """Reject a user registration"""
            if session.get('user_type') not in ['admin']:
                return jsonify({'error': 'Unauthorized'}), 403
                
            try:
                user_id = request.json.get('user_id')
                
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM accounts WHERE id = %s AND status = 0", (user_id,))
                conn.commit()
                cursor.close()
                conn.close()
                
                return jsonify({'success': True, 'message': 'User registration rejected'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @app.route('/api/user/characters')
        def api_user_characters():
            """Get current user's characters"""
            if 'user_id' not in session:
                return jsonify({'error': 'Unauthorized'}), 403
                
            try:
                user_id = session['user_id']
                conn = self.get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT c.charid, c.charname, c.pos_zone, c.last_logout, c.playtime,
                           j.job_level, j.job
                    FROM chars c
                    LEFT JOIN char_jobs j ON c.charid = j.charid AND j.job = (
                        SELECT job FROM char_jobs WHERE charid = c.charid ORDER BY job_level DESC LIMIT 1
                    )
                    WHERE c.accid = %s
                    ORDER BY c.timecreated DESC
                """, (user_id,))
                
                characters = []
                for row in cursor.fetchall():
                    characters.append({
                        'id': row[0],
                        'name': row[1],
                        'zone': row[2] or 'Unknown',
                        'last_login': row[3].isoformat() if row[3] else None,
                        'playtime': self.format_playtime(row[4] or 0),
                        'level': row[5] or 1,
                        'job': row[6] or 'WAR'
                    })
                
                cursor.close()
                conn.close()
                
                return jsonify({'characters': characters})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/user/character/<int:char_id>/inventory')
        def api_character_inventory(char_id):
            """Get character inventory"""
            if 'user_id' not in session:
                return jsonify({'error': 'Unauthorized'}), 403
                
            try:
                user_id = session['user_id']
                conn = self.get_db_connection()
                cursor = conn.cursor()
                
                # Verify character belongs to user
                cursor.execute("SELECT charid FROM chars WHERE charid = %s AND accid = %s", 
                             (char_id, user_id))
                if not cursor.fetchone():
                    return jsonify({'error': 'Character not found'}), 404
                
                cursor.execute("""
                    SELECT i.slot, i.quantity, ib.name
                    FROM char_inventory i
                    JOIN item_basic ib ON i.itemid = ib.itemid
                    WHERE i.charid = %s AND i.location = 0
                    ORDER BY i.slot
                """, (char_id,))
                
                inventory = []
                for row in cursor.fetchall():
                    inventory.append({
                        'slot': row[0],
                        'quantity': row[1],
                        'name': row[2]
                    })
                
                cursor.close()
                conn.close()
                
                return jsonify({'inventory': inventory})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def get_db_connection(self):
        """Get database connection"""
        return mysql.connector.connect(
            host=self.config['database']['host'],
            port=self.config['database']['port'],
            database=self.config['database']['database'],
            user=self.config['database']['user'],
            password=self.config['database']['password']
        )
    
    def get_database_info(self) -> dict:
        """Get database information"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Online players (characters logged in within last 30 minutes)
            cursor.execute("""
                SELECT COUNT(*) FROM chars 
                WHERE last_logout > DATE_SUB(NOW(), INTERVAL 30 MINUTE)
            """)
            online_players = cursor.fetchone()[0]
            
            # Total characters
            cursor.execute("SELECT COUNT(*) FROM chars")
            total_characters = cursor.fetchone()[0]
            
            # Pending registrations
            cursor.execute("SELECT COUNT(*) FROM accounts WHERE status = 0")
            pending_registrations = cursor.fetchone()[0]
            
            # Database connections
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            connections = cursor.fetchone()[1] if cursor.fetchone() else 0
            
            cursor.close()
            conn.close()
            
            return {
                'online_players': online_players,
                'total_characters': total_characters,
                'pending_registrations': pending_registrations,
                'connections': connections
            }
        except Exception as e:
            return {
                'online_players': 0,
                'total_characters': 0,
                'pending_registrations': 0,
                'connections': 0,
                'error': str(e)
            }
    
    def get_server_info(self) -> List[Dict[str, Any]]:
        """Get information about server processes"""
        servers = []
        server_names = ['xi_map', 'xi_login', 'xi_search']
        
        for server_name in server_names:
            status = 'stopped'
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if server_name in proc.info['name']:
                        status = 'running'
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            servers.append({
                'name': server_name,
                'status': status
            })
        
        return servers
    
    def get_vanadiel_date(self) -> str:
        """Calculate current Vana'diel date"""
        # Vana'diel time calculation (simplified)
        # Real time: 1 second = 1 Vana'diel minute
        # 1 Vana'diel day = 57 minutes 36 seconds real time
        unix_timestamp = time.time()
        vanadiel_timestamp = unix_timestamp * 25  # Vana'diel time moves 25x faster
        
        vanadiel_date = datetime.datetime.fromtimestamp(vanadiel_timestamp % (365 * 24 * 60 * 60 * 25))
        return vanadiel_date.strftime("%Y-%m-%d %H:%M")
    
    def get_elemental_day(self) -> str:
        """Get current elemental day"""
        days = ['Firesday', 'Earthsday', 'Watersday', 'Windsday', 'Iceday', 'Lightningsday', 'Lightsday', 'Darksday']
        day_index = int(time.time() / (57.6 * 60)) % 8  # 8-day cycle
        return days[day_index]
    
    def get_moon_phase(self) -> str:
        """Get current moon phase"""
        phases = ['New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous', 
                 'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent']
        phase_index = int(time.time() / (84 * 60)) % 8  # Moon cycle
        return phases[phase_index]
    
    def get_server_uptime(self) -> str:
        """Get server uptime"""
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_delta = datetime.timedelta(seconds=uptime_seconds)
            return str(uptime_delta).split('.')[0]  # Remove microseconds
        except:
            return "Unknown"
    
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def format_gil(self, gil_amount: int) -> str:
        """Format gil amount"""
        if gil_amount >= 1000000:
            return f"{gil_amount/1000000:.1f}M"
        elif gil_amount >= 1000:
            return f"{gil_amount/1000:.1f}K"
        else:
            return str(gil_amount)
    
    def format_playtime(self, seconds: int) -> str:
        """Format playtime in seconds to readable format"""
        hours = seconds // 3600
        return f"{hours} hours"
    
    def run(self, host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
        """Start the web admin panel"""
        print(f"Starting LandSandBoat Web Admin Panel on {host}:{port}")
        print(f"Admin panel: http://{host}:{port}/admin")
        print(f"User portal: http://{host}:{port}/portal")
        app.run(host=host, port=port, debug=debug)

# Templates (defined outside the class for clarity)
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LandSandBoat - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: linear-gradient(135deg, #1a1a1a, #2d2d2d); color: #fff; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: #2d2d2d; padding: 3rem; border-radius: 12px; border: 1px solid #444; box-shadow: 0 10px 30px rgba(0,0,0,0.5); max-width: 400px; width: 100%; }
        .login-header { text-align: center; margin-bottom: 2rem; }
        .login-header h1 { color: #4a90e2; margin-bottom: 0.5rem; }
        .login-header p { color: #ccc; }
        .form-group { margin-bottom: 1.5rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; color: #ccc; }
        .form-group input { width: 100%; padding: 0.75rem; border: 1px solid #555; border-radius: 6px; background: #1a1a1a; color: #fff; font-size: 1rem; }
        .form-group input:focus { outline: none; border-color: #4a90e2; }
        .btn { width: 100%; background: #4a90e2; color: white; border: none; padding: 1rem; border-radius: 6px; cursor: pointer; font-size: 1rem; margin-bottom: 1rem; }
        .btn:hover { background: #357abd; }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #5a6268; }
        .alert { padding: 1rem; border-radius: 6px; margin-bottom: 1rem; }
        .alert-error { background: #e74c3c; color: white; }
        .alert-success { background: #27ae60; color: white; }
        .text-center { text-align: center; }
        .text-link { color: #4a90e2; text-decoration: none; }
        .text-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>🎮 LandSandBoat</h1>
            <p>{{ page_title }}</p>
        </div>
        
        {% if error %}
        <div class="alert alert-error">{{ error }}</div>
        {% endif %}
        
        {% if success %}
        <div class="alert alert-success">{{ success }}</div>
        {% endif %}
        
        <form method="POST">
            {% if page_type == 'register' %}
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required maxlength="16">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="form-group">
                <label for="confirm_password">Confirm Password</label>
                <input type="password" id="confirm_password" name="confirm_password" required>
            </div>
            <button type="submit" class="btn">Register Account</button>
            <div class="text-center">
                <a href="/" class="text-link">Already have an account? Login here</a>
            </div>
            {% else %}
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login</button>
            <a href="/register" class="btn btn-secondary">Create New Account</a>
            <div class="text-center" style="margin-top: 1rem;">
                <a href="/admin" class="text-link">Admin Panel</a>
            </div>
            {% endif %}
        </form>
    </div>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LandSandBoat Admin Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #1a1a1a; color: #fff; }
        .header { background: #2d2d2d; padding: 1rem; border-bottom: 2px solid #4a90e2; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { color: #4a90e2; }
        .header .nav a { color: #fff; text-decoration: none; margin-left: 1rem; padding: 0.5rem 1rem; border-radius: 4px; background: #4a90e2; }
        .header .nav a:hover { background: #357abd; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .tabs { display: flex; border-bottom: 1px solid #444; margin-bottom: 2rem; }
        .tab { padding: 1rem 2rem; cursor: pointer; border-bottom: 2px solid transparent; }
        .tab.active { border-bottom-color: #4a90e2; background: #2d2d2d; }
        .tab:hover { background: #2d2d2d; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-bottom: 2rem; }
        .card { background: #2d2d2d; padding: 1.5rem; border-radius: 8px; border: 1px solid #444; }
        .card h3 { color: #4a90e2; margin-bottom: 1rem; }
        .metric { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
        .metric-value { font-weight: bold; }
        .btn { background: #4a90e2; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; margin: 0.2rem; }
        .btn:hover { background: #357abd; }
        .btn-success { background: #27ae60; }
        .btn-danger { background: #e74c3c; }
        .table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        .table th, .table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #444; }
        .table th { background: #2d2d2d; }
        .table tr:hover { background: #2d2d2d; }
        .status-pending { background: #f39c12; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
        .status-active { background: #27ae60; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
        .status-banned { background: #e74c3c; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
        .form-inline { display: flex; gap: 1rem; align-items: center; margin-bottom: 1rem; }
        .form-inline input, .form-inline select { padding: 0.5rem; border: 1px solid #555; border-radius: 4px; background: #1a1a1a; color: #fff; }
        .alert { padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .alert-success { background: #27ae60; color: white; }
        .alert-error { background: #e74c3c; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎮 LandSandBoat Administration</h1>
        <div class="nav">
            <span>{{ session.get('user_type').title() }}: {{ session.get('username') }}</span>
            <a href="/logout">Logout</a>
        </div>
    </div>

    <div class="container">
        <div id="alerts-container"></div>

        <div class="tabs">
            <div class="tab active" onclick="showTab('dashboard')">Dashboard</div>
            <div class="tab" onclick="showTab('users')">User Management</div>
            <div class="tab" onclick="showTab('characters')">Characters</div>
            <div class="tab" onclick="showTab('gamedata')">Game Data</div>
        </div>

        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <div class="grid">
                <div class="card">
                    <h3>System Metrics</h3>
                    <div class="metric">
                        <span>CPU Usage:</span>
                        <span id="cpu-usage" class="metric-value">--</span>
                    </div>
                    <div class="metric">
                        <span>Memory Usage:</span>
                        <span id="memory-usage" class="metric-value">--</span>
                    </div>
                    <div class="metric">
                        <span>Disk Usage:</span>
                        <span id="disk-usage" class="metric-value">--</span>
                    </div>
                </div>

                <div class="card">
                    <h3>Database Info</h3>
                    <div class="metric">
                        <span>Online Players:</span>
                        <span id="online-players" class="metric-value">--</span>
                    </div>
                    <div class="metric">
                        <span>Total Characters:</span>
                        <span id="total-characters" class="metric-value">--</span>
                    </div>
                    <div class="metric">
                        <span>Pending Registrations:</span>
                        <span id="pending-registrations" class="metric-value">--</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- User Management Tab -->
        <div id="users" class="tab-content">
            <div class="card">
                <h3>User Registration Requests</h3>
                <table class="table" id="users-table">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Registration Date</th>
                            <th>Status</th>
                            <th>Characters</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="users-tbody">
                        <tr><td colspan="6">Loading users...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Characters Tab -->
        <div id="characters" class="tab-content">
            <div class="card">
                <h3>Character Management</h3>
                <table class="table" id="characters-table">
                    <thead>
                        <tr>
                            <th>Character Name</th>
                            <th>Account</th>
                            <th>Level</th>
                            <th>Zone</th>
                            <th>Last Login</th>
                            <th>GM Level</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="characters-tbody">
                        <tr><td colspan="7">Loading characters...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Game Data Tab -->
        <div id="gamedata" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h3>Real-time Game Information</h3>
                    <div class="metric">
                        <span>Current Vana'diel Date:</span>
                        <span id="vanadiel-date" class="metric-value">--</span>
                    </div>
                    <div class="metric">
                        <span>Elemental Day:</span>
                        <span id="elemental-day" class="metric-value">--</span>
                    </div>
                    <div class="metric">
                        <span>Moon Phase:</span>
                        <span id="moon-phase" class="metric-value">--</span>
                    </div>
                </div>

                <div class="card">
                    <h3>Auction House Activity</h3>
                    <div class="metric">
                        <span>Active Listings:</span>
                        <span id="ah-listings" class="metric-value">--</span>
                    </div>
                    <div class="metric">
                        <span>Sales Today:</span>
                        <span id="ah-sales-today" class="metric-value">--</span>
                    </div>
                    <div class="metric">
                        <span>Total Gil in AH:</span>
                        <span id="ah-total-gil" class="metric-value">--</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'users') loadUsers();
            else if (tabName === 'characters') loadCharacters();
            else if (tabName === 'gamedata') loadGameData();
        }

        function loadUsers() {
            fetch('/api/users')
                .then(response => response.json())
                .then(data => {
                    const tbody = document.getElementById('users-tbody');
                    tbody.innerHTML = '';
                    data.users.forEach(user => {
                        const row = `
                            <tr>
                                <td>${user.username}</td>
                                <td>${user.email}</td>
                                <td>${new Date(user.registration_date).toLocaleDateString()}</td>
                                <td><span class="status-${user.status}">${user.status}</span></td>
                                <td>${user.character_count}/2</td>
                                <td>
                                    ${user.status === 'pending' ? 
                                        `<button class="btn btn-success" onclick="approveUser(${user.id})">Approve</button>
                                         <button class="btn btn-danger" onclick="rejectUser(${user.id})">Reject</button>` :
                                        `<button class="btn" onclick="editUser(${user.id})">Edit</button>`
                                    }
                                </td>
                            </tr>
                        `;
                        tbody.innerHTML += row;
                    });
                })
                .catch(error => console.error('Error loading users:', error));
        }

        function loadCharacters() {
            fetch('/api/characters')
                .then(response => response.json())
                .then(data => {
                    const tbody = document.getElementById('characters-tbody');
                    tbody.innerHTML = '';
                    data.characters.forEach(char => {
                        const row = `
                            <tr>
                                <td>${char.name}</td>
                                <td>${char.account}</td>
                                <td>${char.level}</td>
                                <td>${char.zone}</td>
                                <td>${new Date(char.last_login).toLocaleDateString()}</td>
                                <td>${char.gm_level}</td>
                                <td>
                                    <button class="btn" onclick="viewCharacter(${char.id})">View</button>
                                </td>
                            </tr>
                        `;
                        tbody.innerHTML += row;
                    });
                })
                .catch(error => console.error('Error loading characters:', error));
        }

        function loadGameData() {
            fetch('/api/gamedata')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('vanadiel-date').textContent = data.vanadiel_date;
                    document.getElementById('elemental-day').textContent = data.elemental_day;
                    document.getElementById('moon-phase').textContent = data.moon_phase;
                    document.getElementById('ah-listings').textContent = data.auction_house.active_listings;
                    document.getElementById('ah-sales-today').textContent = data.auction_house.sales_today;
                    document.getElementById('ah-total-gil').textContent = data.auction_house.total_gil;
                })
                .catch(error => console.error('Error loading game data:', error));
        }

        function approveUser(userId) {
            fetch('/api/users/approve', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user_id: userId})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('User approved successfully', 'success');
                    loadUsers();
                } else {
                    showAlert('Error approving user: ' + data.error, 'error');
                }
            });
        }

        function rejectUser(userId) {
            if (confirm('Are you sure you want to reject this user registration?')) {
                fetch('/api/users/reject', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: userId})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('User rejected successfully', 'success');
                        loadUsers();
                    } else {
                        showAlert('Error rejecting user: ' + data.error, 'error');
                    }
                });
            }
        }

        function showAlert(message, type) {
            const container = document.getElementById('alerts-container');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            container.appendChild(alert);
            setTimeout(() => container.removeChild(alert), 5000);
        }

        function loadDashboardData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cpu-usage').textContent = data.cpu_percent + '%';
                    document.getElementById('memory-usage').textContent = data.memory_percent + '%';
                    document.getElementById('online-players').textContent = data.database.online_players;
                    document.getElementById('total-characters').textContent = data.database.total_characters;
                    document.getElementById('pending-registrations').textContent = data.database.pending_registrations;
                })
                .catch(error => console.error('Error loading status:', error));
        }

        document.addEventListener('DOMContentLoaded', function() {
            loadDashboardData();
            setInterval(loadDashboardData, 10000);
        });
    </script>
</body>
</html>
"""

USER_PORTAL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LandSandBoat - Player Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #1a1a1a; color: #fff; }
        .header { background: #2d2d2d; padding: 1rem; border-bottom: 2px solid #4a90e2; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { color: #4a90e2; }
        .header .nav a { color: #fff; text-decoration: none; margin-left: 1rem; padding: 0.5rem 1rem; border-radius: 4px; background: #4a90e2; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-bottom: 2rem; }
        .card { background: #2d2d2d; padding: 1.5rem; border-radius: 8px; border: 1px solid #444; }
        .card h3 { color: #4a90e2; margin-bottom: 1rem; }
        .character-list { list-style: none; }
        .character-item { background: #1a1a1a; padding: 1rem; margin: 0.5rem 0; border-radius: 4px; cursor: pointer; }
        .character-item:hover { background: #333; }
        .character-name { font-weight: bold; color: #4a90e2; }
        .character-details { margin-top: 0.5rem; color: #ccc; }
        .metric { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
        .metric-value { font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎮 LandSandBoat Player Portal</h1>
        <div class="nav">
            <span>Welcome, {{ session.get('username') }}</span>
            <a href="/logout">Logout</a>
        </div>
    </div>

    <div class="container">
        <div class="grid">
            <div class="card">
                <h3>Your Characters</h3>
                <ul id="character-list" class="character-list">
                    <li>Loading characters...</li>
                </ul>
            </div>

            <div class="card">
                <h3>Game Information</h3>
                <div class="metric">
                    <span>Vana'diel Date:</span>
                    <span id="vanadiel-date" class="metric-value">--</span>
                </div>
                <div class="metric">
                    <span>Elemental Day:</span>
                    <span id="elemental-day" class="metric-value">--</span>
                </div>
                <div class="metric">
                    <span>Moon Phase:</span>
                    <span id="moon-phase" class="metric-value">--</span>
                </div>
                <div class="metric">
                    <span>Players Online:</span>
                    <span id="players-online" class="metric-value">--</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        function loadUserData() {
            fetch('/api/user/characters')
                .then(response => response.json())
                .then(data => {
                    const list = document.getElementById('character-list');
                    list.innerHTML = '';
                    data.characters.forEach(char => {
                        const item = document.createElement('li');
                        item.className = 'character-item';
                        item.innerHTML = `
                            <div class="character-name">${char.name}</div>
                            <div class="character-details">
                                Level ${char.level} ${char.job} - ${char.zone}<br>
                                Last Login: ${new Date(char.last_login).toLocaleDateString()}
                            </div>
                        `;
                        list.appendChild(item);
                    });
                });

            fetch('/api/gamedata')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('vanadiel-date').textContent = data.vanadiel_date;
                    document.getElementById('elemental-day').textContent = data.elemental_day;
                    document.getElementById('moon-phase').textContent = data.moon_phase;
                    document.getElementById('players-online').textContent = data.players_online;
                });
        }

        document.addEventListener('DOMContentLoaded', function() {
            loadUserData();
            setInterval(loadUserData, 30000);
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LandSandBoat Web Administration Panel")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--config", default="config.json", help="Configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    admin_panel = WebAdminPanel(args.config)
    admin_panel.run(host=args.host, port=args.port, debug=args.debug)