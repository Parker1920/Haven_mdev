# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../src/system_entry_modern.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../data', 'data'),
        ('../photos', 'photos'),
        ('../logs', 'logs'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
        'tkinter',
        'pandas',
        'jsonschema',
    ],
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
    [],
    exclude_binaries=True,
    name='Galactic Archive Terminal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Galactic Archive Terminal',
)
