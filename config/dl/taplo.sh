#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/tamasfe/taplo/releases/latest/download/taplo-full'

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

# shellcheck disable=SC2154
get.sh "$URI" | unpack.sh "$TMP"
F=("$TMP"/*)
chmod +x "${F[@]}"
mv -v -f -- "${F[@]}" "$BIN"
