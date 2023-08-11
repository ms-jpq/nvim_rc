#!/usr/bin/env -S -- pwsh -NoProfile -NonInteractive

Set-StrictMode -Version 'Latest'
$ErrorActionPreference = 'Stop'
$PSStyle.OutputRendering = 'PlainText'

$lib = Join-Path -Path (Split-Path -Path $PSScriptRoot) 'lib' 'pwsh_es.ps1' 'PSScriptAnalyzer'
$analyzer = Join-Path -Path (Get-ChildItem -Path $lib -Filter '*') 'PSScriptAnalyzer.psm1'

Import-Module -- $analyzer
Invoke-Formatter -ScriptDefinition ($input | ForEach-Object { $_.TrimEnd() } | Join-String -Separator ([Environment]::NewLine))
