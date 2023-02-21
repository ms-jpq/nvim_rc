#!/usr/bin/env -S -- bash -Eeuo pipefail -O failglob -O globstar

cd -- "$(dirname -- "$0")"

exec -- python3 -m go deps "$@"
