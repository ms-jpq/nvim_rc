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


TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
rm --recursive --force -- "$LIB"
mv -- "$TMP" "$LIB"
