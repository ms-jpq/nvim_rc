#!/usr/bin/env bash

set -eu
set -o pipefail


mkdir --parents -- "$LIB"
cd "$LIB" || exit 1
dotnet tool install --global fsautocomplete
dotnet tool update --global fsautocomplete
cp -- "$(dirname "$0")/fsautocomplete" "$BIN"
