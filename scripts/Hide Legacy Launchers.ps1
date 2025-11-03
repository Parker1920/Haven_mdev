# Hides legacy launcher files to keep only the new Control Room visible
# Usage: Right-click > Run with PowerShell (may require setting execution policy for the session)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Join-Path $root '..'

$targets = @(
  # Legacy launchers inside scripts
  (Join-Path $root 'scripts/Haven Control Room.bat'),
  # Root launchers to hide
  (Join-Path $root 'Haven Control Room.bat'),
  (Join-Path $root 'haven_control_room_mac.command')
)

foreach ($t in $targets) {
  if (Test-Path $t) {
    try {
      $item = Get-Item $t -Force
      if (-not ($item.Attributes -band [IO.FileAttributes]::Hidden)) {
        $item.Attributes = $item.Attributes -bor [IO.FileAttributes]::Hidden
        Write-Host "Hidden: $t" -ForegroundColor Green
      } else {
        Write-Host "Already hidden: $t" -ForegroundColor Yellow
      }
    } catch {
      Write-Host "Failed to hide: $t - $_" -ForegroundColor Red
    }
  }
}

Write-Host "Done."