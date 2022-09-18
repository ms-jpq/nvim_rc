#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


LIB="$(dirname -- "$(dirname -- "$(realpath -- "$0")")")/lib/powershell-ls"

CACHE="$(mktemp --directory)"
trap 'rm --recursive --force -- "$CACHE"' EXIT INT HUP TERM


CMD=(
  "$LIB/PowerShellEditorServices/Start-EditorServices.ps1"
  -BundledModulesPath
  "$LIB"

  -FeatureFlags
  '@()'
  -AdditionalModules
  '@()'

  -Stdio
  -HostName nvim
  -HostProfileId 0
  -HostVersion 1.0.0

  -LogLevel Normal
  -LogPath
  "$CACHE/powershell_es.log"
  -SessionDetailsPath
  "$CACHE/powershell_es.session.json"
  )


ARGS=(
  -NoLogo
  -NoProfile
  -Command
  "${CMD[*]}"
  )


exec pwsh "${ARGS[@]}"
