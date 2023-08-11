#!/usr/bin/env -S -- pwsh -NoProfile -NonInteractive

Set-StrictMode -Version 'Latest'
$ErrorActionPreference = 'Stop'
$PSStyle.OutputRendering = 'PlainText'


$uri = 'https://github.com/PowerShell/PowerShellEditorServices/releases/latest/download/PowerShellEditorServices.zip'

$tmp = $Env:CI ? (New-Item -ItemType Directory -Path ([Guid]::NewGuid())) : [IO.Directory]::CreateTempSubdirectory()
$out = Split-Path -Leaf -Path $uri
$bin = $Env:BIN
$bin_d = Split-Path -Path $bin

Invoke-WebRequest -Uri $uri -OutFile $out
Expand-Archive -Force -DestinationPath $tmp -Path $out

if (Test-Path -Path $Env:LIB) {
    Remove-Item -Recurse -Force -Path $Env:LIB
}

Move-Item -Path $tmp -Destination $Env:LIB
Copy-Item -Path (Join-Path -Path $PSScriptRoot 'pwsh_fmt.ex.ps1') -Destination (Join-Path -Path $bin_d 'pwsh-fmt.ps1')
Copy-Item -Path (Join-Path -Path $PSScriptRoot 'pwsh_lint.ex.ps1') -Destination (Join-Path -Path $bin_d 'pwsh-lint.ps1')
Copy-Item -Path (Join-Path -Path $PSScriptRoot 'pwsh_es.ex.ps1') -Destination $bin
