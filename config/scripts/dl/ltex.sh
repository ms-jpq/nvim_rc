#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O nullglob -O failglob -O globstar

case "$OSTYPE" in
darwin*)
  URI="$DARWIN_URI"
  ;;
linux*)
  URI="$LINUX_URI"
  ;;
*)
  URI="$NT_URI"
  BIN="$BIN.bat"
  ;;
esac

TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
rm --recursive --force -- "$LIB"
mkdir --parents -- "$LIB"
mv --force -- "$TMP"/*/* "$LIB/"
ln --symbolic --force -- "$LIB/bin/$(basename -- "$BIN")" "$BIN"
