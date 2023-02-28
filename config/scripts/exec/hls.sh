#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O failglob -O globstar

BIN="$(dirname -- "$0")/../lib/haskell-language-server-wrapper/bin"
PATH="$BIN:$PATH"

exec -- "$BIN/haskell-language-server-wrapper"* "$@"
