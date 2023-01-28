#!/usr/bin/env -S -- pwsh -NonInteractive

Set-StrictMode -Version 'Latest'
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

$lib = Join-Path -- (Split-Path -- "$PSScriptRoot") 'lib' 'powershell-ls.ps1' 'PSScriptAnalyzer'
$analyzer = Join-Path -- (Get-ChildItem -Path "$lib" -Filter '*') 'PSScriptAnalyzer.psm1'
$def = [System.Console]::In.ReadToEnd()

Import-Module -- "$analyzer"
Invoke-Formatter -ScriptDefinition "$def"
