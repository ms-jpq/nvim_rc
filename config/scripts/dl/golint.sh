#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

case "$OSTYPE" in
darwin*)
  URI="https://github.com/golangci/golangci-lint/releases/latest/download/golangci-lint-1.53.3-darwin-arm64.tar.gz"
  ;;
linux*)
  URI="https://github.com/golangci/golangci-lint/releases/latest/download/golangci-lint-1.53.3-linux-amd64.tar.gz"
  ;;
*)
  URI="https://github.com/golangci/golangci-lint/releases/latest/download/golangci-lint-1.53.3-windows-amd64.zip"
  BIN="$BIN.exe"
  ;;
esac

TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
mv --force -- "$TMP/"*/golangci-lint "$BIN"
