#!/usr/bin/env -S -- pwsh -NoProfile -NonInteractive

Set-StrictMode -Version 'Latest'
$ErrorActionPreference = 'Stop'
$PSStyle.OutputRendering = 'PlainText'


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
Copy-Item -- (Join-Path -- "$exec" 'pwsh_fmt.ps1') (Join-Path -- (Split-Path -- "$bin") 'pwsh-fmt.ps1')
Copy-Item -- (Join-Path -- "$exec" 'pwsh_lint.ps1') (Join-Path -- (Split-Path -- "$bin") 'pwsh-lint.ps1')
Copy-Item -- (Join-Path -- "$exec" 'pwsh_es.ps1') "$bin"
