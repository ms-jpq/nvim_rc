#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O failglob -O globstar

cp --force -- "$(dirname -- "$0")/../exec/$(basename -- "$0")" "$BIN"
