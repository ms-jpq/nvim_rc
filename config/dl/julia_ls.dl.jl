#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O nullglob -O extglob -O failglob -O globstar
#=
if [[ "$OSTYPE" =~ 'msys' ]]
then
  BIN="$BIN.jl"
fi

export -- JULIA_DEPOT_PATH="$LIB/depot"
mkdir -v -p -- "$JULIA_DEPOT_PATH"
cp -v -f -- "$(dirname -- "$0")/julia_ls.ex.jl" "$BIN"
exec -- timeout 15m julia --project="$LIB" "$0" "$@"
=#

using Pkg;

pkg = "LanguageServer"

Pkg.add(pkg)
Pkg.update(pkg)
