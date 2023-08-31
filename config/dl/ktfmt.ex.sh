#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

exec -- java -jar "$(dirname -- "$0")/../lib/ktfmt.sh"/*.jar "$@"
