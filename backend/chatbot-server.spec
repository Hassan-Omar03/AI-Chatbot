# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('.env.example', '.')],
    hiddenimports=['uvicorn', 'uvicorn.main', 'uvicorn.config', 'uvicorn.lifespan', 'uvicorn.lifespan.off', 'uvicorn.lifespan.on', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.http.h11_impl', 'uvicorn.loops', 'uvicorn.loops.asyncio', 'uvicorn.loops.auto', 'fastapi', 'starlette', 'starlette.routing', 'starlette.middleware', 'starlette.middleware.cors', 'pydantic', 'pydantic.main', 'dotenv', 'requests', 'email.mime.text', 'email.mime.multipart'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='chatbot-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='chatbot-server',
)
