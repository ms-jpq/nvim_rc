#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REPO='koalaman/shellcheck'
BASE="https://github.com/$REPO/releases/latest/download/shellcheck"
VERSION="$(gh-latest.sh . "$REPO")"

case "$OSTYPE" in
darwin*)
  URI="$BASE-$VERSION.darwin.x86_64.tar.xz"
  ;;
linux*)
  URI="$BASE-$VERSION.linux.$HOSTTYPE.tar.xz"
  ;;
*)
  exit 0
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
# shellcheck disable=2154
install -v -b -- "$TMP/shellcheck"*'/shellcheck' "$BIN"
rm -v -fr -- "$TMP"
