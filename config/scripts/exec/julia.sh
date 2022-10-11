#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


SELF="$(readlink --canonicalize-existing -- "$0")"
ROOT="$(dirname -- "$(dirname -- "$(dirname -- "$(dirname -- "$SELF")")")")"
PROJECT="$ROOT/.vars/lib/julia-ls"

exec julia "--project=$PROJECT" "$@"
