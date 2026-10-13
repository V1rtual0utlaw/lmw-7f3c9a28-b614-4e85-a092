# Outer error handler captures failures that happen before SETUP.ps1's try block.
$ErrorActionPreference='Stop'
$TranscriptStarted=$false
try {
    Set-Location -LiteralPath $PSScriptRoot
    New-Item -ItemType Directory -Force -Path (Join-Path $PSScriptRoot 'logs') | Out-Null
    Start-Transcript -Path (Join-Path $PSScriptRoot 'logs\bootstrap.log') -Append | Out-Null
    $TranscriptStarted=$true
    Write-Host "PowerShell version: $($PSVersionTable.PSVersion)"
    Write-Host "Project folder: $PSScriptRoot"
    if (!(Test-Path -LiteralPath (Join-Path $PSScriptRoot 'SETUP.ps1'))) { throw 'SETUP.ps1 missing. Extract the full ZIP first.' }
    & (Join-Path $PSScriptRoot 'SETUP.ps1')
} catch {
    Write-Host 'Startup failed:' -ForegroundColor Red
    Write-Host ($_ | Out-String) -ForegroundColor Red
    Write-Host 'Extract the entire ZIP into a normal writable folder, such as Documents\TrueScienceFactory.'
    exit 1
} finally {
    if ($TranscriptStarted) { try { Stop-Transcript | Out-Null } catch {} }
}
