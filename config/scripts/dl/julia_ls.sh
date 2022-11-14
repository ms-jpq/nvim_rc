#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


BASE="$(dirname -- "$0")"
EXEC="$BASE/../exec"

"$EXEC/julia.sh" "$BASE/julia_ls.jl"

CP=(
  julia_ls.jl
  julia_ls.sh
  julia.sh
  )

mkdir --parents -- "$LIB"

for name in "${CP[@]}"
do
  cp -- "$EXEC/$name" "$LIB/$name"
done

ln --symbolic --force -- "$LIB/julia_ls.sh" "$BIN"
