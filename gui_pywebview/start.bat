@echo off
chcp 65001 >nul
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    MechForge AI v0.5.0                     ║
echo ║               PyWebView 轻量级桌面应用                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"
python desktop_app.py

pause