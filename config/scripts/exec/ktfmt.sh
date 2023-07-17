#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

LIB="$${0%/*}/../lib"

exec -- java -jar "$LIB/ktfmt"/*.jar "$@"
