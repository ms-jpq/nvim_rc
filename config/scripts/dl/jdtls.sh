#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O failglob -O globstar

TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
rm --recursive --force -- "$LIB"
mv -- "$TMP" "$LIB"
ln -s -f -- "$LIB/bin/jdtls" "$BIN"
chmod +x -- "$BIN"
