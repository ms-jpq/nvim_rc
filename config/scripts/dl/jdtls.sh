#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

URI='https://download.eclipse.org/jdtls/snapshots/jdt-language-server-latest.tar.gz'

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dest "$TMP"
rm -rf -- "$LIB"
mv -- "$TMP" "$LIB"
ln -sf -- "$LIB/bin/jdtls" "$BIN"
chmod +x -- "$BIN"
