#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/nolanderc/glsl_analyzer/releases/latest/download'

case "$OSTYPE" in
darwin*)
  URI="$BASE/$HOSTTYPE-macos.zip"
  EXT=''
  ;;
linux*)
  URI="$BASE/$HOSTTYPE-linux-musl.zip"
  EXT=''
  ;;
*)
  URI="$BASE/$HOSTTYPE-windows.zip"
  EXT='.exe'
  ;;
esac
BIN="$BIN$EXT"

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
install -v -b -- "$TMP/bin/glsl_analyzer$EXT" "$BIN"
rm -v -fr -- "$TMP"
