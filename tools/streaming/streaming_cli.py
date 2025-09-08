#!/usr/bin/env python3
"""
FFXI Streaming System CLI
Command-line interface for managing the FFXI real-time streaming system

Usage:
    python streaming_cli.py status
    python streaming_cli.py start-platform youtube "Live Stream"
    python streaming_cli.py config platform youtube --stream-key YOUR_KEY
    python streaming_cli.py demo
"""

import os
import sys
import asyncio
import click
import json
import requests
from typing import Dict, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

# Default API endpoints
DEFAULT_API_BASE = "http://localhost:8888"
DEFAULT_CONFIG_FILE = "streaming_cli_config.json"

class StreamingCLI:
    """CLI interface for FFXI streaming system"""
    
    def __init__(self, api_base: str = DEFAULT_API_BASE, config_file: str = DEFAULT_CONFIG_FILE):
        self.api_base = api_base.rstrip('/')
        self.config_file = Path(config_file)
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load CLI configuration"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {"api_base": DEFAULT_API_BASE, "auth_token": ""}
        
    def save_config(self):
        """Save CLI configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make API request with authentication"""
        headers = kwargs.pop('headers', {})
        if self.config.get('auth_token'):
            headers['Authorization'] = f"Bearer {self.config['auth_token']}"
            
        url = f"{self.api_base}{endpoint}"
        return requests.request(method, url, headers=headers, **kwargs)
        
    def get_status(self) -> Dict[str, Any]:
        """Get streaming system status"""
        try:
            response = self.make_request('GET', '/api/streaming/status')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            console.print(f"[red]Error getting status: {e}[/red]")
            return {}
            
    def get_platforms(self) -> Dict[str, Any]:
        """Get configured platforms"""
        try:
            response = self.make_request('GET', '/api/streaming/platforms')
            response.raise_for_status()
            return response.json().get('platforms', {})
        except requests.RequestException as e:
            console.print(f"[red]Error getting platforms: {e}[/red]")
            return {}
            
    def start_stream(self, platform: str, title: str, description: str = "") -> bool:
        """Start streaming to platform"""
        try:
            data = {
                "platform": platform,
                "title": title,
                "description": description,
                "auto_announce": True
            }
            response = self.make_request('POST', '/api/streaming/start', json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                console.print(f"[green]✅ Stream started on {platform}[/green]")
                return True
            else:
                console.print(f"[red]❌ Failed to start stream: {result.get('error', 'Unknown error')}[/red]")
                return False
                
        except requests.RequestException as e:
            console.print(f"[red]Error starting stream: {e}[/red]")
            return False
            
    def stop_stream(self, platform: str) -> bool:
        """Stop streaming to platform"""
        try:
            response = self.make_request('POST', f'/api/streaming/stop/{platform}')
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                console.print(f"[green]✅ Stream stopped on {platform}[/green]")
                return True
            else:
                console.print(f"[red]❌ Failed to stop stream: {result.get('error', 'Unknown error')}[/red]")
                return False
                
        except requests.RequestException as e:
            console.print(f"[red]Error stopping stream: {e}[/red]")
            return False
            
    def configure_platform(self, platform: str, **config) -> bool:
        """Configure platform settings"""
        try:
            platform_config = {
                "name": platform,
                "platform_type": platform,
                "enabled": True,
                **config
            }
            
            response = self.make_request('POST', f'/api/streaming/platforms/{platform}', 
                                       json=platform_config)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                console.print(f"[green]✅ Platform {platform} configured[/green]")
                return True
            else:
                console.print(f"[red]❌ Failed to configure platform: {result.get('error', 'Unknown error')}[/red]")
                return False
                
        except requests.RequestException as e:
            console.print(f"[red]Error configuring platform: {e}[/red]")
            return False

# CLI Commands
@click.group()
@click.option('--api-base', default=DEFAULT_API_BASE, help='API base URL')
@click.option('--config', default=DEFAULT_CONFIG_FILE, help='Config file path')
@click.pass_context
def cli(ctx, api_base, config):
    """FFXI Real-time Streaming System CLI"""
    ctx.ensure_object(dict)
    ctx.obj['cli'] = StreamingCLI(api_base, config)

@cli.command()
@click.pass_context
def status(ctx):
    """Show streaming system status"""
    streaming_cli = ctx.obj['cli']
    
    # Get status and platforms
    status_data = streaming_cli.get_status()
    platforms_data = streaming_cli.get_platforms()
    
    if not status_data:
        console.print("[red]❌ Unable to connect to streaming service[/red]")
        return
        
    # Create status display
    console.print(Panel.fit("🎥 FFXI Streaming System Status", style="bold blue"))
    
    # Main metrics
    metrics_table = Table(title="System Metrics")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="magenta")
    
    metrics_table.add_row("Service Status", "🟢 Active" if status_data.get('service_active') else "🔴 Inactive")
    metrics_table.add_row("Renderer Status", "🟢 Active" if status_data.get('renderer_active') else "🔴 Inactive")
    metrics_table.add_row("Active Sessions", str(status_data.get('active_sessions', 0)))
    metrics_table.add_row("Total Viewers", str(status_data.get('total_viewers', 0)))
    metrics_table.add_row("Renderer FPS", f"{status_data.get('renderer_fps', 0):.1f}")
    metrics_table.add_row("Tracked Players", str(status_data.get('tracked_players', 0)))
    metrics_table.add_row("Tracked Mobs", str(status_data.get('tracked_mobs', 0)))
    
    console.print(metrics_table)
    console.print()
    
    # Platforms table
    if platforms_data:
        platforms_table = Table(title="Streaming Platforms")
        platforms_table.add_column("Platform", style="cyan")
        platforms_table.add_column("Type", style="yellow")
        platforms_table.add_column("Status", style="magenta")
        platforms_table.add_column("Quality", style="green")
        
        for platform_name, platform_info in platforms_data.items():
            status_emoji = "🟢" if platform_info.get('enabled') else "🔴"
            streaming_status = "Streaming" if platform_info.get('streaming') else "Offline"
            
            platforms_table.add_row(
                platform_name,
                platform_info.get('platform_type', 'unknown'),
                f"{status_emoji} {streaming_status}",
                f"{platform_info.get('quality', 'N/A')} @ {platform_info.get('bitrate', 0)}kbps"
            )
            
        console.print(platforms_table)

@cli.command()
@click.argument('platform')
@click.argument('title')
@click.option('--description', default='', help='Stream description')
@click.pass_context
def start(ctx, platform, title, description):
    """Start streaming to a platform"""
    streaming_cli = ctx.obj['cli']
    
    console.print(f"🚀 Starting stream on {platform}...")
    
    success = streaming_cli.start_stream(platform, title, description)
    if success:
        console.print(f"[green]Stream '{title}' is now live on {platform}![/green]")
    else:
        console.print("[red]Failed to start stream. Check platform configuration.[/red]")

@cli.command()
@click.argument('platform')
@click.pass_context
def stop(ctx, platform):
    """Stop streaming to a platform"""
    streaming_cli = ctx.obj['cli']
    
    console.print(f"⏹️ Stopping stream on {platform}...")
    
    success = streaming_cli.stop_stream(platform)
    if success:
        console.print(f"[green]Stream stopped on {platform}[/green]")
    else:
        console.print("[red]Failed to stop stream[/red]")

@cli.command()
@click.argument('platform')
@click.option('--stream-key', help='Platform stream key')
@click.option('--api-key', help='Platform API key')
@click.option('--secret-key', help='Platform secret key')
@click.option('--rtmp-url', help='Custom RTMP URL')
@click.option('--quality', default='1080p', help='Stream quality')
@click.option('--bitrate', default=6000, type=int, help='Stream bitrate')
@click.pass_context
def config(ctx, platform, stream_key, api_key, secret_key, rtmp_url, quality, bitrate):
    """Configure a streaming platform"""
    streaming_cli = ctx.obj['cli']
    
    config_data = {
        'quality': quality,
        'bitrate': bitrate
    }
    
    if stream_key:
        config_data['stream_key'] = stream_key
    if api_key:
        config_data['api_key'] = api_key
    if secret_key:
        config_data['secret_key'] = secret_key
    if rtmp_url:
        config_data['rtmp_url'] = rtmp_url
        
    console.print(f"⚙️ Configuring {platform}...")
    
    success = streaming_cli.configure_platform(platform, **config_data)
    if success:
        console.print(f"[green]Platform {platform} configured successfully![/green]")
    else:
        console.print("[red]Failed to configure platform[/red]")

@cli.command()
@click.pass_context
def platforms(ctx):
    """List all configured platforms"""
    streaming_cli = ctx.obj['cli']
    
    platforms_data = streaming_cli.get_platforms()
    
    if not platforms_data:
        console.print("[yellow]No platforms configured[/yellow]")
        return
        
    table = Table(title="Configured Platforms")
    table.add_column("Platform", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Enabled", style="magenta")
    table.add_column("Quality", style="green")
    table.add_column("Has Stream Key", style="blue")
    
    for platform_name, platform_info in platforms_data.items():
        enabled_emoji = "✅" if platform_info.get('enabled') else "❌"
        has_key_emoji = "🔑" if platform_info.get('stream_key') else "🚫"
        
        table.add_row(
            platform_name,
            platform_info.get('platform_type', 'unknown'),
            enabled_emoji,
            f"{platform_info.get('quality', 'N/A')} @ {platform_info.get('bitrate', 0)}kbps",
            has_key_emoji
        )
        
    console.print(table)

@cli.command()
@click.option('--event-type', default='gm_demonstration', help='Type of event')
@click.option('--zone-id', default=230, type=int, help='Zone ID')
@click.option('--gm-name', default='GameMaster', help='GM name')
@click.option('--platforms', default='youtube,twitch', help='Platforms (comma-separated)')
@click.argument('title')
@click.argument('description', required=False)
@click.pass_context
def event(ctx, event_type, zone_id, gm_name, platforms, title, description):
    """Start an event stream"""
    streaming_cli = ctx.obj['cli']
    
    platform_list = [p.strip() for p in platforms.split(',')]
    
    try:
        data = {
            "event_type": event_type,
            "title": title,
            "description": description or f"{event_type} in zone {zone_id}",
            "zone_id": zone_id,
            "gm_name": gm_name,
            "platforms": platform_list
        }
        
        response = streaming_cli.make_request('POST', '/api/streaming/event', json=data)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            console.print(f"[green]✅ Event stream started: {title}[/green]")
            console.print(f"Event ID: {result.get('event_id')}")
            console.print(f"Platforms: {', '.join(platform_list)}")
        else:
            console.print(f"[red]❌ Failed to start event stream: {result.get('error', 'Unknown error')}[/red]")
            
    except requests.RequestException as e:
        console.print(f"[red]Error starting event stream: {e}[/red]")

@cli.command()
@click.pass_context
def demo(ctx):
    """Run streaming system demo"""
    streaming_cli = ctx.obj['cli']
    
    console.print(Panel.fit("🎬 FFXI Streaming System Demo", style="bold magenta"))
    
    # Check service status
    console.print("📡 Checking service status...")
    status_data = streaming_cli.get_status()
    
    if not status_data:
        console.print("[red]❌ Streaming service not available. Please start the service first.[/red]")
        console.print("\n[yellow]To start the service:[/yellow]")
        console.print("python ffxi_streaming_service.py")
        return
        
    console.print("[green]✅ Streaming service is running[/green]")
    
    # Demo configuration
    demo_platforms = {
        'demo_youtube': {
            'platform_type': 'youtube',
            'stream_key': 'demo_key_youtube',
            'quality': '1080p',
            'bitrate': 6000
        },
        'demo_twitch': {
            'platform_type': 'twitch',
            'stream_key': 'demo_key_twitch',
            'quality': '1080p',
            'bitrate': 6000
        }
    }
    
    # Configure demo platforms
    console.print("\n⚙️ Configuring demo platforms...")
    for platform_name, config in demo_platforms.items():
        streaming_cli.configure_platform(platform_name, **config)
        
    # Show final status
    console.print("\n📊 Final system status:")
    ctx.invoke(status)
    
    console.print("\n[green]🎉 Demo complete! The streaming system is ready to use.[/green]")
    console.print("\n[yellow]Next steps:[/yellow]")
    console.print("1. Configure real platform credentials: ffxi-streaming config <platform> --stream-key YOUR_KEY")
    console.print("2. Start streaming: ffxi-streaming start <platform> 'Your Stream Title'")
    console.print("3. Monitor through admin dashboard: http://localhost/admin.html")

@cli.command()
@click.pass_context
def health(ctx):
    """Check streaming service health"""
    streaming_cli = ctx.obj['cli']
    
    try:
        response = streaming_cli.make_request('GET', '/health')
        response.raise_for_status()
        health_data = response.json()
        
        status = health_data.get('status', 'unknown')
        timestamp = health_data.get('timestamp', 'unknown')
        
        if status == 'healthy':
            console.print(f"[green]✅ Service is healthy[/green] (checked at {timestamp})")
        else:
            console.print(f"[red]❌ Service is unhealthy[/red] (checked at {timestamp})")
            
    except requests.RequestException as e:
        console.print(f"[red]❌ Health check failed: {e}[/red]")

if __name__ == '__main__':
    cli()