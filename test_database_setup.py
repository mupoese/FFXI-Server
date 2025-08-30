#!/usr/bin/env python3
"""
Create a test SQLite database with sample data for testing the web admin system
"""

import sqlite3
import hashlib
import datetime
import random
import json

def create_test_database():
    """Create test database with sample accounts and characters"""
    
    # Create SQLite database
    conn = sqlite3.connect('test_xidb.sqlite')
    cursor = conn.cursor()
    
    # Create accounts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            login VARCHAR(16) NOT NULL,
            password VARCHAR(64) NOT NULL,
            current_email VARCHAR(64) NOT NULL,
            registration_email VARCHAR(64) NOT NULL,
            timecreate DATETIME NOT NULL,
            timelastmodify TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            content_ids INTEGER NOT NULL DEFAULT 2,
            expansions INTEGER NOT NULL DEFAULT 4094,
            features INTEGER NOT NULL DEFAULT 253,
            status INTEGER NOT NULL DEFAULT 1,
            priv INTEGER NOT NULL DEFAULT 1
        )
    ''')
    
    # Create chars table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chars (
            charid INTEGER PRIMARY KEY,
            accid INTEGER NOT NULL,
            original_accid INTEGER NOT NULL DEFAULT 0,
            charname VARCHAR(15) NOT NULL,
            nation INTEGER NOT NULL DEFAULT 0,
            pos_zone INTEGER NOT NULL,
            pos_prevzone INTEGER NOT NULL DEFAULT 0,
            pos_rot INTEGER NOT NULL DEFAULT 0,
            pos_x REAL NOT NULL DEFAULT 0.0,
            pos_y REAL NOT NULL DEFAULT 0.0,
            pos_z REAL NOT NULL DEFAULT 0.0,
            playtime INTEGER NOT NULL DEFAULT 0,
            gmlevel INTEGER NOT NULL DEFAULT 0,
            job_master INTEGER NOT NULL DEFAULT 1,
            timecreated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_logout DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (accid) REFERENCES accounts(id)
        )
    ''')
    
    # Create char_jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS char_jobs (
            charid INTEGER NOT NULL,
            job INTEGER NOT NULL,
            level INTEGER NOT NULL DEFAULT 1,
            unlocked INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (charid) REFERENCES chars(charid)
        )
    ''')
    
    # Create char_inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS char_inventory (
            charid INTEGER NOT NULL,
            location INTEGER NOT NULL,
            slot INTEGER NOT NULL,
            itemid INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            extra BLOB,
            FOREIGN KEY (charid) REFERENCES chars(charid)
        )
    ''')
    
    # Create auction_house table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auction_house (
            id INTEGER PRIMARY KEY,
            itemid INTEGER NOT NULL,
            stack INTEGER NOT NULL DEFAULT 0,
            seller_name VARCHAR(15) NOT NULL,
            price INTEGER NOT NULL,
            sale_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sample zone data
    zones = {
        1: "Ronfaure", 
        2: "Gusgen Mines",
        235: "Bastok Markets",
        240: "Southern San d'Oria",
        244: "Chateau d'Oraguille",
        245: "Northern San d'Oria",
        246: "Port San d'Oria",
        230: "Windurst Waters",
        231: "Windurst Walls",
        232: "Port Windurst",
        233: "Windurst Woods"
    }
    
    # Insert test admin account
    admin_password = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute('''
        INSERT OR REPLACE INTO accounts (id, login, password, current_email, registration_email, 
                                       timecreate, status, priv, content_ids)
        VALUES (1, 'admin', ?, 'admin@test.com', 'admin@test.com', ?, 1, 5, 2)
    ''', (admin_password, datetime.datetime.now()))
    
    # Insert test moderator account
    mod_password = hashlib.sha256("mod123".encode()).hexdigest()
    cursor.execute('''
        INSERT OR REPLACE INTO accounts (id, login, password, current_email, registration_email,
                                       timecreate, status, priv, content_ids)
        VALUES (2, 'moderator', ?, 'mod@test.com', 'mod@test.com', ?, 1, 3, 2)
    ''', (mod_password, datetime.datetime.now()))
    
    # Insert test user account
    user_password = hashlib.sha256("user123".encode()).hexdigest()
    cursor.execute('''
        INSERT OR REPLACE INTO accounts (id, login, password, current_email, registration_email,
                                       timecreate, status, priv, content_ids)
        VALUES (3, 'testuser', ?, 'user@test.com', 'user@test.com', ?, 1, 1, 2)
    ''', (user_password, datetime.datetime.now()))
    
    # Insert pending approval user
    pending_password = hashlib.sha256("pending123".encode()).hexdigest()
    cursor.execute('''
        INSERT OR REPLACE INTO accounts (id, login, password, current_email, registration_email,
                                       timecreate, status, priv, content_ids)
        VALUES (4, 'pendinguser', ?, 'pending@test.com', 'pending@test.com', ?, 0, 1, 2)
    ''', (pending_password, datetime.datetime.now()))
    
    # Create test characters
    test_characters = [
        (1, 1, "AdminChar", 0, 240, 14400, 120),  # Admin character
        (2, 2, "ModChar", 1, 235, 7200, 75),     # Moderator character
        (3, 3, "TestChar1", 2, 230, 3600, 45),   # User character 1
        (4, 3, "TestChar2", 0, 245, 1800, 30),   # User character 2
    ]
    
    for charid, accid, charname, nation, zone, playtime, gmlevel in test_characters:
        cursor.execute('''
            INSERT OR REPLACE INTO chars (charid, accid, charname, nation, pos_zone, 
                                        playtime, gmlevel, timecreated, last_logout)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (charid, accid, charname, nation, zone, playtime, gmlevel, 
              datetime.datetime.now(), datetime.datetime.now()))
        
        # Add job levels for each character
        jobs = [
            (1, random.randint(10, 75)),  # WAR
            (2, random.randint(1, 50)),   # MNK
            (3, random.randint(1, 40)),   # WHM
            (4, random.randint(1, 35)),   # BLM
            (5, random.randint(1, 30)),   # RDM
            (6, random.randint(1, 25)),   # THF
        ]
        
        for job, level in jobs:
            cursor.execute('''
                INSERT OR REPLACE INTO char_jobs (charid, job, level, unlocked)
                VALUES (?, ?, ?, 1)
            ''', (charid, job, level))
        
        # Add sample inventory items
        for slot in range(10):
            itemid = random.randint(1000, 9999)
            quantity = random.randint(1, 99)
            cursor.execute('''
                INSERT OR REPLACE INTO char_inventory (charid, location, slot, itemid, quantity)
                VALUES (?, 0, ?, ?, ?)
            ''', (charid, slot, itemid, quantity))
    
    # Add sample auction house data
    for i in range(20):
        itemid = random.randint(1000, 9999)
        price = random.randint(100, 100000)
        seller = f"Player{i+1}"
        cursor.execute('''
            INSERT INTO auction_house (itemid, stack, seller_name, price, sale_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (itemid, 0, seller, price, datetime.datetime.now()))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Test database created successfully!")
    print("\nTest accounts created:")
    print("Admin: admin / admin123 (priv: 5)")
    print("Moderator: moderator / mod123 (priv: 3)")
    print("User: testuser / user123 (priv: 1)")
    print("Pending: pendinguser / pending123 (status: 0 - needs approval)")
    
    return "test_xidb.sqlite"

if __name__ == "__main__":
    db_file = create_test_database()
    print(f"\nDatabase file: {db_file}")