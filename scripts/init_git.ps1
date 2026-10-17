# Initialise version control once from the reconstructed history bundle.
# History: M1-M2 baseline snapshot -> supervisor feedback docs -> M3 changes.
# Files already present (evidence artifacts, later edits) are committed on top.
# Safe to re-run: an existing repository is left unchanged.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Output 'git is not installed; version control was not initialised.'
    exit 0
}
if (Test-Path -LiteralPath (Join-Path $root '.git')) {
    Write-Output 'Git repository already exists; nothing to initialise.'
    exit 0
}
$bundle = Join-Path $root 'scripts/git/history.bundle'
if (-not (Test-Path -LiteralPath $bundle)) { throw 'History bundle is missing.' }
function Invoke-Git {
    & git @args
    if ($LASTEXITCODE -ne 0) { throw "git $($args -join ' ') failed with exit code $LASTEXITCODE" }
}
Invoke-Git init -q
Invoke-Git bundle verify -q $bundle
Invoke-Git fetch -q $bundle 'main:refs/remotes/bundle/main'
Invoke-Git update-ref refs/heads/main refs/remotes/bundle/main
Invoke-Git symbolic-ref HEAD refs/heads/main
Invoke-Git update-ref -d refs/remotes/bundle/main
Invoke-Git reset -q --mixed
$identity = @()
$configuredName = & git config user.name
if (-not $configuredName) {
    $identity = @('-c', "user.name=$(& git log -1 --format=%an)", '-c', "user.email=$(& git log -1 --format=%ae)")
}
Invoke-Git add -A
$pending = & git status --porcelain
if ($pending) {
    Invoke-Git @identity commit -q -m 'Track evidence artifacts and files present at repository initialisation'
}
& git log --oneline
Write-Output 'Git repository initialised.'
