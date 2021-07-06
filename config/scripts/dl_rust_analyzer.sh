#!/usr/bin/env bash

set -eu
set -o pipefail


if [[ "$OS" == 'Darwin' ]]
then
  URI="$MAC_URI"
else
  URI="$LINUX_URI"
fi

TMP="$(get "$URI")"
gzip --decompress -- "$TMP"
mv -- 'rust_analyzer'* "$BIN"
chmod +x -- "$BIN"

