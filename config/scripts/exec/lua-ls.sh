#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


LIB="$(dirname "$(dirname "$(realpath "$0")")")/tmp/lua-ls/repo"

ARGS=(
  -E
  "$LIB/main.lua"
  )


exec "$LIB/bin/"*'/lua-language-server' "${ARGS[@]}"
