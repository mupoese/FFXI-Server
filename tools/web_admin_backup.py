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
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Install with: pip install flask mysql-connector-python psutil")
    exit(1)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate secure secret key

# HTML templates for different pages
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

# HTML template for the admin panel
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
        .header { background: #2d2d2d; padding: 1rem; border-bottom: 2px solid #4a90e2; }
        .header h1 { color: #4a90e2; display: inline-block; }
        .header .nav { float: right; }
        .header .nav a { color: #fff; text-decoration: none; margin-left: 1rem; padding: 0.5rem 1rem; border-radius: 4px; background: #4a90e2; }
        .header .nav a:hover { background: #357abd; }
        .status-indicator { float: right; margin-top: 5px; margin-right: 1rem; }
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
        .server-list { list-style: none; }
        .server-item { background: #1a1a1a; padding: 0.5rem; margin: 0.3rem 0; border-radius: 4px; display: flex; justify-content: space-between; }
        .server-status { padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
        .status-running { background: #27ae60; color: white; }
        .status-stopped { background: #e74c3c; color: white; }
        .status-pending { background: #f39c12; color: white; }
        .alert { background: #e74c3c; color: white; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .warning { background: #f39c12; color: white; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .success { background: #27ae60; color: white; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .btn { background: #4a90e2; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; margin: 0.2rem; }
        .btn:hover { background: #357abd; }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
        .btn-success { background: #27ae60; }
        .btn-success:hover { background: #219a52; }
        .btn-warning { background: #f39c12; }
        .btn-warning:hover { background: #d68910; }
        .log-container { background: #1a1a1a; padding: 1rem; border-radius: 4px; height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.9rem; }
        .refresh-indicator { display: inline-block; margin-left: 10px; animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .chart-container { height: 200px; background: #1a1a1a; border-radius: 4px; padding: 1rem; }
        .table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        .table th, .table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #444; }
        .table th { background: #2d2d2d; font-weight: bold; }
        .table tr:hover { background: #2d2d2d; }
        .pagination { display: flex; justify-content: center; margin-top: 1rem; }
        .pagination a { padding: 0.5rem 1rem; margin: 0 0.25rem; background: #2d2d2d; color: #fff; text-decoration: none; border-radius: 4px; }
        .pagination a:hover { background: #4a90e2; }
        .pagination a.active { background: #4a90e2; }
        .form-inline { display: flex; gap: 1rem; align-items: center; margin-bottom: 1rem; }
        .form-inline input, .form-inline select { padding: 0.5rem; border: 1px solid #555; border-radius: 4px; background: #1a1a1a; color: #fff; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="header">
        <h1>🎮 LandSandBoat Administration</h1>
        <div class="nav">
            {% if session.get('user_type') == 'admin' %}
            <span>Admin: {{ session.get('username') }}</span>
            {% elif session.get('user_type') == 'moderator' %}
            <span>Moderator: {{ session.get('username') }}</span>
            {% endif %}
            <a href="/logout">Logout</a>
        </div>
        <div class="status-indicator">
            <span id="status-text">Loading...</span>
            <span id="refresh-indicator" class="refresh-indicator">⟳</span>
        </div>
    </div>

    <div class="container">
        <div id="alerts-container"></div>

        <div class="tabs">
            <div class="tab active" onclick="showTab('dashboard')">Dashboard</div>
            <div class="tab" onclick="showTab('users')">User Management</div>
            <div class="tab" onclick="showTab('characters')">Characters</div>
            <div class="tab" onclick="showTab('gamedata')">Game Data</div>
            {% if session.get('user_type') == 'admin' %}
            <div class="tab" onclick="showTab('moderation')">Moderation</div>
            {% endif %}
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
                    <div class="metric">
                        <span>Network In:</span>
                        <span id="network-in" class="metric-value">--</span>
                    </div>
                    <div class="metric">
                        <span>Network Out:</span>
                        <span id="network-out" class="metric-value">--</span>
                    </div>
                </div>

                <div class="card">
                    <h3>Server Status</h3>
                    <ul id="server-list" class="server-list">
                        <li>Loading server information...</li>
                    </ul>
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
                    <div class="metric">
                        <span>Database Connections:</span>
                        <span id="db-connections" class="metric-value">--</span>
                    </div>
                </div>

                <div class="card">
                    <h3>Quick Actions</h3>
                    <button class="btn" onclick="restartServer('map')">Restart Map Server</button>
                    <button class="btn" onclick="restartServer('login')">Restart Login Server</button>
                    <button class="btn btn-danger" onclick="shutdownAll()">Emergency Shutdown</button>
                    <button class="btn" onclick="backupDatabase()">Backup Database</button>
                    <button class="btn" onclick="refreshData()">Refresh Data</button>
                </div>
            </div>

            <div class="grid">
                <div class="card">
                    <h3>CPU Usage History</h3>
                    <div class="chart-container">
                        <canvas id="cpu-chart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <h3>Player Activity</h3>
                    <div class="chart-container">
                        <canvas id="player-chart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- User Management Tab -->
        <div id="users" class="tab-content">
            <div class="card">
                <h3>User Registration Requests</h3>
                <div class="form-inline">
                    <input type="text" id="user-search" placeholder="Search users..." onkeyup="searchUsers()">
                    <select id="user-filter" onchange="filterUsers()">
                        <option value="all">All Users</option>
                        <option value="pending">Pending Approval</option>
                        <option value="active">Active</option>
                        <option value="banned">Banned</option>
                    </select>
                    <button class="btn" onclick="refreshUsers()">Refresh</button>
                </div>
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
                <div class="pagination" id="users-pagination"></div>
            </div>
        </div>

        <!-- Characters Tab -->
        <div id="characters" class="tab-content">
            <div class="card">
                <h3>Character Management</h3>
                <div class="form-inline">
                    <input type="text" id="char-search" placeholder="Search characters..." onkeyup="searchCharacters()">
                    <select id="char-filter" onchange="filterCharacters()">
                        <option value="all">All Characters</option>
                        <option value="online">Online</option>
                        <option value="offline">Offline</option>
                        <option value="gm">GM Characters</option>
                    </select>
                    <button class="btn" onclick="refreshCharacters()">Refresh</button>
                </div>
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
                <div class="pagination" id="characters-pagination"></div>
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
                    <div class="metric">
                        <span>Server Uptime:</span>
                        <span id="server-uptime" class="metric-value">--</span>
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
                    <button class="btn" onclick="refreshAuctionHouse()">Refresh AH Data</button>
                </div>

                <div class="card">
                    <h3>Zone Population</h3>
                    <div id="zone-population" class="log-container">
                        Loading zone data...
                    </div>
                </div>

                <div class="card">
                    <h3>Economic Overview</h3>
                    <div class="chart-container">
                        <canvas id="economy-chart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Moderation Tab -->
        {% if session.get('user_type') == 'admin' %}
        <div id="moderation" class="tab-content">
            <div class="card">
                <h3>Moderator Management</h3>
                <table class="table" id="moderators-table">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>GM Level</th>
                            <th>Last Active</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="moderators-tbody">
                        <tr><td colspan="6">Loading moderators...</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h3>System Configuration</h3>
                <div class="form-inline">
                    <label>Max Characters per Account:</label>
                    <input type="number" id="max-chars" value="2" min="1" max="16">
                    <button class="btn" onclick="updateMaxChars()">Update</button>
                </div>
                <div class="form-inline">
                    <label>Registration Approval Required:</label>
                    <select id="approval-required">
                        <option value="true">Yes</option>
                        <option value="false">No</option>
                    </select>
                    <button class="btn" onclick="updateApprovalSetting()">Update</button>
                </div>
            </div>
        </div>
        {% endif %}
    </div>

    <script>
        // Tab functionality
        function showTab(tabName) {
            // Hide all tab contents
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
            
            // Load data for the selected tab
            if (tabName === 'users') loadUsers();
            else if (tabName === 'characters') loadCharacters();
            else if (tabName === 'gamedata') loadGameData();
            else if (tabName === 'moderation') loadModerators();
        }

        // Data loading functions
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
                                <td><span class="server-status status-${user.status}">${user.status}</span></td>
                                <td>${user.character_count}/2</td>
                                <td>
                                    ${user.status === 'pending' ? 
                                        `<button class="btn btn-success" onclick="approveUser(${user.id})">Approve</button>
                                         <button class="btn btn-danger" onclick="rejectUser(${user.id})">Reject</button>` :
                                        `<button class="btn btn-warning" onclick="editUser(${user.id})">Edit</button>`
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
                                    <button class="btn btn-warning" onclick="editCharacter(${char.id})">Edit</button>
                                </td>
                            </tr>
                        `;
                        tbody.innerHTML += row;
                    });
                })
                .catch(error => console.error('Error loading characters:', error));
        }

        function loadGameData() {
            // Load Vana'diel time and elemental day
            fetch('/api/gamedata')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('vanadiel-date').textContent = data.vanadiel_date;
                    document.getElementById('elemental-day').textContent = data.elemental_day;
                    document.getElementById('moon-phase').textContent = data.moon_phase;
                    document.getElementById('server-uptime').textContent = data.uptime;
                    document.getElementById('ah-listings').textContent = data.auction_house.active_listings;
                    document.getElementById('ah-sales-today').textContent = data.auction_house.sales_today;
                    document.getElementById('ah-total-gil').textContent = data.auction_house.total_gil;
                    
                    // Update zone population
                    const zoneDiv = document.getElementById('zone-population');
                    zoneDiv.innerHTML = '';
                    data.zone_population.forEach(zone => {
                        zoneDiv.innerHTML += `${zone.name}: ${zone.population} players<br>`;
                    });
                })
                .catch(error => console.error('Error loading game data:', error));
        }

        function loadModerators() {
            fetch('/api/moderators')
                .then(response => response.json())
                .then(data => {
                    const tbody = document.getElementById('moderators-tbody');
                    tbody.innerHTML = '';
                    data.moderators.forEach(mod => {
                        const row = `
                            <tr>
                                <td>${mod.username}</td>
                                <td>${mod.email}</td>
                                <td>${mod.role}</td>
                                <td>${mod.gm_level}</td>
                                <td>${new Date(mod.last_active).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn" onclick="promoteToGM(${mod.id})">Promote to GM</button>
                                    <button class="btn btn-danger" onclick="removeModerator(${mod.id})">Remove</button>
                                </td>
                            </tr>
                        `;
                        tbody.innerHTML += row;
                    });
                })
                .catch(error => console.error('Error loading moderators:', error));
        }

        // User action functions
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
            })
            .catch(error => showAlert('Error approving user', 'error'));
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
                })
                .catch(error => showAlert('Error rejecting user', 'error'));
            }
        }

        function promoteToGM(userId) {
            if (confirm('Promote this moderator to GM status?')) {
                fetch('/api/moderators/promote', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: userId})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('Moderator promoted to GM successfully', 'success');
                        loadModerators();
                    } else {
                        showAlert('Error promoting moderator: ' + data.error, 'error');
                    }
                })
                .catch(error => showAlert('Error promoting moderator', 'error'));
            }
        }

        // Utility functions
        function showAlert(message, type) {
            const container = document.getElementById('alerts-container');
            const alert = document.createElement('div');
            alert.className = type === 'success' ? 'success' : 'alert';
            alert.textContent = message;
            container.appendChild(alert);
            setTimeout(() => container.removeChild(alert), 5000);
        }

        function refreshData() {
            loadDashboardData();
            if (document.getElementById('users').classList.contains('active')) loadUsers();
            if (document.getElementById('characters').classList.contains('active')) loadCharacters();
            if (document.getElementById('gamedata').classList.contains('active')) loadGameData();
            if (document.getElementById('moderation').classList.contains('active')) loadModerators();
        }

        function loadDashboardData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cpu-usage').textContent = data.cpu_percent + '%';
                    document.getElementById('memory-usage').textContent = data.memory_percent + '%';
                    document.getElementById('disk-usage').textContent = data.disk_percent + '%';
                    document.getElementById('network-in').textContent = data.network.bytes_recv;
                    document.getElementById('network-out').textContent = data.network.bytes_sent;
                    document.getElementById('online-players').textContent = data.database.online_players;
                    document.getElementById('total-characters').textContent = data.database.total_characters;
                    document.getElementById('pending-registrations').textContent = data.database.pending_registrations;
                    document.getElementById('db-connections').textContent = data.database.connections;
                    
                    updateServerList(data.servers);
                })
                .catch(error => console.error('Error loading status:', error));
        }

        function updateServerList(servers) {
            const list = document.getElementById('server-list');
            list.innerHTML = '';
            servers.forEach(server => {
                const item = document.createElement('li');
                item.className = 'server-item';
                item.innerHTML = `
                    <span>${server.name}</span>
                    <span class="server-status status-${server.status}">${server.status}</span>
                `;
                list.appendChild(item);
            });
        }

        // Search and filter functions
        function searchUsers() {
            const search = document.getElementById('user-search').value.toLowerCase();
            const rows = document.querySelectorAll('#users-tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(search) ? '' : 'none';
            });
        }

        function searchCharacters() {
            const search = document.getElementById('char-search').value.toLowerCase();
            const rows = document.querySelectorAll('#characters-tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(search) ? '' : 'none';
            });
        }

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboardData();
            setInterval(loadDashboardData, 10000); // Refresh every 10 seconds
        });

        // Placeholder functions for server controls
        function restartServer(type) {
            if (confirm(`Restart ${type} server?`)) {
                fetch('/api/restart', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({server: type})
                })
                .then(response => response.json())
                .then(data => {
                    showAlert(data.message, data.success ? 'success' : 'error');
                });
            }
        }

        function shutdownAll() {
            if (confirm('Emergency shutdown of all servers?')) {
                fetch('/api/shutdown', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    showAlert(data.message, data.success ? 'success' : 'error');
                });
            }
        }

        function backupDatabase() {
            fetch('/api/backup', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                showAlert(data.message, data.success ? 'success' : 'error');
            });
        }
    </script>
</body>
</html>
"""

# User portal template for registered users
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
        .header { background: #2d2d2d; padding: 1rem; border-bottom: 2px solid #4a90e2; }
        .header h1 { color: #4a90e2; display: inline-block; }
        .header .nav { float: right; }
        .header .nav a { color: #fff; text-decoration: none; margin-left: 1rem; padding: 0.5rem 1rem; border-radius: 4px; background: #4a90e2; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-bottom: 2rem; }
        .card { background: #2d2d2d; padding: 1.5rem; border-radius: 8px; border: 1px solid #444; }
        .card h3 { color: #4a90e2; margin-bottom: 1rem; }
        .character-list { list-style: none; }
        .character-item { background: #1a1a1a; padding: 1rem; margin: 0.5rem 0; border-radius: 4px; }
        .character-name { font-weight: bold; color: #4a90e2; }
        .character-details { margin-top: 0.5rem; color: #ccc; }
        .metric { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
        .metric-value { font-weight: bold; }
        .inventory-grid { display: grid; grid-template-columns: repeat(8, 1fr); gap: 2px; margin-top: 1rem; }
        .inventory-slot { aspect-ratio: 1; background: #1a1a1a; border: 1px solid #444; border-radius: 2px; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; }
        .inventory-slot.occupied { background: #4a90e2; color: white; }
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

        <div class="card" id="character-details" style="display: none;">
            <h3>Character Details: <span id="selected-character-name"></span></h3>
            <div class="grid">
                <div>
                    <h4>Statistics</h4>
                    <div class="metric">
                        <span>Level:</span>
                        <span id="char-level" class="metric-value">--</span>
                    </div>
                    <div class="metric">
                        <span>Job:</span>
                        <span id="char-job" class="metric-value">--</span>
                    </div>
                    <div class="metric">
                        <span>Gil:</span>
                        <span id="char-gil" class="metric-value">--</span>
                    </div>
                    <div class="metric">
                        <span>Zone:</span>
                        <span id="char-zone" class="metric-value">--</span>
                    </div>
                    <div class="metric">
                        <span>Play Time:</span>
                        <span id="char-playtime" class="metric-value">--</span>
                    </div>
                </div>
                
                <div>
                    <h4>Inventory</h4>
                    <div id="inventory-grid" class="inventory-grid">
                        <!-- Inventory slots will be populated by JavaScript -->
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>Auction House</h3>
            <div class="metric">
                <span>Active Listings:</span>
                <span id="ah-listings" class="metric-value">--</span>
            </div>
            <div class="metric">
                <span>Recent Sales:</span>
                <span id="ah-sales" class="metric-value">--</span>
            </div>
            <div style="max-height: 200px; overflow-y: auto; margin-top: 1rem;" id="ah-activity">
                Loading auction house data...
            </div>
        </div>
    </div>

    <script>
        function loadUserData() {
            // Load user's characters
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
                        item.onclick = () => selectCharacter(char);
                        list.appendChild(item);
                    });
                })
                .catch(error => console.error('Error loading characters:', error));

            // Load game data
            fetch('/api/gamedata')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('vanadiel-date').textContent = data.vanadiel_date;
                    document.getElementById('elemental-day').textContent = data.elemental_day;
                    document.getElementById('moon-phase').textContent = data.moon_phase;
                    document.getElementById('players-online').textContent = data.players_online;
                })
                .catch(error => console.error('Error loading game data:', error));

            // Load auction house data
            loadAuctionHouse();
        }

        function selectCharacter(character) {
            document.getElementById('character-details').style.display = 'block';
            document.getElementById('selected-character-name').textContent = character.name;
            document.getElementById('char-level').textContent = character.level;
            document.getElementById('char-job').textContent = character.job;
            document.getElementById('char-gil').textContent = character.gil || 0;
            document.getElementById('char-zone').textContent = character.zone;
            document.getElementById('char-playtime').textContent = character.playtime || '0 hours';

            // Load character inventory
            fetch(`/api/user/character/${character.id}/inventory`)
                .then(response => response.json())
                .then(data => {
                    const grid = document.getElementById('inventory-grid');
                    grid.innerHTML = '';
                    for (let i = 0; i < 80; i++) { // Standard inventory size
                        const slot = document.createElement('div');
                        slot.className = 'inventory-slot';
                        const item = data.inventory.find(item => item.slot === i);
                        if (item) {
                            slot.classList.add('occupied');
                            slot.textContent = item.quantity || '1';
                            slot.title = item.name;
                        }
                        grid.appendChild(slot);
                    }
                })
                .catch(error => console.error('Error loading inventory:', error));
        }

        function loadAuctionHouse() {
            fetch('/api/auction_house')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('ah-listings').textContent = data.active_listings;
                    document.getElementById('ah-sales').textContent = data.recent_sales;
                    
                    const activity = document.getElementById('ah-activity');
                    activity.innerHTML = '';
                    data.recent_activity.forEach(item => {
                        activity.innerHTML += `
                            <div style="padding: 0.5rem; border-bottom: 1px solid #444;">
                                <strong>${item.item_name}</strong> - ${item.price} gil<br>
                                <small>${new Date(item.timestamp).toLocaleString()}</small>
                            </div>
                        `;
                    });
                })
                .catch(error => console.error('Error loading auction house:', error));
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadUserData();
            setInterval(loadUserData, 30000); // Refresh every 30 seconds
        });
    </script>
</body>
</html>
                    <span>Total Characters:</span>
                    <span id="total-characters" class="metric-value">--</span>
                </div>
                <div class="metric">
                    <span>Database Connections:</span>
                    <span id="db-connections" class="metric-value">--</span>
                </div>
            </div>

            <div class="card">
                <h3>Quick Actions</h3>
                <button class="btn" onclick="restartServer('map')">Restart Map Server</button>
                <button class="btn" onclick="restartServer('login')">Restart Login Server</button>
                <button class="btn btn-danger" onclick="shutdownAll()">Emergency Shutdown</button>
                <button class="btn" onclick="backupDatabase()">Backup Database</button>
                <button class="btn" onclick="refreshData()">Refresh Data</button>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>CPU Usage History</h3>
                <div class="chart-container">
                    <canvas id="cpu-chart"></canvas>
                </div>
            </div>

            <div class="card">
                <h3>Player Activity</h3>
                <div class="chart-container">
                    <canvas id="player-chart"></canvas>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>Recent Server Logs</h3>
            <div id="log-container" class="log-container">
                Loading logs...
            </div>
        </div>
    </div>

    <script>
        let cpuChart, playerChart;
        let systemData = [];
        let playerData = [];
        
        function initCharts() {
            const cpuCtx = document.getElementById('cpu-chart').getContext('2d');
            cpuChart = new Chart(cpuCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU %',
                        data: [],
                        borderColor: '#4a90e2',
                        backgroundColor: 'rgba(74, 144, 226, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#fff' } } },
                    scales: {
                        x: { ticks: { color: '#ccc' }, grid: { color: '#444' } },
                        y: { ticks: { color: '#ccc' }, grid: { color: '#444' }, min: 0, max: 100 }
                    }
                }
            });

            const playerCtx = document.getElementById('player-chart').getContext('2d');
            playerChart = new Chart(playerCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Online Players',
                        data: [],
                        borderColor: '#27ae60',
                        backgroundColor: 'rgba(39, 174, 96, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#fff' } } },
                    scales: {
                        x: { ticks: { color: '#ccc' }, grid: { color: '#444' } },
                        y: { ticks: { color: '#ccc' }, grid: { color: '#444' }, min: 0 }
                    }
                }
            });
        }

        async function refreshData() {
            try {
                document.getElementById('refresh-indicator').style.display = 'inline-block';
                
                const response = await fetch('/api/status');
                const data = await response.json();
                
                updateSystemMetrics(data.system);
                updateServerStatus(data.servers);
                updateDatabaseInfo(data.database);
                updateCharts(data);
                updateAlerts(data.alerts);
                
                document.getElementById('status-text').textContent = 'Connected';
            } catch (error) {
                console.error('Error fetching data:', error);
                document.getElementById('status-text').textContent = 'Connection Error';
            } finally {
                document.getElementById('refresh-indicator').style.display = 'none';
            }
        }

        function updateSystemMetrics(system) {
            document.getElementById('cpu-usage').textContent = system.cpu_percent + '%';
            document.getElementById('memory-usage').textContent = system.memory_percent + '%';
            document.getElementById('disk-usage').textContent = system.disk_percent + '%';
            document.getElementById('network-in').textContent = formatBytes(system.network_bytes_recv);
            document.getElementById('network-out').textContent = formatBytes(system.network_bytes_sent);
        }

        function updateServerStatus(servers) {
            const serverList = document.getElementById('server-list');
            serverList.innerHTML = '';
            
            for (const [name, info] of Object.entries(servers)) {
                const li = document.createElement('li');
                li.className = 'server-item';
                li.innerHTML = `
                    <span>${name}</span>
                    <span class="server-status ${info.status === 'running' ? 'status-running' : 'status-stopped'}">
                        ${info.status === 'running' ? '✅ Running' : '❌ Stopped'}
                    </span>
                `;
                serverList.appendChild(li);
            }
        }

        function updateDatabaseInfo(database) {
            document.getElementById('online-players').textContent = database.online_players;
            document.getElementById('total-characters').textContent = database.total_characters;
            document.getElementById('db-connections').textContent = database.active_connections;
        }

        function updateCharts(data) {
            const now = new Date().toLocaleTimeString();
            
            // Update CPU chart
            if (cpuChart.data.labels.length > 20) {
                cpuChart.data.labels.shift();
                cpuChart.data.datasets[0].data.shift();
            }
            cpuChart.data.labels.push(now);
            cpuChart.data.datasets[0].data.push(data.system.cpu_percent);
            cpuChart.update('none');
            
            // Update player chart
            if (playerChart.data.labels.length > 20) {
                playerChart.data.labels.shift();
                playerChart.data.datasets[0].data.shift();
            }
            playerChart.data.labels.push(now);
            playerChart.data.datasets[0].data.push(data.database.online_players);
            playerChart.update('none');
        }

        function updateAlerts(alerts) {
            const container = document.getElementById('alerts-container');
            container.innerHTML = '';
            
            alerts.forEach(alert => {
                const alertDiv = document.createElement('div');
                alertDiv.className = alert.severity === 'critical' ? 'alert' : 'warning';
                alertDiv.textContent = alert.message;
                container.appendChild(alertDiv);
            });
        }

        function formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        async function restartServer(serverType) {
            if (confirm(`Are you sure you want to restart the ${serverType} server?`)) {
                try {
                    const response = await fetch('/api/restart', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ server: serverType })
                    });
                    const result = await response.json();
                    alert(result.message);
                } catch (error) {
                    alert('Error restarting server: ' + error.message);
                }
            }
        }

        async function shutdownAll() {
            if (confirm('Are you sure you want to shutdown ALL servers? This will disconnect all players!')) {
                try {
                    const response = await fetch('/api/shutdown', { method: 'POST' });
                    const result = await response.json();
                    alert(result.message);
                } catch (error) {
                    alert('Error shutting down servers: ' + error.message);
                }
            }
        }

        async function backupDatabase() {
            if (confirm('Start database backup? This may take a few minutes.')) {
                try {
                    const response = await fetch('/api/backup', { method: 'POST' });
                    const result = await response.json();
                    alert(result.message);
                } catch (error) {
                    alert('Error starting backup: ' + error.message);
                }
            }
        }

        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            refreshData();
            setInterval(refreshData, 5000); // Refresh every 5 seconds
        });
    </script>
</body>
</html>
"""

class WebAdminPanel:
    """Web-based administration panel for LandSandBoat"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.setup_routes()
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration for web admin panel"""
        default_config = {
            "database": {
                "host": "localhost",
                "port": 3306,
                "database": "xidb",
                "user": "root",
                "password": ""
            },
            "web": {
                "host": "0.0.0.0",
                "port": 8080,
                "debug": False
            }
        }
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Simple merge for this basic implementation
                    for key, value in user_config.items():
                        if key in default_config:
                            default_config[key].update(value)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        return default_config
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @app.route('/')
        def dashboard():
            return render_template_string(HTML_TEMPLATE)
        
        @app.route('/api/status')
        def api_status():
            """Get current system status as JSON"""
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # Server processes
                servers = self._get_server_processes()
                
                # Database info
                db_info = self._get_database_info()
                
                # Generate alerts
                alerts = self._generate_alerts(cpu_percent, memory.percent, disk.percent)
                
                return jsonify({
                    "system": {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "disk_percent": disk.percent,
                        "network_bytes_sent": network.bytes_sent,
                        "network_bytes_recv": network.bytes_recv
                    },
                    "servers": servers,
                    "database": db_info,
                    "alerts": alerts,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/restart', methods=['POST'])
        def api_restart():
            """Restart a specific server"""
            try:
                data = request.get_json()
                server_type = data.get('server')
                
                # This is a placeholder - in real implementation, you'd
                # use systemctl, supervisorctl, or similar
                message = f"Restart command sent for {server_type} server"
                
                return jsonify({"success": True, "message": message})
                
            except Exception as e:
                return jsonify({"success": False, "message": str(e)}), 500
        
        @app.route('/api/shutdown', methods=['POST'])
        def api_shutdown():
            """Emergency shutdown of all servers"""
            try:
                # Placeholder for shutdown logic
                message = "Emergency shutdown initiated"
                return jsonify({"success": True, "message": message})
                
            except Exception as e:
                return jsonify({"success": False, "message": str(e)}), 500
        
        @app.route('/api/backup', methods=['POST'])
        def api_backup():
            """Start database backup"""
            try:
                # Placeholder for backup logic
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                message = f"Database backup started: backup_{timestamp}.sql"
                return jsonify({"success": True, "message": message})
                
            except Exception as e:
                return jsonify({"success": False, "message": str(e)}), 500
    
    def _get_server_processes(self) -> Dict[str, Any]:
        """Get information about server processes"""
        servers = {}
        server_names = ["xi_map", "xi_login", "xi_search", "xi_connect"]
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                for server_name in server_names:
                    if server_name in proc_name:
                        servers[server_name] = {"status": "running", "pid": proc.info['pid']}
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Mark missing servers as stopped
        for server_name in server_names:
            if server_name not in servers:
                servers[server_name] = {"status": "stopped", "pid": None}
        
        return servers
    
    def _get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        try:
            conn = mysql.connector.connect(**self.config["database"])
            cursor = conn.cursor(dictionary=True)
            
            # Get player counts
            cursor.execute("SELECT COUNT(*) as total_chars FROM chars WHERE active = 1")
            char_count = cursor.fetchone()["total_chars"]
            
            cursor.execute("""
                SELECT COUNT(*) as online_players 
                FROM chars c 
                JOIN accounts a ON c.accid = a.id 
                WHERE a.status = 1
            """)
            online_count = cursor.fetchone()["online_players"]
            
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            active_connections = cursor.fetchone()["Value"]
            
            conn.close()
            
            return {
                "total_characters": char_count,
                "online_players": online_count,
                "active_connections": int(active_connections)
            }
            
        except Exception as e:
            return {
                "total_characters": 0,
                "online_players": 0,
                "active_connections": 0,
                "error": str(e)
            }
    
    def _generate_alerts(self, cpu: float, memory: float, disk: float) -> List[Dict[str, str]]:
        """Generate system alerts"""
        alerts = []
        
        if cpu > 80:
            alerts.append({
                "severity": "warning",
                "message": f"High CPU usage: {cpu:.1f}%"
            })
        
        if memory > 85:
            alerts.append({
                "severity": "critical",
                "message": f"High memory usage: {memory:.1f}%"
            })
        
        if disk > 90:
            alerts.append({
                "severity": "critical",
                "message": f"Low disk space: {disk:.1f}% used"
            })
        
        return alerts
    
    def run(self):
        """Start the web admin panel"""
        host = self.config["web"]["host"]
        port = self.config["web"]["port"]
        debug = self.config["web"]["debug"]
        
        print(f"🌐 Starting LandSandBoat Web Admin Panel")
        print(f"📍 Access at: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
        print(f"🔧 Debug mode: {'enabled' if debug else 'disabled'}")
        
        app.run(host=host, port=port, debug=debug)

def main():
    parser = argparse.ArgumentParser(description="LandSandBoat Web Administration Panel")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    panel = WebAdminPanel(args.config)
    
    # Override config with command line arguments
    if args.host:
        panel.config["web"]["host"] = args.host
    if args.port:
        panel.config["web"]["port"] = args.port
    if args.debug:
        panel.config["web"]["debug"] = args.debug
    
    panel.run()

if __name__ == "__main__":
    main()