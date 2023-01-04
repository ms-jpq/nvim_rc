#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s failglob failglob


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
    ;;
esac


TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
rm --recursive --force -- "$LIB"
mkdir --parents -- "$LIB"
mv -- "$TMP"/*/* "$LIB/"
ln --symbolic --force -- "$LIB/bin/$(basename -- "$BIN")" "$BIN"
