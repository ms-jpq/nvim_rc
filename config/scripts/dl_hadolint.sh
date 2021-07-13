#!/usr/bin/env bash

set -eu
set -o pipefail


if [[ "$OS" == 'Darwin' ]]
then
  FILE="$(get -- "$MAC_URI")"
else
  FILE="$(get -- "$LINUX_URI")"
fi


rm --force -- "$BIN"
cp -- "$FILE" "$BIN"
chmod +x -- "$BIN"
