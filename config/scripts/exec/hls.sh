#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


BIN="$(dirname -- "$(dirname -- "$(realpath -- "$0")")")/lib/haskell-language-server-wrapper/bin"
PATH="$BIN:$PATH"


exec "$BIN/haskell-language-server-wrapper" "$@"
