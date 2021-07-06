#!/usr/bin/env bash

set -eu
set -o pipefail


if [[ "$OS" == 'Darwin' ]]
then
  URI="$MAC_OS"
else
  URI="$LINUX"
fi

T="$(get "$URI" --cd "$TMP_DIR")"
gzip --decompress -- "$T"
mv -- "$TMP_DIR/$BIN_NAME"* "$BIN_PATH"
chmod +x -- "$BIN_PATH"

