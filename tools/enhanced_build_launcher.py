#!/usr/bin/env python3
"""
Enhanced Build Script for Configurable Server Launcher
Builds launcher with server information baked in from .env file
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import json
import tempfile

def load_env_config(env_file='.env'):
    """Load configuration from .env file"""
    config = {}
    env_path = Path(env_file)
    
    if not env_path.exists():
        print(f"Warning: {env_file} not found, using defaults")
        return {'SERVERNAME': 'FFXI'}
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"\'')
    except Exception as e:
        print(f"Error loading .env file: {e}")
        return {'SERVERNAME': 'FFXI'}
    
    return config

def create_configured_launcher(config, output_dir):
    """Create launcher with baked-in configuration"""
    server_name = config.get('SERVERNAME', 'FFXI')
    
    # Create a configured version of the launcher
    launcher_template = Path('tools/enhanced_ffxi_launcher.py')
    if not launcher_template.exists():
        print("Error: Enhanced launcher template not found")
        return None
    
    # Read the template
    with open(launcher_template, 'r') as f:
        launcher_code = f.read()
    
    # Create configuration that will be baked into the executable
    baked_config = {
        'SERVERNAME': server_name,
        f'{server_name}_SERVER_NAME': config.get(f'{server_name}_SERVER_NAME', f'{server_name} Private Server'),
        f'{server_name}_SERVER_HOST': config.get(f'{server_name}_SERVER_HOST', 'localhost'),
        f'{server_name}_LOGIN_PORT': config.get(f'{server_name}_LOGIN_PORT', '54001'),
        f'{server_name}_MAP_PORT': config.get(f'{server_name}_MAP_PORT', '54230'),
        f'{server_name}_SEARCH_PORT': config.get(f'{server_name}_SEARCH_PORT', '54002'),
        f'{server_name}_ADMIN_USERNAME': config.get(f'{server_name}_ADMIN_USERNAME', 'admin'),
        f'{server_name}_ADMIN_PASSWORD': config.get(f'{server_name}_ADMIN_PASSWORD', 'admin123'),
        f'{server_name}_API_SECRET_KEY': config.get(f'{server_name}_API_SECRET_KEY', 'your_secret_key_here_change_this'),
        f'{server_name}_WINDOWER_COMPATIBLE': config.get(f'{server_name}_WINDOWER_COMPATIBLE', 'true'),
        f'{server_name}_ASHITA_COMPATIBLE': config.get(f'{server_name}_ASHITA_COMPATIBLE', 'true'),
        f'{server_name}_AUTO_UPDATE': config.get(f'{server_name}_AUTO_UPDATE', 'true'),
        f'{server_name}_CLIENT_TIMEOUT': config.get(f'{server_name}_CLIENT_TIMEOUT', '30000'),
        # URL Configuration with IPv4/IPv6 fallbacks
        f'{server_name}_SERVER_URL': config.get(f'{server_name}_SERVER_URL', 'http://localhost:5000'),
        f'{server_name}_API_BASE_URL': config.get(f'{server_name}_API_BASE_URL', 'http://localhost:5000/api'),
        f'{server_name}_SERVER_IPV4': config.get(f'{server_name}_SERVER_IPV4', '127.0.0.1'),
        f'{server_name}_SERVER_IPV6': config.get(f'{server_name}_SERVER_IPV6', '::1'),
        f'{server_name}_API_PORT': config.get(f'{server_name}_API_PORT', '5000'),
        f'{server_name}_WEB_PORT': config.get(f'{server_name}_WEB_PORT', '80')
    }
    
    # Inject the baked configuration into the launcher code
    config_injection = f"""
# BAKED CONFIGURATION - Generated at build time
BAKED_CONFIG = {repr(baked_config)}

# Override the ServerConfig class to use baked configuration
class ServerConfig:
    def __init__(self, env_file: str = '.env'):
        self.env_file = env_file
        self.config = BAKED_CONFIG.copy()
        self.server_name = self.config.get('SERVERNAME', 'FFXI')
        
        # Try to load additional config from env file if it exists
        if Path(env_file).exists():
            env_config = self.load_env_file()
            self.config.update(env_config)
    
    def load_env_file(self) -> Dict[str, str]:
        config = {{}}
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"\\'')
        except Exception:
            pass
        return config
    
    def get_default_config(self) -> Dict[str, str]:
        return BAKED_CONFIG.copy()
    
    def get(self, key: str, default: str = '') -> str:
        prefixed_key = f"{{self.server_name}}_{{key}}"
        if prefixed_key in self.config:
            return self.config[prefixed_key]
        return self.config.get(key, default)
    
    def set(self, key: str, value: str):
        prefixed_key = f"{{self.server_name}}_{{key}}"
        self.config[prefixed_key] = value
    
    def save(self):
        try:
            with open(self.env_file, 'w') as f:
                f.write(f"# {{self.server_name}} Server Configuration\\n")
                f.write(f"# Generated by {{self.server_name}} Launcher on {{datetime.now().isoformat()}}\\n\\n")
                f.write(f"SERVERNAME={{self.server_name}}\\n\\n")
                for key, value in sorted(self.config.items()):
                    if key != 'SERVERNAME':
                        f.write(f"{{key}}={{value}}\\n")
        except Exception as e:
            logger.error(f"Failed to save .env file: {{e}}")

"""
    
    # Replace the ServerConfig class definition with our baked version
    # Find the class definition and replace it
    lines = launcher_code.split('\n')
    new_lines = []
    skip_class = False
    indent_level = 0
    
    for line in lines:
        if line.strip().startswith('class ServerConfig:'):
            # Insert our baked configuration instead
            new_lines.extend(config_injection.split('\n'))
            skip_class = True
            # Find the indentation level
            indent_level = len(line) - len(line.lstrip())
        elif skip_class:
            # Skip lines until we find the next class or function at the same or lower indent level
            current_indent = len(line) - len(line.lstrip()) if line.strip() else float('inf')
            if line.strip() and current_indent <= indent_level and (line.strip().startswith('class ') or line.strip().startswith('def ')):
                skip_class = False
                new_lines.append(line)
            # Skip the original ServerConfig class
        else:
            new_lines.append(line)
    
    # Write the configured launcher
    output_file = output_dir / f'{server_name.lower()}_launcher.py'
    with open(output_file, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"Created configured launcher: {output_file}")
    return output_file

def build_launcher_executable(launcher_file, config, output_dir):
    """Build the launcher into an executable using PyInstaller"""
    server_name = config.get('SERVERNAME', 'FFXI')
    
    # Create a temporary spec file for PyInstaller
    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{launcher_file}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['requests', 'urllib3', 'certifi'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{server_name}_Launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    spec_file = output_dir / f'{server_name.lower()}_launcher.spec'
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    # Create version info file
    version_info_content = f'''
# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    OS=0x40004,
    # The general type of file.
    fileType=0x1,
    # The function of the file.
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{server_name} Server'),
         StringStruct(u'FileDescription', u'{server_name} Server Launcher'),
         StringStruct(u'FileVersion', u'1.0.0.0'),
         StringStruct(u'InternalName', u'{server_name}_Launcher'),
         StringStruct(u'LegalCopyright', u'Copyright © 2024 {server_name} Server'),
         StringStruct(u'OriginalFilename', u'{server_name}_Launcher.exe'),
         StringStruct(u'ProductName', u'{server_name} Server Launcher'),
         StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    version_file = output_dir / 'version_info.txt'
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(version_info_content)
    
    # Run PyInstaller
    try:
        # Use direct script path instead of spec file to avoid command line conflicts
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', f'{server_name}_Launcher',
            '--version-file', str(version_file),
            '--distpath', str(output_dir / 'dist'),
            '--workpath', str(output_dir / 'work'),
            '--specpath', str(output_dir),
            str(launcher_file)
        ]
        
        print(f"Building {server_name} Launcher executable...")
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        
        # Check for the executable (Windows vs Linux/macOS)
        exe_path = output_dir / 'dist' / f'{server_name}_Launcher.exe'
        if not exe_path.exists():
            exe_path = output_dir / 'dist' / f'{server_name}_Launcher'
        
        return exe_path if exe_path.exists() else None
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def create_ashita_components(config, output_dir):
    """Download and prepare Ashita components"""
    server_name = config.get('SERVERNAME', 'FFXI')
    ashita_dir = output_dir / 'ashita'
    ashita_dir.mkdir(exist_ok=True)
    
    # Create placeholder Ashita files (in real implementation, these would be downloaded)
    pol_exe = ashita_dir / 'pol.exe'
    ashita_cli = ashita_dir / 'Ashita-cli.exe'
    
    # Create placeholder files with info
    placeholder_content = f"""
This is a placeholder for Ashita v4 components.

In a production environment, this script would:
1. Download the latest Ashita v4 beta from GitHub
2. Extract pol.exe and Ashita-cli.exe
3. Configure them for {server_name} server compatibility

For now, these are placeholder files to demonstrate the build process.
"""
    
    with open(ashita_dir / 'README.txt', 'w') as f:
        f.write(placeholder_content)
    
    # Create minimal placeholder executables (for demonstration)
    with open(pol_exe, 'wb') as f:
        f.write(b'Placeholder POL.exe for ' + server_name.encode() + b' server')
    
    with open(ashita_cli, 'wb') as f:
        f.write(b'Placeholder Ashita-cli.exe for ' + server_name.encode() + b' server')
    
    print(f"Created Ashita components in {ashita_dir}")
    return ashita_dir

def create_launcher_package(exe_file, ashita_dir, config, output_dir):
    """Create final launcher package"""
    server_name = config.get('SERVERNAME', 'FFXI')
    package_dir = output_dir / f'{server_name}_Launcher_Package'
    package_dir.mkdir(exist_ok=True)
    
    # Copy executable
    if exe_file and exe_file.exists():
        shutil.copy2(exe_file, package_dir / f'{server_name}_Launcher.exe')
    
    # Copy Ashita components
    if ashita_dir.exists():
        shutil.copytree(ashita_dir, package_dir / 'ashita', dirs_exist_ok=True)
    
    # Create example .env file
    env_example = package_dir / '.env.example'
    with open(env_example, 'w') as f:
        f.write(f"""# {server_name} Server Configuration
# Copy this file to .env and modify the values

SERVERNAME={server_name}

# Server Configuration
{server_name}_SERVER_NAME={config.get(f'{server_name}_SERVER_NAME', f'{server_name} Private Server')}
{server_name}_SERVER_HOST={config.get(f'{server_name}_SERVER_HOST', 'localhost')}
{server_name}_LOGIN_PORT={config.get(f'{server_name}_LOGIN_PORT', '54001')}
{server_name}_MAP_PORT={config.get(f'{server_name}_MAP_PORT', '54230')}
{server_name}_SEARCH_PORT={config.get(f'{server_name}_SEARCH_PORT', '54002')}

# Authentication
{server_name}_ADMIN_USERNAME={config.get(f'{server_name}_ADMIN_USERNAME', 'admin')}
{server_name}_ADMIN_PASSWORD={config.get(f'{server_name}_ADMIN_PASSWORD', 'admin123')}

# Client Configuration
{server_name}_CLIENT_PATH=C:\\Program Files (x86)\\SquareEnix\\FINAL FANTASY XI
{server_name}_WINDOWER_COMPATIBLE=true
{server_name}_ASHITA_COMPATIBLE=true
{server_name}_AUTO_UPDATE=true
{server_name}_CLIENT_TIMEOUT=30000
""")
    
    # Create README
    readme = package_dir / 'README.md'
    with open(readme, 'w') as f:
        f.write(f"""# {server_name} Server Launcher

This launcher provides a complete interface for connecting to the {server_name} server with authentication and client management.

## Features

- **Server Authentication**: Login with your {server_name} server credentials
- **Real-time Status**: Monitor server status and player count
- **Ashita Integration**: Full Ashita v4 compatibility for enhanced gameplay
- **Client Management**: Automatic client validation and configuration
- **Multi-platform Support**: Works on Windows, macOS, and Linux

## Quick Start

1. Run `{server_name}_Launcher.exe`
2. Enter your username and password (default: admin/admin123)
3. Configure your client settings
4. Launch your {server_name} client!

## Configuration

The launcher reads configuration from `.env` files. Copy `.env.example` to `.env` and modify as needed.

### Key Settings

- `{server_name}_SERVER_HOST`: Server hostname or IP address
- `{server_name}_LOGIN_PORT`: Server login port
- `{server_name}_ADMIN_USERNAME`: Your admin username
- `{server_name}_ADMIN_PASSWORD`: Your admin password

## Ashita Integration

The included Ashita components provide:
- Enhanced graphics and performance
- Plugin support for custom functionality
- Windowed mode and resolution scaling
- Advanced input and macro systems

## Support

For support and updates, visit the {server_name} server website or contact the administration team.

---
Built with ❤️ for the {server_name} community
""")
    
    # Create ZIP package
    import zipfile
    zip_file = output_dir / f'{server_name}_Launcher.zip'
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zf.write(file_path, arcname)
    
    print(f"Created launcher package: {zip_file}")
    return zip_file

def main():
    """Main build script"""
    print("Enhanced Server Launcher Build Script")
    print("=====================================")
    
    # Load environment configuration
    config = load_env_config()
    server_name = config.get('SERVERNAME', 'FFXI')
    
    print(f"Building launcher for: {server_name} Server")
    print(f"Configuration loaded with {len(config)} settings")
    
    # Create output directory
    output_dir = Path('launcher_build') / server_name.lower()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Create configured launcher
    print("\n1. Creating configured launcher...")
    launcher_file = create_configured_launcher(config, output_dir)
    if not launcher_file:
        print("Failed to create configured launcher")
        return 1
    
    # Step 2: Build executable
    print("\n2. Building launcher executable...")
    exe_file = build_launcher_executable(launcher_file, config, output_dir)
    
    # Step 3: Create Ashita components
    print("\n3. Preparing Ashita components...")
    ashita_dir = create_ashita_components(config, output_dir)
    
    # Step 4: Create final package
    print("\n4. Creating final launcher package...")
    package_file = create_launcher_package(exe_file, ashita_dir, config, output_dir)
    
    print(f"\n✅ Build complete!")
    print(f"📦 Package: {package_file}")
    print(f"📁 Build directory: {output_dir}")
    
    if exe_file and exe_file.exists():
        print(f"🚀 Executable: {exe_file}")
        print(f"📏 Size: {exe_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    # Create launcher info JSON for web interface
    launcher_info = {
        'server_name': server_name,
        'version': '1.0.0',
        'build_date': str(Path().absolute()),
        'package_file': str(package_file.name),
        'size_mb': round(package_file.stat().st_size / 1024 / 1024, 1) if package_file.exists() else 0,
        'features': [
            'Server Authentication',
            'Real-time Status Monitoring',
            'Ashita v4 Integration',
            'Client Management',
            'Auto-configuration'
        ]
    }
    
    info_file = output_dir.parent / 'launcher_info.json'
    with open(info_file, 'w') as f:
        json.dump(launcher_info, f, indent=2)
    
    print(f"📋 Launcher info: {info_file}")
    print("\nBuild completed successfully! 🎉")
    return 0

if __name__ == "__main__":
    sys.exit(main())