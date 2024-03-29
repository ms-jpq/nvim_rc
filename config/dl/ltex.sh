#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/valentjn/ltex-ls/releases/latest/download/ltex-ls'
VERSION='16.0.0'

case "$OSTYPE" in
darwin*)
  URI="$BASE-$VERSION-mac-x64.tar.gz"
  ;;
linux*)
  URI="$BASE-$VERSION-linux-x64.tar.gz"
  ;;
*)
  URI="$BASE-$VERSION-windows-x64.zip"
  BIN="$BIN.bat"
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
# shellcheck disable=2154
rm -rf -- "$LIB"
mkdir -v -p -- "$LIB"
mv -f -- "$TMP"/*/* "$LIB/"
set -x
ln -v -sf -- "$LIB/bin/$(basename -- "$BIN")" "$BIN"
rm -v -fr -- "$TMP"
