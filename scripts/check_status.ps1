<#
Check whether the Haven API is reachable and open the UI if it is.
Usage: .\scripts\check_status.ps1
#>
try {
  $res = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/status' -TimeoutSec 5
  if ($res -and $res.status -eq 'ok') {
    Write-Host "API status: OK; opening http://127.0.0.1:8000/"
    Start-Process 'http://127.0.0.1:8000/'
  } else {
    Write-Error "API returned unexpected response: $($res | ConvertTo-Json -Depth 3)"
  }
} catch {
  Write-Error "API unreachable: $_"
}
