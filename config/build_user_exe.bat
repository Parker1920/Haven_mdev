@echo off
REM Build Haven Control Room - User Edition
REM This creates a standalone EXE package for end users

echo ========================================
echo Haven Control Room - User Edition Build
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

echo [1/5] Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo [2/5] Installing/upgrading PyInstaller...
python -m pip install --upgrade pyinstaller

echo.
echo [3/5] Building User Edition EXE...
echo This may take several minutes...
pyinstaller config\pyinstaller\HavenControlRoom_User.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for errors.
    pause
    exit /b 1
)

echo.
echo [4/5] Creating distribution package structure...

REM Create the user distribution folder
if not exist "dist\HavenControlRoom_User\" mkdir "dist\HavenControlRoom_User"

REM Copy the EXE
echo Copying EXE...
copy "dist\HavenControlRoom.exe" "dist\HavenControlRoom_User\" >nul

REM Copy reference data files
echo Copying reference data files...
copy "dist\clean_data.json" "dist\HavenControlRoom_User\" >nul
copy "dist\example_data.json" "dist\HavenControlRoom_User\" >nul

REM Copy README and Quick Start
echo Copying documentation...
copy "dist\README_USER.md" "dist\HavenControlRoom_User\README.md" >nul
copy "dist\QUICK_START.txt" "dist\HavenControlRoom_User\QUICK_START.txt" >nul

REM Create the files subdirectory structure
echo Creating files directory structure...
if not exist "dist\HavenControlRoom_User\files\" mkdir "dist\HavenControlRoom_User\files"
if not exist "dist\HavenControlRoom_User\files\logs\" mkdir "dist\HavenControlRoom_User\files\logs"
if not exist "dist\HavenControlRoom_User\files\photos\" mkdir "dist\HavenControlRoom_User\files\photos"
if not exist "dist\HavenControlRoom_User\files\maps\" mkdir "dist\HavenControlRoom_User\files\maps"
if not exist "dist\HavenControlRoom_User\files\backups\" mkdir "dist\HavenControlRoom_User\files\backups"

REM Create a placeholder file in empty directories so they get included in zip
echo. > "dist\HavenControlRoom_User\files\logs\.gitkeep"
echo. > "dist\HavenControlRoom_User\files\photos\.gitkeep"
echo. > "dist\HavenControlRoom_User\files\maps\.gitkeep"
echo. > "dist\HavenControlRoom_User\files\backups\.gitkeep"

echo.
echo [5/5] Creating ZIP archive...

REM Get current date for filename
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set DATE_STR=%datetime:~0,8%

REM Create ZIP using PowerShell
powershell -Command "Compress-Archive -Path 'dist\HavenControlRoom_User\*' -DestinationPath 'dist\HavenControlRoom_User_%DATE_STR%.zip' -Force"

echo.
echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo.
echo User Edition package created:
echo   Location: dist\HavenControlRoom_User\
echo   ZIP file: dist\HavenControlRoom_User_%DATE_STR%.zip
echo.
echo Package contents:
echo   - HavenControlRoom.exe (standalone executable)
echo   - clean_data.json (empty starting point)
echo   - example_data.json (50 demo systems)
echo   - README.md (comprehensive user guide)
echo   - QUICK_START.txt (quick reference)
echo   - files\ (folder for user data, logs, photos, maps)
echo.
echo You can now distribute the HavenControlRoom_User folder
echo or the ZIP file to your users!
echo.
pause
