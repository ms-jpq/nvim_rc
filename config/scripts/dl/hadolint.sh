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


FILE="$(get -- "$URI")"
rm --force -- "$BIN"
cp -- "$FILE" "$BIN"
chmod +x -- "$BIN"
