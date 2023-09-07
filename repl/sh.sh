#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

SH=(
  bash
  -c
  "$(</dev/stdin)"
)

printf -- '%q ' "${SH[@]}"
