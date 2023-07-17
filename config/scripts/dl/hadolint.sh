#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

case "$OSTYPE" in
darwin*)
  URI="https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Darwin-x86_64"
  ;;
linux*)
  URI="https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64"
  ;;
*)
  URI="https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Windows-x86_64.exe"
  BIN="$BIN.exe"
  ;;
esac

FILE="$(get -- "$URI")"
cp --force -- "$FILE" "$BIN"
chmod +x -- "$BIN"
