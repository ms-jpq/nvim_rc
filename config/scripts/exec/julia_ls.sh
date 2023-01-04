#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


SELF="$(readlink --canonicalize-existing -- "$0")"
BASE="$(dirname -- "$SELF")"


exec -- "$BASE/julia.sh" "$BASE/julia_ls.jl" "$@"
