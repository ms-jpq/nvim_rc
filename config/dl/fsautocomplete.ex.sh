#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

LIB="${0%/*}/../lib"
BIN="$LIB/fsautocomplete/fsautocomplete"

if command -v -- asdf >/dev/null; then
  DOTNET="$(asdf which dotnet)"
  export -- DOTNET_ROOT="${DOTNET%/*}"
fi

exec -- "$BIN" "$@"
