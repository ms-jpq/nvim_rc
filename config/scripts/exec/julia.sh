#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


PROJECT="$(dirname -- "$0")/../lib/julia-ls"

exec -- julia "--project=$PROJECT" "$@"
