#!/usr/bin/env -S -- bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


case "$OSTYPE"
in
  darwin*)
    URI="$DARWIN_URI"
    ;;
  linux*)
    URI="$LINUX_URI"
    ;;
  *)
    URI="$NT_URI"
    BIN="$BIN.exe"
    ;;
esac


TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
mv -- "$TMP/lemminx"* "$BIN"
chmod +x -- "$BIN"
