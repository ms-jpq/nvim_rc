#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/nolanderc/glsl_analyzer/releases/latest/download'

case "$OSTYPE" in
darwin*)
  URI="$BASE/$HOSTTYPE-macos.zip"
  ;;
linux*)
  URI="$BASE/$HOSTTYPE-linux-musl.zip"
  ;;
*)
  URI="$BASE/$HOSTTYPE-windows.zip"
  BIN="$BIN.exe"
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
install -v -b -- "$TMP/"*/glsl_analyzer* "$BIN"
rm -v -fr -- "$TMP"
