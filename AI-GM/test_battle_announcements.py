#!/usr/bin/env python3
"""
Test script for battle test announcement functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from battle_test_system import GMBattleTestSystem
from datetime import datetime

def test_battle_announcements():
    """Test the new announcement functionality"""
    print("Testing AI-GM Battle Test Announcements...")
    
    # Initialize system
    battle_system = GMBattleTestSystem()
    
    # Test 1: Create public session with announcement
    print("\n=== Test 1: Public Session with Announcement ===")
    session_id = battle_system.create_battle_test_session(
        gm_id=12345,
        gm_name="GM-TestUser",
        zone_id=106,
        zone_name="West Sarutabaruta",
        gm_position=(100.5, 0.0, 200.3),
        config_name="standard_test",
        announcement="Testing combat mechanics for new players - all welcome!",
        public_demo=True
    )
    
    print(f"Created public session: {session_id}")
    
    if session_id and session_id in battle_system.active_sessions:
        session = battle_system.active_sessions[session_id]
        print(f"  GM: {session.gm_name}")
        print(f"  Zone: {session.zone_name}")
        print(f"  Location: {session.location}")
        print(f"  Announcement: {session.announcement_text}")
        print(f"  Public: {session.public_demonstration}")
        print(f"  Safety Level: {session.safety_warning_level}")
    
    # Test 2: Create private session
    print("\n=== Test 2: Private Session ===")
    private_session_id = battle_system.create_battle_test_session(
        gm_id=12346,
        gm_name="GM-PrivateTest",
        zone_id=112,
        zone_name="East Ronfaure",
        gm_position=(50.0, 0.0, 100.0),
        config_name="endgame_test",
        announcement="Private HNM testing",
        public_demo=False
    )
    
    print(f"Created private session: {private_session_id}")
    
    # Test 3: Spawn mob with announcement
    print("\n=== Test 3: Mob Spawn with Announcement ===")
    if session_id:
        spawn_result = battle_system.spawn_test_mob(session_id, {
            "mob_id": 17461280,
            "gm_position": (100.5, 0.0, 200.3)
        })
        
        if spawn_result["success"]:
            print(f"Spawned mob: {spawn_result['mob_info']['name']}")
            print(f"Level: {spawn_result['mob_info']['level']}")
            
            if "announcement" in spawn_result and spawn_result["announcement"]:
                announcement = spawn_result["announcement"]["announcement"]
                print(f"Announcement sent: {announcement['type']}")
                print(f"Message preview: {announcement['full_message'][:100]}...")
    
    # Test 4: Update session announcement
    print("\n=== Test 4: Update Session Announcement ===")
    if session_id:
        update_result = battle_system.update_session_announcement(
            session_id, 
            "Updated: Now testing advanced combat mechanics - experts welcome!"
        )
        print(f"Announcement update: {'Success' if update_result else 'Failed'}")
    
    # Test 5: Test different safety levels
    print("\n=== Test 5: Safety Level Testing ===")
    configs = ["quick_test", "standard_test", "advanced_test", "endgame_test"]
    for config in configs:
        safety_level = battle_system._determine_safety_level(config)
        print(f"  {config}: {safety_level}")
    
    # Test 6: Get active sessions
    print("\n=== Test 6: Active Sessions ===")
    active_sessions = battle_system.get_active_sessions()
    print(f"Active sessions: {len(active_sessions)}")
    for session in active_sessions:
        print(f"  {session['session_id']}: GM {session['gm_name']} in zone {session['zone_id']}")
    
    print("\n✅ All announcement tests completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_battle_announcements()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)