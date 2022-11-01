#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


if [[ "$OSTYPE" =~ 'darwin' ]]
then
  URI="$MAC_URI"
else
  URI="$LINUX_URI"
fi


TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
mv -- "$TMP"/* "$BIN"
chmod +x -- "$BIN"
