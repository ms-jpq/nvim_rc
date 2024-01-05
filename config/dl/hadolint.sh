#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/hadolint/hadolint/releases/latest/download/hadolint'

case "$HOSTTYPE" in
aarch64)
  HT='arm64'
  ;;
*)
  HT="$HOSTTYPE"
  ;;
esac

case "$OSTYPE" in
darwin*)
  URI="$BASE-Darwin-x86_64"
  ;;
linux*)
  URI="$BASE-Linux-$HT"
  ;;
*)
  URI="$BASE-Windows-$HT.exe"
  BIN="$BIN.exe"
  ;;
esac

FILE="$(get.py -- "$URI")"
install -v -b -- "$FILE" "$BIN"
