#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/hadolint/hadolint/releases/latest/download/hadolint'

case "$OSTYPE" in
darwin*)
  URI="$BASE-Darwin-x86_64"
  ;;
linux*)
  URI="$BASE-Linux-x86_64"
  ;;
*)
  URI="$BASE-Windows-x86_64.exe"
  BIN="$BIN.exe"
  ;;
esac

FILE="$(get.py -- "$URI")"
install -b -- "$FILE" "$BIN"
