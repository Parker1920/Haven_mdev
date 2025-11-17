<#
Open the default system browser pointing at the local Control Room web UI.
If the backend API is running, this opens the UI index page.

Usage: .\scripts\open_browser.ps1
#>
$uiUrl = 'http://127.0.0.1:8000/'
Start-Process $uiUrl
