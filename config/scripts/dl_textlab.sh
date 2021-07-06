#!/usr/bin/env bash

set -eu
set -o pipefail


if [[ "$OS" == 'Darwin' ]]
then
  URI="$MAC_URI"
else
  URI="$LINUX_URI"
fi

get "$URI" | unpack -
mv -- "$TMP_DIR/$BIN_NAME" "$BIN_PATH"
chmod +x -- "$BIN_PATH"

