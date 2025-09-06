
# FFXI Launcher PyInstaller Spec File
# Generated automatically - do not edit manually

block_cipher = None

a = Analysis(
    ['/home/runner/work/FFXI-Server/FFXI-Server/tools/ffxi_launcher.py'],
    pathex=['/home/runner/work/FFXI-Server/FFXI-Server'],
    binaries=[],
    datas=[
        ('ashita/*.exe', 'ashita'),
        ('ashita/*.ini', 'ashita'),
        ('.env.example', '.'),
    ],
    hiddenimports=['tkinter', 'tkinter.ttk', 'configparser', 'urllib.request'],
    hookspath=[],
    hooksconfig={},
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
