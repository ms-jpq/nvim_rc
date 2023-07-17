#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

URI='https://download.eclipse.org/jdtls/snapshots/jdt-language-server-latest.tar.gz'

TMP="$(mktemp --directory)"
get.py -- "$URI" | unpack.py --dest "$TMP"
rm --recursive --force -- "$LIB"
mv -- "$TMP" "$LIB"
ln -s -f -- "$LIB/bin/jdtls" "$BIN"
chmod +x -- "$BIN"
