#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

case "$OSTYPE" in
darwin*)
  URI="https://github.com/mvdan/sh/releases/latest/download/shfmt_v3.7.0_darwin_arm64"
  ;;
linux*)
  URI="https://github.com/mvdan/sh/releases/latest/download/shfmt_v3.7.0_linux_amd64"
  ;;
*)
  URI="https://github.com/mvdan/sh/releases/latest/download/shfmt_v3.7.0_windows_amd64.exe"
  BIN="$BIN.exe"
  ;;
esac

FILE="$(get -- "$URI")"
chmod +x -- "$FILE"
cp --force -- "$FILE" "$BIN"
