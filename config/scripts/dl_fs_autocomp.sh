#!/usr/bin/env bash

set -eu
set -o pipefail


dotnet tool install --global fsautocomplete || true
dotnet tool update --global fsautocomplete
cp -- "$(dirname "$0")/fsharp-ls" "$BIN"
