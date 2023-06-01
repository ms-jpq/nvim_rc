#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O nullglob -O failglob -O globstar

LIB="$(dirname -- "$0")/../lib"
BIN="$LIB/fsautocomplete/fsautocomplete"

if hash asdf 2>/dev/null; then
  export -- DOTNET_ROOT=
  DOTNET_ROOT="$(dirname -- "$(asdf which dotnet)")"
fi

exec -- "$BIN" "$@"
