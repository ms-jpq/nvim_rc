#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob

cd "$(dirname "$0")" || exit 1


if [[ "$OS" == 'Darwin' ]]
then
  FILE="$(get -- "$MAC_URI")"
else
  FILE="$(get -- "$LINUX_URI")"
fi


rm --force -- "$BIN"
cp -- "$FILE" "$BIN"
chmod +x -- "$BIN"
