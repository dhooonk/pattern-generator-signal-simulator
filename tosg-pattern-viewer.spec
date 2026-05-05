# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec — TOSG-400M Pattern Signal Viewer (Windows 단일 실행파일)

빌드:
    pyinstaller tosg-pattern-viewer.spec

산출물:
    dist/tosg-pattern-viewer.exe
"""

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['src', 'core', 'utils'],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('tosg-pattern-viewer.ico', '.'),
    ],
    hiddenimports=collect_submodules('matplotlib') + [
        'pandas',
        'openpyxl',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'IPython', 'jupyter'],
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
    name='tosg-pattern-viewer',
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
    icon='tosg-pattern-viewer.ico',
)
