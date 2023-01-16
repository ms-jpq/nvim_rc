#!/usr/bin/env -S bash
#=
set -Eeu
set -o pipefail
shopt -s failglob failglob

mkdir --parents -- "$LIB"
cp -- "$(dirname -- "$0")/../exec/julia_ls.jl" "$BIN"
exec -- julia --project="$LIB" "$0" "$@"
=#

using Pkg;

pkg = "LanguageServer"

Pkg.add(pkg)
Pkg.update(pkg)
