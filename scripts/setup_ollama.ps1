$ErrorActionPreference = 'Stop'
$m2Root = Split-Path -Parent $PSScriptRoot
$m2Version = '0.34.2'
$m2ExpectedHash = '8f3fd071a2a2f9497b562f43502c77c2b701a99d1ee5dfda28da8c786373063b'
$m2Archive = Join-Path $m2Root '.tools/downloads/ollama-windows-amd64-0.34.2.zip'
$m2Install = Join-Path $m2Root ".tools/ollama/$m2Version"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $m2Archive), $m2Install | Out-Null
if (-not (Test-Path -LiteralPath $m2Archive)) {
    & curl.exe --fail --location --retry 2 --silent --show-error --output $m2Archive 'https://github.com/ollama/ollama/releases/download/v0.34.2/ollama-windows-amd64.zip'
    if ($LASTEXITCODE -ne 0) { throw 'Ollama archive download failed.' }
}
$m2ActualHash = (Get-FileHash -LiteralPath $m2Archive -Algorithm SHA256).Hash.ToLowerInvariant()
if ($m2ActualHash -ne $m2ExpectedHash) { throw 'Ollama archive checksum mismatch; do not execute it.' }
Expand-Archive -LiteralPath $m2Archive -DestinationPath $m2Install -Force
$m2Provenance = [ordered]@{
    version = $m2Version
    url = 'https://github.com/ollama/ollama/releases/download/v0.34.2/ollama-windows-amd64.zip'
    release_api = 'https://api.github.com/repos/ollama/ollama/releases/tags/v0.34.2'
    sha256 = $m2ActualHash
    installed_at = (Get-Date).ToString('o')
}
New-Item -ItemType Directory -Force -Path (Join-Path $m2Root 'artifacts/m2') | Out-Null
$m2Provenance | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $m2Root 'artifacts/m2/runtime-install.json') -Encoding utf8
Write-Output "Verified portable Ollama $m2Version installed in $m2Install"
