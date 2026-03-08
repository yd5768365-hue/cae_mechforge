@echo off
REM MechForge AI 桌面应用打包脚本 (PySide6 版本)
REM 将应用打包成独立的 .exe 文件

echo.
echo ============================================================
echo           MechForge AI 打包工具 v0.5.0 (PySide6)
echo ============================================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装
    pause
    exit /b 1
)

REM 检查 PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 PyInstaller...
    pip install pyinstaller
)

REM 检查 PySide6
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 PySide6...
    pip install PySide6
)

REM 检查其他依赖
echo [INFO] 检查依赖...
pip install fastapi uvicorn pydantic pydantic-settings rich requests pyyaml numpy -q

echo.
echo [INFO] 开始打包 (PySide6 + QWebEngineView)...
echo.

REM 执行打包（目录模式）
python build_pyside.py

echo.
echo ============================================================
echo                    打包完成！
echo ============================================================
echo.
echo 输出目录: dist\MechForgeAI\
echo 可执行文件: dist\MechForgeAI\MechForgeAI.exe
echo.
echo 双击运行 MechForgeAI.exe 启动应用
echo 注意: 首次启动可能需要几秒钟初始化 WebEngine
echo.

pause