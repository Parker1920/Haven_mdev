# Haven API Authentication Test Script (PowerShell)
# This script tests the local API and ngrok tunnel authentication

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Haven API Authentication Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$apiKey = "b14191847f8d166c3ddc3ec0d55fa1a86c644511ffb187ddaf7a8ec68de94aeb"
$headers = @{
    "X-API-Key" = $apiKey
}
$wrongHeaders = @{
    "X-API-Key" = "wrong-key-123"
}

Write-Host "Testing LOCAL API (http://localhost:5000)..." -ForegroundColor Yellow
Write-Host ""

# Test 1: Health check with correct API key
Write-Host "Test 1: Health check with CORRECT API key" -ForegroundColor Green
Write-Host "Expected: Success with 'healthy' status" -ForegroundColor Gray
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/health" -Headers $headers -Method Get
    Write-Host "✓ SUCCESS:" -ForegroundColor Green -NoNewline
    Write-Host " $($response | ConvertTo-Json -Compress)"
} catch {
    Write-Host "✗ FAILED:" -ForegroundColor Red -NoNewline
    Write-Host " $($_.Exception.Message)"
    Write-Host "  Make sure local_sync_api.py is running!" -ForegroundColor Yellow
}
Write-Host ""

# Test 2: Health check with wrong API key
Write-Host "Test 2: Health check with WRONG API key" -ForegroundColor Green
Write-Host "Expected: 401 Unauthorized error" -ForegroundColor Gray
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/health" -Headers $wrongHeaders -Method Get
    Write-Host "✗ UNEXPECTED:" -ForegroundColor Yellow -NoNewline
    Write-Host " Got successful response (should have failed!)"
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "✓ EXPECTED:" -ForegroundColor Green -NoNewline
        Write-Host " Got 401 Unauthorized (correct!)"
    } else {
        Write-Host "✗ FAILED:" -ForegroundColor Red -NoNewline
        Write-Host " $($_.Exception.Message)"
    }
}
Write-Host ""

# Test 3: Systems endpoint
Write-Host "Test 3: Systems endpoint (verify database access)" -ForegroundColor Green
Write-Host "Expected: JSON array of Haven systems" -ForegroundColor Gray
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/systems" -Headers $headers -Method Get
    Write-Host "✓ SUCCESS:" -ForegroundColor Green -NoNewline
    Write-Host " Retrieved $($response.systems.Count) systems from database"
    Write-Host "  First system: $($response.systems[0].name) ($($response.systems[0].abbreviation))" -ForegroundColor Gray
} catch {
    Write-Host "✗ FAILED:" -ForegroundColor Red -NoNewline
    Write-Host " $($_.Exception.Message)"
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test ngrok tunnel
Write-Host "Now testing ngrok tunnel..." -ForegroundColor Yellow
Write-Host ""
$ngrokUrl = Read-Host "Enter your ngrok URL (e.g., https://xyz.ngrok-free.app) or press Enter to skip"

if ($ngrokUrl) {
    Write-Host ""
    Write-Host "Testing through ngrok tunnel: $ngrokUrl" -ForegroundColor Yellow
    Write-Host ""

    try {
        $response = Invoke-RestMethod -Uri "$ngrokUrl/health" -Headers $headers -Method Get
        Write-Host "✓ NGROK SUCCESS:" -ForegroundColor Green -NoNewline
        Write-Host " $($response | ConvertTo-Json -Compress)"
        Write-Host ""
        Write-Host "🎉 ngrok tunnel is working correctly!" -ForegroundColor Green
    } catch {
        Write-Host "✗ NGROK FAILED:" -ForegroundColor Red -NoNewline
        Write-Host " $($_.Exception.Message)"
        Write-Host ""
        Write-Host "Troubleshooting:" -ForegroundColor Yellow
        Write-Host "  1. Make sure ngrok is running (ngrok http 5000)" -ForegroundColor Gray
        Write-Host "  2. Check the ngrok URL is correct" -ForegroundColor Gray
        Write-Host "  3. Visit http://127.0.0.1:4040 to see ngrok web interface" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary:" -ForegroundColor Cyan
Write-Host "  If all tests passed, your API authentication is working!" -ForegroundColor Gray
Write-Host "  Next steps:" -ForegroundColor Gray
Write-Host "    1. Update Railway HAVEN_SYNC_API_URL with your ngrok URL" -ForegroundColor Gray
Write-Host "    2. Restart Railway deployment" -ForegroundColor Gray
Write-Host "    3. Test a /discovery command in Discord" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
