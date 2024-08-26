#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/Exafunction/codeium/releases/latest/download/language_server'

case "$HOSTTYPE" in
aarch64)
  HT='arm'
  ;;
*)
  HT='x64'
  ;;
esac

case "$OSTYPE" in
darwin*)
  URI="${BASE}_macos_$HT.gz"
  ;;
linux*)
  URI="${BASE}_linux_$HT.gz"
  ;;
*)
  URI="${BASE}_windows_$HT.exe.gz"
  BIN="$BIN.exe"
  ;;
esac

# shellcheck disable=SC2154
get.sh "$URI" | unpack.sh "$TMP"
install -v -b -- "$TMP"/* "$BIN"
