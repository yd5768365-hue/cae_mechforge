#!/usr/bin/env python3
"""
MechForge AI 桌面应用打包脚本 - PySide6 版本
使用 PyInstaller 将应用打包成独立的 .exe 文件
基于 PySide6 + QWebEngineView，不依赖系统浏览器
"""

import os
import sys
import shutil
import subprocess
import argparse
import platform
from pathlib import Path


# 项目配置
PROJECT_NAME = "MechForgeAI"
VERSION = "0.5.0"
APP_SCRIPT = "desktop_pyside.py"
ICON_FILE = "dj-whale.png"

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.resolve()
PARENT_ROOT = PROJECT_ROOT.parent


def get_all_data_files():
    """获取所有需要打包的资源文件"""
    data_files = []

    # 前端资源
    frontend_files = [
        "index.html",
        "styles.css",
        "app.js",
        "dj-whale.png",
    ]

    for f in frontend_files:
        path = PROJECT_ROOT / f
        if path.exists():
            data_files.append((str(path), "."))

    # 前端目录
    frontend_dirs = ["core", "services"]
    for d in frontend_dirs:
        path = PROJECT_ROOT / d
        if path.exists():
            data_files.append((str(path), d))

    # 后端服务器
    server_path = PROJECT_ROOT / "server.py"
    if server_path.exists():
        data_files.append((str(server_path), "."))

    # 配置文件
    config_path = PROJECT_ROOT / "server_config.yaml"
    if config_path.exists():
        data_files.append((str(config_path), "."))

    return data_files


def get_hidden_imports():
    """获取隐藏导入"""
    imports = [
        # PySide6 核心
        "PySide6",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebEngineCore",
        "PySide6.QtNetwork",
        "PySide6.QtWebChannel",

        # WebEngine 相关
        "PySide6.QtWebEngine",
        
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

        # MechForge AI
        "mechforge_ai",
        "mechforge_ai.llm_client",
        "mechforge_ai.rag_engine",

        # 数据库
        "sqlite3",

        # 其他
        "requests",
        "rich",
        "rich.console",
        "numpy",
    ]

    return imports


def get_exclude_modules():
    """获取需要排除的模块"""
    excludes = [
        # 不需要的库
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

        # 其他 GUI 库
        "wx",
        "gtk",
        "PyQt5",
        "PyQt6",
        
        # 不需要的 PySide6 模块
        "PySide6.Qt3D",
        "PySide6.QtBluetooth",
        "PySide6.QtCharts",
        "PySide6.QtDataVisualization",
        "PySide6.QtDesigner",
        "PySide6.QtHelp",
        "PySide6.QtLocation",
        "PySide6.QtMultimedia",
        "PySide6.QtMultimediaWidgets",
        "PySide6.QtNfc",
        "PySide6.QtOpenGL",
        "PySide6.QtPositioning",
        "PySide6.QtQuick",
        "PySide6.QtQuickWidgets",
        "PySide6.QtRemoteObjects",
        "PySide6.QtScxml",
        "PySide6.QtSensors",
        "PySide6.QtSerialPort",
        "PySide6.QtSql",
        "PySide6.QtSvg",
        "PySide6.QtTest",
        "PySide6.QtTextToSpeech",
        "PySide6.QtUiTools",
        "PySide6.QtXml",
    ]

    return excludes


def build(output_dir="dist", one_file=False, console=False):
    """执行打包"""

    mode = "单文件" if one_file else "目录"
    window_mode = "控制台" if console else "窗口"

    print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║          MechForge AI 打包工具 v{VERSION} (PySide6)             ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

项目: {PROJECT_NAME}
输出: {(PROJECT_ROOT / output_dir).absolute()}
模式: {mode}
窗口: {window_mode}
框架: PySide6 + QWebEngineView

============================================================
    """)

    # 切换到项目目录
    os.chdir(PROJECT_ROOT)

    # 确保输出目录存在
    (PROJECT_ROOT / output_dir).mkdir(parents=True, exist_ok=True)

    # 构建 PyInstaller 参数
    args = [
        "pyinstaller",
        "--name", PROJECT_NAME,
        "--onedir" if not one_file else "--onefile",
        "--windowed" if not console else "--console",
        "--clean",
        "--noconfirm",
    ]

    # 添加项目路径到搜索路径
    args.extend(["--paths", str(PARENT_ROOT)])
    args.extend(["--paths", str(PROJECT_ROOT)])

    # 添加资源文件
    separator = ";" if platform.system() == "Windows" else ":"
    for src, dst in get_all_data_files():
        args.extend(["--add-data", f"{src}{separator}{dst}"])

    # 添加图标
    icon_path = PROJECT_ROOT / ICON_FILE
    if icon_path.exists():
        args.extend(["--icon", str(icon_path)])

    # 添加隐藏导入
    for imp in get_hidden_imports():
        args.extend(["--hidden-import", imp])

    # 添加排除模块
    for exc in get_exclude_modules():
        args.extend(["--exclude-module", exc])

    # 收集 PySide6 数据文件
    args.extend(["--collect-data", "PySide6"])
    args.extend(["--collect-binaries", "PySide6"])

    # 输出目录
    args.extend(["--distpath", output_dir])
    args.extend(["--workpath", str(Path(output_dir) / "build")])
    args.extend(["--specpath", output_dir])

    # 添加主脚本
    args.append(str(PROJECT_ROOT / APP_SCRIPT))

    print("执行命令:")
    print(" ".join(args[:15]) + " ...")
    print()

    # 执行打包
    try:
        result = subprocess.run(args, check=True, cwd=PROJECT_ROOT)
        print("\n[成功] 打包完成！")

        # 查找生成的 exe 文件
        if one_file:
            exe_path = PROJECT_ROOT / output_dir / f"{PROJECT_NAME}.exe"
        else:
            exe_path = PROJECT_ROOT / output_dir / PROJECT_NAME / f"{PROJECT_NAME}.exe"

        if exe_path.exists():
            size_mb = exe_path.stat().st_size / 1024 / 1024
            print(f"\n生成的文件: {exe_path}")
            print(f"文件大小: {size_mb:.2f} MB")

            if not one_file:
                dir_size = sum(
                    f.stat().st_size
                    for f in (exe_path.parent).rglob("*")
                    if f.is_file()
                ) / 1024 / 1024
                print(f"目录大小: {dir_size:.2f} MB")

            print("\n可以直接运行此 .exe 文件启动桌面应用！")
            print("注意: 首次启动可能需要几秒钟初始化 WebEngine")

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n[错误] 打包失败: {e}")
        return False
    except FileNotFoundError:
        print("\n[错误] 未找到 PyInstaller，请先安装:")
        print("  pip install pyinstaller")
        return False


def clean():
    """清理构建产物"""
    print("[清理] 删除构建文件...")

    patterns = ["build", "dist", "__pycache__"]
    for pattern in patterns:
        path = PROJECT_ROOT / pattern
        if path.exists():
            shutil.rmtree(path)
            print(f"  已删除: {pattern}")

    # 清理 spec 文件
    spec_file = PROJECT_ROOT / f"{PROJECT_NAME}.spec"
    if spec_file.exists():
        spec_file.unlink()
        print(f"  已删除: {PROJECT_NAME}.spec")

    print("[清理] 完成")


def main():
    parser = argparse.ArgumentParser(description="MechForge AI 打包工具 (PySide6)")
    parser.add_argument("-o", "--output", default="dist", help="输出目录")
    parser.add_argument("-f", "--onefile", action="store_true", help="打包为单文件")
    parser.add_argument("-c", "--console", action="store_true", help="显示控制台窗口")
    parser.add_argument("--clean", action="store_true", help="清理构建文件")

    args = parser.parse_args()

    if args.clean:
        clean()
    else:
        build(args.output, args.onefile, args.console)


if __name__ == "__main__":
    main()