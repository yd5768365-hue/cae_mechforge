@echo off
REM MechForge AI Desktop Application Launcher

echo ============================================================
echo                  MechForge AI v0.5.0
echo                   Desktop Launcher
echo ============================================================

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
pip install -q pywebview pyinstaller

REM Launch desktop application
python desktop_app.py

REM Deactivate virtual environment
deactivate

pause
