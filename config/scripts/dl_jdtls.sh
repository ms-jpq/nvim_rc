#!/usr/bin/env bash

set -eu
set -o pipefail


LATEST="$(< "$(get -- "$URI")")"
ZIP="$(get -- "$PREFIX/$LATEST")"
mkdir --parents -- "$LIB"
cd "$LIB" || exit 1
unpack -- "$ZIP"
cp -- "$(dirname "$0")/jdtls" "$BIN"
