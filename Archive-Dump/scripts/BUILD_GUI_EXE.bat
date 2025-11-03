@echo off
echo ================================================
echo    Quick Build - Standalone Executables
echo ================================================
echo.
echo Building System Entry Wizard only (this takes 2-3 minutes)...
echo.

cd /d "%~dp0.."
".venv\Scripts\pyinstaller.exe" --noconfirm --onedir --windowed ^
    --name "Galactic Archive Terminal" ^
    --add-data "data;data" ^
    --add-data "photos;photos" ^
    --hidden-import customtkinter ^
    --hidden-import pandas ^
    --hidden-import jsonschema ^
    "src\system_entry_wizard.py"

echo.
echo ================================================
echo DONE! Check the dist\ folder
echo ================================================
echo.
echo To share with friends:
echo 1. Zip the folder: dist\Galactic Archive Terminal\
echo 2. They extract and run: Galactic Archive Terminal.exe
echo.
pause
