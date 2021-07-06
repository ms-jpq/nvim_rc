#!/usr/bin/env bash

set -eu
set -o pipefail


if [[ "$OS" == 'Darwin' ]]
then
  get -- "$MAC_OS" "$BIN"
else
  get -- "$LINUX" "$BIN"
fi


chmod +x -- "$BIN"
