@echo off
echo ========================================
echo   Haven API Authentication Test
echo ========================================
echo.

REM Set the API key
set API_KEY=b14191847f8d166c3ddc3ec0d55fa1a86c644511ffb187ddaf7a8ec68de94aeb

echo Testing LOCAL API (http://localhost:5000)...
echo.
echo Test 1: Health check with CORRECT API key
echo Expected: {"status":"healthy",...}
echo.
curl -H "X-API-Key: %API_KEY%" http://localhost:5000/health
echo.
echo.

echo Test 2: Health check with WRONG API key
echo Expected: {"error":"Unauthorized"} with 401 status
echo.
curl -H "X-API-Key: wrong-key-123" http://localhost:5000/health
echo.
echo.

echo Test 3: Systems endpoint (verify database access)
echo Expected: {"systems":[...]} with system data
echo.
curl -H "X-API-Key: %API_KEY%" http://localhost:5000/api/systems
echo.
echo.

echo ========================================
echo.
echo If all tests passed:
echo   - Test 1 should show "healthy" status
echo   - Test 2 should show "Unauthorized" error
echo   - Test 3 should show systems data
echo.
echo Next: Update the ngrok URL below and test through ngrok
echo.
set /p NGROK_URL="Enter your ngrok URL (e.g., https://xyz.ngrok-free.app): "
echo.

if not "%NGROK_URL%"=="" (
    echo Testing through ngrok tunnel...
    echo.
    curl -H "X-API-Key: %API_KEY%" %NGROK_URL%/health
    echo.
    echo.
    echo If you see "healthy" status, the tunnel is working!
)

echo.
echo ========================================
pause
