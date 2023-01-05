#!/usr/bin/env -S pwsh

Set-StrictMode -Version 'Latest'
$ErrorActionPreference = 'Stop'


$tmp = Join-Path -- ([System.IO.Path]::GetTempPath()) (New-Guid)
$out = Split-Path -Leaf -- "$Env:URI"

New-Item -ItemType 'Directory' -- "$tmp"
Invoke-WebRequest -Uri "$Env:URI" -OutFile "$out"
Expand-Archive -DestinationPath "$tmp" -- "$out"

if (Test-Path -- "$Env:LIB") {
  Remove-Item -Recurse -Force -- "$Env:LIB"
}

Move-Item -- "$tmp" "$Env:LIB"
Copy-Item -- (Join-Path -- (Split-Path -- "$PSScriptRoot") 'exec' 'powershell_ls.ps1') "$Env:BIN"
