@echo off
REM The Keeper Discord Bot - Restart Script
REM Use this after re-authorizing the bot

echo ========================================
echo The Keeper Bot - Clean Restart
echo ========================================
echo.

echo [1/3] Stopping any running instances...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq The Keeper*" 2>nul
timeout /t 2 >nul

echo [2/3] Clearing command cache...
echo.

cd /d "%~dp0"

echo [3/3] Starting The Keeper...
echo.
echo IMPORTANT: Make sure you've re-authorized the bot with:
echo https://discord.com/api/oauth2/authorize?client_id=1436510971446427720^&permissions=274878294016^&scope=bot%%20applications.commands
echo.
echo Press Ctrl+C to stop the bot
echo ========================================
echo.

.venv\Scripts\python.exe src\main.py

pause
