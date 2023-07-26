#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

T_BIN="$(dirname -- "$BIN")/tectonic"

BASE='https://github.com/latex-lsp/texlab/releases/latest/download/texlab'
T_BASE='https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40'
T_VERSION='0.14.1'

case "$OSTYPE" in
darwin*)
  URI="$BASE-aarch64-macos.tar.gz"
  T_URI="$T_BASE$T_VERSION/tectonic-$T_VERSION-x86_64-apple-darwin.tar.gz"
  ;;
linux*)
  URI="$BASE-x86_64-linux.tar.gz"
  T_URI="$T_BASE$T_VERSION/tectonic-$T_VERSION-x86_64-unknown-linux-gnu.tar.gz"
  ;;
*)
  URI="$BASE-x86_64-windows.zip"
  T_URI="$T_BASE$T_VERSION/tectonic-$T_VERSION-x86_64-pc-windows-msvc.zip"
  BIN="$BIN.exe"
  T_BIN="$T_BIN.exe"
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
get.py -- "$T_URI" | unpack.py --dst "$TMP"
install -b -- "$TMP/texlab"* "$BIN"
install -b -- "$TMP/tectonic"* "$T_BIN"
