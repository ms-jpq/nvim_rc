#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

if ! command -v -- go; then
  exit
fi

exec -- go run -- "$(dirname -- "$0")/delve.go"
