#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


TMP="$(mktemp --directory)"
dotnet tool install --tool-path "$TMP" fsautocomplete
rm --recursive --force -- "$LIB"
mv -- "$TMP" "$LIB"
ln --symbolic --force -- "$LIB/fsautocomplete" "$BIN"
