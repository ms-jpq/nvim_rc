#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s failglob failglob


case "$OSTYPE"
in
  darwin*)
    URI="$DARWIN_URI"
    ;;
  linux*)
    URI="$LINUX_URI"
    ;;
  *)
    exit 0
    ;;
esac


TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
mv -- "$TMP/shellcheck"*'/shellcheck' "$BIN"
chmod +x -- "$BIN"
