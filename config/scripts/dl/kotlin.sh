#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob

cd "$(dirname "$0")" || exit 1


LL="$LIB/bin/kotlin-language-server"
TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
rm --recursive --force -- "$LIB"
mv -- "$TMP/server" "$LIB"
ln --symbolic --force -- "$LL" "$BIN"
chmod +x -- "$LL"
