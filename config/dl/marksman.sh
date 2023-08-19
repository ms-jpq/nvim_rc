#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/artempyanykh/marksman/releases/latest/download/marksman'

case "$OSTYPE" in
darwin*)
  URI="$BASE-macos"
  ;;
linux*)
  URI="$BASE-linux-x64"
  ;;
*)
  URI="$BASE.exe"
  BIN="$BIN.exe"
  ;;
esac

FILE="$(get.py -- "$URI")"
install -v -b -- "$FILE" "$BIN"
