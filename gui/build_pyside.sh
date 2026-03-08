#!/bin/bash
# MechForge AI 桌面应用打包脚本 (PySide6 版本)
# 将应用打包成独立的可执行文件

echo ""
echo "============================================================"
echo "          MechForge AI 打包工具 v0.5.0 (PySide6)"
echo "============================================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 未安装"
    exit 1
fi

# 检查 PyInstaller
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "[INFO] 安装 PyInstaller..."
    pip3 install pyinstaller
fi

# 检查 PySide6
if ! python3 -c "import PySide6" &> /dev/null; then
    echo "[INFO] 安装 PySide6..."
    pip3 install PySide6
fi

# 检查其他依赖
echo "[INFO] 检查依赖..."
pip3 install fastapi uvicorn pydantic pydantic-settings rich requests pyyaml numpy -q

echo ""
echo "[INFO] 开始打包 (PySide6 + QWebEngineView)..."
echo ""

# 执行打包
python3 build_pyside.py

echo ""
echo "============================================================"
echo "                   打包完成！"
echo "============================================================"
echo ""
echo "输出目录: dist/MechForgeAI/"
echo "可执行文件: dist/MechForgeAI/MechForgeAI"
echo ""
echo "运行 ./dist/MechForgeAI/MechForgeAI 启动应用"
echo ""