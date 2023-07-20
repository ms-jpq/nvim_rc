#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BIN=("${0%/*}/../lib/haskell-language-server-wrapper/bin")
PATH="${BIN[*]}:$PATH"

exec -- "${BIN[*]}/haskell-language-server-wrapper" "$@"
