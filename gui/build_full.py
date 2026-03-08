#!/usr/bin/env python3
"""
MechForge AI 桌面应用打包脚本 - 完整版
使用 PyInstaller 将应用打包成独立的 .exe 文件
包含后端服务器 + 前端界面
"""

import os
import sys
import shutil
import subprocess
import argparse
import platform


# 项目配置
PROJECT_NAME = "MechForgeAI"
VERSION = "0.5.0"
APP_SCRIPT = "desktop_app_full.py"
ICON_FILE = "dj-whale.png"

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PARENT_ROOT = os.path.dirname(PROJECT_ROOT)


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
        path = os.path.join(PROJECT_ROOT, f)
        if os.path.exists(path):
            data_files.append((path, f))

    # 前端目录
    frontend_dirs = ["core", "services"]
    for d in frontend_dirs:
        path = os.path.join(PROJECT_ROOT, d)
        if os.path.exists(path):
            data_files.append((path, d))

    # 后端服务器
    server_path = os.path.join(PROJECT_ROOT, "server.py")
    if os.path.exists(server_path):
        data_files.append((server_path, "."))

    # 配置文件
    config_path = os.path.join(PROJECT_ROOT, "server_config.yaml")
    if os.path.exists(config_path):
        data_files.append((config_path, "."))

    return data_files


def get_hidden_imports():
    """获取隐藏导入（PyInstaller 无法检测的模块）"""
    imports = [
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

    return imports


def get_exclude_modules():
    """获取需要排除的模块（减小包体积）"""
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

        # 大型库（如果不需要）
        # "torch",
        # "transformers",
        # "sklearn",
        # "pandas",
        # "numpy",

        # GUI 库（已用 webview）
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "wx",
        "gtk",
    ]

    return excludes


def build(output_dir="dist", one_file=False, console=False):
    """执行打包"""

    mode = "单文件" if one_file else "目录"
    window_mode = "控制台" if console else "窗口"

    print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              MechForge AI 打包工具 v{VERSION}                    ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

项目: {PROJECT_NAME}
输出: {os.path.abspath(output_dir)}
模式: {mode}
窗口: {window_mode}

============================================================
    """)

    # 切换到项目目录
    os.chdir(PROJECT_ROOT)

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

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
    args.extend(["--paths", PARENT_ROOT])
    args.extend(["--paths", PROJECT_ROOT])

    # 添加资源文件
    separator = ";" if platform.system() == "Windows" else ":"
    for src, dst in get_all_data_files():
        args.extend(["--add-data", f"{src}{separator}{dst}"])

    # 添加图标
    icon_path = os.path.join(PROJECT_ROOT, ICON_FILE)
    if os.path.exists(icon_path):
        args.extend(["--icon", icon_path])

    # 添加隐藏导入
    for imp in get_hidden_imports():
        args.extend(["--hidden-import", imp])

    # 添加排除模块
    for exc in get_exclude_modules():
        args.extend(["--exclude-module", exc])

    # 输出目录
    args.extend(["--distpath", output_dir])
    args.extend(["--workpath", os.path.join(output_dir, "build")])
    args.extend(["--specpath", output_dir])

    # 添加主脚本
    args.append(os.path.join(PROJECT_ROOT, APP_SCRIPT))

    print("执行命令:")
    print(" ".join(args[:10]) + " ...")
    print()

    # 执行打包
    try:
        result = subprocess.run(args, check=True, cwd=PROJECT_ROOT)
        print("\n[成功] 打包完成！")

        # 查找生成的 exe 文件
        if one_file:
            exe_path = os.path.join(output_dir, f"{PROJECT_NAME}.exe")
        else:
            exe_path = os.path.join(output_dir, PROJECT_NAME, f"{PROJECT_NAME}.exe")

        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / 1024 / 1024
            print(f"\n生成的文件: {exe_path}")
            print(f"文件大小: {size_mb:.2f} MB")

            if not one_file:
                dir_size = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(os.path.dirname(exe_path))
                    for filename in filenames
                ) / 1024 / 1024
                print(f"目录大小: {dir_size:.2f} MB")

            print("\n可以直接运行此 .exe 文件启动桌面应用！")

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
        path = os.path.join(PROJECT_ROOT, pattern)
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"  已删除: {pattern}")

    # 清理 spec 文件
    spec_file = os.path.join(PROJECT_ROOT, f"{PROJECT_NAME}.spec")
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"  已删除: {PROJECT_NAME}.spec")

    print("[清理] 完成")


def main():
    parser = argparse.ArgumentParser(description="MechForge AI 打包工具")
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