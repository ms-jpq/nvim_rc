#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


if [[ "$OS" == 'Darwin' ]]
then
  URI="$MAC_URI"
else
  URI="$LINUX_URI"
fi


FILE="$(get -- "$URI")"
rm --force -- "$BIN"
cp -- "$FILE" "$BIN"
chmod +x -- "$BIN"
