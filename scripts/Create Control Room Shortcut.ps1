# Creates a Windows shortcut to the Haven Control Room at the repo root, with icon.
# Run from the repository root or via right-click > Run with PowerShell.

param(
    [switch]$Desktop
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path $root)) { $root = (Get-Location).Path }

$exe = Join-Path $root 'dist/HavenControlRoom.exe'
$py  = Join-Path $root 'src/control_room.py'
$ico = Join-Path $root 'config/icons/haven.ico'

if (-not (Test-Path $exe)) {
    Write-Host "Control Room EXE not found at $exe" -ForegroundColor Yellow
    Write-Host "Build it from the Control Room (Build EXE) or run:"
    Write-Host "  python -m PyInstaller --noconfirm --clean --windowed --onefile --name HavenControlRoom src/control_room.py"
    exit 1
}

$targetPath = $exe
$shortcutDir = if ($Desktop) { [Environment]::GetFolderPath('Desktop') } else { $root }
$shortcutPath = Join-Path $shortcutDir 'Haven Control Room.lnk'

$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $targetPath
$Shortcut.WorkingDirectory = $root
if (Test-Path $ico) {
    $Shortcut.IconLocation = $ico
} else {
    $Shortcut.IconLocation = "$exe,0"
}
$Shortcut.Description = 'Haven Control Room'
$Shortcut.Save()

Write-Host "Shortcut created at: $shortcutPath" -ForegroundColor Green
