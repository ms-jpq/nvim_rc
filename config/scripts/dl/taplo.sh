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
  BIN="$BIN.exe"
  ;;
esac

TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
mv --force -- "$TMP"/* "$BIN"
chmod +x -- "$BIN"
