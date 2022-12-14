#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


TMP="$(mktemp --directory)"
dotnet tool install --tool-path "$TMP" fsautocomplete
rm --recursive --force -- "$LIB"
mv -- "$TMP" "$LIB"
cp -- "$(dirname -- "$0")/../exec/fsautocomplete.sh" "$BIN"
