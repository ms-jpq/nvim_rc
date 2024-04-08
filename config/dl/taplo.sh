#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

# BASE='https://github.com/tamasfe/taplo/releases/latest/download/taplo-full'
BASE='https://github.com/tamasfe/taplo/releases/download/0.8.0/taplo-full'

case "$OSTYPE" in
darwin*)
  URI="$BASE-darwin-$HOSTTYPE.gz"
  ;;
linux*)
  URI="$BASE-linux-$HOSTTYPE.gz"
  ;;
*)
  URI="$BASE-windows-$HOSTTYPE.zip"
  BIN="$BIN.exe"
  ;;
esac

TMP="$(mktemp -d)"
get.sh "$URI" | unpack.sh "$TMP"
install -v -b -- "$TMP"/* "$BIN"
rm -v -fr -- "$TMP"
