# First Run Setup for Haven Control Room
# - Installs Python if missing (winget preferred; fallback to direct download)
# - Creates a local virtual environment (.venv)
# - Installs Python dependencies from config/requirements.txt
# - Creates a Desktop shortcut to the launcher
# - Optionally launches the Control Room after setup

[CmdletBinding()]
param(
    [switch]$AutoLaunch
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Write-Log {
    param([string]$Message)
    $timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $line = "[$timestamp] $Message"
    Write-Host $line
    try { Add-Content -Path $Global:LogPath -Value $line -Encoding UTF8 } catch {}
}

# Resolve paths
$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot  = Split-Path -Parent $ScriptDir
$VenvPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'
$Requirements = Join-Path $RepoRoot 'config\requirements.txt'
$LogsDir = Join-Path $RepoRoot 'logs'
if (-not (Test-Path $LogsDir)) { New-Item -ItemType Directory -Path $LogsDir | Out-Null }
$Global:LogPath = Join-Path $LogsDir ("first-run-" + (Get-Date -Format 'yyyy-MM-dd_HHmmss') + ".log")

Write-Log "Starting First Run Setup at $RepoRoot"

function Get-PythonCmd {
    if (Test-Path $VenvPython) { return $VenvPython }
    $py = (Get-Command py -ErrorAction SilentlyContinue)
    if ($py) { return 'py' }
    $pyth = (Get-Command python -ErrorAction SilentlyContinue)
    if ($pyth) { return 'python' }
    return $null
}

function Install-PythonIfMissing {
    $cmd = Get-PythonCmd
    if ($cmd) {
        Write-Log "Python found via: $cmd"
        return
    }
    Write-Log "Python not found. Attempting installation via winget."
    $winget = (Get-Command winget -ErrorAction SilentlyContinue)
    if ($winget) {
        try {
            $pkgId = 'Python.Python.3.11'
            Write-Log "Installing Python using winget package $pkgId"
            $args = @('install','--id', $pkgId, '-e', '--scope','user','--accept-package-agreements','--accept-source-agreements')
            $p = Start-Process -FilePath $winget.Source -ArgumentList $args -PassThru -Wait -NoNewWindow
            Write-Log "winget exit code: $($p.ExitCode)"
        } catch {
            Write-Log "winget install failed: $($_.Exception.Message)"
        }
    } else {
        Write-Log "winget not available. Attempting direct download from python.org"
        try {
            $tmp = [System.IO.Path]::Combine($env:TEMP, 'python-installer.exe')
            $url = 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe'
            Write-Log "Downloading $url to $tmp"
            Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing
            Write-Log "Running installer silently"
            $args = @('/quiet','InstallAllUsers=0','PrependPath=1','Include_test=0')
            $p = Start-Process -FilePath $tmp -ArgumentList $args -PassThru -Wait
            Write-Log "Installer exit code: $($p.ExitCode)"
        } catch {
            Write-Log "Direct download/install failed: $($_.Exception.Message)"
        }
    }
}

function Ensure-VenvAndDeps {
    if (-not (Test-Path $VenvPython)) {
        Write-Log "Creating virtual environment (.venv)"
        $cmd = Get-PythonCmd
        if (-not $cmd) { throw "Python still not available after install." }
        $args = @('-m','venv','.venv')
        if ($cmd -eq 'py') { $args = @('-3') + $args }
        $p = Start-Process -FilePath $cmd -ArgumentList $args -WorkingDirectory $RepoRoot -PassThru -Wait -NoNewWindow
        Write-Log "venv creation exit code: $($p.ExitCode)"
    } else {
        Write-Log ".venv already exists"
    }
    if (-not (Test-Path $VenvPython)) { throw ".venv python not found at $VenvPython" }

    Write-Log "Upgrading pip"
    $p = Start-Process -FilePath $VenvPython -ArgumentList @('-m','pip','install','--upgrade','pip') -WorkingDirectory $RepoRoot -PassThru -Wait -NoNewWindow
    Write-Log "pip upgrade exit code: $($p.ExitCode)"

    if (Test-Path $Requirements) {
        Write-Log "Installing requirements from $Requirements"
        $p = Start-Process -FilePath $VenvPython -ArgumentList @('-m','pip','install','-r', $Requirements) -WorkingDirectory $RepoRoot -PassThru -Wait -NoNewWindow
        Write-Log "requirements install exit code: $($p.ExitCode)"
    } else {
        Write-Log "requirements.txt not found; skipping dependency install"
    }
}

function Create-Shortcut {
    try {
        $shortcutScript = Join-Path $RepoRoot 'scripts/Create Control Room Shortcut.ps1'
        if (Test-Path $shortcutScript) {
            Write-Log "Creating shortcut via existing script"
            & powershell -NoProfile -ExecutionPolicy Bypass -File $shortcutScript | Out-Null
            return
        }
        Write-Log "Creating Desktop shortcut via COM"
        $WshShell = New-Object -ComObject WScript.Shell
        $Desktop = [Environment]::GetFolderPath('Desktop')
        $ShortcutPath = Join-Path $Desktop 'Haven Control Room.lnk'
        $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
        $Shortcut.TargetPath = Join-Path $RepoRoot 'Haven Control Room.bat'
        $Shortcut.WorkingDirectory = $RepoRoot
        $Shortcut.IconLocation = (Join-Path $RepoRoot 'config/icons/haven.ico')
        $Shortcut.Save()
    } catch {
        Write-Log "Failed to create shortcut: $($_.Exception.Message)"
    }
}

try {
    Install-PythonIfMissing
    Ensure-VenvAndDeps
    Create-Shortcut
    Write-Log "Setup complete."
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show("Setup complete. You can now open 'Haven Control Room.bat' or use the desktop shortcut.", 'Haven Control Room') | Out-Null
    if ($AutoLaunch) {
        Write-Log "Auto-launching Control Room"
        Start-Process -FilePath (Join-Path $RepoRoot 'Haven Control Room.bat') -WorkingDirectory $RepoRoot | Out-Null
    }
} catch {
    Write-Log "Setup failed: $($_.Exception.Message)"
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show("Setup failed. See logs in the 'logs' folder.", 'Haven Control Room - Setup Error') | Out-Null
    exit 1
}

exit 0
