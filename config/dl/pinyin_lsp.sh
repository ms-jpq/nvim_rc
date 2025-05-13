#!/usr/bin/env -S -- bash -Eeu -o pipefail -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REPO='iamcco/ds-pinyin-lsp'
BASE="https://github.com/$REPO/releases/latest/download/ds-pinyin-lsp"
VERSION="$(gh-latest.sh . "$REPO")"

case "$OSTYPE" in
darwin*)
  URI="${BASE}_${VERSION}_$HOSTTYPE-apple-darwin.zip"
  ;;
linux*)
  URI="${BASE}_${VERSION}_$HOSTTYPE-unknown-linux-musl.zip"
  ;;
*)
  URI="${BASE}_${VERSION}_$HOSTTYPE-pc-windows-gnu.zip"
  BIN="$BIN.exe"
  ;;
esac

# shellcheck disable=SC2154
get.sh "$URI" | unpack.sh "$TMP"
# shellcheck disable=2154

install -v -b -- "$TMP/ds-pinyin-lsp"* "$BIN"
