#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REPO='mvdan/sh'
BASE="https://github.com/$REPO/releases/latest/download/shfmt"
VERSION="$(gh-latest.sh . "$REPO")"

case "$HOSTTYPE" in
aarch64)
  HT='arm64'
  ;;
*)
  HT='amd64'
  ;;
esac

case "$OSTYPE" in
darwin*)
  URI="${BASE}_${VERSION}_darwin_$HT"
  ;;
linux*)
  URI="${BASE}_${VERSION}_linux_$HT"
  ;;
*)
  URI="${BASE}_${VERSION}_windows_$HT.exe"
  BIN="$BIN.exe"
  ;;
esac

FILE="$(get.sh "$URI")"
install -v -b -- "$FILE" "$BIN"
