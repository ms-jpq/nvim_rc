#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
rm --recursive --force -- "$LIB"
mv -- "$TMP" "$LIB"
cp -- "$(dirname -- "$0")/../exec/powershell-ls.sh" "$BIN"
