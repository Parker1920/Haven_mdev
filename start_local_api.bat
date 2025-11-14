@echo off
echo ========================================
echo   Haven Local Sync API Server
echo ========================================
echo.
echo Starting Flask API server on port 5000...
echo This server exposes VH-Database.db to Railway bot
echo.
echo KEEP THIS WINDOW OPEN while using the bot!
echo.
echo ========================================
echo.

cd /d "%~dp0"
python local_sync_api.py

pause
