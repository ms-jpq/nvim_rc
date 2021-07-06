#!/usr/bin/env bash

set -eu
set -o pipefail


if [[ "$OS" == 'Darwin' ]]
then
  PLATFORM="$MAC_OS"
else
  PLATFORM="$LINUX"
fi
get -- "$URI_ROOT/$PLATFORM" "$(mktemp)" | unpack - -- "$TMP_DIR"
mv -- "$TMP_DIR/$BIN_NAME"*"/$BIN_NAME" "$BIN_PATH"
chmod +x -- "$BIN_PATH"

