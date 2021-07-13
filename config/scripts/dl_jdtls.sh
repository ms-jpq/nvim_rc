#!/usr/bin/env bash

set -eu
set -o pipefail


LATEST="$(< "$(get -- "$URI")")"
mkdir --parents -- "$LIB"
"$(get -- "$PREFIX/$LATEST")" | unpack --format 'tar' --dest "$LIB"
cp -- "$(dirname "$0")/jdtls" "$BIN"
