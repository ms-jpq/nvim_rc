#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

T_BIN="$(dirname -- "$BIN")/tectonic"

case "$OSTYPE" in
darwin*)
  URI="https://github.com/latex-lsp/texlab/releases/latest/download/texlab-x86_64-macos.tar.gz"
  T_URI="https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.13.1/tectonic-0.13.1-x86_64-apple-darwin.tar.gz"
  ;;
linux*)
  URI="https://github.com/latex-lsp/texlab/releases/latest/download/texlab-x86_64-linux.tar.gz"
  T_URI="https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.13.1/tectonic-0.13.1-x86_64-unknown-linux-gnu.tar.gz"
  ;;
*)
  URI="https://github.com/latex-lsp/texlab/releases/latest/download/texlab-x86_64-windows.zip"
  T_URI="https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.13.1/tectonic-0.13.1-x86_64-pc-windows-msvc.zip"
  BIN="$BIN.exe"
  T_BIN="$T_BIN.exe"
  ;;
esac

TMP="$(mktemp --directory)"
get.py -- "$URI" | unpack.py --dest "$TMP"
get.py -- "$T_URI" | unpack.py --dest "$TMP"
install -b -- "$TMP/texlab"* "$BIN"
install -b -- "$TMP/tectonic"* "$T_BIN"
