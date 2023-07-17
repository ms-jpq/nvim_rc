#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

case "$OSTYPE" in
darwin*)
  URI='https://github.com/terraform-linters/tflint/releases/latest/download/tflint_darwin_arm64.zip'
  ;;
linux*)
  URI='https://github.com/terraform-linters/tflint/releases/latest/download/tflint_linux_amd64.zip'
  ;;
*)
  URI='https://github.com/terraform-linters/tflint/releases/latest/download/tflint_windows_amd64.zip'
  ;;
esac

TMP="$(mktemp --directory)"
get.py -- "$URI" | unpack.py --dest "$TMP"
mv --force -- "$TMP/"* "$BIN"
chmod +x -- "$BIN"
