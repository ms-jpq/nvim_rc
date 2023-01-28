#!/usr/bin/env -S -- bash

set -Eeux
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
rm --recursive --force -- "$LIB"
mkdir --parents -- "$LIB"
mv -- "$TMP"/*/* "$LIB/"
ln --symbolic --force -- "$LIB/bin/$(basename -- "$BIN")" "$BIN"
