#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

S_BIN="$(dirname -- "$0")/../../bin/tectonic"
T_BIN="$(dirname -- "$BIN")/tectonic"

BASE='https://github.com/latex-lsp/texlab/releases/latest/download/texlab'
T_REPO='tectonic-typesetting/tectonic'
T_BASE="https://github.com/$T_REPO/releases/latest/download"
T_VERSION="$(gh-latest.sh . "$T_REPO")"
T_VERSION="${T_VERSION/'@'/'-'}"

case "$OSTYPE" in
darwin*)
  URI="$BASE-$HOSTTYPE-macos.tar.gz"
  T_URI="$T_BASE/$T_VERSION-$HOSTTYPE-apple-darwin.tar.gz"
  ;;
linux*)
  URI="$BASE-$HOSTTYPE-linux.tar.gz"
  T_URI="$T_BASE/$T_VERSION-$HOSTTYPE-unknown-linux-gnu.tar.gz"
  ;;
*)
  URI="$BASE-$HOSTTYPE-windows.zip"
  T_URI="$T_BASE/$T_VERSION-$HOSTTYPE-pc-windows-msvc.zip"
  BIN="$BIN.exe"
  S_BIN="$S_BIN.exe"
  T_BIN="$T_BIN.exe"
  ;;
esac

# shellcheck disable=SC2154
get.sh "$URI" | unpack.sh "$TMP"
get.sh "$T_URI" | unpack.sh "$TMP"
mv -v -f -- "$TMP/texlab"* "$BIN"
mv -v -f -- "$TMP/tectonic"* "$T_BIN"
ln -v -sf -- "$T_BIN" "$S_BIN"
