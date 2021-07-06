#!/usr/bin/env bash

set -eu
set -o pipefail


if [[ "$OS" == 'Darwin' ]]
then
  URI="$MAC_OS"
else
  URI="$LINUX"
fi
get -- "$URI" | unpack -
mv -- './shellcheck'*'/shellcheck' "$BIN"
chmod +x -- "$BIN"

