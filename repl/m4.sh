#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

M4="$(</dev/stdin)"$'\n'

printf -- '%q ' printf -- '%s' "$M4"
printf -- '%s ' '|'
printf -- '%q ' m4 --prefix-builtins
