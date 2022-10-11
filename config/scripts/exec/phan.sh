#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


BIN="$(dirname -- "$(dirname -- "$(realpath -- "$0")")")/lib/phan.phar"

exec php "$BIN" "$@"
