#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O failglob -O globstar

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
cp --force -- "$(dirname -- "$0")/../exec/hls.sh" "$BIN"
