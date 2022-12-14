#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


TMP="$(mktemp --directory)"
LATEST="$(< "$(get -- "$URI")")"
mkdir --parents -- "$LIB"
get -- "$PREFIX/$LATEST" | unpack --dest "$TMP"
rm --recursive --force -- "$LIB"
mv -- "$TMP" "$LIB"
cp -- "$(dirname -- "$0")/../exec/jdt_ls.sh" "$BIN"
