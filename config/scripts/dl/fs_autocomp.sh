#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


TMP="$(mktemp --directory)"
TOOLS="$TMP/fsa"
mkdir --parent -- "$TOOLS"

cd "$TMP" || exit 1
dotnet new tool-manifest
dotnet tool install --tool-path "$TOOLS" fsautocomplete
rm --recursive --force -- "$LIB"
mv -- "$TOOLS" "$LIB"
ln --symbolic --force -- "$LIB/fsautocomplete" "$BIN"
