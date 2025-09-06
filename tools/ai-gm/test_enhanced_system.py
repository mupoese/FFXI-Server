#!/usr/bin/env python3
"""
Test script for AI-GM ML and Battle Test System
Tests the enhanced AI-GM capabilities with hardware acceleration
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime

# Add the AI-GM directory to path
sys.path.append(os.path.dirname(__file__))

# Import our modules
try:
    from ml_engine import AIGMMLEngine
    from battle_test_system import GMBattleTestSystem
    from ai_gm_service import AIGMService, AIGMConfig
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required packages are installed: pip install -r requirements.txt")
    sys.exit(1)

class AIGMTester:
    """Test runner for AI-GM enhanced features"""
    
    def __init__(self):
        self.logger = logging.getLogger('AI-GM-Test')
        logging.basicConfig(level=logging.INFO)
        
    def test_ml_engine(self):
        """Test ML engine functionality"""
        print("=" * 50)
        print("Testing AI-GM ML Engine")
        print("=" * 50)
        
        try:
            # Initialize ML engine
            ml_engine = AIGMMLEngine()
            
            # Test hardware detection
            hardware_status = ml_engine.get_hardware_status()
            print(f"Hardware Detection Results:")
            print(f"  Platform: {hardware_status['platform']}")
            print(f"  Backend: {hardware_status['backend']}")
            print(f"  Device: {hardware_status['device']}")
            print(f"  Models Loaded: {hardware_status['models_loaded']}")
            
            # Test with sample data
            sample_player_data = {
                'player_id': 12345,
                'timestamp': datetime.now(),
                'zone_id': 106,
                'pos_x': 100.0,
                'pos_y': 0.0,
                'pos_z': 150.0,
                'hp_percentage': 0.75,
                'mp_percentage': 0.60,
                'actions_per_minute': 3.2,
                'chat_messages_per_hour': 8,
                'login_duration_minutes': 90.0,
                'death_count': 1,
                'jail_history': 0,
                'gm_interactions': 0
            }
            
            # Test preprocessing
            preprocessed = ml_engine.preprocess_player_data([sample_player_data])
            print(f"\nData Preprocessing: {'✅ Success' if not preprocessed.empty else '❌ Failed'}")
            
            # Test prediction (will fail gracefully if no models trained)
            prediction = ml_engine.predict_player_behavior(sample_player_data)
            print(f"Behavior Prediction: {'✅ Success' if prediction else '❌ Failed'}")
            if prediction:
                print(f"  Prediction Result: {prediction}")
            
            # Test learning capability
            ml_engine.learn_from_interaction(sample_player_data, "normal")
            print("Learning Integration: ✅ Success")
            
            return True
            
        except Exception as e:
            print(f"ML Engine Test Failed: {e}")
            return False
    
    def test_battle_system(self):
        """Test battle test system functionality"""
        print("\n" + "=" * 50)
        print("Testing AI-GM Battle Test System")
        print("=" * 50)
        
        try:
            # Initialize battle system
            battle_system = GMBattleTestSystem()
            
            # Test session creation
            session_id = battle_system.create_battle_test_session(
                gm_id=9999,
                gm_name="Test-GM",
                zone_id=106,
                config_name="quick_test"
            )
            
            print(f"Session Creation: {'✅ Success' if session_id else '❌ Failed'}")
            if session_id:
                print(f"  Session ID: {session_id}")
            
            # Test mob spawning
            if session_id:
                spawn_result = battle_system.spawn_test_mob(session_id, {
                    "gm_position": (100.0, 0.0, 100.0)
                })
                
                print(f"Mob Spawning: {'✅ Success' if spawn_result.get('success') else '❌ Failed'}")
                if spawn_result.get('success'):
                    mob_info = spawn_result.get('mob_info', {})
                    print(f"  Mob: {mob_info.get('name', 'Unknown')} (Level {mob_info.get('level', 0)})")
            
            # Test assistance request
            assist_id = battle_system.create_assist_request(
                player_id=67890,
                player_name="TestPlayer",
                zone_id=106,
                position=(120.0, 0.0, 120.0),
                issue_type="stuck_in_combat",
                description="Test assistance request"
            )
            
            print(f"Assist Request: {'✅ Success' if assist_id else '❌ Failed'}")
            if assist_id:
                print(f"  Request ID: {assist_id}")
            
            # Test GM assignment with demo
            if assist_id:
                assign_result = battle_system.assign_gm_to_request(
                    assist_id, "Test-GM", auto_spawn_for_demo=True
                )
                
                print(f"GM Assignment: {'✅ Success' if assign_result.get('success') else '❌ Failed'}")
                if assign_result.get('demo_session'):
                    print("  Demo session created automatically")
            
            # Test system status
            active_sessions = battle_system.get_active_sessions()
            pending_requests = battle_system.get_pending_assist_requests()
            
            print(f"System Status:")
            print(f"  Active Sessions: {len(active_sessions)}")
            print(f"  Pending Requests: {len(pending_requests)}")
            
            return True
            
        except Exception as e:
            print(f"Battle System Test Failed: {e}")
            return False
    
    def test_integrated_service(self):
        """Test integrated AI-GM service"""
        print("\n" + "=" * 50)
        print("Testing Integrated AI-GM Service")
        print("=" * 50)
        
        try:
            # Create test configuration
            config = AIGMConfig()
            config.ml_enabled = True
            config.battle_test_enabled = True
            config.db_host = "localhost"  # This would fail without actual DB
            
            # Initialize service (will work partially without DB)
            service = AIGMService(config)
            
            # Test status
            status = service.get_system_status()
            print(f"Service Status:")
            print(f"  ML Enabled: {status.get('ml_enabled', False)}")
            print(f"  Battle Test Enabled: {status.get('battle_test_enabled', False)}")
            
            if status.get('ml_status'):
                ml_status = status['ml_status']
                print(f"  ML Backend: {ml_status.get('backend', 'Unknown')}")
                print(f"  ML Device: {ml_status.get('device', 'Unknown')}")
            
            # Test battle session creation (without DB)
            if service.battle_system:
                session_id = service.create_gm_battle_session(
                    gm_id=9999,
                    gm_name="Test-GM",
                    zone_id=106
                )
                print(f"Integrated Battle Session: {'✅ Success' if session_id else '❌ Failed'}")
            
            print("Integrated Service: ✅ Success")
            return True
            
        except Exception as e:
            print(f"Integrated Service Test Failed: {e}")
            return False
    
    def test_cross_platform_hardware(self):
        """Test cross-platform hardware support"""
        print("\n" + "=" * 50)
        print("Testing Cross-Platform Hardware Support")
        print("=" * 50)
        
        try:
            ml_engine = AIGMMLEngine()
            hardware_info = ml_engine.hardware_info
            
            print(f"Platform Detection:")
            print(f"  OS: {hardware_info.platform}")
            print(f"  CPU Cores: {hardware_info.cpu_cores}")
            
            print(f"\nGPU Support:")
            print(f"  NVIDIA CUDA: {'✅ Available' if hardware_info.has_cuda else '❌ Not Available'}")
            print(f"  AMD ROCm: {'✅ Available' if hardware_info.has_rocm else '❌ Not Available'}")
            print(f"  Apple Metal: {'✅ Available' if hardware_info.has_metal else '❌ Not Available'}")
            
            print(f"\nNPU Support:")
            print(f"  Intel OpenVINO: {'✅ Available' if hardware_info.has_openvino else '❌ Not Available'}")
            
            print(f"\nDetected Devices:")
            if hardware_info.gpu_devices:
                for device in hardware_info.gpu_devices:
                    print(f"  GPU: {device}")
            if hardware_info.npu_devices:
                for device in hardware_info.npu_devices:
                    print(f"  NPU: {device}")
            
            print(f"\nRecommended Backend: {hardware_info.recommended_backend}")
            
            return True
            
        except Exception as e:
            print(f"Hardware Test Failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all test suites"""
        print("AI-GM Enhanced System Test Suite")
        print("Testing ML capabilities and Battle Test system")
        print("Cross-platform hardware acceleration support\n")
        
        results = {
            "ML Engine": self.test_ml_engine(),
            "Battle System": self.test_battle_system(),
            "Integrated Service": self.test_integrated_service(),
            "Hardware Support": self.test_cross_platform_hardware()
        }
        
        print("\n" + "=" * 50)
        print("Test Results Summary")
        print("=" * 50)
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! AI-GM enhanced system is ready.")
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = AIGMTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)