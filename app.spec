# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# https://stackoverflow.com/questions/33144448/icons-in-pyqt-app-created-by-pyinstaller-wont-work-on-other-computers
a.datas += [('jh-pdf-merger.ico', 'jh-pdf-merger.ico', 'DATA')]
a.datas += [('lang/zh_CN.qm', 'lang/zh_CN.qm', 'DATA')]

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='JH PDF Merger',
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
    icon='jh-pdf-merger.ico',
)


coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='jh_pdf_merger',
)
