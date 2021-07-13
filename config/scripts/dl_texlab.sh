#!/usr/bin/env bash

set -eu
set -o pipefail


if [[ "$OS" == 'Darwin' ]]
then
  URI="$MAC_URI"
else
  URI="$LINUX_URI"
fi


TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
mv -- "$TMP/texlab" "$BIN"
chmod +x -- "$BIN"

