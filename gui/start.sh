#!/bin/bash
# MechForge AI GUI 启动脚本 (Linux/Mac)
# 启动后端服务器 + 桌面应用

echo ""
echo "============================================================"
echo "                  MechForge AI GUI"
echo "               Desktop Application v0.5.0"
echo "============================================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 未安装"
    echo "请先安装 Python 3.10+"
    exit 1
fi

# 激活虚拟环境（如果存在）
if [ -f "../.venv/bin/activate" ]; then
    echo "[INFO] 激活虚拟环境..."
    source ../.venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    echo "[INFO] 激活虚拟环境..."
    source venv/bin/activate
fi

echo "[INFO] 检查依赖..."
python3 -c "import fastapi" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[WARN] FastAPI 未安装，正在安装..."
    pip3 install fastapi uvicorn
fi

python3 -c "import mechforge_ai" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[WARN] MechForge AI 未安装，正在安装..."
    pip3 install -e ".."
fi

echo ""
echo "[INFO] 启动后端服务器 (端口 5000)..."
python3 server.py &
BACKEND_PID=$!

# 等待服务器启动
sleep 3

echo "[INFO] 启动桌面应用..."
python3 desktop_app.py

# 关闭后端服务器
echo ""
echo "[INFO] 关闭后端服务器..."
kill $BACKEND_PID 2>/dev/null

echo "[INFO] 应用已关闭"
