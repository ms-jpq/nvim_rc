#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

SH=(
  perl
  -CASD
  -w
  -e
  "$(</dev/stdin)"
)

printf -- '%q ' "${SH[@]}"
