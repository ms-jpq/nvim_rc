#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob

cd "$(dirname "$0")" || exit 1


if [[ "$OS" == 'Darwin' ]]
then
  URI="$MAC_URI"
else
  URI="$LINUX_URI"
fi


TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
mv -- "$TMP/shellcheck"*'/shellcheck' "$BIN"
chmod +x -- "$BIN"

