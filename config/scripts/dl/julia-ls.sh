#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


BASE="$(dirname -- "$0")"

"$BASE/../exec/julia.sh" "$BASE/julia-ls.jl"
ln --symbolic --force -- "$BASE/../exec/julia-ls.sh" "$BIN"
