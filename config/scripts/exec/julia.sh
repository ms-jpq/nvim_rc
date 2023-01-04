#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


SELF="$(readlink --canonicalize-existing -- "$0")"
ROOT="$(dirname -- "$(dirname -- "$(dirname -- "$(dirname -- "$SELF")")")")"
PROJECT="$ROOT/tmp/lib/julia-ls"

exec -- julia "--project=$PROJECT" "$@"
