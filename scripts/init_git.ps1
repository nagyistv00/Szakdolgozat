# Version control for the project folder.
# First run: create the repository from the reconstructed history bundle
#   (M1-M2 baseline snapshot -> supervisor feedback docs -> M3) and commit existing files.
# Later runs: commit pending changes before a check, so every check runs on committed code.
#   The message comes from scripts/git/pending_message.txt when present (then removed).
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Output 'git is not installed; version control was skipped.'
    exit 0
}
function Invoke-Git {
    & git @args
    if ($LASTEXITCODE -ne 0) { throw "git $($args -join ' ') failed with exit code $LASTEXITCODE" }
}
$created = $false
if (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) {
    $bundle = Join-Path $root 'scripts/git/history.bundle'
    if (-not (Test-Path -LiteralPath $bundle)) { throw 'History bundle is missing.' }
    Invoke-Git init -q
    Invoke-Git bundle verify -q $bundle
    Invoke-Git fetch -q $bundle 'main:refs/remotes/bundle/main'
    Invoke-Git update-ref refs/heads/main refs/remotes/bundle/main
    Invoke-Git symbolic-ref HEAD refs/heads/main
    Invoke-Git update-ref -d refs/remotes/bundle/main
    Invoke-Git reset -q --mixed
    $created = $true
}
$identity = @()
$configuredName = & git config user.name
if (-not $configuredName) {
    $identity = @('-c', "user.name=$(& git log -1 --format=%an)", '-c', "user.email=$(& git log -1 --format=%ae)")
}
Invoke-Git add -A
$pending = & git status --porcelain
if ($pending) {
    $messageFile = Join-Path $root 'scripts/git/pending_message.txt'
    if (Test-Path -LiteralPath $messageFile) {
        Invoke-Git @identity commit -q -F $messageFile
        Remove-Item -LiteralPath $messageFile
    } elseif ($created) {
        Invoke-Git @identity commit -q -m 'Track evidence artifacts and files present at repository initialisation'
    } else {
        Invoke-Git @identity commit -q -m 'Automatic snapshot before running scripts/m3_check.ps1'
    }
}
& git log --oneline -5
Write-Output 'Version control up to date.'
