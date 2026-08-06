$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$outputRoot = Join-Path $repoRoot "output\supplement"
$supplementRoot = Join-Path $outputRoot "MonopolyBench_anonymous_supplement"
$zipPath = Join-Path $outputRoot "MonopolyBench_anonymous_supplement.zip"

New-Item -ItemType Directory -Force -Path $supplementRoot | Out-Null

Copy-Item -LiteralPath (Join-Path $repoRoot "paper\supplement\README.md") `
    -Destination (Join-Path $supplementRoot "README.md") -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "paper\claim_source_audit.md") `
    -Destination (Join-Path $supplementRoot "claim_source_audit.md") -Force
Copy-Item `
    -LiteralPath (Join-Path $repoRoot "docs\research_raw\monopolybench_eight_run_ledger_2026-07-28.csv") `
    -Destination (Join-Path $supplementRoot "monopolybench_eight_run_ledger_2026-07-28.csv") `
    -Force
Copy-Item `
    -LiteralPath (Join-Path $repoRoot "paper\supplement\run115_source_file_inventory.csv") `
    -Destination (Join-Path $supplementRoot "run115_source_file_inventory.csv") `
    -Force

$figureDestination = Join-Path $supplementRoot "figures"
New-Item -ItemType Directory -Force -Path $figureDestination | Out-Null
foreach ($figure in @(
    "architecture.pdf",
    "architecture.png",
    "run273_house_lock.pdf",
    "run273_house_lock.png"
)) {
    Copy-Item -LiteralPath (Join-Path $repoRoot "paper\figures\$figure") `
        -Destination $figureDestination -Force
}

$packagePayloads = @(
    "saved_game_manifest.json",
    "run\replay_report.json",
    "analysis\manifests\source_artifact_hashes.json",
    "analysis\manifests\analysis_manifest.json",
    "analysis\quality\artifact_completeness.json",
    "analysis\quality\call_reconciliation.json",
    "analysis\quality\replay_verification.json",
    "analysis\quality\quality_flags.json",
    "analysis\review\decision_coverage.csv",
    "analysis\review\evidence_index.csv",
    "analysis\reports\integrity_report.md",
    "analysis\reports\manual_review_report.md",
    "analysis\reports\case_studies.md"
)

$ledgerPath = Join-Path $repoRoot "docs\research_raw\monopolybench_eight_run_ledger_2026-07-28.csv"
$games = Import-Csv -LiteralPath $ledgerPath |
    Where-Object { $_.saved_game -ne "TOTAL" }

foreach ($game in $games) {
    $gameRoot = Join-Path $repoRoot "saved_games\$($game.saved_game)"
    $gameDestination = Join-Path $supplementRoot "runs\$($game.saved_game)"
    foreach ($relativePath in $packagePayloads) {
        $source = Join-Path $gameRoot $relativePath
        if (-not (Test-Path -LiteralPath $source)) {
            Write-Host "MISSING_OPTIONAL $($game.saved_game)/$relativePath"
            continue
        }
        $destination = Join-Path $gameDestination $relativePath
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) |
            Out-Null
        Copy-Item -LiteralPath $source -Destination $destination -Force
    }
}

$manifestPath = Join-Path $supplementRoot "supplement_manifest.csv"
$manifestRows = Get-ChildItem -LiteralPath $supplementRoot -Recurse -File |
    Where-Object { $_.FullName -ne $manifestPath } |
    Sort-Object FullName |
    ForEach-Object {
        [pscustomobject]@{
            path = $_.FullName.Substring($supplementRoot.Length + 1).Replace("\", "/")
            bytes = $_.Length
            sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()
        }
    }
$manifestRows |
    Export-Csv -LiteralPath $manifestPath -NoTypeInformation -Encoding utf8

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$archive = [System.IO.Compression.ZipFile]::Open(
    $zipPath,
    [System.IO.Compression.ZipArchiveMode]::Create
)
try {
    $fixedTimestamp = [DateTimeOffset]::new(
        2000,
        1,
        1,
        0,
        0,
        0,
        [TimeSpan]::Zero
    )
    $files = Get-ChildItem -LiteralPath $supplementRoot -Recurse -File |
        Sort-Object {
            $_.FullName.Substring($supplementRoot.Length + 1).Replace("\", "/")
        }
    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($supplementRoot.Length + 1).
            Replace("\", "/")
        $entry = $archive.CreateEntry(
            $relativePath,
            [System.IO.Compression.CompressionLevel]::Optimal
        )
        $entry.LastWriteTime = $fixedTimestamp
        $inputStream = [System.IO.File]::OpenRead($file.FullName)
        $outputStream = $entry.Open()
        try {
            $inputStream.CopyTo($outputStream)
        }
        finally {
            $outputStream.Dispose()
            $inputStream.Dispose()
        }
    }
}
finally {
    $archive.Dispose()
}

$zipInfo = Get-Item -LiteralPath $zipPath
$zipHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $zipPath).Hash
$runCount = (Get-ChildItem -LiteralPath (Join-Path $supplementRoot "runs") -Directory).Count

Write-Output "PAYLOAD_FILES=$($manifestRows.Count)"
Write-Output "RUN_DIRS=$runCount"
Write-Output "ZIP_BYTES=$($zipInfo.Length)"
Write-Output "ZIP_SHA256=$zipHash"
