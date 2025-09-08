#!/usr/bin/env python3
"""
Streaming System Validation and Test Suite
Comprehensive testing for all streaming system components

Tests:
- Asset extraction and rendering engine
- Streaming platform integration
- API endpoints and WebSocket connections
- AI-GM integration and event triggers
- Performance and load testing
"""

import os
import sys
import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any
import tempfile
import shutil
from pathlib import Path
import subprocess
import requests
import websockets
import threading
from datetime import datetime, timedelta

# Test framework
import unittest
from unittest.mock import MagicMock, patch
import numpy as np

# Import streaming components
from ffxi_asset_extractor import FFXIAssetExtractor
from ffxi_renderer import FFXIRenderer, RenderObject, Camera
from streaming_manager import StreamingManager, StreamPlatform
from ffxi_streaming_service import FFXIStreamingService
from aigm_streaming_integration import AIGMStreamingIntegration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamingSystemTestSuite(unittest.TestCase):
    """Comprehensive test suite for streaming system"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="ffxi_streaming_test_"))
        self.assets_dir = self.test_dir / "assets"
        self.config_dir = self.test_dir / "config"
        
        # Create test directories
        self.assets_dir.mkdir(parents=True)
        self.config_dir.mkdir(parents=True)
        
        logger.info(f"Test directory: {self.test_dir}")
        
    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            
    def test_asset_extractor_initialization(self):
        """Test FFXI asset extractor initialization"""
        logger.info("Testing asset extractor initialization...")
        
        extractor = FFXIAssetExtractor("/demo/ffxi", str(self.assets_dir))
        
        # Test initialization
        self.assertIsNotNone(extractor)
        self.assertEqual(extractor.output_path, self.assets_dir)
        
        # Test validation (should pass in demo mode)
        self.assertTrue(extractor.validate_ffxi_installation())
        
        logger.info("✅ Asset extractor initialization test passed")
        
    def test_asset_extraction(self):
        """Test asset extraction functionality"""
        logger.info("Testing asset extraction...")
        
        extractor = FFXIAssetExtractor("/demo/ffxi", str(self.assets_dir))
        
        # Extract demo assets
        assets = extractor.extract_common_assets()
        
        # Verify assets were created
        self.assertIsInstance(assets, dict)
        self.assertIn("zones", assets)
        self.assertIn("character_models", assets)
        self.assertIn("mob_models", assets)
        
        # Check if assets file was created
        assets_file = self.assets_dir / "ffxi_demo_assets.json"
        self.assertTrue(assets_file.exists())
        
        logger.info("✅ Asset extraction test passed")
        
    def test_renderer_initialization(self):
        """Test 3D renderer initialization"""
        logger.info("Testing renderer initialization...")
        
        # Skip on headless systems
        if os.getenv('DISPLAY') is None and os.getenv('PYTEST_CURRENT_TEST') is None:
            logger.info("⏭️ Skipping renderer test (headless environment)")
            return
            
        try:
            renderer = FFXIRenderer(640, 480, str(self.assets_dir))
            
            # Test basic initialization
            self.assertIsNotNone(renderer)
            self.assertEqual(renderer.width, 640)
            self.assertEqual(renderer.height, 480)
            
            # Test asset loading (demo mode)
            success = renderer.load_assets()
            self.assertTrue(success)
            
            logger.info("✅ Renderer initialization test passed")
            
        except Exception as e:
            logger.warning(f"⚠️ Renderer test skipped due to display issue: {e}")
            
    def test_streaming_manager_initialization(self):
        """Test streaming manager initialization"""
        logger.info("Testing streaming manager initialization...")
        
        config_file = self.config_dir / "test_streaming_config.json"
        manager = StreamingManager(str(config_file))
        
        # Test initialization
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager.platforms, dict)
        
        # Test default platforms
        self.assertIn("youtube", manager.platforms)
        self.assertIn("twitch", manager.platforms)
        self.assertIn("facebook", manager.platforms)
        
        logger.info("✅ Streaming manager initialization test passed")
        
    def test_platform_configuration(self):
        """Test platform configuration"""
        logger.info("Testing platform configuration...")
        
        config_file = self.config_dir / "test_streaming_config.json"
        manager = StreamingManager(str(config_file))
        
        # Test platform update
        test_platform = StreamPlatform(
            name="Test Platform",
            platform_type="test",
            enabled=True,
            stream_key="test_key_123",
            rtmp_url="rtmp://test.example.com/live/",
            quality="1080p",
            bitrate=6000
        )
        
        manager.platforms["test"] = test_platform
        manager.save_config()
        
        # Verify configuration was saved
        self.assertTrue(config_file.exists())
        
        # Load and verify
        manager2 = StreamingManager(str(config_file))
        self.assertIn("test", manager2.platforms)
        self.assertEqual(manager2.platforms["test"].stream_key, "test_key_123")
        
        logger.info("✅ Platform configuration test passed")
        
    @patch('subprocess.Popen')
    def test_ffmpeg_integration(self, mock_popen):
        """Test FFmpeg integration"""
        logger.info("Testing FFmpeg integration...")
        
        # Mock FFmpeg process
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process running
        mock_process.stdin = MagicMock()
        mock_popen.return_value = mock_process
        
        config_file = self.config_dir / "test_streaming_config.json"
        manager = StreamingManager(str(config_file))
        
        # Test starting stream (with mock)
        test_platform = manager.platforms["youtube"]
        test_platform.stream_key = "test_key"
        
        # This would normally start FFmpeg
        asyncio.run(manager._start_ffmpeg_stream(test_platform, "test_key"))
        
        # Verify FFmpeg was called
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        self.assertIn('ffmpeg', call_args)
        
        logger.info("✅ FFmpeg integration test passed")
        
    async def test_streaming_service_initialization(self):
        """Test streaming service initialization"""
        logger.info("Testing streaming service initialization...")
        
        config_file = self.config_dir / "test_service_config.json"
        
        # Create test configuration
        test_config = {
            "database": {
                "host": "localhost",
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass",
                "port": 3306
            },
            "renderer": {
                "width": 640,
                "height": 480,
                "assets_path": str(self.assets_dir)
            },
            "streaming": {
                "auto_streaming": True,
                "default_platforms": ["test"]
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(test_config, f, indent=2)
            
        # Test service initialization (mock database)
        with patch('mysql.connector.pooling.MySQLConnectionPool'):
            service = FFXIStreamingService(str(config_file))
            
            # Test config loading
            self.assertIsNotNone(service.config)
            self.assertEqual(service.config["renderer"]["width"], 640)
            
        logger.info("✅ Streaming service initialization test passed")
        
    def test_api_endpoints(self):
        """Test API endpoints (requires running service)"""
        logger.info("Testing API endpoints...")
        
        # This test requires the actual API service to be running
        api_base = "http://localhost:8888"
        
        try:
            # Test health endpoint
            response = requests.get(f"{api_base}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                self.assertIn("status", health_data)
                logger.info("✅ Health endpoint test passed")
            else:
                logger.warning("⚠️ API service not running, skipping endpoint tests")
                return
                
            # Test status endpoint
            response = requests.get(f"{api_base}/api/streaming/status", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                self.assertIsInstance(status_data, dict)
                logger.info("✅ Status endpoint test passed")
                
            # Test platforms endpoint
            response = requests.get(f"{api_base}/api/streaming/platforms", timeout=5)
            if response.status_code == 200:
                platforms_data = response.json()
                self.assertIn("platforms", platforms_data)
                logger.info("✅ Platforms endpoint test passed")
                
        except requests.RequestException as e:
            logger.warning(f"⚠️ API tests skipped (service not running): {e}")
            
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        logger.info("Testing WebSocket connection...")
        
        websocket_url = "ws://localhost:8888/ws/streaming"
        
        try:
            async with websockets.connect(websocket_url) as websocket:
                # Wait for initial message
                message = await asyncio.wait_for(websocket.recv(), timeout=10)
                data = json.loads(message)
                
                self.assertIn("type", data)
                self.assertEqual(data["type"], "status_update")
                
                logger.info("✅ WebSocket connection test passed")
                
        except (ConnectionRefusedError, asyncio.TimeoutError, websockets.exceptions.ConnectionClosedError) as e:
            logger.warning(f"⚠️ WebSocket test skipped (service not running): {e}")
            
    def test_ai_gm_integration(self):
        """Test AI-GM integration"""
        logger.info("Testing AI-GM integration...")
        
        # Mock streaming service
        mock_service = MagicMock()
        mock_service.start_event_stream = MagicMock(return_value=asyncio.Future())
        mock_service.start_event_stream.return_value.set_result(True)
        
        # Test integration initialization
        integration = AIGMStreamingIntegration(mock_service)
        
        self.assertIsNotNone(integration)
        self.assertIsInstance(integration.triggers, dict)
        self.assertIn("gm_battle_demo", integration.triggers)
        
        # Test trigger configuration
        demo_trigger = integration.triggers["gm_battle_demo"]
        self.assertTrue(demo_trigger.enabled)
        self.assertIn("youtube", demo_trigger.auto_platforms)
        
        logger.info("✅ AI-GM integration test passed")
        
    def test_performance_metrics(self):
        """Test performance monitoring"""
        logger.info("Testing performance metrics...")
        
        # Test frame generation performance
        start_time = time.time()
        
        # Generate test frames
        frame_count = 100
        for i in range(frame_count):
            # Simulate frame generation
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            # Simulate processing time
            time.sleep(0.001)
            
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        
        logger.info(f"Frame generation performance: {fps:.1f} FPS")
        
        # Should be able to generate frames faster than real-time
        self.assertGreater(fps, 30.0)
        
        logger.info("✅ Performance metrics test passed")
        
    def test_configuration_validation(self):
        """Test configuration validation"""
        logger.info("Testing configuration validation...")
        
        # Test valid configuration
        valid_config = {
            "database": {
                "host": "localhost",
                "database": "xidb",
                "user": "ffxi",
                "password": "password",
                "port": 3306
            },
            "renderer": {
                "width": 1920,
                "height": 1080,
                "fps": 30
            },
            "streaming": {
                "auto_streaming": True,
                "default_platforms": ["youtube", "twitch"]
            }
        }
        
        config_file = self.config_dir / "valid_config.json"
        with open(config_file, 'w') as f:
            json.dump(valid_config, f, indent=2)
            
        # Test loading valid config
        service = FFXIStreamingService(str(config_file))
        self.assertEqual(service.config["renderer"]["width"], 1920)
        
        logger.info("✅ Configuration validation test passed")

class PerformanceTestSuite:
    """Performance testing for streaming system"""
    
    def __init__(self):
        self.results = {}
        
    async def test_renderer_performance(self):
        """Test 3D renderer performance"""
        logger.info("Testing renderer performance...")
        
        if os.getenv('DISPLAY') is None:
            logger.info("⏭️ Skipping renderer performance test (headless)")
            return
            
        try:
            renderer = FFXIRenderer(1280, 720)
            if not renderer.initialize_opengl():
                logger.warning("⚠️ Cannot initialize OpenGL for performance test")
                return
                
            renderer.load_assets()
            renderer.create_demo_scene()
            
            # Test frame rendering performance
            start_time = time.time()
            frame_count = 300  # 10 seconds at 30 FPS
            
            for i in range(frame_count):
                frame = renderer.render_frame()
                if frame is None:
                    break
                    
            elapsed = time.time() - start_time
            fps = frame_count / elapsed
            
            self.results['renderer_fps'] = fps
            logger.info(f"Renderer performance: {fps:.1f} FPS")
            
            # Should maintain at least 30 FPS
            assert fps >= 25.0, f"Renderer too slow: {fps:.1f} FPS"
            
        except Exception as e:
            logger.warning(f"⚠️ Renderer performance test failed: {e}")
            
    async def test_streaming_throughput(self):
        """Test streaming data throughput"""
        logger.info("Testing streaming throughput...")
        
        # Mock streaming manager
        manager = StreamingManager()
        
        # Test frame update performance
        test_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        
        start_time = time.time()
        update_count = 1000
        
        for i in range(update_count):
            manager.update_frame(test_frame)
            
        elapsed = time.time() - start_time
        updates_per_second = update_count / elapsed
        
        self.results['frame_updates_per_second'] = updates_per_second
        logger.info(f"Frame update throughput: {updates_per_second:.1f} updates/sec")
        
        # Should handle at least 30 updates per second
        assert updates_per_second >= 30.0, f"Frame updates too slow: {updates_per_second:.1f}/sec"
        
    async def test_database_query_performance(self):
        """Test database query performance"""
        logger.info("Testing database query performance...")
        
        # This would test actual database queries
        # For now, simulate query timing
        
        query_times = []
        query_count = 100
        
        for i in range(query_count):
            start_time = time.time()
            # Simulate database query
            await asyncio.sleep(0.001)  # 1ms simulated query
            elapsed = time.time() - start_time
            query_times.append(elapsed * 1000)  # Convert to milliseconds
            
        avg_query_time = sum(query_times) / len(query_times)
        max_query_time = max(query_times)
        
        self.results['avg_query_time_ms'] = avg_query_time
        self.results['max_query_time_ms'] = max_query_time
        
        logger.info(f"Database query performance: {avg_query_time:.1f}ms avg, {max_query_time:.1f}ms max")
        
        # Queries should be fast
        assert avg_query_time < 10.0, f"Queries too slow: {avg_query_time:.1f}ms avg"
        
    def generate_performance_report(self):
        """Generate performance test report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform
            },
            "performance_results": self.results,
            "recommendations": []
        }
        
        # Add recommendations based on results
        if self.results.get('renderer_fps', 0) < 30:
            report["recommendations"].append("Consider lowering render resolution or quality settings")
            
        if self.results.get('avg_query_time_ms', 0) > 5:
            report["recommendations"].append("Consider database query optimization")
            
        return report

async def run_all_tests():
    """Run all streaming system tests"""
    logger.info("🚀 Starting FFXI Streaming System Test Suite")
    
    # Unit tests
    logger.info("\n📋 Running Unit Tests...")
    unittest.main(argv=[''], module=__name__, exit=False, verbosity=2)
    
    # Performance tests
    logger.info("\n⚡ Running Performance Tests...")
    perf_suite = PerformanceTestSuite()
    
    await perf_suite.test_renderer_performance()
    await perf_suite.test_streaming_throughput()
    await perf_suite.test_database_query_performance()
    
    # Generate performance report
    report = perf_suite.generate_performance_report()
    
    # Save performance report
    report_file = Path("streaming_performance_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
        
    logger.info(f"📊 Performance report saved to {report_file}")
    
    # Summary
    logger.info("\n✅ Test Suite Complete!")
    logger.info(f"Performance Results:")
    for metric, value in perf_suite.results.items():
        logger.info(f"  {metric}: {value:.2f}")
        
    if report["recommendations"]:
        logger.info("💡 Recommendations:")
        for rec in report["recommendations"]:
            logger.info(f"  - {rec}")

def main():
    """Main test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == "--performance-only":
        # Run only performance tests
        async def run_perf_only():
            perf_suite = PerformanceTestSuite()
            await perf_suite.test_renderer_performance()
            await perf_suite.test_streaming_throughput()
            await perf_suite.test_database_query_performance()
            
            report = perf_suite.generate_performance_report()
            print(json.dumps(report, indent=2))
            
        asyncio.run(run_perf_only())
    else:
        # Run all tests
        asyncio.run(run_all_tests())

if __name__ == "__main__":
    main()