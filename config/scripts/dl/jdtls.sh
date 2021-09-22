#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


LATEST="$(< "$(get -- "$URI")")"
mkdir --parents -- "$LIB"
get -- "$PREFIX/$LATEST" | unpack --dest "$LIB"
cp -- "$(dirname "$0")/../exec/jdt-ls.sh" "$BIN"
