#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


BIN="$(dirname -- "$(dirname -- "$(realpath -- "$0")")")/lib/haskell-language-server-wrapper/bin"
export PATH="$BIN:$PATH"


exec "$BIN/haskell-language-server-wrapper" "$@"
