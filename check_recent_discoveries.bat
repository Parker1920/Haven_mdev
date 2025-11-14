@echo off
echo ========================================
echo   VH-Database Recent Discoveries Check
echo ========================================
echo.

cd /d "%~dp0"
python check_recent_discoveries.py

pause
