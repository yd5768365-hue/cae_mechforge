#!/usr/bin/env python3
"""
MechForge AI PyWebView 桌面应用打包脚本
使用 PyInstaller 打包为独立可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 路径设置
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
DIST_DIR = SCRIPT_DIR / "dist"
BUILD_DIR = SCRIPT_DIR / "build"

# 需要打包的数据文件
DATA_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "dj-whale.png",
    "core",
    "services",
]


def clean():
    """清理构建目录"""
    print("清理构建目录...")
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
    print("清理完成")


def build():
    """构建可执行文件"""
    print("开始构建...")

    # 收集数据文件参数
    datas = []
    for f in DATA_FILES:
        src = SCRIPT_DIR / f
        if src.exists():
            if src.is_dir():
                datas.append(f"--add-data={src};{f}")
            else:
                datas.append(f"--add-data={src};.")

    # PyInstaller 命令
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=MechForgeAI",
        "--icon=dj-whale.png",
        *datas,
        "desktop_app.py",
    ]

    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=SCRIPT_DIR, check=True)

    print(f"\n构建完成! 输出目录: {DIST_DIR}")


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="MechForge AI 打包脚本")
    parser.add_argument("--clean", action="store_true", help="清理构建目录")
    parser.add_argument("--build", action="store_true", help="构建可执行文件")
    args = parser.parse_args()

    if args.clean:
        clean()
    elif args.build:
        build()
    else:
        clean()
        build()


if __name__ == "__main__":
    main()