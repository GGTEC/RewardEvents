# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os

block_cipher = None

a = Analysis(
    ['RewardEvents.py'],
    pathex=[],
    binaries=[],
    datas=[('.env', '.'),('./web', 'web')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)


splash = Splash('splash.png',
                binaries=a.binaries,
                datas=a.datas,
                always_on_top=False,
                text_pos=None)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    splash,
    splash.binaries,   
    [],
    name='RewardEvents',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_dir='None',
    upx_exclude=[],
    runtime_tmpdir="%appdata%/rewardeventsTemp",
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt',
    icon='web\icon.ico',
)
