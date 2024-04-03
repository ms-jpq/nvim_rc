#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/terraform-linters/tflint/releases/latest/download/tflint'

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
  URI="${BASE}_darwin_$HT.zip"
  ;;
linux*)
  URI="${BASE}_linux_$HT.zip"
  ;;
*)
  URI="${BASE}_windows_$HT.zip"
  ;;
esac

TMP="$(mktemp -d)"
get.sh "$URI" | unpack.py --dst "$TMP"
# shellcheck disable=2154
install -v -b -- "$TMP/"* "$BIN"
rm -v -fr -- "$TMP"
