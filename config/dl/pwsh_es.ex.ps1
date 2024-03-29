#!/usr/bin/env -S -- pwsh -NoProfile -NonInteractive

Set-StrictMode -Version 'Latest'
$ErrorActionPreference = 'Stop'
$PSStyle.OutputRendering = 'PlainText'


$lib = Join-Path -Path (Split-Path -Path $PSScriptRoot) 'lib' 'pwsh_es.ps1'
$cache = [IO.Directory]::CreateTempSubdirectory()

$argv = @(
    Join-Path -Path $lib 'PowerShellEditorServices' 'Start-EditorServices.ps1'
    '-BundledModulesPath', $lib
    '-FeatureFlags', '@()'
    '-AdditionalModules', '@()'
    '-Stdio'
    '-HostName', 'nvim'
    '-HostProfileId', '0'
    '-HostVersion', '1.0.0'
    '-LogLevel', 'Normal'
    '-LogPath', (Join-Path -Path $cache 'powershell_es.log')
    '-SessionDetailsPath', (Join-Path -Path $cache 'powershell_es.session.json')
)

$Env:NOCOLOR = '1'
Switch-Process -- pwsh -NoProfile -NonInteractive -Command @argv
