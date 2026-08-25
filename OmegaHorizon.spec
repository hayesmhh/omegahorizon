# -*- mode: python ; coding: utf-8 -*-
# PyInstaller one-file Windows build specification for Omega Horizon.
# Run on Windows: pyinstaller --noconfirm --clean OmegaHorizon.spec

from PyInstaller.utils.hooks import collect_all

pygame_datas, pygame_binaries, pygame_hiddenimports = collect_all('pygame')

a = Analysis(
    ['omega_horizon_shmup.py'],
    pathex=[],
    binaries=pygame_binaries,
    datas=pygame_datas + [('assets', 'assets')],
    hiddenimports=pygame_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OmegaHorizon',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['omega_horizon.ico'],
    version='version_info.txt',
)
