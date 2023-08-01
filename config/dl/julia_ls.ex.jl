#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O nullglob -O extglob -O failglob -O globstar
#=
LIB="${0%/*}/../lib/julia-ls"
export -- JULIA_DEPOT_PATH="$LIB/depot"
exec -- julia --project="$LIB" "$0" "$@"
=#

using LanguageServer;
runserver()
