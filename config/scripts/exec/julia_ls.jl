#!/usr/bin/env -S bash
#=
set -Eeu
set -o pipefail
shopt -s failglob failglob

exec -- julia --project="$(dirname -- "$0")/../lib/julia-ls" "$0" "$@"
=#

using LanguageServer;
runserver()
