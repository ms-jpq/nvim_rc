#!/usr/bin/env -S -- bash -Eeuo pipefail -O failglob -O globstar

case "$OSTYPE" in
darwin*)
  URI="$DARWIN_URI"
  ;;
linux*)
  URI="$LINUX_URI"
  ;;
*)
  URI="$NT_URI"
  BIN="$BIN.sh"
  ;;
esac

TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
rm --recursive --force -- "$LIB"
mkdir --parents -- "$LIB"
mv -- "$TMP"/* "$LIB"
cp -- "$(dirname -- "$0")/../exec/hls.sh" "$BIN"
