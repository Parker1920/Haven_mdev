@echo off
echo ========================================
echo   ngrok Tunnel for Haven API
echo ========================================
echo.
echo Starting ngrok tunnel on port 5000...
echo.
echo COPY THE HTTPS URL that appears below!
echo You'll need to add it to Railway environment variables:
echo   HAVEN_SYNC_API_URL=https://YOUR-URL.ngrok.io/api
echo.
echo KEEP THIS WINDOW OPEN while using the bot!
echo.
echo ========================================
echo.

REM Try to run ngrok from PATH first
ngrok http 5000 2>nul

REM If that failed, try common installation locations
if errorlevel 1 (
    echo.
    echo ngrok not found in PATH, trying common locations...
    echo.

    if exist "C:\ngrok\ngrok.exe" (
        echo Found ngrok in C:\ngrok\
        C:\ngrok\ngrok.exe http 5000
    ) else if exist "%USERPROFILE%\Downloads\ngrok.exe" (
        echo Found ngrok in Downloads folder
        "%USERPROFILE%\Downloads\ngrok.exe" http 5000
    ) else if exist "%USERPROFILE%\Desktop\ngrok.exe" (
        echo Found ngrok in Desktop
        "%USERPROFILE%\Desktop\ngrok.exe" http 5000
    ) else (
        echo.
        echo ERROR: ngrok.exe not found!
        echo.
        echo Please do one of the following:
        echo   1. Extract ngrok.zip to C:\ngrok\
        echo   2. Run: setx PATH "%%PATH%%;C:\ngrok"
        echo   3. Read NGROK_SETUP.md for detailed instructions
        echo.
        pause
        exit /b 1
    )
)

pause
