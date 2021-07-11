#!/usr/bin/env bash

set -eu
set -o pipefail


if [[ "$OS" == 'Darwin' ]]
then
  URI="$MAC_URI"
else
  URI="$LINUX_URI"
fi

TMP="$(mktemp)"
ZIP="$(get -- "$URI")"
gzip --decompress --keep --force -- "$ZIP"
mv -- "$ZIP" "$TMP"
mv -- "./rust-analyzer-"* "$BIN"
mv -- "$TMP" "$ZIP"
chmod +x -- "$BIN"

