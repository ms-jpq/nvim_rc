#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s failglob failglob


TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
rm --recursive --force -- "$LIB"
mv -- "$TMP" "$LIB"
ln -s -f -- "$LIB/bin/jdtls" "$BIN"
chmod +x -- "$BIN"
