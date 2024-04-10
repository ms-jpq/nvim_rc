#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REPO='tekumara/typos-vscode'
BASE="https://github.com/$REPO/releases/latest/download/typos-lsp"
VERSION="$(gh-latest.sh . "$REPO")"

case "$OSTYPE" in
darwin*)
  URI="$BASE-$VERSION-$HOSTTYPE-apple-darwin.tar.gz"
  ;;
linux*)
  URI="$BASE-$VERSION-$HOSTTYPE-unknown-linux-gnu.tar.gz"
  ;;
*)
  URI="$BASE-$VERSION-$HOSTTYPE-pc-windows-msvc.zip"
  BIN="$BIN.exe"
  ;;
esac

# shellcheck disable=SC2154
get.sh "$URI" | unpack.sh "$TMP"
mv -v -f -- "$TMP/"**'/typos-lsp'* "$BIN"
