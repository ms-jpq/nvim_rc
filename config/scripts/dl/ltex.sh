#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

case "$OSTYPE" in
darwin*)
  URI="https://github.com/valentjn/ltex-ls/releases/latest/download/ltex-ls-16.0.0-mac-x64.tar.gz"
  ;;
linux*)
  URI="https://github.com/valentjn/ltex-ls/releases/latest/download/ltex-ls-16.0.0-linux-x64.tar.gz"
  ;;
*)
  URI="https://github.com/valentjn/ltex-ls/releases/latest/download/ltex-ls-16.0.0-windows-x64.zip"
  BIN="$BIN.bat"
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dest "$TMP"
rm -rf -- "$LIB"
mkdir -p -- "$LIB"
mv -- "$TMP"/*/* "$LIB/"
ln -sf -- "$LIB/bin/${BIN##*/}" "$BIN"
