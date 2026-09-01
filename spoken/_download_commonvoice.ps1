<#
    Download the Common Voice German archive from the Mozilla Data Collective.

    Run it yourself: it prompts for your API key, so the key never goes into a
    command line, your shell history, or a chat window.

        powershell -ExecutionPolicy Bypass -File _download_commonvoice.ps1

    The presigned URL the API hands back is short-lived, and this file is tens
    of gigabytes, so the download may well outlive the link. That is fine: just
    run the script again. It asks for a fresh URL and resumes the partial file
    where it stopped (curl -C -). Re-running never starts over.
#>
[CmdletBinding()]
param(
    [string] $DatasetId = "cmqim3xpi00t6nr07k0myqtkr",
    [string] $OutFile   = "common-voice-scripted-speech-26-0-german-94178357.tar.gz",
    [string] $Dest
)

$ErrorActionPreference = "Stop"

# $PSScriptRoot is not populated while param defaults are bound under -File, so
# a default of "$PSScriptRoot\data\..." silently becomes a rooted "\data\...",
# which lands on the drive root. Resolve it here in the body instead.
$root = if ($PSScriptRoot) { $PSScriptRoot }
        else { Split-Path -Parent $MyInvocation.MyCommand.Definition }
if (-not $Dest) { $Dest = Join-Path $root "data\commonvoice" }

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
$target = Join-Path $Dest $OutFile

# Warn early rather than dying at 90 percent with a full disk.
$drive = (Get-Item $Dest).PSDrive.Name
$free  = (Get-PSDrive $drive).Free / 1GB
Write-Host ("Ziel : {0}" -f $target)
Write-Host ("Frei : {0:N0} GB auf {1}:" -f $free, $drive)
if (Test-Path $target) {
    $have = (Get-Item $target).Length / 1GB
    Write-Host ("Bereits geladen: {0:N2} GB - wird fortgesetzt." -f $have) -ForegroundColor Yellow
}
if ($free -lt 70) {
    Write-Host "Weniger als 70 GB frei. Archiv plus entpackte Kopie brauchen etwa 55 GB." -ForegroundColor Yellow
}

# Read-Host -AsSecureString keeps the key off the screen and out of history.
$secure = Read-Host -Prompt "Mozilla Data Collective API key" -AsSecureString
$key = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
         [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure))
if ([string]::IsNullOrWhiteSpace($key)) { throw "Kein Key eingegeben." }

Write-Host "Fordere Download-Link an..."
try {
    $resp = Invoke-RestMethod -Method Post -TimeoutSec 120 `
        -Uri "https://mozilladatacollective.com/api/datasets/$DatasetId/download" `
        -Headers @{ Authorization = "Bearer $key"; "Content-Type" = "application/json" }
}
finally {
    # Do not leave the key sitting in memory longer than needed.
    $key = $null; [GC]::Collect()
}

$url = $resp.downloadUrl
if (-not $url) {
    Write-Host "Keine downloadUrl in der Antwort. Antwort war:" -ForegroundColor Red
    $resp | ConvertTo-Json -Depth 6
    throw "Abbruch."
}
Write-Host "Link erhalten. Download laeuft, das dauert." -ForegroundColor Green

# curl.exe, not the PowerShell alias: -C - resumes, and it streams to disk
# instead of buffering the whole archive in memory like Invoke-WebRequest.
& curl.exe -L -C - --retry 5 --retry-delay 10 --retry-connrefused `
    --progress-bar -o $target $url
$code = $LASTEXITCODE

if ($code -eq 0) {
    $gb = (Get-Item $target).Length / 1GB
    Write-Host ("`nFertig: {0} ({1:N2} GB)" -f $target, $gb) -ForegroundColor Green
    Write-Host "`nWeiter mit:" -ForegroundColor Cyan
    Write-Host ("  tar -xzf `"{0}`" -C `"{1}`"" -f $target, $Dest)
    Write-Host ("  python `"{0}\_ingest.py`" --cv `"{1}`"" -f $root, $Dest)
} else {
    Write-Host ("`ncurl endete mit Code {0}. Skript nochmal starten, es setzt fort." -f $code) `
        -ForegroundColor Yellow
}
