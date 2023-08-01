#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

URI='https://download.eclipse.org/jdtls/snapshots/jdt-language-server-latest.tar.gz'

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
# shellcheck disable=2154
rm -v -rf -- "$LIB"
mv -v -f -- "$TMP" "$LIB"
# shellcheck disable=2154
ln -v -sf -- "$LIB/bin/jdtls" "$BIN"
