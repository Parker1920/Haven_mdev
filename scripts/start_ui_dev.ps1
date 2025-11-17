<#
Start the Haven UI Dev server (Vite) if Node/npm is available.

This script is optional—if Node/npm is not installed or you prefer to use the built static files
from `Haven-UI/dist`, you can skip this.

Usage:
  .\scripts\start_ui_dev.ps1

Important: run this from project root (the script uses relative paths).
#>
$ErrorActionPreference = 'Stop'

$uiDir = (Resolve-Path 'Haven-UI').Path
Push-Location $uiDir
try {
  if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "npm not found; install Node.js and npm (https://nodejs.org/) to run the dev server."
    exit 1
  }
  Write-Host "Starting SPA dev server (Vite) in $uiDir..."
  Start-Process -NoNewWindow -FilePath npm -ArgumentList 'run','dev' -WorkingDirectory $uiDir
  Write-Host "Vite dev server should open at http://127.0.0.1:5173 by default (or check the terminal)."
} finally {
  Pop-Location
}
