#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob

cd "$(dirname "$0")" || exit 1


LATEST="$(< "$(get -- "$URI")")"
mkdir --parents -- "$LIB"
get -- "$PREFIX/$LATEST" | unpack --dest "$LIB"
cp -- "../exec/jdt-ls" "$BIN"
