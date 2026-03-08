#!/usr/bin/env python3
"""
MechForge AI 桌面应用打包脚本
使用 PyInstaller 将应用打包成独立的 .exe 文件
"""

import os
import sys
import shutil
import subprocess
import argparse


# 项目配置
PROJECT_NAME = "MechForgeAI"
VERSION = "0.5.0"
APP_SCRIPT = "desktop_app.py"
ICON_FILE = "dj-whale.png"

# 项目根目录 (gui 文件夹)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def get_pyinstaller_args(output_dir, one_file=True, windowed=True):
    """构建 PyInstaller 命令行参数"""

    # 收集需要打包的资源文件
    resource_files = [
        "index.html",
        "styles.css",
        "app.js",
        "dj-whale.png",
        "core",
        "services",
    ]

    args = [
        "pyinstaller",
        "--name", PROJECT_NAME,
        "--onedir" if not one_file else "--onefile",
        "--windowed" if windowed else "--console",
        "--clean",
        "--noconfirm",
    ]

    # 添加资源文件（使用 ; 分隔符，Windows 兼容）
    for rf in resource_files:
        rf_path = os.path.join(PROJECT_ROOT, rf)
        if os.path.exists(rf_path):
            args.extend(["--add-data", f"{rf_path};{rf}"])

    # 添加图标（如果存在）
    icon_path = os.path.join(PROJECT_ROOT, ICON_FILE)
    if os.path.exists(icon_path):
        args.extend(["--icon", icon_path])

    # 添加隐藏导入（避免 PyInstaller 无法检测的导入）
    hidden_imports = [
        "http.server",
        "urllib.parse",
        "threading",
        "json",
        "webview",
    ]
    for imp in hidden_imports:
        args.extend(["--hidden-import", imp])

    # 输出目录和工作目录
    args.extend(["--distpath", output_dir])
    args.extend(["--workpath", os.path.join(output_dir, "build")])
    args.extend(["--specpath", output_dir])

    # 添加主脚本
    args.append(os.path.join(PROJECT_ROOT, APP_SCRIPT))

    return args


def build(output_dir="dist"):
    """执行打包"""

    print(f"""
============================================================
               MechForge AI 打包工具 v{VERSION}
============================================================

项目: {PROJECT_NAME}
输出: {os.path.abspath(output_dir)}
模式: 单文件

============================================================
    """)

    # 切换到项目目录
    os.chdir(PROJECT_ROOT)

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 获取 PyInstaller 参数
    args = get_pyinstaller_args(output_dir)

    print(f"执行命令: {' '.join(args)}\n")

    # 执行打包
    try:
        result = subprocess.run(args, check=True, cwd=PROJECT_ROOT)
        print("\n[成功] 打包完成！")

        # 查找生成的 exe 文件
        exe_path = None
        exe_full_path = os.path.join(output_dir, f"{PROJECT_NAME}.exe")
        if os.path.exists(exe_full_path):
            exe_path = exe_full_path

        if exe_path:
            print(f"\n生成的 .exe 文件: {exe_path}")
            print(f"文件大小: {os.path.getsize(exe_path) / 1024 / 1024:.2f} MB")
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
    parser.add_argument("--clean", action="store_true", help="清理构建文件")

    args = parser.parse_args()

    if args.clean:
        clean()
    else:
        build(args.output)


if __name__ == "__main__":
    main()
