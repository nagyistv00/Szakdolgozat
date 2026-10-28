# Runs the project checks from PowerShell in the project folder.
#   ./scripts/check.ps1              lint and unit tests only
#   ./scripts/check.ps1 -Dev         + sample scans, evaluation on the development samples,
#                                      development request scenarios and the demo
#   ./scripts/check.ps1 -Lab         + evaluation on the test application (data/lab)
#   ./scripts/check.ps1 -Requests    + the 14 test requests (data/requests_test.json)
#   ./scripts/check.ps1 -All         everything above (roughly an hour with both models)
#   -SkipModel                       run the scanners without the language model
# The current state is committed to git first. Every step's output is saved in
# results/<UTC date>_<time>_check/.
param(
    [switch]$Dev,
    [switch]$Lab,
    [switch]$Requests,
    [switch]$All,
    [switch]$SkipModel,
    [int]$Repeats = 2,
    [string]$Models = 'qwen2.5-coder:14b,qwen2.5-coder:7b'
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
if ($All) { $Dev = $true; $Lab = $true; $Requests = $true }
$useModel = ($Dev -or $Lab -or $Requests) -and -not $SkipModel

$stamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd_HHmmss')
$out = Join-Path $root "results/${stamp}_check"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$previousEncoding = [Console]::OutputEncoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$status = [ordered]@{}

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
    $status[$Name] = [ordered]@{ exit_code = $code; seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 1) }
    Write-Host "=== $Name finished with exit code $code"
}

# Commits the working tree before the checks, so every result belongs to a commit.
# The message comes from notes/commit_message.txt when that file exists.
function Save-Snapshot {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { 'git not found; no snapshot.'; return }
    $identity = @()
    if (-not (& git config user.name)) {
        $identity = @('-c', "user.name=$(& git log -1 --format=%an)", '-c', "user.email=$(& git log -1 --format=%ae)")
    }
    & git add -A
    if (& git status --porcelain) {
        $messageFile = Join-Path $root 'notes/commit_message.txt'
        if (Test-Path -LiteralPath $messageFile) {
            & git @identity commit -q -F $messageFile
            Remove-Item -LiteralPath $messageFile
        } else {
            & git @identity commit -q -m 'Snapshot before running the checks'
        }
    }
    & git log --oneline -3
}

# The server must not be started inside Invoke-Step: ollama.exe would inherit the
# step's output pipe and the step would never finish.
function Invoke-Ollama([string]$Action) {
    $name = "ollama_$($Action.ToLowerInvariant())"
    $log = Join-Path $out "$name.log"
    try {
        & (Join-Path $root 'scripts/ollama.ps1') -Action $Action | Out-File -LiteralPath $log -Encoding utf8
        $status[$name] = [ordered]@{ exit_code = 0 }
    } catch {
        "$_" | Out-File -LiteralPath $log -Encoding utf8 -Append
        $status[$name] = [ordered]@{ exit_code = -1 }
    }
    Get-Content -LiteralPath $log | ForEach-Object { Write-Host $_ }
}

try {
    Invoke-Step 'git' { Save-Snapshot }
    Invoke-Step 'ruff' { & uv run --locked ruff check src tests scripts }
    Invoke-Step 'pytest' { & uv run --locked pytest -q -rs -p no:cacheprovider --basetemp=.runtime/pytest --junitxml="$out/pytest.xml" }

    $modelArgs = @('--no-model')
    if ($useModel) {
        if (-not (Get-NetTCPConnection -LocalPort 11435 -State Listen -ErrorAction SilentlyContinue)) { Invoke-Ollama 'Start' }
        foreach ($model in ($Models -split ',')) {
            $tag = $model.Trim()
            Invoke-Step "pull_$($tag -replace '[:/]', '_')" { & uv run --locked python scripts/pull_model.py --model $tag }
        }
        $modelArgs = @('--models', $Models)
    }
    if ($Dev) {
        $demoArgs = if ($useModel) { @('--model', ($Models -split ',')[0].Trim()) } else { @('--no-model') }
        Invoke-Step 'scan_samples' { & uv run --locked python scripts/scan_samples.py }
        Invoke-Step 'eval_dev' { & uv run --locked python scripts/eval_dev.py --repeats $Repeats --out "$out/dev" @modelArgs }
        Invoke-Step 'eval_requests_dev' {
            & uv run --locked python scripts/eval_requests.py --cases data/requests_dev.json --root data/samples --out "$out/requests_dev" @modelArgs
        }
        Invoke-Step 'demo' { & uv run --locked python scripts/demo.py --out "$out/demo" @demoArgs }
    }
    if ($Lab) {
        Invoke-Step 'eval_lab' { & uv run --locked python scripts/eval_lab.py --out "$out/lab" @modelArgs }
    }
    if ($Requests) {
        Invoke-Step 'eval_requests' { & uv run --locked python scripts/eval_requests.py --out "$out/requests" @modelArgs }
    }
} finally {
    # Stops only the server recorded by scripts/ollama.ps1 (its identity is checked).
    if ($useModel -and (Test-Path -LiteralPath (Join-Path $root '.runtime/ollama-process.json'))) {
        Invoke-Ollama 'Stop'
    }
    $status | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $out 'status.json') -Encoding utf8
    [Console]::OutputEncoding = $previousEncoding
    Write-Host ''
    Write-Host "Done. Output: $out"
    $status.GetEnumerator() | ForEach-Object { Write-Host ("  {0}: exit {1}" -f $_.Key, $_.Value.exit_code) }
}
