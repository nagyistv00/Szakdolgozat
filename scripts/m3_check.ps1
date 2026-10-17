# One-command milestone 3 check. Run from PowerShell in the project folder:
#   ./scripts/m3_check.ps1              (with the local model; about 15-25 minutes)
#   ./scripts/m3_check.ps1 -SkipModel   (scanners and tests only)
# Every step's full output is saved under artifacts/m3/check-<UTC time>/.
param([switch]$SkipModel, [int]$Repeats = 3)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$out = Join-Path $root "artifacts/m3/check-$stamp"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$previousEncoding = [Console]::OutputEncoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$results = [ordered]@{}

function Invoke-Step([string]$Name, [scriptblock]$Block) {
    Write-Host "=== $Name"
    $global:LASTEXITCODE = 0
    $saved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $started = Get-Date
    try {
        $lines = & $Block 2>&1 | ForEach-Object { "$_" }
        $code = $LASTEXITCODE
    } catch {
        $lines = @("$_")
        $code = -1
    } finally {
        $ErrorActionPreference = $saved
    }
    $lines | Set-Content -LiteralPath (Join-Path $out "$Name.log") -Encoding utf8
    $lines | Select-Object -Last 15 | ForEach-Object { Write-Host $_ }
    $results[$Name] = [ordered]@{ exit_code = $code; seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 1) }
    Write-Host "=== $Name finished with exit code $code"
}

$startedServer = $false
try {
    Invoke-Step 'git' { & powershell -NoProfile -ExecutionPolicy Bypass -File scripts/init_git.ps1 }
    Invoke-Step 'ruff' { & uv run --locked ruff check src tests scripts }
    Invoke-Step 'pytest' { & uv run --locked pytest -q -p no:cacheprovider --junitxml="$out/pytest.xml" }
    Invoke-Step 'm2_reproduction' { & uv run --locked python scripts/m2_diagnostic.py }
    $modelArgs = @()
    if ($SkipModel) {
        $modelArgs = @('--no-model')
    } else {
        $listener = Get-NetTCPConnection -LocalPort 11435 -State Listen -ErrorAction SilentlyContinue
        if (-not $listener) {
            Invoke-Step 'model_server_start' { & powershell -NoProfile -ExecutionPolicy Bypass -File scripts/model_server.ps1 -Action Start }
            $startedServer = $results['model_server_start'].exit_code -eq 0
        }
    }
    Invoke-Step 'dev_eval' { & uv run --locked python scripts/m3_dev_eval.py --repeats $Repeats --out "$out/dev" @modelArgs }
    Invoke-Step 'requests_eval' { & uv run --locked python scripts/m3_requests_eval.py --out "$out/requests" @modelArgs }
    Invoke-Step 'demo' { & uv run --locked python scripts/m3_demo.py --out "$out/demo" @modelArgs }
} finally {
    if ($startedServer) {
        Invoke-Step 'model_server_stop' { & powershell -NoProfile -ExecutionPolicy Bypass -File scripts/model_server.ps1 -Action Stop }
    }
    $results | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $out 'status.json') -Encoding utf8
    [Console]::OutputEncoding = $previousEncoding
    Write-Host ''
    Write-Host "Check finished. Results: $out"
    $results.GetEnumerator() | ForEach-Object { Write-Host ("  {0}: exit {1}" -f $_.Key, $_.Value.exit_code) }
}
