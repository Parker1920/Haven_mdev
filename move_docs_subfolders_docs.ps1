# PowerShell script to move .md files from docs root to appropriate subfolders
# Adjust the $moves array as needed for new files or subfolders

$moves = @(
    @{File='BOT_SYNC_IMPLEMENTATION_SUMMARY.md'; Dest='analysis/'},
    @{File='BOT_SYNC_QUICK_REFERENCE.md'; Dest='analysis/'},
    @{File='DOCUMENTATION_ORGANIZATION.md'; Dest='dev/'},
    @{File='FEATURE_RECOMMENDATIONS.md'; Dest='dev/'},
    @{File='MOON_DATA_POINT_OVERHAUL.md'; Dest='analysis/'},
    @{File='QUICK_START_REFERENCE.md'; Dest='quickstart/'},
    @{File='Raspberry_Pi_5_Complete_Beginner_Guide.md'; Dest='dev/'},
    @{File='raspberry_pi_idea.md'; Dest='dev/'},
    @{File='README.md'; Dest='dev/'},
    @{File='READ_ME_FIRST.md'; Dest='dev/'},
    @{File='ROOT_CLEANUP_SUMMARY.md'; Dest='analysis/'},
    @{File='RPI_CREATIVE_UPGRADES_PART1.md'; Dest='dev/'},
    @{File='RPI_CREATIVE_UPGRADES_SUMMARY.md'; Dest='dev/'},
    @{File='RPI_IMPLEMENTATION_GUIDE.md'; Dest='dev/'},
    @{File='TEST_MANAGER_IMPLEMENTATION_SUMMARY.md'; Dest='analysis/'},
    @{File='VISUAL_SUMMARY.md'; Dest='analysis/'}
)

$docsRoot = $PSScriptRoot
foreach ($move in $moves) {
    $src = Join-Path $docsRoot $move.File
    $dst = Join-Path $docsRoot $move.Dest
    if (Test-Path $src) {
        if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Path $dst -Force | Out-Null }
        Move-Item $src $dst -Force
        Write-Host "Moved $($move.File) to $($move.Dest)"
    } else {
        Write-Host "$($move.File) not found, skipping."
    }
}
