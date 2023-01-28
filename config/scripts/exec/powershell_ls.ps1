#!/usr/bin/env -S -- pwsh -NonInteractive

Set-StrictMode -Version 'Latest'
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true


$lib = Join-Path -- (Split-Path -- "$PSScriptRoot") 'lib' 'powershell-ls.ps1'
$cache = [System.IO.Directory]::CreateTempSubdirectory().FullName

$argv = @(
    Join-Path -- "$lib" 'PowerShellEditorServices' 'Start-EditorServices.ps1'

    '-BundledModulesPath'
    "$lib"

    '-FeatureFlags'
    '@()'

    '-AdditionalModules'
    '@()'

    '-Stdio'

    '-HostName'
    'nvim'

    '-HostProfileId'
    '0'

    '-HostVersion'
    '1.0.0'

    '-LogLevel'
    'Normal'

    '-LogPath'
    Join-Path -- "$cache" 'powershell_es.log'

    '-SessionDetailsPath'
    Join-Path -- "$cache" 'powershell_es.session.json'
)

Switch-Process -- pwsh -NonInteractive -Command @argv
