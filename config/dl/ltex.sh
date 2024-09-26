#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REPO='valentjn/ltex-ls'
BASE="https://github.com/$REPO/releases/latest/download/ltex-ls"
VERSION="$(gh-latest.sh . "$REPO")"

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

# shellcheck disable=SC2154
get.sh "$URI" | unpack.sh "$TMP"
# shellcheck disable=2154
rm -rf -- "$LIB"
mkdir -v -p -- "$LIB"
mv -v -f -- "$TMP"/*/* "$LIB/"
ln -v -snf -- "$LIB/bin/$(basename -- "$BIN")" "$BIN"
