<#
Starts backend and SPA dev server (if Node is installed) in parallel.
This is a convenience script for local development.

Usage: .\scripts\start_server_combo.ps1

#>
$ErrorActionPreference = 'Stop'

Write-Host "Starting backend API via scripts/start_backend.ps1 ..."
Start-Process -NoNewWindow -FilePath pwsh -ArgumentList '-NoExit','-Command',(Resolve-Path scripts/start_backend.ps1).Path

if (Get-Command npm -ErrorAction SilentlyContinue) {
  Write-Host "npm found. Starting SPA dev server via scripts/start_ui_dev.ps1 ..."
  Start-Process -NoNewWindow -FilePath pwsh -ArgumentList '-NoExit','-Command',(Resolve-Path scripts/start_ui_dev.ps1).Path
} else {
  Write-Warning "npm not found; skipping SPA dev server. The backend can still serve built assets from Haven-UI/dist." 
}

Write-Host "Both services have been started asynchronously.
 - Backend: http://127.0.0.1:8000/
 - SPA dev (if started): http://127.0.0.1:5173/"
