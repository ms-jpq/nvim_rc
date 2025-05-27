#!/usr/bin/env -S -- bash -Eeu -o pipefail -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

# shellcheck disable=SC2154
DST="$LIB/lsp-ai"
BASE='https://github.com/SilasMarvin/lsp-ai/releases/latest/download/lsp-ai'

case "$OSTYPE" in
darwin*)
  URI="$BASE-$HOSTTYPE-apple-darwin.gz"
  ;;
linux*)
  URI="$BASE-$HOSTTYPE-unknown-linux-gnu.gz"
  ;;
*)
  URI="$BASE-$HOSTTYPE-pc-windows-msvc.zip"
  DST="$DST.exe"
  BIN="$BIN.exe"
  ;;
esac

# shellcheck disable=SC2154
get.sh "$URI" | unpack.sh "$TMP"

rm -rf -- "$LIB"
mkdir -p -- "$LIB"

case "$OSTYPE" in
darwin* | linux*)
  SRC=("$TMP"/*)
  ;;
*)
  SRC=("$TMP/lsp-ai.exe")
  ;;
esac

mv -v -f -- "${SRC[@]}" "$DST"
chmod +x "$DST"

ln -v -snf -- "$(dirname -- "$0")/lsp_ai.ex.sh" "$BIN"
