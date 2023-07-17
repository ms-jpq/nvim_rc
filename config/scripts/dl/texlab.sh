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
  URI="https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.13.1/tectonic-0.13.1-x86_64-pc-windows-msvc.zip"
  T_URI="$T_NT_URI"
  BIN="$BIN.exe"
  T_BIN="$T_BIN.exe"
  ;;
esac

TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
get -- "$T_URI" | unpack --dest "$TMP"
mv --force -- "$TMP/texlab"* "$BIN"
mv --force -- "$TMP/tectonic"* "$T_BIN"
chmod +x -- "$BIN" "$T_BIN"
