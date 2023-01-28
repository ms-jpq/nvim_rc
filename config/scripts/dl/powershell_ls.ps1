#!/usr/bin/env -S -- pwsh -NonInteractive

Set-StrictMode -Version 'Latest'
$ErrorActionPreference = 'Stop'


$tmp = [System.IO.Directory]::CreateTempSubdirectory()
$out = Split-Path -Leaf -- "$Env:URI"
$exec = Join-Path -- (Split-Path -- "$PSScriptRoot") 'exec'
$bin = "$Env:BIN"

Invoke-WebRequest -Uri "$Env:URI" -OutFile "$out"
Expand-Archive -DestinationPath "$tmp" -- "$out"

if (Test-Path -- "$Env:LIB") {
    Remove-Item -Recurse -Force -- "$Env:LIB"
}

Move-Item -- "$tmp" "$Env:LIB"
Copy-Item -- (Join-Path -- "$exec" 'powershell_analyzer.ps1') (Join-Path -- (Split-Path -- "$bin") 'powershell-analyzer.ps1')
Copy-Item -- (Join-Path -- "$exec" 'powershell_ls.ps1') "$bin"
