#!/usr/bin/env python3
"""
Test Web Administration Panel with SQLite for testing
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
    import psutil
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Missing required dependency: {e}")
    DEPENDENCIES_AVAILABLE = False

if DEPENDENCIES_AVAILABLE:
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)
else:
    app = None

class TestWebAdminPanel:
    """Test Web-based administration panel for LandSandBoat"""
    
    def __init__(self, db_file: str = "test_xidb.sqlite"):
        self.db_file = db_file
        self.config = self.load_config()
        self.setup_routes()
        
    def load_config(self) -> dict:
        """Load configuration for web admin panel"""
        return {
            "database": {
                "type": "sqlite",
                "file": self.db_file
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
        
    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_file)
        
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
                    WHERE login = ? AND password = ?
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
                session['user_type'] = 'admin' if priv >= 5 else 'moderator' if priv >= 3 else 'user'
                
                # Redirect based on user type
                if priv >= 3:  # Admin or moderator
                    return redirect('/admin')
                else:
                    return redirect('/portal')
                    
            except Exception as e:
                return render_template_string(LOGIN_TEMPLATE, 
                                            page_type='login',
                                            page_title='Player Login',
                                            error=f'Login error: {str(e)}')
        
        @app.route('/portal')
        def portal():
            """Player portal page"""
            if 'user_id' not in session:
                return redirect('/')
            
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                
                # Get user's characters
                cursor.execute("""
                    SELECT c.charid, c.charname, c.nation, c.pos_zone, c.playtime, c.gmlevel,
                           c.timecreated, c.last_logout
                    FROM chars c
                    WHERE c.accid = ?
                    ORDER BY c.timecreated
                """, (session['user_id'],))
                
                characters = cursor.fetchall()
                
                # Get character jobs for each character
                char_data = []
                for char in characters:
                    charid = char[0]
                    cursor.execute("""
                        SELECT job, level FROM char_jobs 
                        WHERE charid = ? AND level > 1 
                        ORDER BY level DESC LIMIT 3
                    """, (charid,))
                    jobs = cursor.fetchall()
                    
                    # Get inventory count
                    cursor.execute("""
                        SELECT COUNT(*) FROM char_inventory 
                        WHERE charid = ?
                    """, (charid,))
                    inventory_count = cursor.fetchone()[0]
                    
                    char_data.append({
                        'charid': char[0],
                        'charname': char[1],
                        'nation': ['San d\'Oria', 'Bastok', 'Windurst'][char[2]],
                        'zone': char[3],
                        'playtime': char[4],
                        'gmlevel': char[5],
                        'jobs': jobs,
                        'inventory_count': inventory_count,
                        'last_logout': char[7]
                    })
                
                # Get real-time game data
                game_data = self.get_game_data()
                
                cursor.close()
                conn.close()
                
                return render_template_string(PORTAL_TEMPLATE,
                                            characters=char_data,
                                            game_data=game_data,
                                            username=session['username'])
                
            except Exception as e:
                return f"Portal error: {str(e)}"
        
        @app.route('/admin')
        def admin():
            """Admin panel"""
            if 'user_id' not in session or session.get('user_type') not in ['admin', 'moderator']:
                return redirect('/')
            
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                
                # Get pending users
                cursor.execute("""
                    SELECT id, login, current_email, timecreate 
                    FROM accounts 
                    WHERE status = 0
                    ORDER BY timecreate DESC
                """)
                pending_users = cursor.fetchall()
                
                # Get all users
                cursor.execute("""
                    SELECT a.id, a.login, a.current_email, a.status, a.priv, a.timecreate,
                           COUNT(c.charid) as char_count
                    FROM accounts a
                    LEFT JOIN chars c ON a.id = c.accid
                    GROUP BY a.id
                    ORDER BY a.timecreate DESC
                """)
                all_users = cursor.fetchall()
                
                # Get all characters
                cursor.execute("""
                    SELECT c.charid, c.charname, c.pos_zone, c.gmlevel, c.last_logout,
                           a.login as account_name
                    FROM chars c
                    JOIN accounts a ON c.accid = a.id
                    ORDER BY c.last_logout DESC
                """)
                all_characters = cursor.fetchall()
                
                # Get system stats
                system_stats = {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent,
                    'total_accounts': len(all_users),
                    'pending_accounts': len(pending_users),
                    'total_characters': len(all_characters)
                }
                
                cursor.close()
                conn.close()
                
                return render_template_string(ADMIN_TEMPLATE,
                                            pending_users=pending_users,
                                            all_users=all_users,
                                            all_characters=all_characters,
                                            system_stats=system_stats,
                                            user_type=session.get('user_type'))
                
            except Exception as e:
                return f"Admin error: {str(e)}"
        
        @app.route('/api/approve_user/<int:user_id>')
        def approve_user(user_id):
            """Approve pending user"""
            if session.get('user_type') not in ['admin', 'moderator']:
                return jsonify({'error': 'Unauthorized'}), 403
            
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute("UPDATE accounts SET status = 1 WHERE id = ? AND status = 0", (user_id,))
                conn.commit()
                
                cursor.close()
                conn.close()
                
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/reject_user/<int:user_id>')
        def reject_user(user_id):
            """Reject pending user"""
            if session.get('user_type') not in ['admin', 'moderator']:
                return jsonify({'error': 'Unauthorized'}), 403
            
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM accounts WHERE id = ? AND status = 0", (user_id,))
                conn.commit()
                
                cursor.close()
                conn.close()
                
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/logout')
        def logout():
            """Logout user"""
            session.clear()
            return redirect('/')
    
    def get_game_data(self):
        """Get real-time game data"""
        # Calculate Vana'diel time
        earth_time = time.time()
        vana_time = earth_time * 25  # Vana'diel time moves 25x faster
        
        # Vana'diel epoch starts from midnight of Crystal Era
        vana_timestamp = int(vana_time) + 886 * 360 * 24 * 60 * 60  # Add Crystal Era years
        
        # Calculate date components
        vana_year = 886 + (vana_timestamp // (360 * 24 * 60 * 60))
        days_this_year = (vana_timestamp % (360 * 24 * 60 * 60)) // (24 * 60 * 60)
        
        # Elemental days cycle every 8 days
        elemental_days = ["Firesday", "Earthsday", "Watersday", "Windsday", 
                         "Iceday", "Lightningday", "Lightsday", "Darksday"]
        current_element_day = elemental_days[days_this_year % 8]
        
        # Moon phases cycle every 84 days (12 weeks)
        moon_phases = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
                      "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]
        moon_phase = moon_phases[(days_this_year % 84) // 10]
        
        # Get auction house data
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM auction_house")
            active_listings = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT AVG(price) FROM auction_house WHERE price > 0")
            avg_price = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT SUM(price) FROM auction_house WHERE price > 0")
            total_gil = cursor.fetchone()[0] or 0
            
            cursor.close()
            conn.close()
            
            auction_data = {
                'active_listings': active_listings,
                'average_price': int(avg_price) if avg_price else 0,
                'total_gil_circulation': int(total_gil) if total_gil else 0
            }
        except Exception:
            auction_data = {
                'active_listings': 0,
                'average_price': 0, 
                'total_gil_circulation': 0
            }
        
        return {
            'vana_year': int(vana_year),
            'vana_day': int(days_this_year % 30 + 1),  # Days 1-30 in month
            'vana_month': int((days_this_year % 360) // 30 + 1),  # Months 1-12
            'elemental_day': current_element_day,
            'moon_phase': moon_phase,
            'server_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'auction_house': auction_data
        }

# HTML Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ page_title }}</title>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 400px; margin: 50px auto; background: #2d2d2d; padding: 30px; border-radius: 8px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input { width: 100%; padding: 8px; background: #3d3d3d; border: 1px solid #555; color: #fff; border-radius: 4px; }
        button { width: 100%; padding: 10px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0052a3; }
        .error { color: #ff6b6b; margin-top: 10px; }
        .success { color: #51cf66; margin-top: 10px; }
        .link { color: #339af0; text-decoration: none; }
        .link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h2>{{ page_title }}</h2>
        
        {% if page_type == 'login' %}
        <form method="POST">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
        {% endif %}
        
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        {% if success %}<div class="success">{{ success }}</div>{% endif %}
        
        <p style="text-align: center; margin-top: 20px;">
            Test accounts:<br>
            Admin: admin / admin123<br>
            Moderator: moderator / mod123<br>
            User: testuser / user123<br>
            Pending: pendinguser / pending123
        </p>
    </div>
</body>
</html>
'''

PORTAL_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Player Portal</title>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: #fff; margin: 0; padding: 20px; }
        .header { background: #2d2d2d; padding: 15px; margin-bottom: 20px; border-radius: 8px; }
        .card { background: #2d2d2d; padding: 20px; margin-bottom: 20px; border-radius: 8px; }
        .character { border-left: 4px solid #0066cc; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .stat { background: #3d3d3d; padding: 10px; border-radius: 4px; }
        .logout { float: right; color: #ff6b6b; text-decoration: none; }
        .logout:hover { text-decoration: underline; }
        .auction-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 15px; }
        .auction-stat { background: #4d4d4d; padding: 8px; border-radius: 4px; text-align: center; }
    </style>
    <script>
        setTimeout(function() { location.reload(); }, 30000); // Refresh every 30 seconds
    </script>
</head>
<body>
    <div class="header">
        <h1>Player Portal - Welcome {{ username }}!</h1>
        <a href="/logout" class="logout">Logout</a>
    </div>
    
    <div class="card">
        <h2>🌍 Vana'diel Information</h2>
        <div class="stats">
            <div class="stat">
                <strong>Date:</strong> {{ game_data.vana_month }}/{{ game_data.vana_day }}/{{ game_data.vana_year }}
            </div>
            <div class="stat">
                <strong>Elemental Day:</strong> {{ game_data.elemental_day }}
            </div>
            <div class="stat">
                <strong>Moon Phase:</strong> {{ game_data.moon_phase }}
            </div>
            <div class="stat">
                <strong>Server Time:</strong> {{ game_data.server_time }}
            </div>
        </div>
        
        <h3>🏪 Auction House Activity</h3>
        <div class="auction-stats">
            <div class="auction-stat">
                <strong>Active Listings</strong><br>{{ game_data.auction_house.active_listings }}
            </div>
            <div class="auction-stat">
                <strong>Average Price</strong><br>{{ "{:,}".format(game_data.auction_house.average_price) }} gil
            </div>
            <div class="auction-stat">
                <strong>Gil Circulation</strong><br>{{ "{:,}".format(game_data.auction_house.total_gil_circulation) }} gil
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>🎮 Your Characters</h2>
        {% if characters %}
        {% for char in characters %}
        <div class="card character">
            <h3>{{ char.charname }} ({{ char.nation }})</h3>
            <div class="stats">
                <div class="stat">
                    <strong>Zone:</strong> {{ char.zone }}
                </div>
                <div class="stat">
                    <strong>Playtime:</strong> {{ "%.1f"|format(char.playtime/3600) }} hours
                </div>
                <div class="stat">
                    <strong>GM Level:</strong> {{ char.gmlevel }}
                </div>
                <div class="stat">
                    <strong>Inventory:</strong> {{ char.inventory_count }} items
                </div>
            </div>
            <p><strong>Jobs:</strong> 
            {% for job_id, level in char.jobs %}
                Job{{ job_id }}:{{ level }}{% if not loop.last %}, {% endif %}
            {% endfor %}
            </p>
        </div>
        {% endfor %}
        {% else %}
        <div class="card character">
            <h3>No Characters Found</h3>
            <p>You don't have any characters yet. Create a character in-game to see it here!</p>
            <div class="stats">
                <div class="stat">
                    <strong>Character Limit:</strong> 2 characters maximum
                </div>
                <div class="stat">
                    <strong>How to Create:</strong> Login to the game client and create a new character
                </div>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: #fff; margin: 0; padding: 20px; }
        .header { background: #2d2d2d; padding: 15px; margin-bottom: 20px; border-radius: 8px; }
        .card { background: #2d2d2d; padding: 20px; margin-bottom: 20px; border-radius: 8px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .stat { background: #3d3d3d; padding: 10px; border-radius: 4px; text-align: center; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #555; }
        th { background: #3d3d3d; }
        .btn { padding: 5px 10px; margin: 2px; border: none; border-radius: 3px; cursor: pointer; }
        .btn-approve { background: #51cf66; color: white; }
        .btn-reject { background: #ff6b6b; color: white; }
        .logout { float: right; color: #ff6b6b; text-decoration: none; }
    </style>
    <script>
        function approveUser(userId) {
            fetch('/api/approve_user/' + userId)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Error: ' + data.error);
                    }
                });
        }
        
        function rejectUser(userId) {
            if (confirm('Are you sure you want to reject this user?')) {
                fetch('/api/reject_user/' + userId)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('Error: ' + data.error);
                        }
                    });
            }
        }
        
        setTimeout(function() { location.reload(); }, 60000); // Refresh every minute
    </script>
</head>
<body>
    <div class="header">
        <h1>Admin Panel</h1>
        <a href="/logout" class="logout">Logout</a>
    </div>
    
    <div class="card">
        <h2>📊 System Statistics</h2>
        <div class="stats">
            <div class="stat">
                <strong>CPU Usage</strong><br>{{ "%.1f"|format(system_stats.cpu_percent) }}%
            </div>
            <div class="stat">
                <strong>Memory Usage</strong><br>{{ "%.1f"|format(system_stats.memory_percent) }}%
            </div>
            <div class="stat">
                <strong>Total Accounts</strong><br>{{ system_stats.total_accounts }}
            </div>
            <div class="stat">
                <strong>Pending Accounts</strong><br>{{ system_stats.pending_accounts }}
            </div>
            <div class="stat">
                <strong>Total Characters</strong><br>{{ system_stats.total_characters }}
            </div>
        </div>
    </div>
    
    {% if pending_users %}
    <div class="card">
        <h2>⏳ Pending User Approvals</h2>
        <table>
            <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Registration Date</th>
                <th>Actions</th>
            </tr>
            {% for user in pending_users %}
            <tr>
                <td>{{ user[1] }}</td>
                <td>{{ user[2] }}</td>
                <td>{{ user[3] }}</td>
                <td>
                    <button class="btn btn-approve" onclick="approveUser({{ user[0] }})">Approve</button>
                    <button class="btn btn-reject" onclick="rejectUser({{ user[0] }})">Reject</button>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endif %}
    
    <div class="card">
        <h2>👥 All Users</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Status</th>
                <th>Privilege</th>
                <th>Characters</th>
                <th>Registration</th>
            </tr>
            {% for user in all_users %}
            <tr>
                <td>{{ user[0] }}</td>
                <td>{{ user[1] }}</td>
                <td>{{ user[2] }}</td>
                <td>{{ "Active" if user[3] == 1 else "Pending" }}</td>
                <td>{{ "Admin" if user[4] >= 5 else "Moderator" if user[4] >= 3 else "User" }}</td>
                <td>{{ user[6] }}</td>
                <td>{{ user[5] }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
'''

def main():
    """Main function to run the test web admin"""
    parser = argparse.ArgumentParser(description='Test Web Admin Panel')
    parser.add_argument('--port', type=int, default=8080, help='Port to run on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    if not DEPENDENCIES_AVAILABLE:
        print("Required dependencies not available")
        return
    
    # Initialize the panel
    panel = TestWebAdminPanel()
    
    print(f"Starting Test Web Admin Panel on port {args.port}")
    print(f"Visit: http://localhost:{args.port}")
    print("\nTest accounts:")
    print("Admin: admin / admin123")
    print("Moderator: moderator / mod123") 
    print("User: testuser / user123")
    print("Pending: pendinguser / pending123")
    
    app.run(host='0.0.0.0', port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()