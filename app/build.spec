# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui/index.html', 'app/ui/'),
    ],
    hiddenimports=[
        'pyatv',
        'pyatv.protocols',
        'pyatv.protocols.companion',
        'pyatv.protocols.companion.api',
        'pyatv.protocols.airplay',
        'pyatv.protocols.mrp',
        'pyatv.protocols.dmap',
        'pyatv.protocols.raop',
        'zeroconf',
        'zeroconf._utils',
        'webview',
        'webview.platforms.cocoa',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TVRemote',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    target_arch=None,
    codesign_identity=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='TVRemote',
)

app = BUNDLE(
    coll,
    name='TV Remote.app',
    icon='resources/icon.icns',
    bundle_identifier='com.tvremote.app',
    info_plist={
        'CFBundleDisplayName': 'TV Remote',
        'CFBundleShortVersionString': '2.0.0',
        'NSLocalNetworkUsageDescription': 'Apple TV 기기를 검색하기 위해 로컬 네트워크 접근이 필요합니다.',
        'NSBonjourServices': ['_appletv-v2._tcp', '_companion-link._tcp'],
        'NSHighResolutionCapable': True,
    },
)
