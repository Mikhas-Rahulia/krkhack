# Refreshes the Crossweb snapshot from THIS machine's (residential) IP and pushes it to GitHub.
# Crossweb blocks GitHub's datacenter IPs; your home connection is allowed through.
# Safe to run any time. Register it once with scripts\install_task.ps1.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
$env:PYTHONUTF8 = "1"

python -m krkhack.snapshot
if ($LASTEXITCODE -ne 0) { Write-Host "snapshot failed - nothing pushed"; exit 1 }

git pull --rebase --autostash 2>&1 | Out-Null
git add data/crossweb_snapshot.json
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git -c user.name="krkhack-local" -c user.email="krkhack-local@users.noreply.github.com" commit -m "data: crossweb snapshot $(Get-Date -Format yyyy-MM-dd)"
    git push
} else {
    Write-Host "snapshot unchanged"
}
