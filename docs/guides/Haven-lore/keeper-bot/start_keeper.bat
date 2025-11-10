@echo off
REM The Keeper Discord Bot Launcher
REM Simple Windows batch script to start the bot

echo ========================================
echo Starting The Keeper Discord Bot...
echo ========================================
echo.

cd /d "%~dp0"
.venv\Scripts\python.exe src\main.py

pause
