#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/terraform-linters/tflint/releases/latest/download/tflint'

case "$OSTYPE" in
darwin*)
  URI="${BASE}_darwin_arm64.zip"
  ;;
linux*)
  URI="${BASE}_linux_amd64.zip"
  ;;
*)
  URI="${BASE}_windows_amd64.zip"
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
# shellcheck disable=2154
install -v -b -- "$TMP/"* "$BIN"
rm -fr -- "$TMP"
