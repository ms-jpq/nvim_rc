#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


BIN="$(dirname "$(dirname "$(realpath "$0")")")/tmp/phan.phar"

exec php "$BIN" "$@"
