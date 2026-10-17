# One-command milestone 3 check. Run from PowerShell in the project folder:
#   ./scripts/m3_check.ps1              (local models, 14B default and 7B comparison;
#                                        roughly 30-40 minutes; first run downloads ~9 GB)
#   ./scripts/m3_check.ps1 -SkipModel   (scanners and tests only)
# Every step's full output is saved under artifacts/m3/check-<UTC time>/.
param(
    [switch]$SkipModel,
    [int]$Repeats = 2,
    [string]$Models = 'qwen2.5-coder:14b,qwen2.5-coder:7b'
)
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

# The model server helper starts a long-running ollama.exe. It must not run inside
# Invoke-Step: the child would inherit the output pipe and the step would never end.
function Invoke-ModelServer([string]$Action) {
    $name = "model_server_$($Action.ToLowerInvariant())"
    Write-Host "=== $name"
    $log = Join-Path $out "$name.log"
    try {
        & (Join-Path $root 'scripts/model_server.ps1') -Action $Action | Out-File -LiteralPath $log -Encoding utf8
        $results[$name] = [ordered]@{ exit_code = 0 }
    } catch {
        "$_" | Out-File -LiteralPath $log -Encoding utf8 -Append
        $results[$name] = [ordered]@{ exit_code = -1 }
    }
    Get-Content -LiteralPath $log | ForEach-Object { Write-Host $_ }
}

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
        if (-not $listener) { Invoke-ModelServer 'Start' }
        foreach ($model in ($Models -split ',')) {
            $tag = $model.Trim()
            $safe = $tag -replace '[:/]', '_'
            Invoke-Step "model_pull_$safe" { & uv run --locked python scripts/pull_model.py --model $tag }
        }
        $modelArgs = @('--models', $Models)
    }
    $demoArgs = if ($SkipModel) { @('--no-model') } else { @('--model', ($Models -split ',')[0].Trim()) }
    Invoke-Step 'dev_eval' { & uv run --locked python scripts/m3_dev_eval.py --repeats $Repeats --out "$out/dev" @modelArgs }
    Invoke-Step 'requests_eval' { & uv run --locked python scripts/m3_requests_eval.py --out "$out/requests" @modelArgs }
    Invoke-Step 'demo' { & uv run --locked python scripts/m3_demo.py --out "$out/demo" @demoArgs }
} finally {
    # Stops only the project-owned server recorded in .runtime (identity is verified),
    # including one left running by an interrupted earlier check.
    if (-not $SkipModel -and (Test-Path -LiteralPath (Join-Path $root '.runtime/ollama-process.json'))) {
        Invoke-ModelServer 'Stop'
    }
    $results | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $out 'status.json') -Encoding utf8
    [Console]::OutputEncoding = $previousEncoding
    Write-Host ''
    Write-Host "Check finished. Results: $out"
    $results.GetEnumerator() | ForEach-Object { Write-Host ("  {0}: exit {1}" -f $_.Key, $_.Value.exit_code) }
}
