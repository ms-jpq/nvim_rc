#!/usr/bin/env -S -- bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


BIN="$(dirname -- "$0")/../lib/phan/phan.phar"

exec -- php "$BIN" --allow-polyfill-parser --no-progress-bar --strict-type-checking "$@"
