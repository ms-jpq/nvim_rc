#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

printf -- '\n'
exec -- "${0%/*}/.awk"
