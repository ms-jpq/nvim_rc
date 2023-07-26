#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/eclipse-che4z/che-che4z-lsp-for-cobol/releases/latest/download/cobol-language-support'
VERSION='2.0.1'

case "$OSTYPE" in
darwin*)
  URI="$BASE-darwin-arm64-$VERSION.vsix"
  ;;
linux*)
  URI="$BASE-linux-x64-$VERSION.vsix"
  ;;
*)
  URI="$BASE-win32-x64-$VERSION.vsix"
  BIN="$BIN.exe"
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --format zip --dst "$TMP"
install -b -- "$TMP/extension/server/native/server-"* "$BIN"
