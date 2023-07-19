#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

case "$OSTYPE" in
darwin*)
  URI="https://downloads.haskell.org/~hls/haskell-language-server-1.9.0.0/haskell-language-server-1.9.0.0-aarch64-darwin.tar.xz"
  ;;
linux*)
  URI="https://downloads.haskell.org/~hls/haskell-language-server-1.9.0.0/haskell-language-server-1.9.0.0-x86_64-linux-deb10.tar.xz"
  ;;
*)
  URI="https://downloads.haskell.org/~hls/haskell-language-server-1.9.0.0/haskell-language-server-1.9.0.0-x86_64-windows.zip"
  BIN="$BIN.sh"
  ;;
esac

TMP="$(mktemp -d)"
get.py -- "$URI" | unpack.py --dest "$TMP"
rm -rf -- "$LIB"
mkdir -p -- "$LIB"
mv -- "$TMP"/* "$LIB"
install -b -- "${0%/*}/haskell_language_server.ex.sh" "$BIN"
