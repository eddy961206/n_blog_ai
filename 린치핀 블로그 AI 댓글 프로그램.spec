# -*- mode: python ; coding: utf-8 -*-

my_program_name = "린치핀 블로그 AI 댓글 프로그램 v2.0"


a = Analysis(
    ["blog_automation_gui.py"],
    pathex=[],
    binaries=[],
    datas=[('build/assets/frame0/*', 'build/assets/frame0')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['_pycache_', 'venv', '.git', '.gitignore', 'test', '설정정보.ini'],
    noarchive=False
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=my_program_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='blog_icon.ico'
    )
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=my_program_name,
)
