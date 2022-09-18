#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


SELF="$(readlink --canonicalize-existing -- "$0")"
BASE="$(dirname -- "$SELF")"


exec "$BASE/julia.sh" "$BASE/julia-ls.jl" "$@"
