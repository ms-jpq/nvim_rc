#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

LIB="${0%/*}/../lib"
BIN="$LIB/fantomas/fantomas"

if hash asdf 2>/dev/null; then
  export -- DOTNET_ROOT=
  DOTNET_ROOT="$(dirname -- "$(asdf which dotnet)")"
fi

exec -- "$BIN" "$@"
