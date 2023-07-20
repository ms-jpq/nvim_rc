#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

VERSION='2.0.0.1'

case "$OSTYPE" in
darwin*)
  URI="https://github.com/haskell/haskell-language-server/releases/latest/download/haskell-language-server-$VERSION-aarch64-apple-darwin.tar.xz"
  ;;
linux*)
  URI="https://github.com/haskell/haskell-language-server/releases/latest/download/haskell-language-server-$VERSION-x86_64-linux-ubuntu22.04.tar.xz"
  ;;
*)
  URI="https://github.com/haskell/haskell-language-server/releases/latest/download/haskell-language-server-$VERSION-x86_64-mingw64.zip"
  BIN="$BIN.sh"
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dst "$TMP"
# shellcheck disable=2154
rm -rf -- "$LIB"
mkdir -p -- "$LIB"
mv -- "$TMP"/* "$LIB"
install -b -- "${0%/*}/haskell_language_server.ex.sh" "$BIN"
