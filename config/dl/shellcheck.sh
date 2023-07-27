#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE='https://github.com/koalaman/shellcheck/releases/latest/download/shellcheck'
VERSION='v0.9.0'

case "$OSTYPE" in
darwin*)
  URI="$BASE-$VERSION.darwin.x86_64.tar.xz"
  ;;
linux*)
  URI="$BASE-$VERSION.linux.x86_64.tar.xz"
  ;;
*)
  exit 0
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
# shellcheck disable=2154
install -b -- "$TMP/shellcheck"*'/shellcheck' "$BIN"
rm -fr -- "$TMP"
