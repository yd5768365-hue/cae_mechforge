@echo off
REM MechForge AI GUI 启动脚本 (Windows)
REM 启动后端服务器 + 桌面应用

echo.
echo ============================================================
echo                   MechForge AI GUI
echo                Desktop Application v0.5.0
echo ============================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装或未添加到 PATH
    echo 请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 激活虚拟环境（如果存在）
if exist "..\.venv\Scripts\activate.bat" (
    echo [INFO] 激活虚拟环境...
    call ..\.venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo [INFO] 激活虚拟环境...
    call venv\Scripts\activate.bat
)

echo [INFO] 检查依赖...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [WARN] FastAPI 未安装，正在安装...
    pip install fastapi uvicorn
)

python -c "import mechforge_ai" >nul 2>&1
if errorlevel 1 (
    echo [WARN] MechForge AI 未安装，正在安装...
    pip install -e ".."
)

echo.
echo [INFO] 启动后端服务器 (端口 5000)...
start "MechForge AI Backend" cmd /k "python server.py"

REM 等待服务器启动
timeout /t 3 /nobreak >nul

echo [INFO] 启动桌面应用...
python desktop_app.py

echo.
echo [INFO] 应用已关闭
pause
