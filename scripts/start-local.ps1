$ErrorActionPreference = 'Stop'
$localRepo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
& (Join-Path $localRepo 'python/.venv/Scripts/python.exe') (Join-Path $PSScriptRoot 'start_local.py')
if ($LASTEXITCODE -ne 0) { throw 'Local site startup failed; see output/local-site logs.' }
