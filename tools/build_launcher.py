#!/usr/bin/env python3
"""
FFXI Launcher Builder
Creates compiled executables for the FFXI launcher for distribution
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import zipfile
import json

def create_launcher_executable():
    """Create standalone executable using PyInstaller"""
    
    print("🔧 Building FFXI Launcher executable...")
    
    # Ensure PyInstaller is available
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Create build directory
    build_dir = Path("launcher_build")
    build_dir.mkdir(exist_ok=True)
    
    # Copy launcher script
    launcher_script = Path("tools/ffxi_launcher.py")
    if not launcher_script.exists():
        print("❌ Launcher script not found")
        return False
    
    # Create PyInstaller spec file
    spec_content = f"""
# FFXI Launcher PyInstaller Spec File
# Generated automatically - do not edit manually

block_cipher = None

a = Analysis(
    ['{launcher_script.absolute()}'],
    pathex=['{Path.cwd().absolute()}'],
    binaries=[],
    datas=[
        ('ashita/*.exe', 'ashita'),
        ('ashita/*.ini', 'ashita'),
        ('.env.example', '.'),
    ],
    hiddenimports=['tkinter', 'tkinter.ttk', 'configparser', 'urllib.request'],
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
    name='FFXI_Launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version='version_info.txt'
)
"""
    
    # Create version info file
    version_info = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'FFXI Server Project'),
        StringStruct(u'FileDescription', u'FFXI Server Launcher with Ashita Integration'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'FFXI_Launcher'),
        StringStruct(u'LegalCopyright', u'Open Source'),
        StringStruct(u'OriginalFilename', u'FFXI_Launcher.exe'),
        StringStruct(u'ProductName', u'FFXI Server Launcher'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    spec_file = build_dir / "ffxi_launcher.spec"
    version_file = build_dir / "version_info.txt"
    
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    with open(version_file, 'w') as f:
        f.write(version_info)
    
    try:
        # Run PyInstaller directly with the script
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--onefile", 
            "--name", "FFXI_Launcher",
            "--distpath", str(build_dir / "dist"),
            "--workpath", str(build_dir / "work"),
            "--specpath", str(build_dir),
            str(launcher_script.absolute())
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable built successfully")
            return True
        else:
            print(f"❌ Build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_launcher_package():
    """Create complete launcher package for distribution"""
    
    print("📦 Creating launcher package...")
    
    package_dir = Path("web/downloads")
    package_dir.mkdir(exist_ok=True)
    
    # Create package structure
    launcher_package = package_dir / "ffxi_launcher_package"
    launcher_package.mkdir(exist_ok=True)
    
    # Copy executable
    exe_source = Path("launcher_build/dist/FFXI_Launcher")
    exe_target = launcher_package / "FFXI_Launcher.exe"
    
    if exe_source.exists():
        shutil.copy2(exe_source, exe_target)
        print("✅ Copied launcher executable")
    else:
        print("❌ Launcher executable not found")
        return False
    
    # Copy Ashita files
    ashita_dir = launcher_package / "ashita"
    ashita_dir.mkdir(exist_ok=True)
    
    for ashita_file in Path("ashita").glob("*"):
        if ashita_file.is_file():
            shutil.copy2(ashita_file, ashita_dir / ashita_file.name)
            print(f"✅ Copied {ashita_file.name}")
    
    # Copy configuration files
    if Path(".env.example").exists():
        shutil.copy2(".env.example", launcher_package / ".env.example")
        print("✅ Copied .env.example")
    
    # Create README for launcher package
    readme_content = """# FFXI Server Launcher

## Installation

1. Extract all files to a directory of your choice
2. Copy `.env.example` to `.env` and edit the server settings
3. Run `FFXI_Launcher.exe`

## Configuration

Edit the `.env` file to configure your server connection:

```
FFXI_SERVER_NAME=Your Server Name
FFXI_SERVER_HOST=your.server.com
FFXI_LOGIN_PORT=54001
FFXI_MAP_PORT=54230
FFXI_SEARCH_PORT=54002
FFXI_CLIENT_PATH=C:\\Program Files (x86)\\SquareEnix\\FINAL FANTASY XI
```

## Usage

### GUI Mode
Run `FFXI_Launcher.exe` for the graphical interface.

### Command Line Mode
```bash
FFXI_Launcher.exe --generate-config .env ashita_config.ini
FFXI_Launcher.exe --check-server .env
```

## Requirements

- Windows 7 or newer
- FFXI client installed
- .NET Framework 4.7.2 or newer
- VC++ Redistributable 2015-2022

## Ashita Integration

This launcher includes Ashita v4 integration for enhanced FFXI client functionality:

- Automatic configuration generation
- Client validation and updates
- Windowed mode support
- Plugin and addon compatibility

## Support

For support and updates, visit: https://github.com/mupoese/FFXI-Server
"""
    
    with open(launcher_package / "README.md", 'w') as f:
        f.write(readme_content)
    
    # Create ZIP package
    zip_path = package_dir / "FFXI_Launcher.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in launcher_package.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(launcher_package)
                zipf.write(file_path, arcname)
                print(f"📦 Added {arcname} to package")
    
    # Create package info JSON
    package_info = {
        "name": "FFXI Server Launcher",
        "version": "1.0.0",
        "description": "Advanced FFXI launcher with Ashita v4 integration",
        "filename": "FFXI_Launcher.zip",
        "size": zip_path.stat().st_size,
        "created": str(zip_path.stat().st_mtime),
        "requirements": [
            "Windows 7 or newer",
            "FFXI client installed",
            ".NET Framework 4.7.2+",
            "VC++ Redistributable 2015-2022"
        ],
        "features": [
            "GUI and CLI interfaces",
            "Ashita v4 integration",
            "Automatic configuration generation",
            "Server status checking",
            "Client validation",
            ".env file configuration"
        ]
    }
    
    with open(package_dir / "launcher_info.json", 'w') as f:
        json.dump(package_info, f, indent=2)
    
    print(f"✅ Created launcher package: {zip_path}")
    print(f"📊 Package size: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    return True

def main():
    """Main build process"""
    print("🚀 FFXI Launcher Build Process")
    print("=" * 50)
    
    # Step 1: Build executable
    if not create_launcher_executable():
        print("❌ Failed to build executable")
        sys.exit(1)
    
    # Step 2: Create package
    if not create_launcher_package():
        print("❌ Failed to create package")
        sys.exit(1)
    
    print("\n✅ Build process completed successfully!")
    print("\nPackage contents:")
    print("- FFXI_Launcher.exe (GUI and CLI launcher)")
    print("- ashita/ (Ashita v4 integration files)")
    print("- .env.example (Configuration template)")
    print("- README.md (Documentation)")
    
    print("\nFiles created:")
    print("- web/downloads/FFXI_Launcher.zip (Complete package)")
    print("- web/downloads/launcher_info.json (Package metadata)")

if __name__ == "__main__":
    main()