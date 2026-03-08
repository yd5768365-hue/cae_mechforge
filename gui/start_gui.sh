#!/bin/bash
# MechForge AI GUI 启动器

echo "============================================"
echo "       MechForge AI GUI 启动器"
echo "============================================"
echo

# 检查 Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[错误] 未找到 Python，请先安装 Python 3.8+"
    exit 1
fi

# 使用 python3 或 python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "[信息] 正在启动 MechForge AI GUI..."
echo

# 启动 GUI
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
$PYTHON_CMD "$SCRIPT_DIR/run_gui.py" "$@"
