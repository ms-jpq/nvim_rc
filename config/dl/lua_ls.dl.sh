#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REPO='LuaLS/lua-language-server'
BASE="https://github.com/$REPO/releases/latest/download/lua-language-server"
VERSION="$(gh-latest.sh "$REPO")"

case "$OSTYPE" in
darwin*)
  URI="$BASE-$VERSION-darwin-arm64.tar.gz"
  ;;
linux*)
  URI="$BASE-$VERSION-linux-x64.tar.gz"
  ;;
*)
  URI="$BASE-$VERSION-win32-x64.zip"
  BIN="$BIN.bat"
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
# shellcheck disable=2154
rm -rf -- "$LIB"
mv -f -- "$TMP" "$LIB"
install -v -b -- "${0%/*}/lua_ls.ex.sh" "$BIN"
