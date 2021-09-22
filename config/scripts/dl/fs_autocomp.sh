#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob

cd "$(dirname "$0")" || exit 1


dotnet tool install --global fsautocomplete || true
dotnet tool update --global fsautocomplete
cp -- "../exec/fsharp-ls.sh" "$BIN"
