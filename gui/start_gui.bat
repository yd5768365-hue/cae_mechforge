@echo off
chcp 65001 >nul
echo ============================================
echo        MechForge AI GUI 启动器
echo ============================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 启动 GUI
echo [信息] 正在启动 MechForge AI GUI...
echo.
python "%~dp0run_gui.py" %*

pause
