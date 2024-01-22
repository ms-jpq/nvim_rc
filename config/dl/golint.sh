#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REPO='golangci/golangci-lint'
BASE="https://github.com/$REPO/releases/latest/download/golangci-lint"
VERSION="$(gh-latest.sh . "$REPO")"
VERSION="${VERSION#v}"

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
  URI="$BASE-$VERSION-darwin-$HT.tar.gz"
  ;;
linux*)
  URI="$BASE-$VERSION-linux-$HT.tar.gz"
  ;;
*)
  URI="$BASE-$VERSION-windows-$HT.zip"
  BIN="$BIN.exe"
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
install -v -b -- "$TMP/"*/golangci-lint "$BIN"
rm -v -fr -- "$TMP"
