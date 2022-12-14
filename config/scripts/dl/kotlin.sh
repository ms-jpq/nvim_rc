#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


LL="$LIB/bin/kotlin-language-server"
TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
rm --recursive --force -- "$LIB"
mv -- "$TMP/server" "$LIB"
ln --symbolic --force -- "$LL" "$BIN"
chmod +x -- "$BIN"
