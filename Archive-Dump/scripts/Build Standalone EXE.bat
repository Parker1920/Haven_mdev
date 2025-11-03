@echo off
setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0.."

echo ================================================
echo    Building Standalone Executables
echo ================================================
echo.
echo This will create .exe files that work without Python installed.
echo.

REM Check if Python is available
where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python is required to BUILD the executables.
  echo Install Python 3.10+ from https://www.python.org/downloads/
  pause
  exit /b 1
)

REM Ensure venv exists
if not exist .venv (
  echo Creating virtual environment...
  python -m venv .venv || goto :fail
)

REM Install/update dependencies including PyInstaller
echo Installing dependencies (including PyInstaller)...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r config\requirements.txt

echo.
echo Building GUI executable (Galactic Archive Terminal)...
".venv\Scripts\pyinstaller.exe" --clean config\gui.spec

echo.
echo Building Map Generator executable (Atlas Array)...
".venv\Scripts\pyinstaller.exe" --clean config\map.spec

echo.
echo ================================================
echo    BUILD COMPLETE!
echo ================================================
echo.
echo Executables are in the dist\ folder:
echo   - dist\Galactic Archive Terminal\Galactic Archive Terminal.exe
echo   - dist\Atlas Array\Atlas Array.exe
echo.
echo IMPORTANT: To distribute to friends:
echo   1. Copy the ENTIRE folder (e.g., "Galactic Archive Terminal")
echo   2. They can run the .exe directly - no Python needed!
echo.
pause
exit /b 0

:fail
echo Failed to set up the environment.
pause
exit /b 1
