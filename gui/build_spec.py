# -*- mode: python ; coding: utf-8 -*-
"""
MechForge AI PyInstaller 配置文件
使用: pyinstaller build_spec.py
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 项目配置
PROJECT_NAME = "MechForgeAI"
VERSION = "0.5.0"

# 项目路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PARENT_ROOT = os.path.dirname(PROJECT_ROOT)

# 收集数据文件
datas = [
    # 前端资源
    (os.path.join(PROJECT_ROOT, "index.html"), "."),
    (os.path.join(PROJECT_ROOT, "styles.css"), "."),
    (os.path.join(PROJECT_ROOT, "app.js"), "."),
    (os.path.join(PROJECT_ROOT, "dj-whale.png"), "."),
    (os.path.join(PROJECT_ROOT, "core"), "core"),
    (os.path.join(PROJECT_ROOT, "services"), "services"),
    (os.path.join(PROJECT_ROOT, "server.py"), "."),
    (os.path.join(PROJECT_ROOT, "server_config.yaml"), "."),
]

# 收集隐藏导入
hiddenimports = [
    # Web 框架
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",

    # FastAPI
    "fastapi",
    "starlette",
    "starlette.responses",
    "starlette.routing",
    "starlette.middleware",
    "starlette.middleware.cors",

    # Pydantic
    "pydantic",
    "pydantic_settings",

    # WebView
    "webview",
    "webview.platforms",
    "webview.platforms.winforms",

    # HTTP
    "http",
    "http.server",
    "urllib.parse",
    "h11",

    # 数据处理
    "json",
    "yaml",

    # 系统
    "threading",
    "socket",
    "logging",
    "pathlib",

    # MechForge Core
    "mechforge_core",
    "mechforge_core.config",
    "mechforge_core.logger",
    "mechforge_core.cache",
    "mechforge_core.security",
    "mechforge_core.database",

    # MechForge AI
    "mechforge_ai",
    "mechforge_ai.llm_client",
    "mechforge_ai.rag_engine",
    "mechforge_ai.command_handler",
    "mechforge_ai.prompts",

    # MechForge Theme
    "mechforge_theme",
    "mechforge_theme.colors",
    "mechforge_theme.components",

    # 数据库
    "sqlite3",

    # 其他
    "requests",
    "rich",
    "rich.console",
]

# 排除模块
excludes = [
    "tkinter",
    "unittest",
    "test",
    "tests",
    "pytest",
    "black",
    "mypy",
    "ruff",
    "sphinx",
    "docutils",
    "PyQt5",
    "PyQt6",
    "PySide2",
    "PySide6",
    "wx",
    "gtk",
]

# 分析配置
a = Analysis(
    [os.path.join(PROJECT_ROOT, "desktop_app_full.py")],
    pathex=[PROJECT_ROOT, PARENT_ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

# PYZ 配置
pyz = PYZ(a.pure)

# EXE 配置
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=PROJECT_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(PROJECT_ROOT, "dj-whale.png"),
)

# COLLECT 配置（目录模式）
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=PROJECT_NAME,
)