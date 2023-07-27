#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/tamasfe/taplo/releases/latest/download/taplo-full'

case "$OSTYPE" in
darwin*)
  URI="$BASE-darwin-aarch64.gz"
  ;;
linux*)
  URI="$BASE-linux-x86_64.gz"
  ;;
*)
  URI="$BASE-windows-x86_64.zip"
  BIN="$BIN.exe"
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
install -b -- "$TMP"/* "$BIN"
rm -fr -- "$TMP"
