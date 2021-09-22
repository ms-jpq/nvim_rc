#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


dotnet tool install --global fsautocomplete || true
dotnet tool update --global fsautocomplete
cp -- "$(dirname "$0")/../exec/fsharp-ls.sh" "$BIN"
