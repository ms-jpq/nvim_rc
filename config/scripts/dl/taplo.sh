#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

case "$OSTYPE" in
darwin*)
  URI='https://github.com/tamasfe/taplo/releases/latest/download/taplo-full-darwin-aarch64.gz'
  ;;
linux*)
  URI='https://github.com/tamasfe/taplo/releases/latest/download/taplo-full-linux-x86_64.gz'
  ;;
*)
  URI='https://github.com/tamasfe/taplo/releases/latest/download/taplo-full-windows-x86_64.zip'
  BIN="$BIN.exe"
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
install -b -- "$TMP"/* "$BIN"
