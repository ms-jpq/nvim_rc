#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/mvdan/sh/releases/latest/download/shfmt'
VERSION='v3.7.0'

case "$OSTYPE" in
darwin*)
  URI="${BASE}_${VERSION}_darwin_arm64"
  ;;
linux*)
  URI="${BASE}_${VERSION}_linux_amd64"
  ;;
*)
  URI="${BASE}_${VERSION}_windows_amd64.exe"
  BIN="$BIN.exe"
  ;;
esac

FILE="$(get.py -- "$URI")"
install -b -- "$FILE" "$BIN"
