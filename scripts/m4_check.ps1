# Milestone 4 held-out evaluation on the supervisor security lab. Run from PowerShell:
#   ./scripts/m4_check.ps1                 (14B default + 7B reference; roughly 20-30 min)
#   ./scripts/m4_check.ps1 -SkipModel      (scanners only, no model)
# Static source analysis only: it reads the lab's .py files and never contacts the
# running lab server. Evidence is saved under artifacts/m4/lab-<UTC time>/.
param(
    [switch]$SkipModel,
    [string]$Models = 'qwen2.5-coder:14b,qwen2.5-coder:7b',
    [string]$LabRoot = ''
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
if (-not $LabRoot) { $LabRoot = Join-Path $root 'TestData/security_lab' }
if (-not (Test-Path -LiteralPath $LabRoot)) { throw "Lab root not found: $LabRoot" }
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$out = Join-Path $root "artifacts/m4/lab-$stamp"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$previousEncoding = [Console]::OutputEncoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = '1'; $env:PYTHONIOENCODING = 'utf-8'
$results = [ordered]@{}

function Invoke-Step([string]$Name, [scriptblock]$Block) {
    Write-Host "=== $Name"
    $global:LASTEXITCODE = 0
    $saved = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try { $lines = & $Block 2>&1 | ForEach-Object { "$_" }; $code = $LASTEXITCODE }
    catch { $lines = @("$_"); $code = -1 } finally { $ErrorActionPreference = $saved }
    $lines | Set-Content -LiteralPath (Join-Path $out "$Name.log") -Encoding utf8
    $lines | Select-Object -Last 20 | ForEach-Object { Write-Host $_ }
    $results[$Name] = [ordered]@{ exit_code = $code }
    Write-Host "=== $Name finished with exit code $code"
}

function Invoke-ModelServer([string]$Action) {
    $name = "model_server_$($Action.ToLowerInvariant())"
    $log = Join-Path $out "$name.log"
    try {
        & (Join-Path $root 'scripts/model_server.ps1') -Action $Action | Out-File -LiteralPath $log -Encoding utf8
        $results[$name] = [ordered]@{ exit_code = 0 }
    } catch { "$_" | Out-File -LiteralPath $log -Encoding utf8 -Append; $results[$name] = [ordered]@{ exit_code = -1 } }
    Get-Content -LiteralPath $log | ForEach-Object { Write-Host $_ }
}

try {
    Invoke-Step 'git' { & powershell -NoProfile -ExecutionPolicy Bypass -File scripts/init_git.ps1 }
    Invoke-Step 'ruff' { & uv run --locked ruff check src tests scripts }
    Invoke-Step 'pytest' { & uv run --locked pytest -q -p no:cacheprovider }
    $modelArgs = @()
    if ($SkipModel) {
        $modelArgs = @('--no-model')
    } else {
        $listener = Get-NetTCPConnection -LocalPort 11435 -State Listen -ErrorAction SilentlyContinue
        if (-not $listener) { Invoke-ModelServer 'Start' }
        $modelArgs = @('--models', $Models)
    }
    Invoke-Step 'm4_eval' { & uv run --locked python scripts/m4_eval.py --root "$LabRoot" --out "$out/eval" @modelArgs }
} finally {
    if (-not $SkipModel -and (Test-Path -LiteralPath (Join-Path $root '.runtime/ollama-process.json'))) {
        Invoke-ModelServer 'Stop'
    }
    $results | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $out 'status.json') -Encoding utf8
    [Console]::OutputEncoding = $previousEncoding
    Write-Host ''; Write-Host "M4 check finished. Results: $out"
    $results.GetEnumerator() | ForEach-Object { Write-Host ("  {0}: exit {1}" -f $_.Key, $_.Value.exit_code) }
}
