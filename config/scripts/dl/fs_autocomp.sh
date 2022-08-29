#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
rm --recursive --force -- "$LIB"
mv -- "$TMP" "$LIB"
ln --symbolic --force -- "$LIB/fsautocomplete" "$BIN"
chmod +x -- "$BIN"
