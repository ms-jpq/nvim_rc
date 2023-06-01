#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O nullglob -O extglob -O failglob -O globstar

LIB="$(dirname -- "$0")/../lib"

exec -- java -jar "$LIB/ktfmt"/*.jar "$@"
