#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REPO='LuaLS/lua-language-server'
BASE="https://github.com/$REPO/releases/latest/download/lua-language-server"
VERSION="$(gh-latest.sh . "$REPO")"

case "$HOSTTYPE" in
aarch64)
  HT='arm64'
  ;;
*)
  HT='x64'
  ;;
esac

case "$OSTYPE" in
darwin*)
  URI="$BASE-$VERSION-darwin-$HT.tar.gz"
  ;;
linux*)
  URI="$BASE-$VERSION-linux-$HT.tar.gz"
  ;;
*)
  URI="$BASE-$VERSION-win32-$HT.zip"
  BIN="$BIN.bat"
  ;;
esac

# shellcheck disable=SC2154
get.sh "$URI" | unpack.sh "$TMP"
# shellcheck disable=2154
rm -rf -- "$LIB"
mv -v -f -- "$TMP" "$LIB"
ln -v -snf -- "$(dirname -- "$0")/lua_ls.ex.sh" "$BIN"
