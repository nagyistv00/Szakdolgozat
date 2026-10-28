# Local Ollama server for the project (portable install under .tools, models under models/).
#   ./scripts/ollama.ps1 -Action Install   download and verify Ollama 0.34.2 (once)
#   ./scripts/ollama.ps1 -Action Start     start the server on 127.0.0.1:11435
#   ./scripts/ollama.ps1 -Action Stop      stop the server started by Start
param([ValidateSet('Install', 'Start', 'Stop')][string]$Action = 'Start')
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$version = '0.34.2'
$exe = Join-Path $root ".tools/ollama/$version/ollama.exe"
$runtime = Join-Path $root '.runtime'
$stateFile = Join-Path $runtime 'ollama-process.json'
$endpoint = 'http://127.0.0.1:11435'

if ($Action -eq 'Install') {
    $url = "https://github.com/ollama/ollama/releases/download/v$version/ollama-windows-amd64.zip"
    $expectedHash = '8f3fd071a2a2f9497b562f43502c77c2b701a99d1ee5dfda28da8c786373063b'
    $archive = Join-Path $root ".tools/downloads/ollama-windows-amd64-$version.zip"
    $target = Join-Path $root ".tools/ollama/$version"
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $archive), $target | Out-Null
    if (-not (Test-Path -LiteralPath $archive)) {
        & curl.exe --fail --location --retry 2 --silent --show-error --output $archive $url
        if ($LASTEXITCODE -ne 0) { throw 'Ollama download failed.' }
    }
    $hash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne $expectedHash) { throw 'Ollama archive checksum mismatch; not extracting it.' }
    Expand-Archive -LiteralPath $archive -DestinationPath $target -Force
    $setup = Join-Path $root 'results/setup'
    New-Item -ItemType Directory -Force -Path $setup | Out-Null
    [ordered]@{
        version = $version
        url = $url
        sha256 = $hash
        installed_at = (Get-Date).ToString('o')
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $setup 'ollama_install.json') -Encoding utf8
    Write-Output "Ollama $version installed in $target"
    exit 0
}

New-Item -ItemType Directory -Force -Path $runtime | Out-Null

if ($Action -eq 'Stop') {
    if (-not (Test-Path -LiteralPath $stateFile)) { throw 'No running project server is recorded.' }
    $state = Get-Content -LiteralPath $stateFile -Raw | ConvertFrom-Json
    $process = Get-Process -Id $state.pid -ErrorAction SilentlyContinue
    if ($null -eq $process) { Write-Output 'Server already stopped.'; exit 0 }
    # Only stop the process this script started (same executable and start time).
    $started = [datetime]$state.started_utc
    if ($process.Path -ne $exe -or $process.StartTime.ToUniversalTime().Ticks -ne $started.ToUniversalTime().Ticks) {
        throw 'The recorded process is no longer the project server; not stopping it.'
    }
    Stop-Process -Id $process.Id
    Write-Output 'Ollama server stopped.'
    exit 0
}

if (-not (Test-Path -LiteralPath $exe)) { throw 'Ollama is not installed; run ./scripts/ollama.ps1 -Action Install first.' }
if (Get-NetTCPConnection -LocalPort 11435 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port 11435 is already in use.'
}
$names = @('OLLAMA_HOST', 'OLLAMA_MODELS', 'OLLAMA_NO_CLOUD', 'OLLAMA_NUM_PARALLEL', 'OLLAMA_CONTEXT_LENGTH')
$saved = @{}
foreach ($name in $names) { $saved[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
try {
    $env:OLLAMA_HOST = '127.0.0.1:11435'
    $env:OLLAMA_MODELS = Join-Path $root 'models/ollama'
    $env:OLLAMA_NO_CLOUD = '1'
    $env:OLLAMA_NUM_PARALLEL = '1'
    $env:OLLAMA_CONTEXT_LENGTH = '4096'
    $process = Start-Process -FilePath $exe -ArgumentList 'serve' -WorkingDirectory $root -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $runtime 'ollama.stdout.log') -RedirectStandardError (Join-Path $runtime 'ollama.stderr.log')
} finally {
    foreach ($name in $names) { [Environment]::SetEnvironmentVariable($name, $saved[$name], 'Process') }
}
@{ pid = $process.Id; executable = $exe; started_utc = $process.StartTime.ToUniversalTime().ToString('o') } |
    ConvertTo-Json | Set-Content -LiteralPath $stateFile -Encoding utf8
for ($i = 0; $i -lt 20; $i++) {
    try {
        $info = Invoke-RestMethod -Uri "$endpoint/api/version" -TimeoutSec 1
        Write-Output "Ollama $($info.version) listening on $endpoint (PID $($process.Id))"
        exit 0
    } catch { Start-Sleep -Milliseconds 250 }
}
Stop-Process -Id $process.Id -ErrorAction SilentlyContinue
throw 'The Ollama server did not start; see .runtime/ollama.stderr.log.'
