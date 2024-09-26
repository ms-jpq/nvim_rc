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

# shellcheck disable=SC2154
get.sh "$URI" | unpack.sh "$TMP"
mv -v -f -- "$TMP/"*/golangci-lint "$BIN"
# shellcheck disable=SC2154
mkdir -v -p -- "$LIB"
ln -v -snf -- "$BIN" "$LIB/../../../bin/golangci-lint"
