#!/usr/bin/env -S -- pwsh -NoProfile -NonInteractive

Set-StrictMode -Version 'Latest'
$ErrorActionPreference = 'Stop'
$PSStyle.OutputRendering = 'PlainText'

$uri = 'https://github.com/PowerShell/PowerShellEditorServices/releases/latest/download/PowerShellEditorServices.zip'

$tmp = [IO.Directory]::CreateTempSubdirectory()
$out = Split-Path -Leaf -- $uri
$bin = $Env:BIN
$bin_d = Split-Path -- $bin

Invoke-WebRequest -Uri $uri -OutFile $out
Expand-Archive -Force -DestinationPath $tmp -Path $out

if (Test-Path -- $Env:LIB) {
    Remove-Item -Recurse -Force -- $Env:LIB
}

Move-Item -- $tmp $Env:LIB
Copy-Item -- (Join-Path -- $PSScriptRoot 'pwsh_fmt.ex.ps1') (Join-Path -- $bin_d 'pwsh-fmt.ps1')
Copy-Item -- (Join-Path -- $PSScriptRoot 'pwsh_lint.ex.ps1') (Join-Path -- $bin_d 'pwsh-lint.ps1')
Copy-Item -- (Join-Path -- $PSScriptRoot 'pwsh_es.ex.ps1') $bin
