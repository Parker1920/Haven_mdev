@echo off
echo ========================================
echo   Test Keeper Bot Locally
echo ========================================
echo.
echo This tests the bot on your computer (not Railway)
echo.
echo Make sure VH-Database.db exists at:
echo   data\VH-Database.db
echo.
echo ========================================
echo.

cd /d "%~dp0\docs\guides\Haven-lore\keeper-bot"
python src/main.py

pause
