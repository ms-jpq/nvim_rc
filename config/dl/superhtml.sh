#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/kristoff-it/superhtml/releases/latest/download'

case "$OSTYPE" in
darwin*)
  URI="$BASE/$HOSTTYPE-macos.tar.gz"
  ;;
linux*)
  URI="$BASE/$HOSTTYPE-linus-musl.tar.gz"
  ;;
*)
  URI="$BASE/$HOSTTYPE-windows.zip"
  BIN="$BIN.exe"
  ;;
esac

# shellcheck disable=SC2154
get.sh "$URI" | unpack.sh "$TMP"
mv -v -f -- "$TMP"/*/* "$BIN"
