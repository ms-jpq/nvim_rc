#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


BASE="$(dirname -- "$0")"
EXEC="$BASE/../exec"

"$EXEC/julia.sh" "$BASE/julia-ls.jl"

CP=(
  julia-ls.jl
  julia-ls.sh
  julia.sh
  )

mkdir --parents -- "$LIB"

for name in "${CP[@]}"
do
  cp -- "$EXEC/$name" "$LIB/$name"
done

ln --symbolic --force -- "$LIB/julia-ls.sh" "$BIN"
