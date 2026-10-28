param([ValidateSet('Start', 'Stop')][string]$Action = 'Start')
$ErrorActionPreference = 'Stop'
$m2Root = Split-Path -Parent $PSScriptRoot
$m2Executable = Join-Path $m2Root '.tools/ollama/0.34.2/ollama.exe'
$m2Runtime = Join-Path $m2Root '.runtime'
$m2StatePath = Join-Path $m2Runtime 'ollama-process.json'
$m2Endpoint = 'http://127.0.0.1:11435'
New-Item -ItemType Directory -Force -Path $m2Runtime | Out-Null
if ($Action -eq 'Stop') {
    if (-not (Test-Path -LiteralPath $m2StatePath)) { throw 'No project-owned process record.' }
    $m2State = Get-Content -LiteralPath $m2StatePath -Raw | ConvertFrom-Json
    $m2Process = Get-Process -Id $m2State.pid -ErrorAction SilentlyContinue
    if ($null -eq $m2Process) { Write-Output 'Project server already stopped.'; exit 0 }
    if ($m2Process.Path -ne $m2Executable -or $m2Process.StartTime.ToUniversalTime().ToString('o') -ne $m2State.started_utc) {
        throw 'Process identity changed; refusing to stop another process.'
    }
    try {
        Invoke-RestMethod -Uri "$m2Endpoint/api/generate" -Method Post -ContentType 'application/json' -Body '{"model":"qwen2.5-coder:7b","keep_alive":0}' -TimeoutSec 30 | Out-Null
    } catch { Write-Warning 'Could not request model unload before stopping the project server.' }
    Stop-Process -Id $m2Process.Id
    Write-Output 'Project Ollama server stopped.'
    exit 0
}
if (-not (Test-Path -LiteralPath $m2Executable)) { throw 'Run scripts/setup_ollama.ps1 first.' }
$m2Listener = Get-NetTCPConnection -LocalPort 11435 -State Listen -ErrorAction SilentlyContinue
if ($m2Listener) { throw 'Port 11435 is already in use; leaving the existing process unchanged.' }
$m2Names = @('OLLAMA_HOST', 'OLLAMA_MODELS', 'OLLAMA_NO_CLOUD', 'OLLAMA_NUM_PARALLEL', 'OLLAMA_CONTEXT_LENGTH')
$m2Saved = @{}
foreach ($m2Name in $m2Names) { $m2Saved[$m2Name] = [Environment]::GetEnvironmentVariable($m2Name, 'Process') }
try {
    $env:OLLAMA_HOST = '127.0.0.1:11435'
    $env:OLLAMA_MODELS = Join-Path $m2Root 'models/ollama'
    $env:OLLAMA_NO_CLOUD = '1'
    $env:OLLAMA_NUM_PARALLEL = '1'
    $env:OLLAMA_CONTEXT_LENGTH = '4096'
    $m2Process = Start-Process -FilePath $m2Executable -ArgumentList 'serve' -WorkingDirectory $m2Root -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $m2Runtime 'ollama.stdout.log') -RedirectStandardError (Join-Path $m2Runtime 'ollama.stderr.log')
} finally {
    foreach ($m2Name in $m2Names) { [Environment]::SetEnvironmentVariable($m2Name, $m2Saved[$m2Name], 'Process') }
}
@{pid=$m2Process.Id; executable=$m2Executable; started_utc=$m2Process.StartTime.ToUniversalTime().ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $m2StatePath -Encoding utf8
for ($m2Attempt = 0; $m2Attempt -lt 20; $m2Attempt++) {
    try {
        $m2Version = Invoke-RestMethod -Uri "$m2Endpoint/api/version" -TimeoutSec 1
        Write-Output "Project Ollama $($m2Version.version) listening on $m2Endpoint (PID $($m2Process.Id))"
        exit 0
    } catch { Start-Sleep -Milliseconds 250 }
}
Stop-Process -Id $m2Process.Id -ErrorAction SilentlyContinue
throw 'Project Ollama server did not become ready; inspect .runtime/ollama.stderr.log.'
