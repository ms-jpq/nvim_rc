#!/usr/bin/env -S -- bash
#=
set -Eeu
set -o pipefail
shopt -s globstar failglob


if [[ "$OSTYPE" =~ 'msys' ]]
then
  BIN="$BIN.jl"
fi

export JULIA_DEPOT_PATH="$LIB/depot"
mkdir --parents -- "$JULIA_DEPOT_PATH"
cp -- "$(dirname -- "$0")/../exec/julia_ls.jl" "$BIN"
exec -- julia --project="$LIB" "$0" "$@"
=#

using Pkg;

pkg = "LanguageServer"

Pkg.add(pkg)
Pkg.update(pkg)
