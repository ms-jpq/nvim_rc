#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

exec -- "$(dirname -- "$0")/../lib/lua-language-server/bin/lua-language-server" "$@"
