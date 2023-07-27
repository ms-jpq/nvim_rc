#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/golangci/golangci-lint/releases/latest/download/golangci-lint'
VERSION='1.53.3'

case "$OSTYPE" in
darwin*)
  URI="$BASE-$VERSION-darwin-arm64.tar.gz"
  ;;
linux*)
  URI="$BASE-$VERSION-linux-amd64.tar.gz"
  ;;
*)
  URI="$BASE-$VERSION-windows-amd64.zip"
  BIN="$BIN.exe"
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
install -b -- "$TMP/"*/golangci-lint "$BIN"
