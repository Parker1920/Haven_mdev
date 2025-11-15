# PowerShell script to move all .md and .txt files from the root to appropriate docs subfolders (except AI-project)
# Adjust the $moves array as needed for new files or subfolders

$moves = @(
    @{File='NGROK_401_FIX.md'; Dest='docs/legacy-reports/'},
    @{File='NGROK_SETUP.md'; Dest='docs/legacy-reports/'},
    @{File='IMPORT_FIX_REPORT.md'; Dest='docs/legacy-reports/'},
    @{File='IMPORT_FIX_COMPLETE.md'; Dest='docs/legacy-reports/'},
    @{File='IMPORT_BUG_FIX_ANALYSIS.md'; Dest='docs/legacy-reports/'},
    @{File='FINAL_COMPREHENSIVE_AUDIT_REPORT.md'; Dest='docs/analysis/'},
    @{File='RAILWAY_FILES_TO_CREATE.md'; Dest='docs/deployment/'},
    @{File='RAILWAY_QUICK_START.md'; Dest='docs/deployment/'},
    @{File='RAILWAY_OPTION_B_GUIDE.md'; Dest='docs/deployment/'},
    @{File='RAILWAY_INDEX.md'; Dest='docs/deployment/'},
    @{File='RAILWAY_DEPLOYMENT_PLAN.md'; Dest='docs/deployment/'},
    @{File='RAILWAY_ARCHITECTURE.md'; Dest='docs/deployment/'},
    @{File='QUICK_START.md'; Dest='docs/quickstart/'},
    @{File='WHAT_WAS_FIXED.md'; Dest='docs/legacy-reports/'},
    @{File='VISUAL_SUMMARY.md'; Dest='docs/'},
    @{File='KEEPER_DISCOVERIES_FORMAT_SUPPORT.md'; Dest='docs/guides/'},
    @{File='START_HERE_RAILWAY.md'; Dest='docs/deployment/'},
    @{File='SOLUTION_SUMMARY.md'; Dest='docs/analysis/'},
    @{File='DELIVERY_SUMMARY.md'; Dest='docs/legacy-reports/'},
    @{File='DISCORD_BOT_RESET_SUMMARY.md'; Dest='docs/legacy-reports/'},
    @{File='DISCOVERIES_FIX_REPORT.md'; Dest='docs/legacy-reports/'},
    @{File='DISCOVERIES_QUICK_START.md'; Dest='docs/guides/'},
    @{File='DISCOVERY_IMPORT_FIX.md'; Dest='docs/legacy-reports/'},
    @{File='DISCOVERY_IMPORT_QUICK_FIX.md'; Dest='docs/legacy-reports/'},
    @{File='DISCOVERY_SYNC_GUIDE.md'; Dest='docs/guides/'},
    @{File='README.md'; Dest='docs/'},
    @{File='READ_ME_FIRST.md'; Dest='docs/'},
    @{File='raspberry_pi_idea.md'; Dest='docs/'},
    @{File='RPI_IMPLEMENTATION_GUIDE.md'; Dest='docs/'},
    @{File='RPI_CREATIVE_UPGRADES_SUMMARY.md'; Dest='docs/'},
    @{File='RPI_CREATIVE_UPGRADES_PART1.md'; Dest='docs/'},
    @{File='QUICK_REFERENCE_RPI.txt'; Dest='docs/'}
)

foreach ($move in $moves) {
    $src = Join-Path $PSScriptRoot $move.File
    $dst = Join-Path $PSScriptRoot $move.Dest
    if (Test-Path $src) {
        if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Path $dst -Force | Out-Null }
        Move-Item $src $dst -Force
        Write-Host "Moved $($move.File) to $($move.Dest)"
    } else {
        Write-Host "$($move.File) not found, skipping."
    }
}
